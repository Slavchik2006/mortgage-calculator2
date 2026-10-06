import { formatEur } from '../formatting.js';

const container = () => document.getElementById('results');

function el(tag, text, className) {
  const node = document.createElement(tag);
  if (text !== undefined) node.textContent = text;
  if (className) node.className = className;
  return node;
}

function summaryBlock(s) {
  const rows = [
    ['Monthly payment (principal and interest)', s.monthlyPI],
    ['Monthly property tax', s.monthlyTax],
    ['Monthly home insurance', s.monthlyInsurance],
    ['Total monthly payment', s.monthlyTotal],
    ['Total paid over the term (principal and interest)', s.totalPaid],
    ['Total interest', s.totalInterest],
  ];
  const dl = el('dl', undefined, 'summary');
  for (const [label, value] of rows) {
    dl.append(el('dt', label), el('dd', formatEur(value)));
  }
  return dl;
}

function scheduleTable(schedule) {
  const table = el('table');
  const head = el('tr');
  for (const h of ['Month', 'Payment', 'Interest', 'Principal', 'Remaining balance']) {
    head.append(el('th', h));
  }
  const thead = el('thead');
  thead.append(head);
  table.append(thead);
  const body = el('tbody');
  for (const row of schedule) {
    const tr = el('tr');
    tr.append(
      el('td', String(row.month)),
      el('td', formatEur(row.payment)),
      el('td', formatEur(row.interest)),
      el('td', formatEur(row.principal)),
      el('td', formatEur(row.balance)),
    );
    body.append(tr);
  }
  table.append(body);
  const wrap = el('div', undefined, 'table-scroll');
  wrap.append(table);
  return wrap;
}

/** @param {import('../types.js').MortgageResult} result */
export function render(result) {
  container().replaceChildren(summaryBlock(result.summary), scheduleTable(result.schedule));
}

export function clear() {
  container().replaceChildren();
}
