from samcov import consensus

def test_generate_consensus_correct_call():
    consensus.generate_consensus("tests/resources/mt.sorted.bam", "tests/resources/mt.sorted.fasta")