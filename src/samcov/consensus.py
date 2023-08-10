import os
import pysam
from tqdm import tqdm
import logging

logger = logging.getLogger(__name__)

def check_for_samtools():
    try:
        return True
    except Exception as ex:
        print(ex)
        return False

def generate_consensus(bam_path, output_path):
    logger.debug("Generating consensus for \"%s\" using samtools.")
    pysam.consensus("-f", "fasta", bam_path, "-o", output_path)


def generate_all_consensus(*bams: str, output_folder):
    logger.info("Generating consensus files and outputting to \"%s\".", output_folder)
    for item_path in tqdm(bams, unit="SAM", smoothing=0.75):
        item_abs_path = os.path.abspath(item_path)
        abs_out_folder = os.path.abspath(output_folder)
        item_abs_out_path = os.path.join(
            abs_out_folder, os.path.splitext(os.path.basename(item_path))[0] + ".fasta"
        )
        generate_consensus(item_abs_path, item_abs_out_path)
