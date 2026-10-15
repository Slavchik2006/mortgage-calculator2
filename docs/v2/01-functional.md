# 01 - Functional delta (V2)

V2 keeps every rule of `docs/v1/01-functional.md` (inputs, ranges, formulas, rounding, outputs, invalid-input behaviour). Only the differences are listed here.

## Added

- **F8 Anonymous session.** No accounts. The browser keeps a random session id; scenarios belong to it. Clearing browser data loses them. Calculating needs no session.
- **F9 Saved scenarios (per session).** Save the six current inputs under a name (1-60 chars); list, load into the form, overwrite, delete. Max 50 per session. Loading fills the form; the user presses Calculate (results are never stored).
- **F10 Saving requires valid inputs.** Same validation and inline errors as Calculate.

## Changed

- Calculation and validation run on a server. If it cannot be reached the page shows "Calculation service unavailable", with no results and no field errors.
- Calculate is disabled while a request is in flight.

## Non-functional

- Calculate responds in < 1 s on localhost for the maximum term (480 rows).
- A user can never read or modify another session's scenarios.

## Still out of scope

Export, sharing, charts, extra payments, variable rates, currency/locale switching, accounts, login.
