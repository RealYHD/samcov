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