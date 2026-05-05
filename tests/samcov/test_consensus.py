from unittest.mock import patch
from samcov import consensus


def test_check_for_samtools_not_found(monkeypatch):
    import shutil
    monkeypatch.setattr(shutil, "which", lambda _: None)
    assert consensus.check_for_samtools() is False


def test_check_for_samtools_found(monkeypatch):
    import shutil
    monkeypatch.setattr(shutil, "which", lambda _: "/usr/bin/samtools")
    assert consensus.check_for_samtools() is True


def test_generate_consensus_correct_call():
    with patch("subprocess.run") as mock_run:
        consensus.generate_consensus("tests/resources/mt.sorted.bam",
                                     "tests/resources/mt.sorted.fasta")
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert args[0] == "samtools"
        assert "tests/resources/mt.sorted.bam" in args
        assert "tests/resources/mt.sorted.fasta" in args
