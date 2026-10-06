# 04 - Review (V1)

Independent review of `01-functional.md`, `02-architecture.md` and `03-test-scenarios.md`. Reviewer read only these three files and did not trust their claims. All reference values were recomputed in a separate script (Python `decimal`, 80 digits) and a double-precision mirror of the planned implementation. No project files were modified by the review.

## 1. Summary of checks

- **Coverage:** all 37 requirement IDs in the `03-test-scenarios.md` catalogue are cited by at least one test, and every requirement has at least 2 tests. 161 tests, unique IDs and names. Two tests cite no F-requirement: CAL-32 and INT-17 (architecture only).
- **Reference values:** V1-V12, the V1 rows 1, 2, 9 and 360, and the V7 row 480 interest all recompute correctly. The largest difference from the quoted totals is 3.6e-9, which is the 8 dp truncation. Also correct: the 50 non-footing V1 rows, the V1 and V7 display strings, FMT-04/05/06/10/15/16, INT-03/04/05/10, UIR-01/04/05/11.
- **Where claims break:** the values are right, but the tolerances and the double-precision assumptions around them are not (findings 1-5).

## 2. Findings

| # | Severity | Finding (verified) | Affects |
|---|---|---|---|
| 1 | High | Reference values are quoted to 10 dp but compared with TOL1 (1e-12 relative); even a perfect implementation fails. CAL-09 M: diff 3.8e-11 vs tolerance 1e-12. CAL-09 row-1 interest: diff 3.3e-11 vs 1e-12. CAL-13 M: diff 2.9e-12 vs 1e-12. CAL-13 totalPaid `0.01032797`: diff 1.6e-9 vs 1e-12. CAL-23 row 360 interest: diff 5.0e-11 vs tolerance 6e-12. CAL-23 row 360 principal: diff 8.3e-9 vs tolerance 1.2e-9. | CAL-09, CAL-13, CAL-23; A9 |
| 2 | High | CAL-08 (V6, 0.01 %, 40 y) fails TOL1 when `1 - (1+r)^-n` is computed literally as in F§3: M is off by 1.4e-9 vs tolerance 2.1e-10; totalInterest by 6.6e-7 vs 2e-10. It passes only with `expm1`/`log1p`. Spec and architecture do not say which form to use; edge case #9 notes the risk but leaves it open. | CAL-08; A§3.4; F§3 |
| 3 | High | "Double precision is sufficient for price <= 1e12" (A§1) is false for cent-accurate output. V7 schedule: 493 of 1920 displayed cells differ from the decimal result at the cent level, maximum error 1.47. The final payment differs from M by 1.47, which contradicts edge case #11 ("about 1e-9 relative"). V8: 4 of 48 cells wrong, maximum error 3.5e-3. CAL-10 and INT-04 check only M, last-row interest and last balance (forced to 0), so they cannot see this. | A§1, A§6; CAL-10/11, INT-04; UIR (table at large values) |
| 4 | High | The tolerance for "principal column sums to P" is 1e-9 x P (A9/TOL2). At P = 1e12 that allows 1000 EUR of error, so the check says nothing at cent level. | CAL-24, CAL-33; A9 |
| 5 | Medium | `P = price - down` in doubles loses cents at large magnitude. Price `1000000000000`, down `999999999999.99` gives `0.010009765625` instead of 0.01 (0.1 % error). No test covers it (VAL-04 tests validation only). Integer-cent arithmetic would avoid it. | F2.7; `calculation`; missing test |
| 6 | High (ambiguity) | F§3/F§4 use an unrounded M, so the "final payment adjusted so balance_n = 0.00" rule does nothing (V1 diff about 1e-73). Real lenders round M to cents, and two valid implementations then give different totals: V1 total paid is 431,676.38 with unrounded M, about 431,676.00 with M rounded to 1,199.10. Displayed table rows also do not sum to the displayed Total paid. | F§3, F§4, F§5.2; CAL-23; UIR-05 |
| 7 | Medium (ambiguity) | F§6 "no results until every field is valid" does not say whether results stay visible after an input is edited without pressing Calculate. UIF-11 says they stay (stale numbers beside changed inputs); this is a design choice, not a spec statement. | F6.3; UIF-11; `main` |
| 8 | Medium (ambiguity) | The numeric grammar is invented in A1/A2. Does `250000.500` meet "<= 2 dp"? Is `30.0` a valid integer term? What about `.5`, `+1`, leading zeros, and the cross-field error being placed on `downPayment`? Each could reasonably go the other way. | F§2, F§6; VAL-23/27/51-53, VAL-05 |
| 9 | Medium | The tax and insurance cap (A5) is a spec gap: without it a 400-digit value gives `Infinity`/NaN in `calculate`. `01-functional.md` is not yet amended. | F2.5, F2.6; VAL-32-36 |
| 10 | Medium (ambiguity) | F§1 says "minimal jargon" but F§5 names "Monthly P&I". Labels, the `€1,234.56` format and the 0.01 table discrepancy (A7, which extends F§4's allowance from the summary to the table) are assumptions. | F1, F4.2, F4.3; A6, A7, A13 |
| 11 | Low | A§6 says `toFixed` has "banker-style behaviours [that] differ across engines". In JS `toFixed` is deterministic and rounds the exact binary value half-up: `(0.125).toFixed(2)` = `0.13`, `(1.005).toFixed(2)` = `1.00`. FMT-04's remark that banker's rounding gives `€0.12` is moot. A§6 ("epsilon-safe `Math.round`") and A6 ("shortest decimal representation") also describe different algorithms. | A§6, A6; FMT-04/05/16 |
| 12 | Low | CAL-32 and INT-17 cite no F-requirement. UIF-15/16, UIR-13, FMT-11/14, FMT-18, CAL-31 and VAL-64 are attached to F-IDs but test assumptions the spec does not state (A10, A12, A6, security). F1 "plain language" is checked only by label strings. | Check 1; F1, F6.2, F4.2 |
| 13 | Low | `index.html` and `styles.css` have no owner in the §3.9 coverage table, yet F1, F5.4 and the A10/A14 ids and CSS live there. Where the error-message text lives (`validation` or `ui`) is not stated. A§7 says invalid state is "unrepresentable" but also that `calculate` throws on violations. | A§3, A§6, A§7 |
| 14 | Low | UIR-08 (`scrollHeight > clientHeight`, computed style), UIR-13 (timing) and UIF-12 (no page reload) need a real browser, since jsdom has no layout. The test runner is still undecided (open point 5). | UIR-08/13, UIF-12; runner choice |

## 3. Missing edge cases and invalid inputs

- **Cross-field:** price `0` with down `0` (expect only the price error, no down error); price `0.01` with down `0.01`; price empty with a valid down.
- **Large-magnitude arithmetic:** price `1e12` with down `999999999999.99` (finding 5); tiny P with a high rate (P = 0.01, 25 %, 40 y). No test compares intermediate table cells with decimal references at large values (finding 3).
- **Paste artifacts:** non-breaking space, tab or newline in a pasted value. A1 trims ASCII whitespace only; VAL-55 covers only full-width digits and U+2212.
- **Zero forms:** `-0` is tested only for down payment. Rate, tax and insurance are untested, and so are `-0.00`, `0.00` and `00`.
- **Term forms:** `007`, `+30`.
- **Terminology:** F§6 lists "negative" and "out of range" as separate invalid cases, but the tests merge them into one RANGE message.
- **Interaction:** Calculate clicked while a previous render is in progress; repeated Enter keypresses.

## 4. Out-of-scope features and the modules they would change

| Feature | Modules that change | Note |
|---|---|---|
| Extra payments | `types` (`RawInput`, `LoanInput`, `ScheduleRow` gets an extra column, `Summary` gets payoff month and its totals); `constants` (new limits); `validation` (new fields, rule order, a cross-field rule against the balance); `calculation` (the recurrence, the `n` rows invariant, the final payment, and `totalPaid = M x n`, which stops being true); `ui/form` (new fields); `ui/results` (new column, shorter table); `index.html`, `styles.css` | A§9 says `ScheduleRow` is stable; it is not. `formatting` and `main` stay unchanged. |
| CSV export | New `ui/export`; `main` (wiring); `formatting` (a plain numeric format instead of `€1,234.56`, with its own separator choice); `index.html` (button) | INT-14 and UIR-08 flip. It touches `formatting` and `main`, which A§9 does not mention. |
| i18n and multi-currency | `formatting` (separators, symbol); `validation` (the `.`-only grammar in A1, and the error messages); `ui/form` (labels, `collect`); `ui/results` (labels, headers); `constants` (currency); `index.html` | A§9's "confined to `formatting` and UI labels" is wrong: `validation` parsing and message text change too (F2.8, A1, A4). `calculation` is unaffected. |

## 5. Reproduction

The recalculation scripts were run from the session scratchpad and are not stored in the repo. They implement the F§3 recurrences with `decimal` at 80 digits, a double-precision mirror with a naive and a `log1p` variant of the annuity formula, a parse of the `03-test-scenarios.md` tables for coverage and uniqueness, and Node checks of `toFixed` and `Number()` behaviour.
