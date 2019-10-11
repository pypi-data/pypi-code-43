from ngs_test_utils import testcase


class TestGtfTestCase(testcase.NgsTestCase):

    def test_make_gtf(self):
        gtf = self.make_gtf([
            dict(feature="intron", start=100, end=200, strand="+", gene_id="G0001"),
            dict(feature="intron", start=400, end=500, strand="-", gene_name="BRCA2"),
        ])

        content = self.tsv_to_list(gtf)
        self.assertEqual(len(content), 2)
        self.assertEqual(content, [
            ['chr1', 'UCSC', 'intron', '101', '200', '1', '+', '.', 'gene_id "G0001";'],
            ['chr1', 'UCSC', 'intron', '401', '500', '1', '-', '.', 'gene_name "BRCA2";']
        ])
