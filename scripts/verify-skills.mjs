import {createHash} from 'node:crypto';
import {readFile, readdir, lstat, writeFile} from 'node:fs/promises';
import {join, resolve, relative, dirname} from 'node:path';

const root = resolve(import.meta.dirname, '..');
const skillsRoot = join(root, 'skills');
const manifestPath = join(skillsRoot, 'manifest.json');
const write = process.argv.includes('--write');
const forbidden = /cutagent_(?:account_status|connect_local_runtime|(?:music|color|sound_effect)_asset_[a-z_]+|sound_effect_search)|CUTAGENT_CLOUD|app\.cutagent\.ai|CutAgent Cloud|CutAgent desktop|CutAgent account|\bhosted\b|\bsubscription\b|ElevenLabs|Supabase|Cloudflare R2|cutagent-sdk --title/i;

async function walk(directory) {
  const paths = [];
  for (const entry of await readdir(directory, {withFileTypes: true})) {
    const path = join(directory, entry.name);
    const stat = await lstat(path);
    if (stat.isSymbolicLink()) throw new Error(`Skill symlink is not allowed: ${path}`);
    if (stat.isDirectory()) paths.push(...await walk(path));
    else if (stat.isFile()) paths.push(path);
    else throw new Error(`Non-regular skill entry: ${path}`);
  }
  return paths;
}

const files = (await walk(skillsRoot)).filter((path) => path !== manifestPath).sort();
const entries = [];
const skills = new Set();
for (const path of files) {
  const rel = relative(skillsRoot, path).replaceAll('\\', '/');
  const parts = rel.split('/');
  if (parts.length < 2 || !/^cutagent(?:-[a-z0-9]+)*$/.test(parts[0])) throw new Error(`Unexpected skill path: ${rel}`);
  const bytes = await readFile(path);
  const body = bytes.toString('utf8');
  if (forbidden.test(body)) throw new Error(`Hosted/private runtime dependency in ${rel}`);
  if (/\/(?:Users|home)\/[A-Za-z0-9_.-]+/.test(body)) throw new Error(`Machine path in ${rel}`);
  if (parts.length === 2 && parts[1] === 'SKILL.md') {
    const frontmatter = body.match(/^---\n([\s\S]*?)\n---\n/);
    if (!frontmatter) throw new Error(`Missing YAML frontmatter in ${rel}`);
    const name = frontmatter[1].match(/^name:\s*(.+)$/m)?.[1]?.trim();
    const description = frontmatter[1].match(/^description:\s*(.+)$/m)?.[1]?.trim();
    if (name !== parts[0] || name.length > 64) throw new Error(`Invalid skill name in ${rel}`);
    if (!description || description.length > 1024) throw new Error(`Invalid skill description in ${rel}`);
    if (!/^license:\s*AGPL-3\.0-only$/m.test(frontmatter[1])) throw new Error(`Missing public license in ${rel}`);
    skills.add(name);
  }
  if (rel.endsWith('.md')) {
    for (const match of body.matchAll(/!?\[[^\]]*\]\(([^)]+)\)/g)) {
      const href = match[1].split(/[?#]/)[0];
      if (!href || /^(?:https?:|mailto:|tel:|data:)/.test(href)) continue;
      const target = resolve(dirname(path), decodeURIComponent(href));
      if (!target.startsWith(skillsRoot + '/') || !(await lstat(target).catch(() => null))) {
        throw new Error(`Broken or escaping skill link in ${rel}: ${href}`);
      }
    }
  }
  entries.push({path: rel, sha256: createHash('sha256').update(bytes).digest('hex')});
}
for (const name of new Set(entries.map(({path}) => path.split('/')[0]))) {
  if (!skills.has(name)) throw new Error(`Missing SKILL.md in ${name}`);
}
const manifest = {schemaVersion: 1, files: entries};
if (write) {
  await writeFile(manifestPath, JSON.stringify(manifest, null, 2) + '\n');
} else {
  const recorded = JSON.parse(await readFile(manifestPath, 'utf8'));
  if (JSON.stringify(recorded) !== JSON.stringify(manifest)) throw new Error('Skill manifest is missing, stale, or contains unexpected paths');
}
if (!process.argv.includes('--quiet')) console.log(`Verified ${skills.size} standalone skills and ${entries.length} allowlisted files.`);
