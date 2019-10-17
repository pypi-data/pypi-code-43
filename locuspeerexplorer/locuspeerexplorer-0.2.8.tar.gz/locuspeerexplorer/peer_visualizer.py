import pandas as pd
import seaborn as sn
import datetime

import os
import matplotlib
import matplotlib.pyplot as plt
from . import peer_explorer

dirname, filename = os.path.split(os.path.abspath(__file__))
matplotlib.use("MacOSX", warn=False, force=True)


def _code2name(df_data, msa):
    name = list(df_data[df_data["MSA"] == msa].MSA_NAME)[0]
    msa = name.split(",")[0]
    state = name.split(",")[1]
    msa = msa.split("-")[0]
    state = name.split("-")[0]
    return msa + " (" + state + ")"


def _fm_string(fm):
    fm = fm.split("-")[0]
    fm = " ".join([x.capitalize() for x in fm.split("_")])
    return fm


def _time_string():
    now = datetime.datetime.now()
    return "_".join([str(x) for x in [now.month, now.day, now.hour, now.minute]])


def add_mean_row(df_data, subset_msa=None, col_dim="MSA"):
    df_data = df_data.set_index(col_dim).T
    df_data["mean"] = df_data.mean(axis=1)
    df_data = (df_data.T).reset_index()
    return df_data


def barplot_me_vs_peers(df_data, peers, col, save_fig=True, show=False):
    plt.clf()
    sn.set(style="ticks", color_codes=True)
    df_data = df_data.set_index("MSA")
    df_data.loc["National mean"] = df_data.mean()
    df_data = df_data.reset_index()
    y = df_data[col].mean()
    q1 = df_data[col].quantile(0.25)
    q3 = df_data[col].quantile(0.75)
    df_data = df_data[df_data["MSA"].isin(peers)]
    df_data.sort_values(col, inplace=True, ascending=False)
    df_data["NAME"] = df_data["MSA_NAME"].apply(lambda x: x.split("-")[0])
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
    df_data["Peer"] = df_data.apply(lambda x: 1 if (x.MSA) in peers else 0, axis=1)
    df_rest = df_data[~df_data["MSA"].isin(peers)]
    sn.boxplot(x="Peer", y=col, data=df_data, palette="viridis")
    if save_fig:
        time = _time_string()
        plt.savefig(os.path.join(dirname, f"../results/box_peers_nat_{col}_{time}.png"))
    if show:
        plt.show()


def hist_peers_vs_nat(msa, peers, col, save_fig=True, show=False):
    plt.clf()
    df_data["Peer"] = df_data.apply(lambda x: 1 if (x.MSA) in peers else 0, axis=1)
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
    df_data["Peer"] = df_data.apply(lambda x: 1 if (x.MSA) in peers else 0, axis=1)
    sns.violinplot(x="Peer", y="col", data=df_data, palette="muted", split=True)
    if save_fig:
        time = _time_string()
        plt.savefig(os.path.join(dirname, f"../results/violin_peers_{col}_{time}.png"))
    if show:
        plt.show()


def quadrant_viz(df_data, msa, peers, col, save_fig=True, show=False):
    plt.clf()
    if not os.path.exists(os.path.join(dirname, "../results/")):
        os.mkdir(os.path.join(dirname, "../results/"))
    name = _code2name(df_data, msa)
    fm = _fm_string(col)
    df_data["Peer"] = df_data.apply(
        lambda x: "Peers" if (x.MSA) in peers else "Others", axis=1
    )
    fig, axes = plt.subplots(figsize=(10, 10), ncols=2, nrows=2)
    df_data["NAME"] = df_data["MSA_NAME"].apply(lambda x: x.split("-")[0])
    subdata = df_data[df_data["MSA"].isin(peers)]
    y = df_data[col].mean()
    q1 = df_data[col].quantile(0.25)
    q3 = df_data[col].quantile(0.75)
    sn.barplot(x="NAME", y=col, data=subdata, palette="viridis", ax=axes[0][0])
    axes[0][0].axhline(y=y, c="red")
    axes[0][0].axhline(y=q1, ls="--", lw=0.5, c="red")
    axes[0][0].axhline(y=q3, ls="--", lw=0.5, c="red")
    axes[0][0].set_ylabel(f"Concentration of {fm}")
    axes[0][0].set_xlabel("MSA")
    for tick in axes[0][0].get_xticklabels():
        tick.set_rotation(30)
    sn.kdeplot(
        list(df_data[df_data["Peer"] == "Peers"][col]),
        # color="blue",
        bw=0.005,
        label="Peer group",
        shade=True,
        ax=axes[0][1],
    )
    sn.kdeplot(
        list(df_data[df_data["Peer"] == "Others"][col]),
        # color="blue",
        bw=0.005,
        label="All other MSAs",
        shade=True,
        ax=axes[0][1],
    )
    axes[0][1].set_ylabel("Distribution")
    axes[0][1].set_xlabel(f"Concentration of {fm}")

    sn.violinplot(
        x="Peer", y=col, data=df_data, palette="viridis", split=True, ax=axes[1][0]
    )
    axes[1][0].set_ylabel(f"Concentration of {fm}")
    axes[1][0].set_xlabel("MSA group")

    sn.boxplot(x="Peer", y=col, data=df_data, palette="viridis", ax=axes[1][1])
    axes[1][1].set_ylabel(f"Concentration of {fm}")
    axes[1][1].set_xlabel("MSA group")

    fig.suptitle(f"{name} and its peers for the {fm} FM", fontsize=16)

    if save_fig:
        time = _time_string()
        plt.savefig(os.path.join(dirname, f"../results/quadrant_msa_{col}.png"))
        print(
            f'File saved in {os.path.join(dirname, f"../results/quadrant_msa_{col}.png")}'
        )
    if show:
        plt.show()


if __name__ == "__main__":
    dirname, filename = os.path.split(os.path.abspath(__file__))
    df_data = pd.read_csv(
        os.path.join(dirname, "../data/processed/metrics_outcomes.csv")
    )
    df_data = df_data[df_data["YEAR"] == 2016]
    peers, fms = peer_explorer.get_top_n_fms_peers(
        df_data, msa=35620, year=2016, n_peers=8
    )
    msa = 35620
    # barplot_me_vs_peers(df_data, [35620] + peers, col=fms[1])
    # boxplot_peers_vs_nat(df_data, [35620] + peers, col=fms[1])
    # hist_peers_vs_nat(df_data, [35620] + peers, col=fms[1])
    quadrant_viz(df_data, msa, [35620] + peers, col=fms[1])
