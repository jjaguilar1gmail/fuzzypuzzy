# Frontend: Hidato Web Game

Next.js web application for playing Hidato puzzles.

## Setup

```bash
npm install
```

## Development

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## Testing

```bash
# Run tests in watch mode
npm test

# Run tests with UI
npm run test:ui

# Generate coverage report
npm run test:coverage
```

## Build

```bash
npm run build
npm start
```

## Project Structure

- `src/pages/` — Next.js routes
- `src/components/` — React components (Grid, Palette, HUD)
- `src/domain/` — TypeScript domain models
- `src/state/` — Zustand stores
- `src/lib/` — Utilities (loaders, validators, persistence)
- `public/packs/` — Static JSON puzzle packs
- `tests/` — Vitest unit and integration tests

## Puzzle Packs

Packs are generated via the Python CLI (`app/packgen/`) and placed in `public/packs/{packId}/`.

See `specs/001-hidato-web-game/quickstart.md` for details.
