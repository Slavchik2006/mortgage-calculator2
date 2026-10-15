# mortgage-calculator2

Mortgage calculator (fixed-rate annuity, EUR) built through a staged, documented workflow (functional spec -> architecture -> tests -> review -> plan -> retro).

## Run

Requires Node `>=20` (see `engines.node` in `package.json`). No dependencies to install.

```bash
npm start
```

Then open `http://localhost:3000` (override the port with the `PORT` environment variable). Opening `index.html` directly from disk does not work: the page uses ES modules, which browsers block over `file://`.

## Test

```bash
npm test
```

Runs the built-in `node --test` runner over `tests/`. `node scripts/check-coverage.mjs` checks that every requirement ID in `docs/v1/03-test-scenarios.md` is cited by an implemented test.

## Notes on the numbers

- Money maths uses BigInt fixed-point arithmetic, so the schedule is exact even at the 1,000,000,000,000 cap; values are rounded half-up to 2 decimals only for display.
- The monthly payment is not rounded to cents before the schedule is built (spec F§3/F§4). Cells in the table are rounded independently, so a row can differ by 0.01 from the sum of its displayed parts, and the table is an estimate rather than a lender's statement.

## Structure

- `src/` - `types`, `constants`, `validation`, `calculation`, `formatting`, `ui/form`, `ui/results`, `main`
- `tests/` - `node --test` suites
- `scripts/` - static server and requirement-coverage check
- `CLAUDE.md` - project instructions for Claude Code
- `docs/handoff.md` - current state and next steps
- `docs/v1/` - v1 workflow artifacts (01-functional ... 06-retro, prompts)

## V2 (frontend + API + Python backend)

V2 moves validation and calculation to a Python API; the V1 files in `src/` and `index.html` are kept for reference until the cut-over is approved. Design: `docs/v2/02-architecture.md`.

Run (Windows PowerShell; from the repo root):

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000` (the API serves `frontend/`; API docs at `/docs`).

Test: `.\.venv\Scripts\python.exe -m pytest` in `backend/`, and `npm run test:frontend` in the repo root.

Saved scenarios use an anonymous per-browser session id. Storage is in memory by default; set `STORAGE=supabase`, `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY` (see `backend/.env.example`) after applying `supabase/migrations/`.
