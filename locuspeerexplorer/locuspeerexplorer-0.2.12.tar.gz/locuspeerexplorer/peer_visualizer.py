import pandas as pd
import seaborn as sn
import datetime

import os
import matplotlib
import matplotlib.pyplot as plt
from . import peer_explorer, peer_finder

dirname, filename = os.path.split(os.path.abspath(__file__))
matplotlib.use("MacOSX", warn=False, force=True)


def _code2name(df_data, area):
    name = list(df_data[df_data["AREA"] == area].AREA_NAME)[0]
    if "," in name:
        area = name.split(",")[0]
        state = name.split(",")[1]
        area = area.split("-")[0]
        state = name.split("-")[0]
        name = area + " (" + state + ")"
    return name


def _fm_string(fm):
    fm = fm.split("-")[0]
    fm = " ".join([x.capitalize() for x in fm.split("_")])
    return fm


def _time_string():
    now = datetime.datetime.now()
    return "_".join([str(x) for x in [now.month, now.day, now.hour, now.minute]])


def add_mean_row(df_data, subset_area=None, col_dim="AREA"):
    df_data = df_data.set_index(col_dim).T
    df_data["mean"] = df_data.mean(axis=1)
    df_data = (df_data.T).reset_index()
    return df_data


def barplot_me_vs_peers(df_data, peers, col, save_fig=True, show=False):
    plt.clf()
    sn.set(style="ticks", color_codes=True)
    df_data = df_data.set_index("AREA")
    df_data.loc["National mean"] = df_data.mean()
    df_data = df_data.reset_index()
    y = df_data[col].mean()
    q1 = df_data[col].quantile(0.25)
    q3 = df_data[col].quantile(0.75)
    df_data = df_data[df_data["AREA"].isin(peers)]
    df_data.sort_values(col, inplace=True, ascending=False)
    df_data["NAME"] = df_data["AREA_NAME"].apply(lambda x: x.split("-")[0])
    fig = sn.barplot(x="NAME", y=col, data=df_data, palette="viridis")
    fig.axhline(y=y, c="red")
    fig.axhline(y=q1, ls="--", lw=0.5, c="red")
    fig.axhline(y=q3, ls="--", lw=0.5, c="red")
    plt.xticks(rotation=20)
    if save_fig:
        time = _time_string()
        plt.savefig(os.path.join(dirname, f"../results/bar_peers_{col}_{time}.png"))
    if show:
        plt.show()


def boxplot_peers_vs_nat(df_data, peers, col, save_fig=True, show=False):
    plt.clf()
    df_data["Peer"] = df_data.apply(lambda x: 1 if (x.AREA) in peers else 0, axis=1)
    df_rest = df_data[~df_data["AREA"].isin(peers)]
    sn.boxplot(x="Peer", y=col, data=df_data, palette="viridis")
    if save_fig:
        time = _time_string()
        plt.savefig(os.path.join(dirname, f"../results/box_peers_nat_{col}_{time}.png"))
    if show:
        plt.show()


def hist_peers_vs_nat(area, peers, col, save_fig=True, show=False):
    plt.clf()
    df_data["Peer"] = df_data.apply(lambda x: 1 if (x.AREA) in peers else 0, axis=1)
    sn.kdeplot(
        list(df_data[df_data["Peer"] == 1][col]),
        # color="blue",
        bw=0.01,
        label="Peer group",
        shade=True,
    )
    sn.kdeplot(
        list(df_data[df_data["Peer"] == 0][col]),
        # color="red",
        bw=0.01,
        label="Not peer",
        shade=True,
    )
    if save_fig:
        time = _time_string()
        plt.savefig(
            os.path.join(dirname, f"../results/hist_peers_nat_{col}_{time}.png")
        )
    if show:
        plt.show()


def violin_peers_vs_nat(df_data, peers, col, save_fig=True, show=False):
    plt.clf()
    df_data["Peer"] = df_data.apply(lambda x: 1 if (x.AREA) in peers else 0, axis=1)
    sns.violinplot(x="Peer", y="col", data=df_data, palette="muted", split=True)
    if save_fig:
        time = _time_string()
        plt.savefig(os.path.join(dirname, f"../results/violin_peers_{col}_{time}.png"))
    if show:
        plt.show()


def quadrant_viz(df_data, area, peers, col, save_fig=True, show=False):
    plt.clf()

    df_data = df_data.dropna(subset=[col], how="any")
    if not os.path.exists(os.path.join(dirname, "../results/")):
        os.mkdir(os.path.join(dirname, "../results/"))
    name = _code2name(df_data, area)
    fm = _fm_string(col)
    df_data["Peer"] = df_data.apply(
        lambda x: "Peers" if (x.AREA) in peers else "Others", axis=1
    )
    fig, axes = plt.subplots(figsize=(10, 10), ncols=2, nrows=2)
    df_data["NAME"] = df_data["AREA_NAME"].apply(lambda x: x.split(",")[0][:12])
    subdata = df_data[df_data["AREA"].isin(peers)]
    y = df_data[col].median()
    q1 = df_data[col].quantile(0.25)
    q3 = df_data[col].quantile(0.75)
    sn.barplot(x=col, y="NAME", data=subdata, palette="viridis", ax=axes[0][0])
    axes[0][0].axvline(x=y, c="#ef8d22ff", label="National Median")
    axes[0][0].axvline(x=q1, ls="--", lw=0.5, c="#ef8d22ff", label="1st quantile")
    axes[0][0].axvline(x=q3, ls="--", lw=0.5, c="#ef8d22ff", label="3rd quantile")
    axes[0][0].set_xlabel(f"Concentration of {fm}")
    axes[0][0].set_ylabel(f"")

    axes[0][0].text(q1, 0, "1st quantile", rotation=90, color="#ef8d22ff", va="top")
    axes[0][0].text(q3, 0, "3rd quantile", rotation=90, color="#ef8d22ff", va="top")
    axes[0][0].text(y, 0, "National median", rotation=90, color="#ef8d22ff", va="top")

    # for tick in axes[0][0].get_xticklabels():
    #     tick.set_rotation(30)
    sn.kdeplot(
        list(df_data[df_data["Peer"] == "Peers"][col]),
        # color="blue",
        bw=0.009,
        label="Peer group",
        shade=True,
        ax=axes[0][1],
        color="#20A387FF",
    )
    sn.kdeplot(
        list(df_data[df_data["Peer"] == "Others"][col]),
        # color="blue",
        bw=0.009,
        label="All other AREAs",
        shade=True,
        ax=axes[0][1],
        color="#33638DFF",
    )
    axes[0][1].set_ylabel("Distribution")
    axes[0][1].set_xlabel(f"Concentration of {fm}")

    sn.violinplot(
        x="Peer", y=col, data=df_data, palette="viridis", split=True, ax=axes[1][0]
    )
    axes[1][0].set_ylabel(f"Concentration of {fm}")
    axes[1][0].set_xlabel("Group")

    sn.boxplot(x="Peer", y=col, data=df_data, palette="viridis", ax=axes[1][1])
    axes[1][1].set_ylabel(f"Concentration of {fm}")
    axes[1][1].set_xlabel("Group")

    fig.suptitle(f"{name} and its peers for the {fm} FM", fontsize=16)

    if save_fig:
        time = _time_string()
        plt.savefig(os.path.join(dirname, f"../results/quadrant_area_{col}.png"))
        print(
            f'File saved in {os.path.join(dirname, f"../results/quadrant_area_{col}.png")}'
        )
    if show:
        plt.show()


if __name__ == "__main__":
    dirname, filename = os.path.split(os.path.abspath(__file__))
    df_data = pd.read_csv(
        os.path.join(dirname, "../data/processed/metrics_outcomes.csv")
    )
    df_data = df_data[df_data["YEAR"] == 2016]
    peers, fms = peer_finder.get_top_n_fms_peers(
        df_data, area=35620, year=2016, n_peers=8, n_fms=50
    )
    area = 35620
    print(fms)
    # barplot_me_vs_peers(df_data, [35620] + peers, col=fms[1])
    # boxplot_peers_vs_nat(df_data, [35620] + peers, col=fms[1])
    # hist_peers_vs_nat(df_data, [35620] + peers, col=fms[1])
    quadrant_viz(df_data, area, [35620] + peers, col=fms[30])
