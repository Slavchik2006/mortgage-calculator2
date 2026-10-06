# Handoff

## Current state

- Docs `01`-`05` done (see `docs/v1/`). `05-plan.md` committed and pushed (25f067c).
- **Implementation done, uncommitted** (plan steps 1-8 built in one session on the plan's defaults):
  - `src/`: `types`, `constants`, `formatting`, `validation`, `calculation`, `ui/form`, `ui/results`, `main`; `index.html`, `styles.css`.
  - `scripts/serve.mjs` (`npm start`, port 3000 / `PORT`), `scripts/check-coverage.mjs`.
  - `package.json` (no dependencies, `engines.node >=20`), `README.md`, `.gitignore`.
- `npm test`: 119 tests, 0 fail. Covers VAL-01..64, CAL-01..33, FMT-01..18, INT-17, TECH-02/03/05.
- Manually verified in the browser pane: V1 summary, first/last rows, 360 rows, invalid rate shows inline error and clears results.
- `node scripts/check-coverage.mjs` exits 1: F1, F5.1, F5.2, F5.4, F6.1, F6.3, F7 are only covered by DOM tests, which do not exist yet.

## Decisions taken (plan §7.2 defaults, not yet approved by the user)

- Plain JS (ES modules) + `node --test`; no installs.
- Unrounded monthly payment, as in F§3/F§4 (R6). README states the table is an estimate.
- Arithmetic: BigInt fixed point (cents x 1e40) in `calculation`, exact at the 1e12 cap (R3, R5); outputs are unrounded doubles. `formatEur` rounds half-up on the shortest decimal string (A6).
- Tax/insurance cap 1e12 (A5) implemented in `constants`/`validation`; `01-functional.md` is NOT yet amended.
- Deviation from `03` A9: reference values are quoted to <= 10 dp, so CAL tests use 1e-8 abs + 1e-12 rel (instead of TOL1) and column sums use 1e-12 x P + 1e-6 (R1, R4). `03` is not yet updated.
- FMT-12 is checked by asserting no locale API is used (no process-locale switch in Node).
- Test counts differ from the plan's 161: DOM tests (UIF-01..16, UIR-01..13, INT-01..16 = 45) are missing.

## Next steps

1. Decide DOM test approach (needs install approval): `jsdom` for UIF/UIR/INT-01..16, plus a headless browser only for UIR-08, UIR-13, UIF-12 (plan risk 5). Without installs those 45 tests are NOT MET.
2. Step 0 doc amendments: `01-functional.md` (tax/insurance cap), `03` tolerances and new edge cases (R§3), final test count.
3. `.claude/` skills/hooks/subagents from plan §6 are not created.
4. Review and commit (needs approval). Suggested split per plan §4, or one commit.

## Notes

- Commits, pushes and installs need explicit approval (project `CLAUDE.md`).
- Nested folder `mortgage-calculator2/mortgage-calculator2/` is an older separate repo (own `.git`); ignored.
