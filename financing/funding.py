"""One itemised transaction-use calculation, shared by every output."""

from dataclasses import dataclass, asdict


@dataclass(frozen=True)
class FundingUses:
    cash_consideration: float
    debt_principal_repaid: float
    transaction_expenses: float
    award_settlement_reserve: float = 0.0
    redemption_premium: float = 0.0
    accrued_interest: float = 0.0
    lc_collateral_reserve: float = 0.0
    other_closing_uses: float = 0.0
    financing_fees: float = 0.0

    def rows(self):
        return asdict(self)

    @property
    def total(self):
        return sum(self.rows().values())


def replace_acquisition_debt(opening, amount, fee_rate, convention):
    """Equity replaces acquisition borrowing; all nonfinancing uses stay fixed.

    D = (acquisition debt + other nonfinancing uses funded by debt)/(1-fee).
    Equity is the displaced acquisition principal, not an unexplained cash plug.
    """
    original = opening["acquisition_borrowing"]
    opening["analytical_equity"] = original - amount
    if convention == "issued_debt":
        other = (
            opening["cash_uses"]
            - opening["financing_fees"]
            - opening["cash_contribution"]
            - original
        )
        total = (amount + other) / (1 - fee_rate)
        opening["financing_fees"] = total * fee_rate
        opening["itemised_uses"]["financing_fees"] = opening["financing_fees"]
        opening["cash_uses"] = sum(opening["itemised_uses"].values())
        opening["borrowing_for_refinancing_and_fees"] = total - amount
    elif convention == "fixed_budget":
        total = amount + opening["borrowing_for_refinancing_and_fees"]
    else:
        raise ValueError("Fee convention must be fixed_budget or issued_debt")
    opening["acquisition_borrowing"] = amount
    opening["total_new_borrowing"] = total
    opening["opening_debt"] = opening["retained_debt"] + total
    opening["sources_uses_difference"] = (
        opening["cash_contribution"]
        + total
        + opening["analytical_equity"]
        - opening["cash_uses"]
    )
