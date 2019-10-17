import unittest

import fastq_vcf_pipeline
from mock import patch, MagicMock


class TestPipelineREADLengthMethod(unittest.TestCase):

    @patch('__builtin__.open', spec=open)
    def test_interface_format(self, mock_open):
        handle1 = MagicMock()
        handle1.__enter__.return_value.__iter__.return_value = ('aa', 100*'A')
        handle1.__exit__.return_value = False
        handle2 = MagicMock()
        handle2.__enter__.return_value.__iter__.return_value = ('AA', 10*'C')
        handle2.__exit__.return_value = False
        handle3 = MagicMock()
        handle3.__enter__.return_value.__iter__.return_value = ('aa', 100*'A')
        handle3.__exit__.return_value = False
        handle4 = MagicMock()
        handle4.__enter__.return_value.__iter__.return_value = ('AA', 100*'C')
        handle4.__exit__.return_value = False
        mock_open.side_effect = (handle1, handle2, handle3, handle4)
        self.assertEqual(
            fastq_vcf_pipeline.get_reads_length("AAAAA,BBBB"'bbb,BBBBB'), 100)

    @patch('gzip.open', spec=open)
    def test_interface_gz(self, mock_open):
        handle1 = MagicMock()
        handle1.__enter__.return_value.__iter__.return_value = ('aa', 130*'A')
        handle1.__exit__.return_value = False
        handle2 = MagicMock()
        handle2.__enter__.return_value.__iter__.return_value = ('AA', 130*'C')
        handle2.__exit__.return_value = False
        handle3 = MagicMock()
        handle3.__enter__.return_value.__iter__.return_value = ('aa', 130*'A')
        handle3.__exit__.return_value = False
        handle4 = MagicMock()
        handle4.__enter__.return_value.__iter__.return_value = ('AA', 130*'C')
        handle4.__exit__.return_value = False
        mock_open.side_effect = (handle1, handle2, handle3, handle4)
        self.assertEqual(
            fastq_vcf_pipeline.get_reads_length("AAAAA.gz,BBBB.gz"'bbb.gz,BBBBB.gz'), 150)
        # with open("123") as F:

        #    print (F.readlines())
    def test_all_reads_list(self):
        data = {
            'N': {'R1': ['NR1L1,NR1L2,NR1L3,NR1L4'], 'R2': ['NR2L1,NR2L2,NR2L3,NR2L4']},
            'T': {'R1': ['TR1L1,TR1L2'], 'R2': ['TR2L1,TR2L2']}
        }
        re_data = ['NR1L1,NR1L2,NR1L3,NR1L4',
                   'NR2L1,NR2L2,NR2L3,NR2L4',
                   'TR1L1,TR1L2','TR2L1,TR2L2']

        self.assertItemsEqual(re_data, fastq_vcf_pipeline.get_all_reads(data))


if __name__ == "__main__":
    unittest.main()
