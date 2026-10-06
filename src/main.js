import { validate } from './validation.js';
import { calculate } from './calculation.js';
import * as form from './ui/form.js';
import * as results from './ui/results.js';

function run() {
  form.clearErrors();
  results.clear();
  const validation = validate(form.collect());
  if (!validation.ok) {
    form.showErrors(validation.errors);
    return;
  }
  results.render(calculate(validation.value));
}

form.onCalculate(run);
