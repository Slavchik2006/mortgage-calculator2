// The only module that rounds. Half-up on the decimal string returned by the API (A6).
// Input is a plain decimal string such as "1216.0414" or "-5.5"; numbers are accepted via String().

const PLAIN = /^(-?)([0-9]+)(?:\.([0-9]+))?$/;

/** @returns {bigint} signed cents, half-up on |value| */
function toCents(value) {
  const m = PLAIN.exec(String(value));
  if (!m) throw new RangeError(`Cannot format ${value}`);
  const [, sign, int, frac = ''] = m;
  const f = (frac + '000').slice(0, 3);
  let cents = BigInt(int + f.slice(0, 2));
  if (f[2] >= '5') cents += 1n;
  return sign && cents !== 0n ? -cents : cents;
}

/** @param {string|number} value @returns {string} e.g. "€1,234.56", "-€5.50" */
export function formatEur(value) {
  const cents = toCents(value);
  const neg = cents < 0n;
  const abs = neg ? -cents : cents;
  const int = (abs / 100n).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
  const frac = (abs % 100n).toString().padStart(2, '0');
  return `${neg ? '-' : ''}€${int}.${frac}`;
}
