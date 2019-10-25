import numpy as np
import pandas as pd
import pkg_resources
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import spearmanr
from crispy import CrispyPlot, QCplot, Utils
from crispy.CRISPRData import CRISPRDataSet, ReadCounts


DPATH = pkg_resources.resource_filename("data", "moi/")

if __name__ == "__main__":
    # - Samplesheet
    #
    ss = pd.read_excel(f"{DPATH}/samplesheet.xlsx", index_col=0).query(
        "cas9_activity == 90"
    )

    order = [
        "MOI15 R1 exp",
        "MOI15 R3 exp",
        "MOI30 R2 exp",
        "MOI30 R3 exp",
        "MOI60 R1 exp",
        "MOI60 R2 exp",
        "MOI60 R3 exp",
        "MOI30 R1 screen",
        "MOI30 R2 screen",
        "MOI30 R3 screen",
    ]
    palette = ss.groupby("name")["palette"].first()

    # - Counts
    #
    counts = pd.concat(
        [
            pd.read_csv(
                f"{DPATH}/raw_counts/{f}.read_count.tsv.gz", sep="\t", index_col=0
            )
            .drop(columns=["gene"])
            .add_prefix(f"{ss.loc[f, 'name']}_")
            for f in ss.index
        ],
        axis=1,
        sort=False,
    )
    counts.columns = [
        c.split("_")[1] if c.endswith(".plasmid") else c.split("_")[0] for c in counts
    ]
    counts = counts.loc[:, ~counts.columns.duplicated(keep="last")]
    counts.to_csv(f"{DPATH}/moi_cas90_raw_counts.csv.gz", compression="gzip")

    # - Experiment details
    #
    moi = dict(
        name="HT-29 MOI",
        read_counts="moi_cas90_raw_counts.csv.gz",
        library="Yusa_v1.csv.gz",
        plasmids=["ERS717283.plasmid"],
        samplesheet="samplesheet.xlsx",
    )

    counts = CRISPRDataSet(moi, ddir=DPATH)

    # - Fold-changes
    #
    fc = (
        counts.counts.remove_low_counts(counts.plasmids)
        .norm_rpm()
        .foldchange(counts.plasmids)
    )

    fc_gene = fc.groupby(counts.lib.reindex(fc.index)["Gene"]).mean()

    fc_gene_scaled = ReadCounts(fc_gene).scale()

    # - sgRNAs counts
    #
    count_thres = 10

    plot_df = (
        pd.concat(
            [
                counts.counts.sum().rename("Total reads"),
                (counts.counts > count_thres).sum().rename("Guides threshold"),
            ],
            axis=1,
            sort=False,
        ).dropna().loc[order].reset_index()
    )

    for x in ["Total reads", "Guides threshold"]:
        plt.figure(figsize=(2, 1.5), dpi=600)

        sns.barplot(
            x=x,
            y="index",
            orient="h",
            linewidth=0,
            saturation=1,
            order=order,
            data=plot_df,
            palette=palette[order],
        )
        plt.grid(True, ls=":", lw=0.1, alpha=1.0, zorder=0, axis="x")
        plt.title(
            "Total raw counts"
            if x == "Total reads"
            else f"sgRNAs with counts > {count_thres}"
        )
        plt.xlabel("Total counts (sum)" if x == "Total reads" else "Number of sgRNAs")
        plt.ylabel("")

        plt.savefig(
            f"{DPATH}/reports/rawcounts_{x.replace(' ', '_')}_barplot.pdf",
            bbox_inches="tight",
        )
        plt.close("all")

    # - Fold-changes boxplots
    #
    for n, df in [("sgRNA fold-change", fc), ("Gene fold-change", fc_gene)]:
        plot_df = df[order].unstack().rename("fc").reset_index()
        plot_df.columns = ["sample", "sgRNA", "fc"]

        plt.figure(figsize=(2, 1.5), dpi=600)
        sns.boxplot(
            "fc",
            "sample",
            orient="h",
            data=plot_df,
            order=order,
            palette=palette[order],
            saturation=1,
            showcaps=False,
            boxprops=dict(lw=0.3),
            medianprops=dict(lw=0.3),
            flierprops=CrispyPlot.FLIERPROPS,
            whiskerprops=dict(lw=0.3),
        )
        plt.xlabel("Fold-change (log2)")
        plt.ylabel("")
        plt.grid(True, ls=":", lw=0.1, alpha=1.0, zorder=0, axis="both")
        plt.title(n)
        plt.savefig(
            f"{DPATH}/reports/boxplots_{n.replace(' ', '_')}.pdf", bbox_inches="tight"
        )
        plt.close("all")

    # - Fold-changes clustermap
    #
    for n, df in [("sgRNA fold-change", fc), ("Gene fold-change", fc_gene)]:
        plot_df = df[order].corr(method="spearman")
        sns.clustermap(
            plot_df,
            cmap="Spectral",
            annot=True,
            center=0,
            fmt=".2f",
            annot_kws=dict(size=4),
            figsize=(3, 3),
            lw=0.05,
            col_colors=pd.Series(palette)[plot_df.columns].rename("MOI"),
            row_colors=pd.Series(palette)[plot_df.index].rename("MOI"),
        )
        plt.suptitle(n)
        plt.savefig(
            f"{DPATH}/reports/clustermap_{n.replace(' ', '_')}.pdf", bbox_inches="tight"
        )
        plt.close("all")

    # - Recall gene lists
    #
    plot_df = fc_gene[order]

    for n, gset in [
        ("Essential", Utils.get_essential_genes()),
        ("Non-essential", Utils.get_non_essential_genes()),
    ]:
        # Aroc
        plt.figure(figsize=(2, 2), dpi=600)
        ax = plt.gca()
        _, stats_ess = QCplot.plot_cumsum_auc(
            plot_df, gset, palette=palette, legend_prop={"size": 4}, ax=ax
        )
        plt.title(f"{n} recall curve")
        plt.xlabel("Percent-rank of genes")
        plt.ylabel("Cumulative fraction")
        plt.grid(True, ls=":", lw=0.1, alpha=1.0, zorder=0, axis="both")
        plt.savefig(f"{DPATH}/reports/roccurves_{n}.pdf", bbox_inches="tight")
        plt.close("all")

        # Barplot
        df = pd.Series(stats_ess["auc"])[palette.index].rename("auc").reset_index()

        plt.figure(figsize=(2, 1), dpi=600)
        sns.barplot(
            "auc",

            "name",
            data=df,
            palette=palette,
            linewidth=0,
            saturation=1,
            orient="h",
        )
        plt.axvline(0.5, ls="-", lw=0.1, alpha=1.0, zorder=0, color="k")
        plt.xlabel("Area under the recall curve")
        plt.ylabel("")
        plt.title(n)
        plt.grid(True, ls=":", lw=0.1, alpha=1.0, zorder=0, axis="both")
        plt.savefig(f"{DPATH}/reports/roccurves_{n}_barplot.pdf", bbox_inches="tight")
        plt.close("all")

    # - Scatter grid
    #
    plot_df = fc_gene[order]

    def triu_plot(x, y, color, label, **kwargs):
        z = CrispyPlot.density_interpolate(x, y)

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
            f"R={r:.2f}\np={p:.1e}" if p != 0 else f"R={r:.2f}\np<0.0001",
            xy=(0.5, 0.5),
            xycoords=ax.transAxes,
            ha="center",
            va="center",
            fontsize=9,
        )

    grid = grid.map_upper(triu_plot, marker="o", edgecolor="", cmap="Spectral_r", s=2)
    grid.fig.subplots_adjust(wspace=0.05, hspace=0.05)
    plt.gcf().set_size_inches(12, 12)
    plt.savefig(
        f"{DPATH}/reports/pairplot_gene_fold_changes.png", bbox_inches="tight", dpi=600
    )
    plt.close("all")
