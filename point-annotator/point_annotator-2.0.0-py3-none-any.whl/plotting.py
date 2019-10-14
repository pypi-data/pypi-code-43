"""
This script implements functions for plotting the results of annotation
"""
from collections import Counter

import numpy as np
import pandas as pd
import seaborn as sn
from matplotlib import pyplot as plt
from openTSNE import TSNE
from sklearn.cluster import DBSCAN
from sklearn.decomposition import PCA


def confusion_matrix(annotations, original_labels, num_annot_label=3):
    """
    This function computes a confusion matrix that compares real labels (provided
    together with the dataset) to annotations.

    Parameters
    ----------
    annotations : pd.DataFrame
        The data frame with annotation scores - same format that
        AnnotateSamples.filter_annotations and
        AnnotateSamples.assign_annotations return.
    original_labels : list
        The list of original annotations/clusters for items.
    num_annot_label : int
        A number of most common annotations per label.

    Returns
    -------
    np.array
        Array with confusion matrix values
    list
        Row names
    list
        Column names
    """

    # create confusion matrix
    ids_unique = sorted(list(set(original_labels)))
    labels_cells = annotations.idxmax(axis=1)
    lables_no_nan = labels_cells.dropna()
    labels_unique = sorted(list(set(lables_no_nan)))

    confusion_mtx = np.zeros((len(labels_unique), len(ids_unique)))
    for l, idx in zip(lables_no_nan, original_labels):
        confusion_mtx[labels_unique.index(l), ids_unique.index(idx)] += 1

    # subsample confusion matrix - take three most common cell types per column
    sel_ind = []
    for i in range(confusion_mtx.shape[1]):
        ind = confusion_mtx[:, i].argsort()[-num_annot_label:]
        sel_ind += [i for i in ind if i not in sel_ind]
    conf_sub_smp = confusion_mtx[sel_ind]
    labels_unique_sub = np.array(labels_unique)[sel_ind].tolist()

    return conf_sub_smp, labels_unique_sub, ids_unique


def confusion_matrix_plot(annotations, original_labels, num_annot_label=3):
    """
    This function plots the results of annotation comparing to annotations
    provided together with the dataset.

    Parameters
    ----------
    annotations : pd.DataFrame
        The data frame with annotation scores - same format that
        AnnotateSamples.filter_annotations and
        AnnotateSamples.assign_annotations return.
    original_labels : list
        The list of original annotations/clusters for items.
    num_annot_label : int
        The number of most common annotations per label.
    """
    conf_sub_smp, labels_unique_sub, ids_unique = confusion_matrix(
        annotations, original_labels, num_annot_label=num_annot_label)

    # make a plot
    df_cm = pd.DataFrame(conf_sub_smp, index=labels_unique_sub,
                         columns=ids_unique)
    ax = sn.heatmap(df_cm, annot=True, fmt='g')
    ax.set(xlabel='Original annotations', ylabel='Cell Types annotations')
    plt.show()


def _tsne_projection(data, num_tsne_components=2, num_pca_components=50):
    pca = PCA(n_components=num_pca_components)  # PCA first speed up the tSNE
    pca_data = pca.fit_transform(data)
    tsne = TSNE(n_components=num_tsne_components)
    data_embedded = tsne.fit(pca_data)
    return data_embedded


def annotations_in_tsne_plot(
        data, annotations, num_annot=1, eps=1, min_samples=4):
    """
    This function maps data to a TSNE plot. It then annotations on the clusters
    in the plot.

    Parameters
    ----------
    data : pd.DataFrame
        Original tabular data (usually they would be normalized).
    annotations : pd.DataFrame
        The data frame with annotation scores - same format that
        AnnotateSamples.filter_annotations and
        AnnotateSamples.assign_annotations return.
    num_annot : int
        The number of annotations per cluster that will be shown on the plot.
    eps : int
        The epsilon (neighborhood) parameter for DBSCAN clustering.
    min_samples : int
        The min_samples (core group minimal size) parameter for DBSCAN
        clustering.
    """

    embedded_data = _tsne_projection(data)

    # cluster points
    clustering = DBSCAN(eps=eps, min_samples=min_samples).fit(embedded_data)
    clusters = clustering.labels_

    # plot
    labels_cells = annotations.idxmax(axis=1)
    for l in set(clusters) - {-1}:
        incl = clusters == l
        x = np.array(embedded_data)[incl, :]
        plt.scatter(x[:, 0], x[:, 1], label=l, alpha=0.2)

        center = x.mean(axis=0)
        labels_cl = labels_cells.loc[incl].dropna()
        counts = Counter(labels_cl)

        max_el = "\n".join("{0}\n{1:.1f} %".format(
            "\n".join(k.split()), v / len(x) * 100) for k, v in
                           counts.most_common(num_annot))

        plt.annotate(max_el,
                     center,
                     horizontalalignment='center',
                     verticalalignment='center',
                     size=20 - (num_annot - 1) * 2, weight='bold')

    # plot data from cluster -1 (unclustered data)
    incl = clusters == -1
    x = np.array(embedded_data)[incl, :]
    plt.scatter(x[:, 0], x[:, 1], marker=".", alpha=0.2, color="gray")
    plt.show()
