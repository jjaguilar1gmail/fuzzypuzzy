# Frontend: Hidato Web Game

Next.js web application for playing Hidato puzzles with mobile-first responsive design.

## Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Open http://localhost:3000
```

## Development

### Local Development
```bash
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) in your browser.

### Mobile Testing (Same WiFi Network)
```bash
# Start server accessible on local network
npm run dev -- -H 0.0.0.0
```
Then access from your phone using your computer's IP address:
```
http://192.168.x.x:3000
```
(Find your IP with `ipconfig` on Windows or `ifconfig` on Mac/Linux)

## Testing

```bash
# Run tests in watch mode
npm test

# Run tests with UI
npm run test:ui

# Generate coverage report
npm run test:coverage
```

## Build for Production

```bash
npm run build
npm start
```

## Project Structure

```
frontend/
├── src/
│   ├── pages/              # Next.js routes
│   │   ├── index.tsx       # Daily puzzle page
│   │   └── packs/          # Pack browsing routes
│   ├── components/         # React components
│   │   ├── Grid/           # SVG puzzle grid
│   │   ├── Palette/        # Number input (desktop + mobile bottom sheet)
│   │   └── HUD/            # Settings, completion modal
│   ├── domain/             # TypeScript domain models
│   ├── state/              # Zustand stores (game, settings, progress)
│   ├── lib/                # Utilities
│   │   ├── loaders/        # Pack/puzzle JSON loaders
│   │   ├── validation/     # Hidato rules validation
│   │   └── persistence.ts  # localStorage save/load
│   └── styles/             # Global CSS and theme
├── public/packs/           # Static JSON puzzle packs
├── tests/                  # Vitest unit and integration tests
└── MOBILE_AUDIT.md         # Mobile testing checklist
```

## Features

### User Stories
✅ **US1: Play Daily Puzzle (MVP)**
- SVG grid with 8-neighbor adjacency
- Number palette with pencil marks
- Undo/redo (100 moves)
- Local persistence
- Completion modal with stats
- Settings (theme, sound, pencil mode)

✅ **US2: Browse Puzzle Packs**
- Pack list with difficulty filtering
- Pack detail with statistics
- Progress tracking per pack
- Sequential puzzle navigation

✅ **US3: Generate Packs (CLI)**
- See root `/app/packgen/` for Python CLI
- Generate validated unique puzzles
- Export to JSON matching schemas
- Auto-update pack index

✅ **US4: Mobile Responsive**
- Bottom sheet palette on mobile
- 44px minimum touch targets (iOS guideline)
- No horizontal scroll
- Orientation change support
- Breakpoints: 320px, 375px, 768px, 1024px

### Accessibility
- WCAG AA contrast ratios
- Keyboard navigation
- Screen reader support
- Focus indicators (2px ring)
- Reduced motion support

## Puzzle Packs

### Pack Structure
```
public/packs/
├── index.json              # Array of PackSummary objects
└── {packId}/
    ├── metadata.json       # Pack metadata
    └── puzzles/
        ├── {puzzleId}.json # Individual puzzles
        └── ...
```

### Generate Packs (Python CLI)

From the repository root:

```bash
# Generate a pack with easy 5x5 puzzles
python -m app.packgen.cli \
  --outdir frontend/public/packs/my-pack \
  --sizes 5 \
  --difficulties easy \
  --count 10 \
  --title "My First Pack" \
  --description "10 easy 5x5 puzzles"

# Generate mixed sizes and difficulties
python -m app.packgen.cli \
  --outdir frontend/public/packs/mixed-pack \
  --sizes 5,7,9 \
  --difficulties easy,medium,hard \
  --count 30 \
  --seed 12345
```

**CLI Options:**
- `--outdir`: Output directory (required)
- `--sizes`: Comma-separated puzzle sizes 5-10 (required)
- `--difficulties`: easy, medium, hard, extreme (required)
- `--count`: Number of puzzles to generate (required)
- `--title`: Pack title
- `--description`: Pack description
- `--seed`: Random seed for reproducibility
- `--retries`: Max retries per puzzle (default: 5)
- `--path-mode`: Path generation algorithm (default: backbite_v1)
- `--dry-run`: Validate without writing files
- `--include-solution`: Include solution in output

The CLI automatically updates `public/packs/index.json` when generating packs.

## Configuration

### Environment Variables
Create `.env.local` for environment-specific settings:
```bash
# Optional: override defaults
NEXT_PUBLIC_DAILY_PACK_ID=daily-nov
```

### Pack Selection
Daily puzzles are selected deterministically from available packs using a date-based hash.

## Mobile Testing Checklist

See `MOBILE_AUDIT.md` for comprehensive mobile testing guidance including:
- Touch target verification (44px minimum)
- Viewport testing (320px-1024px)
- Orientation change handling
- Real device testing procedures

## Troubleshooting

### Packs Not Loading
- Verify pack folders exist in `public/packs/`
- Check `public/packs/index.json` lists correct pack IDs
- Generate packs using the CLI if missing
- Check browser console for 404 errors

### Mobile Connection Issues
- Ensure phone and computer are on same WiFi
- Use actual IP address, not `0.0.0.0` or `localhost`
- Check Windows Firewall allows Node.js connections
- Try hard refresh on phone (close/reopen browser)

### TypeScript Errors
```bash
# Clear Next.js cache
rm -rf .next

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

## Documentation

- **Specs**: `/specs/001-hidato-web-game/`
  - `spec.md` — Feature specification
  - `plan.md` — Technical implementation plan
  - `data-model.md` — Domain models
  - `contracts/` — JSON schemas and API contracts
  - `tasks.md` — Task breakdown

- **Python CLI**: `/app/packgen/`
  - `cli.py` — Command-line interface
  - `generate_pack.py` — Pack generation logic
  - `export.py` — JSON exporters
  - `config.example.json` — Configuration example

## License

See repository root for license information.
