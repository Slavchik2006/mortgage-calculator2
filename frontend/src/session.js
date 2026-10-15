// Anonymous session id: random UUID kept in localStorage (no accounts). Falls back to a
// per-page-load id if storage is unavailable.
const KEY = 'mortgage-session-id';
let memoryId = null;

export function getSessionId() {
  try {
    let id = localStorage.getItem(KEY);
    if (!id) {
      id = crypto.randomUUID();
      localStorage.setItem(KEY, id);
    }
    return id;
  } catch {
    memoryId ??= crypto.randomUUID();
    return memoryId;
  }
}
