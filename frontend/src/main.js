import * as api from './api.js';
import * as form from './ui/form.js';
import * as results from './ui/results.js';
import * as scenarios from './ui/scenarios.js';

const UNAVAILABLE = 'Calculation service unavailable. Try again later.';
let requestSeq = 0;

async function run() {
  const seq = ++requestSeq;
  form.clearErrors();
  form.showBanner(null);
  results.clear();
  form.setBusy(true);
  const res = await api.calculate(form.collect());
  if (seq !== requestSeq) return; // a newer request superseded this one
  form.setBusy(false);
  if (res.ok) results.render(res.data);
  else if (res.networkError) form.showBanner(UNAVAILABLE);
  else if (res.errors) form.showErrors(res.errors);
  else form.showBanner(res.error ?? UNAVAILABLE);
}

async function refreshScenarios() {
  const res = await api.listScenarios();
  if (!res.ok) {
    scenarios.showNote('Saved scenarios are unavailable right now.');
    return;
  }
  scenarios.showNote(null);
  scenarios.renderList(res.data, {
    onLoad: (item) => {
      form.clearErrors();
      results.clear();
      form.setValues(item.inputs);
    },
    onDelete: async (item) => {
      const del = await api.deleteScenario(item.id);
      if (del.ok || del.status === 404) await refreshScenarios();
      else scenarios.showNote('Could not delete the scenario.');
    },
  });
}

async function save() {
  scenarios.setNameError(null);
  form.clearErrors();
  const res = await api.saveScenario(scenarios.nameValue(), form.collect());
  if (res.ok) {
    await refreshScenarios();
  } else if (res.networkError) {
    scenarios.showNote('Saved scenarios are unavailable right now.');
  } else if (res.errors) {
    const { name, ...fieldErrors } = res.errors;
    if (name) scenarios.setNameError(name);
    form.showErrors(fieldErrors);
  } else {
    scenarios.showNote(res.error ?? 'Could not save the scenario.');
  }
}

form.onCalculate(run);
scenarios.onSave(save);
refreshScenarios();
