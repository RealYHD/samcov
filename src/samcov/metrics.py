from tqdm import trange, tqdm
import statistics
import logging

logger = logging.getLogger(__name__)

def measure_centers(coverage_maps: dict[str, dict[int, int]], length: int):
    statistics_centers = {
        "mean": {},
        "median": {},
        "mode": {}
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
        statistics_centers["mode"][i] = statistics.mode(across_samples)
    return statistics_centers

def calculate_consecutive_low_coverage(coverage_maps: dict[str, dict[int, int]], length: int, threshold=1):
    ranges: dict[str, list[list[int]]] = {}
    logger.info("Finding continuous low-coverage regions.")
    logger.info("Everything position with coverages lower than %d will be considered low-coverage.", threshold)
    for sample_name, coverage_map in tqdm(coverage_maps.items(), unit="pos", smoothing=0.5):
        ranges[sample_name] = []
        last_pos = -1
        for pos, coverage in coverage_map.items():
            if coverage < threshold:
                continue
            if pos - last_pos > 1:
                ranges[sample_name].append([last_pos + 1, pos - 1])
            last_pos = pos
    return ranges