# Color Control Constitution

## Purpose
This document ensures every new feature adheres to a unified visual language, keeps the game accessible, and prevents palette drift. Treat it as the binding policy for color work.

## Core Principles
1. **Single Source of Truth** - `frontend/src/styles/theme.css` defines every color token (light + dark). If it is not there, it does not exist.
2. **Semantic Naming** - Tokens describe roles (e.g., `--color-grid-target`) rather than literal hues. New tokens must follow that pattern so downstream code never relies on accidental color meaning.
3. **Mode Parity** - Any token introduced for light mode must have a dark-mode counterpart in the same file. Never ship a color update that leaves dark mode using stale values.
4. **Accessibility First** - Minimum contrast is WCAG AA (4.5:1 for body text, 3:1 for large text/UI affordances). Validate every new token against both surfaces it appears on.
5. **Composable Layers** - Tailwind utilities (`frontend/tailwind.config.js`) and TS helpers (`frontend/src/styles/colorTokens.ts`) only map existing tokens. They must never introduce raw color literals.

## Authoritative References
- **Tokens**: `frontend/src/styles/theme.css` (default, `prefers-color-scheme: dark`, `[data-theme="dark"]`).
- **Utility Mapping**: `frontend/tailwind.config.js` exposes tokens to classes (`bg-surface`, `text-copy`, etc.).
- **Runtime Access**: `frontend/src/styles/colorTokens.ts` provides `cssVar()` plus palettes for SVG/Canvas/JS-driven colors.
- **Components**: All React/Tailwind code must consume colors via the utilities or palettes above. Inline hex values are forbidden.

## Workflow for Adding or Changing Colors
1. Define or update the token in `theme.css` with light and dark values.
2. Map the token (if needed) inside `tailwind.config.js` or `colorTokens.ts` using semantic naming.
3. Consume the token via Tailwind class or palette helper. No direct `rgb()` literals.
4. Verify both modes by running the app in light and dark (or toggling `[data-theme]`).
5. Document usage in the PR description if the token is new, including rationale and contrast checks.

## Dos and Don'ts
- Reuse existing tokens whenever possible before inventing new names.
- Add comments in `theme.css` only when intent is non-obvious (for example, temporary event colors).
- Do not set `style={{ color: '#fff' }}` anywhere. Use `text-copy`, `text-primary`, etc.
- Do not import Tailwind color helpers into TS; always go through `colorTokens.ts`.
- Do not extend Tailwind with arbitrary brand palettes; every entry must wrap a CSS variable.

## Palette Extension Checklist
- [ ] Name expresses semantic role (state, hierarchy, interaction).
- [ ] Token defined for all theme contexts.
- [ ] Added to Tailwind config or TS palette (if needed) with matching semantics.
- [ ] Contrast tested against each intended background.
- [ ] Screenshots or theme toggle verified locally.

## Maintenance Rules
- Remove unused tokens when features are deleted to keep the palette lean.
- When refactoring, consolidate duplicate semantics under one token and update all consumers.
- If an exception is absolutely necessary (for example, a third-party library requiring inline color), wrap it in a reusable component that still reads from `cssVar()` so the exception remains compliant.

Adhering to this constitution keeps Number Flow visually consistent, accessible, and easy to theme, and every contributor and AI agent is expected to comply.
