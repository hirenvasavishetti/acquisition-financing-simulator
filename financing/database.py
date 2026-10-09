"""Versioned SQLite storage used to load inputs and inspect analytical results."""

import json
import sqlite3
from pathlib import Path
from .evidence import fingerprint

SCHEMA = "\nPRAGMA foreign_keys=ON;\nCREATE TABLE IF NOT EXISTS schema_version(version INTEGER PRIMARY KEY CHECK(version=1));\nINSERT OR IGNORE INTO schema_version VALUES(1);\nCREATE TABLE IF NOT EXISTS configurations(id TEXT PRIMARY KEY,mode TEXT NOT NULL CHECK(mode IN ('synthetic','historical')),payload TEXT NOT NULL);\nCREATE TABLE IF NOT EXISTS companies(id TEXT PRIMARY KEY,name TEXT NOT NULL);\nCREATE TABLE IF NOT EXISTS source_documents(id TEXT PRIMARY KEY,url TEXT NOT NULL,published TEXT NOT NULL,retrieved TEXT NOT NULL,sha256 TEXT NOT NULL,payload TEXT NOT NULL);\nCREATE TABLE IF NOT EXISTS financial_observations(id TEXT PRIMARY KEY,company_id TEXT REFERENCES companies(id),source_id TEXT REFERENCES source_documents(id),metric TEXT NOT NULL,period_start TEXT,period_end TEXT,units TEXT NOT NULL,classification TEXT NOT NULL,value_json TEXT NOT NULL,config_id TEXT REFERENCES configurations(id));\nCREATE TABLE IF NOT EXISTS debt_instruments(id TEXT PRIMARY KEY,company_id TEXT NOT NULL REFERENCES companies(id),config_id TEXT NOT NULL REFERENCES configurations(id),principal REAL NOT NULL CHECK(principal>=0),maturity REAL NOT NULL,payload TEXT NOT NULL);\nCREATE TABLE IF NOT EXISTS market_data(id TEXT PRIMARY KEY,config_id TEXT REFERENCES configurations(id),series TEXT NOT NULL,period INTEGER NOT NULL,value REAL NOT NULL,basis TEXT NOT NULL,source_id TEXT REFERENCES source_documents(id));\nCREATE TABLE IF NOT EXISTS assumptions(id TEXT PRIMARY KEY,config_id TEXT NOT NULL REFERENCES configurations(id),name TEXT NOT NULL,value_json TEXT NOT NULL,rationale TEXT NOT NULL);\nCREATE TABLE IF NOT EXISTS model_runs(id TEXT PRIMARY KEY,config_id TEXT NOT NULL REFERENCES configurations(id),evidence_id TEXT NOT NULL,code_id TEXT NOT NULL,status TEXT NOT NULL,payload TEXT NOT NULL);\nCREATE TABLE IF NOT EXISTS annual_results(run_id TEXT REFERENCES model_runs(id),structure TEXT,scenario TEXT,year INTEGER CHECK(year BETWEEN 1 AND 5),cash REAL NOT NULL,debt REAL NOT NULL,interest REAL NOT NULL,ebitda REAL NOT NULL,maturity_gap REAL NOT NULL,PRIMARY KEY(run_id,structure,scenario,year));\nCREATE TABLE IF NOT EXISTS breaches(run_id TEXT REFERENCES model_runs(id),structure TEXT,scenario TEXT,period INTEGER,constraint_name TEXT,headroom REAL);\nCREATE VIEW IF NOT EXISTS scenario_summary AS SELECT run_id,structure,scenario,MIN(cash) AS min_cash, SUM(interest) AS total_interest,MAX(maturity_gap) AS max_maturity_gap FROM annual_results GROUP BY run_id,structure,scenario;\nCREATE INDEX IF NOT EXISTS observation_lookup ON financial_observations(company_id,metric,period_end);\nCREATE TABLE IF NOT EXISTS historical_reviews(id TEXT PRIMARY KEY,status TEXT NOT NULL,payload TEXT NOT NULL);\nCREATE TABLE IF NOT EXISTS public_information_reviews(id TEXT PRIMARY KEY,payload TEXT NOT NULL);\n"


def connect(path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path)
    db.row_factory = sqlite3.Row
    db.executescript(SCHEMA)
    if [r[0] for r in db.execute("SELECT version FROM schema_version")] != [1]:
        raise ValueError("Unsupported database schema")
    return db


def store_config(db, config):
    cid = fingerprint(config)
    with db:
        db.execute(
            "INSERT OR IGNORE INTO configurations VALUES(?,?,?)",
            (cid, config["mode"], json.dumps(config, sort_keys=True)),
        )
        for c in config["companies"]:
            company = f"{config['mode']}:{c['name']}"
            db.execute(
                "INSERT OR IGNORE INTO companies VALUES(?,?)", (company, c["name"])
            )
            for year in (2022, 2023, 2024):
                for key in ("revenue", "gross_margin", "cash", "rent"):
                    if config["mode"] != "synthetic":
                        continue
                    value = (
                        c[key] / 1.025 ** (2024 - year) if key == "revenue" else c[key]
                    )
                    ident = fingerprint([cid, company, year, key])
                    db.execute(
                        "INSERT OR IGNORE INTO financial_observations VALUES(?,?,?,?,?,?,?,?,?,?)",
                        (
                            ident,
                            company,
                            None,
                            key,
                            f"{year}-01-01",
                            f"{year}-12-31",
                            "USD millions" if key != "gross_margin" else "fraction",
                            "synthetic input",
                            json.dumps(value),
                            cid,
                        ),
                    )
            for d in c["debts"]:
                db.execute(
                    "INSERT OR IGNORE INTO debt_instruments VALUES(?,?,?,?,?,?)",
                    (
                        fingerprint([cid, d["id"]]),
                        company,
                        cid,
                        d["principal"],
                        d["maturity"],
                        json.dumps(d),
                    ),
                )
        for section in ("policy", "new_debt", "synergies", "transaction", "quarterly"):
            for key, value in config[section].items():
                db.execute(
                    "INSERT OR IGNORE INTO assumptions VALUES(?,?,?,?,?)",
                    (
                        fingerprint([cid, section, key]),
                        cid,
                        f"{section}.{key}",
                        json.dumps(value),
                        (
                            "Explicit synthetic scenario choice"
                            if config["mode"] == "synthetic"
                            else "See historical assumption register"
                        ),
                    ),
                )
        for year, value in enumerate(config["new_debt"]["benchmark"], 1):
            db.execute(
                "INSERT OR IGNORE INTO market_data VALUES(?,?,?,?,?,?,?)",
                (
                    fingerprint([cid, year, "benchmark"]),
                    cid,
                    "floating benchmark",
                    year,
                    value,
                    (
                        "Synthetic assumption, not a market observation"
                        if config["mode"] == "synthetic"
                        else "Historical assumption register"
                    ),
                    None,
                ),
            )
    return cid


def store_historical_review(db, report):
    payload = {
        k: report[k]
        for k in (
            "recommendation_status",
            "historical_gap_register",
            "supported_historical_calculations",
            "historical_operating_sensitivities",
            "historical_financing_sensitivities",
            "historical_capacity_status",
        )
    }
    with db:
        db.execute(
            "INSERT OR REPLACE INTO historical_reviews VALUES(?,?,?)",
            (
                fingerprint(
                    [
                        report["evidence"]["case_id"],
                        report["evidence"]["source_state_id"],
                    ]
                ),
                report["recommendation_status"],
                json.dumps(payload),
            ),
        )


def load_config(db, cid):
    row = db.execute("SELECT payload FROM configurations WHERE id=?", (cid,)).fetchone()
    if not row:
        raise ValueError("Configuration not found")
    return json.loads(row[0])


def store_evidence(db, case, report):
    with db:
        for s in case.get("sources", []):
            db.execute(
                "INSERT OR REPLACE INTO source_documents VALUES(?,?,?,?,?,?)",
                (
                    s["id"],
                    s["url"],
                    s["published"],
                    s["retrieved"],
                    s["sha256"],
                    json.dumps(s),
                ),
            )
        for o in case.get("observations", []):
            company = o.get("company", "transaction")
            db.execute(
                "INSERT OR IGNORE INTO companies VALUES(?,?)", (company, company)
            )
            src = next(
                (
                    s["id"]
                    for s in case.get("sources", [])
                    if any((c["key"] == o["key"] for c in s.get("claims", [])))
                ),
                None,
            )
            status = next(
                (r["classification"] for r in report["rows"] if r["key"] == o["key"])
            )
            db.execute(
                "INSERT OR REPLACE INTO financial_observations VALUES(?,?,?,?,?,?,?,?,?,?)",
                (
                    fingerprint(o),
                    company,
                    src,
                    o["key"],
                    o.get("period_start"),
                    o.get("period_end"),
                    o.get("units", "scenario choice"),
                    status,
                    json.dumps(o.get("value")),
                    None,
                ),
            )


def store_run(db, cid, evidence_id, code_id, bundle, status):
    rid = fingerprint([cid, evidence_id, code_id, bundle.get("analysis_scope", "full")])
    with db:
        db.execute(
            "INSERT OR REPLACE INTO model_runs VALUES(?,?,?,?,?,?)",
            (rid, cid, evidence_id, code_id, status, json.dumps(bundle)),
        )
        db.execute("DELETE FROM annual_results WHERE run_id=?", (rid,))
        db.execute("DELETE FROM breaches WHERE run_id=?", (rid,))
        for r in bundle["comparisons"]:
            for a in r["years"]:
                db.execute(
                    "INSERT INTO annual_results VALUES(?,?,?,?,?,?,?,?,?)",
                    (
                        rid,
                        r["structure"],
                        r["scenario"],
                        a["year"],
                        a["closing_cash"],
                        a["closing_debt"],
                        a["interest"],
                        a["ebitda"],
                        a["maturity_gap"],
                    ),
                )
            for b in r["breaches"]:
                db.execute(
                    "INSERT INTO breaches VALUES(?,?,?,?,?,?)",
                    (
                        rid,
                        r["structure"],
                        r["scenario"],
                        b["period"],
                        b["constraint"],
                        b["headroom"],
                    ),
                )
    return rid


QUERIES = {
    "public": "SELECT id,json_extract(payload,'$.scope') AS scope,json_extract(payload,'$.provenance.code_id') AS code_id,json_extract(payload,'$.comparison_summary') AS comparison_summary FROM public_information_reviews",
    "summary": "SELECT * FROM scenario_summary ORDER BY structure,scenario",
    "gaps": "SELECT * FROM breaches ORDER BY structure,scenario,period",
    "sources": "SELECT id,url,published,retrieved FROM source_documents ORDER BY published",
    "observations": "SELECT company_id,metric,period_end,classification,value_json FROM financial_observations ORDER BY company_id,metric,period_end",
    "maturities": "SELECT company_id,principal,maturity,payload FROM debt_instruments ORDER BY maturity",
}

# Preserved implementation notes
# Demo history is flat for stocks/margins and backcast for revenue.
# It is explicitly synthetic; historical ingestion uses source observations.
