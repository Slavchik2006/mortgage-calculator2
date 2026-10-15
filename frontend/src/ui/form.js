export const FIELD_NAMES = ['price', 'downPayment', 'annualRate', 'termYears', 'annualTax', 'annualInsurance'];

const input = (name) => document.getElementById(name);
const errorEl = (name) => document.getElementById(`${name}-error`);

/** @returns {Record<string,string>} verbatim field strings */
export function collect() {
  return Object.fromEntries(FIELD_NAMES.map((name) => [name, input(name).value]));
}

/** @param {Record<string,string|null>} values */
export function setValues(values) {
  for (const name of FIELD_NAMES) input(name).value = values?.[name] ?? '';
}

/** @param {Record<string,string>} errors */
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

/** @param {boolean} busy */
export function setBusy(busy) {
  document.getElementById('calculate').disabled = busy;
}

/** @param {() => void} handler */
export function onCalculate(handler) {
  document.getElementById('mortgage-form').addEventListener('submit', (event) => {
    event.preventDefault();
    handler();
  });
}

/** Shows a service-level message above the form; null hides it. */
export function showBanner(message) {
  const el = document.getElementById('banner');
  el.textContent = message ?? '';
  el.hidden = !message;
}
