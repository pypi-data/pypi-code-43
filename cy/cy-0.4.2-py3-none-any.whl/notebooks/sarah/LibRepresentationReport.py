# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.3'
#       jupytext_version: 1.0.0
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %matplotlib inline
# %autosave 0
# %load_ext autoreload
# %autoreload 2

import logging
import pandas as pd
import pkg_resources
import matplotlib.pyplot as plt
from crispy.LibRepresentationReport import LibraryRepresentaion


LOG = logging.getLogger("Crispy")
RPATH = pkg_resources.resource_filename("notebooks", "sarah/reports/")


if __name__ == "__main__":
    lib_counts = pd.read_csv(
        f"{RPATH}/sample1.count.txt", sep="\t", index_col=0
    ).dropna()

    librep = LibraryRepresentaion(lib_counts)

    gini_score = librep.gini()
    LOG.info(f"Gini score = {gini_score:.2f}")

    librep.boxplot()
    plt.savefig(f"{RPATH}/librep_boxplot.pdf", bbox_inches="tight", dpi=600)
    plt.close("all")

    percentile_score = librep.percentile()
    LOG.info(f"Percentile 95% = {percentile_score:.2f}")

    dropout_rate = librep.dropout_rate() * 100
    LOG.info(f"Dropout rate = {dropout_rate:.2f}%")

    librep.lorenz_curve()
    plt.savefig(f"{RPATH}/librep_lorenz_curve.pdf", bbox_inches="tight", dpi=600)
    plt.close("all")
