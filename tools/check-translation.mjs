#!/usr/bin/env node
/**
 * Translation guard, run before every build.
 *
 * The English edition is the structural source of truth. A translation is
 * allowed to change words and nothing else — so this checks that every
 * translated chapter still carries the same chapter number, the same printed
 * page range, the same figures in the same order, and that the market
 * vocabulary the translation is supposed to keep in English is still there.
 *
 * It fails the build rather than warning, for the same reason tools/prune.py
 * does: a silent structural drift between the two editions is worse than a
 * broken build.
 */
import { readFileSync, readdirSync, existsSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const site = join(root, 'site', 'src');
const LANGS = [{ code: 'pa', dir: join(site, 'content', 'book-pa') }];

const problems = [];
const fail = (msg) => problems.push(msg);

const frontmatter = (text, file) => {
  const m = text.match(/^---\n([\s\S]*?)\n---/);
  if (!m) throw new Error(`${file}: no frontmatter`);
  const out = {};
  for (const line of m[1].split('\n')) {
    const kv = line.match(/^(\w+):\s*(.*)$/);
    if (kv) out[kv[1]] = kv[2].replace(/^"|"$/g, '');
  }
  return out;
};

/** every <Figure src=".." /> in document order */
const figures = (text) => [...text.matchAll(/<Figure\s+src="([^"]+)"/g)].map((m) => m[1]);

const enDir = join(site, 'content', 'book');
const enFiles = readdirSync(enDir).filter((f) => f.endsWith('.mdx')).sort();

// ── chapters ────────────────────────────────────────────────────────────
for (const { code, dir } of LANGS) {
  const translated = new Set(readdirSync(dir).filter((f) => f.endsWith('.mdx')));

  for (const file of enFiles) {
    if (!translated.has(file)) { fail(`${code}: missing chapter ${file}`); continue; }
    translated.delete(file);

    const en = readFileSync(join(enDir, file), 'utf8');
    const tr = readFileSync(join(dir, file), 'utf8');
    const a = frontmatter(en, file);
    const b = frontmatter(tr, `${code}/${file}`);

    for (const key of ['order', 'printedStart', 'printedEnd', 'figures']) {
      if (a[key] !== b[key]) fail(`${code}/${file}: ${key} is ${b[key]}, English says ${a[key]}`);
    }
    if (!b.title?.trim()) fail(`${code}/${file}: empty title`);
    if (!b.section?.trim()) fail(`${code}/${file}: empty section`);

    const fa = figures(en);
    const fb = figures(tr);
    if (fa.join('|') !== fb.join('|')) {
      fail(`${code}/${file}: figures differ\n    English: ${fa.join(', ') || '(none)'}\n    ${code}: ${fb.join(', ') || '(none)'}`);
    }
    if (fb.length !== Number(b.figures)) {
      fail(`${code}/${file}: frontmatter says ${b.figures} figures, body has ${fb.length}`);
    }
  }
  for (const extra of translated) fail(`${code}: ${extra} has no English original`);

  // Section names must be consistent: one English section maps to exactly one
  // translated name, or the sidebar splits a section in two.
  const sections = new Map();
  for (const file of enFiles) {
    if (!existsSync(join(dir, file))) continue;
    const a = frontmatter(readFileSync(join(enDir, file), 'utf8'), file).section;
    const b = frontmatter(readFileSync(join(dir, file), 'utf8'), file).section;
    const seen = sections.get(a);
    if (seen === undefined) sections.set(a, b);
    else if (seen !== b) fail(`${code}: section "${a}" is translated both as "${seen}" and "${b}"`);
  }
}

// ── kept vocabulary ─────────────────────────────────────────────────────
// A spot check, not a proof: these terms appear so often in the English text
// that a translation which rendered them into Gurmukhi would show up here.
const KEEP = ['volume', 'market', 'price', 'spread', 'trend'];
for (const { code, dir } of LANGS) {
  for (const file of enFiles) {
    const path = join(dir, file);
    if (!existsSync(path)) continue;
    const en = readFileSync(join(enDir, file), 'utf8').toLowerCase();
    const tr = readFileSync(path, 'utf8').toLowerCase();
    for (const term of KEEP) {
      const inEn = (en.match(new RegExp(term, 'g')) || []).length;
      if (inEn >= 5 && !tr.includes(term)) {
        fail(`${code}/${file}: "${term}" appears ${inEn}× in English but never in the translation — market vocabulary must stay in English (see src/data/i18n/keep-terms.json)`);
      }
    }
  }
}

// ── data files ──────────────────────────────────────────────────────────
const readJson = (p) => JSON.parse(readFileSync(p, 'utf8'));
const slugOf = (id) => id.replace(/^\d+-/, '').replace(/\.mdx$/, '');
const slugs = enFiles.map(slugOf);

for (const { code } of LANGS) {
  const dataDir = join(site, 'data', code);

  const notes = readJson(join(dataDir, 'annotations.json'));
  for (const slug of slugs) {
    const n = notes[slug];
    if (!n) { fail(`${code}/annotations.json: missing "${slug}"`); continue; }
    if (!n.plain?.trim()) fail(`${code}/annotations.json: "${slug}" has no plain summary`);
    const enNote = readJson(join(site, 'data', 'annotations.json'))[slug];
    if (enNote && n.remember?.length !== enNote.remember.length) {
      fail(`${code}/annotations.json: "${slug}" has ${n.remember?.length} takeaways, English has ${enNote.remember.length}`);
    }
  }

  const glEn = readJson(join(site, 'data', 'glossary.json'));
  const glTr = readJson(join(dataDir, 'glossary.json'));
  const byslug = new Map(glTr.map((e) => [e.slug, e]));
  for (const entry of glEn) {
    const t = byslug.get(entry.slug);
    if (!t) { fail(`${code}/glossary.json: missing "${entry.slug}"`); continue; }
    const kinds = (blocks) => blocks.map((b) => b.t).join('|');
    if (kinds(entry.blocks) !== kinds(t.blocks)) {
      fail(`${code}/glossary.json: "${entry.slug}" block structure differs (${kinds(t.blocks)} vs ${kinds(entry.blocks)})`);
    }
    for (const [i, b] of entry.blocks.entries()) {
      if (b.t === 'figure' && b.src !== t.blocks[i]?.src) {
        fail(`${code}/glossary.json: "${entry.slug}" figure ${i} points at ${t.blocks[i]?.src}, English has ${b.src}`);
      }
    }
  }

  const dgEn = readJson(join(site, 'data', 'diagrams.json'));
  const dgTr = readJson(join(dataDir, 'diagrams.json'));
  for (const name of Object.keys(dgTr)) {
    if (!(name in dgEn)) fail(`${code}/diagrams.json: "${name}" is not a diagram`);
  }
  for (const name of Object.keys(dgEn)) {
    if (!(name in dgTr)) fail(`${code}/diagrams.json: missing "${name}"`);
  }
}

if (problems.length) {
  console.error(`\ntranslation check failed — ${problems.length} problem(s):\n`);
  for (const p of problems) console.error(`  • ${p}`);
  console.error('');
  process.exit(1);
}
console.log(`translation check passed — ${enFiles.length} chapters × ${LANGS.length} translation(s)`);
