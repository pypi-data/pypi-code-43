import crispy
import logging
import numpy as np
import pandas as pd
import pkg_resources
import seaborn as sns
import matplotlib.pyplot as plt
from scipy import stats
from crispy.QCPlot import QCplot
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
from sklearn.linear_model.base import LinearRegression

LOG = logging.getLogger("Crispy")

DPATH = pkg_resources.resource_filename("crispy", "data/")
RPATH = pkg_resources.resource_filename("notebooks", "depmap/reports/")

TCGA_GEXP_FILE = "/Users/eg14/Data/tcga/GSE62944_merged_expression_voom.tsv"
GDSC_GEXP_FILE = "/Users/eg14/Projects/dtrace/dtrace/data/genomic/rnaseq_voom.csv.gz"


def pc_labels(n):
    return [f"PC{i}" for i in np.arange(1, n + 1)]


def dim_reduction(
    df,
    pca_ncomps=50,
    tsne_ncomps=2,
    perplexity=30.0,
    early_exaggeration=12.0,
    learning_rate=200.0,
    n_iter=1000,
):
    df_pca = PCA(n_components=pca_ncomps).fit_transform(df.T)
    df_pca = pd.DataFrame(df_pca, index=df.T.index, columns=pc_labels(pca_ncomps))

    df_tsne = TSNE(
        n_components=tsne_ncomps,
        perplexity=perplexity,
        early_exaggeration=early_exaggeration,
        learning_rate=learning_rate,
        n_iter=n_iter,
    ).fit_transform(df_pca)
    df_tsne = pd.DataFrame(df_tsne, index=df_pca.index, columns=pc_labels(tsne_ncomps))

    return df_tsne, df_pca


def regressout(values, covariates):
    lm = LinearRegression().fit(covariates, values)
    return values - covariates.dot(lm.coef_) - lm.intercept_


if __name__ == "__main__":
    # GDSC imports
    #
    gdsc_ss = pd.read_csv(f"{DPATH}/model_list_latest.csv.gz", index_col=0)
    gdsc_ss["growth"] = (
        pd.read_csv(f"{DPATH}/growth_rates_rapid_screen_1536_v1.3.0_20190222.csv")
        .groupby("model_id")["GROWTH_RATE"]
        .mean()
    )

    gdsc_gexp = pd.read_csv(GDSC_GEXP_FILE, index_col=0)
    gdsc_tissue_pal = pd.read_csv(f"{DPATH}/tissue_palette.csv", index_col=0)["color"]

    # TCGA imports
    #
    tcga_gex = pd.read_csv(TCGA_GEXP_FILE, index_col=0, sep="\t")

    # GTEx gene median expression
    #
    gtex = pd.read_csv(
        f"{DPATH}/GTEx_Analysis_2017-06-05_v8_RNASeQCv1.1.9_gene_median_tpm.gct",
        sep="\t",
    )

    # Low and High expressed genes
    tcga_genes = (
        tcga_gex.loc[gdsc_gexp.index].median(1).dropna().sort_values(ascending=False)
    )

    gtex_genes = gtex[gtex["Description"].isin(gdsc_gexp.index)]
    gtex_genes = (
        np.log10(gtex_genes.drop(columns=["Name"]).groupby("Description").median().median(1).sort_values(ascending=False) + 1)
    )

    n = 500
    lh_genes = {
        "low": set(tcga_genes.tail(n).index).intersection(gtex_genes.tail(n).index),
        "high": set(tcga_genes.head(n).index).intersection(gtex_genes.head(n).index),
    }
    lh_genes_pal = {"low": "#ff6d59", "high": "#3cd2ff"}
    LOG.info(f"High: {len(lh_genes['high'])}; Low: {len(lh_genes['low'])}")

    # GTEx genes distribution
    #
    plt.figure(figsize=(2.5, 1.5), dpi=600)
    for s in lh_genes:
        sns.distplot(
            gdsc_gexp.loc[lh_genes[s]].mean(),
            hist=False,
            label=s,
            kde_kws={"cut": 0, "shade": True},
            color=lh_genes_pal[s],
        )
    plt.grid(True, ls=":", lw=0.1, alpha=1.0, zorder=0, axis="x")
    plt.xlabel("RNA-seq voom")
    plt.legend(frameon=False, title="TCGA", prop={"size": 4}).get_title().set_fontsize(
        "5"
    )
    plt.savefig(
        f"{RPATH}/gdsc_gexp_highlow_genes_hist.pdf",
        bbox_inches="tight",
        transparent=True,
    )
    plt.close("all")

    # GDSC tSNE
    #
    gdsc_gexp_tsne, gdsc_gexp_pca = dim_reduction(gdsc_gexp)

    # Regress-out covariates
    #
    covariates = pd.concat(
        [
            pd.get_dummies(gdsc_ss["tissue"]),
            gdsc_gexp_pca["PC1"],
            gdsc_ss["ploidy"],
            gdsc_ss["mutational_burden"],
        ],
        axis=1,
        sort=False,
    )
    covariates = covariates.loc[gdsc_gexp.columns].dropna()
    covariates = covariates.loc[:, covariates.std() != 0]

    samples = list(covariates.index)
    LOG.info(f"Samples={len(samples)}")

    #
    #
    kernels = {
        k: stats.gaussian_kde(gdsc_gexp.loc[lh_genes[k]].median())
        for k in ["low", "high"]
    }

    def discretise_genes(values, low_thres=0.25, high_thres=.25, verbose=0):
        df = values.sort_values()

        if verbose > 0:
            LOG.info(f"Sample: {df.name}")

        df_low = kernels["low"].pdf(df)
        df_low_n = np.argwhere(df_low > low_thres)
        df_low_n = 0 if len(df_low_n) == 0 else df_low_n[-1][0]
        df_low_disc = [1] * df_low_n + [0] * (len(df) - df_low_n)

        df_high = kernels["high"].pdf(df)
        df_high_n = np.argwhere(df_high > high_thres)
        df_high_n = 0 if len(df_high_n) == 0 else df_high_n[0][0]
        df_high_disc = [0] * df_high_n + [1] * (len(df) - df_high_n)

        return pd.DataFrame(
            {f"{df.name}_low": df_low_disc, f"{df.name}_high": df_high_disc},
            index=df.index,
        )

    gdsc_gexp_disc = pd.concat(
        [discretise_genes(gdsc_gexp[s], verbose=1) for s in gdsc_gexp],
        axis=1,
        sort=False,
    )

    #
    #
    mobem_gexp = {}
    for k in lh_genes:
        df = gdsc_gexp_disc.loc[:, gdsc_gexp_disc.columns.str.endswith(k)]
        df = df[df.sum(1) > 3]
        df.columns = [v.split("_")[0] for v in df.columns]
        mobem_gexp[k] = df

    # Recall curves
    #
    for s in lh_genes:
        plt.figure(figsize=(2, 2), dpi=600)

        ax = plt.gca()

        _, stats_ess = QCplot.plot_cumsum_auc(
            gdsc_gexp, lh_genes[s], legend=False, ax=ax
        )

        ax.set_xlabel("Percent-rank of genes")
        ax.set_ylabel("Cumulative fraction")

        plt.savefig(
            f"{RPATH}/gdsc_gexp_highlow_genes_recall_{s}.pdf", bbox_inches="tight"
        )
        plt.close("all")

    # GDSC tSNE plot
    #
    for n in ["tSNE", "PCA"]:
        plot_df = pd.concat(
            [gdsc_gexp_tsne if n == "tSNE" else gdsc_gexp_pca, gdsc_ss[["tissue"]]],
            axis=1,
            sort=False,
        ).dropna()

        plt.figure(figsize=(4, 4))
        for t, df in plot_df.groupby("tissue"):
            plt.scatter(
                df["PC1"],
                df["PC2"],
                c=gdsc_tissue_pal[t],
                marker="o",
                edgecolor="",
                s=5,
                label=t,
            )
        plt.title(f"{n} - GDSC GExp")
        plt.xlabel("Dimension 1")
        plt.ylabel("Dimension 2")
        plt.axis("off" if n == "tSNE" else "on")
        plt.legend(
            loc="center left",
            bbox_to_anchor=(1, 0.5),
            prop={"size": 4},
            frameon=False,
            title="Tissue",
        ).get_title().set_fontsize("5")
        plt.savefig(f"{RPATH}/gdsc_gexp_{n}.pdf", bbox_inches="tight", transparent=True)
        plt.close("all")

    #
    #
    plot_df = (
        gdsc_gexp_disc.sum()
        .reset_index()
        .rename(columns={"index": "sample", 0: "count"})
    )
    plot_df["type"] = plot_df["sample"].apply(lambda v: v.split("_")[1])

    plt.figure(figsize=(1.0, 2.0), dpi=600)
    sns.boxplot(
        "type",
        "count",
        data=plot_df,
        palette=lh_genes_pal,
        saturation=1,
        showcaps=False,
        flierprops=QCplot.FLIERPROPS,
        boxprops=dict(linewidth=0.3),
        whiskerprops=dict(linewidth=0.3),
        notch=True,
    )
    plt.grid(True, ls=":", lw=0.1, alpha=1.0, zorder=0, axis="y")
    plt.savefig(
        f"{RPATH}/gdsc_gexp_disc_count_boxplots.pdf",
        bbox_inches="tight",
        transparent=True,
    )
    plt.close("all")

    #
    #
    s = "SIDM00347"
    plot_df = pd.concat(
        [gdsc_gexp[s], discretise_genes(gdsc_gexp[s])],
        axis=1,
        sort=False,
    ).sort_values(s)

    ax = plt.gca()

    sns.boxplot(
        data=pd.concat(
            [gdsc_gexp.loc[lh_genes[c], s].rename(c) for c in lh_genes],
            axis=1,
            sort=False,
        ),
        palette=lh_genes_pal,
        saturation=1,
        orient="h",
        showcaps=False,
        flierprops=QCplot.FLIERPROPS,
        boxprops=dict(linewidth=0.3),
        whiskerprops=dict(linewidth=0.3),
        notch=True,
        ax=ax,
    )

    sns.distplot(
        gdsc_gexp[s],
        hist=False,
        kde_kws={"cut": 0, "shade": True},
        color=QCplot.PAL_DBGD[0],
        ax=ax.twinx(),
    )

    for k in lh_genes_pal:
        sns.rugplot(
            plot_df.query(f"{s}_{k} == 1")[s], color=lh_genes_pal[k], ax=ax, lw=0.3
        )

    plt.title(s)

    ax.grid(True, ls=":", lw=0.1, alpha=1.0, zorder=0, axis="x")
    ax.set_xlabel("RNA-seq voom")
    plt.gcf().set_size_inches(2.5, 1)
    plt.savefig(
        f"{RPATH}/gdsc_gexp_hist_{s}.pdf", bbox_inches="tight", transparent=True
    )
    plt.close("all")

    #
    #
    g = "MYC"

    plot_df = pd.concat(
        [
            gdsc_gexp.loc[g],
            mobem_gexp["low"].loc[g].rename(f"{g}_low"),
            mobem_gexp["high"].loc[g].rename(f"{g}_high"),
        ],
        axis=1,
        sort=False,
    ).sort_values(g)

    ax = plt.gca()

    sns.distplot(
        plot_df[g],
        hist=False,
        kde_kws={"cut": 0, "shade": True},
        color=QCplot.PAL_DBGD[0],
        ax=ax,
    )

    sns.distplot(
        gdsc_gexp.mean(),
        hist=False,
        kde_kws={"cut": 0, "shade": True, "lw": 0, "alpha": .3},
        color=QCplot.PAL_DBGD[2],
        ax=ax,
    )

    for k in lh_genes_pal:
        sns.rugplot(
            plot_df.query(f"{g}_{k} == 1")[g], color=lh_genes_pal[k], ax=ax, lw=0.3
        )

    plt.title(g)

    ax.grid(True, ls=":", lw=0.1, alpha=1.0, zorder=0, axis="x")
    ax.set_xlabel("RNA-seq voom")
    plt.gcf().set_size_inches(2.5, 1)
    plt.savefig(
        f"{RPATH}/gdsc_gexp_hist_gene_{g}.pdf", bbox_inches="tight", transparent=True
    )
    plt.close("all")

    #
    #
    for k in lh_genes:
        plot_df = mobem_gexp[k].groupby(gdsc_ss["tissue"], axis=1).mean().corr()
        sns.clustermap(
            plot_df,
            cmap="Spectral",
            annot=True,
            center=0,
            fmt=".2f",
            annot_kws=dict(size=4),
            figsize=(6, 6),
            lw=0.05,
            col_colors=gdsc_tissue_pal[plot_df.columns].rename("tissue"),
            row_colors=gdsc_tissue_pal[plot_df.index].rename("tissue"),
        )
        plt.suptitle(k)
        plt.savefig(
            f"{RPATH}/gdsc_gexp_mobem_{k}_tissue_clustermap.pdf", bbox_inches="tight"
        )
        plt.close("all")
