import pandas as pd
import birch

def load_data(path,target):
    df = pd.read_csv(path)
    y = df[target]
    X = df.drop(labels = target, axis = 1)
    X = X.apply(pd.to_numeric)
    return df,X,y

def get_data(file_path,target='defects',normal_class='normal'):
    train_df, train_X, train_y = load_data(file_path,target)
    y_train = []
    for instance in train_y.values:
        if instance == normal_class:
            y_train.append(1)
        else:
            y_train.append(-1)
    y_train = pd.Series(y_train)
    train_df.defects.unique()
    return train_df,train_X,y_train

# Cluster Driver
def cluster_driver(file,print_tree = False):
    _, train_X, train_y = get_data(file)
    cluster = birch.birch(branching_factor=20)
    cluster.fit(train_X,train_y)
    cluster_tree,max_depth = cluster.get_cluster_tree()
    cluster_tree = cluster.model_adder(cluster_tree)
    cluster_tree = cluster.outlier_model_adder(cluster_tree)
    if print_tree:
        cluster.show_clutser_tree()
    return cluster,cluster_tree,max_depth