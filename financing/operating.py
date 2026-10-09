"""Company-level operating forecasts; working capital is a balance, not a plug."""

from datetime import date
import calendar


def period_date(start, months):
    d = date.fromisoformat(start)
    index = d.year * 12 + d.month - 1 + months
    y, m = divmod(index, 12)
    m += 1
    return date(y, m, min(d.day, calendar.monthrange(y, m)[1])).isoformat()


def starting_nwc(company):
    b = company.get("closing_working_capital")
    return (
        b["inventory"] + b["receivables"] - b["payables"]
        if b
        else trailing(company)["nwc"]
    )


def trailing(company):
    r = company["revenue"]
    ebitda = (
        r * (company["gross_margin"] - company["variable_opex"])
        - company["fixed_opex"]
        - company["rent"]
    )
    cogs = r * (1 - company["gross_margin"])
    return dict(
        revenue=r,
        ebitda=ebitda,
        da=r * company["da_ratio"],
        rent=company["rent"],
        nwc=cogs * (company["dio"] - company["dpo"]) / 365 + r * company["dso"] / 365,
    )


def forecast(config, shock):
    result = []
    for company in config["companies"]:
        base_revenue = company["revenue"]
        previous = starting_nwc(company)
        for y in range(5):
            base_revenue *= 1 + company["growth"][y]
            revenue = base_revenue * (1 + shock.revenue)
            gm = company["gross_margin"] + shock.margin
            cogs = revenue * (1 - gm)
            variable = revenue * company["variable_opex"]
            fixed = company["fixed_opex"] * (1 + company["fixed_growth"]) ** (y + 1)
            rent = company["rent"] * (1 + company["fixed_growth"]) ** (y + 1)
            ebitda = revenue - cogs - variable - fixed - rent
            da = revenue * company["da_ratio"]
            wc_cogs = revenue * company.get("working_capital_cost_ratio", 1 - gm)
            inventory = wc_cogs * (company["dio"] + shock.inventory_days) / 365
            receivables = revenue * company["dso"] / 365
            payables = wc_cogs * company["dpo"] / 365
            nwc = inventory + receivables - payables
            result.append(
                dict(
                    company=company["name"],
                    year=y + 1,
                    revenue=revenue,
                    cogs=cogs,
                    variable_opex=variable,
                    fixed_opex=fixed,
                    rent=rent,
                    rent_cash=rent * company["rent_cash_factor"],
                    ebitda=ebitda,
                    da=da,
                    ebit=ebitda - da,
                    capex=revenue * company["capex_ratio"],
                    inventory=inventory,
                    receivables=receivables,
                    payables=payables,
                    nwc=nwc,
                    delta_nwc=nwc - previous,
                )
            )
            previous = nwc
    return result


def operating_periods(config, shock, frequency=1):
    annual = forecast(config, shock)
    rows = []
    previous = sum((starting_nwc(c) for c in config["companies"]))
    for year in range(1, 6):
        pair = [r for r in annual if r["year"] == year]
        sy = config["synergies"]
        ramp_index = year - 1 - shock.synergy_delay
        saving = (
            sy["run_rate"] * sy["ramp"][ramp_index] * shock.synergy_factor
            if ramp_index >= 0
            else 0.0
        )
        for q in range(frequency):
            row = dict(
                year=year,
                quarter=q + 1,
                period=(year - 1) * frequency + q + 1,
                time=year - 1 + (q + 1) / frequency,
                period_end=period_date(
                    config["closing_date"],
                    ((year - 1) * frequency + q + 1) * 12 // frequency,
                ),
            )
            for k in (
                "revenue",
                "cogs",
                "variable_opex",
                "fixed_opex",
                "rent",
                "rent_cash",
                "da",
                "capex",
            ):
                row[k] = sum(
                    (
                        r[k]
                        * (
                            config["companies"][i]["seasonality"][q]
                            if frequency == 4
                            and k in ("revenue", "cogs", "variable_opex", "capex")
                            else 1 / frequency
                        )
                        for i, r in enumerate(pair)
                    )
                )
            row["inventory"] = sum(
                (
                    r["inventory"]
                    * (
                        config["companies"][i]["inventory_seasonality"][q]
                        if frequency == 4
                        else 1
                    )
                    for i, r in enumerate(pair)
                )
            )
            row["receivables"] = sum((r["receivables"] for r in pair))
            row["payables"] = sum((r["payables"] for r in pair))
            row["nwc"] = row["inventory"] + row["receivables"] - row["payables"]
            row["delta_nwc"] = row["nwc"] - previous
            previous = row["nwc"]
            row["synergy"] = saving / frequency
            row["integration"] = sy["integration"][year - 1] / frequency
            row["ebitda"] = (
                row["revenue"]
                - row["cogs"]
                - row["variable_opex"]
                - row["fixed_opex"]
                - row["rent"]
                + row["synergy"]
            )
            row["ebit"] = row["ebitda"] - row["da"]
            rows.append(row)
    return (annual, rows)
