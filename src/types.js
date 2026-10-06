// Shared data contracts (no logic). See docs/v1/02-architecture.md section 4.

/**
 * @typedef {Object} RawInput
 * @property {string} price
 * @property {string} downPayment
 * @property {string} annualRate
 * @property {string} termYears
 * @property {string} annualTax        "" => 0
 * @property {string} annualInsurance  "" => 0
 */

/**
 * @typedef {Object} LoanInput
 * @property {number} price
 * @property {number} downPayment
 * @property {number} annualRatePct
 * @property {number} termYears
 * @property {number} annualTax
 * @property {number} annualInsurance
 */

/** @typedef {keyof RawInput} FieldName */
/** @typedef {Partial<Record<FieldName, string>>} FieldErrors */

/**
 * @typedef {{ok: true, value: LoanInput} | {ok: false, errors: FieldErrors}} ValidationResult
 */

/**
 * @typedef {Object} ScheduleRow
 * @property {number} month
 * @property {number} payment
 * @property {number} interest
 * @property {number} principal
 * @property {number} balance
 */

/**
 * @typedef {Object} Summary
 * @property {number} principal
 * @property {number} monthlyPI
 * @property {number} monthlyTax
 * @property {number} monthlyInsurance
 * @property {number} monthlyTotal
 * @property {number} totalPaid     M * n (P&I only)
 * @property {number} totalInterest M * n - P
 */

/** @typedef {{summary: Summary, schedule: ScheduleRow[]}} MortgageResult */

export const FIELD_NAMES = ['price', 'downPayment', 'annualRate', 'termYears', 'annualTax', 'annualInsurance'];
