# 01 - Functional specification (V1)

## 1. Purpose and users

Mortgage calculator for home buyers estimating a monthly payment. Plain-language labels, minimal jargon.

## 2. Inputs

| Field | Required | Valid range | Precision | Notes |
|---|---|---|---|---|
| Home price (EUR) | yes | > 0 and ≤ 1,000,000,000,000 (technical cap) | ≤ 2 dp | |
| Down payment (EUR) | yes | 0 ≤ down < price | ≤ 2 dp | Absolute amount, not percent |
| Annual interest rate (%) | yes | 0 – 25 inclusive | ≤ 2 dp | Nominal, fixed for the whole term |
| Term (years) | yes | 1 – 40 inclusive | integer | Whole years only |
| Annual property tax (EUR) | no | ≥ 0, default 0 | ≤ 2 dp | |
| Annual home insurance (EUR) | no | ≥ 0, default 0 | ≤ 2 dp | |

- Principal `P = price − down payment`. There is no direct loan-amount field.
- Decimal separator is `.` only. Currency is EUR, fixed (no locale or currency switching).

## 3. Calculation rules

- Fixed-rate annuity, monthly compounding: `r = annual_rate / 100 / 12`, `n = years × 12`.
- Monthly principal & interest (P&I):
  - `r > 0`: `M = P · r / (1 − (1 + r)^−n)`
  - `r = 0`: `M = P / n`
- Monthly tax `T = annual_tax / 12`; monthly insurance `I = annual_insurance / 12`.
- All-in monthly total `= M + T + I`.
- Total P&I paid over the term `= M × n`; total interest `= M × n − P`. Totals cover the loan only and exclude tax and insurance.
- Amortization schedule, per month `k = 1..n`:
  - `interest_k = balance_{k−1} · r`
  - `principal_k = payment_k − interest_k`
  - `balance_k = balance_{k−1} − principal_k`, with `balance_0 = P`
  - `payment_k = M` for `k < n`; the final payment is adjusted so `balance_n = 0.00` exactly.

## 4. Rounding rules

- Calculate at full precision internally; round only for display.
- Display: 2 decimals, half-up.
- The final-payment adjustment ensures the schedule closes at exactly 0.00.
- Assumption: displayed tax, insurance and all-in total are each rounded from unrounded values, so the displayed all-in total may differ by 0.01 from the sum of the displayed parts.

## 5. Outputs

Shown after a successful Calculate:

1. Monthly P&I, monthly tax, monthly insurance, and all-in monthly total.
2. Total paid (P&I over the term) and total interest.
3. Full monthly amortization table (`n` rows): month, payment, interest, principal, remaining balance. Scrollable, no export.

## 6. Interaction and invalid input

- Calculation is triggered by a Calculate button (no live recalculation).
- Invalid values show an inline error on the offending field. No results are shown until every field is valid. Nothing is silently corrected or clamped.
- Invalid cases: empty required field, non-numeric, negative, outside the range in §2, more than 2 decimals (rate and money), non-integer term, down payment ≥ price.

## 7. Out of scope for V1

- Variable/adjustable rates; differentiated (declining) payments.
- Extra payments or prepayments, refinancing, PMI, fees, APR.
- Export, saving, sharing, accounts, history.
- Charts, multi-currency, i18n, scenario comparison.
