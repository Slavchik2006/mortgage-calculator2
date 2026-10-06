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
