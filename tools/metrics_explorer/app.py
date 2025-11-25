"""Streamlit app for exploring pack-level puzzle metrics."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Iterable, Tuple

import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(page_title="Pack Metrics Explorer", layout="wide")

METRIC_GUIDE = {
    "timings_ms.total": "End-to-end generation time per puzzle (ms). Higher values often correlate with more pruning/solver work.",
    "timings_ms.solve": "Deterministic solve phase time (if tracked). Spikes can point to ambiguous regions.",
    "solver.clue_density": "Fraction of cells given at start. Lower densities typically mean harder puzzles.",
    "solver.logic_ratio": "Share of steps solvable without search. Lower ratios imply more guesswork.",
    "solver.nodes": "Search nodes explored by the deterministic solver — proxy for branching complexity.",
    "solver.depth": "Max search depth reached; deeper trees often mean higher difficulty.",
    "structure.givens.row_counts": "Distribution of givens per row. Uneven distributions can create bottlenecks.",
    "structure.anchors.density": "Anchors per path length. Sparse anchors may increase ambiguity.",
    "structure.branching.average_branching_factor": "Nodes/depth — rough average branching factor during solve.",
    "structure.branching.search_ratio": "1 - logic_ratio. Helps differentiate logic- vs search-heavy puzzles.",
}

ANALYSIS_TIPS = [
    "Plot `solver.clue_density` vs `solver.depth` to see which puzzles depart from the designed difficulty band.",
    "Color a scatter of `structure.branching.average_branching_factor` vs `timings_ms.total` by `difficulty` to catch outliers.",
    "Filter hard puzzles and inspect `structure.anchors.gaps.avg`; long gaps may highlight why certain puzzles feel brutal.",
    "Use the histogram of `timings_ms.total` to understand the spread of generator effort and spot multi-modal distributions.",
    "Export the CSV and compute correlations between `clue_density`, `logic_ratio`, and player solve telemetry once available.",
]


def flatten_dict(data: Dict, prefix: str = "", sep: str = ".") -> Dict[str, object]:
    """Flatten nested dicts using dot-notation keys."""
    items = []
    for key, value in data.items():
        new_key = f"{prefix}{sep}{key}" if prefix else key
        if isinstance(value, dict):
            items.extend(flatten_dict(value, new_key, sep=sep).items())
        else:
            items.append((new_key, value))
    return dict(items)


def _extract_record(puzzle_data: Dict) -> Dict:
    """Extract a single row of metrics from a puzzle JSON blob."""
    record = {
        "puzzle_id": puzzle_data.get("id"),
        "pack_id": puzzle_data.get("pack_id"),
        "size": puzzle_data.get("size"),
        "difficulty": puzzle_data.get("difficulty"),
        "clue_count": puzzle_data.get("clue_count"),
        "seed": puzzle_data.get("seed"),
    }

    metrics_block = puzzle_data.get("metrics", {})
    record.update(flatten_dict(metrics_block))
    return record


@st.cache_data(show_spinner=True)
def load_pack(pack_dir: str) -> Tuple[Dict, pd.DataFrame]:
    """Load pack metadata and puzzle metrics into a DataFrame."""
    pack_path = Path(pack_dir)
    metadata_file = pack_path / "metadata.json"
    puzzles_dir = pack_path / "puzzles"

    if not metadata_file.exists():
        raise FileNotFoundError(f"metadata.json not found under {pack_path}")
    if not puzzles_dir.exists():
        raise FileNotFoundError(f"puzzles/ directory not found under {pack_path}")

    with metadata_file.open("r", encoding="utf-8") as f:
        metadata = json.load(f)

    rows = []
    for puzzle_file in sorted(puzzles_dir.glob("*.json")):
        with puzzle_file.open("r", encoding="utf-8") as f:
            rows.append(_extract_record(json.load(f)))

    if not rows:
        raise ValueError(f"No puzzles found in {puzzles_dir}")

    frame = pd.DataFrame(rows)
    numeric_cols = frame.select_dtypes(include=["number"]).columns
    frame[numeric_cols] = frame[numeric_cols].apply(pd.to_numeric, errors="ignore")

    return metadata, frame


def sidebar_filters(df: pd.DataFrame) -> pd.DataFrame:
    """Render sidebar controls and return filtered DataFrame."""
    st.sidebar.header("Filters")

    sizes = sorted(df["size"].dropna().unique())
    difficulties = sorted(df["difficulty"].dropna().unique())

    selected_sizes = st.sidebar.multiselect("Sizes", sizes, default=sizes)
    selected_difficulties = st.sidebar.multiselect(
        "Difficulties", difficulties, default=difficulties
    )

    filtered = df[df["size"].isin(selected_sizes) & df["difficulty"].isin(selected_difficulties)]

    numeric_cols = sorted(filtered.select_dtypes(include=["number"]).columns)
    numeric_filter_column = st.sidebar.selectbox(
        "Numeric filter column", ["(none)"] + numeric_cols
    )
    if numeric_filter_column != "(none)":
        col_min = float(filtered[numeric_filter_column].min())
        col_max = float(filtered[numeric_filter_column].max())
        min_val, max_val = st.sidebar.slider(
            "Range",
            min_value=col_min,
            max_value=col_max,
            value=(col_min, col_max),
        )
        filtered = filtered[
            (filtered[numeric_filter_column] >= min_val)
            & (filtered[numeric_filter_column] <= max_val)
        ]

    return filtered


def choose_chart(df: pd.DataFrame):
    """Render chart controls and display a plotly visualization."""
    st.subheader("Visualization")
    if df.empty:
        st.info("No puzzles match the current filters.")
        return

    numeric_cols = sorted(df.select_dtypes(include=["number"]).columns)
    all_cols = df.columns.tolist()

    chart_type = st.selectbox(
        "Chart type",
        ["Scatter (2D)", "Scatter (3D)", "Histogram", "Box"],
    )

    hover_fields = ["puzzle_id", "size", "difficulty", "clue_count"]

    if chart_type == "Scatter (2D)":
        if len(numeric_cols) < 2:
            st.warning("Need at least two numeric metrics for scatter plot.")
            return
        x_col = st.selectbox("X axis", numeric_cols, index=0)
        y_col = st.selectbox("Y axis", numeric_cols, index=min(1, len(numeric_cols) - 1))
        color_col = st.selectbox("Color", ["(none)"] + all_cols, index=all_cols.index("difficulty") + 1 if "difficulty" in all_cols else 0)
        size_col = st.selectbox("Size", ["(none)"] + numeric_cols, index=0)
        fig = px.scatter(
            df,
            x=x_col,
            y=y_col,
            color=None if color_col == "(none)" else color_col,
            size=None if size_col == "(none)" else size_col,
            hover_data=hover_fields,
        )
        st.plotly_chart(fig, use_container_width=True)
    elif chart_type == "Scatter (3D)":
        if len(numeric_cols) < 3:
            st.warning("Need at least three numeric metrics for 3D scatter.")
            return
        x_col = st.selectbox("X axis", numeric_cols, index=0, key="3d_x")
        y_col = st.selectbox("Y axis", numeric_cols, index=1, key="3d_y")
        z_col = st.selectbox("Z axis", numeric_cols, index=2, key="3d_z")
        color_col = st.selectbox("Color", ["(none)"] + all_cols, key="3d_color")
        fig = px.scatter_3d(
            df,
            x=x_col,
            y=y_col,
            z=z_col,
            color=None if color_col == "(none)" else color_col,
            hover_data=hover_fields,
        )
        st.plotly_chart(fig, use_container_width=True)
    elif chart_type == "Histogram":
        metric = st.selectbox("Metric", numeric_cols)
        color_col = st.selectbox("Color", ["(none)"] + all_cols, key="hist_color")
        fig = px.histogram(
            df,
            x=metric,
            color=None if color_col == "(none)" else color_col,
            nbins=25,
        )
        st.plotly_chart(fig, use_container_width=True)
    elif chart_type == "Box":
        metric = st.selectbox("Metric", numeric_cols, key="box_metric")
        group = st.selectbox(
            "Group by", ["difficulty", "size"] + [c for c in all_cols if c not in ("difficulty", "size")]
        )
        fig = px.box(
            df,
            x=group,
            y=metric,
            points="all",
        )
        st.plotly_chart(fig, use_container_width=True)


def pack_summary(metadata: Dict, df: pd.DataFrame):
    """Display summary statistics for the selected pack."""
    st.sidebar.markdown("---")
    st.sidebar.subheader("Pack summary")
    st.sidebar.write(f"Title: **{metadata.get('title', metadata.get('id'))}**")
    st.sidebar.write(f"Puzzles: **{len(df)}**")
    st.sidebar.write("Difficulty counts:")
    st.sidebar.json(metadata.get("difficulty_counts", {}))
    st.sidebar.write("Size distribution:")
    st.sidebar.json(metadata.get("size_distribution", {}))


def render_metric_guide():
    """Show reference information for available metrics."""
    with st.expander("Metric guide & analysis tips", expanded=False):
        st.markdown("**Core metrics**")
        for key, description in METRIC_GUIDE.items():
            st.markdown(f"- **`{key}`** — {description}")
        st.markdown("**Analysis ideas**")
        for tip in ANALYSIS_TIPS:
            st.markdown(f"- {tip}")


def discover_packs(base_path: Path) -> list[Path]:
    """Return subdirectories that look like pack outputs."""
    if not base_path.exists() or not base_path.is_dir():
        return []
    return sorted(
        p for p in base_path.iterdir() if p.is_dir() and (p / "metadata.json").exists()
    )


def main():
    st.title("Pack Metrics Explorer")
    st.caption("Visualize the per-puzzle metrics captured during pack generation.")

    default_path = "playground_outputs"
    typed_path = st.sidebar.text_input(
        "Pack directory or parent folder",
        value=default_path,
        help="Either a pack folder (with metadata.json) or a directory containing pack folders.",
    )

    if not typed_path:
        st.info("Provide a pack directory to begin.")
        return

    base_path = Path(typed_path).expanduser()
    pack_path = base_path
    detected_packs = discover_packs(base_path)

    if detected_packs and not (base_path / "metadata.json").exists():
        option_labels = ["(use typed path)"] + [p.name for p in detected_packs]
        selection = st.sidebar.selectbox(
            "Detected packs", option_labels, help="Select a discovered pack under the provided folder."
        )
        if selection != "(use typed path)":
            pack_path = next(p for p in detected_packs if p.name == selection)
            st.sidebar.info(f"Using detected pack: {pack_path}")
    else:
        pack_path = base_path

    try:
        metadata, df = load_pack(str(pack_path))
    except Exception as exc:
        st.error(f"Could not load pack: {exc}")
        if detected_packs:
            st.info("Choose one of the detected packs from the dropdown above.")
        return

    pack_summary(metadata, df)
    render_metric_guide()

    filtered = sidebar_filters(df)
    choose_chart(filtered)

    st.subheader("Data")
    st.dataframe(filtered, use_container_width=True)
    csv = filtered.to_csv(index=False).encode("utf-8")
    st.download_button("Download CSV", data=csv, file_name="puzzle_metrics.csv", mime="text/csv")


if __name__ == "__main__":
    main()
