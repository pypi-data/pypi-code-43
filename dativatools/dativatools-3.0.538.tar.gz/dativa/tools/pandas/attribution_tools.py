"""Attribution methods implemented on pandas dataframes."""
import math
import logging
import multiprocessing
from .columns import get_unique_column_name

logger = logging.getLogger('dativa.attribution.shapley')

try:
    import pandas as pd
except ImportError:
    pd = None


def _get_marginal_score(pop_size,
                        item_label,
                        coalitions,
                        infer_missing,
                        default_value):
    score = 0
    skipped = 0
    run = 0
    total_scored = 0
    total_skipped = 0

    for label in coalitions:
        if label & item_label > 0:
            run = run + 1
            subset_label = label - item_label
            superset = coalitions.get(subset_label + item_label, default_value)
            superset_score = superset["scoring_conversions"]
            superset_impressions = superset["exposures"]

            subset = coalitions.get(subset_label, default_value)
            subset_score = subset["scoring_conversions"]
            subset_size = subset["number_players"]

            total_scored = total_scored + superset_impressions

            if subset_label > 0 and infer_missing and (superset_score == 0 or subset_score == 0):
                if superset_score > 0 or subset_score > 0:
                    skipped = skipped + 1
                    total_skipped = total_skipped + superset_impressions
            else:
                scaling_factor = math.factorial(subset_size) * math.factorial(pop_size - subset_size - 1)
                score = score + (superset_score - subset_score) * scaling_factor


    return score, skipped, run, total_scored, total_skipped


# Wrapper function for the multithreading to populate the shared results
def _score(results,
           skipped,
           run,
           total_scored,
           total_skipped,
           element,
           pop_size,
           item_label,
           coalitions,
           infer_missing,
           default_value):
    results[element], skipped[element], run[element], total_scored[element], total_skipped[
        element] = _get_marginal_score(pop_size,
                                       item_label,
                                       coalitions,
                                       infer_missing,
                                       default_value)


class Shapley:
    """Shapley attribution of scores to members of sets.

    See `medium <https://towardsdatascience.com/one-feature-attribution-method-to-supposedly-rule-them-all-shapley-values-f3e04534983d>`_
    or `wiki <https://en.wikipedia.org/wiki/Shapley_value>`_ for details on the math. The aim is to apportion scores between the members of a set
    responsible for producing that score.

    :param df_impression: impression data to be parsed.
    :param df_conversions: conversion events to score
    :param id_column: column containing the id values of users who viewed impressions / converted.
    :param sets_column: label of the column containing features
    :param default_score: score to assign to any combination that has not been observed, defaults to 0.
    :param infer_missing: {'average', 'regression', 'filter', False} defaults to False. To be implemented
    :param metric: The column used to calculate the Shapley value
    :param normalize_impressions: defaults to True, normalize the score column according to the number of impressions

    :type df_impressions:  pandas.DataFrame
    :type df_conversions:  pandas.DataFrame
    :type id_column: str
    :type sets_column: str
    :type default_score: int or float
    :type infer_missing: bool or str
    """

    def __init__(self,
                 df_impression,
                 df_conversions,
                 id_column,
                 sets_column,
                 default_score=0,
                 infer_missing=False,
                 normalize_impressions=True,
                 metric='conversions'):

        if not pd:
            raise ImportError("pandas must be installed to run Shapley")

        if infer_missing and infer_missing not in ('filter'):  # to be extended
            raise KeyError('{} is not a valid option for infer_missing'.format(infer_missing))

        self.default_value = default_score
        self.infer_missing = (infer_missing == 'filter')
        self.normalize_impressions = normalize_impressions

        if metric in df_conversions.columns.tolist():
            self.conversion_col = metric
        elif metric in ['conversions']:
            # this is redundant because we've already checked if it's in the df, which sort of defeats the purpose?
            # i'll have to think about how anyone would actually use this
            self.conversion_col = get_unique_column_name(df_conversions, metric)
        else:
            raise KeyError('{} is not a valid option for metric'.format(metric))

        if type(default_score) is not int:
            raise TypeError('default_score: {} is not valid - must be numeric'.format(default_score))

        self.sets_column = sets_column

        self.population = df_impression[sets_column].unique()
        self.conversion_dict = self._build_conversion_dict(self.population)

        self.coalitions = self._get_coalitions(df_impression, df_conversions, id_column, default_score)

    def _get_coalitions(self, df_impression, df_conversions, id_column, default_value):

        label_column = get_unique_column_name(df_impression, 'label')
        number_players_column = get_unique_column_name(df_impression, 'number_players')
        scoring_conversions = get_unique_column_name(df_impression, 'scoring_conversions')

        # Group by the exposed device and assign the integer label for the set of campaigns viewed...
        lookup = pd.DataFrame.from_dict(self.conversion_dict, orient='index', columns=[label_column])
        g = df_impression.drop_duplicates().join(lookup, on=self.sets_column).groupby(id_column, as_index=False)[
            label_column].sum()

        # Add a conversion column if we don't already have it
        if self.conversion_col not in df_conversions.columns:
            df_conversions[self.conversion_col] = 1  # so we can count them
            m = pd.merge(g, df_conversions, on=id_column, how='left')
            df_conversions.drop(columns=self.conversion_col, inplace=True)
        else:
            m = pd.merge(g, df_conversions, on=id_column, how='left')

        # Now group by the set and count the number of conversions on each
        df_scored = m.groupby(label_column, as_index=False).agg({self.conversion_col: sum,
                                                                 id_column: pd.Series.nunique})

        # Add in each set
        df_scored[number_players_column] = df_scored[label_column].apply(lambda x: len([a for a in bin(x) if a == '1']))

        if self.normalize_impressions:
            df_scored[scoring_conversions] = df_scored[self.conversion_col] / df_scored[id_column]
        else:
            df_scored[scoring_conversions] = df_scored[self.conversion_col]

        df_scored.rename(columns={number_players_column: "number_players",
                                  id_column: "exposures",
                                  self.conversion_col: "conversions",
                                  scoring_conversions: "scoring_conversions",
                                  }, inplace=True)

        return df_scored.set_index(label_column)[["number_players",
                                                  "exposures",
                                                  "conversions",
                                                  "scoring_conversions"]].to_dict(orient='index')

    @staticmethod
    def _build_conversion_dict(population):
        # Convert a subset {x_i} into a unique integer sum( 2 ** i ) for i in [0, n)
        # vastly better performance
        return {member: 2 ** i for i, member in enumerate(population)}

    def _reverse_conversion_dict(self, l):
       return [list(self.conversion_dict.keys())[i] for i in
                [i for i, bit in enumerate(reversed([int(bit) for bit in "{0:b}".format(l)])) if bit == 1]]

    def run(self):

        # get the constant values
        pop_size = len(self.population)

        results = dict()
        skipped = dict()
        run = dict()
        total_scored = dict()
        total_skipped = dict()

        default = {"sets": "missing",
                   "number_players": 0,
                   "exposures": 0,
                   "conversions": 0,
                   "scoring_conversions": self.default_value
                   }

        for element in self.population:

            _score(results,
                   skipped,
                   run,
                   total_scored,
                   total_skipped,
                   element,
                   pop_size,
                   self.conversion_dict[element],
                   self.coalitions,
                   self.infer_missing,
                   default)

        # Check the threads have worked - they fail silently if they don't work
        assert (len(results) == pop_size)

        # Finalize the calculation and log out bad results
        for element in self.population:
            results[element] = results[element] * (1 / math.factorial(len(self.population)))
            if skipped[element] > 0:
                logger.warning("Skipped {0}/{1} {3:.0%} for {2}".format(skipped[element], run[element], element,
                                                                        total_skipped[element] / total_scored[element]))
            if results[element] < 0:
                logger.warning("Negative score for {0} = {1}".format(element, results[element]))

        # Prepare the data frame to return
        df = pd.DataFrame.from_dict(results, orient='index')
        df.reset_index(inplace=True)
        df.rename(columns={'index': self.sets_column, 0: 'Shapley_val'}, inplace=True)
        df.sort_values('Shapley_val', ascending=False, inplace=True)
        df.reset_index(inplace=True, drop=True)

        return df
