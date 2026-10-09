"""Fail closed on missing coverage, changed files, unsupported facts and conflict."""

from collections import defaultdict
from datetime import date, datetime
from hashlib import sha256
from pathlib import Path
import json
import math
from .policy import REQUIREMENTS, SUPPLEMENTAL, CUTOFF, BLOCKED, VERIFIED


def fingerprint(value):
    return sha256(
        json.dumps(
            value, sort_keys=True, allow_nan=False, separators=(",", ":")
        ).encode()
    ).hexdigest()


def populated(value):
    if value is None or (isinstance(value, str) and (not value.strip())):
        return False
    if isinstance(value, float) and (not math.isfinite(value)):
        return False
    if isinstance(value, (dict, list)):
        return bool(value) and all(
            (
                populated(v)
                for v in (value.values() if isinstance(value, dict) else value)
            )
        )
    return True


def source_problem(source, root):
    needed = ("id", "url", "document_id", "published", "retrieved", "path", "sha256")
    if any(
        (
            not isinstance(source.get(k), str) or not populated(source.get(k))
            for k in needed
        )
    ):
        return "Incomplete source provenance"
    try:
        if date.fromisoformat(source["published"]) > date.fromisoformat(CUTOFF):
            return "Source published after historical cutoff"
        retrieved = datetime.fromisoformat(source["retrieved"].replace("Z", "+00:00"))
        if retrieved.date() < date.fromisoformat(source["published"]):
            return "Retrieval predates publication"
        path = (root / source["path"]).resolve()
        if not path.is_relative_to(root.resolve()):
            return "Source path outside case directory"
        if sha256(path.read_bytes()).hexdigest() != source["sha256"]:
            return "Source content hash mismatch"
    except (OSError, ValueError, TypeError):
        return "Missing source file or invalid source date/path"
    if not source["url"].startswith("https://"):
        return "Missing HTTPS source URL"
    return None


def check_evidence(case, root, context=None):
    root = Path(root)
    if not isinstance(case, dict):
        raise ValueError("Case must be a JSON object")
    for field, identifier in (("observations", "key"), ("sources", "id")):
        if not isinstance(case.get(field, []), list):
            raise ValueError(f"{field} must be a list")
        for item in case.get(field, []):
            if (
                not isinstance(item, dict)
                or not isinstance(item.get(identifier), str)
                or (not item[identifier].strip())
            ):
                raise ValueError(f"Invalid {field} record or identifier")
            if field == "sources" and (
                not isinstance(item.get("claims", []), list)
                or any((not isinstance(c, dict) for c in item.get("claims", [])))
            ):
                raise ValueError("Source claims must be a list of objects")
    observations = defaultdict(list)
    sources = defaultdict(list)
    for row in case.get("observations", []):
        observations[row["key"]].append(row)
    for source in case.get("sources", []):
        sources[source["id"]].append(source)
    source_errors = {
        sid: (
            "Duplicate source identifier"
            if len(group) != 1
            else source_problem(group[0], root)
        )
        for sid, group in sources.items()
    }
    rows = []
    required = {r.key: r for r in REQUIREMENTS}
    required.update({k: r for k, r in SUPPLEMENTAL.items() if k in observations})
    from .policy import Requirement

    for key in observations.keys() - required.keys():
        required[key] = Requirement(
            key,
            "unregistered input",
            "Unmapped model dependencies",
            "Register the material input and its evidence policy in code before use.",
        )
    for key, req in sorted(required.items()):
        group = observations.get(key, [])
        classification, reason = ("missing evidence", "Required observation absent")
        obs = group[0] if group else {}
        if not group:
            pass
        elif len(group) > 1 or obs.get("conflict"):
            classification, reason = (
                "conflicting evidence",
                "Duplicate observations or unresolved dispute",
            )
        elif key not in {r.key for r in REQUIREMENTS} | SUPPLEMENTAL.keys():
            reason = "Input not registered in evidence policy"
        elif not populated(obs.get("value")):
            reason = "Required value missing or non-finite"
        elif obs.get("origin") == "synthetic":
            reason = "Synthetic input cannot verify a historical fact"
        elif obs.get("kind") == "assumption":
            if (
                req.assumption_allowed
                and populated(obs.get("rationale"))
                and (obs.get("origin") == "analyst")
            ):
                classification, reason = (
                    "explicit modelling assumption",
                    obs["rationale"],
                )
            else:
                reason = (
                    "Historical fact cannot be relabelled as a modelling assumption"
                )
        elif req.assumption_allowed:
            reason = (
                "Future choice requires an explicit modelling assumption and rationale"
            )
        else:
            needed = (
                "company",
                "units",
                "period_start",
                "period_end",
                "extraction_method",
            )
            if obs.get("kind") != "fact" or obs.get("origin") not in (
                "reported",
                "management_guidance",
            ):
                reason = "Historical observation has no supported factual origin"
            elif any((not populated(obs.get(k)) for k in needed)):
                reason = (
                    "Missing observation company, units, period or extraction method"
                )
            else:
                try:
                    start, end = (
                        date.fromisoformat(obs["period_start"]),
                        date.fromisoformat(obs["period_end"]),
                    )
                    valid_period = start <= end <= date.fromisoformat(CUTOFF)
                except (ValueError, TypeError):
                    valid_period = False
                if not valid_period:
                    reason = "Invalid period or post-cutoff historical observation"
                else:
                    payload = {
                        k: obs[k]
                        for k in (
                            "key",
                            "value",
                            "company",
                            "units",
                            "period_start",
                            "period_end",
                        )
                    }
                    matching, conflicting, failures = ([], [], [])
                    for sid, records in sources.items():
                        for src in records:
                            for claim in src.get("claims", []):
                                if claim.get("key") != key:
                                    continue
                                if source_errors[sid]:
                                    failures.append(source_errors[sid])
                                elif not all(
                                    (
                                        populated(claim.get(k))
                                        for k in (
                                            "reviewer",
                                            "reviewed_at",
                                            "section",
                                            "review_note",
                                            "payload_hash",
                                        )
                                    )
                                ):
                                    failures.append(
                                        "Source claim has not been fully reviewed"
                                    )
                                elif claim["payload_hash"] != fingerprint(payload):
                                    conflicting.append(sid)
                                else:
                                    matching.append(sid)
                    if conflicting:
                        classification, reason = (
                            "conflicting evidence",
                            "Reviewed source claims disagree with the selected observation",
                        )
                    elif failures:
                        reason = "; ".join(sorted(set(failures)))
                    elif matching:
                        classification, reason = (
                            "verified fact",
                            "Exact observation supported by reviewed source: "
                            + ", ".join(matching),
                        )
                    else:
                        reason = "No available reviewed source claim supports this observation"
        from .policy import materiality

        blocking, material_reason = materiality(key, context)
        rows.append(
            {
                "key": key,
                "category": req.category,
                "classification": classification,
                "reason": reason,
                "affected_calculations": req.affects,
                "resolution": req.resolution,
                "value": obs.get("value"),
                "declared_kind": obs.get("kind"),
                "origin": obs.get("origin"),
                "recommendation_blocking": blocking,
                "materiality_reason": material_reason,
            }
        )
    lookup = {r["key"]: r for r in rows}
    sums = {
        f"{role}.FY2024.ebitda_reconciliation": [
            f"{role}.FY2024.operating_profit",
            f"{role}.FY2024.depreciation_amortisation",
        ]
        for role in ("acquirer", "target")
    }
    sums["target.opening.debt_principal"] = [
        "detail.target.notes_principal",
        "detail.target.finance_lease",
    ]
    for key, deps in sums.items():
        if key in observations:
            continue
        if all(
            (
                d in lookup
                and lookup[d]["classification"] == "verified fact"
                and isinstance(lookup[d]["value"], (int, float))
                for d in deps
            )
        ):
            lookup[key].update(
                classification="verified fact",
                origin="derived",
                value=sum((lookup[d]["value"] for d in deps)),
                dependencies=deps,
                reason="Derived from verified inputs: "
                + " + ".join(deps)
                + (
                    ". Simple operating EBITDA; not adjusted EBITDA or contractual EBITDAR."
                    if "ebitda" in key
                    else ". Includes finance-lease liability; excludes operating leases."
                ),
            )
    blocked = any(
        (
            row["recommendation_blocking"]
            and row["classification"] in ("missing evidence", "conflicting evidence")
            for row in rows
        )
    )
    return {
        "status": BLOCKED if blocked else VERIFIED,
        "blocked": blocked,
        "cutoff": CUTOFF,
        "policy_version": 2,
        "rows": rows,
        "case_id": fingerprint(case),
        "source_state_id": fingerprint(source_errors),
    }


# Preserved implementation notes
# Also audit unknown inputs: they cannot disappear from the completeness report.
# Bind review to exact value, period, company and units, not only metric name.
# Fixed derivations, never arbitrary input expressions or analyst overrides.
# Explicit supplied conflicts are preserved instead of replaced by arithmetic.
