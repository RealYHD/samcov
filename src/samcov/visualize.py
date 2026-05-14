"""Coverage plotting utilities.

Generates vector line plots (SVG) from per-position coverage data.
"""
import logging
from typing import Iterable
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

logger = logging.getLogger(__name__)


def plot_coverage(
    coverage_maps: dict[str, dict[int, int]],
    max_length: int,
    output_path: str,
    start_pos: int = 0,
    sample_names: Iterable[str] | None = None,
    chrom_name: str | None = None,
    total_only: bool = False,
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
    ax.plot(x, total_y, linewidth=1.5, color="black", label="total coverage")

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
        ax.plot(x, total_y, linewidth=1.5, color="black", label="total coverage")
        ax.set_title(ref_name)
        ax.set_xlabel("Base position")
        ax.set_ylabel("Coverage depth")
        ax.legend(loc="upper right", fontsize="small")
        ax.margins(x=0.01)

    fig.tight_layout()
    fig.savefig(output_path, format="svg")
    plt.close(fig)
    logger.info("Multi-reference plot saved → %s", output_path)
