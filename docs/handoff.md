# Handoff

## Current state

- `docs/v1/01-functional.md` done.
- `docs/v1/02-architecture.md` drafted (modular, pure core + thin UI; stack assumed browser TS/JS, no deps). Pending user review.
- `docs/v1/03-test-scenarios.md` drafted: 161 tests, 37 requirement IDs (all covered), unique names, assumptions A1-A14, no open decisions in expected outputs. Pending user approval of the assumptions.
- `docs/v1/reference_values.py` = source of all reference values (Python decimal, 60 digits; run to reproduce).
- `docs/v1/04-review.md` done: independent review, 14 findings (see its §2).
- No implementation.

## Next steps

1. Resolve the review's High findings before planning: tolerances/reference precision (1, 2, 4), double vs exact arithmetic at the 1e12 cap and principal in cents (3, 5), rounded-vs-unrounded payment (6).
2. Approve open points in `03-test-scenarios.md` §11: tax/insurance cap of 1e12 (spec gap A5, needs amendment to `01-functional.md`), `€1,234.56` display format (A6), results labels without "P&I" (A13), 0.01 table discrepancy (A7).
3. Review/confirm `02-architecture.md` §10 open questions (stack, test runner; installing a runner needs approval).
4. Write `docs/v1/05-plan.md`.
