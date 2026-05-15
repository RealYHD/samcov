import csv
from tqdm import trange, tqdm
import logging
from typing import Union

logger = logging.getLogger(__name__)


def export_coverages_as_csv(
    coverage_maps: dict[str, dict[int, int]],
    length,
    output_path: str,
    sparse: bool,
    start_pos: int = 0,
):
    logger.info("Beginning export of coverage data as CSV")
    if sparse:
        logger.info("CSV will be sparse")
    with open(output_path, "w") as coverage_stream:
        csv_writer = csv.writer(coverage_stream)
        coverage_names = list(coverage_maps.keys())
        headers = ["position", *coverage_names]
        logger.debug("Using the following headers: %s", headers)
        csv_writer.writerow(headers)
        for i in trange(length, unit="row", smoothing=0.5):
            row: list[Union[int, float]] = [i + start_pos]
            coverage_sum = 0
            for coverage_name in coverage_names:
                coverage = (
                    coverage_maps[coverage_name][i]
                    if i in coverage_maps[coverage_name]
                    else 0
                )
                row.append(coverage)
                coverage_sum += coverage
            if sparse:
                if coverage_sum > 0:
                    csv_writer.writerow(row)
            else:
                csv_writer.writerow(row)


def export_centers_as_csv(
    stat_centers: dict[str, dict[int, float]],
    length: int,
    output_path: str,
    sparse: bool,
    start_pos: int = 0,
):
    logger.info("Beginning export of statistical center measures")
    if sparse:
        logger.info("Centers CSV will be sparse.")
    with open(output_path, "w") as centers_stream:
        csv_writer = csv.writer(centers_stream)
        measure_names = list(stat_centers.keys())
        headers = ["position", *measure_names]
        logger.debug("Using the following headers: %s", headers)
        csv_writer.writerow(headers)
        for i in trange(length, unit="row", smoothing=0.5):
            row: list[Union[int, float]] = [i + start_pos]
            has_data = True
            for measure_name in measure_names:
                if i not in stat_centers[measure_name]:
                    has_data = False
                    break
                row.append(
                    stat_centers[measure_name][i]
                    if i in stat_centers[measure_name]
                    else 0
                )
            if sparse:
                if has_data:
                    csv_writer.writerow(row)
            else:
                if not has_data:
                    row.extend([0.0] * len(measure_names))
                csv_writer.writerow(row)


def export_shared_low_coverage_csv(
    ranges: list[list[int]],
    length: int,
    output_path: str,
    threshold: int,
    start_pos: int = 0,
):
    """Export shared low-coverage intervals as a CSV."""
    logger.info("Beginning export of shared low coverage areas CSV")
    with open(output_path, "w") as stream:
        writer = csv.writer(stream)
        writer.writerow(["start", "end", "length", "threshold"])
        for start, end in ranges:
            writer.writerow([
                start + start_pos,
                end + start_pos,
                end - start + 1,
                threshold,
            ])


def export_low_coverage_csv(
    ranges: dict[str, list[list[int]]],
    length: int,
    output_path: str,
    start_pos: int = 0,
):
    logger.info("Beginning export of low coverage areas CSV")
    with open(output_path, "w") as low_coverage_stream:
        csv_writer = csv.writer(low_coverage_stream)
        rows = ["sample", "low coverage ranges"]
        csv_writer.writerow(rows)
        for sample_name, low_cov in tqdm(ranges.items(), unit="sample"):
            pretty_ranges = ", ".join(
                [str([pos + start_pos for pos in cov_range]) for cov_range in low_cov]
            )
            csv_writer.writerow([sample_name, pretty_ranges])


# ── BED export helpers ─────────────────────────────────────────────


def export_low_coverage_bed(
    ranges: dict[str, list[list[int]]],
    output_path: str,
    start_pos: int = 0,
    chrom: str = ".",
):
    """Export per-sample low-coverage intervals as a BED file.

    BED format: chrom start end name score strand
    (start is 0-based, end is exclusive)
    """
    logger.info("Beginning export of low-coverage regions as BED")
    with open(output_path, "w") as bed_stream:
        for sample_name, intervals in tqdm(ranges.items(), unit="sample"):
            for start, end in intervals:
                bed_start = start + start_pos
                bed_end = end + start_pos + 1  # BED end is exclusive
                bed_stream.write(
                    f"{chrom}\t{bed_start}\t{bed_end}\t{sample_name}\t0\t+\n"
                )


def export_shared_low_coverage_bed(
    ranges: list[list[int]],
    output_path: str,
    start_pos: int = 0,
    chrom: str = ".",
    name: str = "shared_low_coverage",
):
    """Export shared low-coverage intervals as a BED file."""
    logger.info("Beginning export of shared low-coverage regions as BED")
    with open(output_path, "w") as bed_stream:
        for start, end in ranges:
            bed_start = start + start_pos
            bed_end = end + start_pos + 1  # BED end is exclusive
            bed_stream.write(
                f"{chrom}\t{bed_start}\t{bed_end}\t{name}\t0\t+\n"
            )


def export_shared_high_coverage_csv(
    ranges: list[list[int]],
    length: int,
    output_path: str,
    threshold: int,
    start_pos: int = 0,
):
    """Export shared high-coverage intervals as a CSV."""
    logger.info("Beginning export of shared high coverage areas CSV")
    with open(output_path, "w") as stream:
        writer = csv.writer(stream)
        writer.writerow(["start", "end", "length", "threshold"])
        for start, end in ranges:
            writer.writerow([
                start + start_pos,
                end + start_pos,
                end - start + 1,
                threshold,
            ])


def export_shared_high_coverage_bed(
    ranges: list[list[int]],
    output_path: str,
    start_pos: int = 0,
    chrom: str = ".",
    name: str = "shared_high_coverage",
):
    """Export shared high-coverage intervals as a BED file."""
    logger.info("Beginning export of shared high-coverage regions as BED")
    with open(output_path, "w") as bed_stream:
        for start, end in ranges:
            bed_start = start + start_pos
            bed_end = end + start_pos + 1  # BED end is exclusive
            bed_stream.write(
                f"{chrom}\t{bed_start}\t{bed_end}\t{name}\t0\t+\n"
            )
