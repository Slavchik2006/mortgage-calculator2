# 06 - Retrospective (V1)

State now: the calculator works and 119 tests pass. 45 browser (DOM) tests are not written yet because `jsdom` needs an install approval. So V1 is not fully accepted.

## 1. What the plan got right

- The build order worked. Core modules first, UI last, nothing had to be reordered.
- Test IDs (VAL-01, CAL-05, ...) made progress easy to count.
- The risks about precision and tolerances were real. The plan's default (exact BigInt arithmetic) fixed them.
- Every open question had a default, so I could start without waiting for answers.
- The TECH checks (start command, README, no dependencies) became simple automated tests.

## 2. What the plan got wrong

- **Step 0 was skipped.** I used the defaults. The docs (`01`, `03`) are not updated yet, so docs and code disagree on the tax/insurance cap and on tolerances.
- **Tolerances changed.** The tests wanted 1e-12 precision, but reference values only have 10 decimals. I used 1e-8 + 1e-12 relative. The random test (CAL-33) also needed looser sums at very large loans.
- **FMT-12 changed.** Node cannot switch locale per call, so the test checks that no locale function is used.
- **Coverage script is weaker than planned.** It checks that a test exists, not that it passes.
- **Test count.** 119 run now, not 161. The missing 45 are DOM tests (the plan flagged this as a risk).
- **Skills, hooks and subagents from section 6 were never created.** So their value is unproven.

Bugs caught on the way: a payment of 1000 became 999.9999999999999 (fixed by parsing the number from a string); a wrong `append` call in `results.js` (found by reading, a DOM test would have caught it).

## 3. Prompt with the biggest impact

The independent-reviewer prompt: fresh role, read only three files, "do not trust, verify", recalculate in a separate script, no edits. It found the tolerance and precision problems that shaped the code. Second best: the "control these options" prompts, which led to `reference_values.py` and a fixed build order.

(This is my judgement from the files, not a controlled comparison.)

## 4. Review findings

Important:
- Tolerances too strict (R1, R4): tests would fail on correct code.
- Double precision at 1e12 (R3, R5): led to the BigInt design.
- Tax/insurance cap missing (R9): implemented, still not in the spec text.
- Browser-only tests (R14): the biggest blocker, 45 tests wait on it.

Not important so far:
- Rounded vs unrounded payment (R6): followed the spec, no problem appeared. Still a product decision.
- Stale results after editing (R7), wording of labels (R10), `toFixed` remark (R11), requirement tagging (R12, R13).
- The extra edge cases (spaces, `007`, `+30`) were not added.

## 5. Expected vs actual

| Expected | Actual |
|---|---|
| Reference values match to 1e-12 | Match to 10 decimals, as quoted. 1e-12 was never possible. |
| BigInt might be too costly | About 40 lines in one module. Cheap. |
| Final payment adjustment does nothing | Confirmed: it differs from M by less than 1e-9 relative. |
| Random test passes | Failed first time, because of tolerance, not maths. |
| All 161 tests green | 119 of 119 runnable are green. 45 are missing. |
| UI works once the core is green | Checked by hand in the browser: values match the tests. Not automated. |

## 6. What I would change for V2

1. Finish step 0 (update docs) before writing code.
2. Decide the test runner (jsdom or browser) when choosing the stack, not later.
3. Quote reference values with more digits and derive tolerances from them.
4. Make the coverage script check that tests pass.
5. Keep the independent review prompt, and run it again after the code exists.
6. Write each decision into the doc it changes in the same session.
7. Build a tool from section 6 only if it is actually used (the commit-guard hook is the cheapest).
8. Record timings and counts while working.

## 7. Comparison with a simple single-file calculator (no spec)

Control experiment: a plain `mortgage-calculator.html` (price, down payment, rate, term; live results; yearly table) was built in one step without reading `01`-`06`, outside the repo. Then `03-test-scenarios.md` was applied to it.

Method and limits: VAL, CAL and FMT scenarios were executed against the script of that HTML (Node, stub DOM that mimics `type=number` sanitising; reference values V1-V12 from `03` §3). UIF, UIR and INT were judged by reading the code (no jsdom). A scenario passes only if everything it asserts is observable and correct; a missing feature counts as not met. Validation was scored leniently (accept/reject plus "message names the right field", symbolic messages not required). These are my judgement numbers, not an automated run.

### 7.1 Result

| Group | Scenarios | Simple calculator | This repo (V1) |
|---|---|---|---|
| VAL | 64 | 34 | 64 |
| CAL | 33 | 6 | 33 |
| FMT | 18 | 13 | 18 |
| INT-17 (architecture) | 1 | 0 | 1 |
| UIF, UIR, INT-01..16 | 45 | 5 | not automated (checked by hand) |
| **Total** | **161** | **58 (36%)** | **116 runnable pass, 45 missing** |

The repo's 119 passing tests are these 116 runnable scenarios plus 3 TECH tests that `03` does not contain.

### 7.2 What the simple calculator did right and wrong

- Right: formula and all summary figures for V1-V12, also at the 1e12 cap (to the cent); half-up rounding of 1.005 and 2.675 (`Intl`); fixed locale; no network or storage; rejection of text, negatives, hex, `Infinity`, down >= price.
- Wrong, spec decisions (100 of the 103 misses): no tax/insurance; live recalculation instead of a Calculate button; yearly instead of monthly table; rate max 100 and term max 50 (spec 25 and 40); empty down payment treated as 0; no decimal, cap or integer-term rules; one shared error instead of one per field; results shown on load.
- Wrong, numerical (3):
  - CAL-08 (V6, 0.01 %, 40 y): total interest off by 6.6e-7, worse than even the relaxed 1e-8 tolerance. `1-(1+r)^-n` loses precision for small r (edge case 9).
  - CAL-22: closing balance is not `=== 0` (V5 1.7e-9, V3 1.1e-10, V6 6.6e-7). No final-payment adjustment; `Math.max(bal, 0)` and formatting hide it.
  - CAL-25: interest column vs total interest differs by 3.3e-9 relative on V6 (limit 1e-9).
- Formatting: `-€0.00` for -1e-12 and -0 (edge case 6 reproduced); no `RangeError` for NaN, Infinity or 1e15.

### 7.3 Against the retro

| Retro statement | Evidence from the simple calculator |
|---|---|
| The precision risk was real; BigInt fixed it (R3, R5) | Partly confirmed. Doubles are fine at 1e12 to the cent (V7, V8 pass), but fail at tiny rates (V6) and for an exactly-zero closing balance. |
| Tolerances of 1e-12 were impossible, reference has 10 decimals | Confirmed: V4, V10, V12 match M only at 1e-8. V6 misses even that, so the relaxed tolerance still catches a real defect. |
| Final-payment adjustment does nothing | True for the payment amount, but without it the closing balance is not exactly 0. |
| Edge case 4: `type=number` hides invalid text | Reproduced: `abc` and `3,5` become empty and give a "required"-style message; `.5` is accepted. |
| Edge case 6: `-€0.00` | Reproduced in the formatter. Not reached with the loans tried. |
| Step 0 / docs first | Supported: the misses are spec decisions (tax/insurance, caps, button, monthly table, error model), not arithmetic. |
| 45 DOM tests missing is the biggest blocker | Same blocker here: UI and integration had to be judged by reading code, so the 36 % has the weakest evidence in those 45 scenarios. |

### 7.4 Conclusions

1. The core maths is cheap. A spec-blind build gets the summary figures right and loses on scope, UX and validation: 100 of 103 misses.
2. The three numerical defects are exactly what the plan's precision work targeted (tiny rate, exact closing balance). The BigInt and final-payment design is justified, not over-engineering.
3. The suite separates a correct formula from a conforming implementation (36 % vs 119/119 runnable).
4. Scenarios tied to module APIs (`validate`, `collect`, `calculate`, per-field `#x-error`) cannot pass in any other implementation. For comparing implementations a DOM-only version of them is needed.
5. For V2: finish step 0 first, and automate the 45 UI/integration scenarios, otherwise any comparison stays partly manual.
