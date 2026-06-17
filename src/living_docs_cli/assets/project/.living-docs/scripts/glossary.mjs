#!/usr/bin/env node
import { existsSync, readFileSync, writeFileSync } from 'node:fs';
import { join, relative } from 'node:path';
import { readdirSync, statSync } from 'node:fs';

const root = process.cwd();
const configPath = join(root, '.living-docs', 'config.json');

function fail(message) {
  console.error(`Error: ${message}`);
  process.exit(1);
}

if (!existsSync(configPath)) {
  fail('missing .living-docs/config.json; run living-docs init first');
}

const config = JSON.parse(readFileSync(configPath, 'utf8'));
const contentDir = join(root, config.contentDir || 'docs/content/docs');
const glossaryPath = join(contentDir, 'glossary.mdx');

function walk(dir) {
  const results = [];
  for (const name of readdirSync(dir)) {
    const path = join(dir, name);
    const stat = statSync(path);
    if (stat.isDirectory()) results.push(...walk(path));
    if (stat.isFile() && path.endsWith('.mdx')) results.push(path);
  }
  return results;
}

function frontmatter(text) {
  if (!text.startsWith('---\n')) return '';
  const end = text.indexOf('\n---', 4);
  return end === -1 ? '' : text.slice(4, end);
}

function scalar(fm, key) {
  const match = fm.match(new RegExp(`^${key}:\\s*["']?([^"'\\n]+)["']?\\s*$`, 'm'));
  return match?.[1]?.trim() || '';
}

function terms(fm) {
  const lines = fm.split(/\r?\n/);
  const out = [];
  let inTerms = false;
  let current = null;
  for (const line of lines) {
    if (line.startsWith('terms:')) {
      inTerms = true;
      continue;
    }
    if (inTerms && /^[a-zA-Z0-9_-]+:/.test(line)) break;
    if (!inTerms) continue;
    const name = line.match(/^\s*-\s*name:\s*["']?(.+?)["']?\s*$/);
    if (name) {
      current = { name: name[1], description: '' };
      out.push(current);
      continue;
    }
    const description = line.match(/^\s*description:\s*["']?(.+?)["']?\s*$/);
    if (description && current) current.description = description[1];
  }
  return out;
}

const byName = new Map();
for (const file of walk(contentDir)) {
  if (file === glossaryPath) continue;
  const fm = frontmatter(readFileSync(file, 'utf8'));
  const domain = scalar(fm, 'domain') || 'system';
  for (const term of terms(fm)) {
    const key = term.name.toLowerCase();
    if (!byName.has(key)) {
      byName.set(key, { ...term, domain, sources: [] });
    }
    byName.get(key).sources.push(relative(contentDir, file));
  }
}

const items = [...byName.values()].sort((a, b) => a.name.localeCompare(b.name));
const bodyItems = items
  .map((item) => `    { name: ${JSON.stringify(item.name)}, description: ${JSON.stringify(item.description)}, meta: ${JSON.stringify(`${item.domain} · ${item.sources.join(', ')}`)} },`)
  .join('\n');

const content = [
  '---',
  'title: "Glossary"',
  'description: "Generated term index for living-docs"',
  'type: "glossary"',
  '---',
  '',
  '# Glossary',
  '',
  'Generated from MDX frontmatter `terms`.',
  '',
  '<TermGrid',
  '  items={[',
  bodyItems,
  '  ]}',
  '/>',
  '',
].join('\n');

writeFileSync(glossaryPath, content);
console.log(`wrote ${relative(root, glossaryPath)} (${items.length} terms)`);
