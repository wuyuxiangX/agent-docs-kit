import defaultMdxComponents from 'fumadocs-ui/mdx';
import type { MDXComponents } from 'mdx/types';
import {
  ArchMap,
  ChangeMeta,
  DocsHero,
  FlowMap,
  FlowSteps,
  LayerMap,
  RoadmapMap,
  SkillGrid,
  StateFlow,
  SystemMap,
  TermGrid,
} from './agent-docs-kit';

export function getMDXComponents(components?: MDXComponents) {
  return {
    ...defaultMdxComponents,
    ArchMap,
    ChangeMeta,
    DocsHero,
    FlowMap,
    FlowSteps,
    LayerMap,
    RoadmapMap,
    SkillGrid,
    StateFlow,
    SystemMap,
    TermGrid,
    ...components,
  } satisfies MDXComponents;
}

export const useMDXComponents = getMDXComponents;
