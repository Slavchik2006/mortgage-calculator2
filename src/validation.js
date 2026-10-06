import { MAX_PRICE, MAX_TAX_INSURANCE, RATE_MIN, RATE_MAX, TERM_MIN, TERM_MAX, MAX_DECIMALS } from './constants.js';

export const MESSAGES = Object.freeze({
  REQUIRED: 'This field is required.',
  NUMERIC: 'Enter a number using digits and . only.',
  RANGE_PRICE: 'Price must be more than 0 and at most 1,000,000,000,000.',
  RANGE_DOWN: 'Down payment must be 0 or more and less than the home price.',
  RANGE_RATE: 'Rate must be between 0 and 25.',
  RANGE_TERM: 'Term must be between 1 and 40 years.',
  RANGE_TAXINS: 'Must be between 0 and 1,000,000,000,000.',
  DEC2: 'Use at most 2 decimal places.',
  INT_TERM: 'Enter a whole number of years.',
});

const NUMERIC = /^-?[0-9]+(\.[0-9]+)?$/;
const trim = (s) => s.replace(/^[ \t\n\r\f\v]+|[ \t\n\r\f\v]+$/g, '');

/**
 * Rule order per field: required -> numeric -> range -> precision (A2).
 * @returns {{value: number} | {error: string}}
 */
function parseField(raw, { optional, inRange, rangeMsg, integer }) {
  const s = trim(String(raw ?? ''));
  if (s === '') return optional ? { value: 0 } : { error: MESSAGES.REQUIRED };
  if (!NUMERIC.test(s)) return { error: MESSAGES.NUMERIC };
  const n = Number(s);
  if (!inRange(n)) return { error: rangeMsg };
  const dot = s.indexOf('.');
  if (dot !== -1) {
    if (integer) return { error: MESSAGES.INT_TERM };
    if (s.length - dot - 1 > MAX_DECIMALS) return { error: MESSAGES.DEC2 };
  }
  return { value: n === 0 ? 0 : n }; // -0 -> +0
}

const SPECS = {
  price: { inRange: (n) => n > 0 && n <= MAX_PRICE, rangeMsg: MESSAGES.RANGE_PRICE },
  downPayment: { inRange: (n) => n >= 0 && n <= MAX_PRICE, rangeMsg: MESSAGES.RANGE_DOWN },
  annualRate: { inRange: (n) => n >= RATE_MIN && n <= RATE_MAX, rangeMsg: MESSAGES.RANGE_RATE },
  termYears: { inRange: (n) => n >= TERM_MIN && n <= TERM_MAX, rangeMsg: MESSAGES.RANGE_TERM, integer: true },
  annualTax: { optional: true, inRange: (n) => n >= 0 && n <= MAX_TAX_INSURANCE, rangeMsg: MESSAGES.RANGE_TAXINS },
  annualInsurance: { optional: true, inRange: (n) => n >= 0 && n <= MAX_TAX_INSURANCE, rangeMsg: MESSAGES.RANGE_TAXINS },
};

/**
 * @param {import('./types.js').RawInput} raw
 * @returns {import('./types.js').ValidationResult}
 */
export function validate(raw) {
  const values = {};
  const errors = {};
  for (const [field, spec] of Object.entries(SPECS)) {
    const r = parseField(raw?.[field], spec);
    if ('error' in r) errors[field] = r.error;
    else values[field] = r.value;
  }
  if (!('price' in errors) && !('downPayment' in errors) && values.downPayment >= values.price) {
    errors.downPayment = MESSAGES.RANGE_DOWN;
  }
  if (Object.keys(errors).length > 0) return { ok: false, errors };
  return {
    ok: true,
    value: {
      price: values.price,
      downPayment: values.downPayment,
      annualRatePct: values.annualRate,
      termYears: values.termYears,
      annualTax: values.annualTax,
      annualInsurance: values.annualInsurance,
    },
  };
}
