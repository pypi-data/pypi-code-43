"""Test utilities for FASTQ files."""
import numpy


class FastqTestCaseMixin:
    """Mixin for manipulation of FASTA files in tests."""

    @staticmethod
    def make_quality_scores(size, min_chr=33, max_chr=74, rnd_seed=None):
        """Make random quality scores of length `size`."""
        numpy.random.seed(rnd_seed)
        scores = [chr(i) for i in range(min_chr, max_chr + 1)]
        return "".join(numpy.random.choice(scores, size))
