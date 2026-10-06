import { FIELD_NAMES } from '../types.js';

const input = (name) => document.getElementById(name);
const errorEl = (name) => document.getElementById(`${name}-error`);

/** @returns {import('../types.js').RawInput} verbatim field strings */
export function collect() {
  return Object.fromEntries(FIELD_NAMES.map((name) => [name, input(name).value]));
}

/** @param {import('../types.js').FieldErrors} errors */
export function showErrors(errors) {
  for (const name of FIELD_NAMES) {
    const message = errors[name];
    errorEl(name).textContent = message ?? '';
    if (message) {
      input(name).setAttribute('aria-invalid', 'true');
      input(name).setAttribute('aria-describedby', `${name}-error`);
    } else {
      input(name).removeAttribute('aria-invalid');
      input(name).removeAttribute('aria-describedby');
    }
  }
}

export function clearErrors() {
  showErrors({});
}

/** @param {() => void} handler */
export function onCalculate(handler) {
  document.getElementById('mortgage-form').addEventListener('submit', (event) => {
    event.preventDefault();
    handler();
  });
}
