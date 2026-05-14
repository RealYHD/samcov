import os
import pytest
from unittest.mock import patch, MagicMock
from samcov.cli import validate_inputs, run


def test_validate_inputs_ok(tmp_path):
    p = tmp_path / "file.bam"
    p.write_text("")
    validate_inputs([str(p)])


def test_validate_inputs_missing():
    with pytest.raises(FileNotFoundError):
        validate_inputs(["/nonexistent/file.bam"])


def test_validate_inputs_not_a_file(tmp_path):
    with pytest.raises(ValueError):
        validate_inputs([str(tmp_path)])


@patch("samcov.cli.count.count_all_sam_positions")
@patch("samcov.cli.export.export_coverages_as_csv")
def test_cli_csv(mock_export, mock_count, tmp_path, capsys):
    p = tmp_path / "fake.bam"
    p.write_text("")
    mock_count.return_value = ({"fake.bam/ref": {0: 5}}, 1)
    run([str(p), "--csv", str(tmp_path / "out.csv")])
    mock_export.assert_called_once()


@patch("samcov.cli.count.count_all_sam_positions")
@patch("samcov.cli.visualize.plot_coverage")
def test_cli_plot_svg_simple_with_thresholds(mock_plot, mock_count, tmp_path):
    p = tmp_path / "fake.bam"
    p.write_text("")
    mock_count.return_value = ({"fake.bam/ref": {0: 5, 1: 0, 2: 3}}, 3)
    out = tmp_path / "plot.svg"
    run([str(p), "--plot-svg-simple", str(out), "--plot-thresholds", "1,5"])
    mock_plot.assert_called_once()
    call_kwargs = mock_plot.call_args.kwargs
    assert call_kwargs.get("thresholds") == [1, 5]


@patch("samcov.cli.count.count_all_sam_positions")
@patch("samcov.cli.visualize.plot_coverage")
def test_cli_plot_svg_simple(mock_plot, mock_count, tmp_path, capsys):
    p = tmp_path / "fake.bam"
    p.write_text("")
    mock_count.return_value = ({"fake.bam/ref": {0: 5}}, 1)
    out = tmp_path / "plot.svg"
    run([str(p), "--plot-svg-simple", str(out)])
    mock_plot.assert_called_once()


@patch("samcov.cli.count.count_all_sam_positions")
@patch("samcov.cli.visualize.plot_all")
def test_cli_plot_svg_no_total(mock_plot, mock_count, tmp_path):
    p = tmp_path / "fake.bam"
    p.write_text("")
    mock_count.return_value = ({"fake.bam/ref": {0: 5}}, 1)
    out = tmp_path / "plot.svg"
    run([str(p), "--plot-svg", str(out), "--no-total"])
    mock_plot.assert_called_once()
    call_kwargs = mock_plot.call_args.kwargs
    assert call_kwargs.get("show_total") is False


@patch("samcov.cli.count.count_all_sam_positions")
@patch("samcov.cli.visualize.plot_all")
def test_cli_plot_svg(mock_plot, mock_count, tmp_path, capsys):
    p = tmp_path / "fake.bam"
    p.write_text("")
    mock_count.return_value = ({"fake.bam/ref": {0: 5}}, 1)
    out = tmp_path / "plot.svg"
    run([str(p), "--plot-svg", str(out)])
    mock_plot.assert_called_once()


@patch("samcov.cli.count.count_all_sam_positions")
@patch("samcov.cli.metrics.measure_centers")
@patch("samcov.cli.export.export_centers_as_csv")
def test_cli_centers_csv(mock_export, mock_metrics, mock_count, tmp_path):
    p = tmp_path / "fake.bam"
    p.write_text("")
    mock_count.return_value = ({"fake.bam/ref": {0: 5}}, 1)
    mock_metrics.return_value = {"mean": {0: 5.0}}
    run([str(p), "--centers-csv", str(tmp_path / "centers.csv")])
    mock_export.assert_called_once()


@patch("samcov.cli.count.count_all_sam_positions")
@patch("samcov.cli.metrics.calculate_consecutive_low_coverage")
@patch("samcov.cli.export.export_low_coverage_csv")
def test_cli_low_coverage_csv(mock_export, mock_metrics, mock_count, tmp_path):
    p = tmp_path / "fake.bam"
    p.write_text("")
    mock_count.return_value = ({"fake.bam/ref": {0: 5}}, 1)
    mock_metrics.return_value = {"fake.bam/ref": []}
    run([str(p), "--low-coverage-csv", str(tmp_path / "low.csv"), "--low-coverage", "2"])
    mock_export.assert_called_once()


@patch("samcov.cli.count.count_all_sam_positions")
@patch("samcov.cli.metrics.calculate_shared_low_coverage")
@patch("samcov.cli.export.export_shared_low_coverage_csv")
def test_cli_shared_low_coverage_csv(mock_export, mock_metrics, mock_count, tmp_path):
    p = tmp_path / "fake.bam"
    p.write_text("")
    mock_count.return_value = ({"fake.bam/ref": {0: 5}}, 1)
    mock_metrics.return_value = []
    run([str(p), "--shared-low-coverage-csv", str(tmp_path / "shared.csv")])
    mock_export.assert_called_once()


@patch("samcov.cli.count.count_all_sam_positions")
@patch("samcov.cli.metrics.calculate_shared_low_coverage")
@patch("samcov.cli.export.export_shared_low_coverage_bed")
def test_cli_shared_low_coverage_bed(mock_export, mock_metrics, mock_count, tmp_path):
    p = tmp_path / "fake.bam"
    p.write_text("")
    mock_count.return_value = ({"fake.bam/ref": {0: 5}}, 1)
    mock_metrics.return_value = []
    run([str(p), "--shared-low-coverage-bed", str(tmp_path / "shared.bed")])
    mock_export.assert_called_once()


@patch("samcov.cli.count.count_all_sam_positions")
@patch("samcov.cli.metrics.calculate_consecutive_low_coverage")
@patch("samcov.cli.export.export_low_coverage_bed")
def test_cli_low_coverage_bed(mock_export, mock_metrics, mock_count, tmp_path):
    p = tmp_path / "fake.bam"
    p.write_text("")
    mock_count.return_value = ({"fake.bam/ref": {0: 5}}, 1)
    mock_metrics.return_value = {"fake.bam/ref": []}
    run([str(p), "--low-coverage-bed", str(tmp_path / "low.bed")])
    mock_export.assert_called_once()


@patch("samcov.cli.consensus.check_for_samtools", return_value=True)
@patch("samcov.cli.consensus.generate_all_consensus")
@patch("samcov.cli.count.count_all_sam_positions")
def test_cli_consensus(mock_count, mock_gen, mock_check, tmp_path):
    p = tmp_path / "fake.bam"
    p.write_text("")
    mock_count.return_value = ({"fake.bam/ref": {0: 5}}, 1)
    run([str(p), "--consensus", str(tmp_path / "consensus")])
    mock_gen.assert_called_once()


@patch("samcov.cli.consensus.check_for_samtools", return_value=False)
@patch("samcov.cli.count.count_all_sam_positions")
def test_cli_consensus_no_samtools(mock_count, mock_check, tmp_path):
    p = tmp_path / "fake.bam"
    p.write_text("")
    mock_count.return_value = ({"fake.bam/ref": {0: 5}}, 1)
    with pytest.raises(RuntimeError, match="samtools"):
        run([str(p), "--consensus", str(tmp_path / "consensus")])
