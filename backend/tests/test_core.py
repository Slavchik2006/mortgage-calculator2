import sys
from decimal import Decimal as D
from pathlib import Path

import pytest

from app.api.serialization import money
from app.core.calculation import calculate
from app.core.types import LoanInput
from app.core.validation import MESSAGES, validate

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "docs" / "v1"))
import reference_values as ref  # noqa: E402  independent Decimal reference (60 digits)


def raw(**kw):
    base = dict(price="250000", downPayment="50000", annualRate="6", termYears="30", annualTax="", annualInsurance="")
    base.update(kw)
    return base


# ---- validation ----
def test_valid_defaults_optional_to_zero():
    v = validate(raw())
    assert isinstance(v, LoanInput)
    assert (v.annual_tax, v.annual_insurance, v.term_years) == (0, 0, 30)


@pytest.mark.parametrize("field,value,msg", [
    ("price", "", "REQUIRED"), ("price", "abc", "NUMERIC"), ("price", "1e3", "NUMERIC"),
    ("price", "1,5", "NUMERIC"), ("price", "0", "RANGE_PRICE"), ("price", "-5", "RANGE_PRICE"),
    ("price", "1000000000000.01", "RANGE_PRICE"), ("price", "10.123", "DEC2"),
    ("annualRate", "25.01", "RANGE_RATE"), ("annualRate", "-0.01", "RANGE_RATE"), ("annualRate", "4.567", "DEC2"),
    ("termYears", "0", "RANGE_TERM"), ("termYears", "41", "RANGE_TERM"), ("termYears", "10.5", "INT_TERM"),
    ("annualTax", "-1", "RANGE_TAXINS"), ("annualInsurance", "x", "NUMERIC"),
    ("downPayment", "", "REQUIRED"), ("downPayment", "-1", "RANGE_DOWN"),
])
def test_invalid_field(field, value, msg):
    e = validate(raw(**{field: value}))
    assert e == {field: MESSAGES[msg]}


def test_down_must_be_less_than_price():
    assert validate(raw(downPayment="250000")) == {"downPayment": MESSAGES["RANGE_DOWN"]}


def test_range_checked_before_precision():
    assert validate(raw(price="2000000000000.123")) == {"price": MESSAGES["RANGE_PRICE"]}


def test_boundaries_and_whitespace_and_negative_zero():
    v = validate(raw(price=" 1000000000000 ", downPayment="-0", annualRate="25", termYears="40"))
    assert isinstance(v, LoanInput) and v.down_payment == 0 and not v.down_payment.is_signed()


def test_missing_keys_are_required():
    assert set(validate({})) == {"price", "downPayment", "annualRate", "termYears"}


def test_trailing_newline_is_trimmed_not_smuggled():
    assert isinstance(validate(raw(price="100000\n")), LoanInput)
    assert validate(raw(price="1\n0")) == {"price": MESSAGES["NUMERIC"]}


# ---- calculation vs independent reference ----
@pytest.mark.parametrize("name", list(ref.LOANS))
def test_matches_reference(name):
    price, down, rate, years = ref.LOANS[name]
    v = validate(dict(price=price, downPayment=down, annualRate=rate, termYears=str(years)))
    assert isinstance(v, LoanInput)
    res = calculate(v)
    p, r, n, m = ref.loan(price, down, rate, years)
    assert res.summary.principal == p
    assert abs(res.summary.monthly_pi - m) <= D("1e-30")
    rows = ref.schedule(p, r, n, m)
    assert len(res.schedule) == n
    for got, (k, pay, i, pr, bal) in zip(res.schedule, rows):
        assert got.month == k
        assert abs(got.payment - pay) <= D("1e-20") * max(1, abs(pay))
        assert abs(got.interest - i) <= D("1e-20") * max(1, abs(i))
        assert abs(got.balance - bal) <= D("1e-20") * max(1, abs(p))


def test_known_value_v1():
    res = calculate(validate(raw()))
    assert format(res.summary.monthly_pi, ".2f") == "1199.10"


def test_invariants():
    res = calculate(validate(raw(annualTax="3000", annualInsurance="600")))
    s = res.summary
    assert res.schedule[-1].balance == 0
    assert abs(sum(x.principal for x in res.schedule) - s.principal) <= D("1e-20")
    assert abs(sum(x.interest for x in res.schedule) - s.total_interest) <= D("1e-20")
    assert s.monthly_total == s.monthly_pi + s.monthly_tax + s.monthly_insurance
    assert (s.monthly_tax, s.monthly_insurance) == (250, 50)


def test_zero_rate():
    res = calculate(validate(raw(price="120000", downPayment="0", annualRate="0", termYears="10")))
    assert res.summary.monthly_pi == 1000
    assert all(x.interest == 0 and x.payment == 1000 for x in res.schedule)


def test_precondition_violation_raises():
    bad = LoanInput(D(100), D(100), D(5), 10, D(0), D(0))
    with pytest.raises(ValueError):
        calculate(bad)


def test_money_serialisation():
    assert money(D("1000")) == "1000"
    assert money(D("0.10")) == "0.1"
    assert money(D("-0.0000000000001")) == "0"
    assert money(D("1E+12")) == "1000000000000"
    assert money(D("1216.04136")) == "1216.04136"
