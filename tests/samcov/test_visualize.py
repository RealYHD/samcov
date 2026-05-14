import pytest
from samcov import visualize


def test_plot_coverage_basic(tmp_path):
    """Smoke-test a single-panel strip SVG export."""
    cov = {
        "sample_A": {0: 5, 1: 10, 2: 3},
        "sample_B": {0: 2, 2: 7},
    }
    out = tmp_path / "coverage.svg"
    visualize.plot_coverage(cov, 3, str(out), start_pos=1)
    assert out.exists()
    text = out.read_text()
    assert text.startswith("<?xml")
    assert "svg" in text


def test_plot_all_basic(tmp_path):
    """Smoke-test a multi-panel strip SVG export."""
    cov = {
        "run1/ref1": {0: 5, 1: 0, 2: 3},
        "run2/ref1": {0: 2, 1: 4, 2: 1},
        "run1/ref2": {0: 1, 1: 2},
    }
    out = tmp_path / "multi.svg"
    visualize.plot_all(cov, 3, str(out), start_pos=0)
    assert out.exists()
    text = out.read_text()
    assert text.startswith("<?xml")
    assert "svg" in text


def test_plot_coverage_with_chrom_name(tmp_path):
    """Regression: chrom name should appear in the SVG title."""
    cov = {"s1": {0: 1}}
    out = tmp_path / "named.svg"
    visualize.plot_coverage(cov, 1, str(out), chrom_name="chr1")
    text = out.read_text()
    assert "chr1" in text


def test_plot_all_no_data(tmp_path, caplog):
    """Regression: empty coverage_maps should not crash and should log a warning."""
    out = tmp_path / "empty.svg"
    visualize.plot_all({}, 0, str(out))
    assert not out.exists() or out.read_text() == ""
    assert "No coverage data" in caplog.text


def test_plot_coverage_with_thresholds(tmp_path):
    """Regression: threshold tracks should render without crashing."""
    cov = {
        "s1": {0: 5, 1: 0, 2: 3, 3: 8},
        "s2": {0: 2, 1: 1, 2: 7},
    }
    out = tmp_path / "thresholds.svg"
    visualize.plot_coverage(cov, 4, str(out), thresholds=[1, 5, 10])
    assert out.exists()
    text = out.read_text()
    assert "svg" in text


def test_plot_all_with_thresholds(tmp_path):
    """Regression: threshold tracks on multi-panel plot."""
    cov = {
        "run1/ref1": {0: 5, 1: 0, 2: 3},
        "run2/ref1": {0: 2, 1: 4, 2: 1},
    }
    out = tmp_path / "multi_thresh.svg"
    visualize.plot_all(cov, 3, str(out), thresholds=[2, 6])
    assert out.exists()
    text = out.read_text()
    assert "svg" in text
