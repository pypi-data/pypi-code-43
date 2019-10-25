import os
import gzip
import logging
import numpy as np
import pandas as pd
import pkg_resources
import seaborn as sns
import matplotlib.pyplot as plt
from crispy import logger as LOG
from GuideDesign import GuideDesign
from crispy.LibRepresentationReport import LibraryRepresentaion


RPATH = pkg_resources.resource_filename("notebooks", "bedit/")
FASTQ_DIR = "reports/fastq/MiSeq_walk_up_208_repeat-139969833/FASTQ_Generation_2019-08-14_13_08_57Z-191552501/"

SEQUENCE_LEN = 25
SCAFFOLD_LEN = 6


def parse_read(lines, reverse_read=False):
    read_dict = dict()

    # Read sample index
    read_dict["index"] = lines[0].split(":")[-1:][0]

    # Sequence
    read_dict["sequence"] = lines[1]

    # Exclude unrecognised bp
    if len(set(lines[1]) - {"A", "T", "C", "G"}) > 0:
        return None

    assert (
        len(lines[1]) == SEQUENCE_LEN
    ), f"Expected fastq file sequence length to be 25bp: {len(lines[1])} found instead {lines[1]}"

    # Parse sequence
    seq = (
        GuideDesign.reverse_complement(read_dict["sequence"])
        if reverse_read
        else read_dict["sequence"]
    )

    read_dict["sgRNA"] = seq[SCAFFOLD_LEN:] if reverse_read else seq[:-SCAFFOLD_LEN]
    read_dict["scaffold"] = seq[:SCAFFOLD_LEN] if reverse_read else seq[-SCAFFOLD_LEN:]

    return read_dict


def parse_fastq_file(filename, reverse_read=False):
    counts = []

    with gzip.open(filename, "rt") as f:
        # Read FASTQ
        experiment_fastq = f.read().splitlines()

        # Parse every four lines
        line_start = 4

        while line_start < len(experiment_fastq):
            # Parse read
            reads = experiment_fastq[line_start - 4 : line_start]

            try:
                read_dict = parse_read(reads, reverse_read)

            except KeyError as e:
                LOG.error(e)
                LOG.error(f"At line {line_start}: {reads}")
                raise e

            # Store parsed read
            if read_dict is not None:
                counts.append(read_dict)

            line_start += 4

    counts = pd.DataFrame(counts)

    return counts


def fastq_to_counts(counts, library, scaffold, index):
    # Annotate fastq sequences with sgRNA IDs
    counts_lib = counts.assign(
        sgRNA_ID=library["sgRNA_ID"].reindex(counts["sgRNA"]).values
    )

    # Annotate which scaffold and indecies match perfectly
    counts_lib = counts_lib.assign(
        scaffold_match=(counts_lib["scaffold"] == scaffold).values
    )
    counts_lib = counts_lib.assign(index_match=(counts_lib["index"] == index).values)

    # Report of perfect matches
    n_reads = counts_lib.shape[0]

    match_report = dict(
        scaffold=counts_lib["scaffold_match"].sum() / n_reads,
        index=counts_lib["index_match"].sum() / n_reads,
        sgRNA=counts_lib["sgRNA_ID"].count() / n_reads,
    )

    # Count number of read per guide
    counts_lib = counts_lib["sgRNA_ID"].dropna().value_counts()
    counts_lib = counts_lib.reindex(library["sgRNA_ID"], fill_value=0)
    counts_lib = counts_lib.sort_values(ascending=False)

    return counts_lib, match_report


if __name__ == "__main__":
    # JAK1 base-editing library
    #
    lib = pd.read_excel(f"{RPATH}/reports/bedit_jak1_sgrnas_v1.1.xlsx", index_col="fastq")

    # Library samplesheet
    #
    lib_ss = pd.read_excel(f"{RPATH}/reports/bedit_jak1_sgrnas_v1.1_samplesheet.xlsx")

    # Analyse each library prep
    #
    lib_counts, lib_reports = {}, {}

    for idx in lib_ss.index:
        s_name = lib_ss.loc[idx, "name"]
        LOG.info(f"{s_name} (index={idx})")

        # Import fastq file
        fastq_file = f"{RPATH}/{FASTQ_DIR}/{lib_ss.loc[idx, 'directory']}/{lib_ss.loc[idx, 'file']}"

        # Is reverse read?
        fastq_reverse = lib_ss.loc[idx, "reverse_read"]

        # Parse reads from fastq file
        fastq_counts = parse_fastq_file(fastq_file, fastq_reverse)

        # Calculate sgRNA counts and match report
        sgrna_counts, fastq_qc = fastq_to_counts(
            fastq_counts, lib, lib_ss.loc[idx, "scaffold"], lib_ss.loc[idx, "index"]
        )

        lib_counts[s_name] = sgrna_counts
        lib_reports[s_name] = fastq_qc
        LOG.info(
            f"Match(%): "
            + "; ".join({f"{k}={v*100:.2f}%" for k, v in fastq_qc.items()})
        )

    lib_counts = pd.DataFrame(lib_counts)
    lib_counts.to_excel(f"{RPATH}/reports/bedit_jak1_sgrnas_v1.1_counts.xlsx")
    # lib_counts = pd.read_excel(f"{RPATH}/reports/bedit_jak1_sgrnas_v1.1_counts.xlsx", index_col=0)

    lib_reports = pd.DataFrame(lib_reports)
    lib_reports.to_excel(f"{RPATH}/reports/bedit_jak1_sgrnas_v1.1_reports.xlsx")
    # lib_reports = pd.read_excel(f"{RPATH}/reports/bedit_jak1_sgrnas_v1.1_reports.xlsx", index_col=0)

    # Library representation reports
    #
    lib_report = LibraryRepresentaion(lib_counts)

    order = [
        "Sample1_R1",
        "Sample1_R2",
        "Sample2_R1",
        "Sample2_R2",
        "Sample3_R1",
        "Sample3_R2",
        "Sample4_R1",
        "Sample4_R2",
    ]

    pal = lib_ss.set_index("name")["palette"].to_dict()

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
        order=order,
        palette=pal,
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

    plt.savefig(f"{RPATH}/reports/librep_gini_barplot.pdf", bbox_inches="tight")
    plt.close("all")

    # Lorenz curves
    #
    lib_report.lorenz_curve()
    plt.gcf().set_size_inches(2, 2)
    plt.savefig(f"{RPATH}/reports/librep_lorenz_curve.pdf", bbox_inches="tight", dpi=600)
    plt.close("all")

    # sgRNA counts boxplots
    #
    lib_report.boxplot()
    plt.gcf().set_size_inches(1.5, 1.5)
    plt.savefig(f"{RPATH}/reports/librep_counts_boxplots.pdf", bbox_inches="tight", dpi=600)
    plt.close("all")

    # sgRNA counts histograms
    #
    lib_report.distplot()
    plt.gcf().set_size_inches(2.5, 2)
    plt.savefig(f"{RPATH}/reports/librep_counts_histograms.pdf", bbox_inches="tight")
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
        order=order,
        palette=pal,
        saturation=1,
        lw=0,
    )

    plt.grid(True, ls="-", lw=0.1, alpha=1.0, zorder=0, axis="x")

    plt.axvline(6, lw=0.5, zorder=1, color="k")

    plt.xlabel("Fold-change range containing 95% of the guides")
    plt.ylabel("")

    plt.savefig(f"{RPATH}/reports/librep_fc_range_barplot.pdf", bbox_inches="tight")
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
        order=order,
        palette=pal,
        saturation=1,
        lw=0,
    )

    plt.grid(True, ls="-", lw=0.1, alpha=1.0, zorder=0, axis="x")

    vals = ax.get_xticks()
    ax.set_xticklabels([f"{x:.1f}%" for x in vals])

    plt.xlabel("Dropout sgRNAs (zero counts)")
    plt.ylabel("")

    plt.savefig(f"{RPATH}/reports/librep_dropout_barplot.pdf", bbox_inches="tight")
    plt.close("all")

    # Matching reports barplots
    #
    plot_df = pd.melt(lib_reports.reset_index(), id_vars="index", value_vars=list(pal))

    f, axs = plt.subplots(
        1,
        lib_reports.shape[0],
        sharex="all",
        sharey="all",
        figsize=(lib_reports.shape[0] * 2.0, 2.),
        dpi=600,
    )

    for i, (dtype, df) in enumerate(plot_df.groupby("index")):
        ax = axs[i]

        df_ = df.set_index("variable").loc[reversed(order)].drop(columns=["index"]) * 100

        ax.barh(
            np.arange(len(order)),
            df_["value"],
            color=[pal[c] for c in reversed(order)],
            lw=0,
        )

        ax.set_yticks(np.arange(len(order)))
        ax.set_yticklabels(reversed(order))

        ax.grid(True, ls="-", lw=0.1, alpha=1.0, zorder=0, axis="x")

        ax.set_title(dtype)
        ax.set_xlabel("FASTQ reads matching (%)")
        ax.set_ylabel("")

    plt.subplots_adjust(hspace=0, wspace=0.05)
    plt.savefig(f"{RPATH}/reports/librep_match_report.pdf", bbox_inches="tight")
    plt.close("all")
