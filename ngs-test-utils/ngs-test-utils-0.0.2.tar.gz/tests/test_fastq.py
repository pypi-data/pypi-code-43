from ngs_test_utils import testcase


class TestFastqTestCase(testcase.NgsTestCase):

    def test_make_quality_scores(self):
        seq = self.make_quality_scores(10, rnd_seed=42)
        self.assertEqual(len(seq), 10)
        self.assertEqual(seq, 'G=/(5G37++')
