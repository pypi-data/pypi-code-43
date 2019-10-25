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
import numpy as np
import pandas as pd
import pkg_resources
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import spearmanr
from adjustText import adjust_text
from scipy.interpolate import interpn
from crispy import CrispyPlot, QCplot, Utils
from crispy.CRISPRData import CRISPRDataSet, ReadCounts

LOG = logging.getLogger("Crispy")
DPATH = pkg_resources.resource_filename("data", "organoids/sarah/")
RPATH = pkg_resources.resource_filename("notebooks", "sarah/reports/")

if __name__ == "__main__":
    organoids = dict(
        name="MHC orgs",
        read_counts="raw_counts.csv.gz",
        library="Yusa_v1.1.csv.gz",
        plasmids=["Plasmid_v1.1"],
        samplesheet="samplesheet.xlsx",
    )

    # - Imports
    ss = pd.read_excel(f"{DPATH}/{organoids['samplesheet']}", index_col=0).query(
        "experiment == 2"
    )
    dset = CRISPRDataSet(organoids, ddir=DPATH)

    # -
    samples = list(set(dset.counts).intersection(ss.index))
    palette = ss.groupby("name")["color"].first()

    # - Fold-changes
    counts = dset.counts[samples].rename(columns=ss["name"])

    counts_sgrna = pd.concat([dset.lib["Gene"], counts], axis=1, sort=False)
    counts_sgrna.to_excel(f"{RPATH}/sgrnas_counts.xlsx")

    counts_gene = counts.groupby(dset.lib["Gene"]).median()
    counts_gene.to_excel(f"{RPATH}/gene_counts.xlsx")

    # - Genes : sgRNAs
    sgrnas_counts = counts.groupby(dset.lib["Gene"]).count().iloc[:, 0]
    genes_counts = list(sgrnas_counts[sgrnas_counts >= 3].index)

    # - Comparisons
    comparisons = [
        ("IFNg_MHC_LOW", "IFNg_MHC_HI"),
        ("IFNg_MHC_LOW", "MHC_LOW"),
        ("IFNg_MHC_HI", "MHC_HI"),
    ]

    # - Clustermap gene fold-change
    plot_df = (counts_gene > 0).astype(int)
    plot_df = plot_df[plot_df.std(1) > 0].loc[:, plot_df.std(0) > 0]
    plot_df = plot_df.corr()

    sns.clustermap(
        plot_df,
        cmap="Spectral",
        annot=True,
        center=0,
        fmt=".2f",
        annot_kws=dict(size=4),
        figsize=(3, 3),
        lw=0.05,
        col_colors=palette[plot_df.columns].rename("Sample"),
        row_colors=palette[plot_df.index].rename("Sample"),
    )
    plt.savefig(f"{RPATH}/clustermap_gene_fold_change.pdf", bbox_inches="tight")
    plt.close("all")

    # -
    for org, org_df in ss.groupby("sample"):
        for cond1, cond2 in comparisons:
            cond1, cond2 = f"{org}_{cond1}_2", f"{org}_{cond2}_2"
            LOG.info(f"{org}: {cond1} vs {cond2}")

            plot_df = pd.concat(
                [
                    counts_gene.loc[genes_counts][cond1],
                    counts_gene.loc[genes_counts][cond2],
                ],
                axis=1,
                sort=False,
            )
            plot_df = plot_df[plot_df.std(1) > 0]
            plot_df["density"] = CrispyPlot.density_interpolate(
                plot_df[cond1], plot_df[cond2]
            )
            plot_df = plot_df.sort_values("density")

            ax = plt.gca()

            ax.scatter(
                plot_df[cond1],
                plot_df[cond2],
                c=plot_df["density"],
                marker="o",
                edgecolor="",
                cmap="Spectral_r",
                s=2,
            )

            ax.set_xlabel(cond1)
            ax.set_ylabel(cond2)
            ax.set_title(org)
            ax.grid(True, ls=":", lw=0.1, alpha=1.0, zorder=0, axis="both")

            plt.gcf().set_size_inches(2, 2)

            genes = {
                g
                for c in [cond1, cond2]
                for g in plot_df[c].sort_values(ascending=False).head(10).index
            }

            texts = [
                plt.text(
                    plot_df.loc[g, cond1],
                    plot_df.loc[g, cond2],
                    g,
                    color="k",
                    fontsize=2,
                )
                for g in genes
            ]
            adjust_text(
                texts,
                precision=0.001,
                expand_text=(1.01, 1.05),
                expand_points=(1.01, 1.05),
                force_text=(0.01, 0.25),
                force_points=(0.01, 0.25),
                arrowprops=dict(arrowstyle="-", color="k", alpha=0.75, lw=0.3),
            )

            plt.savefig(
                f"{RPATH}/pairplot_{org}_{cond1}_{cond2}.pdf", bbox_inches="tight"
            )
            plt.close("all")

    # -
    for org, org_df in ss.groupby("sample"):
        conditions = org_df["condition"]

        f, axs = plt.subplots(
            len(conditions), len(conditions), sharex="none", sharey="none", dpi=600
        )

        plt.gcf().set_size_inches(8, 8)
        plt.subplots_adjust(wspace=0.05, hspace=0.05)

        for i, cond_i in enumerate(conditions):
            for j, cond_j in enumerate(conditions):
                if i >= j:
                    axs[i, j].axis("off")
                    continue

                LOG.info(f"{org}: {cond_i} ({i}) vs {cond_j} ({j})")

                ax = axs[i, j]

                plot_df = pd.concat(
                    [
                        counts_gene[f"{org}_{cond_i}_2"].rename(cond_i),
                        counts_gene[f"{org}_{cond_j}_2"].rename(cond_j),
                    ],
                    axis=1,
                    sort=False,
                ).loc[genes_counts]
                plot_df = plot_df[plot_df.std(1) > 0]
                plot_df["density"] = CrispyPlot.density_interpolate(
                    plot_df[cond_j], plot_df[cond_i]
                )
                plot_df = plot_df.sort_values("density")

                ax.scatter(
                    plot_df[cond_j],
                    plot_df[cond_i],
                    c=plot_df["density"],
                    marker="o",
                    edgecolor="",
                    cmap="Spectral_r",
                    s=2,
                )

                ax.set_xlabel(f"{cond_j.replace('_', ' ')}\nGene Median Raw Counts" if (j - i) == 1 else "", fontsize=5)
                ax.set_ylabel(f"{cond_i.replace('_', ' ')}\nGene Median Raw Counts" if (j - i) == 1 else "", fontsize=5)

                if (j - i) != 1:
                    ax.axes.get_yaxis().set_ticks([])

                ax.set_title("" if i != 0 else org)
                ax.grid(True, ls=":", lw=0.1, alpha=1.0, zorder=0, axis="both")

                genes = {
                    g
                    for c in [cond_j, cond_i]
                    for g in plot_df[c].sort_values(ascending=False).head(10).index
                }

                texts = [
                    ax.text(
                        plot_df.loc[g, cond_j],
                        plot_df.loc[g, cond_i],
                        g,
                        color="k",
                        fontsize=4,
                    )
                    for g in genes
                ]
                adjust_text(
                    texts,
                    arrowprops=dict(arrowstyle="-", color="k", alpha=0.75, lw=0.3),
                    ax=ax,
                )

        plt.savefig(f"{RPATH}/pairplot_{org}.png", bbox_inches="tight")
        plt.close("all")

    # Copyright (C) 2019 Emanuel Goncalves
