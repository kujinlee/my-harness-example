# UI design guide

## Design principles
1. Feels like a professional creator tool — functional, not decorative.
2. Dark background, high-contrast text. Nothing competes with the report content.
3. One clear action per screen: URL input first, report second.

## AI slop antipatterns — do not do this
| Avoid | Reason |
|-------|------|
| backdrop-filter: blur() | Glass morphism is one of the most common AI-template tells |
| gradient-text (gradient on text) | #1 sign of AI-made SaaS landing pages |
| "Powered by AI" badges | Decoration, not functionality. No user value |
| box-shadow glow animations | Neon glow = AI slop |
| Purple / indigo brand colors | "AI = purple" cliché |
| Same rounded-2xl on every card | Uniform corners feel templated |
| Background gradient orbs (blur-3xl circles) | Ornament on every AI landing page |

## Color

### Backgrounds
| Use | Value |
|------|------|
| Page | #0a0a0a |
| Card | #141414 |

### Text
| Use | Value |
|------|------|
| Primary text | #ffffff |
| Body | #d4d4d4 (neutral-300) |
| Secondary | #a3a3a3 (neutral-400) |
| Disabled | #737373 (neutral-500) |

### Data / semantic colors
| Use | Value |
|------|------|
| Positive / success | #22c55e |
| Negative / error | #ef4444 |
| Neutral / default | #525252 |

## Components

### Card
```
rounded-md bg-[#141414] border border-neutral-800 p-6
```

### Button
```
Primary:  rounded-md bg-white text-black font-medium px-4 py-2 hover:bg-neutral-200
Disabled: bg-neutral-800 text-neutral-500 cursor-not-allowed
```

### Input fields
```
rounded-md bg-neutral-900 border border-neutral-800 px-4 py-3 text-white placeholder-neutral-500 focus:outline-none focus:border-neutral-600
```

## Layout
- Overall width: max-w-3xl
- Alignment: left-aligned by default
- Spacing: gap-4 within sections, space-y-8 between sections

## Typography
| Use | Style |
|------|--------|
| Page title | text-2xl font-semibold text-white |
| Section title | text-base font-medium text-white |
| Card label | text-xs font-medium text-neutral-400 uppercase tracking-wide |
| Body | text-sm text-neutral-300 leading-relaxed |

## Animation
- Fade-in only (opacity 0 → 1, 0.3s ease) for the report section appearing
- No other animation allowed

## Icons
- Inline SVG, strokeWidth 1.5
- Do not wrap icons in rounded background boxes
