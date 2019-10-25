from unittest import *
import sys
sys.path.append("..")
from pycout import *  # cout, endl
from pycout.cout import Cout


class Test(TestCase):
    def test(self):
        cout << 1000 << "hellos to the world !" << endl;

        self.assertIsInstance(
            cout << "Hello" << " Worlds !" << endl,
            Cout,
            "cout chain must be of type _Cout"
        )
