import pandas as pd
import pkg_resources
from crispy.Utils import Utils
from crispy.CRISPRData import Library
from crispy.CRISPRData import CRISPRDataSet
from minlib.Utils import project_score_sample_map

DPATH = pkg_resources.resource_filename("data", "dualguide/")

if __name__ == "__main__":
    #
    master_lib = Library.load_library("MasterLib_v1.csv.gz", set_index=False)

    #
    ky = CRISPRDataSet("Yusa_v1.1")
    ky_smap = project_score_sample_map()
    ky_fc = (
        ky.counts.remove_low_counts(ky.plasmids)
        .norm_rpm()
        .norm_rpm()
        .foldchange(ky.plasmids)
    )
    ky_fc_avg = ky_fc.groupby(ky_smap["model_id"], axis=1).mean()
    ky_fc_avg_gene = ky_fc_avg.groupby(ky.lib["Gene"]).mean()

    ht29 = pd.concat(
        [
            ky_fc_avg_gene["SIDM00136"],
            ky_fc_avg.loc[[i.startswith("CTRL0") for i in ky_fc.index]]["SIDM00136"],
        ]
    ).sort_values()

    #
    dg_lib_sgrnas = pd.read_excel(
        f"{DPATH}/DualGuidePilot_Map.xlsx", index_col=0, sheetname="sgrnas"
    )
    dg_lib_scaffold = pd.read_excel(
        f"{DPATH}/DualGuidePilot_Map.xlsx", index_col=0, sheetname="scaffold"
    )
    dg_lib_linkers = pd.read_excel(
        f"{DPATH}/DualGuidePilot_Map.xlsx", index_col=0, sheetname="linkers"
    )

    #
    dg_lib = pd.read_excel(f"{DPATH}/DualGuidePilot.xlsx", index_col=0)

    # Remove duplicates
    # dg_lib = (
    #     dg_lib.groupby(["sequence", "sgRNA1", "scaffold", "linker", "trna", "sgRNA2"])[
    #         "sgRNA_ID"
    #     ]
    #     .agg(lambda v: ";".join(v))
    #     .reset_index()
    #     .set_index("sgRNA_ID")
    # )
    dups = dg_lib.reset_index().groupby("sequence")["sgRNA_ID"].agg(len)
    dg_lib["duplicates"] = dups[dg_lib["sequence"]].values

    dg_lib = pd.concat(
        [
            dg_lib,
            dg_lib_sgrnas.loc[dg_lib["sgRNA1"]].add_suffix("1").set_index(dg_lib.index),
            dg_lib_sgrnas.loc[dg_lib["sgRNA2"]].add_suffix("2").set_index(dg_lib.index),
            dg_lib_scaffold.loc[dg_lib["scaffold"]].set_index(dg_lib.index)["type"].rename("scaffold_type"),
            dg_lib_linkers.loc[dg_lib["linker"]].set_index(dg_lib.index)["type"].rename("linker_type"),
            dg_lib["sgRNA1"].apply(lambda v: v[0]).rename("sgRNA1_first"),
            dg_lib["sgRNA2"].apply(lambda v: v[0]).rename("sgRNA2_first"),
        ],
        axis=1,
        sort=False,
    )
    dg_lib["gene1_HT29"] = ht29[dg_lib["gene1"]].values
    dg_lib["gene2_HT29"] = ht29[dg_lib["gene2"]].values

    # Export library
    dg_lib.to_excel(f"{DPATH}/DualGuidePilot_v1.1_annotated.xlsx")
