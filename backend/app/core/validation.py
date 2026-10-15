"""Raw strings -> LoanInput | FieldErrors. Pure; never clamps or corrects (F section 6)."""
import re
from collections.abc import Mapping
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
from .types import FIELDS, FieldErrors, LoanInput

MESSAGES = {
    "REQUIRED": "This field is required.",
    "NUMERIC": "Enter a number using digits and . only.",
    "RANGE_PRICE": "Price must be more than 0 and at most 1,000,000,000,000.",
    "RANGE_DOWN": "Down payment must be 0 or more and less than the home price.",
    "RANGE_RATE": "Rate must be between 0 and 25.",
    "RANGE_TERM": "Term must be between 1 and 40 years.",
    "RANGE_TAXINS": "Must be between 0 and 1,000,000,000,000.",
    "DEC2": "Use at most 2 decimal places.",
    "INT_TERM": "Enter a whole number of years.",
}

_NUMERIC = re.compile(r"-?[0-9]+(\.[0-9]+)?")
_WS = " \t\n\r\f\v"

# field -> (optional, in_range, range message, integer)
_SPECS = {
    "price": (False, lambda n: 0 < n <= MAX_PRICE, MESSAGES["RANGE_PRICE"], False),
    "downPayment": (False, lambda n: 0 <= n <= MAX_PRICE, MESSAGES["RANGE_DOWN"], False),
    "annualRate": (False, lambda n: RATE_MIN <= n <= RATE_MAX, MESSAGES["RANGE_RATE"], False),
    "termYears": (False, lambda n: TERM_MIN <= n <= TERM_MAX, MESSAGES["RANGE_TERM"], True),
    "annualTax": (True, lambda n: 0 <= n <= MAX_TAX_INSURANCE, MESSAGES["RANGE_TAXINS"], False),
    "annualInsurance": (True, lambda n: 0 <= n <= MAX_TAX_INSURANCE, MESSAGES["RANGE_TAXINS"], False),
}


def _parse_field(raw, optional, in_range, range_msg, integer):
    """Rule order per field: required -> numeric -> range -> precision (A2)."""
    s = (raw if isinstance(raw, str) else "").strip(_WS)
    if s == "":
        return (Decimal(0), None) if optional else (None, MESSAGES["REQUIRED"])
    if _NUMERIC.fullmatch(s) is None:
        return None, MESSAGES["NUMERIC"]
    n = Decimal(s)
    if not in_range(n):
        return None, range_msg
    if "." in s:
        if integer:
            return None, MESSAGES["INT_TERM"]
        if len(s) - s.index(".") - 1 > MAX_DECIMALS:
            return None, MESSAGES["DEC2"]
    return abs(n) if n == 0 else n, None  # -0 -> +0


def validate(raw: Mapping[str, object]) -> LoanInput | FieldErrors:
    """Return a LoanInput, or a non-empty FieldErrors dict."""
    values: dict[str, Decimal] = {}
    errors: FieldErrors = {}
    for field in FIELDS:
        optional, in_range, range_msg, integer = _SPECS[field]
        value, error = _parse_field(raw.get(field), optional, in_range, range_msg, integer)
        if error is not None:
            errors[field] = error
        else:
            values[field] = value
    if "price" not in errors and "downPayment" not in errors and values["downPayment"] >= values["price"]:
        errors["downPayment"] = MESSAGES["RANGE_DOWN"]
    if errors:
        return errors
    return LoanInput(
        price=values["price"],
        down_payment=values["downPayment"],
        annual_rate_pct=values["annualRate"],
        term_years=int(values["termYears"]),
        annual_tax=values["annualTax"],
        annual_insurance=values["annualInsurance"],
    )
