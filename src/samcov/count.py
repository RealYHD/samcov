from typing import Iterable
from os import path
import logging
import subprocess

logger = logging.getLogger(__name__)


def _get_reference_lengths(sam_path: str) -> dict[str, int]:
    """Get reference names and lengths from @SQ lines in the header."""
    cmd = ["samtools", "view", "-H", sam_path]
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=True,
    )
    lengths: dict[str, int] = {}
    for line in proc.stdout.splitlines():
        if line.startswith("@SQ"):
            parts = line.split("\t")
            name: str | None = None
            length: int | None = None
            for part in parts:
                if part.startswith("SN:"):
                    name = part[3:]
                elif part.startswith("LN:"):
                    length = int(part[3:])
            if name is not None and length is not None:
                lengths[name] = length
    return lengths


def _run_samtools_depth(sam_path: str):
    """Run samtools depth and yield (ref_name, pos, coverage) triples.

    samtools depth only outputs positions with coverage > 0.
    Zero-coverage positions are inferred downstream.
    """
    cmd = ["samtools", "depth", sam_path]
    logger.debug("Running: %s", " ".join(cmd))
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=True,
    )
    for line in proc.stdout.splitlines():
        parts = line.split("\t")
        if len(parts) != 3:
            continue
        ref_name, pos_str, cov_str = parts
        yield ref_name, int(pos_str) - 1, int(cov_str)  # 0-based position


def count_sam_positions(sam_path: str):
    logger.info('Retrieving coverage for "%s"', sam_path)

    ref_lengths = _get_reference_lengths(sam_path)
    coverage_maps: dict[str, dict[int, int]] = {}
    for ref_name in ref_lengths:
        coverage_maps[ref_name] = {}

    current_ref: str | None = None
    current_map: dict[int, int] = {}

    for ref_name, pos, cov in _run_samtools_depth(sam_path):
        if ref_name != current_ref:
            if current_ref is not None:
                coverage_maps[current_ref] = current_map
            current_ref = ref_name
            current_map = coverage_maps.get(ref_name, {})
        current_map[pos] = cov

    if current_ref is not None:
        coverage_maps[current_ref] = current_map

    max_length = max(ref_lengths.values()) if ref_lengths else 0
    logger.info("Completed coverage retrieval from SAM files.")
    return coverage_maps, max_length


def count_all_sam_positions(sam_paths: Iterable[str]):
    coverage_maps = {}
    lengths = []
    for sam_path in sam_paths:
        sam_coverage_maps, max_length = count_sam_positions(sam_path)
        lengths.append(max_length)
        for reference_name, coverage_map in sam_coverage_maps.items():
            coverage_maps[f"{path.basename(sam_path)}/{reference_name}"] = coverage_map
    return coverage_maps, int(max(lengths))