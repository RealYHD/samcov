from samcov import count

def test_count_sam_positions_returns_list():
    result = count.count_sam_positions("tests/resources/HG00096.chrom11.bam")
    assert len(result) > 0
    assert isinstance(result, list)

def test_count_all_sample_positions_returns_dictionary():
    result = count.count_all_sam_positions(["tests/resources/HG00096.chrom11.bam"])
    assert isinstance(result, dict)