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
  primaryHref = '/docs/architecture',
  primaryLabel = 'Open architecture',
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
