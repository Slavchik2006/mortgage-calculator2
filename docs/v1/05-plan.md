# 05 - Plan (V1)

Derived from `01-functional.md` (F§), `02-architecture.md` (A§), `03-test-scenarios.md` (T§) and `04-review.md` (R). Test IDs are those of `03-test-scenarios.md`; nothing is renamed here.

## 1. Objectives of V1

1. **Correct payment maths.** A pure calculation core that reproduces the decimal reference values (V1-V12) and closes every schedule at exactly 0.00, within tolerances that a correct implementation can actually meet (R findings 1-4).
2. **Strict, honest input handling.** Raw strings are validated into a typed `LoanInput` or per-field errors; nothing is clamped, corrected or echoed as markup (F§6, A§6).
3. **Usable single-page app.** Six labelled fields, a Calculate button, inline errors, a summary block and a scrollable amortization table, all in EUR, half-up 2 dp (F§1, F§4, F§5).
4. **Verifiable delivery.** Every acceptance criterion maps to an automated test; the app starts with one command and the README says how (section 3).

## 2. Scope

The scope of V1 is exactly `docs/v1/01-functional.md`: inputs (§2), calculation rules (§3), rounding (§4), outputs (§5), interaction and invalid input (§6). Out of scope is F§7 (variable rates, extra payments, refinancing, export/save/share, charts, multi-currency, i18n, comparison); INT-14 asserts its absence.

Amendments that this plan makes part of scope (they close spec gaps; see section 7 for the approval gate): tax and insurance technical cap 1e12 (T§2 A5), decision on rounded vs unrounded M (R6), and the assumptions A1-A14 as stated in T§2.

## 3. Acceptance criteria

### 3.1 Functional

V1 is accepted when all 161 tests of `03-test-scenarios.md` pass. No criterion is listed without a test, and no test is left out:

| Group | Tests that must pass | Count | Requirements verified |
|---|---|---|---|
| Validation | VAL-01 ... VAL-64 | 64 | F2.1-F2.8, F6.2, F6.4, F6.5.1-F6.5.7 |
| Calculation | CAL-01 ... CAL-33 | 33 | F2.7, F3.1-F3.8, F4.1, F4.4, F5.3 |
| Formatting | FMT-01 ... FMT-18 | 18 | F2.8, F4.1-F4.4 |
| UI form | UIF-01 ... UIF-16 | 16 | F1, F2.1-F2.6, F6.1-F6.5.2 |
| UI results | UIR-01 ... UIR-13 | 13 | F1, F4.2-F4.4, F5.1-F5.4, F6.3 |
| End to end / architecture | INT-01 ... INT-17 | 17 | F2.x, F3.x, F4.x, F5.x, F6.x, F7 |

Pass/fail of each criterion is binary: the named test ID reports pass in the `node --test` output. "Pass" means status `ok`; `skip`, `todo` or a missing ID counts as fail. The set is closed: V1 is accepted when every ID in the table, plus any ID added in step 0, is present and passing. Nothing outside this list is an acceptance criterion.

Requirement-level traceability is T§1 (37 requirement IDs, each cited by at least 2 tests per R§1). Check (command, unambiguous result): `node scripts/check-coverage.mjs` exits 0 only if every requirement ID in T§1 appears in at least one passing test's `Verifies requirement` cell; it exits 1 and lists the uncovered IDs otherwise. This script is part of TECH-04 below.

Where the tests need correction before they can pass (R findings 1, 2, 4, 5, 11 and the "missing edge cases" in R§3), the correction goes into `03-test-scenarios.md` in step 0 with the new expected values written out, so that every expected value is a number or string and not a judgement. Corrected tests keep their IDs; added tests get new IDs; none is deleted silently. Step 0 ends with the final test count written into this table and into `handoff.md`.

### 3.2 Technical

Each technical criterion is a test or command with a fixed expected result. The TECH tests live in `tests/tech.test.js` and are counted in `npm test`.

| ID | Criterion | Command / test | Expected result |
|---|---|---|---|
| TECH-01 | The test command passes without errors | `npm test` | exit code 0; output reports `fail 0`, `skipped 0`, `todo 0`; the number of passing tests equals the count in 3.1 plus the TECH tests |
| TECH-02 | The application starts with a single command | `npm start` in the background, then `curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/` (port fixed at 3000, overridable by `PORT`) | `npm start` does not exit within 5 s; HTTP status `200`; response body contains `<button` and the text `Calculate`; also `/src/main.js` returns `200` with a JavaScript content type |
| TECH-03 | The README explains how to run it | test reads `README.md` | contains the exact strings `npm test` and `npm start`, `http://localhost:3000`, and the minimum Node version stated in `package.json` `engines.node`; each appears inside a fenced code block or inline code |
| TECH-04 | Every requirement has a test | `node scripts/check-coverage.mjs` | exit code 0 (see 3.1) |
| TECH-05 | No runtime dependencies | test reads `package.json` | `dependencies` is absent or `{}`; `devDependencies` contains only packages approved in step 0 |

TECH-02 is run as an automated test (child process spawn, fetch against the port, kill at the end), not by hand.

## 4. Build order

Dependencies come from A§3: `types`, `constants` and `formatting` depend on nothing; `validation` and `calculation` depend on `types`/`constants`; `ui/*` depend on `types` (and `formatting` for results); `main` depends on everything. Each step is one commit. All commits need explicit approval per `CLAUDE.md`.

Stack assumption (A§10 open question 1): plain JavaScript (ES modules, JSDoc types), tests with the built-in `node --test`, so nothing has to be installed. Module names and signatures from A§3-4 are unchanged; only the extension changes (`.ts` to `.js`).

| Step | Module | Tests that must pass | Commit |
|---|---|---|---|
| 0 | **Decisions, no code.** Resolve R findings 1-6, approve T§11 open points and A5, choose the DOM test approach. Amend `01-functional.md` (cap) and `03-test-scenarios.md` (tolerances, reference precision, new edge cases). | none (documents only). Command check: `python docs/v1/reference_values.py` exits 0 (currently does) and every reference value quoted in `03` §3 equals its output at the stated number of digits | `docs: resolve review findings, amend spec and tests` |
| 1 | **Scaffold + `types` + `constants`** (`package.json` with `test`, `start` and `engines`, `src/`, `tests/`, `scripts/serve.mjs`, `scripts/check-coverage.mjs`, an empty `index.html`). Depends on nothing (A§3.1, A§3.2). | INT-17 (dependency direction; passes vacuously until more modules exist, so it guards every later step); TECH-01, TECH-05 | `feat: project scaffold, types, constants` |
| 2 | **`formatting`** (`formatEur`, `roundHalfUp2`) | FMT-01 ... FMT-18; INT-17 | `feat: formatting module` |
| 3 | **`validation`** (`validate`, error messages) | VAL-01 ... VAL-64; FMT-*; INT-17 | `feat: validation module` |
| 4 | **`calculation`** (`calculate`: annuity, `r = 0` branch, schedule, final payment) | CAL-01 ... CAL-33; VAL-*; FMT-*; INT-17 | `feat: calculation module` |
| 5 | **`ui/form`** + `index.html` form markup + `styles.css` (form part). Depends on `types` only (A§3.6). | UIF-01 ... UIF-08, UIF-12, UIF-14, UIF-15 (these use `collect`, `showErrors`, `clearErrors`, `onCalculate` with a handler spy; none needs `validate`, `calculate` or `ui/results`); all earlier tests | `feat: ui/form` |
| 6 | **`ui/results`** + results markup and table CSS. Depends on `types`, `formatting` (A§3.7); tests feed it `calculate(...)` output, available since step 4. | UIR-01 ... UIR-13; all earlier tests | `feat: ui/results` |
| 7 | **`main`** (composition root). Depends on all modules (A§3.8). | INT-01 ... INT-16; UIF-09, UIF-10, UIF-11, UIF-13, UIF-16 (each clicks Calculate and so needs the full flow); all earlier tests | `feat: main wiring, end-to-end` |
| 8 | **Docs and release check** (README, `npm start`, `handoff.md`, retro input) | TECH-01 ... TECH-05; full suite via `npm test` | `docs: README and V1 wrap-up` |

Dependency check against A§3 (each module's "Depends on" line; a step may only need modules from earlier steps):

| Step | Module | A§ "Depends on" | Provided by step |
|---|---|---|---|
| 1 | `types`, `constants` | nothing | - |
| 2 | `formatting` | nothing | - |
| 3 | `validation` | `types`, `constants` | 1 |
| 4 | `calculation` | `types`, `constants` | 1 |
| 5 | `ui/form` | `types` | 1 |
| 6 | `ui/results` | `types`, `formatting` | 1, 2 |
| 7 | `main` | all | 1-6 |

All 161 test IDs are assigned to exactly one step in the table above (VAL to 3, CAL to 4, FMT to 2, UIF to 5 and 7, UIR to 6, INT-01..16 to 7, INT-17 to 1), so no test is scheduled before the module it exercises exists.

Ordering notes:

- `formatting` comes before `validation` because it has no dependencies and its half-up rule is the only non-trivial rounding in the project (R finding 11); finishing it first removes the temptation to round anywhere else.
- `calculation` follows `validation` but does not import it (A§2 principle 2); the order is only for review convenience, steps 3 and 4 are interchangeable.
- UI steps come after the core is green, so a UI failure never has to be debugged together with a maths failure.

## 5. Definition of Done for each step

A step is done only when all of the following hold:

1. **Module tests green:** every test listed for the step in section 4 passes under `npm test`.
2. **No regressions:** the whole suite from earlier steps still passes (the command is always the full `npm test`, never a subset).
3. **Commit created:** one commit with the message from section 4, made only after the user approves it; no push without approval.
4. **Handoff provided:** `docs/handoff.md` updated with current state, what was verified (test counts), open decisions and the next step.

Additionally for every step: no dependency added without approval, no file outside the step's module and tests changed except `handoff.md`, and any deviation from `02-architecture.md` is recorded in `handoff.md` rather than made silently.

## 6. Build tools

The repo has no `.claude/` configuration yet (only `.gitkeep`), so the items below are to be created in step 0/1 (names are working names; adapt to what was set up in Hour 3):

| Tool | Use | Why |
|---|---|---|
| **Skill `/end-session`** | At the end of every step: run `npm test`, update `docs/handoff.md`, show the proposed commit message and `git status`; it never commits. | Enforces DoD items 2-4 the same way every time and matches the `CLAUDE.md` rule that `handoff.md` is updated each session and commits need approval. |
| **Hook: test on edit** (PostToolUse on Edit/Write for `src/**` and `tests/**`, runs `npm test`) | Immediate red/green feedback while implementing a module. | Catches regressions in earlier modules (DoD item 2) at the moment they are introduced; the suite is fast (pure functions, no browser until the UI steps). |
| **Hook: commit guard** (PreToolUse on `git commit` / `git push`: block unless approved in chat) | Backs up the written rule. | A rule in `CLAUDE.md` can be forgotten; a hook cannot. |
| **Subagent `calc-verifier`** | After step 4 (and again after step 8): in a fresh context, recompute V1-V12 and a sample of schedule rows with `docs/v1/reference_values.py` (Python `decimal`), compare with the JS output at cent level for the full table at V1, V7, V8, and report differences. It does not edit code. | R finding 3 shows that the unit tests could not see cent-level drift in the table at large values. An independent implementation that did not write the code avoids "the author checks their own arithmetic". |
| **Subagent `spec-checker`** (optional) | At step 8: read `01`, `03` and `npm test` output and list any requirement ID without a passing test. | Confirms the "no criterion without a test" rule mechanically instead of by eye. |

## 7. Risks and open questions

### 7.1 Risks

| # | Risk | Likelihood / impact | If it happens |
|---|---|---|---|
| 1 | **Reference tolerances unreachable** (R1, R2, R4): tests compare 10-dp reference values with 1e-12 tolerance; `1 - (1+r)^-n` at r = 0.01 %/12 loses precision. A correct implementation fails CAL-08/09/13/23. | High / blocks step 4 | Step 0 fixes the tests: quote references at 15+ dp or compare at an explicit absolute tolerance; use `expm1`/`log1p` in `calculate` (the formula is mathematically identical to F§3). Record the choice in `02-architecture.md`. |
| 2 | **Double precision at 1e12** (R3, R5): cent-level errors in the V7 table (493 of 1920 cells off, up to 1.47) and in `price - down`. | High / wrong money shown at the cap | Preferred fix: integer-cent arithmetic for `P`, and decimal-safe accumulation for the schedule (e.g. BigInt cents with a scaled rate, or `BigInt`-based fixed point). If that is too costly, lower the technical cap (needs an F§2 amendment and approval). Add a table-level comparison at V7/V8 to `03` and let `calc-verifier` check it. |
| 3 | **Rounded vs unrounded M** (R6): the spec's final-payment rule is vacuous with unrounded M; real lenders round M, and totals differ (431,676.38 vs about 431,676.00). | Medium / user-visible, changes reference values | Default: keep the spec (unrounded M, round for display) and state in the README that the table is an estimate and does not foot to the cent. If the user chooses rounded M, `F§3/F§4` and the V-table are amended first and all dependent tests regenerated before step 4. |
| 4 | **Display discrepancy** (A7/R10): table cells rounded independently do not foot in 50 of 360 V1 rows. | Certain / cosmetic | Accepted by default; documented in README. If rejected, introduce a rounded-schedule mode in `calculation` and update UIR-05/11. |
| 5 | **Tests that need a real browser** (R14): UIR-08 (layout), UIR-13 (timing), UIF-12 (no reload) cannot run in jsdom; the runner is undecided and installing one needs approval. | High / "no criterion without a test" at risk | Decision in step 0, in order of preference: (a) approve `jsdom` for DOM tests plus a headless-browser dev dependency (e.g. Playwright) only for those three tests; (b) approve one headless browser for all DOM tests; (c) if nothing may be installed, UIR-08, UIR-13 and UIF-12 cannot be automated; they are then reported as NOT MET in `handoff.md` rather than checked by hand, because a manual check has no unambiguous result. |
| 6 | **Unrepresentable ES modules over `file://`**: `index.html` opened by double-click shows a blank page. | Medium / user confusion | `npm start` serves over http with a Node built-in server; README states that opening the file directly does not work. |
| 7 | **Spec ambiguity in input grammar** (R8, A1/A2): `250000.500`, `30.0`, `.5`, `+1`, leading zeros. | Medium / rework of VAL tests | Defaults in `03` stay unless the user changes them in step 0; any change updates VAL IDs listed in T§2 "Tests affected" and nothing else. |
| 8 | **Scope creep from the "missing edge cases"** (R§3): paste artefacts (NBSP, tabs), `-0` on other fields, `007`, `+30`. | Medium / test count grows | Add them as new tests in step 0 only if cheap; each uses the grammar already fixed in A1, so most become rows in existing tables. |
| 9 | **Stale results after editing inputs** (R7, UIF-11): results stay visible next to changed inputs. | Low / confusing UX | Kept as the tested behaviour (no live recalculation, F§6). Optional: mark the results block as outdated; that would be a spec change, not a V1 requirement. |
| 10 | **Process: commits and installs need approval.** Waiting for approval can stall a step. | Low | Prepare commit message and diff summary in `/end-session`, ask once per step. |

### 7.2 Open questions (to resolve in step 0)

1. Approve the four open points of T§11 (cap for tax/insurance, `€1,234.56` format, labels without "P&I", 0.01 table discrepancy) and amend `01-functional.md` for the cap.
2. Rounded or unrounded monthly payment (R6)? Default: unrounded, as written.
3. Arithmetic model: doubles with corrected tolerances, or integer-cent/BigInt for money (R3, R5)? Default: BigInt-cent for `P` and the schedule if the cap stays at 1e12; otherwise lower the cap.
4. Stack: plain JS + `node --test` (assumed) or TypeScript (needs a compiler install)? Default: plain JS.
5. DOM and browser-only tests: which of the options in risk 5 is approved?
6. Which Hour 3 skills, hooks and subagents already exist and can be reused instead of the working names in section 6?
