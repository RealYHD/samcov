import csv
from tqdm import trange

def export_coverages_as_csv(coverage_maps: dict[str, list[int]], output_path: str, sparse: bool):
    length = None
    for coverage_map in coverage_maps.values():
        if length is None or len(coverage_map) > length:
            length = len(coverage_map)
    if length is None:
        raise AttributeError("Coverage maps are empty!")
    with open(output_path, "w") as coverage_stream:
        csv_writer = csv.writer(coverage_stream)
        coverage_names = list(coverage_maps.keys())
        header = ["position", *coverage_maps.keys()]
        csv_writer.writerow(header)
        for i in trange(length, unit="row", smoothing=0.5):
            row = [i]
            coverage_sum = 0
            for coverage_name in coverage_names:
                coverage = coverage_maps[coverage_name][i] if i in coverage_maps[coverage_name] else 0
                row.append(coverage)
                coverage_sum += coverage
            if sparse:
                if coverage_sum > 0:
                    csv_writer.writerow(row)
            else:
                csv_writer.writerow(row)