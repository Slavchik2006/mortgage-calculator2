"""The parameter catalog must agree with validation, and with the database migration seed."""
import re
from decimal import Decimal
from pathlib import Path

import httpx
import pytest

from app.core.parameters import PARAMETERS, diff_with_rows
from app.core.validation import validate
from app.storage.supabase import SupabaseScenarioStore

MIGRATION = Path(__file__).resolve().parents[2] / "supabase" / "migrations" / "20261015000000_scenarios.sql"
GOOD = dict(price="500000", downPayment="1", annualRate="5", termYears="10", annualTax="", annualInsurance="")
MONEY_OPTIONAL = ("annualTax", "annualInsurance")


def _fmt(d: Decimal) -> str:
    return format(d, "f")


def _field_ok(raw: dict, field: str) -> bool:
    res = validate(raw)
    return not isinstance(res, dict) or field not in res


@pytest.mark.parametrize("p", PARAMETERS, ids=lambda p: p.code)
def test_limits_match_validation(p):
    raw = dict(GOOD, price="1000000000000")  # high price so the down payment can reach its max
    raw[p.code] = _fmt(p.max_value) if p.code != "downPayment" else "999999999999.99"
    assert _field_ok(raw, p.code)
    if p.code != "downPayment":
        raw[p.code] = _fmt(p.max_value + (1 if p.kind != "money" else Decimal("0.01")))
        assert not _field_ok(raw, p.code)
    if p.code != "price":
        raw[p.code] = _fmt(p.min_value)
        raw["price"] = "500000"
        assert _field_ok(raw, p.code)
    raw[p.code] = _fmt(p.min_value - (Decimal("0.01") if p.code == "price" else 1))
    raw["price"] = "500000" if p.code != "price" else raw["price"]
    assert not _field_ok(raw, p.code)


def test_catalog_shape():
    assert {p.code: p.max_decimals for p in PARAMETERS}["termYears"] == 0
    assert [p.code for p in PARAMETERS if not p.required] == list(MONEY_OPTIONAL)
    assert [p.sort_order for p in PARAMETERS] == [1, 2, 3, 4, 5, 6]


def _rows_from(params):
    return [dict(code=p.code, kind=p.kind, required=p.required, min_value=float(p.min_value),
                 max_value=float(p.max_value), max_decimals=p.max_decimals, sort_order=p.sort_order) for p in params]


def test_migration_seed_matches_catalog():
    sql = MIGRATION.read_text(encoding="utf-8")
    block = sql[sql.index("insert into public.parameters"): sql.index("-- 2. sessions")]
    pattern = r"\('(\w+)',\s*'([^']*)',\s*'(\w+)',\s*(true|false),\s*([\d.]+),\s*([\d.]+),\s*(\d+),\s*(\d+)\)"
    rows = [dict(code=c, kind=k, required=r == "true", min_value=lo, max_value=hi, max_decimals=d, sort_order=o)
            for c, _label, k, r, lo, hi, d, o in re.findall(pattern, block)]
    assert len(rows) == len(PARAMETERS)
    assert diff_with_rows(rows) == []


def test_diff_detects_drift():
    base = _rows_from(PARAMETERS)
    assert diff_with_rows(base) == []
    drifted = [dict(r) for r in base]
    drifted[2]["max_value"] = 30
    assert len(diff_with_rows(drifted)) == 1
    assert diff_with_rows(base[:-1]) == ["annualInsurance: missing in database"]
    assert diff_with_rows(base + [dict(base[0], code="extra")]) == ["extra: unknown in code"]


def _store(rows):
    transport = httpx.MockTransport(lambda r: httpx.Response(200, json=rows))
    return SupabaseScenarioStore("https://x.supabase.co", "k", httpx.Client(transport=transport))


def test_store_verify_parameters_raises_on_drift():
    rows = _rows_from(PARAMETERS)
    _store(rows).verify_parameters()
    rows[0]["max_value"] = 5
    with pytest.raises(RuntimeError, match="out of sync"):
        _store(rows).verify_parameters()
