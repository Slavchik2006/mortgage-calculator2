# 03 - Test scenarios (V1)

Derived from `01-functional.md` (F§) and `02-architecture.md` (A§). Inputs are raw strings as typed, except for `calculation` and `formatting` tests, which take typed values. "B" is the base valid input: price `250000`, down `50000`, rate `6`, term `30`, tax `""`, ins `""` (principal 200000).

Self-check (run by the generating script before this file was written): every test name and ID is unique; every requirement ID in §1 appears in at least one `Verifies requirement` cell; no expected output contains an open decision; every test has a source of expected value.

## 1. Requirement catalogue (layer 1)

Layer 1 has no requirement IDs, so the spec text is split into atomic requirements here. The `Verifies requirement` column of every test table uses these IDs.

| ID | Requirement | Spec ref |
|---|---|---|
| F1 | Plain-language labels, minimal jargon | F§1 |
| F2.1 | Home price: required, > 0 and <= 1,000,000,000,000, <= 2 dp | F§2 |
| F2.2 | Down payment: required, 0 <= down < price, <= 2 dp, absolute amount | F§2 |
| F2.3 | Annual rate: required, 0-25 inclusive, <= 2 dp | F§2 |
| F2.4 | Term: required, integer 1-40 inclusive | F§2 |
| F2.5 | Annual property tax: optional, >= 0, default 0, <= 2 dp | F§2 |
| F2.6 | Annual home insurance: optional, >= 0, default 0, <= 2 dp | F§2 |
| F2.7 | Principal P = price - down payment (no loan-amount field) | F§2 |
| F2.8 | Decimal separator `.` only; currency EUR fixed, no locale/currency switching | F§2 |
| F3.1 | r = rate/100/12, n = years x 12 | F§3 |
| F3.2 | Monthly P&I for r > 0: M = P r / (1 - (1+r)^-n) | F§3 |
| F3.3 | Monthly P&I for r = 0: M = P / n | F§3 |
| F3.4 | Monthly tax T = annual tax / 12; monthly insurance I = annual insurance / 12 | F§3 |
| F3.5 | All-in monthly total = M + T + I | F§3 |
| F3.6 | Total P&I = M x n; total interest = M x n - P; both exclude tax and insurance | F§3 |
| F3.7 | Schedule recurrences: interest_k = balance_{k-1} r; principal_k = payment_k - interest_k; balance_k = balance_{k-1} - principal_k; balance_0 = P | F§3 |
| F3.8 | Final payment adjusted so balance_n = 0.00 exactly | F§3 |
| F4.1 | Full precision internally; round only for display | F§4 |
| F4.2 | Display: 2 decimals, half-up | F§4 |
| F4.3 | Displayed tax, insurance and all-in total each rounded from unrounded values (may differ by 0.01 from sum of displayed parts) | F§4 |
| F4.4 | Schedule closes at exactly 0.00 (final-payment adjustment) | F§4 |
| F5.1 | After a successful Calculate show monthly P&I, monthly tax, monthly insurance, all-in monthly total | F§5.1 |
| F5.2 | Show total paid (P&I over the term) and total interest | F§5.2 |
| F5.3 | Full monthly amortization table: n rows; month, payment, interest, principal, remaining balance | F§5.3 |
| F5.4 | Table is scrollable; no export | F§5.3 |
| F6.1 | Calculation triggered by a Calculate button; no live recalculation | F§6 |
| F6.2 | Invalid value shows an inline error on the offending field | F§6 |
| F6.3 | No results shown until every field is valid | F§6 |
| F6.4 | Nothing silently corrected or clamped | F§6 |
| F6.5.1 | Invalid case: empty required field | F§6 |
| F6.5.2 | Invalid case: non-numeric | F§6 |
| F6.5.3 | Invalid case: negative | F§6 |
| F6.5.4 | Invalid case: outside the range in F§2 | F§6 |
| F6.5.5 | Invalid case: more than 2 decimals (rate and money) | F§6 |
| F6.5.6 | Invalid case: non-integer term | F§6 |
| F6.5.7 | Invalid case: down payment >= price | F§6 |
| F7 | Out of scope for V1 is absent (variable rates, extra payments, export/save/share, charts, multi-currency, i18n, comparison) | F§7 |

## 2. Assumptions fixed for the tests

The spec is silent on the points below. Each is fixed to one concrete value so the expected outputs are exact. Changing one means changing the listed tests.

| ID | Assumption | Tests affected |
|---|---|---|
| A1 | Numeric grammar: after trimming ASCII whitespace a value is numeric iff it matches `^-?[0-9]+(\.[0-9]+)?$`. Everything else (`+1`, `.5`, `5.`, `.`, `1e5`, `0x10`, `Infinity`, `NaN`, `3,5`, `250 000`, full-width digits, U+2212 minus) gives NUMERIC. Whitespace-only counts as empty. | VAL-36, 41-56 |
| A2 | Per-field rule order is required -> numeric -> range -> precision; only the first failing rule is reported. Precision is textual: more than 2 digits after `.` gives DEC2 for money and rate (so `250000.500` fails); any `.` in the term gives INT_TERM (so `30.0` fails). `-0` is normalised to +0. | VAL-11, 22-24, 27, 54, 57, 58 |
| A3 | The cross-field rule `down < price` runs only when price and down have no error of their own; failure sets `errors.downPayment = RANGE_DOWN`. | VAL-05, 06, 59-61 |
| A4 | Error messages (symbolic names used in the tests): REQUIRED `This field is required.`; NUMERIC `Enter a number using digits and . only.`; RANGE_PRICE `Price must be more than 0 and at most 1,000,000,000,000.`; RANGE_DOWN `Down payment must be 0 or more and less than the home price.`; RANGE_RATE `Rate must be between 0 and 25.`; RANGE_TERM `Term must be between 1 and 40 years.`; RANGE_TAXINS `Must be between 0 and 1,000,000,000,000.`; DEC2 `Use at most 2 decimal places.`; INT_TERM `Enter a whole number of years.` | all VAL, UIF, INT error rows |
| A5 | SPEC GAP: F§2 gives tax and insurance only a lower bound (`>= 0`). A 400-digit string would parse to Infinity and break `calculate`. Assumed technical cap 1,000,000,000,000, the same as price. Needs your approval and an amendment to `01-functional.md`. | VAL-32 to 36 |
| A6 | `formatEur`: `€` prefix, `,` thousands grouping, `.` decimal, always 2 dp, half-up applied to the shortest decimal representation of the double (so 1.005 gives 1.01); negatives as `-€5.50`; a value that rounds to zero prints `€0.00` with no sign; NaN, +-Infinity or abs(value) >= 1e15 throws `RangeError`. | FMT-*, UIR-*, INT-* |
| A7 | The table rounds every cell independently, so displayed payment may differ from displayed interest + principal by 0.01 (F§4 accepts this for the summary only; extending it to the table is an assumption). | UIR-11 |
| A8 | Pressing Enter in any input triggers Calculate (form submit with default prevented). | UIF-12 |
| A9 | Tolerances: TOL1 = abs(actual - expected) <= 1e-12 x max(1, abs(expected)) for single closed-form values; TOL2 = relative 1e-9 for values accumulated over the schedule. `balance_n` is compared with strict `===`. | CAL-* |
| A10 | Each field has an error element `#<field>-error` with `role="alert"`; the input gets `aria-describedby="<field>-error"` and `aria-invalid="true"` while an error is shown. Field ids: price, downPayment, annualRate, termYears, annualTax, annualInsurance. | UIF-06 to 08, 15 |
| A11 | No minimum payment rule: a loan whose monthly payment rounds to `€0.00` is calculated and shown normally. | INT-05 |
| A12 | Performance budget: rendering 480 rows takes at most 200 ms (median of 5 runs); the spec gives no number, A§6 only says no virtualisation is needed. | UIR-13 |
| A13 | Display labels: results `Monthly payment (principal and interest)`, `Monthly property tax`, `Monthly home insurance`, `Total monthly payment`, `Total paid over the term (principal and interest)`, `Total interest`; table headers `Month`, `Payment`, `Interest`, `Principal`, `Remaining balance`; form labels as in UIF-01. Chosen to avoid the jargon `P&I` (F§1). | UIF-01, UIR-01, UIR-02 |
| A14 | The scrollable table container has CSS `overflow-y: auto` and a finite `max-height`. | UIR-08 |

## 3. Reference values and their source

Every reference value comes from `docs/v1/reference_values.py`: Python `decimal` at 60 digits, implementing the F§3 formulas literally (`M = P r / (1 - (1+r)^-n)`, `M = P/n` for r = 0, schedule recurrences, final payment = balance + interest). It is independent of the double-precision implementation under test. Rounded values use half-up.

| Ref | Price | Down | Rate % | Term y | P | Monthly P&I M | Total paid | Total interest |
|---|---|---|---|---|---|---|---|---|
| V1 | 250000 | 50000 | 6 | 30 | 200000 | 1199.1010503055 | 431676.37810998 | 231676.37810998 |
| V2 | 120000 | 0 | 0 | 10 | 120000 | 1000 | 120000 | 0 |
| V3 | 100000 | 0 | 12 | 1 | 100000 | 8884.8788678342 | 106618.54641401 | 6618.54641401 |
| V4 | 1 | 0 | 25 | 40 | 1 | 0.0208343816 | 10.00050315 | 9.00050315 |
| V5 | 300000 | 0 | 3.5 | 25 | 300000 | 1501.8707107785 | 450561.21323354 | 150561.21323354 |
| V6 | 100000 | 0 | 0.01 | 40 | 100000 | 208.7511458309 | 100200.54999883 | 200.54999883 |
| V7 | 1000000000000 | 0 | 25 | 40 | 1e12 | 20834381562.2599435685 | 10000503149884.77291286 | 9000503149884.77291286 |
| V8 | 999999999999.99 | 0 | 25 | 1 | 999999999999.99 | 95044203263.9082952426 | 1140530439166.89954291 | 140530439166.90954291 |
| V9 | 100000 | 0 | 0 | 3 | 100000 | 2777.7777777778 | 100000 | 0 |
| V10 | 0.01 | 0 | 0 | 1 | 0.01 | 0.0008333333 | 0.01 | 0 |
| V11 | 1000000000000 | 0 | 0 | 40 | 1e12 | 2083333333.3333333333 | 1000000000000 | 0 |
| V12 | 0.01 | 0 | 6 | 1 | 0.01 | 0.0008606643 | 0.01032797 | 0.00032797 |

Schedule reference values (V1): row 1 interest 1000, principal 199.1010503055, balance 199800.8989496945; row 2 interest 999.0044947485, principal 200.0965555570, balance 199600.8023941375; row 9 interest 991.8951847996, principal 207.2058655059, balance 198171.8310944167; row 360 interest 5.9656768672, principal 1193.1353734383, balance 0. V7 row 480 interest 425191460.4543. Other HAND values are one-line arithmetic stated in the test's source cell.

Note: the double-precision result for V8 is 95044203263.90858, which differs from the decimal reference 95044203263.90830 by 3e-4 (relative 3e-15). Tests therefore use TOL1, never exact equality, for such values.

Source codes: **REF** = reference vector/row above; **HAND** = arithmetic shown in the cell; **F§x / A§x** = stated in the spec/architecture; **A1-A14** = assumption in §2.

## 4. Validation (`validation`)

| ID | Test | Level | Module | Input | Expected output | Source of expected value | Verifies requirement | Type |
|---|---|---|---|---|---|---|---|---|
| VAL-01 | valid base, optionals empty | unit | validation | B (tax `""`, ins `""`) | `ok:true`, value = {price 250000, down 50000, rate 6, term 30, tax 0, ins 0} | F§2 default 0; A§3.3 | F2.1, F2.2, F2.3, F2.4, F2.5, F2.6 | happy path |
| VAL-02 | valid, all six fields | unit | validation | B + tax `2400`, ins `1200` | `ok:true`, value = {250000, 50000, 6, 30, 2400, 1200} as numbers | F§2; A§4 LoanInput | F2.5, F2.6 | happy path |
| VAL-03 | down payment 0 accepted | unit | validation | B + down `0` | `ok:true`, downPayment = 0 | F§2 `0 <= down` | F2.2 | edge case |
| VAL-04 | down = price - 0.01 accepted | unit | validation | price `100000`, down `99999.99` | `ok:true`, downPayment = 99999.99 | F§2 `down < price` | F2.2, F2.7 | edge case |
| VAL-05 | down = price rejected | unit | validation | price `100000`, down `100000` | `ok:false`, errors = {downPayment: RANGE_DOWN} | F§2, F§6; A3 | F2.2, F6.5.7 | edge case |
| VAL-06 | down > price rejected | unit | validation | price `100000`, down `150000` | `ok:false`, errors = {downPayment: RANGE_DOWN} | F§6; A3 | F6.5.7 | invalid input |
| VAL-07 | price at 1e12 cap accepted | unit | validation | B + price `1000000000000`, down `0` | `ok:true`, price = 1000000000000 | F§2 technical cap | F2.1 | edge case |
| VAL-08 | price just above cap rejected | unit | validation | B + price `1000000000000.01` | errors = {price: RANGE_PRICE} | F§2 `<= 1e12` | F2.1, F6.5.4 | edge case |
| VAL-09 | price 0 rejected | unit | validation | B + price `0` | errors = {price: RANGE_PRICE} | F§2 `> 0` | F2.1, F6.5.4 | edge case |
| VAL-10 | price 0.01 accepted | unit | validation | B + price `0.01`, down `0` | `ok:true`, price = 0.01 | F§2 `> 0`, <= 2 dp | F2.1 | edge case |
| VAL-11 | price negative rejected | unit | validation | B + price `-1` | errors = {price: RANGE_PRICE} | F§6 negative; A1, A2 | F2.1, F6.5.3 | invalid input |
| VAL-12 | rate 0 accepted | unit | validation | B + rate `0` | `ok:true`, annualRatePct = 0 | F§2 0 inclusive | F2.3 | edge case |
| VAL-13 | rate 25 accepted | unit | validation | B + rate `25` | `ok:true`, annualRatePct = 25 | F§2 25 inclusive | F2.3 | edge case |
| VAL-14 | rate 25.01 rejected | unit | validation | B + rate `25.01` | errors = {annualRate: RANGE_RATE} | F§2 range | F2.3, F6.5.4 | edge case |
| VAL-15 | rate -0.01 rejected | unit | validation | B + rate `-0.01` | errors = {annualRate: RANGE_RATE} | F§6 negative | F2.3, F6.5.3 | invalid input |
| VAL-16 | rate with 2 dp accepted | unit | validation | B + rate `3.75` | `ok:true`, annualRatePct = 3.75 | F§2 <= 2 dp | F2.3 | happy path |
| VAL-17 | rate with 3 dp rejected | unit | validation | B + rate `3.755` | errors = {annualRate: DEC2} | F§6 > 2 decimals | F2.3, F6.5.5 | invalid input |
| VAL-18 | term 1 accepted | unit | validation | B + term `1` | `ok:true`, termYears = 1 | F§2 range | F2.4 | edge case |
| VAL-19 | term 40 accepted | unit | validation | B + term `40` | `ok:true`, termYears = 40 | F§2 range | F2.4 | edge case |
| VAL-20 | term 0 rejected | unit | validation | B + term `0` | errors = {termYears: RANGE_TERM} | F§2 range | F2.4, F6.5.4 | edge case |
| VAL-21 | term 41 rejected | unit | validation | B + term `41` | errors = {termYears: RANGE_TERM} | F§2 range | F2.4, F6.5.4 | edge case |
| VAL-22 | term 2.5 rejected | unit | validation | B + term `2.5` | errors = {termYears: INT_TERM} | F§6 non-integer term | F2.4, F6.5.6 | invalid input |
| VAL-23 | term written 30.0 rejected | unit | validation | B + term `30.0` | errors = {termYears: INT_TERM} | A2 (any `.` in term fails) | F2.4, F6.5.6 | edge case |
| VAL-24 | term negative rejected | unit | validation | B + term `-5` | errors = {termYears: RANGE_TERM} | F§6 negative | F2.4, F6.5.3 | invalid input |
| VAL-25 | price with 2 dp accepted | unit | validation | B + price `250000.99` | `ok:true`, price = 250000.99 | F§2 <= 2 dp | F2.1 | happy path |
| VAL-26 | price with 3 dp rejected | unit | validation | B + price `250000.999` | errors = {price: DEC2} | F§6 > 2 decimals | F2.1, F6.5.5 | invalid input |
| VAL-27 | price 250000.500 rejected (textual 3 dp) | unit | validation | B + price `250000.500` | errors = {price: DEC2} | A2 (textual precision, A§6) | F2.1, F6.5.5 | edge case |
| VAL-28 | down payment with 3 dp rejected | unit | validation | B + down `100.001` | errors = {downPayment: DEC2} | F§6 > 2 decimals | F2.2, F6.5.5 | invalid input |
| VAL-29 | tax with 3 dp rejected | unit | validation | B + tax `100.001` | errors = {annualTax: DEC2} | F§6 > 2 decimals | F2.5, F6.5.5 | invalid input |
| VAL-30 | insurance with 3 dp rejected | unit | validation | B + ins `100.001` | errors = {annualInsurance: DEC2} | F§6 > 2 decimals | F2.6, F6.5.5 | invalid input |
| VAL-31 | tax 0 accepted | unit | validation | B + tax `0` | `ok:true`, annualTax = 0 | F§2 `>= 0` | F2.5 | edge case |
| VAL-32 | tax negative rejected | unit | validation | B + tax `-1` | errors = {annualTax: RANGE_TAXINS} | F§6 negative; A5 | F2.5, F6.5.3 | invalid input |
| VAL-33 | insurance negative rejected | unit | validation | B + ins `-0.01` | errors = {annualInsurance: RANGE_TAXINS} | F§6 negative; A5 | F2.6, F6.5.3 | invalid input |
| VAL-34 | tax at 1e12 cap accepted | unit | validation | B + tax `1000000000000` | `ok:true`, annualTax = 1000000000000 | A5 (spec gap, cap = price cap) | F2.5 | edge case |
| VAL-35 | tax above cap rejected | unit | validation | B + tax `1000000000000.01` | errors = {annualTax: RANGE_TAXINS} | A5 | F2.5, F6.5.4 | edge case |
| VAL-36 | insurance 400-digit string rejected | unit | validation | B + ins = `9` repeated 400 times | errors = {annualInsurance: RANGE_TAXINS} (Number() gives Infinity, above cap); no exception | A1, A5 | F2.6, F6.5.4 | edge case |
| VAL-37 | price empty | unit | validation | B + price `""` | errors = {price: REQUIRED} | F§6 empty required | F2.1, F6.5.1 | invalid input |
| VAL-38 | down payment empty | unit | validation | B + down `""` | errors = {downPayment: REQUIRED} | F§2 required, no default | F2.2, F6.5.1 | invalid input |
| VAL-39 | rate empty | unit | validation | B + rate `""` | errors = {annualRate: REQUIRED} | F§2 required | F2.3, F6.5.1 | invalid input |
| VAL-40 | term empty | unit | validation | B + term `""` | errors = {termYears: REQUIRED} | F§2 required | F2.4, F6.5.1 | invalid input |
| VAL-41 | price whitespace-only = empty | unit | validation | B + price `"   "` | errors = {price: REQUIRED} | A1 (whitespace-only = empty) | F2.1, F6.5.1 | edge case |
| VAL-42 | tax whitespace-only = empty optional | unit | validation | B + tax `"  "` | `ok:true`, annualTax = 0 | A1; F§2 default 0 | F2.5 | edge case |
| VAL-43 | surrounding spaces trimmed | unit | validation | B + price `" 250000 "` | `ok:true`, price = 250000 | A1 (trim) | F2.1 | edge case |
| VAL-44 | price text rejected | unit | validation | B + price `abc` | errors = {price: NUMERIC} | F§6 non-numeric | F2.1, F6.5.2 | invalid input |
| VAL-45 | optional tax text rejected | unit | validation | B + tax `abc` | errors = {annualTax: NUMERIC} | F§6 non-numeric | F2.5, F6.5.2 | invalid input |
| VAL-46 | comma decimal separator rejected | unit | validation | B + rate `3,5` | errors = {annualRate: NUMERIC} | F§2 `.` only | F2.8, F6.5.2 | invalid input |
| VAL-47 | thousands separators rejected | unit | validation | B + price `250,000` (run again with `250 000`) | errors = {price: NUMERIC} in both runs | F§2 `.` only; A1 | F2.8, F6.5.2 | invalid input |
| VAL-48 | scientific notation rejected | unit | validation | B + price `1e5` | errors = {price: NUMERIC} | A§6 (rejects `1e3`-style); A1 | F6.5.2 | invalid input |
| VAL-49 | Infinity and NaN strings rejected | unit | validation | B + price `Infinity` (run again with `NaN`) | errors = {price: NUMERIC} in both runs | A1 (Number() would accept Infinity) | F6.5.2 | invalid input |
| VAL-50 | hex literal rejected | unit | validation | B + price `0x10` | errors = {price: NUMERIC} | A1 (Number(`0x10`) = 16 must not pass) | F6.5.2 | invalid input |
| VAL-51 | leading plus rejected | unit | validation | B + price `+1000` | errors = {price: NUMERIC} | A1 | F6.5.2 | edge case |
| VAL-52 | malformed decimal points rejected | unit | validation | B + price `.5`; `5.`; `.` (three runs) | errors = {price: NUMERIC} in each run | A1 | F6.5.2 | edge case |
| VAL-53 | leading zeros accepted | unit | validation | B + price `0001000`, down `0` | `ok:true`, price = 1000 | A1 (grammar allows leading zeros) | F2.1 | edge case |
| VAL-54 | negative zero normalised | unit | validation | B + down `-0` | `ok:true`; `Object.is(value.downPayment, 0)` is true | A2 (-0 normalised to +0) | F2.2 | edge case |
| VAL-55 | non-ASCII digits and minus rejected | unit | validation | B + price `１２３` (full-width); B + rate `−5` (U+2212) | errors = {price: NUMERIC}; errors = {annualRate: NUMERIC} | A1 (ASCII digits and `-` only); F§6 | F6.4, F6.5.2 | edge case |
| VAL-56 | 400-digit price rejected | unit | validation | B + price = `9` repeated 400 times | errors = {price: RANGE_PRICE}; no exception | F§2 cap; Number() = Infinity | F2.1, F6.5.4 | edge case |
| VAL-57 | several fields invalid at once | unit | validation | B + price `""`, rate `30`, term `0.5` | errors has exactly 3 keys: {price: REQUIRED, annualRate: RANGE_RATE, termYears: RANGE_TERM} | A§7 per-field errors; A2 | F6.2, F6.5.1, F6.5.4 | invalid input |
| VAL-58 | rule order: range before precision | unit | validation | B + rate `-1.234` | errors = {annualRate: RANGE_RATE} (one message only) | A§3.3, A§7 order; A2 | F6.2, F6.5.3 | edge case |
| VAL-59 | cross-field error alongside other error | unit | validation | price `100`, down `100`, rate `abc`, term `30` | errors = {downPayment: RANGE_DOWN, annualRate: NUMERIC} | A§7 cross-field on downPayment; A3 | F2.2, F6.5.2, F6.5.7 | edge case |
| VAL-60 | cross-field skipped when price invalid | unit | validation | price `abc`, down `100` | errors = {price: NUMERIC} only | A3 | F6.5.2 | edge case |
| VAL-61 | cross-field skipped when down invalid | unit | validation | price `100000`, down `abc` | errors = {downPayment: NUMERIC} only | A3 | F6.5.2 | edge case |
| VAL-62 | no clamping on invalid value | unit | validation | B + rate `25.5` | `ok:false`; result has no `value` property (no clamped 25) | F§6 nothing silently corrected | F6.4 | invalid input |
| VAL-63 | all required empty | unit | validation | all six fields `""` | errors = {price, downPayment, annualRate, termYears} each REQUIRED; no annualTax/annualInsurance keys | F§2 required vs optional | F6.5.1 | invalid input |
| VAL-64 | validate never throws | unit | validation | every raw input used in VAL-01..VAL-63 | each call returns an object whose `ok` is a boolean; zero exceptions | A§7 | F6.2 | invalid input |

## 5. Calculation (`calculation`)

| ID | Test | Level | Module | Input | Expected output | Source of expected value | Verifies requirement | Type |
|---|---|---|---|---|---|---|---|---|
| CAL-01 | standard loan, no tax/insurance | unit | calculation | V1: price 250000, down 50000, 6 %, 30 y, tax 0, ins 0 | principal 200000; monthlyPI 1199.1010503055; monthlyTax 0; monthlyInsurance 0; monthlyTotal 1199.1010503055; totalPaid 431676.37810998; totalInterest 231676.37810998 (all within TOL1) | REF V1 | F2.7, F3.1, F3.2, F3.5, F3.6 | happy path |
| CAL-02 | standard loan with tax and insurance | unit | calculation | V1 + tax 2400, ins 1200 | monthlyTax 200; monthlyInsurance 100; monthlyTotal 1499.1010503055 (TOL1) | HAND 2400/12 = 200, 1200/12 = 100; REF V1 M | F3.4, F3.5 | happy path |
| CAL-03 | principal = price - down | unit | calculation | price 300000, down 75000, 5 %, 20 y | summary.principal = 225000 exactly | HAND 300000 - 75000 | F2.7 | happy path |
| CAL-04 | second reference loan | unit | calculation | V5: price 300000, down 0, 3.5 %, 25 y | monthlyPI 1501.8707107785; totalInterest 150561.21323354 (TOL1) | REF V5 | F3.2, F3.6 | happy path |
| CAL-05 | one-year loan at 12 % | unit | calculation | V3: price 100000, down 0, 12 %, 1 y | monthlyPI 8884.8788678342; totalInterest 6618.54641401; schedule.length 12 (TOL1) | REF V3 | F3.1, F3.2, F3.6 | edge case |
| CAL-06 | zero rate branch | unit | calculation | V2: price 120000, down 0, 0 %, 10 y | monthlyPI 1000 exactly; every interest_k === 0; every payment_k === 1000; abs(totalInterest) <= 1e-9 | F§3 `M = P/n`; HAND 120000/120 | F3.3, F3.6 | edge case |
| CAL-07 | zero rate, non-terminating payment | unit | calculation | V9: price 100000, down 0, 0 %, 3 y | monthlyPI 2777.7777777778 (TOL1); schedule[35].balance === 0 | HAND 100000/36; F§3 | F3.3, F3.8 | edge case |
| CAL-08 | very small positive rate | unit | calculation | V6: price 100000, down 0, 0.01 %, 40 y | monthlyPI 208.7511458309; totalInterest 200.54999883 (TOL1); every schedule value is finite | REF V6 | F3.2 | edge case |
| CAL-09 | minimum principal, max rate, max term | unit | calculation | V4: price 1, down 0, 25 %, 40 y | monthlyPI 0.0208343816; schedule.length 480; schedule[0].interest 0.0208333333 (= 1 x 0.25/12); schedule[479].balance === 0 | REF V4; HAND 0.25/12 | F3.2, F3.7, F3.8 | edge case |
| CAL-10 | maximum principal, max rate, max term | unit | calculation | V7: price 1e12, down 0, 25 %, 40 y | monthlyPI 20834381562.2599 (TOL1); schedule.length 480; schedule[479].interest 425191460.4543 (TOL2); schedule[479].balance === 0 | REF V7 | F2.1, F3.2, F3.8 | edge case |
| CAL-11 | large principal, short term, high rate | unit | calculation | V8: price 999999999999.99, down 0, 25 %, 1 y | monthlyPI 95044203263.9083 (TOL1); schedule.length 12; schedule[11].balance === 0; abs(sum principal - P) <= 1e-9 x P | REF V8 (decimal, not float: float gives ...90858) | F3.2, F3.8 | edge case |
| CAL-12 | large principal, zero rate, max term | unit | calculation | V11: price 1e12, down 0, 0 %, 40 y | monthlyPI 2083333333.3333333 (TOL1); every interest_k === 0; abs(totalInterest) <= 1e-3 | HAND 1e12/480 | F3.3 | edge case |
| CAL-13 | tiny principal at 6 % | unit | calculation | V12: price 0.01, down 0, 6 %, 1 y | monthlyPI 0.0008606643 (TOL1); totalPaid 0.01032797; schedule.length 12; schedule[11].balance === 0 | REF V12 | F3.2, F3.8 | edge case |
| CAL-14 | down payment 0 gives full price principal | unit | calculation | price 100000, down 0, 5 %, 20 y | summary.principal = 100000 | F§2 P = price - down | F2.2, F2.7 | edge case |
| CAL-15 | tax only | unit | calculation | V1 + tax 1234.56, ins 0 | monthlyTax = 102.88 (TOL1); monthlyInsurance 0; monthlyTotal = 1199.1010503055 + 102.88 = 1301.9810503055 | HAND 1234.56/12 = 102.88 | F3.4, F3.5 | happy path |
| CAL-16 | insurance only | unit | calculation | V1 + tax 0, ins 600 | monthlyInsurance = 50; monthlyTotal = 1249.1010503055 (TOL1) | HAND 600/12 | F3.4, F3.5 | happy path |
| CAL-17 | tax/insurance excluded from loan totals | unit | calculation | V1 computed twice: (tax 0, ins 0) and (tax 2400, ins 1200) | totalPaid, totalInterest and every schedule row are strictly equal (===) between the two results | F§3 totals exclude tax and insurance | F3.6 | edge case |
| CAL-18 | schedule length = 12 x term | unit | calculation | terms 1, 10, 30, 40 (price 200000, down 0, 5 %) | schedule.length = 12, 120, 360, 480 | F§5.3 n rows; A§8 | F5.3 | edge case |
| CAL-19 | month numbering | unit | calculation | V1 | schedule[k].month === k+1 for k = 0..359 | F§3 k = 1..n | F3.7 | happy path |
| CAL-20 | first schedule row | unit | calculation | V1 | payment 1199.1010503055; interest 1000; principal 199.1010503055; balance 199800.8989496945 (TOL1) | REF V1 row 1; HAND 200000 x 0.005 | F3.7 | happy path |
| CAL-21 | second schedule row | unit | calculation | V1 | interest 999.0044947485; principal 200.0965555570; balance 199600.8023941375 (TOL1) | REF V1 row 2 | F3.7 | happy path |
| CAL-22 | closing balance exactly zero | unit | calculation | V1, V3, V5, V6 (four runs) | schedule[n-1].balance === 0 (strict equality) | F§3, F§4; A§6 | F3.8, F4.4 | edge case |
| CAL-23 | final payment adjustment | unit | calculation | V1 | schedule[359].interest 5.9656768672; principal 1193.1353734383; payment = schedule[358].balance + schedule[359].interest; abs(payment - M) <= 1e-9 x M | REF V1 row 360; A§6 final payment rule | F3.8 | edge case |
| CAL-24 | principal column sums to P | unit | calculation | V1, V5, V6 (three runs) | abs(sum principal_k - P) <= 1e-9 x P in each run | A§8 invariant; TOL2 | F3.7, F3.8 | edge case |
| CAL-25 | interest column sums to total interest | unit | calculation | V1, V5, V6 (three runs) | abs(sum interest_k - totalInterest) <= 1e-9 x max(1, totalInterest) in each run | A§8 invariant; TOL2 | F3.6, F3.7 | edge case |
| CAL-26 | row identities | unit | calculation | V1, all 360 rows | payment_k = interest_k + principal_k and balance_k = balance_{k-1} - principal_k, each within abs 1e-6 | F§3 recurrences | F3.7 | edge case |
| CAL-27 | balance monotone | unit | calculation | V1 and V5 | balance_k < balance_{k-1} and balance_k >= 0 for every k; interest_k decreasing and principal_k increasing for k = 1..n-1 | F§3 (annuity property) | F3.7 | edge case |
| CAL-28 | unrounded monthly total identity | unit | calculation | V1 + tax 2400 + ins 1200 | monthlyTotal === monthlyPI + monthlyTax + monthlyInsurance (strict equality) | A§8 invariant | F3.5 | edge case |
| CAL-29 | total paid and interest definitions | unit | calculation | V1 | totalPaid === monthlyPI x 360 and totalInterest === monthlyPI x 360 - principal (strict equality) | F§3 `M x n`, `M x n - P` | F3.6 | happy path |
| CAL-30 | no rounding inside calculation | unit | calculation | V1 | monthlyPI !== 1199.10 and equals 1199.1010503055 within TOL1 | F§4 round only for display | F4.1 | edge case |
| CAL-31 | calculate is pure | unit | calculation | V1 as a frozen object, called twice | no exception; the two results are deeply equal; input unchanged | A§2 pure core | F4.1 | edge case |
| CAL-32 | precondition violations throw | unit | calculation | three runs: termYears 0; downPayment = price; annualRatePct NaN | each run throws an `Error` | A§7 programmer error | (A§7 only) | invalid input |
| CAL-33 | property test over random valid inputs | unit | calculation | 1000 inputs from a PRNG with seed 42: money 2 dp within F§2 ranges, term integer 1-40, rate 2 dp in 0-25 | for every input: length = 12 x term; last balance === 0; principal sum within 1e-9 x P of P; interest sum within 1e-9 x max(1,totalInterest) of totalInterest; if rate 0 every interest_k === 0; 0 failures | A§8 invariants; TOL2 | F3.3, F3.7, F3.8, F4.4 | edge case |

## 6. Formatting (`formatting`)

| ID | Test | Level | Module | Input | Expected output | Source of expected value | Verifies requirement | Type |
|---|---|---|---|---|---|---|---|---|
| FMT-01 | two decimals and symbol | unit | formatting | formatEur(1199.10105) | `€1,199.10` | F§4 2 dp; A6 format | F4.2 | happy path |
| FMT-02 | round down below half | unit | formatting | formatEur(1.004) | `€1.00` | HAND 1.004 -> 1.00 | F4.2 | happy path |
| FMT-03 | round up above half | unit | formatting | formatEur(1.006) | `€1.01` | HAND | F4.2 | happy path |
| FMT-04 | half-up on exact binary halves | unit | formatting | formatEur(0.125); formatEur(0.375) | `€0.13`; `€0.38` (banker's rounding would give `€0.12` for the first) | F§4 half-up; HAND | F4.2 | edge case |
| FMT-05 | half-up on binary-inexact halves | unit | formatting | formatEur(1.005); formatEur(2.675) | `€1.01`; `€2.68` (`toFixed(2)` gives 1.00 and 2.67) | F§4 half-up on the decimal value; A6; A§6 | F4.2 | edge case |
| FMT-06 | half-up on large value | unit | formatting | formatEur(123456789.125) | `€123,456,789.13` | HAND (.125 exact in binary) | F4.2 | edge case |
| FMT-07 | zero | unit | formatting | formatEur(0) | `€0.00` | HAND | F4.2 | edge case |
| FMT-08 | float residue near zero has no sign | unit | formatting | formatEur(1e-12); formatEur(-1e-12) | `€0.00` for both | F§4 closes at 0.00; A6 | F4.2, F4.4 | edge case |
| FMT-09 | negative zero | unit | formatting | formatEur(-0) | `€0.00` | A6 | F4.2 | edge case |
| FMT-10 | largest realistic magnitude | unit | formatting | formatEur(1140530439166.903) | `€1,140,530,439,166.90` | REF V8 total paid 1140530439166.8995 (decimal) | F4.2 | edge case |
| FMT-11 | value at or above 1e15 rejected | unit | formatting | formatEur(1e15) | throws `RangeError` | A6 (supported range; largest spec total is about 1.0e13) | F4.2 | invalid input |
| FMT-12 | output independent of runtime locale | unit | formatting | formatEur(1234.56) with process locale `sk-SK`, then `en-US` | `€1,234.56` in both runs | F§2 no locale switching | F2.8 | edge case |
| FMT-13 | thousands grouping | unit | formatting | formatEur(1234567.5) | `€1,234,567.50` | A6 | F4.2 | happy path |
| FMT-14 | NaN and Infinity rejected | unit | formatting | formatEur(NaN); formatEur(Infinity) | each throws `RangeError` | A6 | F4.2 | invalid input |
| FMT-15 | rounded parts, total rounds down | unit | formatting | formatEur(1000.004); formatEur(0.004); formatEur(0.004); formatEur(1000.012) | `€1,000.00`; `€0.00`; `€0.00`; `€1,000.01` (parts sum 1000.00, total 1000.01) | F§4 discrepancy; HAND | F4.3 | edge case |
| FMT-16 | rounded parts, total rounds up | unit | formatting | formatEur(1000.005); formatEur(0.005); formatEur(0.005); formatEur(1000.015) | `€1,000.01`; `€0.01`; `€0.01`; `€1,000.02` (parts sum 1000.03, total 1000.02) | F§4 discrepancy; HAND | F4.3 | edge case |
| FMT-17 | negative non-zero value | unit | formatting | formatEur(-5.5) | `-€5.50` | A6 | F4.2 | edge case |
| FMT-18 | roundHalfUp2 idempotent | unit | formatting | roundHalfUp2 applied once vs twice to 1.005, 2.675, 0.125, 1199.10105, 1e-12 | twice-applied result strictly equals once-applied result for all five inputs | A§3.5 helper; HAND | F4.2 | edge case |

## 7. UI form (`ui/form`)

| ID | Test | Level | Module | Input | Expected output | Source of expected value | Verifies requirement | Type |
|---|---|---|---|---|---|---|---|---|
| UIF-01 | six labelled fields | DOM | ui/form | load index.html | exactly 6 `input` elements, each with an associated label; label texts: `Home price (EUR)`, `Down payment (EUR)`, `Annual interest rate (%)`, `Term (years)`, `Annual property tax (EUR)`, `Annual home insurance (EUR)`; tax and insurance labels also contain `optional`, the other four do not | F§2 field names; A13 | F1, F2.1, F2.2, F2.3, F2.4, F2.5, F2.6 | happy path |
| UIF-02 | no jargon in form labels | DOM | ui/form | load index.html | no label or hint text contains `amortization`, `APR`, `PMI`, `escrow` or `principal` (case-insensitive) | F§1 minimal jargon | F1 | edge case |
| UIF-03 | one Calculate button | DOM | ui/form | load index.html | exactly 1 `button` with text `Calculate` | F§6 | F6.1 | happy path |
| UIF-04 | collect returns raw strings | DOM | ui/form | type price `250000`, down `50000`, rate `1e3`, term `30`, tax `""`, ins `" "`; call collect() | {price `250000`, downPayment `50000`, annualRate `1e3`, termYears `30`, annualTax `""`, annualInsurance `" "`} verbatim, not trimmed or parsed | A§3.6, A§6 validate strings | F6.4 | happy path |
| UIF-05 | untouched optional fields collected as empty | DOM | ui/form | fill four required fields only; call collect() | annualTax === `""` and annualInsurance === `""` | A§4 RawInput | F2.5, F2.6 | happy path |
| UIF-06 | error shown next to field | DOM | ui/form | showErrors({price: REQUIRED}) | element `#price-error` has text = REQUIRED message, is inside the price field container, has `role="alert"`; the five other error elements have empty text | F§6 inline error; A10 | F6.2 | happy path |
| UIF-07 | several errors, each on own field | DOM | ui/form | showErrors({price: REQUIRED, annualRate: RANGE_RATE, termYears: RANGE_TERM}) | 3 non-empty error elements, each inside its own field container; 3 error elements empty | F§6 inline error | F6.2 | edge case |
| UIF-08 | clearErrors removes all errors | DOM | ui/form | showErrors with 3 fields, then clearErrors() | all 6 error elements have empty text; no input has `aria-invalid="true"` | A§3.6 | F6.2 | edge case |
| UIF-09 | stale error cleared after valid Calculate | DOM | ui/form | click Calculate with rate `30`, set rate `6`, click Calculate | rate error element text is empty after the second click | A§5 clear first | F6.2, F6.3 | edge case |
| UIF-10 | partly fixed input keeps remaining error | DOM | ui/form | rate `30` and term `0`; fix rate only; click Calculate | rate error empty; term error = RANGE_TERM text | A§5 | F6.2 | edge case |
| UIF-11 | no live recalculation | DOM | ui/form | after a successful result, set rate to `7` and dispatch `input` and `change` events | calculate handler call count unchanged; results container innerHTML unchanged | F§6 Calculate button only | F6.1 | edge case |
| UIF-12 | Enter key triggers Calculate | DOM | ui/form | press Enter inside the price input | calculate handler called exactly once; page not reloaded | A8 | F6.1 | edge case |
| UIF-13 | double click on Calculate | DOM | ui/form | two clicks in a row with valid input V1 | results container has exactly 1 summary block and 360 table rows | A§5 render replaces | F5.3, F6.1 | edge case |
| UIF-14 | inputs are text type | DOM | ui/form | load index.html; type `abc` into price; call collect() | all 6 inputs have `type="text"`; collect().price === `abc` | A§6 strings reach validation | F6.5.2 | invalid input |
| UIF-15 | error is announced and linked | DOM | ui/form | showErrors({price: REQUIRED}) | price input has `aria-describedby="price-error"` and `aria-invalid="true"` | A10 | F6.2 | edge case |
| UIF-16 | error text is not parsed as markup | DOM | ui/form | type price `<b>x</b>`, click Calculate | `#price-error` textContent = NUMERIC message; `#price-error` contains no child element; the typed string appears nowhere in the DOM outside the input value | A4 fixed messages (no user input echoed) | F6.2, F6.5.2 | invalid input |

## 8. UI results (`ui/results`)

| ID | Test | Level | Module | Input | Expected output | Source of expected value | Verifies requirement | Type |
|---|---|---|---|---|---|---|---|---|
| UIR-01 | summary values | DOM | ui/results | render(calculate(V1 + tax 2400 + ins 1200)) | `Monthly payment (principal and interest)` = `€1,199.10`; `Monthly property tax` = `€200.00`; `Monthly home insurance` = `€100.00`; `Total monthly payment` = `€1,499.10`; `Total paid over the term (principal and interest)` = `€431,676.38`; `Total interest` = `€231,676.38` | REF V1 (rounded half-up); A13 labels | F1, F4.2, F5.1, F5.2 | happy path |
| UIR-02 | table columns | DOM | ui/results | render(calculate(V1)) | header cells in order: `Month`, `Payment`, `Interest`, `Principal`, `Remaining balance` | F§5.3 columns; A13 | F5.3 | happy path |
| UIR-03 | table row count | DOM | ui/results | render for term 30; term 40; term 1 | tbody rows = 360; 480; 12 | F§5.3 n rows | F5.3 | edge case |
| UIR-04 | first row text | DOM | ui/results | render(calculate(V1)) | cells `1`, `€1,199.10`, `€1,000.00`, `€199.10`, `€199,800.90` | REF V1 row 1 | F5.3, F4.2 | happy path |
| UIR-05 | last row closes at zero | DOM | ui/results | render(calculate(V1)) | cells `360`, `€1,199.10`, `€5.97`, `€1,193.14`, `€0.00` | REF V1 row 360 (5.9657, 1193.1354) | F4.4, F5.3 | edge case |
| UIR-06 | all currency cells formatted | DOM | ui/results | render(calculate(V1)) | every currency cell matches regex `^€[0-9]{1,3}(,[0-9]{3})*\.[0-9]{2}$`; no cell contains `e+`, `NaN` or `Infinity` | A§3.7 via formatEur; A6 | F4.2 | edge case |
| UIR-07 | zero tax and insurance displayed | DOM | ui/results | render(calculate(V1)) with tax 0, ins 0 | tax and insurance values read `€0.00` (rows present) | F§5.1 four values always shown | F5.1 | edge case |
| UIR-08 | table scrolls, no export | DOM | ui/results | render(calculate(V4)) (480 rows) | table container computed `overflow-y` is `auto` or `scroll` and `max-height` is not `none`; scrollHeight > clientHeight; no button or link whose text contains `export`, `download` or `save` (case-insensitive) | F§5.3; A§6; A14 | F5.4 | edge case |
| UIR-09 | re-render replaces previous result | DOM | ui/results | render(V4 result) then render(V3 result) | tbody has exactly 12 rows; first row first cell `1`; summary values from V3 (monthly payment `€8,884.88`) | A§3.7 | F5.3 | edge case |
| UIR-10 | clear empties results | DOM | ui/results | render(V1 result) then clear() | no summary element, no table element; results container textContent === `""` | A§3.7; F§6 | F6.3 | edge case |
| UIR-11 | table row where displayed parts do not foot | DOM | ui/results | render(calculate(V1)), month 9 row | cells `9`, `€1,199.10`, `€991.90`, `€207.21`, `€198,171.83` (991.90 + 207.21 = 1,199.11, not 1,199.10) | REF V1 row 9 (decimal); A7 | F4.3, F5.3 | edge case |
| UIR-12 | summary rounds each part independently | DOM | ui/results | render with summary monthlyPI 1000.004, monthlyTax 0.004, monthlyInsurance 0.004, monthlyTotal 1000.012 | `€1,000.00`, `€0.00`, `€0.00`; total `€1,000.01` | F§4 discrepancy; HAND | F4.3, F5.1 | edge case |
| UIR-13 | render time for 480 rows | DOM | ui/results | render(calculate(V4)), median of 5 runs | median render time <= 200 ms | A§6 no virtualisation; A12 | F5.3 | edge case |

## 9. End to end (`main`) and architecture checks

| ID | Test | Level | Module | Input | Expected output | Source of expected value | Verifies requirement | Type |
|---|---|---|---|---|---|---|---|---|
| INT-01 | happy path end to end | integration | main | price `250000`, down `50000`, rate `6`, term `30`, tax `2400`, ins `1200`; click Calculate | summary as in UIR-01; 360 table rows; all 6 error elements empty | REF V1; A§5 | F2.7, F3.4, F5.1, F5.2, F5.3, F6.1 | happy path |
| INT-02 | optional fields left empty | integration | main | price `250000`, down `50000`, rate `6`, term `30`, tax and ins untouched | `Total monthly payment` = `€1,199.10`; tax `€0.00`; insurance `€0.00` | F§2 default 0; REF V1 | F2.5, F2.6, F3.5 | happy path |
| INT-03 | zero-rate loan | integration | main | price `120000`, down `0`, rate `0`, term `10` | monthly payment `€1,000.00`; total paid `€120,000.00`; total interest `€0.00`; 120 rows; every interest cell `€0.00`; last balance `€0.00` | REF V2 | F2.3, F3.3, F4.4, F5.3 | edge case |
| INT-04 | largest allowed loan | integration | main | price `1000000000000`, down `0`, rate `25`, term `40` | monthly payment `€20,834,381,562.26`; total paid `€10,000,503,149,884.77`; total interest `€9,000,503,149,884.77`; 480 rows; last balance `€0.00`; no cell contains `NaN`, `Infinity` or `e+` | REF V7 (decimal 20834381562.2599, 10000503149884.7729); double-precision value 10000503149884.771 rounds to the same cents | F2.1, F3.2, F4.2, F4.4 | edge case |
| INT-05 | smallest allowed loan | integration | main | price `0.01`, down `0`, rate `0`, term `1` | monthly payment `€0.00`; total paid `€0.01`; total interest `€0.00`; 12 rows; every payment cell `€0.00`; last balance `€0.00` | HAND 0.01/12 = 0.000833; REF V10 total 0.01; A11 | F2.1, F3.3, F4.4 | edge case |
| INT-06 | invalid input shows error, no results | integration | main | B with rate `30`; click Calculate | rate error element = RANGE_RATE text; other 5 error elements empty; results container textContent === `""` | F§6 | F6.2, F6.3, F6.5.4 | invalid input |
| INT-07 | every required field invalid | integration | main | price `""`, down `abc`, rate `-1`, term `0.5`; click Calculate | errors: price REQUIRED, down NUMERIC, rate RANGE_RATE, term RANGE_TERM, each under its own field; results empty | F§6; A2 | F6.2, F6.3, F6.5.1, F6.5.2, F6.5.3 | invalid input |
| INT-08 | valid then invalid | integration | main | valid Calculate (B), then rate `30`, Calculate | results container empty after second click; rate error shown | A§5 clear first; F§6 | F6.3 | edge case |
| INT-09 | invalid then valid | integration | main | rate `30`, Calculate; then rate `6`, Calculate | all error elements empty; summary and 360 rows shown | A§5 | F6.2, F6.3 | edge case |
| INT-10 | term shrinks between calculations | integration | main | price `100000`, down `0`, rate `12`; term `30` then term `1`; Calculate each time | after second click: 12 rows; monthly payment `€8,884.88`; total interest `€6,618.55` | REF V3 | F5.3 | edge case |
| INT-11 | down payment equals price | integration | main | price `100000`, down `100000`, rate `6`, term `30` | down payment error = RANGE_DOWN text; results empty | F§2, F§6 | F2.2, F6.3, F6.5.7 | invalid input |
| INT-12 | calculate twice with same inputs | integration | main | B; Calculate twice | results container innerHTML identical after both clicks | A§5 | F6.1 | edge case |
| INT-13 | nothing shown on load | integration | main | load index.html | all 6 error elements empty; results container textContent === `""` | F§6 no results until valid | F6.3 | edge case |
| INT-14 | out-of-scope features absent | integration | main | load index.html and click Calculate with B | exactly 6 `input` and 1 `button` elements; no `canvas`, `select`, `a[download]`; page text contains none of: export, download, share, chart, compare, extra payment (case-insensitive) | F§7 | F7, F5.4 | edge case |
| INT-15 | currency fixed to EUR | integration | main | load index.html and click Calculate with B; run again with browser locale `sk-SK` | every currency cell starts with `€`; no currency/locale control; identical results text in both runs | F§2 | F2.8 | edge case |
| INT-16 | no network and no storage | integration | main | click Calculate with B while spying on fetch, XMLHttpRequest, sendBeacon | 0 network calls; `localStorage.length` = 0; `document.cookie` = `""` | A§1 no backend/persistence; F§7 no saving | F7 | edge case |
| INT-17 | dependency direction | static | architecture | static check of imports in `src/` | violations list is empty: `calculation` imports only `types`, `constants`; `validation` imports only `types`, `constants`; `formatting` imports nothing; no core module imports `ui/*` | A§2 principle 2 | (A§2 only) | edge case |

## 10. Edge cases found beyond the original spec

| # | Edge case | Why it matters | Covered by |
|---|---|---|---|
| 1 | Tax and insurance have no upper bound in F§2 | A 400-digit value parses to Infinity and `calculate` returns NaN; cap assumed in A5 | VAL-34, 35, 36 |
| 2 | `Number()` accepts `Infinity`, `0x10`, `1e5`, whitespace | Raw-string grammar must be explicit (A1); A§6 mentions only `1e3` and `,` | VAL-47 to 52, 55 |
| 3 | Textual vs numeric precision: `250000.500`, `30.0`, `-0`, `.5`, `5.`, `+1000`, leading zeros | F§2 says `<= 2 dp` / integer; A§6 uses a regex, so the accepted grammar is a design choice (A1, A2) | VAL-23, 27, 51 to 54 |
| 4 | `type="number"` inputs turn invalid text into `""` | `abc` would be reported as REQUIRED instead of NUMERIC, or never reach validation | UIF-14 |
| 5 | Half-way values that are inexact in binary: 1.005, 2.675, 1000.005 | `Math.round(x*100)` and `toFixed` misround them; epsilon must also work near 1e12 | FMT-05, 16 |
| 6 | Float residue and `-0.00` | A tiny negative balance would print `-€0.00` | FMT-08, 09 |
| 7 | Table does not foot: rounded interest + principal differs from rounded payment by 0.01 in 50 of the 360 V1 rows (e.g. month 9, month 360) | F§4 accepts a 0.01 discrepancy only for the summary; A7 extends it to the table | UIR-05, UIR-11 |
| 8 | Double precision drifts from the exact result at large magnitudes: V8 monthly payment differs at 3e-4 | Exact equality on money values fails; tolerance TOL1 (A9). Cent-level display still agrees for V7 and V8 | CAL-11, INT-04 |
| 9 | Annuity formula near r = 0 (0.01 %) | `1 - (1+r)^-n` loses precision as r shrinks; only r = 0 exactly is special-cased | CAL-08 |
| 10 | Loans so small the payment displays as `€0.00` | Allowed by F§2 (price 0.01); A11 accepts it | INT-05, CAL-13 |
| 11 | Final payment equals M within float error, not cents | With unrounded M the closing adjustment is about 1e-9 relative, so it hides no real error; a larger gap would signal a bug | CAL-23 |
| 12 | Cross-field rule when one side is invalid | Avoids a spurious `downPayment` error next to a `price` error (A3) | VAL-60, 61 |
| 13 | One message per field when several rules fail | `-1.234` is negative and 3 dp; range wins (A2) | VAL-58 |
| 14 | Enter key and double click | Form submit would reload the page; double render would duplicate rows | UIF-12, 13 |
| 15 | Browser locale with comma decimal (sk-SK) | Input must still use `.`; output must not switch | FMT-12, INT-15 |
| 16 | Pasted look-alike characters (full-width digits, U+2212) | Must be errors, never converted (F6.4) | VAL-55 |
| 17 | Re-render after a longer schedule | 480 rows then 12 rows must not leave stale rows | UIR-09, INT-10 |
| 18 | User input echoed into the DOM | Typing `<b>x</b>` must not produce markup; messages are fixed strings | UIF-16 |

## 11. Open points for approval

| # | Point | Default used |
|---|---|---|
| 1 | Amend F§2 with a technical cap for tax and insurance (A5) | 1,000,000,000,000 |
| 2 | Confirm `€1,234.56` display format (A6) | as stated |
| 3 | Confirm results labels without `P&I` (A13) | as stated |
| 4 | Confirm that the table may be off by 0.01 per row (A7) | accepted |
| 5 | Test runner (none installed; installing needs your approval) | none |
