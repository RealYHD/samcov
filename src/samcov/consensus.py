import os
import shutil
import subprocess
import logging
from tqdm import tqdm

logger = logging.getLogger(__name__)


def check_for_samtools() -> bool:
    """Check if samtools is available on PATH."""
    return shutil.which("samtools") is not None


def generate_consensus(bam_path: str, output_path: str) -> None:
    """Generate consensus FASTA from a BAM file using samtools."""
    logger.debug('Generating consensus for "%s" using samtools.', bam_path)
    subprocess.run(
        ["samtools", "consensus", "-f", "fasta", bam_path, "-o", output_path],
        check=True,
    )


def generate_all_consensus(*bams: str, output_folder: str) -> None:
    """Generate consensus FASTA files for multiple BAM files."""
    logger.info('Generating consensus files and outputting to "%s".', output_folder)
    for bam_path in tqdm(bams, unit="SAM", smoothing=0.75):
        abs_bam = os.path.abspath(bam_path)
        abs_out = os.path.abspath(output_folder)
        base = os.path.splitext(os.path.basename(bam_path))[0]
        out_path = os.path.join(abs_out, f"{base}.fasta")
        generate_consensus(abs_bam, out_path)
