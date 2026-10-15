// Thin wrapper over the backend API. Validation is server-side only.
import { getSessionId } from './session.js';

const BASE = '/api/v1';

/**
 * @returns {Promise<{ok: true, status: number, data: any} | {ok: false, status: number, errors?: object, error?: string} | {ok: false, networkError: true}>}
 */
async function request(method, path, body, { session = false } = {}) {
  const headers = {};
  if (body !== undefined) headers['Content-Type'] = 'application/json';
  if (session) headers['X-Session-Id'] = getSessionId();
  let res;
  try {
    res = await fetch(BASE + path, { method, headers, body: body === undefined ? undefined : JSON.stringify(body) });
  } catch {
    return { ok: false, networkError: true };
  }
  if (res.status === 204) return { ok: true, status: 204, data: null };
  let data = null;
  try {
    data = await res.json();
  } catch {
    // non-JSON body (e.g. proxy error page)
  }
  if (res.ok) return { ok: true, status: res.status, data };
  if (res.status >= 500) return { ok: false, networkError: true };
  return { ok: false, status: res.status, errors: data?.errors, error: data?.error };
}

export const calculate = (raw) => request('POST', '/calculate', raw);
export const listScenarios = () => request('GET', '/scenarios', undefined, { session: true });
export const saveScenario = (name, inputs) => request('POST', '/scenarios', { name, inputs }, { session: true });
export const deleteScenario = (id) => request('DELETE', `/scenarios/${id}`, undefined, { session: true });
