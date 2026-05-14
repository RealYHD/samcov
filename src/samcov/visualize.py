"""Coverage plotting utilities.

Generates vector line plots (SVG) from per-position coverage data.
"""
import logging
from typing import Iterable
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

logger = logging.getLogger(__name__)

# Color-blind-friendly warm palette (red → orange → gold → green → blue)
_THRESHOLD_COLORS = ["#e41a1c", "#fd8d3c", "#fecc5c", "#41ab5d", "#2c7fb8"]


def _threshold_segments(total_y: list[int], threshold: int):
    """Return list of (start_index, width_in_positions) where total < threshold."""
    segments: list[tuple[int, int]] = []
    in_seg = False
    seg_start = 0
    for idx, val in enumerate(total_y):
        if val < threshold and not in_seg:
            seg_start = idx
            in_seg = True
        elif val >= threshold and in_seg:
            segments.append((seg_start, idx - seg_start))
            in_seg = False
    if in_seg:
        segments.append((seg_start, len(total_y) - seg_start))
    return segments


def _draw_threshold_tracks(
    ax,
    total_y: list[int],
    thresholds: list[int],
    x: list[int],
    track_height: float = 0.10,
    gap: float = 0.03,
):
    """Draw thin color-coded threshold tracks below the x-axis.

    Parameters
    ----------
    ax
        Matplotlib Axes instance.
    total_y
        Total coverage per position.
    thresholds
        Depth thresholds (ascending preferred).
    x
        Position labels.
    track_height
        Height of each individual track in data units.
    gap
        Vertical gap between adjacent tracks.
    """
    if not thresholds:
        return

    y_min, y_max = ax.get_ylim()
    n = len(thresholds)
    total_h = n * track_height + (n + 1) * gap
    ax.set_ylim(bottom=-total_h)

    for i, thresh in enumerate(thresholds):
        segs = _threshold_segments(total_y, thresh)
        if not segs:
            continue
        color = _THRESHOLD_COLORS[i % len(_THRESHOLD_COLORS)]
        # bottom of this track
        y_base = -(i + 1) * (track_height + gap)
        bar_h = track_height
        xr = [(x[s], max(1, w)) for s, w in segs]
        ax.broken_barh(xr, (y_base, bar_h), facecolors=color, edgecolors="none", alpha=0.9, linewidth=0)

    # Phantom handles for legend so the user knows what each color means
    for i, thresh in enumerate(thresholds):
        color = _THRESHOLD_COLORS[i % len(_THRESHOLD_COLORS)]
        ax.plot([], [], color=color, linewidth=3, label=f"<{thresh}×")


def plot_coverage(
    coverage_maps: dict[str, dict[int, int]],
    max_length: int,
    output_path: str,
    start_pos: int = 0,
    sample_names: Iterable[str] | None = None,
    chrom_name: str | None = None,
    total_only: bool = False,
    thresholds: list[int] | None = None,
    show_total: bool = True,
):
    """Render a line-plot SVG of coverage across positions.

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
    sample_names
        If given, only these sample traces are drawn (still includes total).
    chrom_name
        Subtitle / label for the contig being plotted.
    total_only
        When ``True``, suppress per-sample lines and draw only the total.
    thresholds
        List of depth thresholds. For each threshold a colored track is drawn
        below the x-axis showing regions where total coverage is strictly
        below that value.
    show_total
        When ``False``, suppress the black total-coverage line.
    """
    logger.info("Generating coverage plot → %s", output_path)

    names = list(coverage_maps.keys())
    if sample_names is not None:
        names = [n for n in sample_names if n in coverage_maps]

    positions = list(range(max_length))
    x = [p + start_pos for p in positions]

    fig, ax = plt.subplots(figsize=(12, 6))

    # per-sample traces
    if not total_only:
        for name in names:
            cov_map = coverage_maps[name]
            y = [cov_map.get(p, 0) for p in positions]
            ax.plot(x, y, linewidth=0.8, alpha=0.7, label=name)

    # total coverage trace
    total_y: list[int] = []
    for p in positions:
        total = sum(cov_map.get(p, 0) for cov_map in coverage_maps.values())
        total_y.append(total)
    if show_total:
        ax.plot(x, total_y, linewidth=1.5, color="black", label="total coverage")

    # threshold tracks below x-axis
    if thresholds:
        _draw_threshold_tracks(ax, total_y, thresholds, x)

    ax.set_xlabel("Base position")
    ax.set_ylabel("Coverage depth")
    title = "Coverage per base position"
    if chrom_name:
        title += f" — {chrom_name}"
    ax.set_title(title)
    ax.legend(loc="upper right", fontsize="small")
    ax.margins(x=0.01)

    fig.tight_layout()
    fig.savefig(output_path, format="svg")
    plt.close(fig)
    logger.info("Plot saved successfully.")


def plot_all(
    coverage_maps: dict[str, dict[int, int]],
    max_length: int,
    output_path: str,
    start_pos: int = 0,
    thresholds: list[int] | None = None,
    show_total: bool = True,
):
    """Produce a single SVG with one panel per reference.

    ``coverage_maps`` keys are expected to be ``sample/reference``.
    """
    # group by reference
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

    fig, axes = plt.subplots(n, 1, figsize=(12, 4 * n), sharex=False)
    if n == 1:
        axes = [axes]

    for ax, (ref_name, sample_maps) in zip(axes, refs.items()):
        positions = list(range(max_length))
        x = [p + start_pos for p in positions]
        for sample_name, cov_map in sample_maps.items():
            y = [cov_map.get(p, 0) for p in positions]
            ax.plot(x, y, linewidth=0.8, alpha=0.7, label=sample_name)
        total_y = [
            sum(cov_map.get(p, 0) for cov_map in sample_maps.values())
            for p in positions
        ]
        if show_total:
            ax.plot(x, total_y, linewidth=1.5, color="black", label="total coverage")

        if thresholds:
            _draw_threshold_tracks(ax, total_y, thresholds, x)

        ax.set_title(ref_name)
        ax.set_xlabel("Base position")
        ax.set_ylabel("Coverage depth")
        ax.legend(loc="upper right", fontsize="small")
        ax.margins(x=0.01)

    fig.tight_layout()
    fig.savefig(output_path, format="svg")
    plt.close(fig)
    logger.info("Multi-reference plot saved → %s", output_path)
