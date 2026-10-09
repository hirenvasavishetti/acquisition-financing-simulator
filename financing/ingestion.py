"""Cached bounded downloads and cutoff-safe SEC fact candidates; never auto-verify."""

from datetime import datetime, timezone, date
from hashlib import sha256
import json
from pathlib import Path
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from .policy import CUTOFF


def fetch(
    url, cache, user_agent, timeout=20, retries=3, opener=urlopen, sleeper=time.sleep
):
    if not url.startswith("https://"):
        raise ValueError("HTTPS required")
    if "sec.gov/" in url and "@" not in user_agent:
        raise ValueError(
            "SEC downloads require a truthful SEC_USER_AGENT identifying your organization/contact email"
        )
    if not 1 <= retries <= 5:
        raise ValueError("Retries must be bounded between 1 and 5")
    cache = Path(cache)
    cache.mkdir(parents=True, exist_ok=True)
    key = sha256(url.encode()).hexdigest()
    body = cache / f"{key}.bin"
    meta = cache / f"{key}.json"
    if body.exists() and meta.exists():
        record = json.loads(meta.read_text())
        if sha256(body.read_bytes()).hexdigest() != record["sha256"]:
            raise ValueError("Cached document integrity failure")
        return (body, record)
    for attempt in range(retries):
        try:
            sleeper(0.2)
            with opener(
                Request(
                    url,
                    headers={"User-Agent": user_agent, "Accept-Encoding": "identity"},
                ),
                timeout=timeout,
            ) as response:
                data = response.read()
            if not data:
                raise ValueError("Empty source response")
            record = {
                "url": url,
                "retrieved": datetime.now(timezone.utc).isoformat(),
                "sha256": sha256(data).hexdigest(),
            }
            body.write_bytes(data)
            meta.write_text(json.dumps(record, indent=2), encoding="utf-8")
            return (body, record)
        except HTTPError as exc:
            if exc.code not in (429, 500, 502, 503, 504) or attempt == retries - 1:
                raise
            retry = exc.headers.get("Retry-After", "")
            sleeper(min(10, float(retry) if retry.isdigit() else 2**attempt))
        except (URLError, TimeoutError):
            if attempt == retries - 1:
                raise
            sleeper(min(10, 2**attempt))


def companyfacts_candidates(payload, tags, cutoff=CUTOFF):
    """Keep original filing periods/accessions. Later restatements are excluded.

    Candidate extraction is not evidence verification. Multiple original filings
    remain visible for reconciliation; fiscal-year labels alone never select facts.
    """
    rows = []
    for tag in tags:
        fact = payload.get("facts", {}).get("us-gaap", {}).get(tag, {})
        for units, entries in fact.get("units", {}).items():
            for entry in entries:
                if (
                    entry.get("filed", "9999") > cutoff
                    or entry.get("end", "9999") > cutoff
                ):
                    continue
                if entry.get("form") not in ("10-K", "10-Q"):
                    continue
                if "val" not in entry:
                    continue
                start = entry.get("start", entry["end"])
                duration = (
                    date.fromisoformat(entry["end"]) - date.fromisoformat(start)
                ).days + 1
                rows.append(
                    dict(
                        tag=tag,
                        units=units,
                        period_start=start,
                        period_end=entry["end"],
                        duration_days=duration,
                        period_basis=(
                            "instant"
                            if "start" not in entry
                            else (
                                "annual"
                                if duration >= 350
                                else "cumulative_or_quarterly_requires_review"
                            )
                        ),
                        value=entry["val"],
                        accession=entry["accn"],
                        filed=entry["filed"],
                        classification="unverified candidate",
                    )
                )
    return rows


def standalone_quarter(current, previous):
    if (
        current["period_start"] != previous["period_start"]
        or current["units"] != previous["units"]
    ):
        raise ValueError("Cannot subtract incompatible cumulative quarters")
    if current["period_end"] <= previous["period_end"]:
        raise ValueError("Quarter ordering invalid")
    return current["value"] - previous["value"]


# Preserved implementation notes
# At most five requests/sec, below SEC's published maximum.
