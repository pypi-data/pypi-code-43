#!/usr/bin/env python
# Copyright (C) 2019 Emanuel Goncalves

import os
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from collections import OrderedDict
from scipy.stats import gaussian_kde
from scipy.interpolate import interpn
from CrispyPlot import CrispyPlot
from CopyNumberCorrection import Crispy


if __name__ == '__main__':
    dfiles = [f for f in os.listdir("data/rescue/") if "35_DAYS" in f and f.endswith(".tsv.gz")]
    dfiles_headers = {f: list(pd.read_csv(f"data/rescue/{f}", index_col=0, sep="\t"))[1] for f in dfiles}

    dfs = {f: pd.read_csv(f"data/rescue/{f}", index_col=0, sep="\t") for f in dfiles}
    dfs_sgrna = pd.concat([dfs[f].drop(columns=["Plasmid_v1.1"]).iloc[:, 1].rename(f.split(".")[0]) for f in dfs], axis=1, sort=False)
    dfs_sgrna.to_excel(f"reports/rescue/rescue_sgrna_level_counts_mean.xlsx")

    #
    lib = pd.read_csv("data/rescue/KY_Library_v1.1_annotated.csv", index_col=0)

    highlights = {
        "SATA": {"SUPT3H": "#3683BB", "TADA1": "#e35621", "SUPT7L": "#37A257", "TAF6L": "#F667A8"},
        "WRN": {"WRNIP1": "#d95f0e"},
    }

    for k, genes in highlights.items():
        sgrnas = lib[lib["GENES"].isin(genes)]

        # -
        plot_df = pd.concat([dfs[f][dfiles_headers[f]].rename(f) for f in dfiles], axis=1)
        plot_df = np.log2(plot_df + 1)

        xy_lims = [0, plot_df.max().max()]

        f, axs = plt.subplots(2, 2, sharex='all', sharey='all', dpi=600, figsize=(4, 4))

        for i in [0, 1]:
            for j in [0, 1]:
                ax = axs[i][j]

                x = plot_df[[c for c in plot_df if f"_{(i+1)}_DOXY_" in c][0]]
                y = plot_df[[c for c in plot_df if f"_{(i+1)}_CTRL_" in c][0]]

                data, x_e, y_e = np.histogram2d(x, y, bins=20)
                z = interpn((0.5 * (x_e[1:] + x_e[:-1]), 0.5 * (y_e[1:] + y_e[:-1])), data, np.vstack([x, y]).T, method="splinef2d", bounds_error=False)

                idx = z.argsort()
                x, y, z = x[idx], y[idx], z[idx]

                ax.scatter(x, y, c=z, marker="o", edgecolor="", cmap="viridis_r", s=1, alpha=0.85)

                for g, df in sgrnas.groupby("GENES"):
                    ax.scatter(x.loc[df.index], y.loc[df.index], c=genes[g], marker="o", edgecolor="white", linewidth=.3, s=10, label=g)

                ax.set_ylim(xy_lims)
                ax.set_xlim(xy_lims)
                ax.plot(xy_lims, xy_lims, 'k-', lw=.3, zorder=0)

                ax.set_ylim([0, 13])

                if j == 0:
                    ax.set_ylabel(f"Control\n(replicate {i + 1})")

                if i == 1:
                    ax.set_xlabel(f"Doxycycline\n(replicate {j + 1})")

        handles, labels = plt.gca().get_legend_handles_labels()
        by_label = OrderedDict(zip(labels, handles))
        by_label = {k: by_label[k] for k in by_label if k in genes}
        plt.legend()
        plt.legend(
            by_label.values(), by_label.keys(), loc='center left', bbox_to_anchor=(1, 1), prop={'size': 8},
            frameon=False
        )

        plt.suptitle("CRISPR-Cas9 knockout of inducible WRN")
        plt.subplots_adjust(wspace=0.05, hspace=0.05)
        plt.savefig(f'reports/rescue/rawcounts_scatter_{k}.png', bbox_inches='tight')
        plt.close('all')

        # -
        plot_df = pd.concat([dfs[f][dfiles_headers[f]].rename(f) for f in dfiles], axis=1)
        plot_df = Crispy(plot_df).scale_raw_counts(plot_df)
        plot_df = np.log2(plot_df + 1)

        x = plot_df[[c for c in plot_df if f"_DOXY_" in c]].mean(1)
        y = plot_df[[c for c in plot_df if f"_CTRL_" in c]].mean(1)

        z = interpn((0.5 * (x_e[1:] + x_e[:-1]), 0.5 * (y_e[1:] + y_e[:-1])), data, np.vstack([x, y]).T, method="splinef2d",
                    bounds_error=False)

        idx = z.argsort()
        x, y, z = x[idx], y[idx], z[idx]

        xy_lims = [0, plot_df.max().max()]

        plt.figure(figsize=(1.5, 1.5), dpi=600)

        plt.scatter(x, y, c=z, marker="o", edgecolor="", cmap="viridis_r", s=1, alpha=0.85)

        for g, df in sgrnas.groupby("GENES"):
            plt.scatter(x.loc[df.index], y.loc[df.index], c=genes[g], marker="o", edgecolor="white", linewidth=.3, s=10, label=g)

        plt.ylim(xy_lims)
        plt.xlim(xy_lims)
        plt.plot(xy_lims, xy_lims, 'k-', lw=.3, zorder=0)

        plt.ylim([0, 10])

        plt.ylabel(f"Control\n(mean log2 counts)")
        plt.xlabel(f"Doxycycline\n(mean log2 counts)")

        handles, labels = plt.gca().get_legend_handles_labels()
        by_label = OrderedDict(zip(labels, handles))
        by_label = {k: by_label[k] for k in by_label if k in genes}
        plt.legend()
        plt.legend(
            by_label.values(), by_label.keys(), loc='center left', bbox_to_anchor=(1, .5), prop={'size': 6},
            frameon=False
        )

        plt.savefig(f'reports/rescue/rawcounts_scatter_averge_{k}.png', bbox_inches='tight')
        plt.close('all')

        # -
        controls = [
            "HCT116_C9_I-SG4_CL4_CRISPR_1_CTRL_35_DAYS.read_count.tsv.gz",
            "HCT116_C9_I-SG4_CL4_CRISPR_2_CTRL_35_DAYS.read_count.tsv.gz"
        ]

        doxys = [
            "HCT116_C9_I-SG4_CL4_CRISPR_1_DOXY_35_DAYS.read_count.tsv.gz",
            "HCT116_C9_I-SG4_CL4_CRISPR_2_DOXY_35_DAYS.read_count.tsv.gz"
        ]

        plot_df = pd.concat([dfs[f][dfiles_headers[f]].rename(f) for f in dfiles], axis=1)
        plot_df = Crispy(plot_df, plasmid=controls).fold_changes(qc_replicates_thres=None)
        plot_df = plot_df.sort_values(ascending=False).rename("fc").to_frame()
        plot_df["index"] = list(range(plot_df.shape[0]))

        plt.figure(figsize=(3, 1.5), dpi=600)

        plt.scatter(plot_df["index"], plot_df["fc"], c=CrispyPlot.PAL_DBGD[2], s=1, lw=0)

        for g, df in sgrnas.groupby("GENES"):
            plt.scatter(
                plot_df.loc[df.index, "index"], plot_df.loc[df.index, "fc"], c=genes[g], marker="o", edgecolor="white",
                linewidth=.1, s=3, label=g
            )

        plt.axhline(0, ls='-', lw=.1, zorder=0, color='black')

        plt.ylabel("Doxy / Control\n(log2 fold-changes)")

        handles, labels = plt.gca().get_legend_handles_labels()
        by_label = OrderedDict(zip(labels, handles))
        by_label = {k: by_label[k] for k in by_label if k in genes}
        plt.legend()
        plt.legend(
            by_label.values(), by_label.keys(), loc=1, prop={'size': 6}, frameon=False
        )

        plt.gca().axes.xaxis.set_visible(False)

        plt.savefig(f'reports/rescue/rawcounts_scatter_foldchange_{k}.png', bbox_inches='tight')
        plt.close('all')
