import argparse
import os

import numpy as np
import pandas as pd

import fastemc

parser = argparse.ArgumentParser(
    description='Fast Exponential Monte Carlo'
)

parser.add_argument(
    '--features', '-f', type=str, default='features.csv',
    help='input csv filename containing feature data'
)
parser.add_argument(
    '--labels', '-l', type=str, default='labels.csv',
    help='input csv filename containing class labels'
)
parser.add_argument(
    '--results', '-r', type=str, default='results.csv',
    help='results csv filename'
)
parser.add_argument(
    '--num_mc_steps', '-N', type=int, default=10000,
    help='number of features in each cluster used for classification'
)
parser.add_argument(
    '--cluster_size', '-c', type=int, default=20,
    help='number of features in each cluster used for classification'
)
parser.add_argument(
    '--num_clusters', '-k', type=int, default=40,
    help='number of features in each cluster used for classification'
)
parser.add_argument(
    '--max_swaps_per_step', '-m', type=int, default=20,
    help='number of features in each cluster used for classification'
)
parser.add_argument(
    '--num_fast_mc_steps', '-n', type=int, default=20,
    help='number of features in each cluster used for classification'
)
parser.add_argument(
    '--log_noise', '-T', type=float, default=0.03,
    help='number of features in each cluster used for classification'
)

args = parser.parse_args()

args.features = os.path.realpath(args.features)
args.labels = os.path.realpath(args.labels)
args.results = os.path.realpath(args.results)
def path_check(path):
    return (
        os.path.exists(path), 
        """
        File not found: {}.
        """.format(path)
    )
assert path_check(args.features)
assert path_check(args.labels)
assert path_check(args.results)

try:
    features = pd.read_csv(args.features, index_col=0)
except FileNotFoundError:
    print('Provide a features file using the --features flag')
try:
    labels = pd.read_csv(args.labels, index_col=0)
except FileNotFoundError:
    print('Provide a labels file using the --features flag')

def save_results(global_optimum_score, global_optimum_choice):
    ordering = np.argsort(global_optimum_score)
    global_optimum_score = global_optimum_score[ordering]
    global_optimum_choice = global_optimum_choice[ordering]
    results = pd.DataFrame(
        [
            [score, *features.columns[choice]]
            for score, choice in zip(global_optimum_score, global_optimum_choice)
        ],
        columns=[
            'score', 
            *('feature_{}'.format(i) for i in range(args.cluster_size))
        ]
    )
    results.to_csv(args.results)

_ = fastemc.run(
    features.values, labels.values,
    num_mc_steps=args.num_mc_steps,
    cluster_size=args.cluster_size,
    num_clusters=args.num_clusters,
    max_swaps_per_step=args.max_swaps_per_step,
    num_fast_mc_steps=args.num_fast_mc_steps,
    log_noise=args.log_noise,
    logger=save_results
)