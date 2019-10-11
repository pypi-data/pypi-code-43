import unittest

from ngs_test_utils import testcase


class TestFastaTestCase(testcase.NgsTestCase):

    def test_make_fasta_sequence(self):
        seq = self.make_fasta_sequence(20, include_n=False, rnd_seed=42)
        self.assertEqual(len(seq), 20)
        self.assertEqual(seq, 'GTAGGTAAGCGGGGTATTTG')

        seq = self.make_fasta_sequence(20, include_n=True, rnd_seed=42)
        self.assertEqual(len(seq), 20)
        self.assertEqual(seq, 'TNGNNCGGGNTGNCTCTNAT')

    def test_make_fasta(self):
        # headers=None, sequences=None
        fasta = self.make_fasta(sequences=None, headers=None, num_sequences=3, seq_len=20, rnd_seed=42)
        self.assertEqual(self.tsv_to_list(fasta), [
            ['>1'],
            ['CATTATGCTCGATCAGGCCG'],
            ['>2'],
            ['CTTTACGCCTTTCTTTGATG'],
            ['>3'],
            ['CTTTGGGGCACTTAACTCCC']
        ])
