import defaultMdxComponents from 'fumadocs-ui/mdx';
import type { MDXComponents } from 'mdx/types';
import {
  ArchMap,
  ChangeMeta,
  DocsHero,
  FlowSteps,
  SkillGrid,
  StateFlow,
  TermGrid,
} from './living-docs';

export function getMDXComponents(components?: MDXComponents) {
  return {
    ...defaultMdxComponents,
    ArchMap,
    ChangeMeta,
    DocsHero,
    FlowSteps,
    SkillGrid,
    StateFlow,
    TermGrid,
    ...components,
  } satisfies MDXComponents;
}

export const useMDXComponents = getMDXComponents;
