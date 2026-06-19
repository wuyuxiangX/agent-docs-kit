#!/usr/bin/env node
import { existsSync, readFileSync, readdirSync, statSync } from 'node:fs';
import { join, relative } from 'node:path';

const root = process.cwd();
const configPath = join(root, '.living-docs', 'config.json');
const errors = [];

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

function hasDiagram(text) {
  return [
    '<ArchMap',
    '<FlowSteps',
    '<StateFlow',
    '<SystemMap',
    '<LayerMap',
    '<FlowMap',
    '<RoadmapMap',
    '```mermaid',
  ].some((marker) => text.includes(marker));
}

if (!existsSync(configPath)) {
  errors.push('missing .living-docs/config.json');
} else {
  const config = JSON.parse(readFileSync(configPath, 'utf8'));
  const contentDir = join(root, config.contentDir || 'docs/content/docs');
  if (!existsSync(contentDir)) {
    errors.push(`missing content directory: ${relative(root, contentDir)}`);
  } else {
    const files = walk(contentDir);
    if (files.length === 0) errors.push('no MDX files found');
    for (const file of files) {
      const rel = relative(root, file);
      const text = readFileSync(file, 'utf8');
      const fm = frontmatter(text);
      const type = scalar(fm, 'type');
      if (!scalar(fm, 'title')) errors.push(`${rel}: missing title`);
      if (rel.includes('/changes/') && type !== 'change') errors.push(`${rel}: changes pages must set type: change`);
      if (rel.includes('/plans/') && type !== 'plan') errors.push(`${rel}: plan pages must set type: plan`);
      if ((type === 'architecture' || type === 'change') && !hasDiagram(text)) {
        errors.push(`${rel}: architecture/change docs need an architecture map, flow map, state map, roadmap map, or mermaid`);
      }
      if ((type === 'architecture' || type === 'change' || type === 'plan') && !fm.includes('terms:') && !text.includes('<TermGrid')) {
        errors.push(`${rel}: managed docs should define terms or render <TermGrid />`);
      }
    }
    if (!existsSync(join(contentDir, 'glossary.mdx'))) {
      errors.push('missing glossary.mdx; run node .living-docs/scripts/glossary.mjs');
    }
  }
}

if (errors.length) {
  console.error(`living-docs check failed (${errors.length} issue(s))`);
  for (const error of errors) console.error(`  - ${error}`);
  process.exit(1);
}

console.log('living-docs check passed');
