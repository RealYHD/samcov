from samcov import count
from samcov import export
import argparse
import logging

logger = logging.getLogger(__name__)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

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
    parser.add_argument("--csv", type=str, help="Path to output as a CSV", metavar="o",required=False, default="")
    parser.add_argument("--sparse-csv", type=str, help="Path to output as a sparse CSV", metavar="o",required=False, default="")
    logger.info("Beginning coverage extraction...")
    args = parser.parse_args()
    coverage_maps = count.count_all_sam_positions(args.input)
    if args.csv:
        export.export_coverages_as_csv(coverage_maps, args.csv, False)
    if args.sparse_csv:
        export.export_coverages_as_csv(coverage_maps, args.sparse_csv, True)

def main():
    run()