"""Catalog of the six loan inputs. Built from constants.py (the source of truth); the database
`parameters` table mirrors it and is checked against it at startup (storage/supabase.py)."""
from dataclasses import dataclass
from decimal import Decimal

from .constants import (
    MAX_DECIMALS,
    MAX_PRICE,
    MAX_TAX_INSURANCE,
    RATE_MAX,
    RATE_MIN,
    TERM_MAX,
    TERM_MIN,
)


@dataclass(frozen=True)
class Parameter:
    code: str
    label: str
    kind: str  # money | percent | integer
    required: bool
    min_value: Decimal
    max_value: Decimal
    max_decimals: int
    sort_order: int


_CENT = Decimal("0.01")

PARAMETERS: tuple[Parameter, ...] = (
    Parameter("price", "Home price (EUR)", "money", True, _CENT, MAX_PRICE, MAX_DECIMALS, 1),
    Parameter("downPayment", "Down payment (EUR)", "money", True, Decimal(0), MAX_PRICE, MAX_DECIMALS, 2),
    Parameter("annualRate", "Annual interest rate (%)", "percent", True, RATE_MIN, RATE_MAX, MAX_DECIMALS, 3),
    Parameter("termYears", "Term (years)", "integer", True, Decimal(TERM_MIN), Decimal(TERM_MAX), 0, 4),
    Parameter("annualTax", "Annual property tax (EUR)", "money", False, Decimal(0), MAX_TAX_INSURANCE, MAX_DECIMALS, 5),
    Parameter("annualInsurance", "Annual home insurance (EUR)", "money", False, Decimal(0), MAX_TAX_INSURANCE, MAX_DECIMALS, 6),
)


def diff_with_rows(rows: list[dict]) -> list[str]:
    """Compare catalog rows from the database with PARAMETERS; return human-readable differences."""
    by_code = {r["code"]: r for r in rows}
    problems: list[str] = []
    for p in PARAMETERS:
        r = by_code.pop(p.code, None)
        if r is None:
            problems.append(f"{p.code}: missing in database")
            continue
        got = (r["kind"], bool(r["required"]), Decimal(str(r["min_value"])), Decimal(str(r["max_value"])),
               int(r["max_decimals"]), int(r["sort_order"]))
        want = (p.kind, p.required, p.min_value, p.max_value, p.max_decimals, p.sort_order)
        if got != want:
            problems.append(f"{p.code}: database {got} != code {want}")
    problems += [f"{code}: unknown in code" for code in by_code]
    return problems
