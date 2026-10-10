"""All public outputs derive from this fresh evaluation, never a saved preference."""

from .evidence import check_evidence
from .model import calculate


def build_report(
    case,
    root,
    illustrative_inputs=None,
    database_path=None,
    full=True,
    public_information=False,
    public_overrides=None,
):
    from .credit import stress_grid
    from .markets import bond_risk

    evidence = check_evidence(case, root)
    from .historical_review import (
        gap_register,
        supported_calculations,
        partial_sensitivities,
        financing_sensitivities,
    )

    report = {
        "recommendation_status": evidence["status"],
        "preferred_structure": None,
        "historical_analysis_complete": False,
        "historical_results": [],
        "evidence": evidence,
        "analysis_limitation": "Historical forecasts and preferences require verified material evidence and a reconciled historical model mapping. Synthetic engineering is independent.",
        "illustrative_label": "Illustrative scenario analysis — anonymous synthetic companies; not historical results.",
        "illustrative_results": [],
        "engineering_status": "Not run",
        "historical_mapping_error": None,
    }
    report["bond_lab"] = bond_risk()
    report["historical_gap_register"] = gap_register(case, evidence)
    report["supported_historical_calculations"] = supported_calculations(evidence)
    report["historical_operating_sensitivities"] = partial_sensitivities(evidence)
    report["historical_financing_sensitivities"] = financing_sensitivities(evidence)
    report["historical_capacity_status"] = (
        "Unavailable: complete funding uses, eligible cash, instrument schedules and contractual borrowing capacity remain unresolved."
        if evidence["blocked"]
        else "Subject to historical model mapping"
    )
    if public_information:
        from .public_case import analyse_public

        report["public_information"] = analyse_public(
            evidence, report["historical_gap_register"], full, public_overrides
        )
        public_bundle = report["public_information"]
        if public_bundle.get("config"):
            public_bundle["joint_stress"] = stress_grid(public_bundle["config"])
        from .analysis import code_id

        report["public_information"]["provenance"] = {
            "case_id": evidence["case_id"],
            "source_state_id": evidence["source_state_id"],
            "code_id": code_id(),
            "cutoff": evidence["cutoff"],
        }
        report["historical_capacity_status"] = (
            "Strict assessment remains blocked. Separately scoped public-information schedules and analytical capacity are shown with their own dependency status."
        )
        report["analysis_limitation"] = (
            "The strict assessment remains blocked. Public-information projections use verified starting values, relevant public contracts and explicit forecasts; each output has its own dependency status. No execution, covenant-compliance or overall financing preference is asserted."
        )
    if database_path:
        from . import database as dbm

        db = dbm.connect(database_path)
        dbm.store_evidence(db, case, evidence)
        dbm.store_historical_review(db, report)
        if public_information:
            import json
            from .evidence import fingerprint

            with db:
                db.execute(
                    "INSERT OR REPLACE INTO public_information_reviews VALUES(?,?)",
                    (
                        fingerprint(report["public_information"]),
                        json.dumps(report["public_information"]),
                    ),
                )
        db.close()
    if (
        illustrative_inputs is not None
        and illustrative_inputs.get("schema_version") != 2
    ):
        report["illustrative_results"] = calculate(illustrative_inputs)
        return report
    from .analysis import analyse
    from .evidence import fingerprint
    from . import database as dbm

    config = None
    if illustrative_inputs is not None:
        if illustrative_inputs.get("mode") != "synthetic":
            raise ValueError(
                "Illustrative mode requires explicit synthetic configuration"
            )
        config = illustrative_inputs
    elif not evidence["blocked"]:
        from .historical import historical_config

        try:
            config = historical_config(case, evidence)
        except (ValueError, KeyError, TypeError) as exc:
            report["historical_mapping_error"] = str(exc)
            report["recommendation_status"] = (
                "Blocked — incomplete or unreconciled historical model mapping."
            )
    if config is not None:
        db = dbm.connect(database_path) if database_path else None
        if db:
            cid = dbm.store_config(db, config)
            dbm.store_evidence(db, case, evidence)
            config = dbm.load_config(db, cid)
        bundle = analyse(config, full)
        bundle["joint_stress"] = stress_grid(config)
        report["model"] = bundle
        report["config_id"] = fingerprint(config)
        report["engineering_status"] = (
            (
                "Complete synthetic model run"
                if full
                else "Partial synthetic preview; stress and sensitivity suite omitted"
            )
            if config["mode"] == "synthetic"
            else "Historical model run"
        )
        if config["mode"] == "synthetic":
            report["illustrative_results"] = bundle["base"]
        else:
            report["historical_results"] = bundle["base"]
            report["historical_analysis_complete"] = True
            report["recommendation_status"] = (
                "Qualified historical analysis — conditional on stated assumptions."
            )
            report["preferred_structure"] = bundle["recommendation"][
                "preferred_structure"
            ]
        if db:
            report["run_id"] = dbm.store_run(
                db,
                cid,
                fingerprint(evidence),
                bundle["code_id"],
                bundle,
                report["recommendation_status"],
            )
            db.close()
    report["verified_observations"] = [
        r for r in evidence["rows"] if r["classification"] == "verified fact"
    ]
    return report


# Preserved implementation notes
# Do not read recommendation/preferred_structure/status from untrusted input.
# Preserved foundation benchmark and output regression.
# Calculations consume the stored canonical configuration.
