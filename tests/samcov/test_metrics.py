from samcov import metrics

def test_measure_centers_correct():
    dummy_coverage_map = {
        "s1": {
            1: 1,
            2: 3,
            5: 4
        },
        "s2": {
            1: 4,
            2: 6,
            5: 10
        },
        "s3": {
            1: 4,
            2: 6,
            5: 10
        }
    }
    expected_measures = {
        "mean": {
            1: 3,
            2: 5,
            5: 8
        },
        "median": {
            1: 4,
            2: 6,
            5: 10
        },
        "mode": {
            1: 4,
            2: 6,
            5: 10
        }
    }

    assert metrics.measure_centers(dummy_coverage_map, length=6) == expected_measures


def test_calculate_consecutive_low_coverage():
    dummy_coverage_map = {
        "s1": {
            0: 2,
            1: 1,
            2: 3,
            5: 4
        },
        "s2": {
            0: 2,
            1: 4,
            2: 6,
            6: 10
        },
        "s3": {
            1: 4,
            2: 6,
            5: 10,
            6: 4,
            20: 2
        }
    }
    expected_low_cov = {
        "s1": [[3,4]],
        "s2": [[3,5]],
        "s3": [[0,0], [3,4], [7,19]]
    }

    assert metrics.calculate_consecutive_low_coverage(dummy_coverage_map, 3) == expected_low_cov