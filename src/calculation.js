import { MONTHS_PER_YEAR, MAX_PRICE, RATE_MIN, RATE_MAX, TERM_MIN, TERM_MAX } from './constants.js';

// Money is computed in BigInt fixed point (cents x 10^40), so the schedule is exact to ~1e-30
// even at the 1e12 cap (review findings 3, 5). Results are converted to unrounded doubles.
const SCALE = 10n ** 40n;

// scaled cents -> euros; parsing the decimal string is correctly rounded (1000 stays 1000)
const toEur = (x) => Number(`${x}e-42`);
const cents = (x) => BigInt(Math.round(x * 100));

function check(cond, msg) {
  if (!cond) throw new Error(`calculate: ${msg}`);
}

/**
 * @param {import('./types.js').LoanInput} input
 * @returns {import('./types.js').MortgageResult}
 */
export function calculate(input) {
  const { price, downPayment, annualRatePct, termYears, annualTax, annualInsurance } = input;
  check(Number.isFinite(price) && price > 0 && price <= MAX_PRICE, 'invalid price');
  check(Number.isFinite(downPayment) && downPayment >= 0 && downPayment < price, 'invalid down payment');
  check(Number.isFinite(annualRatePct) && annualRatePct >= RATE_MIN && annualRatePct <= RATE_MAX, 'invalid rate');
  check(Number.isInteger(termYears) && termYears >= TERM_MIN && termYears <= TERM_MAX, 'invalid term');
  check(Number.isFinite(annualTax) && annualTax >= 0, 'invalid tax');
  check(Number.isFinite(annualInsurance) && annualInsurance >= 0, 'invalid insurance');

  const n = termYears * MONTHS_PER_YEAR;
  const P = cents(price) - cents(downPayment); // integer cents, exact
  const principal = Number(P) / 100;
  const rateHundredths = BigInt(Math.round(annualRatePct * 100));
  const r = (rateHundredths * SCALE) / 120000n; // annual% / 100 / 12, scaled

  let M; // monthly P&I, scaled cents
  if (rateHundredths === 0n) {
    M = (P * SCALE) / BigInt(n);
  } else {
    let growth = SCALE; // (1 + r)^n
    let base = SCALE + r;
    for (let e = n; e > 0; e >>= 1) {
      if (e & 1) growth = (growth * base) / SCALE;
      base = (base * base) / SCALE;
    }
    const denom = SCALE - (SCALE * SCALE) / growth; // 1 - (1+r)^-n
    M = (P * SCALE * r) / denom;
  }

  const schedule = [];
  let balance = P * SCALE;
  for (let k = 1; k <= n; k++) {
    const interest = (balance * r) / SCALE;
    let payment = M;
    let principalK = M - interest;
    let next = balance - principalK;
    if (k === n) {
      payment = balance + interest; // final payment closes the loan exactly
      principalK = balance;
      next = 0n;
    }
    schedule.push({
      month: k,
      payment: toEur(payment),
      interest: toEur(interest),
      principal: toEur(principalK),
      balance: toEur(next),
    });
    balance = next;
  }

  const monthlyPI = toEur(M);
  const monthlyTax = annualTax / MONTHS_PER_YEAR;
  const monthlyInsurance = annualInsurance / MONTHS_PER_YEAR;
  const totalPaid = monthlyPI * n;
  return {
    summary: {
      principal,
      monthlyPI,
      monthlyTax,
      monthlyInsurance,
      monthlyTotal: monthlyPI + monthlyTax + monthlyInsurance,
      totalPaid,
      totalInterest: totalPaid - principal,
    },
    schedule,
  };
}
