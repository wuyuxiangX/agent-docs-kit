export type ArchTone = 'blue' | 'green' | 'violet' | 'amber' | 'red';

export type ArchBox = {
  title: string;
  body: string;
  tone?: ArchTone;
};

export type ArchTier = {
  title: string;
  boxes: ArchBox[];
};

export function DocsHero({
  title,
  eyebrow = 'Living documentation',
  description,
  primaryHref = '/docs/atlas',
  primaryLabel = 'Open Project Atlas',
  secondaryHref = '/docs/glossary',
  secondaryLabel = 'View glossary',
}: {
  title: string;
  eyebrow?: string;
  description: string;
  primaryHref?: string;
  primaryLabel?: string;
  secondaryHref?: string;
  secondaryLabel?: string;
}) {
  return (
    <section className="ld-docs-hero">
      <div className="ld-hero-kicker">{eyebrow}</div>
      <h1>{title}</h1>
      <p>{description}</p>
      <div className="ld-hero-actions">
        <a className="ld-hero-action" data-primary="true" href={primaryHref}>
          {primaryLabel}
        </a>
        <a className="ld-hero-action" href={secondaryHref}>
          {secondaryLabel}
        </a>
      </div>
    </section>
  );
}

export type SkillItem = {
  name: string;
  body: string;
  tone?: ArchTone;
};

export type FlowStep = {
  title: string;
  body: string;
  tone?: ArchTone;
};

export type StateNode = {
  name: string;
  description?: string;
  tone?: ArchTone;
};

export function SkillGrid({ items }: { items: SkillItem[] }) {
  return (
    <ul className="ld-skill-grid">
      {items.map((item) => (
        <li className="ld-skill-card" data-tone={item.tone} key={item.name}>
          <code>{item.name}</code>
          <span>{item.body}</span>
        </li>
      ))}
    </ul>
  );
}

export function ArchMap({ tiers }: { tiers: ArchTier[] }) {
  return (
    <div className="ld-arch-map">
      {tiers.map((tier) => (
        <section className="ld-tier" key={tier.title}>
          <div className="ld-tier-title">{tier.title}</div>
          <div className="ld-boxes">
            {tier.boxes.map((box) => (
              <div className="ld-box" data-tone={box.tone} key={`${tier.title}-${box.title}`}>
                <strong>{box.title}</strong>
                <span>{box.body}</span>
              </div>
            ))}
          </div>
        </section>
      ))}
    </div>
  );
}

export type SystemNode = {
  title: string;
  body: string;
  tone?: ArchTone;
  href?: string;
};

export type SystemLink = {
  from: string;
  to: string;
  label?: string;
};

export function SystemMap({
  title,
  nodes,
  links = [],
}: {
  title?: string;
  nodes: SystemNode[];
  links?: SystemLink[];
}) {
  return (
    <section className="ld-system-map">
      {title ? <div className="ld-map-title">{title}</div> : null}
      <div className="ld-system-grid">
        {nodes.map((node) => {
          const content = (
            <>
              <strong>{node.title}</strong>
              <span>{node.body}</span>
            </>
          );
          return node.href ? (
            <a className="ld-system-node" data-tone={node.tone} href={node.href} key={node.title}>
              {content}
            </a>
          ) : (
            <div className="ld-system-node" data-tone={node.tone} key={node.title}>
              {content}
            </div>
          );
        })}
      </div>
      {links.length ? (
        <ol className="ld-system-links">
          {links.map((link) => (
            <li key={`${link.from}-${link.to}-${link.label ?? ''}`}>
              <span>{link.from}</span>
              <strong>{link.label ?? 'connects to'}</strong>
              <span>{link.to}</span>
            </li>
          ))}
        </ol>
      ) : null}
    </section>
  );
}

export type LayerItem = {
  title: string;
  body: string;
  tone?: ArchTone;
  items: string[];
};

export function LayerMap({
  title,
  layers,
}: {
  title?: string;
  layers: LayerItem[];
}) {
  return (
    <section className="ld-layer-map">
      {title ? <div className="ld-map-title">{title}</div> : null}
      <div className="ld-layer-stack">
        {layers.map((layer) => (
          <section className="ld-layer-row" data-tone={layer.tone} key={layer.title}>
            <div>
              <strong>{layer.title}</strong>
              <span>{layer.body}</span>
            </div>
            <ul>
              {layer.items.map((item) => (
                <li key={`${layer.title}-${item}`}>
                  <code>{item}</code>
                </li>
              ))}
            </ul>
          </section>
        ))}
      </div>
    </section>
  );
}

export type FlowLane = {
  title: string;
  body: string;
  tone?: ArchTone;
  steps: string[];
};

export function FlowMap({
  title,
  flows,
}: {
  title?: string;
  flows: FlowLane[];
}) {
  return (
    <section className="ld-flow-map">
      {title ? <div className="ld-map-title">{title}</div> : null}
      <div className="ld-flow-lanes">
        {flows.map((flow) => (
          <section className="ld-flow-lane" data-tone={flow.tone} key={flow.title}>
            <strong>{flow.title}</strong>
            <span>{flow.body}</span>
            <ol>
              {flow.steps.map((step, index) => (
                <li key={`${flow.title}-${step}`}>
                  <span>{String(index + 1).padStart(2, '0')}</span>
                  {step}
                </li>
              ))}
            </ol>
          </section>
        ))}
      </div>
    </section>
  );
}

export type RoadmapItem = {
  title: string;
  body: string;
  status?: string;
  tone?: ArchTone;
};

export function RoadmapMap({ items }: { items: RoadmapItem[] }) {
  return (
    <section className="ld-roadmap-map">
      {items.map((item) => (
        <article className="ld-roadmap-item" data-tone={item.tone} key={item.title}>
          {item.status ? <span className="ld-roadmap-status">{item.status}</span> : null}
          <strong>{item.title}</strong>
          <span>{item.body}</span>
        </article>
      ))}
    </section>
  );
}

export function FlowSteps({
  title,
  steps,
}: {
  title?: string;
  steps: FlowStep[];
}) {
  return (
    <section className="ld-flow">
      {title ? <div className="ld-flow-title">{title}</div> : null}
      <ol className="ld-flow-steps">
        {steps.map((step, index) => (
          <li className="ld-flow-step" data-tone={step.tone} key={`${index}-${step.title}`}>
            <span className="ld-step-index">{String(index + 1).padStart(2, '0')}</span>
            <div>
              <strong>{step.title}</strong>
              <span>{step.body}</span>
            </div>
          </li>
        ))}
      </ol>
    </section>
  );
}

export function StateFlow({
  title,
  states,
}: {
  title?: string;
  states: StateNode[];
}) {
  return (
    <section className="ld-state-flow">
      {title ? <div className="ld-flow-title">{title}</div> : null}
      <div className="ld-state-row">
        {states.map((state, index) => (
          <div className="ld-state-group" key={`${index}-${state.name}`}>
            <div className="ld-state-node" data-tone={state.tone}>
              <strong>{state.name}</strong>
              {state.description ? <span>{state.description}</span> : null}
            </div>
            {index < states.length - 1 ? <span className="ld-state-arrow">{'->'}</span> : null}
          </div>
        ))}
      </div>
    </section>
  );
}

export type TermItem = {
  name: string;
  description: string;
  meta?: string;
};

export function TermGrid({ items }: { items: TermItem[] }) {
  return (
    <ul className="ld-term-grid">
      {items.map((item) => (
        <li className="ld-term" key={item.name}>
          <strong>{item.name}</strong>
          <span>{item.description}</span>
          {item.meta ? <div className="ld-meta">{item.meta}</div> : null}
        </li>
      ))}
    </ul>
  );
}

export function ChangeMeta({
  date,
  source,
  tests,
}: {
  date?: string;
  source?: string;
  tests?: string;
}) {
  return (
    <div className="ld-change-meta">
      {date ? <span className="ld-chip">Date: {date}</span> : null}
      {source ? <span className="ld-chip">Source: {source}</span> : null}
      {tests ? <span className="ld-chip">Tests: {tests}</span> : null}
    </div>
  );
}
