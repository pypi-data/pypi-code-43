import pandas as pd

from ngs_toolkit.demo import generate_project
from sklearn.decomposition import NMF
from ngs_toolkit.graphics import plot_projection

a = generate_project(n_factors=3)
a.normalize()

m = a.annotate_samples(save=False, assign=False)

nmf = NMF()
x_new = pd.DataFrame(
    nmf.fit_transform(a.matrix_norm.T),
    index=m.columns)
color_dataframe = a.get_level_colors(index=m.columns, as_dataframe=True)

plot_projection(
    x_new,
    color_dataframe=color_dataframe,
    dims=8, output_file="nmf.svg",
    attributes_to_plot=["A", "B"],
    plot_group_centroids=True,
    axis_ticklabels_name="NMF")
