# Numeric Mode Implementation Tasks

1. **Add navigation affordance on the main daily page.** (done)
   - Floating `#` button now renders inside `frontend/src/pages/index.tsx` and links to `/numeric`.
   - Styling for the floating action button lives in `frontend/src/styles/theme.css` via the `.numeric-mode-fab` class.

2. **Create the numeric-only page and route.** (done)
   - New page in `frontend/src/pages/numeric.tsx` mirrors the daily layout and reuses the shared stores/components.
   - Includes inline back link in the header plus a floating FAB to return to `/`.

3. **Force numeric symbol set and limited options.** (done)
   - Numeric page locks the difficulty to `classic`, renders only the 5x5/6x6/7x7 buttons, and injects the `numeric` symbol set via the new `GuidedGrid` prop.
   - Preferences persist in `hpz:numeric:selection`, keeping the default daily state untouched.

4. **Add return navigation from the numeric page.** (done)
   - Header link and a dedicated floating FAB both route back to `/` for redundancy.

5. **Adjust shared components/configuration if needed.** (done)
   - `GuidedGrid` now accepts an optional `symbolSetId`, letting numeric mode swap to the numeric glyphs without affecting other routes.
   - Numeric mode keeps its own preference key/state so store analytics and persistence remain consistent.

6. **Finalize styling and responsive polish.** (done)
   - `.numeric-mode-fab` styles live in `frontend/src/styles/theme.css`, anchoring the Symbol Flow shortcut.
   - Layout changes reuse the existing responsive wrappers; visual verification still recommended in browser.

## Follow-up Adjustments

1. **Allow Number Flow to use mixed difficulties with real size options.** (done)
   - `getDailyPuzzle` now accepts optional overrides so numeric mode can request 5x5/6x6/7x7 puzzles from either difficulty.
   - Numeric mode persists progress under a `-numeric` suffix to avoid colliding with Symbol Flow saves.

2. **Rename experiences for clarity.** (done)
   - Main daily page now titles itself “Symbol Flow,” while the numeric route displays “Number Flow.”

3. **Reposition navigation affordances.** (done)
   - Removed the overlapping inline/back buttons; a single arrow button now sits to the left of the Number Flow title, eliminating conflicts with other controls.
