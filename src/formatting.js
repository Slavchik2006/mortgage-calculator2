// The only module that rounds. Half-up on the shortest decimal representation (A6).

const SMALL = 1e-6; // below this String() switches to exponent form; always rounds to 0.00
const MAX_ABS = 1e15;

/** @param {number} value @returns {bigint} signed cents, half-up on |value| */
function toCents(value) {
  if (!Number.isFinite(value) || Math.abs(value) >= MAX_ABS) {
    throw new RangeError(`Cannot format ${value}`);
  }
  const abs = Math.abs(value);
  if (abs < SMALL) return 0n;
  const [int, frac = ''] = String(abs).split('.');
  const f = (frac + '000').slice(0, 3);
  let cents = BigInt(int + f.slice(0, 2));
  if (f[2] >= '5') cents += 1n;
  return value < 0 ? -cents : cents;
}

/** @param {number} value @returns {number} value rounded half-up to 2 dp (never -0) */
export function roundHalfUp2(value) {
  return Number(toCents(value)) / 100 || 0;
}

/** @param {number} value @returns {string} e.g. "€1,234.56", "-€5.50" */
export function formatEur(value) {
  const cents = toCents(value);
  const neg = cents < 0n;
  const abs = neg ? -cents : cents;
  const int = (abs / 100n).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
  const frac = (abs % 100n).toString().padStart(2, '0');
  return `${neg ? '-' : ''}€${int}.${frac}`;
}
