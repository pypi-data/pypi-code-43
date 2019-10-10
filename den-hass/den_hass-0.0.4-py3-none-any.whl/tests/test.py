from unittest import TestCase

import denhub

class TestJoke(TestCase):
    def test_is_string(self):
        s = denhub.connect("192.168.86.24", "479b247c-fcab-44f8-bac5-be7630a28f4b", "f19a3953af0ca86e0f29c9d2adeb52")
        self.assertFalse(denhub.is_on("7039ee52-d25a-59c5-b957-844ff067233f","0"))