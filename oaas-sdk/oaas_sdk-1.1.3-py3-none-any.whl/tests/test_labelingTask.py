from unittest import TestCase

import oaas_sdk


class TestLabelingTask(TestCase):
    def test_get_labeling_solutions(self):
        assert len(oaas_sdk.sdk.get_labeling_solutions()) > 1
        assert 'verified' in oaas_sdk.sdk.get_labeling_solutions()  ##TODO these shoudl be verified and unverified
        assert 'unverified' in oaas_sdk.sdk.get_labeling_solutions() ##TODO these should be verified and unverified

    def test_get_companies(self):
        assert len(oaas_sdk.sdk.get_companies('verified', 'search')) > 200 ##TODO these shoudl be verified and unverified
        assert len(oaas_sdk.sdk.get_companies('unverified', 'search')) > 1500 ##TODO these shoudl be verified and unverified
