import os
import pysam
import tqdm


def generate_consensus(bam_path, output_path):
    pysam.consensus("-f", "fasta", bam_path, "-o", output_path)


def generate_all_consensus(*bams: str, output_folder):
    for item_path in bams:
        item_abs_path = os.path.abspath(item_path)
        abs_out_folder = os.path.abspath(output_folder)
        item_abs_out_path = os.path.join(
            abs_out_folder, os.path.splitext(os.path.basename(item_path))[0] + ".fasta"
        )
        generate_consensus(item_abs_path, item_abs_out_path)
