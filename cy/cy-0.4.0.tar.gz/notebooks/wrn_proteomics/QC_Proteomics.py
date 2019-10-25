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

import numpy as np
import pandas as pd
import pkg_resources
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import spearmanr
from scipy.interpolate import interpn
from crispy.CrispyPlot import CrispyPlot

DPATH = pkg_resources.resource_filename("data", "wrn_proteomics/")
RPATH = pkg_resources.resource_filename("notebooks", "wrn_proteomics/reports/")

if __name__ == "__main__":
    prot_ss = pd.read_excel(f"{DPATH}/proteomics_samplesheet.xlsx")
    prot_matrix = pd.read_excel(f"{DPATH}/GP01_TMT11plex_Full_MasterProteins.xlsx")

    prot_idmap = (
        prot_matrix.set_index("Accession")["Gene Symbol"]
        .dropna()
        .apply(lambda v: v.split("; ")[0])
    )

    prot_values = prot_matrix[prot_matrix["Protein FDR Confidence"] == "High"]
    prot_values = prot_values.set_index("Accession")[prot_ss["samples_scaled"]].dropna()
    prot_values = prot_values.rename(
        columns=prot_ss.set_index("samples_scaled")["name"]
    )

    pd.concat([prot_values, prot_idmap], axis=1, sort=False).dropna().to_csv(
        f"{RPATH}/proteomics_scaled.xlsx"
    )

    prot_palette = prot_ss.set_index("name")["palette"]

    # Comparisons
    #
    comp = {
        "doxy57_vs_ctrl57": pd.concat(
            [
                prot_values[["DOXY57h1", "DOXY57h2"]],
                prot_values[["CTRL57h1"]],
                np.log2(
                    prot_values[["DOXY57h1", "DOXY57h2"]].mean(1)
                    / prot_values[["CTRL57h1"]].mean(1)
                ).rename("FC"),
                prot_idmap,
            ],
            axis=1,
            sort=False,
        )
        .dropna()
        .sort_values("FC"),
        "doxy57_vs_doxy36": pd.concat(
            [
                prot_values[["DOXY57h1", "DOXY57h2"]],
                prot_values[["DOXY36h1", "DOXY36h2"]],
                np.log2(
                    prot_values[["DOXY57h1", "DOXY57h2"]].mean(1)
                    / prot_values[["DOXY36h1", "DOXY36h2"]].mean(1)
                ).rename("FC"),
                prot_idmap,
            ],
            axis=1,
            sort=False,
        )
        .dropna()
        .sort_values("FC"),
        "doxy36_vs_ctrl36": pd.concat(
            [
                prot_values[["DOXY36h1", "DOXY36h2"]],
                prot_values[["CTRL36h1", "CTRL36h2"]],
                np.log2(
                    prot_values[["DOXY36h1", "DOXY36h2"]].mean(1)
                    / prot_values[["CTRL36h1", "CTRL36h2"]].mean(1)
                ).rename("FC"),
                prot_idmap,
            ],
            axis=1,
            sort=False,
        )
        .dropna()
        .sort_values("FC"),
        "doxy39_vs_ctrl36": pd.concat(
            [
                prot_values[["DOXY39h1", "DOXY39h2"]],
                prot_values[["CTRL36h1", "CTRL36h2"]],
                np.log2(
                    prot_values[["DOXY39h1", "DOXY39h2"]].mean(1)
                    / prot_values[["CTRL36h1", "CTRL36h2"]].mean(1)
                ).rename("FC"),
                prot_idmap,
            ],
            axis=1,
            sort=False,
        )
        .dropna()
        .sort_values("FC"),
        "doxy45_vs_ctrl36": pd.concat(
            [
                prot_values[["DOXY45h1", "DOXY45h2"]],
                prot_values[["CTRL36h1", "CTRL36h2"]],
                np.log2(
                    prot_values[["DOXY45h1", "DOXY45h2"]].mean(1)
                    / prot_values[["CTRL36h1", "CTRL36h2"]].mean(1)
                ).rename("FC"),
                prot_idmap,
            ],
            axis=1,
            sort=False,
        )
        .dropna()
        .sort_values("FC"),
        "doxy57_vs_ctrl36": pd.concat(
            [
                prot_values[["DOXY57h1", "DOXY57h2"]],
                prot_values[["CTRL36h1", "CTRL36h2"]],
                np.log2(
                    prot_values[["DOXY57h1", "DOXY57h2"]].mean(1)
                    / prot_values[["CTRL36h1", "CTRL36h2"]].mean(1)
                ).rename("FC"),
                prot_idmap,
            ],
            axis=1,
            sort=False,
        )
        .dropna()
        .sort_values("FC"),
    }

    comp["doxy_vs_ctrl36"] = (
        pd.concat(
            [
                prot_values[
                    [
                        "CTRL36h1",
                        "CTRL36h2",
                        "DOXY36h1",
                        "DOXY36h2",
                        "DOXY39h1",
                        "DOXY39h2",
                        "DOXY45h1",
                        "DOXY45h2",
                        "DOXY57h1",
                        "DOXY57h2",
                    ]
                ],
                pd.concat(
                    [
                        comp[c]["FC"]
                        for c in [
                            "doxy36_vs_ctrl36",
                            "doxy39_vs_ctrl36",
                            "doxy45_vs_ctrl36",
                            "doxy57_vs_ctrl36",
                        ]
                    ],
                    axis=1,
                )
                .mean(1)
                .rename("AvgFC"),
                prot_idmap,
            ],
            axis=1,
            sort=False,
        )
        .dropna()
        .sort_values("AvgFC")
    )

    for c in comp:
        comp[c].to_excel(f"{RPATH}/fold_change_{c}.xlsx")

    # Clustermap
    #
    plot_df = prot_values.corr()

    g = sns.clustermap(
        plot_df,
        cmap="Spectral",
        center=0,
        annot=True,
        fmt=".2f",
        annot_kws=dict(size=4),
        figsize=(4, 4),
        lw=0.05,
        col_colors=prot_palette.loc[plot_df.columns],
        row_colors=prot_palette[plot_df.index],
    )
    plt.savefig(f"{RPATH}/clustermap_wrn_proteomics.pdf", bbox_inches="tight")
    plt.close("all")

    # Boxplots
    #
    plt.figure(figsize=(2, 3), dpi=600)
    sns.boxplot(
        orient="h",
        data=prot_values,
        palette=prot_palette,
        saturation=1,
        showcaps=False,
        notch=True,
        flierprops=CrispyPlot.FLIERPROPS,
    )
    plt.savefig(f"{RPATH}/boxplot_wrn_proteomics.pdf", bbox_inches="tight")
    plt.close("all")

    # Scatter
    #
    plot_df = prot_values.copy()

    def triu_plot(x, y, color, label, **kwargs):
        data, x_e, y_e = np.histogram2d(x, y, bins=20)
        z = interpn(
            (0.5 * (x_e[1:] + x_e[:-1]), 0.5 * (y_e[1:] + y_e[:-1])),
            data,
            np.vstack([x, y]).T,
            method="splinef2d",
            bounds_error=False,
        )

        idx = z.argsort()
        x, y, z = x[idx], y[idx], z[idx]

        plt.scatter(x, y, c=z, **kwargs)

        plt.axhline(0, ls=":", lw=0.1, c="#484848", zorder=0)
        plt.axvline(0, ls=":", lw=0.1, c="#484848", zorder=0)

        (x0, x1), (y0, y1) = plt.xlim(), plt.ylim()
        lims = [max(x0, y0), min(x1, y1)]
        plt.plot(lims, lims, ls=":", lw=0.1, c="#484848", zorder=0)

    def diag_plot(x, color, label, **kwargs):
        sns.distplot(x, label=label)

    grid = sns.PairGrid(plot_df, height=1.1, despine=False)

    grid.map_diag(diag_plot, kde=True, hist_kws=dict(linewidth=0), bins=30)

    for i, j in zip(*np.tril_indices_from(grid.axes, -1)):
        ax = grid.axes[i, j]
        r, p = spearmanr(plot_df.iloc[:, i], plot_df.iloc[:, j])
        ax.annotate(
            f"R={r:.2f}\np={p:.1e}",
            xy=(0.5, 0.5),
            xycoords=ax.transAxes,
            ha="center",
            va="center",
            fontsize=9,
        )

    grid = grid.map_upper(triu_plot, marker="o", edgecolor="", cmap="Spectral_r", s=2)

    grid.fig.subplots_adjust(wspace=0.05, hspace=0.05)

    plt.savefig(f"{RPATH}/scatter_wrn_proteomics.png", bbox_inches="tight")
    plt.close("all")
