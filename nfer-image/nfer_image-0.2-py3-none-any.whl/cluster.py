import pandas as pd
import numpy as np
import sklearn.manifold
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import os
import pandas as pd
from sklearn.linear_model import LinearRegression
from tqdm import tqdm

def load_embedding(path, sample_size=None): 
    dtype = {}
    dtype['File'] = 'str'
    for i in range(2048):
        dtype[i] = np.float16
    if sample_size:
        features_df = pd.read_csv(path, index_col='File', dtype=dtype, nrows=sample_size)
    else:
        features_df = pd.read_csv(path, index_col='File', dtype=dtype)
    
    return features_df

def tsne_optimization(embedding_df, scalar_df, label):
    """
    Optimize for signals you WANT to see; this is NOT proper TSNE optimization
    """
    max_score = 0
    for i in tqdm(range(20,50)):
        tsne = sklearn.manifold.TSNE(n_components=2, perplexity=i)
        tsne_output = tsne.fit_transform(embedding_df)
        tsne_df = pd.DataFrame(tsne_output, index=embedding_df.index, columns=['tsne0', 'tsne1'])
        tsne_scalar_df = scalar_df.set_index('File').join(tsne_df, on='File')
        tsne_scalar_df = tsne_scalar_df.dropna(subset=['tsne0', 'tsne1', label])

        fig = px.scatter(tsne_scalar_df.dropna(subset=[label]).reset_index(), x="tsne0", y="tsne1", color=label, hover_data=['File'])
        fig.show()

        # assess goodness of fit
        reg = sklearn.linear_model.LinearRegression().fit(tsne_scalar_df[['tsne0', 'tsne1']], tsne_scalar_df[label])
        fit_score = reg.score(tsne_scalar_df[['tsne0', 'tsne1']], tsne_scalar_df[label])
        print('perplexity: ', i,  ' fit score: ', fit_score)
        if fit_score > max_score:
            optimized_output = tsne_output
            max_score = fit_score


def tsne_from_dataframe(exp_name, embedding_df, scalar_df, label=None, optimize=False):

    if optimize:
        tsne_output = tsne_optimization(embedding_df, scalar_df, label)
    else:
        tsne = sklearn.manifold.TSNE(n_components=2, perplexity=30)
        tnse_output = tsne.fit_transform(embedding_df)

    tsne_df = pd.DataFrame(tsne_output, index=embedding_df.index, columns=['tsne0', 'tsne1'])
    tsne_scalar_df = tsne_df.join(scalar_df, on='File')
    tsne_scalar_df.to_csv('{}_tsne.csv'.format(exp_name))
    return tsne_scalar_df

def getImage(path):
    img = plt.imread(path)
    return OffsetImage(img, zoom=0.5)

def myround(x, base=5):
    return base * round(x/base)

def tsne_image_figure_binary(tsne_df, domainLabel, domainA, domainB, domainA_dir, domainB_dir):

    tsne_df['tsne0'] = myround(tsne_df['tsne0'], base=5)
    tsne_df['tsne1'] = myround(tsne_df['tsne1'], base=5)

    tsne_df = tsne_df.drop_duplicates(subset=['tsne0', 'tsne1'])

    for index, row in tsne_df.iterrows():
        if row[domainLabel] == domainA:
            path = os.path.join(domainA_dir, row['File'])
            bboxprops = {'fc':'red'}
        elif row[domainLabel] == domainB:
            path = os.path.join(domainB_dir, row['File'])
            bboxprops = {'fc':'cyan'}
        ab = AnnotationBbox(getImage(path), (row['tsne0'], row['tsne1']), bboxprops=bboxprops)
        ax.add_artist(ab)