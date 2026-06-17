import { defineConfig, defineDocs } from 'fumadocs-mdx/config';
import { pageSchema, metaSchema } from 'fumadocs-core/source/schema';
import { z } from 'zod';

export const docs = defineDocs({
  dir: 'content/docs',
  docs: {
    schema: pageSchema.extend({
      domain: z.string().optional(),
      type: z.enum(['guide', 'architecture', 'change', 'plan', 'glossary']).default('guide'),
      status: z.enum(['draft', 'active', 'shipped', 'deprecated']).optional(),
      date: z.string().optional(),
      source: z.string().optional(),
      tests: z.string().optional(),
      terms: z
        .array(
          z.object({
            name: z.string(),
            description: z.string(),
          }),
        )
        .default([]),
    }),
  },
  meta: {
    schema: metaSchema,
  },
});

export default defineConfig({
  mdxOptions: {
    providerImportSource: '@/components/mdx',
  },
});
