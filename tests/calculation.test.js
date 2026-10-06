import test from 'node:test';
import assert from 'node:assert/strict';
import { calculate } from '../src/calculation.js';

// Reference values (docs/v1/reference_values.py) are quoted to <= 10 dp, so the comparison
// tolerance is 1e-8 abs + 1e-12 rel instead of the unreachable TOL1 of 03-test-scenarios A9
// (review findings 1, 4). Column sums use 1e-12 x P + 1e-6.
const close = (actual, expected, abs = 1e-8) =>
  assert.ok(Math.abs(actual - expected) <= abs + 1e-12 * Math.abs(expected), `${actual} != ${expected}`);
const sumTol = (x) => 1e-12 * x + 1e-6;

const loan = (price, downPayment, annualRatePct, termYears, annualTax = 0, annualInsurance = 0) =>
  ({ price, downPayment, annualRatePct, termYears, annualTax, annualInsurance });
const V1 = () => loan(250000, 50000, 6, 30);
const V3 = () => loan(100000, 0, 12, 1);
const V4 = () => loan(1, 0, 25, 40);
const V5 = () => loan(300000, 0, 3.5, 25);
const V6 = () => loan(100000, 0, 0.01, 40);
const sum = (rows, key) => rows.reduce((a, r) => a + r[key], 0);

test('CAL-01 standard loan, no tax/insurance', () => {
  const { summary: s } = calculate(V1());
  assert.equal(s.principal, 200000);
  close(s.monthlyPI, 1199.1010503055);
  assert.equal(s.monthlyTax, 0);
  assert.equal(s.monthlyInsurance, 0);
  close(s.monthlyTotal, 1199.1010503055);
  close(s.totalPaid, 431676.37810998);
  close(s.totalInterest, 231676.37810998);
});
test('CAL-02 standard loan with tax and insurance', () => {
  const { summary: s } = calculate(loan(250000, 50000, 6, 30, 2400, 1200));
  close(s.monthlyTax, 200);
  close(s.monthlyInsurance, 100);
  close(s.monthlyTotal, 1499.1010503055);
});
test('CAL-03 principal = price - down', () => assert.equal(calculate(loan(300000, 75000, 5, 20)).summary.principal, 225000));
test('CAL-04 second reference loan', () => {
  const { summary: s } = calculate(V5());
  close(s.monthlyPI, 1501.8707107785);
  close(s.totalInterest, 150561.21323354);
});
test('CAL-05 one-year loan at 12 %', () => {
  const r = calculate(V3());
  close(r.summary.monthlyPI, 8884.8788678342);
  close(r.summary.totalInterest, 6618.54641401);
  assert.equal(r.schedule.length, 12);
});
test('CAL-06 zero rate branch', () => {
  const r = calculate(loan(120000, 0, 0, 10));
  assert.equal(r.summary.monthlyPI, 1000);
  assert.ok(r.schedule.every((row) => row.interest === 0 && row.payment === 1000));
  assert.ok(Math.abs(r.summary.totalInterest) <= 1e-9);
});
test('CAL-07 zero rate, non-terminating payment', () => {
  const r = calculate(loan(100000, 0, 0, 3));
  close(r.summary.monthlyPI, 2777.7777777778);
  assert.equal(r.schedule[35].balance, 0);
});
test('CAL-08 very small positive rate', () => {
  const r = calculate(V6());
  close(r.summary.monthlyPI, 208.7511458309);
  close(r.summary.totalInterest, 200.54999883);
  assert.ok(r.schedule.every((row) => Object.values(row).every(Number.isFinite)));
});
test('CAL-09 minimum principal, max rate, max term', () => {
  const r = calculate(V4());
  close(r.summary.monthlyPI, 0.0208343816);
  assert.equal(r.schedule.length, 480);
  close(r.schedule[0].interest, 0.0208333333);
  assert.equal(r.schedule[479].balance, 0);
});
test('CAL-10 maximum principal, max rate, max term', () => {
  const r = calculate(loan(1e12, 0, 25, 40));
  close(r.summary.monthlyPI, 20834381562.2599, 1e-3);
  assert.equal(r.schedule.length, 480);
  close(r.schedule[479].interest, 425191460.4543, 1e-3);
  assert.equal(r.schedule[479].balance, 0);
});
test('CAL-11 large principal, short term, high rate', () => {
  const r = calculate(loan(999999999999.99, 0, 25, 1));
  close(r.summary.monthlyPI, 95044203263.9083, 1e-3); // decimal reference; exact arithmetic matches it
  assert.equal(r.schedule.length, 12);
  assert.equal(r.schedule[11].balance, 0);
  assert.ok(Math.abs(sum(r.schedule, 'principal') - 999999999999.99) <= sumTol(1e12));
});
test('CAL-12 large principal, zero rate, max term', () => {
  const r = calculate(loan(1e12, 0, 0, 40));
  close(r.summary.monthlyPI, 2083333333.3333333);
  assert.ok(r.schedule.every((row) => row.interest === 0));
  assert.ok(Math.abs(r.summary.totalInterest) <= 1e-3);
});
test('CAL-13 tiny principal at 6 %', () => {
  const r = calculate(loan(0.01, 0, 6, 1));
  close(r.summary.monthlyPI, 0.0008606643);
  close(r.summary.totalPaid, 0.01032797);
  assert.equal(r.schedule.length, 12);
  assert.equal(r.schedule[11].balance, 0);
});
test('CAL-14 down payment 0 gives full price principal', () =>
  assert.equal(calculate(loan(100000, 0, 5, 20)).summary.principal, 100000));
test('CAL-15 tax only', () => {
  const { summary: s } = calculate(loan(250000, 50000, 6, 30, 1234.56, 0));
  close(s.monthlyTax, 102.88);
  assert.equal(s.monthlyInsurance, 0);
  close(s.monthlyTotal, 1301.9810503055);
});
test('CAL-16 insurance only', () => {
  const { summary: s } = calculate(loan(250000, 50000, 6, 30, 0, 600));
  close(s.monthlyInsurance, 50);
  close(s.monthlyTotal, 1249.1010503055);
});
test('CAL-17 tax/insurance excluded from loan totals', () => {
  const a = calculate(V1());
  const b = calculate(loan(250000, 50000, 6, 30, 2400, 1200));
  assert.equal(a.summary.totalPaid, b.summary.totalPaid);
  assert.equal(a.summary.totalInterest, b.summary.totalInterest);
  assert.deepEqual(a.schedule, b.schedule);
});
test('CAL-18 schedule length = 12 x term', () => {
  for (const [y, n] of [[1, 12], [10, 120], [30, 360], [40, 480]]) {
    assert.equal(calculate(loan(200000, 0, 5, y)).schedule.length, n);
  }
});
test('CAL-19 month numbering', () => {
  calculate(V1()).schedule.forEach((row, k) => assert.equal(row.month, k + 1));
});
test('CAL-20 first schedule row', () => {
  const row = calculate(V1()).schedule[0];
  close(row.payment, 1199.1010503055);
  close(row.interest, 1000);
  close(row.principal, 199.1010503055);
  close(row.balance, 199800.8989496945);
});
test('CAL-21 second schedule row', () => {
  const row = calculate(V1()).schedule[1];
  close(row.interest, 999.0044947485);
  close(row.principal, 200.096555557);
  close(row.balance, 199600.8023941375);
});
test('CAL-22 closing balance exactly zero', () => {
  for (const l of [V1(), V3(), V5(), V6()]) {
    const { schedule } = calculate(l);
    assert.equal(schedule[schedule.length - 1].balance, 0);
  }
});
test('CAL-23 final payment adjustment', () => {
  const { summary: s, schedule } = calculate(V1());
  const last = schedule[359];
  close(last.interest, 5.9656768672);
  close(last.principal, 1193.1353734383);
  assert.ok(Math.abs(last.payment - (schedule[358].balance + last.interest)) <= 1e-9);
  assert.ok(Math.abs(last.payment - s.monthlyPI) <= 1e-9 * s.monthlyPI);
});
test('CAL-24 principal column sums to P', () => {
  for (const [l, P] of [[V1(), 200000], [V5(), 300000], [V6(), 100000]]) {
    assert.ok(Math.abs(sum(calculate(l).schedule, 'principal') - P) <= sumTol(P));
  }
});
test('CAL-25 interest column sums to total interest', () => {
  for (const l of [V1(), V5(), V6()]) {
    const r = calculate(l);
    // totalInterest = M x n - P differs from the schedule's sum only by the final-payment adjustment
    assert.ok(Math.abs(sum(r.schedule, 'interest') - r.summary.totalInterest) <= sumTol(r.summary.principal + r.summary.totalInterest));
  }
});
test('CAL-26 row identities', () => {
  const { schedule } = calculate(V1());
  schedule.forEach((row, i) => {
    assert.ok(Math.abs(row.payment - (row.interest + row.principal)) <= 1e-6);
    const prev = i === 0 ? 200000 : schedule[i - 1].balance;
    assert.ok(Math.abs(row.balance - (prev - row.principal)) <= 1e-6);
  });
});
test('CAL-27 balance monotone', () => {
  for (const l of [V1(), V5()]) {
    const { schedule } = calculate(l);
    schedule.forEach((row, i) => {
      assert.ok(row.balance >= 0);
      if (i > 0) assert.ok(row.balance < schedule[i - 1].balance);
      if (i > 0 && i < schedule.length - 1) {
        assert.ok(row.interest < schedule[i - 1].interest);
        assert.ok(row.principal > schedule[i - 1].principal);
      }
    });
  }
});
test('CAL-28 unrounded monthly total identity', () => {
  const { summary: s } = calculate(loan(250000, 50000, 6, 30, 2400, 1200));
  assert.equal(s.monthlyTotal, s.monthlyPI + s.monthlyTax + s.monthlyInsurance);
});
test('CAL-29 total paid and interest definitions', () => {
  const { summary: s } = calculate(V1());
  assert.equal(s.totalPaid, s.monthlyPI * 360);
  assert.equal(s.totalInterest, s.monthlyPI * 360 - s.principal);
});
test('CAL-30 no rounding inside calculation', () => {
  const { monthlyPI } = calculate(V1()).summary;
  assert.notEqual(monthlyPI, 1199.1);
  close(monthlyPI, 1199.1010503055);
});
test('CAL-31 calculate is pure', () => {
  const input = Object.freeze(V1());
  const a = calculate(input);
  const b = calculate(input);
  assert.deepEqual(a, b);
  assert.deepEqual(input, V1());
});
test('CAL-32 precondition violations throw', () => {
  assert.throws(() => calculate(loan(250000, 50000, 6, 0)), Error);
  assert.throws(() => calculate(loan(100000, 100000, 6, 30)), Error);
  assert.throws(() => calculate(loan(250000, 50000, NaN, 30)), Error);
});
test('CAL-33 property test over random valid inputs', () => {
  let seed = 42; // mulberry32
  const rand = () => {
    seed = (seed + 0x6d2b79f5) | 0;
    let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
  for (let i = 0; i < 1000; i++) {
    const price = Math.max(1, Math.round(rand() ** 3 * 1e14)) / 100; // 0.01 .. 1e12
    const down = Math.floor(rand() * price * 100) / 100;
    const rate = rand() < 0.1 ? 0 : Math.round(rand() * 2500) / 100;
    const years = 1 + Math.floor(rand() * 40);
    const input = loan(price, down, rate, years);
    const { summary: s, schedule } = calculate(input);
    assert.equal(schedule.length, 12 * years, JSON.stringify(input));
    assert.equal(schedule[schedule.length - 1].balance, 0, JSON.stringify(input));
    assert.ok(Math.abs(sum(schedule, 'principal') - s.principal) <= sumTol(s.principal), JSON.stringify(input));
    assert.ok(Math.abs(sum(schedule, 'interest') - s.totalInterest) <= sumTol(s.principal + s.totalInterest), JSON.stringify(input));
    if (rate === 0) assert.ok(schedule.every((r) => r.interest === 0));
  }
});
