import os
import subprocess
import tempfile
from samcov import count, metrics, export

# Real BAM files from PRJEB72167 (Chlamydia trachomatis, subsampled to 2k reads each)
RESOURCES = os.path.join(os.path.dirname(__file__), "..", "resources")
BAM_88 = os.path.join(RESOURCES, "ERR13397788.bam")
BAM_94 = os.path.join(RESOURCES, "ERR13397794.bam")


def test_e2e_count_real_bams():
    """E2E: count coverage from real PRJEB72167 BAMs."""
    coverage_maps, max_length = count.count_all_sam_positions([BAM_88, BAM_94])
    assert len(coverage_maps) == 2
    assert max_length > 1_000_000  # Chlamydia genome ~1.04 Mbp
    assert max_length < 1_100_000
    # Both samples should have coverage on the same reference
    refs = {k.split("/")[-1] for k in coverage_maps.keys()}
    assert len(refs) == 1  # Single reference: NC_000117.1


def test_e2e_shared_low_coverage_real_bams():
    """E2E: find shared low-coverage regions in real BAMs."""
    coverage_maps, max_length = count.count_all_sam_positions([BAM_88, BAM_94])
    shared = metrics.calculate_shared_low_coverage(coverage_maps, max_length, threshold=1)
    # With 2k reads on a 1 Mbp genome, most positions should have 0 coverage.
    # Shared low-coverage regions should be substantial.
    total_shared_bases = sum(end - start + 1 for start, end in shared)
    assert total_shared_bases > 0
    # Sanity: shared regions should not exceed the genome length
    assert total_shared_bases <= max_length


def test_e2e_cli_csv_export():
    """E2E: run CLI and verify CSV output for real BAMs."""
    with tempfile.TemporaryDirectory() as tmpdir:
        csv_path = os.path.join(tmpdir, "coverage.csv")
        result = subprocess.run(
            [
                "samcov",
                BAM_88, BAM_94,
                "--csv", csv_path,
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, result.stderr
        assert os.path.exists(csv_path)
        with open(csv_path) as f:
            lines = f.readlines()
        assert len(lines) > 1
        header = lines[0].strip().split(",")
        assert header[0] == "position"
        assert len(header) == 3  # position + 2 samples


def test_e2e_cli_shared_bed_export():
    """E2E: run CLI and verify BED output for shared low-coverage."""
    with tempfile.TemporaryDirectory() as tmpdir:
        bed_path = os.path.join(tmpdir, "shared.bed")
        result = subprocess.run(
            [
                "samcov",
                BAM_88, BAM_94,
                "--shared-low-coverage-bed", bed_path,
                "--low-coverage", "1",
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, result.stderr
        assert os.path.exists(bed_path)
        with open(bed_path) as f:
            lines = f.readlines()
        assert len(lines) > 0
        first = lines[0].strip().split("\t")
        assert len(first) == 6  # BED6: chrom start end name score strand
        assert first[0] == "."
        assert first[5] == "+"
