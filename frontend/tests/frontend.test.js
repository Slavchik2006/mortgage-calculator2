import test from 'node:test';
import assert from 'node:assert/strict';

globalThis.crypto ??= (await import('node:crypto')).webcrypto;
const { formatEur } = await import('../src/formatting.js');
const api = await import('../src/api.js');

test('formatEur: half-up on decimal strings', () => {
  assert.equal(formatEur('1216.0414'), '€1,216.04');
  assert.equal(formatEur('0.005'), '€0.01');
  assert.equal(formatEur('0.0049999'), '€0.00');
  assert.equal(formatEur('1000000000000'), '€1,000,000,000,000.00');
  assert.equal(formatEur('0'), '€0.00');
  assert.equal(formatEur('-5.5'), '-€5.50');
  assert.equal(formatEur('-0.001'), '€0.00');
  assert.equal(formatEur(1234.5), '€1,234.50');
});

test('formatEur: rejects non-plain input', () => {
  assert.throws(() => formatEur('1e3'), RangeError);
  assert.throws(() => formatEur('abc'), RangeError);
});

function stubFetch(handler) {
  const calls = [];
  globalThis.fetch = async (url, init) => {
    calls.push({ url, init });
    return handler(url, init);
  };
  return calls;
}
const json = (status, body) => new Response(JSON.stringify(body), { status, headers: { 'content-type': 'application/json' } });

test('calculate: success, no session header', async () => {
  const calls = stubFetch(() => json(200, { summary: {}, schedule: [] }));
  const res = await api.calculate({ price: '1' });
  assert.equal(res.ok, true);
  assert.equal(calls[0].url, '/api/v1/calculate');
  assert.equal(calls[0].init.headers['X-Session-Id'], undefined);
  assert.deepEqual(JSON.parse(calls[0].init.body), { price: '1' });
});

test('calculate: 422 maps to field errors', async () => {
  stubFetch(() => json(422, { errors: { annualRate: 'bad' } }));
  const res = await api.calculate({});
  assert.deepEqual(res, { ok: false, status: 422, errors: { annualRate: 'bad' }, error: undefined });
});

test('calculate: network failure and 5xx are networkError, not field errors', async () => {
  stubFetch(() => { throw new TypeError('offline'); });
  assert.deepEqual(await api.calculate({}), { ok: false, networkError: true });
  stubFetch(() => new Response('<html>bad gateway</html>', { status: 502 }));
  assert.deepEqual(await api.calculate({}), { ok: false, networkError: true });
});

test('scenarios: send a stable UUID session header; delete handles 204', async () => {
  const store = new Map();
  globalThis.localStorage = { getItem: (k) => store.get(k) ?? null, setItem: (k, v) => store.set(k, v) };
  const calls = stubFetch((url, init) => (init.method === 'DELETE' ? new Response(null, { status: 204 }) : json(200, [])));
  await api.listScenarios();
  const del = await api.deleteScenario('abc');
  assert.deepEqual(del, { ok: true, status: 204, data: null });
  const [a, b] = calls.map((c) => c.init.headers['X-Session-Id']);
  assert.match(a, /^[0-9a-f-]{36}$/);
  assert.equal(a, b);
  assert.equal(store.get('mortgage-session-id'), a);
});

test('session id falls back to memory when localStorage throws', async () => {
  globalThis.localStorage = { getItem() { throw new Error('blocked'); }, setItem() { throw new Error('blocked'); } };
  const calls = stubFetch(() => json(200, []));
  await api.listScenarios();
  await api.listScenarios();
  assert.equal(calls[0].init.headers['X-Session-Id'], calls[1].init.headers['X-Session-Id']);
});
