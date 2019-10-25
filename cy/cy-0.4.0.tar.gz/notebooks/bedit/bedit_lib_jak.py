import ast
import pandas as pd
from crispy.Utils import Utils
import matplotlib.pyplot as plt
from crispy.GuideDesign import GuideDesign
from crispy.CRISPRData import CRISPRDataSet

corder = [
    "sgRNA_ID",
    "Gene",
    "sgRNA_type",
    "chr",
    "start",
    "end",
    "strand",
    "seq",
    "sgRNA",
    "off_target_summary",
]

if __name__ == "__main__":
    score_fc = pd.read_csv(
        "/Users/eg14/Downloads/EssentialityMatrices/01a_qnorm_corrected_logFCs.tsv",
        sep="\t",
        index_col=0,
    )

    achiles_ceres = pd.read_csv(
        "/Users/eg14/Downloads/Achilles_gene_effect.csv", index_col=0
    ).T
    achiles_ceres.index = [i.split(" ")[0] for i in achiles_ceres.index]

    achiles_rnai = pd.read_csv(
        "/Users/eg14/Downloads/D2_combined_gene_dep_scores.csv", index_col=0
    )
    achiles_rnai.index = [i.split(" ")[0] for i in achiles_rnai.index]

    #
    ht29_dep = (
        pd.concat(
            [
                score_fc["HT-29v1.1"].rename("sanger - crispr"),
                achiles_ceres["ACH-000552"].rename("broad - crispr"),
                achiles_rnai["HT29_LARGE_INTESTINE"].rename("broad - rnai"),
            ],
            axis=1,
            sort=False,
        )
        .dropna(subset=["sanger - crispr"])
        .sort_values("sanger - crispr")
    )

    #
    ess_hart = Utils.get_essential_genes(return_series=False)

    top_ess_genes = ht29_dep.dropna(subset=["broad - crispr", "broad - rnai"])
    top_ess_genes = top_ess_genes[
        (top_ess_genes["broad - crispr"] < -1) & (top_ess_genes["broad - rnai"] < -1)
    ]
    top_ess_genes = top_ess_genes[
        top_ess_genes["sanger - crispr"]
        < ht29_dep.reindex(ess_hart)["sanger - crispr"].mean()
    ]
    top_ess_genes.to_csv(
        "/Users/eg14/Projects/crispy/crispy/data/bedit/HT-29_essential_genes.csv"
    )

    #
    non_ess_hart = Utils.get_non_essential_genes(return_series=False)

    non_ess_genes = (
        ht29_dep.dropna(subset=["broad - crispr", "broad - rnai"])
        .reindex(non_ess_hart)
        .dropna()
    )
    non_ess_genes = non_ess_genes[(non_ess_genes > 0).sum(1) == 3]
    non_ess_genes = non_ess_genes.loc[
        (
            non_ess_genes["sanger - crispr"]
            - ht29_dep.reindex(non_ess_hart)["sanger - crispr"].median()
        )
        .abs()
        .sort_values()
        .index
    ]

    non_ess_genes.head(50).to_csv(
        "/Users/eg14/Projects/crispy/crispy/data/bedit/HT-29_nonessential_genes.csv"
    )

    # --
    gd = GuideDesign()

    #
    exclude_stop_genes = ["PRPF8", "RPTN"]

    istop_guides = pd.read_excel(
        "/Users/eg14/Projects/crispy/crispy/data/bedit/iSTOP_essential_ht29.xlsx"
    )
    istop_guides = istop_guides[~istop_guides["Gene Name"].isin(exclude_stop_genes)]
    istop_guides["sgRNA"] = [i.upper() for i in istop_guides["PAM: NGG"]]
    istop_guides = (
        istop_guides.groupby(["sgRNA", "Gene Name", "Strand"])
        .first()
        .reset_index()
        .set_index("sgRNA")
    )

    istop_guides_ness = pd.read_excel(
        "/Users/eg14/Projects/crispy/crispy/data/bedit/iSTOP_nonessential_ht29.xlsx"
    )
    istop_guides_ness = istop_guides_ness[
        ~istop_guides_ness["Gene Name"].isin(exclude_stop_genes)
    ]
    istop_guides_ness["sgRNA"] = [i.upper() for i in istop_guides_ness["PAM: NGG"]]
    istop_guides_ness = (
        istop_guides_ness.groupby(["sgRNA", "Gene Name", "Strand"])
        .first()
        .reset_index()
        .set_index("sgRNA")
    )

    #
    stop_guides = []
    for guide in istop_guides.sort_values("Gene Name").index:
        # iSTOP guide info
        istop_info = istop_guides.loc[guide]
        print(f"{istop_info['Gene Name']}: {guide}")

        # Guide ID
        guide_id = gd.search_by_seq(guide, get_db_data="0")
        if guide_id.shape[0] != 1:
            print(f"WARNING: Multiple Guide IDs {guide_id}")
            continue
        guide_id = guide_id.iloc[0, 0]

        # Guide Info
        guide_info = gd.search_by_id(guide_id).iloc[:, 0]
        strand = "+" if guide_info["pam_right"] == 1 else "-"

        guide_res = dict(
            sgRNA_ID=guide_id,
            sgRNA_type="stop_essential",
            chr=guide_info["chr_name"],
            start=guide_info["chr_start"],
            end=guide_info["chr_end"],
            strand=strand,
            seq=guide_info["seq"],
            sgRNA=guide_info["seq"]
            if strand == "+"
            else gd.reverse_complement(guide_info["seq"]),
            off_target_summary=guide_info["off_target_summary"],
            Gene=istop_info["Gene Name"],
            stop_codon=istop_info["Targeted Codon"],
            nmd=istop_info["NMD Prediction (%)"],
        )
        stop_guides.append(guide_res)

    stop_guides = pd.DataFrame(stop_guides)[corder + ["stop_codon", "nmd"]]
    stop_guides.to_clipboard(index=False)

    #
    stop_guides_ness = []
    for guide in istop_guides_ness.sort_values("Gene Name").index:
        # iSTOP guide info
        istop_info = istop_guides_ness.loc[guide]
        print(f"{istop_info['Gene Name']}: {guide}")

        # Guide ID
        guide_id = gd.search_by_seq(guide, get_db_data="0")
        if guide_id.shape[0] != 1:
            print(f"WARNING: Multiple Guide IDs {guide_id}")
            continue
        guide_id = guide_id.iloc[0, 0]

        # Guide Info
        guide_info = gd.search_by_id(guide_id).iloc[:, 0]
        strand = "+" if guide_info["pam_right"] == 1 else "-"

        guide_res = dict(
            sgRNA_ID=guide_id,
            sgRNA_type="stop_nonessential",
            chr=guide_info["chr_name"],
            start=guide_info["chr_start"],
            end=guide_info["chr_end"],
            strand=strand,
            seq=guide_info["seq"],
            sgRNA=guide_info["seq"]
            if strand == "+"
            else gd.reverse_complement(guide_info["seq"]),
            off_target_summary=guide_info["off_target_summary"],
            Gene=istop_info["Gene Name"],
            stop_codon=istop_info["Targeted Codon"],
            nmd=istop_info["NMD Prediction (%)"],
        )
        stop_guides_ness.append(guide_res)

    stop_guides_ness = pd.DataFrame(stop_guides_ness)[corder + ["stop_codon", "nmd"]]
    stop_guides_ness.to_clipboard(index=False)

    # --
    sl_counts = CRISPRDataSet("Sabatini_Lander_AML")
    sl_fc = (
        sl_counts.counts.remove_low_counts(sl_counts.plasmids)
        .norm_rpm()
        .foldchange(sl_counts.plasmids)
    )

    sl_intergenic = {i for i in sl_counts.lib.index if i.startswith("INTERGENIC")}

    ky_counts = CRISPRDataSet("Yusa_v1.1")
    ky_fc = (
        ky_counts.counts.remove_low_counts(ky_counts.plasmids)
        .norm_rpm()
        .foldchange(ky_counts.plasmids)
    )

    crtl_sgrnas = {i for i in ky_counts.counts.index if i.startswith("CTRL0")}

    # -
    ht29_sgnrna_fcs = ky_fc[[i for i in ky_fc.columns if i.startswith("HT29")]]

    # -
    ctrl_guides = (
        ht29_sgnrna_fcs.reindex(crtl_sgrnas)
        .median(1)
        .sort_values(ascending=False)
        .dropna()
    )
    ctrl_guides = sl_counts.lib.loc[ctrl_guides.head(57).index].dropna(subset=["sgRNA"])

    stop_guides_ctrl = []
    for guide_id in ctrl_guides.index:
        guide = ctrl_guides.loc[guide_id, "sgRNA"]
        print(guide)

        guide_res = dict(
            sgRNA_ID=guide_id,
            Gene=None,
            sgRNA_type="non_targeting",
            chr=None,
            start=None,
            end=None,
            strand=None,
            seq=None,
            sgRNA=guide,
            off_target_summary=None,
            stop_codon=None,
            nmd=None,
            exonic=0,
            genic=0,
        )
        stop_guides_ctrl.append(guide_res)

    corder = [
        "sgRNA_ID",
        "Gene",
        "sgRNA_type",
        "chr",
        "start",
        "end",
        "strand",
        "seq",
        "sgRNA",
        "off_target_summary",
    ]
    stop_guides_ctrl = pd.DataFrame(stop_guides_ctrl)[
        corder + ["stop_codon", "nmd", "exonic", "genic"]
    ]
    stop_guides_ctrl.to_clipboard(index=False)

    gd = GuideDesign()
    for g in stop_guides_ctrl["sgRNA"]:
        guide_id = gd.search_by_seq(g)
        if guide_id.shape[0] > 0:
            print(f"WARNING: {guide} has a match")

    # -
    intergenic_guides = (
        sl_fc.reindex(sl_intergenic).median(1).sort_values(ascending=False).dropna()
    )
    intergenic_guides = sl_counts.lib.loc[intergenic_guides.head(200).index].dropna(
        subset=["sgRNA"]
    )

    stop_guides_intergenic = []
    for guide in intergenic_guides["sgRNA"]:
        # Guide ID
        guide_id = gd.search_by_seq(guide, get_db_data="0")
        if guide_id.shape[0] != 1:
            print(f"WARNING: Multiple Guide IDs {guide_id}")
            continue
        guide_id = guide_id.iloc[0, 0]

        # Guide Info
        guide_info = gd.search_by_id(guide_id).iloc[:, 0]
        strand = "+" if guide_info["pam_right"] == 1 else "-"

        guide_res = dict(
            sgRNA_ID=guide_id,
            sgRNA_type="intergenic",
            chr=guide_info["chr_name"],
            start=guide_info["chr_start"],
            end=guide_info["chr_end"],
            strand=strand,
            seq=guide_info["seq"],
            sgRNA=guide_info["seq"]
            if strand == "+"
            else gd.reverse_complement(guide_info["seq"]),
            off_target_summary=guide_info["off_target_summary"],
            Gene=None,
            stop_codon=None,
            nmd=None,
        )
        stop_guides_intergenic.append(guide_res)

    stop_guides_intergenic = pd.DataFrame(stop_guides_intergenic)[
        corder + ["stop_codon", "nmd"]
    ]
    stop_guides_intergenic.to_clipboard(index=False)

    # -
    library = pd.read_excel(
        "/Users/eg14/Projects/crispy/crispy/data/bedit/bedit_jak1_sgrnas_v1.1.xlsx"
    )

    # library = library[~((library["sgRNA_type"] == "intergenic") & (library["chr"].isin(["X", "Y"])))]
    #
    # noness_gene = library[library["sgRNA_type"] == "stop_nonessential"].groupby("Gene")["sgRNA_ID"].count()
    # library = library[~((library["sgRNA_type"] == "stop_nonessential") & (library["Gene"].isin(noness_gene[noness_gene <= 2].index)))]

    # library = library[[(ast.literal_eval(o)[0] == 1) and (ast.literal_eval(o)[1] == 0) for i, o in library[["sgRNA_type", "off_target_summary"]].values]]

    # gd = GuideDesign()
    # library_guideid = []
    # for guide in library["sgRNA"]:
    #     guide_id = gd.search_by_seq(guide[:-3], get_db_data='0')
    #
    #     if guide_id.shape[0] != 1:
    #         print(f"WARNING: {guide}, Multiple Guide IDs {guide_id}")
    #     guide_id = guide_id.iloc[0, 0]
    #
    #     library_guideid.append(guide_id)
    # library["sgRNA_ID"] = library_guideid

    # gd = GuideDesign()
    # library_extrainfo = {}
    # for i in library.index:
    #     guide_id = library.loc[i, "sgRNA_ID"]
    #     guide_info = gd.search_by_id(guide_id).iloc[:, 0]
    #     library_extrainfo[i] = dict(exonic=guide_info["exonic"], genic=guide_info["genic"])
    # library_extrainfo = pd.DataFrame(library_extrainfo).T
    #
    # library = library.drop(["exonic", "genic"], axis=1)
    # library = pd.concat([library, library_extrainfo], axis=1, sort=False)

    library.to_excel(
        "/Users/eg14/Projects/crispy/crispy/data/bedit/bedit_jak1_sgrnas_v1.1.xlsx",
        index=False,
    )
