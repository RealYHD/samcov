from samcov import metrics


def test_measure_centers_correct():
    dummy_coverage_map = {
        "s1": {1: 1, 2: 3, 5: 4},
        "s2": {1: 4, 2: 6, 5: 10},
        "s3": {1: 4, 2: 6, 5: 10},
    }
    expected_measures = {
        "mean": {1: 3, 2: 5, 5: 8},
        "median": {1: 4, 2: 6, 5: 10},
        "mode": {1: 4, 2: 6, 5: 10},
    }

    assert metrics.measure_centers(dummy_coverage_map, length=6) == expected_measures


def test_calculate_consecutive_low_coverage():
    """Low-coverage gaps include leading, internal, and trailing regions."""
    dummy_coverage_map = {
        "s1": {0: 2, 1: 1, 2: 3, 5: 4},
        "s2": {0: 2, 1: 4, 2: 6, 6: 10},
        "s3": {1: 4, 2: 6, 5: 10, 6: 4, 20: 2},
    }
    expected_low_cov = {
        "s1": [[3, 4], [6, 20]],
        "s2": [[3, 5], [7, 20]],
        "s3": [[0, 0], [3, 4], [7, 19]],
    }

    assert (
        metrics.calculate_consecutive_low_coverage(dummy_coverage_map, 21)
        == expected_low_cov
    )


def test_calculate_consecutive_low_coverage_trailing_only():
    """A single covered position at the start should yield one trailing gap."""
    cov = {"s": {0: 5}}
    assert metrics.calculate_consecutive_low_coverage(cov, 10) == {"s": [[1, 9]]}


def test_calculate_consecutive_low_coverage_leading_only():
    """A single covered position at the end should yield one leading gap."""
    cov = {"s": {9: 5}}
    assert metrics.calculate_consecutive_low_coverage(cov, 10) == {"s": [[0, 8]]}


def test_calculate_consecutive_low_coverage_all_high():
    """Every position covered should return an empty list."""
    cov = {"s": {i: 5 for i in range(10)}}
    assert metrics.calculate_consecutive_low_coverage(cov, 10) == {"s": []}


# ── Shared low-coverage across all samples ──────────────────────────

def test_calculate_shared_low_coverage_basic():
    """Regions where ALL samples have coverage < threshold."""
    cov = {
        "s1": {0: 5, 1: 5, 2: 0, 3: 0, 4: 5},
        "s2": {0: 5, 1: 0, 2: 0, 3: 0, 4: 5},
    }
    # Only positions 2 and 3 have ALL samples < 1 (zero in both)
    assert metrics.calculate_shared_low_coverage(cov, 5, threshold=1) == [[2, 3]]


def test_calculate_shared_low_coverage_trailing():
    """Shared trailing gap to end of sequence."""
    cov = {
        "s1": {0: 5, 1: 5},
        "s2": {0: 5, 1: 5},
    }
    assert metrics.calculate_shared_low_coverage(cov, 10, threshold=1) == [[2, 9]]


def test_calculate_shared_low_coverage_all_low():
    """Every position low in all samples."""
    cov = {
        "s1": {},
        "s2": {},
    }
    assert metrics.calculate_shared_low_coverage(cov, 5, threshold=1) == [[0, 4]]


def test_calculate_shared_low_coverage_none():
    """No shared low-coverage regions at all."""
    cov = {
        "s1": {0: 5, 1: 5, 2: 5},
        "s2": {0: 5, 1: 0, 2: 5},
    }
    assert metrics.calculate_shared_low_coverage(cov, 3, threshold=1) == []


# ── Shared high-coverage across all samples ───────────────────────

def test_calculate_shared_high_coverage_basic():
    """Regions where ALL samples have coverage >= threshold."""
    cov = {
        "s1": {0: 5, 1: 10, 2: 10, 3: 5},
        "s2": {0: 5, 1: 10, 2: 12, 3: 5},
    }
    # Only positions 1 and 2 have ALL samples >= 10
    assert metrics.calculate_shared_high_coverage(cov, 4, threshold=10) == [[1, 2]]


def test_calculate_shared_high_coverage_trailing():
    """Shared trailing high region to end of sequence."""
    cov = {
        "s1": {0: 5, 1: 10, 2: 10, 3: 10, 4: 10, 5: 10, 6: 10, 7: 10, 8: 10, 9: 10},
        "s2": {0: 5, 1: 10, 2: 10, 3: 10, 4: 10, 5: 10, 6: 10, 7: 10, 8: 10, 9: 10},
    }
    assert metrics.calculate_shared_high_coverage(cov, 10, threshold=10) == [[1, 9]]


def test_calculate_shared_high_coverage_all_high():
    """Every position high in all samples."""
    cov = {
        "s1": {0: 10, 1: 10, 2: 10},
        "s2": {0: 10, 1: 10, 2: 10},
    }
    assert metrics.calculate_shared_high_coverage(cov, 3, threshold=10) == [[0, 2]]


def test_calculate_shared_high_coverage_none():
    """No shared high-coverage regions at all."""
    cov = {
        "s1": {0: 5, 1: 10, 2: 5},
        "s2": {0: 5, 1: 8, 2: 5},
    }
    assert metrics.calculate_shared_high_coverage(cov, 3, threshold=10) == []
