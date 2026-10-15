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

## V2 backend (session of 2026-10-15, uncommitted)

- Design: `docs/v2/01-functional.md` (delta), `docs/v2/02-architecture.md` (frontend / API / Python backend / Supabase, anonymous session id, no accounts).
- Built `backend/` (FastAPI, venv at `backend/.venv`, pins in `backend/requirements.txt`): `core/` (validation, Decimal calculation), `api/` (`/api/v1/calculate`, `/scenarios` CRUD, `/health`), `storage/` (memory default, Supabase PostgREST). Run from `backend/`: `.venv/Scripts/python -m pytest` (56 pass), `.venv/Scripts/python -m uvicorn app.main:app`.
- `supabase/migrations/20261015000000_scenarios.sql` written, NOT applied to project `mortgage_calculator` (dapqejeusrqpdhxhnbrh; empty). Needs approval + `backend/.env` with `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `STORAGE=supabase`.
- Next: apply migration and smoke-test; frontend migration (`api.js`, `session.js`, `ui/scenarios.js`, serve `frontend/` from the API); docs/v2 stages 03-06; V1 JS validation/calculation removal after the frontend switch.
- Not committed (needs approval).

### Update: frontend built (same day)

- `frontend/` (index.html, styles.css, `src/{main,api,session,formatting}.js`, `src/ui/{form,results,scenarios}.js`) calls the API; formatting works on decimal strings. Served by the API at `/` (same origin). Verified in the browser: calculate (360 rows, EUR 1,216.04 monthly P&I), inline 422 error, save scenario.
- Tests: `backend` pytest 57 pass; `npm run test:frontend` 7 pass. Root V1 tests (`npm test`) untouched.
- Old V1 `src/`, `index.html`, `tests/`, `scripts/` are still in place (no deletions without approval). Decide: remove V1 JS validation/calculation after cut-over.
- Supabase deferred by the user: scenarios use the in-memory store until the migration is applied.
- `.claude/launch.json` added for the dev server (port 8000).

### Update: Supabase data model (same day, uncommitted)

- Migration rewritten as four tables: `parameters` (6 seeded rows), `sessions`, `scenarios` (unique name per session), `scenario_values`, plus atomic `create_scenario` / `update_scenario` functions. NOT applied; SQL not executed anywhere yet (only seed parity is unit-tested).
- Backend: `core/parameters.py`, `storage/supabase.py` rewritten (embedding reads, RPC writes, `verify_parameters()` at startup), duplicate name -> 409 in memory and Supabase stores. Frontend shows 409 under the name field.
- Tests: backend pytest 72 pass.
- To go live: apply migration, create `backend/.env` (`STORAGE=supabase`, `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`), start the API (it verifies the catalog), smoke-test.
