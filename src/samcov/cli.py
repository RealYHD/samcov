from samcov import count, metrics
from samcov import export
import argparse
import logging

# create logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)


def run():
    parser = argparse.ArgumentParser(
        description="A simple SAM/BAM file coverage extraction tool.")
    parser.add_argument("input", nargs="+", type=str,
                        help="The SAM/BAM files to extract coverages upon.", metavar="I")
    parser.add_argument("--csv", type=str, help="Path to output as a CSV", required=False, default="")
    parser.add_argument("--centers-csv", type=str, help="Path to output as a CSV of center measures of each position.", required=False, default="")
    parser.add_argument("--low-coverage-csv", type=str, help="Path to output low coverage ranges as a CSV.", required=False, default="")
    parser.add_argument("--low-coverage", type=int, help="A number that is to be considered low coverage.", required=False, default=1)
    parser.add_argument("--start-at", type=int, help="Sets the first position.", default=0, required=False)
    parser.add_argument("--sparse", action="store_true", help="Whether or not output should be as sparse as possible.", required=False, default=False)
    parser.add_argument("--verbosity", type=str, help="Sets the verbosity of the output", required=False, default="INFO")
    
    args = parser.parse_args()
    logger.setLevel(args.verbosity)
    logger.debug("Verbosity set to: %s", args.verbosity)
    logger.info("SAM Coverage extraction tool")
    start_pos = args.start_at
    if start_pos:
        logger.info("Start set to %d.", start_pos)
    coverage_maps, max_length = count.count_all_sam_positions(args.input)
    if args.csv:
        export.export_coverages_as_csv(coverage_maps, max_length, args.csv, args.sparse, start_pos=start_pos)
    if args.centers_csv:
        center_measures = metrics.measure_centers(coverage_maps, max_length)
        export.export_centers_as_csv(center_measures, max_length, args.centers_csv, args.sparse, start_pos=start_pos)
    if args.low_coverage_csv:
        low_coverage_ranges = metrics.calculate_consecutive_low_coverage(coverage_maps, max_length, args.low_coverage)
        export.export_low_coverage_csv(low_coverage_ranges, max_length, args.low_coverage_csv, start_pos=start_pos)

def main():
    run()


if __name__ == "__main__":
    main()