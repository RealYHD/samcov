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
