from typing import Iterable
import pysam
from os import path
import logging
from tqdm import tqdm
import sys

logger = logging.getLogger(__name__)

def count_sam_positions(sam_path: str, position_start: int = 0):
    logger.info('Retrieving coverage for "%s"', sam_path)
    sam = pysam.AlignmentFile(sam_path)
    reference_names = sam.references
    coverage_maps = {}
    for reference_name in reference_names:
        length = sam.get_reference_length(reference_name)
        coverage_maps[reference_name] = {}
        last_pos = 0
        iterations = 0
        with tqdm(total=length, unit="col", smoothing=0.5, desc=reference_name) as progress:
            for read_col in sam.pileup(reference=reference_name, stepper="all"):
                coverage_maps[reference_name][read_col.pos + position_start] = read_col.n
                progress.update(read_col.pos + position_start - last_pos)
                last_pos = read_col.pos + position_start
                iterations += 1
        sys.stdout.write("\033[F")
    sys.stdout.write("\n")
    logger.info("Completed coverage retrieval from SAM files.")
    return coverage_maps, int(max(sam.lengths))

def count_all_sam_positions(sam_paths: Iterable[str], position_start: int = 0):
    coverage_maps = {}
    lengths: list[int] = []
    for sam_path in sam_paths:
        sam_coverage_maps, max_length = count_sam_positions(sam_path, position_start)
        lengths.append(max_length)
        for reference_name, coverage_map in sam_coverage_maps.items():
            coverage_maps[f"{path.basename(sam_path)}/{reference_name}"] = coverage_map
    return coverage_maps, int(max(lengths))