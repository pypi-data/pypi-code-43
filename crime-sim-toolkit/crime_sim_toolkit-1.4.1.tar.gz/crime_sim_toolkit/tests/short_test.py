import os
import json
import unittest
from unittest.mock import patch
import numpy as np
import pandas as pd
import folium
from crime_sim_toolkit import vis_utils, utils
import crime_sim_toolkit.initialiser as Initialiser
import crime_sim_toolkit.poisson_sim as Poisson_sim
import pkg_resources

# specified for directory passing test
test_dir = os.path.dirname(os.path.abspath(__file__))

# Could be any dot-separated package/module name or a "Requirement"
resource_package = 'crime_sim_toolkit'

class Test(unittest.TestCase):


    def test_moving_window_datetime(self):

        self.week = pd.to_datetime("2017-01-01")

        self.test1 = [x.strftime("%Y-%m-%d") for x in Poisson_sim.Poisson_sim.moving_window_datetime(self.week, window=1)]

        self.test2 = [x.strftime("%Y-%m-%d") for x in Poisson_sim.Poisson_sim.moving_window_datetime(self.week, window=0)]

        self.test3 = [x.strftime("%Y-%m-%d") for x in Poisson_sim.Poisson_sim.moving_window_datetime(self.week, window=2)]

        self.assertEqual(self.test1, ["2017-01-01",
                                      "2017-01-02",
                                      "2016-12-31"])

        self.assertEqual(self.test2, ["2017-01-01"])

        self.assertEqual(self.test3, ["2017-01-01",
                                      "2017-01-02",
                                      "2016-12-31",
                                      "2017-01-03",
                                      "2016-12-30"]
                                      )


if __name__ == "__main__":
    unittest.main(verbosity=2)
