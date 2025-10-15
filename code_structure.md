  core/                # domain model (no I/O, pure logic)
    cell.py
    position.py
    grid.py
    puzzle.py
    constraints.py
    adjacency.py
  solve/               # deterministic solver & difficulty analysis
    solver.py
    strategies.py
    search.py
    uniqueness.py
    difficulty.py
  generate/            # puzzle generation pipeline
    path_builder.py
    shape_factory.py
    clue_placer.py
    generator.py
    symmetry.py
    validator.py
  io/                  # adapters; no business logic
    serializers.py     # JSON/YAML
    exporters.py       # text/ASCII, SVG/PNG, PDF hooks
    parsers.py
  util/
    rng.py
    profiling.py
    logging.py
    config.py
  app/
    api.py             # high-level façade for CLI/GUI
    presets.py         # sizes/difficulties
    telemetry.py       # optional: events for debugging/UX
  tests/               # unit & property tests