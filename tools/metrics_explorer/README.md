# Metrics Explorer

Interactive Streamlit app for visualizing the per‑puzzle metrics emitted by the
pack generator.

## Setup

```
python -m venv .venv
.venv\Scripts\activate  # or source .venv/bin/activate on mac/linux
pip install -r tools/metrics_explorer/requirements.txt
```

## Usage

```
streamlit run tools/metrics_explorer/app.py
```

When the app loads, provide either the path to a generated pack directory
(for example `playground_outputs/difficulty_5x5_metrics`) or the parent folder
that contains multiple pack outputs (`playground_outputs`). If you supply a
parent folder, the app will list the detected packs so you can select one.
The explorer will then scan the puzzles in that pack, normalize their metric
dictionaries, and expose them as a data
table you can slice, filter, and visualize.

Features include:

- Quick summary of the selected pack (title, size/difficulty distribution).
- Dynamic filtering by size, difficulty, and arbitrary numeric metric ranges.
- 2D/3D scatter plots, histograms, and box plots with configurable axes,
  coloring, and sizing.
- Built-in metric guide and analysis tips to help interpret the telemetry.
- Scatter plots support in-app point picking when the optional
  `streamlit-plotly-events` dependency is installed (see requirements.txt);
  otherwise they fall back to a dropdown selector.
- Download of the normalized metrics as CSV for additional analysis.

> **Tip:** If the interactive dependency is unavailable, the table and dropdown
> selectors still let you inspect specific puzzles.

The tool is intended for developers and puzzle designers; it lives under
`tools/` so it does not interfere with the production game frontend.
