# UI design guide

## Design principles
1. {Principle 1 — e.g. “Should feel like a tool, not a marketing site—a dashboard you use every day.”}
2. {Principle 2}
3. {Principle 3}

## AI slop antipatterns — do not do this
| Avoid | Reason |
|-------|------|
| backdrop-filter: blur() | Glass morphism is one of the most common AI-template tells |
| gradient-text (gradient on text) | #1 sign of AI-made SaaS landing pages |
| “Powered by AI” badges | Decoration, not functionality. No user value |
| box-shadow glow animations | Neon glow = AI slop |
| Purple / indigo brand colors | “AI = purple” cliché |
| Same rounded-2xl on every card | Uniform corners feel templated |
| Background gradient orbs (blur-3xl circles) | Ornament on every AI landing page |

## Color

### Backgrounds
| Use | Value |
|------|------|
| Page | {e.g. #0a0a0a} |
| Card | {e.g. #141414} |

### Text
| Use | Value |
|------|------|
| Primary text | {e.g. text-white} |
| Body | {e.g. text-neutral-300} |
| Secondary | {e.g. text-neutral-400} |
| Disabled | {e.g. text-neutral-500} |

### Data / semantic colors
| Use | Value |
|------|------|
| {Positive / success} | {e.g. #22c55e} |
| {Negative / error} | {e.g. #ef4444} |
| {Neutral / default} | {e.g. #525252} |

## Components

### Card
```
{e.g. rounded-lg bg-[#141414] border border-neutral-800 p-6}
```

### Button
```
Primary: {e.g. rounded-lg bg-white text-black hover:bg-neutral-200}
Text:    {e.g. text-neutral-500 hover:text-neutral-300}
```

### Input fields
```
{e.g. rounded-lg bg-neutral-900 border border-neutral-800 px-4 py-3}
```

## Layout
- Overall width: {e.g. max-w-5xl}
- Alignment: {e.g. left-aligned by default. No centered layouts}
- Spacing: {e.g. gap-3–4, space-y-8 between sections}

## Typography
| Use | Style |
|------|--------|
| Page title | {e.g. text-4xl font-semibold text-white} |
| Card title | {e.g. text-sm font-medium text-neutral-400} |
| Body | {e.g. text-sm text-neutral-300 leading-relaxed} |

## Animation
- {List only animations you allow. e.g. fade-in (0.4s), slide-up (0.5s)}
- {Disallow all other animation}

## Icons
- {e.g. inline SVG, strokeWidth 1.5}
- {e.g. do not wrap icons in rounded background boxes}
