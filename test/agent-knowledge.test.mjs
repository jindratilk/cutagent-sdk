import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import test from 'node:test';
import ts from 'typescript';

const root = path.resolve(import.meta.dirname, '../skills/cutagent');
function walk(directory) {
  return fs.readdirSync(directory, {withFileTypes: true}).flatMap(entry => {
    const file = path.join(directory, entry.name);
    return entry.isDirectory() ? walk(file) : [file];
  });
}
const files = walk(root);

test('every knowledge reference is reachable from the skill and all local links resolve', () => {
  const visited = new Set();
  function visit(file) {
    if (visited.has(file)) return;
    visited.add(file);
    for (const match of fs.readFileSync(file, 'utf8').matchAll(/\]\(([^)]+)\)/g)) {
      const target = match[1].split('#')[0];
      if (!target || /^[a-z]+:/i.test(target)) continue;
      const destination = path.resolve(path.dirname(file), target);
      assert.ok(fs.existsSync(destination), `${path.relative(root, file)}: missing ${target}`);
      assert.ok(destination.startsWith(root + path.sep), `Reference escapes the self-contained skill: ${target}`);
      if (destination.endsWith('.md')) visit(destination);
    }
  }
  visit(path.join(root, 'SKILL.md'));
  assert.deepEqual([...visited].sort(), files.filter(f => f.endsWith('.md')).sort());
});

test('JavaScript and TypeScript knowledge examples parse', () => {
  for (const file of files.filter(f => f.endsWith('.md'))) {
    let index = 0;
    for (const match of fs.readFileSync(file, 'utf8').matchAll(/^```(js|javascript|ts|typescript)\n([\s\S]*?)^```/gm)) {
      const language = match[1];
      const sourceName = `${path.relative(root, file)}:${++index}`;
      const result = ts.transpileModule(match[2], {
        fileName: sourceName + (/^(js|javascript)$/.test(language) ? '.js' : '.ts'),
        reportDiagnostics: true,
        compilerOptions: {target: ts.ScriptTarget.ES2023, module: ts.ModuleKind.ESNext, allowJs: true},
      });
      const errors = (result.diagnostics ?? []).filter(d => d.category === ts.DiagnosticCategory.Error);
      assert.deepEqual(errors.map(d => ts.flattenDiagnosticMessageText(d.messageText, '\n')), [], sourceName);
    }
  }
});

test('published package includes the skill entrypoint and references', () => {
  const pkg = JSON.parse(fs.readFileSync(path.resolve(root, '../../package.json'), 'utf8'));
  assert.ok(pkg.files.includes('skills/cutagent/'));
});
