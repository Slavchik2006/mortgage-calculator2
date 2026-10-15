"""MortgageResult -> JSON-ready dict. Money is a decimal string (no float loss).

Values are cut to 12 decimals (half-even, far below the 2 dp display rounding) to keep the
480-row payload small; the frontend still does the only display rounding.
"""
from decimal import Decimal

from ..core.types import MortgageResult

_Q = Decimal(1).scaleb(-12)


def money(x: Decimal) -> str:
    s = format(x.quantize(_Q), "f")
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    return "0" if s in ("", "-0") else s


def result_to_dict(res: MortgageResult) -> dict:
    s = res.summary
    return {
        "summary": {
            "principal": money(s.principal),
            "monthlyPI": money(s.monthly_pi),
            "monthlyTax": money(s.monthly_tax),
            "monthlyInsurance": money(s.monthly_insurance),
            "monthlyTotal": money(s.monthly_total),
            "totalPaid": money(s.total_paid),
            "totalInterest": money(s.total_interest),
        },
        "schedule": [
            {
                "month": row.month,
                "payment": money(row.payment),
                "interest": money(row.interest),
                "principal": money(row.principal),
                "balance": money(row.balance),
            }
            for row in res.schedule
        ],
    }
