import warnings

import numpy as np
import pandas as pd
import scipy as sp
from sklearn.exceptions import ConvergenceWarning, DataConversionWarning
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
from tqdm import tqdm

warnings.filterwarnings(action='ignore', category=ConvergenceWarning)
warnings.filterwarnings(action='ignore', category=DataConversionWarning)

def score(features, labels, setting='fast', cv=5):
    def wrapper(choice):
        if setting=='fast':
            clf = LogisticRegression(solver='lbfgs', multi_class='multinomial', max_iter=10)
        if setting=='slow':
            clf = LogisticRegression(solver='lbfgs', multi_class='multinomial', max_iter=100)
        return np.mean(cross_val_score(clf, features[:,choice], labels, cv=5))
    return wrapper

def classify(features, training_choice, training_labels):
    clf = LogisticRegression(solver='lbfgs', multi_class='multinomial', max_iter=100)
    clf.fit(training_choice, training_labels)
    return clf.predict(features)

def default_logger(*_):
    pass

def run(
        features, labels,
        num_mc_steps=10000,
        cluster_size=20,
        num_clusters=40,
        max_swaps_per_step=20,
        num_fast_mc_steps=20,
        log_noise=0.03,
        random_seed=0,
        logger=default_logger
):
    """
    Given input set of features and labels
    returns a subset of features that are optimal for classification
    """
    # setup
    np.random.seed(random_seed)

    features = np.array(features)
    labels = np.array(labels)
    score_fast = score(features, labels, setting='fast')
    score_slow = score(features, labels, setting='slow')

    num_features = features.shape[1]

    current_choice=np.random.choice(
        np.arange(num_features),
        size=cluster_size,
        replace=False
    )
    current_score=score_fast(current_choice)

    proposed_choice=current_choice
    proposed_score=current_score

    local_optimum_choice=current_choice
    local_optimum_score=current_score
    local_optimum_score_slow=score_slow(local_optimum_choice)

    global_optimum_choice=np.array([current_choice for _ in range(num_clusters)])
    global_optimum_score=np.array([local_optimum_score_slow for _ in range(num_clusters)])

    # outer Monte Carlo loop
    print('Running fastemc...')
    for _ in tqdm(range(num_mc_steps)):
        # inner "fast" Monte Carlo loop
        for _ in tqdm(range(num_fast_mc_steps)):
            num_to_swap = min(np.random.randint(2, max_swaps_per_step+1), num_features)
            proposed_insertion = np.random.choice(
                np.delete(np.arange(num_features), current_choice),
                size=num_to_swap,
                replace=False
            )
            proposed_removal = np.random.choice(
                cluster_size, 
                size=num_to_swap,
                replace=False
            )
            proposed_choice = current_choice
            np.put(proposed_choice, proposed_removal, proposed_insertion)

            proposed_score = score_fast(proposed_choice)

            if proposed_score > current_score - log_noise*np.log(1/np.random.rand()):
                current_choice = proposed_choice
                current_score = proposed_score

                if current_score > local_optimum_score:
                    local_optimum_choice = current_choice
                    local_optimum_score = current_score

        # slow scoring
        local_optimum_score_slow = score_slow(local_optimum_choice)
        if local_optimum_score_slow > np.min(global_optimum_score):
            min_index = np.argmin(global_optimum_score)
            global_optimum_choice[min_index] = local_optimum_choice
            global_optimum_score[min_index] = local_optimum_score_slow

        local_optimum_score = current_score
        local_optimum_choice = current_choice

        logger(global_optimum_score, global_optimum_choice)

    return global_optimum_score, global_optimum_choice
