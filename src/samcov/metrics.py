from tqdm import trange
import statistics

def measure_centers(coverage_maps: dict[str, dict[int, int]], length: int):
    statistics_centers = {
        "mean": {},
        "median": {},
        "mode": {}
    }
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