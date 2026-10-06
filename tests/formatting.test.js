import test from 'node:test';
import assert from 'node:assert/strict';
import { formatEur, roundHalfUp2 } from '../src/formatting.js';

const eq = (v, s) => assert.equal(formatEur(v), s);

test('FMT-01 two decimals and symbol', () => eq(1199.10105, '€1,199.10'));
test('FMT-02 round down below half', () => eq(1.004, '€1.00'));
test('FMT-03 round up above half', () => eq(1.006, '€1.01'));
test('FMT-04 half-up on exact binary halves', () => { eq(0.125, '€0.13'); eq(0.375, '€0.38'); });
test('FMT-05 half-up on binary-inexact halves', () => { eq(1.005, '€1.01'); eq(2.675, '€2.68'); });
test('FMT-06 half-up on large value', () => eq(123456789.125, '€123,456,789.13'));
test('FMT-07 zero', () => eq(0, '€0.00'));
test('FMT-08 float residue near zero has no sign', () => { eq(1e-12, '€0.00'); eq(-1e-12, '€0.00'); });
test('FMT-09 negative zero', () => eq(-0, '€0.00'));
test('FMT-10 largest realistic magnitude', () => eq(1140530439166.903, '€1,140,530,439,166.90'));
test('FMT-11 value at or above 1e15 rejected', () => assert.throws(() => formatEur(1e15), RangeError));
test('FMT-12 output independent of runtime locale', () => {
  // formatEur does not use Intl or toLocaleString, so the runtime locale cannot affect it.
  const original = Number.prototype.toLocaleString;
  Number.prototype.toLocaleString = () => { throw new Error('locale API used'); };
  try { eq(1234.56, '€1,234.56'); } finally { Number.prototype.toLocaleString = original; }
});
test('FMT-13 thousands grouping', () => eq(1234567.5, '€1,234,567.50'));
test('FMT-14 NaN and Infinity rejected', () => {
  assert.throws(() => formatEur(NaN), RangeError);
  assert.throws(() => formatEur(Infinity), RangeError);
});
test('FMT-15 rounded parts, total rounds down', () => {
  eq(1000.004, '€1,000.00'); eq(0.004, '€0.00'); eq(0.004, '€0.00'); eq(1000.012, '€1,000.01');
});
test('FMT-16 rounded parts, total rounds up', () => {
  eq(1000.005, '€1,000.01'); eq(0.005, '€0.01'); eq(0.005, '€0.01'); eq(1000.015, '€1,000.02');
});
test('FMT-17 negative non-zero value', () => eq(-5.5, '-€5.50'));
test('FMT-18 roundHalfUp2 idempotent', () => {
  for (const v of [1.005, 2.675, 0.125, 1199.10105, 1e-12]) {
    const once = roundHalfUp2(v);
    assert.equal(roundHalfUp2(once), once);
  }
});
