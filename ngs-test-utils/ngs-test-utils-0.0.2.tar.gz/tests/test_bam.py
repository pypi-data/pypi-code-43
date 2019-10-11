import unittest

import pysam

from ngs_test_utils import testcase


class TestBamTestCase(testcase.NgsTestCase):

    def test_get_flag_value(self):
        flag = self.get_flag_value(
            is_paired=True,
            is_proper_pair=True,
            is_unmapped=True,
            mate_is_unmapped=True,
            is_reverse=True,
            mate_is_reverse=True,
            is_read1=True,
            is_read2=True,
            is_secondary=True,
            is_qcfail=True,
            is_duplicate=True,
            is_supplementary=True,
        )
        self.assertEqual(flag, 4095)

    def test_make_bam(self):
        bam = self.make_bam(
            chroms=[("chr1", 1000), ("chr2", 1000)],
            segments=[
                dict(qname="r001", pos=100, cigar=[(0, 100)]),
                dict(qname="r002", pos=200, cigar=[(0, 100)]),
                dict(qname="r002", pos=200, cigar=[(0, 100)], is_unmapped=True),
            ],
        )
        with pysam.AlignmentFile(bam, mode="rb", require_index=True) as bamfile:
            self.assertEqual(bamfile.references, ('chr1', 'chr2'))
            self.assertEqual(bamfile.mapped, 2)
            self.assertEqual(bamfile.unmapped, 1)
            for read in bamfile.fetch():
                pass
