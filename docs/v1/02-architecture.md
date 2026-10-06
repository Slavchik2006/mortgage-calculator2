# 02 - Architecture (V1)

Derived from `01-functional.md`. Covers module boundaries, data contracts, and data flow. Test cases, plan and code are out of scope here (stages 03-05).

## 1. Assumptions

- Single-page, client-side app. No backend, no persistence, no network (V1 has no saving, accounts or export).
- Stack is not fixed by the spec. Assumed: plain TypeScript/JavaScript + HTML/CSS, no runtime dependencies (nothing to install). The module split below is stack-independent; only file extensions change.
- Calculation core is pure and has no UI/DOM dependency, so it is testable in isolation.
- Money is held as full-precision `number` (IEEE double) internally; rounding happens only in the formatting layer (spec §4). Double precision is sufficient for the spec's range (price ≤ 1e12, n ≤ 480).

## 2. Design principles

1. **Pure core, thin shell.** `validation`, `calculation`, `formatting` are pure functions. Only `ui` touches the DOM.
2. **One-directional dependencies.** `ui → (validation, calculation, formatting)`; the three core modules never import `ui`; `calculation` never imports `validation`.
3. **Parse, don't clamp.** Raw input strings are validated into a typed `LoanInput` or a set of field errors; nothing is silently corrected (spec §6).
4. **Round late.** Rounding exists in exactly one module (`formatting`).

## 3. Module overview

```
src/
  types.ts          shared data contracts (no logic)
  constants.ts      limits from spec §2 (single source of truth)
  validation.ts     raw strings -> LoanInput | FieldErrors
  calculation.ts    LoanInput -> MortgageResult (summary + schedule)
  formatting.ts     number -> display string (EUR, 2 dp, half-up)
  ui/
    form.ts         reads fields, shows inline errors, Calculate button
    results.ts      renders summary block + amortization table
  main.ts           composition root: wires form -> validate -> calculate -> render
index.html
styles.css
```

Requirement references use the section numbers of `01-functional.md` (e.g. F§3 = "Calculation rules"). Interfaces use the types defined in §4.

### 3.1 `types`
> Defines the data shapes shared by all modules, with no logic of its own.

- **Responsibility:** shared data contracts only; no logic.
- **Interface:** `RawInput`, `LoanInput`, `FieldName`, `FieldErrors`, `ValidationResult`, `ScheduleRow`, `Summary`, `MortgageResult` (see §4).
- **Implements:** F§2 (field set, optional fields), F§5 (shape of outputs).
- **Depends on:** nothing.

### 3.2 `constants`
> Holds the numeric limits from the spec in one place so no other module hard-codes them.

- **Responsibility:** single source of truth for spec limits; used by `validation` and tests.
- **Interface:** `MAX_PRICE = 1e12`, `RATE_MIN = 0`, `RATE_MAX = 25`, `TERM_MIN = 1`, `TERM_MAX = 40`, `MAX_DECIMALS = 2`, `MONTHS_PER_YEAR = 12`.
- **Implements:** F§2 (valid ranges, precision, technical cap).
- **Depends on:** nothing.

### 3.3 `validation` (pure)
> Checks the raw form text against the spec rules and returns either clean numbers or an error message per field.

- **Responsibility:** turn untrusted strings into a typed `LoanInput`, or report errors per field. Checks, in order per field: required → numeric → range → precision. Enforces the cross-field rule `down < price`. Empty optional fields become `0`. Never clamps or corrects.
- **Interface:** `validate(raw: RawInput): ValidationResult`
- **Implements:**
  - F§2 - required/optional, ranges, ≤ 2 dp for money and rate, integer term, `.` as the only decimal separator, `0 ≤ down < price`.
  - F§6 - invalid cases list (empty, non-numeric, negative, out of range, too many decimals, non-integer term, down ≥ price); nothing silently corrected.
- **Depends on:** `types`, `constants`.

### 3.4 `calculation` (pure)
> Computes the monthly payment, totals and full amortization schedule from valid inputs, without any rounding.

- **Responsibility:** all financial math at full precision, no rounding. Computes principal, monthly rate, annuity payment (explicit `r = 0` branch), monthly tax/insurance, all-in total, totals, and the amortization schedule with the final-payment adjustment so `balance_n = 0`.
- **Interface:** `calculate(input: LoanInput): MortgageResult`
- **Implements:**
  - F§2 - `P = price − down payment`.
  - F§3 - annuity formula (`r > 0` and `r = 0`), `T`, `I`, all-in total, total P&I and total interest (loan only, excluding tax/insurance), per-month schedule recurrences.
  - F§4 - full-precision internals; schedule closes at exactly 0.00.
  - F§5 items 1-3 (data side) - summary values and `n` schedule rows.
- **Depends on:** `types`, `constants` (months per year).

### 3.5 `formatting` (pure)
> Rounds numbers half-up to 2 decimals and turns them into EUR display strings.

- **Responsibility:** the only place where rounding happens; converts numbers to display strings.
- **Interface:** `formatEur(value: number): string` (2 dp, half-up, EUR); optionally `roundHalfUp2(value: number): number` as the internal helper, exported for tests.
- **Implements:** F§4 - display with 2 decimals, half-up; rounding from unrounded values (hence the documented 0.01 discrepancy in the displayed all-in total). F§2 - EUR fixed, no locale/currency switching.
- **Depends on:** nothing.

### 3.6 `ui/form`
> Reads what the user typed, shows inline errors next to the invalid fields, and signals when Calculate is clicked.

- **Responsibility:** read the six fields from the DOM as strings, show an inline error next to each offending field, clear stale errors, expose the Calculate action.
- **Interface:**
  - `collect(): RawInput`
  - `showErrors(errors: FieldErrors): void`
  - `clearErrors(): void`
  - `onCalculate(handler: () => void): void`
- **Implements:**
  - F§2 - six labelled input fields; plain-language labels (F§1).
  - F§6 - Calculate button (no live recalculation), inline error on the offending field.
- **Depends on:** `types`.

### 3.7 `ui/results`
> Displays the monthly payment summary and the scrollable amortization table, or nothing when the input is invalid.

- **Responsibility:** render the summary block and the scrollable amortization table; clear everything when input is invalid.
- **Interface:**
  - `render(result: MortgageResult): void`
  - `clear(): void`
- **Implements:**
  - F§5 - monthly P&I, tax, insurance, all-in total; total paid and total interest; full table (month, payment, interest, principal, balance); scrollable, no export.
  - F§4 - all displayed values pass through `formatEur`.
  - F§6 - no results shown until every field is valid.
- **Depends on:** `types`, `formatting`.

### 3.8 `main`
> Connects the modules on each Calculate click: read the form, validate, calculate, then show errors or results.

- **Responsibility:** composition root; the only module that knows the flow. On Calculate: clear old errors/results → `collect` → `validate` → on error `showErrors`, on success `calculate` → `render`.
- **Interface:** none exported; runs on page load.
- **Implements:** F§6 - Calculate-triggered flow, results only after all fields are valid; F§7 - nothing beyond V1 scope is wired in.
- **Depends on:** all modules above.

### 3.9 Requirements coverage

| Spec section | Covered by |
|---|---|
| F§1 Purpose, plain labels | `ui/form`, `ui/results` |
| F§2 Inputs | `types`, `constants`, `validation`, `ui/form` |
| F§3 Calculation rules | `calculation` |
| F§4 Rounding | `calculation` (no rounding), `formatting` (only rounding) |
| F§5 Outputs | `calculation` (data), `ui/results` (display) |
| F§6 Interaction / invalid input | `validation`, `ui/form`, `ui/results`, `main` |
| F§7 Out of scope | not built; see §9 |

## 4. Data contracts

```ts
// What the user typed (strings, untrusted)
interface RawInput {
  price: string; downPayment: string; annualRate: string; termYears: string;
  annualTax: string;        // "" => 0
  annualInsurance: string;  // "" => 0
}

// Validated, typed
interface LoanInput {
  price: number; downPayment: number; annualRatePct: number; termYears: number;
  annualTax: number; annualInsurance: number;
}

type FieldName = keyof RawInput;
type FieldErrors = Partial<Record<FieldName, string>>;   // empty => valid

type ValidationResult =
  | { ok: true;  value: LoanInput }
  | { ok: false; errors: FieldErrors };

interface ScheduleRow { month: number; payment: number; interest: number; principal: number; balance: number; }

interface Summary {
  principal: number;
  monthlyPI: number; monthlyTax: number; monthlyInsurance: number; monthlyTotal: number;
  totalPaid: number;       // M * n (P&I only)
  totalInterest: number;   // M * n - P
}

interface MortgageResult { summary: Summary; schedule: ScheduleRow[]; }  // schedule.length === n
```

Signatures:

```ts
validate(raw: RawInput): ValidationResult
calculate(input: LoanInput): MortgageResult
formatEur(value: number): string
```

All numeric values in `MortgageResult` are **unrounded**; `ui/results` calls `formatEur` at render time.

## 5. Data flow

```
[Calculate click]
      |
 ui/form.collect() ──RawInput──▶ validation.validate()
                                     |
                       ┌─── ok:false ┴─ ok:true ───┐
                       ▼                            ▼
          ui/form.showErrors(errors)      calculation.calculate(LoanInput)
          ui/results.clear()                         |
                                              MortgageResult
                                                     ▼
                                     ui/form.clearErrors()
                                     ui/results.render(result)  ──uses──▶ formatting.formatEur
```

`main.ts` owns this sequence. On every Calculate: previous errors and results are cleared first, so stale output never coexists with new errors (spec §6: no results until all fields valid).

## 6. Key design decisions

| Decision | Rationale | Spec ref |
|---|---|---|
| Validation lives separately from calculation; `calculate` assumes a valid `LoanInput` | Keeps formulas free of defensive branches; invalid state is unrepresentable past the validation boundary | §6 |
| Inputs validated as **strings** | Needed to detect `>2` decimals, non-numeric, empty, `1e3`-style or `,` separators, which are lost after `Number()` | §2, §6 |
| Decimal-place check done textually (regex on the string), range checks done numerically | Avoids float artifacts such as `0.1 + 0.2` when counting decimals | §2 |
| `r = 0` handled as an explicit branch in `calculation` | Formula divides by zero otherwise | §3 |
| Final payment = `balance_{n-1} + interest_n`; final `balance` set to exactly `0` | Guarantees the schedule closes at 0.00 without float residue | §3, §4 |
| Rounding only in `formatting` (half-up, on the unrounded value) | Matches spec; the displayed all-in total may differ by 0.01 from the sum of displayed parts (documented assumption) | §4 |
| Half-up implemented explicitly (e.g. `Math.round` on `x * 100` with an epsilon-safe approach), not via `toFixed` | `toFixed`/banker-style behaviours differ across engines and give surprising results on binary-inexact halves; behaviour must be deterministic and testable | §4 |
| Constants centralised | Spec limits change in one place; validation and tests reference the same values | §2 |
| Schedule rendered as a plain scrollable table, up to 480 rows | Small enough that no virtualisation is needed; export/charts are out of scope | §5, §7 |
| `main.ts` is the only composition point | Core modules stay reusable (e.g. a future CLI or test harness can call `validate` + `calculate` directly) | - |

## 7. Error handling

- `validation` never throws on bad user input; it returns `FieldErrors`.
- Each field gets at most one displayed message (the first failing rule in order: required → numeric → range → precision), keyed by `FieldName`. Cross-field error `down >= price` is attached to `downPayment`.
- `calculation` throws only on programmer error (precondition violation), which `main` does not catch; this is a bug signal, not a user-facing path.
- Invalid input leaves the results area empty. No clamping, no defaults other than empty optional fields → `0`.

## 8. Testability

- `validation`, `calculation`, `formatting` are unit-testable with no DOM.
- Invariants checkable on `calculate` output (feed into stage 03):
  - `schedule.length === termYears * 12`
  - `schedule[n-1].balance === 0`
  - `Σ principal_k ≈ P` and `Σ interest_k ≈ totalInterest`
  - `monthlyTotal === monthlyPI + monthlyTax + monthlyInsurance` (unrounded)
  - `r = 0` ⇒ every `interest_k === 0`, `payment = P / n`
- `ui` modules are exercised through a small number of DOM-level checks (error placement, no results on invalid input).

## 9. Extension points (not built in V1)

Kept possible by the module split, deliberately not implemented (spec §7):

- Extra payments / variable rates: extend `calculate` or add a sibling schedule generator; `types.ScheduleRow` is stable.
- Export: new `ui/export.ts` consuming `MortgageResult`.
- i18n / currency: confined to `formatting` and UI labels.

## 10. Open questions

1. Confirm the stack assumption (browser TS/JS, no dependencies). If Python/R or a framework is preferred, the module boundaries stay the same.
2. Test runner for stage 03 (none assumed; adding one needs approval to install per project rules).
