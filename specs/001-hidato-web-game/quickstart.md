# Quickstart: Hidato Web Game & Puzzle Packs

**Status**: ✅ Implemented (All User Stories Complete)  
**Branch**: 001-hidato-web-game

## What You Have

- ✅ Static JSON puzzle packs in `frontend/public/packs/{packId}/`
- ✅ Next.js frontend with mobile-responsive design
- ✅ Python CLI for generating validated unique puzzles
- ✅ Four complete user stories (Daily Play, Browse Packs, CLI Generator, Mobile UX)

## Quick Start

### 1. Generate Puzzle Packs

From the repository root:

```bash
# Generate your first pack
python -m app.packgen.cli \
  --outdir frontend/public/packs/my-first-pack \
  --sizes 5,6 \
  --difficulties easy \
  --count 10 \
  --title "My First Pack" \
  --description "10 easy puzzles to get started"

# The CLI automatically updates frontend/public/packs/index.json
```

### 2. Start the Frontend

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

### 3. Test on Mobile

```bash
# Start with network access
npm run dev -- -H 0.0.0.0

# Find your IP
ipconfig  # Windows
ifconfig  # Mac/Linux

# On your phone (same WiFi): http://192.168.x.x:3000
```

## Architecture Overview

### Folder Layout
```
frontend/
├── public/packs/
│   ├── index.json              # Array of PackSummary
│   └── {packId}/
│       ├── metadata.json       # Pack metadata
│       └── puzzles/
│           ├── {puzzleId}.json # Individual puzzles
│           └── ...
├── src/
│   ├── pages/                  # Next.js routes
│   ├── components/             # React components (Grid, Palette, HUD)
│   ├── state/                  # Zustand stores (game, settings, progress)
│   └── lib/                    # Utilities (loaders, validation, persistence)
└── tests/                      # Vitest unit & integration tests

app/packgen/                    # Python CLI (repository root)
├── cli.py                      # Command-line interface
├── generate_pack.py            # Pack generation logic
├── export.py                   # JSON exporters
└── report.py                   # Statistics reporting
```

## JSON Contracts
```

## Architecture Overview
- frontend/
  - public/
    - packs/
      - classic-9x9-hard/
        - metadata.json (Pack)
        - puzzles/
          - 0001.json (Puzzle)
          - 0002.json
          - ...

## JSON Contracts

Full schemas available in `specs/001-hidato-web-game/contracts/`:
- `pack.schema.json` — Pack metadata structure
- `puzzle.schema.json` — Puzzle data structure  
- `api.openapi.yaml` — API contract (maps to static files in MVP)

### Pack metadata.json (example)
{
  "schema_version": "1.0",
  "id": "classic-9x9-hard",
  "title": "Classic 9x9 — Hard",
  "description": "Challenging 9x9 Hidato pack",
  "puzzles": ["0001", "0002"],
  "difficulty_counts": {"hard": 50},
  "size_distribution": {"9": 50},
  "created_at": "2025-11-11T00:00:00Z"
}

### Puzzle {puzzleId}.json (example)
```json
{
  "schema_version": "1.0",
  "id": "0001",
  "pack_id": "my-first-pack",
  "size": 5,
  "difficulty": "easy",
  "seed": 12345,
  "clue_count": 8,
  "max_gap": 3,
  "givens": [
    {"row": 0, "col": 0, "value": 1},
    {"row": 4, "col": 4, "value": 25}
  ],
  "solution": null
}
```

## Implementation Details

### Deterministic Daily Selection
### Deterministic Daily Selection
- Compute index from today's date using hash function
- Select puzzle by `index % pack_length`
- If puzzle unavailable, advance to next available puzzle
- No user accounts required; localStorage tracks last-played

### Local Persistence
- Game state saved to localStorage per puzzle: `hpz:v1:state:{puzzleId}`
- Settings persisted: `hpz-settings`
- Progress tracked: `hpz-progress`
- Schema versioning enables future migrations

### Pack Generation
Python CLI tool (`app/packgen/cli.py`):
- Uses existing Hidato generator engine
- Validates uniqueness and guardrails
- Exports JSON matching schemas
- Writes to `frontend/public/packs/{packId}/`
- Auto-updates `index.json` with new pack entries

### Frontend Consumption
- Static file serving via Next.js `/public` directory
- Fetches `/packs/{packId}/metadata.json`
- Loads `/packs/{packId}/puzzles/{puzzleId}.json` on demand
- No authentication or backend API required (MVP)
- Zod validation ensures runtime type safety

## CLI Usage

### Basic Commands

```bash
# Generate easy puzzles
python -m app.packgen.cli \
  --outdir frontend/public/packs/easy-collection \
  --sizes 5 \
  --difficulties easy \
  --count 20 \
  --title "Easy Collection"

# Generate mixed difficulty pack
python -m app.packgen.cli \
  --outdir frontend/public/packs/mixed-challenge \
  --sizes 6,7,8 \
  --difficulties medium,hard \
  --count 30 \
  --seed 99999 \
  --title "Mixed Challenge"

# Dry run (validate without writing)
python -m app.packgen.cli \
  --outdir frontend/public/packs/test-pack \
  --sizes 5 \
  --difficulties easy \
  --count 5 \
  --dry-run
```

### CLI Options
- `--outdir` **(required)**: Output directory path
- `--sizes` **(required)**: Comma-separated sizes (5-10)
- `--difficulties` **(required)**: easy, medium, hard, extreme
- `--count` **(required)**: Number of puzzles to generate
- `--title`: Human-readable pack title
- `--description`: Pack description text
- `--seed`: Random seed for reproducibility
- `--retries`: Max retries per puzzle (default: 5)
- `--path-mode`: Path algorithm (default: backbite_v1)
- `--dry-run`: Validate without writing files
- `--include-solution`: Include solution in output JSON

## User Stories Implemented

### ✅ US1: Play a Daily Hidato Puzzle (P1 — MVP)
**What**: Load today's puzzle, place numbers, validate, undo/redo, see completion stats

**Features**:
- SVG grid with 8-neighbor adjacency visualization
- Number palette with pencil marks for candidates
- Undo/redo stack (100 moves)
- Local persistence (auto-save)
- Completion modal with time, moves, mistakes
- Settings menu (theme, sound, pencil mode default)
- Framer Motion animations (≤150ms)

**Routes**: `/` (daily puzzle)

### ✅ US2: Browse & Select Puzzle Packs (P2)
**What**: View all packs, filter by difficulty, select pack, play puzzles sequentially

**Features**:
- Pack list with difficulty filtering
- Pack detail page showing statistics
- Progress tracking per pack
- Sequential puzzle navigation (prev/next)
- Completion badges
- Last-played puzzle restoration

**Routes**: `/packs`, `/packs/[packId]`, `/packs/[packId]/puzzles/[puzzleId]`

### ✅ US3: Generate Puzzle Packs via CLI (P3)
**What**: CLI tool to generate validated unique puzzles

**Features**:
- Python CLI with argparse interface
- Configurable sizes, difficulties, count
- Uniqueness verification via existing engine
- JSON export matching schemas
- Generation statistics report
- Auto-update `index.json`
- Reproducible via seed parameter

**Location**: `app/packgen/cli.py`

### ✅ US4: Mobile Responsive Interaction (P3)
**What**: Comfortable mobile play with adaptive UI

**Features**:
- Bottom sheet palette for mobile (<768px)
- 44px minimum touch targets (iOS guideline)
- No horizontal scroll at any viewport
- Responsive typography (h1: 1.75rem → 1.5rem)
- Orientation change support
- Breakpoints: 320px, 375px, 768px, 1024px
- Landscape layout optimizations

**Testing**: See `frontend/MOBILE_AUDIT.md`

## Development Workflow

### Adding New Packs
1. Generate pack using CLI (see commands above)
2. Pack automatically added to `index.json`
3. Refresh frontend to see new pack
4. No build step required (static JSON)

### Testing
```bash
cd frontend

# Unit & integration tests
npm test

# Tests with UI
npm run test:ui

# Coverage report
npm run test:coverage
```

### Mobile Testing
See `frontend/MOBILE_AUDIT.md` for comprehensive checklist including:
- Touch target verification (44px minimum)
- Viewport testing (320px-1024px)
- Orientation change handling
- Real device testing procedures

**Quick mobile test**:
```bash
# In frontend directory
npm run dev -- -H 0.0.0.0

# Find your IP
ipconfig  # Windows

# Access from phone: http://192.168.x.x:3000
```

## Technical Stack

### Frontend
- **Framework**: Next.js 14 (Pages Router)
- **Language**: TypeScript 5.4
- **Styling**: TailwindCSS 3.4 + custom theme
- **State**: Zustand 4.5 (with localStorage persistence)
- **Validation**: Zod 3.23
- **Animation**: Framer Motion 11.0
- **Testing**: Vitest 1.4 + Testing Library

### Backend (CLI)
- **Language**: Python 3.11 (stdlib only)
- **Generator**: Existing Hidato engine
- **Validation**: Internal uniqueness checking
- **Export**: JSON with schema validation

### Accessibility
- WCAG AA contrast ratios
- Keyboard navigation support
- Screen reader compatible
- Focus indicators (2px ring, 2px offset)
- `prefers-reduced-motion` support

## Troubleshooting

### No Packs Available
- Generate packs using CLI (see commands above)
- Verify `frontend/public/packs/index.json` exists
- Check pack folders have `metadata.json` and `puzzles/` directory

### Mobile Can't Connect
- Ensure phone and computer on same WiFi network
- Use actual IP address (not `0.0.0.0` or `localhost`)
- Check Windows Firewall allows Node.js
- Try hard refresh on phone (close/reopen browser)

### TypeScript Errors
```bash
# Clear Next.js cache
rm -rf frontend/.next

# Reinstall dependencies
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Tests Failing
```bash
# Ensure you're in frontend directory
cd frontend

# Clear test cache
npm test -- --clearCache

# Run specific test file
npm test Grid.test.tsx
```

## Next Steps

### Production Deployment
1. Build for production: `npm run build`
2. Deploy to Vercel/Netlify (static export supported)
3. Generate production packs with appropriate difficulty mix
4. Consider adding analytics (optional)

### Future Enhancements
- User accounts and cloud sync
- Leaderboards and competitions
- Hints system
- Tutorial mode
- Additional puzzle variants
- PWA support for offline play

## Additional Resources

- **Specification**: `specs/001-hidato-web-game/spec.md`
- **Technical Plan**: `specs/001-hidato-web-game/plan.md`
- **Data Model**: `specs/001-hidato-web-game/data-model.md`
- **Task Breakdown**: `specs/001-hidato-web-game/tasks.md`
- **Mobile Audit**: `frontend/MOBILE_AUDIT.md`
- **Frontend README**: `frontend/README.md`
