# Prompts

Log of key prompts used for v1 (trivial follow-ups merged or omitted).

## 1. Repo scaffold

> i want to create a repo named mortgage-calculator2 on my github with this structure
> mortgage-calculator2/
> ├── README.md
> ├── CLAUDE.md
> ├── docs/
> │   ├── handoff.md
> │   └── v1/
> │       ├── 01-functional.md
> │       ├── 02-architecture.md
> │       ├── 03-test-scenarios.md
> │       ├── 04-review.md
> │       ├── 05-plan.md
> │       ├── 06-retro.md
> │       └── prompts.md
> └── .claude/
> dont implement the calculator yet, only create a repo and basic file structure

Follow-up decisions: create the structure fresh in the outer folder (existing nested folder left untouched); public GitHub repo.

## 2. Functional scope interview

> I want to define the functional scope of Version 1 of the mortgage calculator.
> Interview me about the functional scope of V1.
> Your goal is to help me decide: who will use the calculator, what inputs it accepts, what it calculates, what outputs it displays, valid input ranges, invalid inputs, calculation rules, rounding rules, what is explicitly outside the scope of V1.
> Do not create or modify any files yet.

## 3. Write the functional spec

> yes, now you can write this into file

Result: `docs/v1/01-functional.md`.

## 4. Commit and push

> commit it / commit the rest / push it

Result: spec and scaffold committed, pushed to `origin/master`.

## 5. Log prompts

> i want to fill the prompts.md with the prompts from this session, but only important prompts for example you can unite commit and push as one prompt

## 6. Architecture draft

> i want to do a 02-architecture.md file from my github repo mortgage-calculator2, propose a modular architekture(read first 01-functional.md)

Result: `docs/v1/02-architecture.md` (pure core + thin UI; stack assumed browser TS/JS, no dependencies); `docs/handoff.md` updated.

## 7. Module detail

> For each module give responsibility, interface and which requirements it implements
> each module need to describe in one sentence

Result: per-module subsections (responsibility, interface, requirements by spec section, dependencies), a one-sentence description per module, and a spec-to-module coverage table.

## 8. Commit and log prompts

> ok, commit this and do prompts.md for this session

## 9. Test scenarios

> read 01-functional.md and 02-architecture.md and give me test scenarios for file 03-test-scenarious.md in table with columns: test, level, module, input, source of expected value and type(happy path, edge case, invalid input) and also list edge cases that i havent mentioned

Result: first draft of `docs/v1/03-test-scenarios.md` (about 130 tests, edge-case list).

## 10. Test scenario quality check

> can you control this options: each requirement from layer 1 appears in the ' Verifies Requirement ' column, each test has an unique name, no expected output is vague, each reference value has a source
> if something wrong correct it

Result: `03-test-scenarios.md` rewritten (37 requirement IDs, 161 tests, unique names, assumptions A1-A14, no open decisions); `docs/v1/reference_values.py` added as the source of reference values. Corrected: V8 float vs decimal value, V4 precision, final-payment claim.

## 11. Commit and push

> commit and push and add prompts to prompts.md

## 12. Independent review (layer 4)

> You are an independent reviewer. You did not write this plan.
> Read only: `docs/v1/01-functional.md`, `docs/v1/02-architecture.md`, `docs/v1/03-test-scenarios.md`. Do not trust the claims; verify them.
> Check: 1. Every requirement has a module and at least one test, and every test covers a real requirement. 2. Ambiguous requirements that could lead to different implementations or results. 3. Missing edge cases and invalid inputs. 4. For 3 out-of-scope features, specify exactly which modules would need changes. 5. Recalculate every reference value in a separate script. Do not estimate.
> Return numbered findings in a table with severity and what each finding affects. Do not modify any files.

Result: 14 findings (4 High, 1 High ambiguity, 4 Medium, 5 Low); all 12 reference values correct, but tolerances unsatisfiable (CAL-08/09/13/23) and double precision insufficient at the 1e12 cap.

## 13. Write review, commit and push

> write this in 04-review.md, commit push and add prompts to the prompts.md

Result: `docs/v1/04-review.md` written, prompts logged, committed and pushed.

## 14. Build plan (layer 5)

> read first four files from docs/v1/ from my github repo mortgage-calculator and write 05-plan.md in requested structure(sections):
> section1 objectives of v1 (2-4objectives); section2 scope - reference to 01-functional.md; section3 acceptance Criteria (Functional: list the tests from 03-test-scenarios.md that must pass, no criterion without a corresponding test; Technical: the test command passes without errors, the application starts with a single command, the README explains how to run it); section4 Build Order (modules ordered by dependencies; for each step the module, the tests that must pass, one commit); section5 Definition of Done for each step (module tests green, previous tests green, commit, handoff); section6 Build Tools (skills, hooks, subagents from Hour 3 and why); section7 Risks and Open Questions

Result: `docs/v1/05-plan.md` written (4 objectives, 161 tests assigned to 9 steps, 7 risks + 6 open questions).

## 15. Plan control

> control this plan with this options: 1. each acceptance criterion is a specific test or command with an unambiguous result 2. the build order respects the dependencies from 02-architecture.md

Result: technical criteria replaced by TECH-01..05 (fixed commands and expected results); UIF-09/10/11/13/16 moved from step 5 to step 7 (they need the full flow); dependency table added.

## 16. Commit and push

> commit push and add prompts to prompts.md

## 17. Build from the plan

> build a mortgage calculator with a plan from my github repo mortgage-calculator2 file 05-plan.md

Result: steps 1-8 built on the plan's defaults (plain JS, BigInt cents arithmetic, `node --test`); 119 tests green; 45 DOM tests not written (jsdom needs install approval); step 0 doc amendments and `.claude/` tools not done. `handoff.md` updated.

## 18. Retrospective

> now you need to write 06-retro.md (six questions: what the plan got right/wrong, biggest prompt change, review findings, experiment results, V2 methodology changes)
> make it more simplier

Result: `docs/v1/06-retro.md`, first detailed, then rewritten in plain language.

## 19. Commit, push, fix prompts

> commit push and correct the prompts.md

Result: implementation and docs committed and pushed; prompts 17-19 added.
