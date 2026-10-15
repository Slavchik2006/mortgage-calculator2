"""Shared data contracts (no logic)."""
from dataclasses import dataclass
from decimal import Decimal

FIELDS = ("price", "downPayment", "annualRate", "termYears", "annualTax", "annualInsurance")

# field name -> message; empty dict means valid
FieldErrors = dict[str, str]


@dataclass(frozen=True)
class LoanInput:
    price: Decimal
    down_payment: Decimal
    annual_rate_pct: Decimal
    term_years: int
    annual_tax: Decimal
    annual_insurance: Decimal


@dataclass(frozen=True)
class ScheduleRow:
    month: int
    payment: Decimal
    interest: Decimal
    principal: Decimal
    balance: Decimal


@dataclass(frozen=True)
class Summary:
    principal: Decimal
    monthly_pi: Decimal
    monthly_tax: Decimal
    monthly_insurance: Decimal
    monthly_total: Decimal
    total_paid: Decimal  # P&I only: M * n
    total_interest: Decimal  # M * n - P


@dataclass(frozen=True)
class MortgageResult:
    summary: Summary
    schedule: list[ScheduleRow]
