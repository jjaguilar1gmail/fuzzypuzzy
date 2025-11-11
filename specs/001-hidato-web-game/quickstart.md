# Quickstart: Hidato Web Game & Puzzle Packs

Status: Planning artifacts (MVP design)
Branch: 001-hidato-web-game

## What you'll have
- Static JSON puzzle packs in `frontend/public/packs/{packId}`
- A Next.js frontend that reads those JSON files at runtime
- A Python CLI (to be implemented) that generates packs using the existing engine

## Folder layout (planned)
- frontend/
  - public/
    - packs/
      - classic-9x9-hard/
        - metadata.json (Pack)
        - puzzles/
          - 0001.json (Puzzle)
          - 0002.json
          - ...

## JSON contracts
- See `specs/001-hidato-web-game/contracts/` for:
  - `pack.schema.json`
  - `puzzle.schema.json`
  - `api.openapi.yaml` (reference endpoints that map to static files in MVP)

### Pack metadata.json example (abbreviated)
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

### Puzzle 0001.json example (abbreviated)
{
  "schema_version": "1.0",
  "id": "0001",
  "pack_id": "classic-9x9-hard",
  "size": 9,
  "difficulty": "hard",
  "seed": 42,
  "clue_count": 31,
  "max_gap": 11,
  "givens": [
    {"row": 0, "col": 0, "value": 1},
    {"row": 8, "col": 8, "value": 81}
  ],
  "solution": null
}

## Deterministic daily selection
- Compute an index from today’s date, then pick a puzzle id by modulo the pack length.
- If that id is missing (e.g., filtered), advance to the next available id.
- Do not track accounts; persist last-played locally.

## Local persistence
- Save `PlayerState` per puzzle to localStorage using a namespaced key, e.g., `hpz:v1:state:{packId}:{puzzleId}`.
- Include `schema_version` to enable future migrations.

## Generation (to be implemented)
- A small Python CLI will:
  - Use the existing generator to produce unique puzzles
  - Validate against guardrails
  - Emit JSON conforming to the schemas here
  - Write metadata.json and puzzle files under `frontend/public/packs/{packId}/`

## Frontend consumption
- Frontend will fetch `/packs/{packId}/metadata.json` and each `/packs/{packId}/puzzles/{puzzleId}.json`.
- No authentication or accounts in MVP; all assets are static under `public/`.

## Notes
- For difficulty labels and size bounds, follow the schemas exactly.
- `solution` is optional in client bundles; the engine can validate without exposing it.
