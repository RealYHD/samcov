"""Coverage plotting utilities.

Generates strip-style SVG plots showing threshold regions from per-position
coverage data.
"""
import logging
from typing import Iterable
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

logger = logging.getLogger(__name__)

# Color-blind-friendly warm palette (red → orange → gold → green → blue)
_THRESHOLD_COLORS = ["#e41a1c", "#fd8d3c", "#fecc5c", "#41ab5d", "#2c7fb8"]


def _mean_std_at_positions(
    coverage_maps: dict[str, dict[int, int]], positions: list[int]
) -> tuple[list[float], list[float]]:
    """Compute mean and sample-standard-deviation per position."""
    mean_y: list[float] = []
    std_y: list[float] = []
    for p in positions:
        values = np.array([cov_map.get(p, 0) for cov_map in coverage_maps.values()], dtype=float)
        mean_y.append(float(np.mean(values)))
        if len(values) > 1:
            std_y.append(float(np.std(values, ddof=1)))
        else:
            std_y.append(0.0)
    return mean_y, std_y


def _below_segments(mean_y: list[float], threshold: int):
    """Return list of (start_index, width_in_positions) where mean < threshold."""
    segments: list[tuple[int, int]] = []
    in_seg = False
    seg_start = 0
    for idx, val in enumerate(mean_y):
        if val < threshold and not in_seg:
            seg_start = idx
            in_seg = True
        elif val >= threshold and in_seg:
            segments.append((seg_start, idx - seg_start))
            in_seg = False
    if in_seg:
        segments.append((seg_start, len(mean_y) - seg_start))
    return segments


def _above_segments(mean_y: list[float], threshold: int):
    """Return list of (start_index, width_in_positions) where mean > threshold."""
    segments: list[tuple[int, int]] = []
    in_seg = False
    seg_start = 0
    for idx, val in enumerate(mean_y):
        if val > threshold and not in_seg:
            seg_start = idx
            in_seg = True
        elif val <= threshold and in_seg:
            segments.append((seg_start, idx - seg_start))
            in_seg = False
    if in_seg:
        segments.append((seg_start, len(mean_y) - seg_start))
    return segments


def _draw_tracks(
    ax,
    mean_y: list[float],
    below: list[int] | None = None,
    above: list[int] | None = None,
    x: list[int] | None = None,
    track_height: float = 6.0,
    gap: float = 1.5,
):
    """Draw color-coded threshold tracks: below in negative y, above in positive y.

    Parameters
    ----------
    ax
        Matplotlib Axes instance.
    mean_y
        Mean coverage per position.
    below
        Depth thresholds for below-threshold tracks (ascending preferred).
    above
        Depth thresholds for above-threshold tracks (ascending preferred).
    x
        Position labels.
    track_height
        Height of each track in data units.
    gap
        Vertical gap between adjacent tracks / axis.
    """
    below = below or []
    above = above or []
    if not below and not above:
        return

    n_below = len(below)
    n_above = len(above)
    total_below_h = n_below * track_height + (n_below + 1) * gap if n_below else 0
    total_above_h = n_above * track_height + (n_above + 1) * gap if n_above else 0
    ax.set_ylim(-total_below_h, total_above_h)
    if x:
        ax.set_xlim(min(x), max(x))

    # Below tracks (negative y, closest to axis first)
    for i, thresh in enumerate(below):
        segs = _below_segments(mean_y, thresh)
        if not segs:
            continue
        color = _THRESHOLD_COLORS[i % len(_THRESHOLD_COLORS)]
        y_base = -(i + 1) * (track_height + gap)
        bar_h = track_height
        xr = [(x[s], max(1, w)) for s, w in segs] if x else segs
        ax.broken_barh(xr, (y_base, bar_h), facecolors=color, edgecolors="none", alpha=0.9, linewidth=0)

    # Above tracks (positive y, closest to axis first)
    for i, thresh in enumerate(above):
        segs = _above_segments(mean_y, thresh)
        if not segs:
            continue
        color = _THRESHOLD_COLORS[i % len(_THRESHOLD_COLORS)]
        y_base = gap + i * (track_height + gap)
        bar_h = track_height
        xr = [(x[s], max(1, w)) for s, w in segs] if x else segs
        ax.broken_barh(xr, (y_base, bar_h), facecolors=color, edgecolors="none", alpha=0.9, linewidth=0)

    # Phantom handles for legend
    handles = []
    for i, thresh in enumerate(below):
        color = _THRESHOLD_COLORS[i % len(_THRESHOLD_COLORS)]
        handle, = ax.plot([], [], color=color, linewidth=3, label=f"<{thresh}×")
        handles.append(handle)
    for i, thresh in enumerate(above):
        color = _THRESHOLD_COLORS[i % len(_THRESHOLD_COLORS)]
        handle, = ax.plot([], [], color=color, linewidth=3, label=f">{thresh}×")
        handles.append(handle)
    if handles:
        ax.legend(loc="upper right", fontsize="small")


def _style_strip_axes(ax):
    """Remove y-axis and spines; keep only x-axis and title area."""
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.set_yticks([])
    ax.set_ylabel("")


def plot_coverage(
    coverage_maps: dict[str, dict[int, int]],
    max_length: int,
    output_path: str,
    start_pos: int = 0,
    chrom_name: str | None = None,
    below: list[int] | None = None,
    above: list[int] | None = None,
):
    """Render a strip-style SVG showing threshold regions only.

    Parameters
    ----------
    coverage_maps
        ``sample_name → {position: depth}``.
    max_length
        Number of reference positions.
    output_path
        Where to save the SVG.
    start_pos
        Offset added to each x-axis label.
    chrom_name
        Subtitle / label for the contig being plotted.
    below
        Depth thresholds. For each threshold a colored track is drawn
        showing regions where mean coverage is strictly below that value.
    above
        Depth thresholds. For each threshold a colored track is drawn
        showing regions where mean coverage is strictly above that value.
    """
    logger.info("Generating coverage strip plot → %s", output_path)

    positions = list(range(max_length))
    x = [p + start_pos for p in positions]
    mean_y, _ = _mean_std_at_positions(coverage_maps, positions)

    n_tracks = (len(below) if below else 0) + (len(above) if above else 0)
    fig, ax = plt.subplots(figsize=(12, 1.5 + 0.4 * n_tracks))

    if below or above:
        _draw_tracks(ax, mean_y, below=below, above=above, x=x)

    ax.set_xlabel("Base position")
    title = "Coverage threshold regions"
    if chrom_name:
        title += f" — {chrom_name}"
    ax.set_title(title)
    _style_strip_axes(ax)

    fig.tight_layout()
    fig.savefig(output_path, format="svg")
    plt.close(fig)
    logger.info("Plot saved successfully.")


def plot_all(
    coverage_maps: dict[str, dict[int, int]],
    max_length: int,
    output_path: str,
    start_pos: int = 0,
    below: list[int] | None = None,
    above: list[int] | None = None,
):
    """Produce a single SVG with one strip panel per reference.

    ``coverage_maps`` keys are expected to be ``sample/reference``.
    """
    refs: dict[str, dict[str, dict[int, int]]] = {}
    for key, cov_map in coverage_maps.items():  # type: ignore[assignment]
        if "/" in key:
            sample, ref = key.split("/", 1)
        else:
            sample, ref = key, "reference"
        refs.setdefault(ref, {})[sample] = cov_map

    n = len(refs)
    if n == 0:
        logger.warning("No coverage data to plot.")
        return

    n_tracks = (len(below) if below else 0) + (len(above) if above else 0)
    strip_h = 1.5 + 0.4 * n_tracks
    fig, axes = plt.subplots(n, 1, figsize=(12, strip_h * n), sharex=False)
    if n == 1:
        axes = [axes]

    for ax, (ref_name, sample_maps) in zip(axes, refs.items()):
        positions = list(range(max_length))
        x = [p + start_pos for p in positions]
        mean_y, _ = _mean_std_at_positions(sample_maps, positions)

        if below or above:
            _draw_tracks(ax, mean_y, below=below, above=above, x=x)

        ax.set_title(ref_name)
        ax.set_xlabel("Base position")
        _style_strip_axes(ax)

    fig.tight_layout()
    fig.savefig(output_path, format="svg")
    plt.close(fig)
    logger.info("Multi-reference plot saved → %s", output_path)
