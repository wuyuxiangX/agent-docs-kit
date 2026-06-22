#!/usr/bin/env node
import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = process.cwd();
const configPath = join(root, '.agent-docs-kit', 'config.json');

function fail(message) {
  console.error(`Error: ${message}`);
  process.exit(1);
}

if (!existsSync(configPath)) {
  fail('missing .agent-docs-kit/config.json; run agent-docs-kit init first');
}

const config = JSON.parse(readFileSync(configPath, 'utf8'));
const contentDir = join(root, config.contentDir || 'docs/content/docs');
const templatesDir = join(root, '.agent-docs-kit', 'templates');

function slugify(input) {
  return input
    .toLowerCase()
    .trim()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '') || 'doc';
}

function titleize(input) {
  return input
    .replace(/[-_]+/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

function render(template, values) {
  let out = template;
  for (const [key, value] of Object.entries(values)) {
    out = out.replaceAll(`__${key}__`, value);
  }
  return out;
}

function writeNew(path, content) {
  if (existsSync(path)) {
    fail(`refusing to overwrite existing file: ${path}`);
  }
  mkdirSync(dirname(path), { recursive: true });
  writeFileSync(path, content);
}

const [kind, domainArg, topicArg, ...titleParts] = process.argv.slice(2);
if (!kind || !['atlas', 'architecture', 'change', 'plan'].includes(kind)) {
  fail('usage: create-doc.mjs <atlas|architecture|change|plan> <domain> [topic-slug] [title]');
}
if (!domainArg) {
  fail('domain is required');
}

const domain = slugify(domainArg);
const today = new Date().toISOString().slice(0, 10);
const topic = topicArg ? slugify(topicArg) : domain;
const title = titleParts.length ? titleParts.join(' ') : titleize(topic);
const source = process.env.AGENT_DOCS_KIT_SOURCE || 'TODO';
const tests = process.env.AGENT_DOCS_KIT_TESTS || 'TODO';

let templateName = `${kind}.mdx`;
let outPath;
if (kind === 'atlas') {
  outPath = join(contentDir, 'atlas.mdx');
} else if (kind === 'architecture') {
  outPath = join(contentDir, domain, 'architecture.mdx');
} else if (kind === 'change') {
  outPath = join(contentDir, domain, 'changes', `${today}-${topic}.mdx`);
} else {
  outPath = join(contentDir, domain, 'plans', `${topic}.mdx`);
}

const template = readFileSync(join(templatesDir, templateName), 'utf8');
writeNew(outPath, render(template, {
  TITLE: title,
  DOMAIN: domain,
  DATE: today,
  SOURCE: source,
  TESTS: tests,
}));

console.log(outPath);
