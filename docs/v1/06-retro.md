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
