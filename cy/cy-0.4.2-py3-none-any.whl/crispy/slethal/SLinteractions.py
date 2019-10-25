#!/usr/bin/env python
# Copyright (C) 2019 Emanuel Goncalves

import logging
import numpy as np
import DataImporter
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from crispy import logger, dpath


class SLinteractions:
    def __init__(self):
        # Import data-sets
        self.crispr_obj = DataImporter.CRISPRComBat()
        self.gexp_obj = DataImporter.GeneExpression()

        self.samples = list(
            set.intersection(
                set(self.gexp_obj.get_data().columns),
                set(self.crispr_obj.get_data().columns),
            )
        )

        logger.log(logging.INFO, f"#(Samples)={len(self.samples)}")

        # Import samplesheet
        self.samplesheet = DataImporter.Sample()

        # Filter
        self.gexp = self.gexp_obj.filter(subset=self.samples)
        self.crispr = self.crispr_obj.filter(subset=self.samples, scale=True)
