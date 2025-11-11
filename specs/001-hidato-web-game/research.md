# Research: Hidato Web Game & Puzzle Pack Generator

Date: 2025-11-11  
Branch: 001-hidato-web-game

## Decisions and Rationale

### Frontend Stack (React + Next.js + TypeScript)
- Decision: Use Next.js (React, TS) with TailwindCSS and Framer Motion.
- Rationale: SEO-friendly SSR/SSG, rapid development, strong ecosystem, PWA path.
- Alternatives considered: Vite + React Router (faster dev server but less built-in routing/SSR), SvelteKit (lean, but team familiarity lower), Vanilla SPA (SEO and DX trade-offs).

### Rendering (SVG for grid; Canvas later if needed)
- Decision: SVG for crisp, scalable grid and cell interactions.
- Rationale: Accessibility and styling ease; Canvas reserved for advanced effects or very large boards.
- Alternatives: Canvas now (premature complexity), WebGL (overkill).

### State & Validation (Zustand + Zod)
- Decision: Zustand for lightweight state; Zod for runtime schema checks on packs.
- Rationale: Minimal boilerplate, strong typing, runtime safety.
- Alternatives: Redux Toolkit (heavier), React Context only (less modular for growing state).

### Data Delivery (Static JSON packs)
- Decision: Pre-generate JSON packs and serve from `/public/packs`.
- Rationale: Instant load, no backend roundtrips; aligns with static hosting.
- Alternatives: Live API (FastAPI) — deferred for simplicity.

### Daily Puzzle Selection
- Decision: Deterministic seed-of-day mapping to pre-generated pool; wrap to next available if missing.
- Alternatives: Random non-repeat (less reproducible), Scheduled calendar (more content ops overhead).

### Accounts & Sharing
- Decision: Exclude accounts for MVP; defer sharing feature.
- Rationale: Keep scope focused on gameplay quality and content pipeline.
- Stack recap (for agent context): Next.js 15 (React 19), TypeScript, TailwindCSS, Framer Motion (effects only), Zustand (state), Zod (validation), SVG grid rendering, static JSON packs served from public/packs. Python CLI generator produces pack metadata + puzzle JSON conforming to schemas (draft-07). Deterministic daily puzzle selection via date-hash modulo. No server uniqueness computation in MVP.

## Open Questions Resolved
- None remaining for MVP after spec clarifications.

## Best Practices Notes
- Accessibility: Maintain WCAG AA contrast; focus states visible; keyboard nav for palette and grid.
- Performance: Keep animations ≤150ms; only re-render changed cells; memoize cell components; lazy-load packs index.
- Mobile UX: Bottom-sheet palette, 40px touch targets, avoid horizontal scroll; handle rotation.

