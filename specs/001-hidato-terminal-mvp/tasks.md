# Tasks — Hidato Terminal MVP

Branch: 001-hidato-terminal-mvp
Feature: specs/001-hidato-terminal-mvp/spec.md
Plan: specs/001-hidato-terminal-mvp/plan.md

## Phase 1 — Setup

- [x] T001 Create feature docs directories if missing at specs/001-hidato-terminal-mvp/
- [x] T002 Add seed logging guideline to util/logging.py header comment
- [x] T003 Add project README section linking to spec/plan/quickstart in README.md

## Phase 2 — Foundational (blocking prerequisites)

- [x] T004 Move printing out of core: remove print_grid/pretty_print_grid from core/grid.py and replace with no-op docstrings
- [x] T005 Create ASCII renderer in io/exporters.py with function ascii_render(puzzle) and ascii_print(puzzle)
- [x] T006 Implement JSON serializer in io/serializers.py with to_json(puzzle) and from_json(data)
- [x] T007 Ensure determinism: create util/rng.py seeded RNG helper and wire through generate pipeline
- [x] T008 Contract tests: Position equality/hash in tests/test_position_contract.py
- [x] T009 Contract tests: Adjacency neighbors for 4- and 8-neighbor in tests/test_adjacency_contract.py
- [x] T010 Contract tests: Givens immutable (cannot overwrite) in tests/test_givens_immutable.py

## Phase 3 — User Story 1: Generate and View Easy Puzzle (P1)

Story goal: Generate 5x5 or 7x7 easy puzzle (serpentine path, even clues) and render in ASCII.
Independent Test: Run generate 5x5, ensure 1 and N printed among givens and formatting is correct.

- [x] T011 [P] [US1] Implement PathBuilder.build(mode="serpentine") in generate/path_builder.py
- [x] T012 [P] [US1] Implement CluePlacer.choose(mode="even") in generate/clue_placer.py
- [x] T013 [US1] Implement Validator basic checks in generate/validator.py (range, duplicates, contiguity when applicable)
- [x] T014 [US1] Implement Generator to orchestrate path → clues → validate in generate/generator.py
- [x] T015 [US1] Implement presets for 5x5 and 7x7 in app/presets.py
- [x] T016 [US1] Implement REPL command: generate in app/api.py (store current puzzle + metadata)
- [x] T017 [US1] Implement REPL command: show in app/api.py using io/exporters.ascii_print
- [x] T018 [US1] Wire JSON export metadata: seed, modes, timings in io/serializers.py

## Phase 4 — User Story 2: Make a Move with Validation (P2)

Story goal: User can place a number; system validates adjacency/range and accepts/rejects with message.
Independent Test: On a generated puzzle, valid move accepted, invalid move rejected with reason.

- [x] T019 [P] [US2] Add move validation helper in app/api.py (or app/logic) using core/Constraints + Grid
- [x] T020 [US2] Implement REPL command: move <row> <col> <value> in app/api.py
- [x] T021 [US2] Update ascii renderer to mark last move (optional visual cue) in io/exporters.py
- [x] T022 [US2] Error handling messages per spec (unsupported size, invalid move, overwrite given/blocked)

## Phase 5 — User Story 3: Hint and Auto-Solve (P3)

Story goal: Provide one-step hint and full auto-solve using consecutive logic (logic_v0).
Independent Test: Hint provides a valid next placement; auto-solve completes a valid path.

- [x] T023 [P] [US3] Implement Solver.solve(mode="logic_v0") in solve/solver.py (deterministic, no guessing, explain steps)
- [x] T024 [US3] Implement REPL command: hint in app/api.py returning one safe placement + explanation
- [x] T025 [US3] Implement REPL command: solve in app/api.py that fills puzzle copy and prints result + summary
- [x] T026 [US3] Ensure solver returns a trace of steps; print a short summary in app/api.py

## Final Phase — Polish & Cross-Cutting

- [x] T027 Add import/export commands to REPL (io/parsers.py, io/serializers.py)
- [x] T028 Add quick performance timing logs for generate/solve in util/profiling.py and output in REPL
- [x] T029 Update README quickstart with REPL examples and JSON export path
- [x] T030 Add minimal CLI entry wrapper (optional) to run REPL script

## Dependencies

- Phase 2 must complete before US1/US2/US3 implementation
- US1 → US2: US2 depends on having a generated puzzle and renderer
- US1 → US3: US3 uses same puzzle and renderer

## Parallel Execution Examples

- US1: T011 and T012 can run in parallel; T013 after T011/T012; T014 after T013; T015–T018 can proceed once T014 exists
- US2: T019 and T021 can run in parallel; T020 after T019; T022 can proceed in parallel with T020 implementation
- US3: T023 can start once T014 (Generator) is available; T024/T025/T026 follow T023

## MVP Scope Suggestion

- MVP = Phase 1–3 only (US1). This yields a presentable generator + renderer demo with presets and metadata export.

## Format Validation

All tasks follow the strict checklist format: "- [ ] T### [P] [US#] Description with file path". Story labels are present only in story phases. Parallelizable tasks are marked [P].
