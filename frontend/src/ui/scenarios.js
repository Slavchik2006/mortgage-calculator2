const $ = (id) => document.getElementById(id);

export function nameValue() {
  return $('scenario-name').value;
}

export function setNameError(message) {
  $('scenario-name-error').textContent = message ?? '';
}

export function showNote(message) {
  const el = $('scenarios-note');
  el.textContent = message ?? '';
  el.hidden = !message;
}

function button(label, handler) {
  const b = document.createElement('button');
  b.type = 'button';
  b.textContent = label;
  b.addEventListener('click', handler);
  return b;
}

/** @param {{id:string,name:string,inputs:object}[]} items */
export function renderList(items, { onLoad, onDelete }) {
  const list = $('scenario-list');
  if (items.length === 0) {
    const li = document.createElement('li');
    li.className = 'empty';
    li.textContent = 'No saved scenarios yet.';
    list.replaceChildren(li);
    return;
  }
  list.replaceChildren(...items.map((item) => {
    const li = document.createElement('li');
    const name = document.createElement('span');
    name.className = 'name';
    name.textContent = item.name;
    li.append(name, button('Load', () => onLoad(item)), button('Delete', () => onDelete(item)));
    return li;
  }));
}

export function onSave(handler) {
  $('save-scenario').addEventListener('click', handler);
}
