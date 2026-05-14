import os
from samcov import count, metrics, export, consensus, visualize
import argparse
import logging

# create logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)


def validate_inputs(inputs):
    """Ensure all input files exist and are readable."""
    for path in inputs:
        if not os.path.exists(path):
            logger.error("Input file not found: %s", path)
            raise FileNotFoundError(f"Input file not found: {path}")
        if not os.path.isfile(path):
            logger.error("Not a file: %s", path)
            raise ValueError(f"Not a file: {path}")

def run(argv=None):
    parser = argparse.ArgumentParser(
        description="A simple SAM/BAM file coverage extraction tool."
    )
    parser.add_argument(
        "input",
        nargs="+",
        type=str,
        help="The SAM/BAM files to extract coverages upon.",
        metavar="I",
    )
    parser.add_argument(
        "--csv", type=str, help="Path to output as a CSV", required=False, default=""
    )
    parser.add_argument(
        "--centers-csv",
        type=str,
        help="Path to output as a CSV of center measures of each position.",
        required=False,
        default="",
    )
    parser.add_argument(
        "--low-coverage-csv",
        type=str,
        help="Path to output low coverage ranges as a CSV.",
        required=False,
        default="",
    )
    parser.add_argument(
        "--low-coverage",
        type=int,
        help="A number that is to be considered low coverage.",
        required=False,
        default=1,
    )
    parser.add_argument(
        "--start-at",
        type=int,
        help="Sets the first position.",
        default=0,
        required=False,
    )
    parser.add_argument(
        "--sparse",
        action="store_true",
        help="Whether or not output should be as sparse as possible.",
        required=False,
        default=False,
    )
    parser.add_argument(
        "--verbosity",
        type=str,
        help="Sets the verbosity of the output",
        required=False,
        default="INFO",
    )
    parser.add_argument(
        "--shared-low-coverage-csv",
        type=str,
        help="Path to output shared low-coverage ranges (across all samples) as a CSV.",
        required=False,
        default="",
    )
    parser.add_argument(
        "--shared-low-coverage-bed",
        type=str,
        help="Path to output shared low-coverage ranges (across all samples) as a BED file.",
        required=False,
        default="",
    )
    parser.add_argument(
        "--low-coverage-bed",
        type=str,
        help="Path to output per-sample low-coverage ranges as a BED file.",
        required=False,
        default="",
    )
    parser.add_argument(
        "--consensus",
        type=str,
        help="Generates consensus sequences at the specified output directory.",
        required=False,
        default="",
    )
    parser.add_argument(
        "--plot-svg",
        type=str,
        help="Path to output a coverage line-plot SVG (one panel per reference).",
        required=False,
        default="",
    )
    parser.add_argument(
        "--plot-svg-simple",
        type=str,
        help="Path to output a single-panel SVG when all inputs target one reference.",
        required=False,
        default="",
    )
    parser.add_argument(
        "--plot-thresholds",
        type=str,
        help="Comma-separated depth thresholds for SVG plot tracks (e.g. 1,5,10).",
        required=False,
        default="",
    )
    parser.add_argument(
        "--no-total",
        action="store_true",
        help="Suppress the total-coverage black line in SVG plots.",
        required=False,
        default=False,
    )
    args = parser.parse_args(argv)
    logger.setLevel(args.verbosity)
    logger.debug("Verbosity set to: %s", args.verbosity)
    logger.info("SAM Coverage extraction tool")
    validate_inputs(args.input)
    start_pos = args.start_at
    if start_pos:
        logger.info("Start set to %d.", start_pos)
    coverage_maps, max_length = count.count_all_sam_positions(args.input)
    if args.csv:
        export.export_coverages_as_csv(
            coverage_maps, max_length, args.csv, args.sparse, start_pos=start_pos
        )
    if args.centers_csv:
        center_measures = metrics.measure_centers(coverage_maps, max_length)
        export.export_centers_as_csv(
            center_measures,
            max_length,
            args.centers_csv,
            args.sparse,
            start_pos=start_pos,
        )
    if args.low_coverage_csv:
        low_coverage_ranges = metrics.calculate_consecutive_low_coverage(
            coverage_maps, max_length, args.low_coverage
        )
        export.export_low_coverage_csv(
            low_coverage_ranges, max_length, args.low_coverage_csv, start_pos=start_pos
        )
    if args.low_coverage_bed:
        low_coverage_ranges = metrics.calculate_consecutive_low_coverage(
            coverage_maps, max_length, args.low_coverage
        )
        export.export_low_coverage_bed(
            low_coverage_ranges, args.low_coverage_bed, start_pos=start_pos
        )
    if args.shared_low_coverage_csv:
        shared_ranges = metrics.calculate_shared_low_coverage(
            coverage_maps, max_length, args.low_coverage
        )
        export.export_shared_low_coverage_csv(
            shared_ranges,
            max_length,
            args.shared_low_coverage_csv,
            args.low_coverage,
            start_pos=start_pos,
        )
    if args.shared_low_coverage_bed:
        shared_ranges = metrics.calculate_shared_low_coverage(
            coverage_maps, max_length, args.low_coverage
        )
        export.export_shared_low_coverage_bed(
            shared_ranges, args.shared_low_coverage_bed, start_pos=start_pos
        )
    if args.consensus:
        if not consensus.check_for_samtools():
            logger.warning(
                "samtools is not installed on PATH. "
                "The --consensus option requires samtools. "
                "Install it (e.g. 'conda install -c bioconda samtools') and retry."
            )
            raise RuntimeError(
                "samtools is required for consensus generation but was not found on PATH."
            )
        consensus.generate_all_consensus(*args.input, output_folder=args.consensus)

    thresholds = []
    if args.plot_thresholds:
        try:
            thresholds = [int(t.strip()) for t in args.plot_thresholds.split(",")]
        except ValueError:
            parser.error("--plot-thresholds must be comma-separated integers (e.g. 1,5,10)")
    if args.plot_svg:
        visualize.plot_all(
            coverage_maps, max_length, args.plot_svg, start_pos=start_pos, thresholds=thresholds, show_total=not args.no_total
        )
    if args.plot_svg_simple:
        # simple mode: all keys treated as samples on a single reference
        visualize.plot_coverage(
            coverage_maps, max_length, args.plot_svg_simple, start_pos=start_pos, thresholds=thresholds, show_total=not args.no_total
        )


def main():
    run()


if __name__ == "__main__":
    main()
