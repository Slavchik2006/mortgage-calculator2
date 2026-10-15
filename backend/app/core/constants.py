"""Limits from docs/v1/01-functional.md section 2 (single source of truth)."""
from decimal import Decimal

MAX_PRICE = Decimal(10**12)
MAX_TAX_INSURANCE = Decimal(10**12)  # technical cap, assumption A5
RATE_MIN = Decimal(0)
RATE_MAX = Decimal(25)
TERM_MIN = 1
TERM_MAX = 40
MAX_DECIMALS = 2
MONTHS_PER_YEAR = 12
DECIMAL_PRECISION = 60
