import csv
from samcov import export


def test_export_coverages_as_csv_dense(tmp_path):
    cov = {"s1": {0: 5, 1: 0}, "s2": {1: 3}}
    out = tmp_path / "out.csv"
    export.export_coverages_as_csv(cov, 2, str(out), sparse=False, start_pos=1)
    with out.open(newline="") as f:
        rows = list(csv.reader(f))
    assert rows[0] == ["position", "s1", "s2"]
    assert rows[1] == ["1", "5", "0"]
    assert rows[2] == ["2", "0", "3"]


def test_export_coverages_as_csv_sparse(tmp_path):
    cov = {"s1": {0: 5}, "s2": {}}
    out = tmp_path / "out.csv"
    export.export_coverages_as_csv(cov, 2, str(out), sparse=True, start_pos=0)
    with out.open(newline="") as f:
        rows = list(csv.reader(f))
    assert rows[0] == ["position", "s1", "s2"]
    assert len(rows) == 2  # header + one data row
    assert rows[1] == ["0", "5", "0"]


def test_export_centers_as_csv(tmp_path):
    centers = {"mean": {0: 2.5}, "median": {0: 2.0}}
    out = tmp_path / "centers.csv"
    export.export_centers_as_csv(centers, 1, str(out), sparse=False, start_pos=0)
    with out.open(newline="") as f:
        rows = list(csv.reader(f))
    assert rows[0] == ["position", "mean", "median"]
    assert rows[1] == ["0", "2.5", "2.0"]


def test_export_low_coverage_csv(tmp_path):
    ranges = {"s1": [[0, 2], [5, 5]]}
    out = tmp_path / "low.csv"
    export.export_low_coverage_csv(ranges, 6, str(out), start_pos=0)
    with out.open(newline="") as f:
        rows = list(csv.reader(f))
    assert rows[0] == ["sample", "low coverage ranges"]
    assert rows[1][0] == "s1"


def test_export_shared_low_coverage_csv(tmp_path):
    ranges = [[0, 2], [4, 5]]
    out = tmp_path / "shared.csv"
    export.export_shared_low_coverage_csv(ranges, 6, str(out), threshold=1, start_pos=0)
    with out.open(newline="") as f:
        rows = list(csv.reader(f))
    assert rows[0] == ["start", "end", "length", "threshold"]
    assert rows[1] == ["0", "2", "3", "1"]
    assert rows[2] == ["4", "5", "2", "1"]


def test_export_low_coverage_bed(tmp_path):
    ranges = {"s1": [[0, 2], [4, 5]]}
    out = tmp_path / "low.bed"
    export.export_low_coverage_bed(ranges, str(out), start_pos=0, chrom="chr1")
    text = out.read_text()
    lines = text.strip().splitlines()
    assert lines[0] == "chr1\t0\t3\ts1\t0\t+"
    assert lines[1] == "chr1\t4\t6\ts1\t0\t+"


def test_export_shared_low_coverage_bed(tmp_path):
    ranges = [[0, 2], [4, 5]]
    out = tmp_path / "shared.bed"
    export.export_shared_low_coverage_bed(ranges, str(out), start_pos=0, chrom="chr1")
    text = out.read_text()
    lines = text.strip().splitlines()
    assert lines[0] == "chr1\t0\t3\tshared_low_coverage\t0\t+"
    assert lines[1] == "chr1\t4\t6\tshared_low_coverage\t0\t+"
