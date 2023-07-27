from samcov import count

def test_count_sam_positions_returns_list():
    result, max_length = count.count_sam_positions("tests/resources/mt.sorted.bam")
    assert len(result) > 0
    assert isinstance(result, dict)
    assert max_length > 0

def test_count_all_sample_positions_returns_dictionary():
    result, max_length = count.count_all_sam_positions(["tests/resources/mt.sorted.bam"])
    assert isinstance(result, dict)
    assert max_length > 0