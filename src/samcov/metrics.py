from tqdm import trange, tqdm
import statistics
import logging

logger = logging.getLogger(__name__)


def measure_centers(coverage_maps: dict[str, dict[int, int]], length: int):
    statistics_centers = {
        "mean": {},
        "median": {},
        "mode": {},
    }
    logger.info("Calculating center statistics")
    for i in trange(length, unit="col", smoothing=0.5):
        across_samples = []
        for _, coverage_map in coverage_maps.items():
            across_samples.append(coverage_map[i] if i in coverage_map else 0)
        if sum(across_samples) == 0:
            continue
        statistics_centers["mean"][i] = statistics.fmean(across_samples)
        statistics_centers["median"][i] = statistics.median(across_samples)
        statistics_centers["mode"][i] = statistics.multimode(across_samples)[0]
    return statistics_centers


def calculate_consecutive_low_coverage(
    coverage_maps: dict[str, dict[int, int]],
    length: int,
    threshold: int = 1,
):
    """Find contiguous low-coverage regions per sample.

    A position is "low coverage" when its depth is **strictly below**
    *threshold*.  Gaps between high-coverage positions are reported as
    ``[start, end]`` (both inclusive, zero-based).

    Parameters
    ----------
    coverage_maps
        Mapping of ``sample_name → {position: depth}``.  Only positions
        ``< length`` are considered.
    length
        Total length of the reference sequence (number of positions).
    threshold
        Depth values below this are treated as low coverage.  Default 1.

    Returns
    -------
    dict[str, list[list[int]]]
        Per-sample list of ``[start, end]`` low-coverage ranges.
    """
    ranges: dict[str, list[list[int]]] = {}
    logger.info("Finding continuous low-coverage regions.")
    logger.info(
        "Every position with coverage lower than %d will be considered low-coverage.",
        threshold,
    )
    for sample_name, coverage_map in tqdm(
        coverage_maps.items(), unit="pos", smoothing=0.5
    ):
        ranges[sample_name] = []
        last_pos = -1
        for pos, coverage in sorted(coverage_map.items()):
            if pos >= length or coverage < threshold:
                continue
            if pos - last_pos > 1:
                ranges[sample_name].append([last_pos + 1, pos - 1])
            last_pos = pos
        # Report trailing gap from last high-coverage position to end of sequence
        if last_pos >= 0 and last_pos < length - 1:
            ranges[sample_name].append([last_pos + 1, length - 1])
    return ranges
