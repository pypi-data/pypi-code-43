import os
import gzip
import logging
import numpy as np
import pandas as pd
import pkg_resources
from Bio import SeqIO
from Bio import pairwise2
from Bio.SeqUtils import GC
from adjustText import adjust_text
import seaborn as sns
import matplotlib as mpl
import matplotlib.pyplot as plt
from crispy import logger as LOG
from GuideDesign import GuideDesign
from crispy.LibRepresentationReport import LibraryRepresentaion


DPATH = pkg_resources.resource_filename("data", "dualguide/")
RPATH = pkg_resources.resource_filename("notebooks", "dualguide/reports/")

FASTQ_DIR = (
    "MiSeq_walk_up_227-142397264/FASTQ_Generation_2019-10-11_10_04_51Z-194053941/"
)

STYPES = ["sgRNA1", "sgRNA2", "scaffold", "linker", "trna"]

STYPES_POS_R1 = dict(
    sgRNA1=(0, 20),
    scaffold=(20, 96),
    linker=(96, 102),
    trna=(102, 173),
    sgRNA2=(173, 193),
)

STYPES_POS_R2 = dict(sgRNA2=(0, 20), trna=(20, 91))

SELEMS = [("sgRNA1", "R1"), ("scaffold", "R1"), ("linker", "R1"), ("sgRNA2", "R2")]

RELEMS = [
    "sgRNA1_exists",
    "sgRNA2_exists",
    "scaffold_exists",
    "scaffold_WT",
    "scaffold_MT",
    "linker_exists",
    "sgRNA1_exists_inlib",
    "sgRNA2_exists_inlib",
    "swapping",
    "sgRNA_ID1_exists",
    "sgRNA_ID2_exists",
    "sgRNAs_both_inlib",
    "sgRNAs_any_inlib",
    "swapping_WT",
    "swapping_MT",
]


def parse_seq(values, stype, rtype):
    assert stype in STYPES, f"sequence type '{stype}' not supported"
    pos = STYPES_POS_R1[stype] if rtype == "R1" else STYPES_POS_R2[stype]
    seq = (
        values[pos[0] : pos[1]]
        if rtype == "R1"
        else values[pos[0] : pos[1]].reverse_complement()
    )
    return seq


def parse_fastq_file(filename):
    with gzip.open(filename, "rt") as f:
        reads = {r.id: r for r in SeqIO.parse(f, "fastq")}
    return reads


if __name__ == "__main__":
    # Library samplesheet
    #

    lib = pd.read_excel(
        f"{DPATH}/DualGuidePilot_v1.1_annotated.xlsx",
    )

    lib_sets = {c: set(lib[c]) for c in ["sgRNA1", "sgRNA2", "scaffold", "linker"]}
    lib_sgrnas = lib_sets["sgRNA1"].union(lib_sets["sgRNA2"])
    lib_pairs = {(sg1, sg2) for sg1, sg2 in lib[["sgRNA1", "sgRNA2"]].values}
    lib_scaffold = lib.groupby("scaffold")["scaffold_type"].first().to_dict()
    lib_sgrnas_count = (
        pd.Series(
            [sg for sg1, sg2 in lib[["sgRNA1", "sgRNA2"]].values for sg in [sg1, sg2]]
        )
        .value_counts()
        .to_dict()
    )

    lib_ss = pd.read_excel(f"{DPATH}/run227_samplesheet.xlsx")
    lib_ss = lib_ss[~lib_ss["name"].apply(lambda v: v.endswith("-2"))]

    samples = ["DNA12", "DNA22", "DNA32", "Lib1", "Lib2", "Lib3", "Oligo14", "Oligo26"]
    samples_pal = lib_ss.groupby("name")["palette"].first()

    # Analyse each library prep
    #

    reports, counts, swaps = {}, {}, {}

    # n, lib_ss_df = list(lib_ss.groupby("name"))[0]
    for n, lib_ss_df in lib_ss.groupby("name"):
        LOG.info(f"{n}")

        # Read fastq (R1 and R2)
        ss_reads = {}
        for idx in lib_ss_df.index:
            fastq_file = f"{DPATH}/{FASTQ_DIR}/{lib_ss.loc[idx, 'directory']}/{lib_ss.loc[idx, 'file']}"
            ss_reads[lib_ss.loc[idx, "read"]] = parse_fastq_file(fastq_file)
            LOG.info(
                f"{n} ({lib_ss.loc[idx, 'read']}) reads parsed: {len(ss_reads[lib_ss.loc[idx, 'read']])}"
            )

        # Sample index
        ss_index = pd.DataFrame(
            {
                r: pd.Series(
                    [rec.description.split(":")[-1] for rec in ss_reads["R1"].values()]
                ).value_counts()
                for r in ["R1", "R2"]
            }
        )
        LOG.info(ss_index.head())

        # Sequence quality
        for idx in lib_ss_df.index:
            plot_df = np.array(
                [
                    rec.letter_annotations["phred_quality"]
                    for _, rec in ss_reads[lib_ss_df.loc[idx, "read"]].items()
                ]
            )
            plot_df = pd.DataFrame(
                dict(mean=np.median(plot_df, axis=0), std=np.std(plot_df, axis=0))
            )

            plt.figure(figsize=(0.03 * lib_ss_df.loc[idx, "read_len"], 1.0))
            plt.errorbar(
                list(plot_df.index + 1),
                plot_df["mean"],
                yerr=plot_df["std"],
                fmt="o",
                color=lib_ss_df.iloc[0]["palette"],
                ecolor="lightgray",
                elinewidth=0.5,
                capsize=0,
                markersize=2,
            )
            plt.grid(True, ls="-", lw=0.1, alpha=1.0, zorder=0, axis="both")
            plt.title(f"{n} - {lib_ss_df.loc[idx, 'read']}")
            plt.xlabel("Read position")
            plt.ylabel("Quality score\n(Phred median)")
            plt.savefig(
                f"{RPATH}/run227_position_quality_{n}_{lib_ss_df.loc[idx, 'read']}.pdf",
                bbox_inches="tight",
            )
            plt.close("all")

        # Retrieve sequence elements
        reads_id = set(ss_reads["R1"]).intersection(set(ss_reads["R2"]))

        ss_reads_seq = {
            r_id: {s: parse_seq(ss_reads[r][r_id], s, r) for s, r in SELEMS}
            for r_id in reads_id
        }
        LOG.info(f"Number of reads: {len(reads_id)}")

        # Annotate reads
        # Guide IDs
        lib_ids = [["sgRNA1", "sgRNA2"], ["sgRNA1", "scaffold", "linker", "sgRNA2"]]
        for idx, lib_id in enumerate(lib_ids):
            lib_w_id = (
                lib.groupby(lib_id)["sgRNA_ID"].agg(lambda v: ";".join(v)).to_dict()
            )
            LOG.info(f"Annotate sgRNA IDs: {';'.join(lib_id)}")

            for r_id in ss_reads_seq:
                r_elem_id = tuple([ss_reads_seq[r_id][i].seq._data for i in lib_id])
                ss_reads_seq[r_id][f"sgRNA_ID{idx+1}"] = (
                    lib_w_id[r_elem_id] if r_elem_id in lib_w_id else np.nan
                )

        # Contained in library
        for r_id in ss_reads_seq:
            # Constructs exist
            for e in lib_sets:
                ss_reads_seq[r_id][f"{e}_exists"] = int(
                    ss_reads_seq[r_id][e].seq._data in lib_sets[e]
                )

            # sgRNAs at all in library
            for i in ["sgRNA1", "sgRNA2"]:
                ss_reads_seq[r_id][f"{i}_exists_inlib"] = int(
                    ss_reads_seq[r_id][i].seq._data in lib_sgrnas
                )

            # sgRNA ID matching
            for i in ["sgRNA_ID1", "sgRNA_ID2"]:
                ss_reads_seq[r_id][f"{i}_exists"] = int(
                    ss_reads_seq[r_id][i] is not np.nan
                )

            # Bool combination of sgRMAs in lib
            ss_reads_seq[r_id]["sgRNAs_both_inlib"] = (
                ss_reads_seq[r_id]["sgRNA1_exists_inlib"]
                and ss_reads_seq[r_id]["sgRNA2_exists_inlib"]
            )
            ss_reads_seq[r_id]["sgRNAs_any_inlib"] = (
                ss_reads_seq[r_id]["sgRNA1_exists_inlib"]
                or ss_reads_seq[r_id]["sgRNA2_exists_inlib"]
            )

            # Scaffold
            ss_reads_seq[r_id]["scaffold_WT"] = ss_reads_seq[r_id][
                "scaffold_exists"
            ] and (lib_scaffold[ss_reads_seq[r_id]["scaffold"].seq._data] == "wildtype")
            ss_reads_seq[r_id]["scaffold_MT"] = ss_reads_seq[r_id][
                "scaffold_exists"
            ] and (lib_scaffold[ss_reads_seq[r_id]["scaffold"].seq._data] == "modified")

            # Swapping
            r_swap_order = 1 - ss_reads_seq[r_id]["sgRNA_ID1_exists"]
            r_swap_inlib = ss_reads_seq[r_id]["sgRNAs_both_inlib"]

            ss_reads_seq[r_id]["sgRNAs_exists_inlib"] = r_swap_inlib
            ss_reads_seq[r_id]["swapping"] = r_swap_order and r_swap_inlib

            ss_reads_seq[r_id]["swapping_WT"] = (
                ss_reads_seq[r_id]["swapping"] and ss_reads_seq[r_id]["scaffold_WT"]
            )
            ss_reads_seq[r_id]["swapping_MT"] = (
                ss_reads_seq[r_id]["swapping"] and ss_reads_seq[r_id]["scaffold_MT"]
            )

        # Counts
        sgrna_id_types = [f"sgRNA_ID{i+1}" for i in np.arange(len(lib_ids))]
        counts[n] = {
            i: pd.Series([ss_reads_seq[r][i] for r in ss_reads_seq]).value_counts()
            for i in sgrna_id_types
        }

        # Set of swaps
        swaps[n] = [
            ss_reads_seq[r_id]
            for r_id in ss_reads_seq
            if ss_reads_seq[r_id]["swapping"]
        ]

        # Reports
        reports[n] = (
            pd.DataFrame(
                {e: {r: ss_reads_seq[r][e] for r in ss_reads_seq} for e in RELEMS}
            )
            .sum()
            .set_value("total", len(ss_reads_seq))
        )

        LOG.info(reports[n])

    # Parse runs
    #
    reports = pd.DataFrame(reports).T
    reports.to_excel(f"{RPATH}/run227_samples_report.xlsx")

    counts = {
        i: pd.DataFrame({s: counts[s][i] for s in samples})
        for i in ["sgRNA_ID1", "sgRNA_ID2"]
    }
    for i in counts:
        counts[i].to_excel(f"{RPATH}/run227_samples_counts_{i}.xlsx")

    # Total reads
    #
    _, ax = plt.subplots(1, 1, figsize=(1, 1.5))
    ax.bar(
        np.arange(len(samples)),
        reports.loc[samples, "total"],
        color=samples_pal.loc[samples],
        lw=0,
    )
    ax.set_xticks(np.arange(len(samples)))
    ax.set_xticklabels(samples, rotation=90)
    ax.set_title("FASTQ reads")
    ax.set_ylabel("Number of reads")
    ax.grid(True, ls="-", lw=0.1, alpha=1.0, zorder=0, axis="y")
    plt.savefig(f"{RPATH}/run227_total_counts.pdf", bbox_inches="tight")
    plt.close("all")

    # Reports barplots
    #
    plot_df = (reports.T / reports["total"]) * 100
    plot_df = pd.melt(plot_df.drop("total", axis=0).reset_index(), id_vars="index")

    col_order = [
        "scaffold_exists",
        "scaffold_WT",
        "scaffold_MT",
        "linker_exists",
        "sgRNA1_exists_inlib",
        "sgRNA2_exists_inlib",
        "sgRNA_ID1_exists",
        "sgRNA_ID2_exists",
        "swapping",
        "swapping_WT",
        "swapping_MT",
        "sgRNAs_both_inlib",
    ]

    f, axs = plt.subplots(
        1,
        len(col_order),
        sharex="all",
        sharey="all",
        figsize=(len(col_order) * 1.2, 3.0),
        dpi=600,
    )

    for i, c in enumerate(col_order):
        ax = axs[i]

        df = plot_df.query(f"index == '{c}'")
        df = df.set_index("variable").loc[samples]

        ax.bar(np.arange(len(samples)), df["value"], color=samples_pal[df.index], lw=0)

        ax.set_ylim(0, 110)
        ax.set_yticks(np.arange(0, 110, 10))
        ax.set_xticks(np.arange(len(samples)))
        ax.set_xticklabels(samples, rotation=90)

        ax.grid(True, ls="-", lw=0.1, alpha=1.0, zorder=0, axis="y")

        for idx, o in enumerate(samples):
            ax.text(
                idx,
                df.loc[o, "value"],
                f"{df.loc[o, 'value']:.1f}%",
                fontsize=6,
                c="k",
                rotation=90,
                ha="center",
                va="bottom",
            )

        ax.set_title(c)
        ax.set_ylabel("% of total FASTQ reads" if i == 0 else "")
        ax.set_xlabel("")

    plt.subplots_adjust(hspace=0, wspace=0.05)
    plt.savefig(f"{RPATH}/run227_match_report.pdf", bbox_inches="tight")
    plt.close("all")

    # Swap pairs
    #
    plot_df = (
        pd.Series(
            [
                f"{r['sgRNA1'].seq._data}_{r['sgRNA2'].seq._data}"
                for n in swaps
                for r in swaps[n]
            ]
        )
        .value_counts()
        .reset_index()
    )
    plot_df = plot_df.rename(columns={0: "count"})
    plot_df["match"] = [
        sum([b1 == b2 for b1, b2 in zip(*sg.split("_"))]) for sg in plot_df["index"]
    ]
    plot_df["alignment"] = [
        pairwise2.align.globalxx(*sg.split("_"))[0][2] for sg in plot_df["index"]
    ]
    plot_df["lib_count"] = [
        sum([lib_sgrnas_count[g] for g in dg.split("_")]) for dg in plot_df["index"]
    ]

    _, ax = plt.subplots(1, 1, figsize=(2, 1.5))
    ax.scatter(
        plot_df.query("count > 10").index,
        plot_df.query("count > 10")["count"],
        c="k",
        s=5,
        linewidths=0,
    )
    texts = [
        ax.text(i, r["count"], r["index"], color="k", fontsize=2)
        for i, r in plot_df.head(10).iterrows()
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

    ax.set_title("Swap pairs frequency")
    ax.set_ylabel("Frequency")
    ax.grid(True, ls="-", lw=0.1, alpha=1.0, zorder=0, axis="y")
    plt.savefig(f"{RPATH}/run227_swaps_pairs_counts.pdf", bbox_inches="tight")
    plt.close("all")

    # Swap pairs by sequence homology
    #
    _, ax = plt.subplots(1, 1, figsize=(3.5, 1.5))
    sns.boxplot(
        plot_df["alignment"].astype(int),
        np.log2(plot_df["count"]),
        palette="Reds",
        saturation=1,
        showcaps=False,
        boxprops=dict(linewidth=0.3),
        whiskerprops=dict(linewidth=0.3),
        flierprops=dict(
            marker="o",
            markerfacecolor="black",
            markersize=1.0,
            linestyle="none",
            markeredgecolor="none",
            alpha=0.6,
        ),
        notch=True,
        ax=ax,
    )
    ax.set_xlabel("Alignment")
    ax.set_ylabel("Frequency (log2)")
    ax.grid(True, ls="-", lw=0.1, alpha=1.0, zorder=0, axis="both")
    plt.savefig(f"{RPATH}/run227_swaps_pairs_match.pdf", bbox_inches="tight")
    plt.close("all")

    #
    #
    m_sgrnas = (
        pd.pivot_table(
            pd.DataFrame([dict(sg1=sg1, sg2=sg2) for sg1, sg2 in lib_pairs]).assign(
                values=1
            ),
            index="sg1",
            columns="sg2",
            values="values",
            fill_value=0,
        )
        .loc[lib_sgrnas, lib_sgrnas]
        .replace(np.nan, 0)
        .astype(int)
    )

    _, ax = plt.subplots(1, 1, figsize=(4, 4), dpi=600)
    sns.heatmap(m_sgrnas, yticklabels=False, xticklabels=False, cmap="viridis", ax=ax)
    plt.savefig(f"{RPATH}/run227_sgrnas_mapping_heatmap.png", bbox_inches="tight")
    plt.close("all")

    m_sgrnas_swaps = (
        pd.pivot_table(
            pd.DataFrame([dict(sg1=sg.split("_")[0], sg2=sg.split("_")[1]) for sg in plot_df["index"]]).assign(
                values=1
            ),
            index="sg1",
            columns="sg2",
            values="values",
            fill_value=0,
        )
        .loc[lib_sgrnas, lib_sgrnas]
        .replace(np.nan, 0)
        .astype(int)
    )

    _, ax = plt.subplots(1, 1, figsize=(4, 4), dpi=600)
    sns.heatmap(m_sgrnas_swaps, yticklabels=False, xticklabels=False, cmap="viridis", ax=ax)
    plt.savefig(f"{RPATH}/run227_sgrnas_mapping_heatmap_swap.png", bbox_inches="tight")
    plt.close("all")


    m_sgrnas_counts = (
        pd.pivot_table(
            pd.DataFrame([dict(sg1=sg1, sg2=sg2, values=np.log10(lib_sgrnas_count[sg1] + lib_sgrnas_count[sg2])) for sg1, sg2 in lib_pairs]),
            index="sg1",
            columns="sg2",
            values="values",
            fill_value=0,
        )
        .loc[lib_sgrnas, lib_sgrnas]
        .replace(np.nan, 0)
        .astype(int)
    )

    _, ax = plt.subplots(1, 1, figsize=(4, 4), dpi=600)
    sns.heatmap(m_sgrnas_counts, yticklabels=False, xticklabels=False, cmap="viridis", ax=ax)
    plt.savefig(f"{RPATH}/run227_sgrnas_count_mapping_heatmap.png", bbox_inches="tight")
    plt.close("all")


    m_sgrnas_swaps_counts = (
        pd.pivot_table(
            pd.DataFrame([dict(sg1=sg.split("_")[0], sg2=sg.split("_")[1], values=np.log10(c)) for sg, c in plot_df[["index", "count"]].values]),
            index="sg1",
            columns="sg2",
            values="values",
            fill_value=0,
        )
        .loc[lib_sgrnas, lib_sgrnas]
        .replace(np.nan, 0)
        .astype(int)
    )

    _, ax = plt.subplots(1, 1, figsize=(4, 4), dpi=600)
    sns.heatmap(m_sgrnas_swaps_counts, yticklabels=False, xticklabels=False, cmap="viridis", ax=ax)
    plt.savefig(f"{RPATH}/run227_sgrnas_count_mapping_heatmap_swap.png", bbox_inches="tight")
    plt.close("all")

    # Counts
    #
    counts_df = pd.DataFrame(
        {
            idx: row if ";" not in i else row.divide(len(i.split(";"))).astype(int)
            for i, row in counts["sgRNA_ID2"].iterrows()
            for idx in i.split(";")
        }
    ).T.loc[lib["sgRNA_ID"]]
    counts_df = counts_df.replace(np.nan, 0).astype(int)
    counts_df.to_csv(f"{RPATH}/run227_rawcounts.csv.gz", compression="gzip")

    # Library representation reports
    #
    lib_report = LibraryRepresentaion(counts_df)

    # Comparison gini scores
    #
    gini_scores_comparison = dict(
        avana=0.361, brunello=0.291, yusa_v1=0.342, yusa_v11=0.229
    )

    gini_scores_comparison_palette = dict(
        avana="#66c2a5", brunello="#fc8d62", yusa_v1="#8da0cb", yusa_v11="#e78ac3"
    )

    gini_scores = (
        lib_report.gini().reset_index().rename(columns={"index": "sample", 0: "gini"})
    )

    # Gini scores barplot
    #
    plt.figure(figsize=(2.5, 1.0), dpi=600)

    sns.barplot(
        "gini",
        "sample",
        data=gini_scores,
        orient="h",
        order=samples,
        palette=samples_pal,
        saturation=1,
        lw=0,
    )

    plt.grid(True, ls="-", lw=0.1, alpha=1.0, zorder=0, axis="x")

    for k, v in gini_scores_comparison.items():
        plt.axvline(
            v, lw=0.5, zorder=1, color=gini_scores_comparison_palette[k], label=k
        )

    plt.xlabel("Gini score")
    plt.ylabel("")

    plt.legend(
        frameon=False, loc="center left", bbox_to_anchor=(1, 0.5), prop={"size": 4}
    )

    plt.savefig(f"{RPATH}/run227_gini_barplot.pdf", bbox_inches="tight")
    plt.close("all")

    # Lorenz curves
    #
    lib_report.lorenz_curve(palette=samples_pal)
    plt.gcf().set_size_inches(2, 2)
    plt.savefig(f"{RPATH}/run227_lorenz_curve.pdf", bbox_inches="tight", dpi=600)
    plt.close("all")

    # sgRNA counts boxplots
    #
    lib_report.boxplot(palette=samples_pal)
    plt.gcf().set_size_inches(1.5, 1.5)
    plt.savefig(f"{RPATH}/run227_counts_boxplots.pdf", bbox_inches="tight", dpi=600)
    plt.close("all")

    # sgRNA counts histograms
    #
    lib_report.distplot(palette=samples_pal)
    plt.gcf().set_size_inches(2.5, 2)
    plt.savefig(f"{RPATH}/run227_counts_histograms.pdf", bbox_inches="tight")
    plt.close("all")

    # Percentile scores barplot (good library will have a value below 6)
    #
    percentile_scores = (
        lib_report.percentile()
        .reset_index()
        .rename(columns={"index": "sample", 0: "range"})
    )

    plt.figure(figsize=(2.5, 1.0), dpi=600)

    sns.barplot(
        "range",
        "sample",
        data=percentile_scores,
        orient="h",
        order=samples,
        palette=samples_pal,
        saturation=1,
        lw=0,
    )

    plt.grid(True, ls="-", lw=0.1, alpha=1.0, zorder=0, axis="x")

    plt.axvline(6, lw=0.5, zorder=1, color="k")

    plt.xlabel("Fold-change range containing 95% of the guides")
    plt.ylabel("")

    plt.savefig(f"{RPATH}/run227_fc_range_barplot.pdf", bbox_inches="tight")
    plt.close("all")

    # Drop-out rates barplot
    #
    dropout_rates = lib_report.dropout_rate() * 100
    dropout_rates = dropout_rates.reset_index().rename(
        columns={"index": "sample", 0: "dropout"}
    )

    plt.figure(figsize=(2.5, 1.0), dpi=600)

    ax = sns.barplot(
        "dropout",
        "sample",
        data=dropout_rates,
        orient="h",
        order=samples,
        palette=samples_pal,
        saturation=1,
        lw=0,
    )

    plt.grid(True, ls="-", lw=0.1, alpha=1.0, zorder=0, axis="x")

    vals = ax.get_xticks()
    ax.set_xticklabels([f"{x:.1f}%" for x in vals])

    plt.xlabel("Dropout sgRNAs (zero counts)")
    plt.ylabel("")

    plt.savefig(f"{RPATH}/run227_dropout_barplot.pdf", bbox_inches="tight")
    plt.close("all")
