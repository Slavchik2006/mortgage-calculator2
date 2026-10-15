"""LoanInput -> MortgageResult. Pure, exact (decimal, 60 digits), no rounding (F sections 3-4)."""
from decimal import Decimal, localcontext

from .constants import (
    DECIMAL_PRECISION,
    MAX_PRICE,
    MONTHS_PER_YEAR,
    RATE_MAX,
    RATE_MIN,
    TERM_MAX,
    TERM_MIN,
)
from .types import LoanInput, MortgageResult, ScheduleRow, Summary


def _check(cond: bool, msg: str) -> None:
    if not cond:
        raise ValueError(f"calculate: {msg}")  # programmer error, not a user-facing path


def calculate(inp: LoanInput) -> MortgageResult:
    _check(0 < inp.price <= MAX_PRICE, "invalid price")
    _check(0 <= inp.down_payment < inp.price, "invalid down payment")
    _check(RATE_MIN <= inp.annual_rate_pct <= RATE_MAX, "invalid rate")
    _check(TERM_MIN <= inp.term_years <= TERM_MAX, "invalid term")
    _check(inp.annual_tax >= 0 and inp.annual_insurance >= 0, "invalid tax/insurance")

    with localcontext() as ctx:
        ctx.prec = DECIMAL_PRECISION
        n = inp.term_years * MONTHS_PER_YEAR
        p = inp.price - inp.down_payment
        r = inp.annual_rate_pct / 100 / MONTHS_PER_YEAR
        m = p / n if r == 0 else p * r / (1 - (1 + r) ** (-n))

        schedule: list[ScheduleRow] = []
        balance = p
        for k in range(1, n + 1):
            interest = balance * r
            payment = m if k < n else balance + interest  # final payment closes the loan
            principal = payment - interest
            balance = Decimal(0) if k == n else balance - principal
            schedule.append(ScheduleRow(k, payment, interest, principal, balance))

        monthly_tax = inp.annual_tax / MONTHS_PER_YEAR
        monthly_ins = inp.annual_insurance / MONTHS_PER_YEAR
        total_paid = m * n
        summary = Summary(
            principal=p,
            monthly_pi=m,
            monthly_tax=monthly_tax,
            monthly_insurance=monthly_ins,
            monthly_total=m + monthly_tax + monthly_ins,
            total_paid=total_paid,
            total_interest=total_paid - p,
        )
    return MortgageResult(summary, schedule)
