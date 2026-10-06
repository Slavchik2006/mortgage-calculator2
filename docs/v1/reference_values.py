"""Reference values for docs/v1/03-test-scenarios.md.

Independent of the implementation under test: Python decimal, 60 digits,
literal F§3 formulas. Run: python reference_values.py
"""
from decimal import Decimal as D, getcontext, ROUND_HALF_UP

getcontext().prec = 60

LOANS = {  # name: (price, down, annual_rate_pct, term_years)
    "V1": ("250000", "50000", "6", 30),
    "V2": ("120000", "0", "0", 10),
    "V3": ("100000", "0", "12", 1),
    "V4": ("1", "0", "25", 40),
    "V5": ("300000", "0", "3.5", 25),
    "V6": ("100000", "0", "0.01", 40),
    "V7": ("1000000000000", "0", "25", 40),
    "V8": ("999999999999.99", "0", "25", 1),
    "V9": ("100000", "0", "0", 3),
    "V10": ("0.01", "0", "0", 1),
    "V11": ("1000000000000", "0", "0", 40),
    "V12": ("0.01", "0", "6", 1),
}


def half_up(x):
    return x.quantize(D("0.01"), ROUND_HALF_UP)


def loan(price, down, rate, years):
    p = D(price) - D(down)
    r = D(rate) / 100 / 12
    n = years * 12
    m = p / n if r == 0 else p * r / (1 - (1 + r) ** (-n))
    return p, r, n, m


def schedule(p, r, n, m):
    bal, rows = p, []
    for k in range(1, n + 1):
        interest = bal * r
        payment = m if k < n else bal + interest  # final payment adjustment
        principal = payment - interest
        bal -= principal
        rows.append((k, payment, interest, principal, bal))
    return rows


if __name__ == "__main__":
    for name, args in LOANS.items():
        p, r, n, m = loan(*args)
        print(f"{name}: P={p} M={m:.10f} total={m*n:.8f} interest={m*n-p:.8f} "
              f"(display M={half_up(m)}, total={half_up(m*n)}, interest={half_up(m*n-p)})")
    rows = schedule(*loan(*LOANS["V1"]))
    for k in (1, 2, 9, 360):
        _, pay, i, pr, b = rows[k - 1]
        print(f"V1 row {k}: payment={pay:.10f} interest={i:.10f} principal={pr:.10f} balance={b:.10f}")
    print("V1 rows where displayed interest+principal != displayed payment:",
          sum(1 for _, pay, i, pr, _ in rows if half_up(i) + half_up(pr) != half_up(pay)))
    rows = schedule(*loan(*LOANS["V7"]))
    print(f"V7 row 480 interest={rows[-1][2]:.4f}")
