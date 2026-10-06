// Every requirement ID in docs/v1/03-test-scenarios.md section 1 must be cited by at least one
// test ID that exists as a test() name in tests/*.test.js. Exit 0 if covered, 1 otherwise.
import { readFileSync, readdirSync } from 'node:fs';
import { fileURLToPath } from 'node:url';

const root = fileURLToPath(new URL('..', import.meta.url));
const doc = readFileSync(`${root}docs/v1/03-test-scenarios.md`, 'utf8');

const section1 = doc.split('## 2.')[0];
const required = [...section1.matchAll(/^\| (F[0-9.]+) \|/gm)].map((m) => m[1]);

const testDir = `${root}tests/`;
const implemented = new Set();
for (const f of readdirSync(testDir).filter((n) => n.endsWith('.test.js'))) {
  const src = readFileSync(testDir + f, 'utf8');
  for (const m of src.matchAll(/\b((?:VAL|CAL|FMT|UIF|UIR|INT)-\d{2})\b/g)) implemented.add(m[1]);
}

const covered = new Set();
for (const m of doc.matchAll(/^\| ((?:VAL|CAL|FMT|UIF|UIR|INT)-\d{2}) \|(.*)$/gm)) {
  if (!implemented.has(m[1])) continue;
  const cells = m[2].split('|').map((c) => c.trim());
  const verifies = cells[cells.length - 3] ?? ''; // ... | Verifies requirement | Type |
  for (const id of verifies.split(',').map((s) => s.trim())) covered.add(id);
}

const missing = required.filter((id) => !covered.has(id));
if (missing.length) {
  console.error(`Uncovered requirement IDs (${missing.length}/${required.length}): ${missing.join(', ')}`);
  process.exit(1);
}
console.log(`All ${required.length} requirement IDs covered.`);
