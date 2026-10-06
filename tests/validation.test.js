import test from 'node:test';
import assert from 'node:assert/strict';
import { validate, MESSAGES as M } from '../src/validation.js';

const B = { price: '250000', downPayment: '50000', annualRate: '6', termYears: '30', annualTax: '', annualInsurance: '' };
const v = (o = {}) => validate({ ...B, ...o });
const ok = (res, expected) => {
  assert.equal(res.ok, true, JSON.stringify(res));
  if (expected) assert.deepEqual(res.value, expected);
};
const err = (res, expected) => {
  assert.equal(res.ok, false);
  assert.deepEqual(res.errors, expected);
  assert.equal('value' in res, false);
};
const nines = '9'.repeat(400);

const all = [];
const t = (name, fn) => { all.push(fn); test(name, fn); };

t('VAL-01 valid base, optionals empty', () =>
  ok(v(), { price: 250000, downPayment: 50000, annualRatePct: 6, termYears: 30, annualTax: 0, annualInsurance: 0 }));
t('VAL-02 valid, all six fields', () =>
  ok(v({ annualTax: '2400', annualInsurance: '1200' }),
    { price: 250000, downPayment: 50000, annualRatePct: 6, termYears: 30, annualTax: 2400, annualInsurance: 1200 }));
t('VAL-03 down payment 0 accepted', () => assert.equal(v({ downPayment: '0' }).value.downPayment, 0));
t('VAL-04 down = price - 0.01 accepted', () =>
  assert.equal(v({ price: '100000', downPayment: '99999.99' }).value.downPayment, 99999.99));
t('VAL-05 down = price rejected', () => err(v({ price: '100000', downPayment: '100000' }), { downPayment: M.RANGE_DOWN }));
t('VAL-06 down > price rejected', () => err(v({ price: '100000', downPayment: '150000' }), { downPayment: M.RANGE_DOWN }));
t('VAL-07 price at 1e12 cap accepted', () =>
  assert.equal(v({ price: '1000000000000', downPayment: '0' }).value.price, 1e12));
t('VAL-08 price just above cap rejected', () => err(v({ price: '1000000000000.01' }), { price: M.RANGE_PRICE }));
t('VAL-09 price 0 rejected', () => err(v({ price: '0' }), { price: M.RANGE_PRICE }));
t('VAL-10 price 0.01 accepted', () => assert.equal(v({ price: '0.01', downPayment: '0' }).value.price, 0.01));
t('VAL-11 price negative rejected', () => err(v({ price: '-1' }), { price: M.RANGE_PRICE }));
t('VAL-12 rate 0 accepted', () => assert.equal(v({ annualRate: '0' }).value.annualRatePct, 0));
t('VAL-13 rate 25 accepted', () => assert.equal(v({ annualRate: '25' }).value.annualRatePct, 25));
t('VAL-14 rate 25.01 rejected', () => err(v({ annualRate: '25.01' }), { annualRate: M.RANGE_RATE }));
t('VAL-15 rate -0.01 rejected', () => err(v({ annualRate: '-0.01' }), { annualRate: M.RANGE_RATE }));
t('VAL-16 rate with 2 dp accepted', () => assert.equal(v({ annualRate: '3.75' }).value.annualRatePct, 3.75));
t('VAL-17 rate with 3 dp rejected', () => err(v({ annualRate: '3.755' }), { annualRate: M.DEC2 }));
t('VAL-18 term 1 accepted', () => assert.equal(v({ termYears: '1' }).value.termYears, 1));
t('VAL-19 term 40 accepted', () => assert.equal(v({ termYears: '40' }).value.termYears, 40));
t('VAL-20 term 0 rejected', () => err(v({ termYears: '0' }), { termYears: M.RANGE_TERM }));
t('VAL-21 term 41 rejected', () => err(v({ termYears: '41' }), { termYears: M.RANGE_TERM }));
t('VAL-22 term 2.5 rejected', () => err(v({ termYears: '2.5' }), { termYears: M.INT_TERM }));
t('VAL-23 term written 30.0 rejected', () => err(v({ termYears: '30.0' }), { termYears: M.INT_TERM }));
t('VAL-24 term negative rejected', () => err(v({ termYears: '-5' }), { termYears: M.RANGE_TERM }));
t('VAL-25 price with 2 dp accepted', () => assert.equal(v({ price: '250000.99' }).value.price, 250000.99));
t('VAL-26 price with 3 dp rejected', () => err(v({ price: '250000.999' }), { price: M.DEC2 }));
t('VAL-27 price 250000.500 rejected (textual 3 dp)', () => err(v({ price: '250000.500' }), { price: M.DEC2 }));
t('VAL-28 down payment with 3 dp rejected', () => err(v({ downPayment: '100.001' }), { downPayment: M.DEC2 }));
t('VAL-29 tax with 3 dp rejected', () => err(v({ annualTax: '100.001' }), { annualTax: M.DEC2 }));
t('VAL-30 insurance with 3 dp rejected', () => err(v({ annualInsurance: '100.001' }), { annualInsurance: M.DEC2 }));
t('VAL-31 tax 0 accepted', () => assert.equal(v({ annualTax: '0' }).value.annualTax, 0));
t('VAL-32 tax negative rejected', () => err(v({ annualTax: '-1' }), { annualTax: M.RANGE_TAXINS }));
t('VAL-33 insurance negative rejected', () => err(v({ annualInsurance: '-0.01' }), { annualInsurance: M.RANGE_TAXINS }));
t('VAL-34 tax at 1e12 cap accepted', () => assert.equal(v({ annualTax: '1000000000000' }).value.annualTax, 1e12));
t('VAL-35 tax above cap rejected', () => err(v({ annualTax: '1000000000000.01' }), { annualTax: M.RANGE_TAXINS }));
t('VAL-36 insurance 400-digit string rejected', () => err(v({ annualInsurance: nines }), { annualInsurance: M.RANGE_TAXINS }));
t('VAL-37 price empty', () => err(v({ price: '' }), { price: M.REQUIRED }));
t('VAL-38 down payment empty', () => err(v({ downPayment: '' }), { downPayment: M.REQUIRED }));
t('VAL-39 rate empty', () => err(v({ annualRate: '' }), { annualRate: M.REQUIRED }));
t('VAL-40 term empty', () => err(v({ termYears: '' }), { termYears: M.REQUIRED }));
t('VAL-41 price whitespace-only = empty', () => err(v({ price: '   ' }), { price: M.REQUIRED }));
t('VAL-42 tax whitespace-only = empty optional', () => assert.equal(v({ annualTax: '  ' }).value.annualTax, 0));
t('VAL-43 surrounding spaces trimmed', () => assert.equal(v({ price: ' 250000 ' }).value.price, 250000));
t('VAL-44 price text rejected', () => err(v({ price: 'abc' }), { price: M.NUMERIC }));
t('VAL-45 optional tax text rejected', () => err(v({ annualTax: 'abc' }), { annualTax: M.NUMERIC }));
t('VAL-46 comma decimal separator rejected', () => err(v({ annualRate: '3,5' }), { annualRate: M.NUMERIC }));
t('VAL-47 thousands separators rejected', () => {
  err(v({ price: '250,000' }), { price: M.NUMERIC });
  err(v({ price: '250 000' }), { price: M.NUMERIC });
});
t('VAL-48 scientific notation rejected', () => err(v({ price: '1e5' }), { price: M.NUMERIC }));
t('VAL-49 Infinity and NaN strings rejected', () => {
  err(v({ price: 'Infinity' }), { price: M.NUMERIC });
  err(v({ price: 'NaN' }), { price: M.NUMERIC });
});
t('VAL-50 hex literal rejected', () => err(v({ price: '0x10' }), { price: M.NUMERIC }));
t('VAL-51 leading plus rejected', () => err(v({ price: '+1000' }), { price: M.NUMERIC }));
t('VAL-52 malformed decimal points rejected', () => {
  for (const p of ['.5', '5.', '.']) err(v({ price: p }), { price: M.NUMERIC });
});
t('VAL-53 leading zeros accepted', () => assert.equal(v({ price: '0001000', downPayment: '0' }).value.price, 1000));
t('VAL-54 negative zero normalised', () => {
  const res = v({ downPayment: '-0' });
  ok(res);
  assert.ok(Object.is(res.value.downPayment, 0));
});
t('VAL-55 non-ASCII digits and minus rejected', () => {
  err(v({ price: '１２３' }), { price: M.NUMERIC });
  err(v({ annualRate: '−5' }), { annualRate: M.NUMERIC });
});
t('VAL-56 400-digit price rejected', () => err(v({ price: nines }), { price: M.RANGE_PRICE }));
t('VAL-57 several fields invalid at once', () =>
  err(v({ price: '', annualRate: '30', termYears: '0.5' }),
    { price: M.REQUIRED, annualRate: M.RANGE_RATE, termYears: M.RANGE_TERM }));
t('VAL-58 rule order: range before precision', () => err(v({ annualRate: '-1.234' }), { annualRate: M.RANGE_RATE }));
t('VAL-59 cross-field error alongside other error', () =>
  err(v({ price: '100', downPayment: '100', annualRate: 'abc' }), { downPayment: M.RANGE_DOWN, annualRate: M.NUMERIC }));
t('VAL-60 cross-field skipped when price invalid', () =>
  err(v({ price: 'abc', downPayment: '100' }), { price: M.NUMERIC }));
t('VAL-61 cross-field skipped when down invalid', () =>
  err(v({ price: '100000', downPayment: 'abc' }), { downPayment: M.NUMERIC }));
t('VAL-62 no clamping on invalid value', () => err(v({ annualRate: '25.5' }), { annualRate: M.RANGE_RATE }));
t('VAL-63 all required empty', () =>
  err(validate({ price: '', downPayment: '', annualRate: '', termYears: '', annualTax: '', annualInsurance: '' }),
    { price: M.REQUIRED, downPayment: M.REQUIRED, annualRate: M.REQUIRED, termYears: M.REQUIRED }));
test('VAL-64 validate never throws', () => {
  for (const fn of all) assert.doesNotThrow(fn); // replays VAL-01..63 inputs
  for (const raw of [{}, undefined, { price: null }, { price: nines, downPayment: nines }]) {
    assert.equal(typeof validate(raw).ok, 'boolean');
  }
});
