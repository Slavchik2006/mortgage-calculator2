import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, readdirSync } from 'node:fs';
import { spawn } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const root = fileURLToPath(new URL('..', import.meta.url));
const read = (p) => readFileSync(root + p, 'utf8');

function walk(dir) {
  return readdirSync(root + dir, { withFileTypes: true }).flatMap((d) =>
    d.isDirectory() ? walk(`${dir}/${d.name}`) : [`${dir}/${d.name}`]);
}

test('INT-17 dependency direction', () => {
  const allowed = {
    'src/formatting.js': [],
    'src/validation.js': ['types', 'constants'],
    'src/calculation.js': ['types', 'constants'],
    'src/ui/form.js': ['types'],
    'src/ui/results.js': ['types', 'formatting'],
  };
  const violations = [];
  for (const file of walk('src').filter((f) => f.endsWith('.js'))) {
    const imports = [...read(file).matchAll(/from '\.{1,2}\/([^']+?)(?:\.js)?'/g)].map((m) => m[1].split('/').pop());
    const rule = allowed[file];
    if (!rule) continue;
    for (const dep of imports) if (!rule.includes(dep)) violations.push(`${file} -> ${dep}`);
  }
  assert.deepEqual(violations, []);
});

test('TECH-02 application starts with a single command', async () => {
  const port = 3917;
  const child = spawn(process.execPath, ['scripts/serve.mjs'], { cwd: root, env: { ...process.env, PORT: String(port) } });
  try {
    await new Promise((resolve, reject) => {
      child.stdout.on('data', resolve);
      child.on('error', reject);
      child.on('exit', () => reject(new Error('server exited')));
      setTimeout(() => reject(new Error('server did not start within 5 s')), 5000);
    });
    const page = await fetch(`http://localhost:${port}/`);
    const html = await page.text();
    assert.equal(page.status, 200);
    assert.ok(html.includes('<button') && html.includes('Calculate'));
    const js = await fetch(`http://localhost:${port}/src/main.js`);
    assert.equal(js.status, 200);
    assert.match(js.headers.get('content-type'), /javascript/);
  } finally {
    child.kill();
  }
});

test('TECH-03 README explains how to run it', () => {
  const readme = read('README.md');
  const node = JSON.parse(read('package.json')).engines.node;
  const min = node.replace(/[^0-9.]/g, '');
  for (const s of ['npm test', 'npm start', 'http://localhost:3000', min]) {
    assert.ok(readme.includes(s), `README is missing ${s}`);
  }
});

test('TECH-05 no runtime dependencies', () => {
  const pkg = JSON.parse(read('package.json'));
  assert.deepEqual(pkg.dependencies ?? {}, {});
  assert.deepEqual(pkg.devDependencies ?? {}, {});
});
