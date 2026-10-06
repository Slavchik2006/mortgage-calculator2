# Handoff

## Current state

- `docs/v1/01-functional.md` done.
- `docs/v1/02-architecture.md` drafted (modular, pure core + thin UI; stack assumed browser TS/JS, no deps). Pending user review.
- `docs/v1/03-test-scenarios.md` drafted: 161 tests, 37 requirement IDs (all covered), unique names, assumptions A1-A14, no open decisions in expected outputs. Pending user approval of the assumptions.
- `docs/v1/reference_values.py` = source of all reference values (Python decimal, 60 digits; run to reproduce).
- `docs/v1/04-review.md` done: independent review, 14 findings (see its §2).
- `docs/v1/05-plan.md` done (committed and pushed, 25f067c): 4 objectives, acceptance criteria = 161 tests + TECH-01..05, 9 build steps (0 = decisions, 1-8 = modules in dependency order, one commit each), DoD, build tools, 10 risks, 6 open questions. Checked against: every criterion is a test/command with a fixed result; build order matches the "Depends on" lines of `02`.
- No implementation. Stack assumed in the plan: plain JS (ES modules) + `node --test`, no installs.
- Not yet created: `.claude/` skills/hooks/subagents named in plan §6 (`/end-session`, test-on-edit hook, commit guard, `calc-verifier`).

## Next steps

1. Step 0 of the plan (no code): decide the open questions in `05-plan.md` §7.2 and amend docs accordingly:
   - Review High findings: tolerances/reference precision (1, 2, 4), double vs exact arithmetic at the 1e12 cap and principal in cents (3, 5), rounded vs unrounded payment (6).
   - Approve `03` §11 open points: tax/insurance cap 1e12 (spec gap A5, amend `01-functional.md`), `€1,234.56` format (A6), labels without "P&I" (A13), 0.01 table discrepancy (A7).
   - Stack (plain JS vs TypeScript) and DOM/browser test approach (jsdom / headless browser need install approval; without it UIR-08, UIR-13, UIF-12 are NOT MET).
   - Confirm which Hour 3 skills/hooks/subagents exist.
   - Write the final test count into `05-plan.md` §3.1.
2. Step 1: scaffold + `types` + `constants` (INT-17, TECH-01, TECH-05), then steps 2-8 per `05-plan.md` §4.

## Notes

- Commits, pushes and installs need explicit approval (project `CLAUDE.md`).
- Nested folder `mortgage-calculator2/mortgage-calculator2/` is an older separate repo (own `.git`); ignored by the plan.
