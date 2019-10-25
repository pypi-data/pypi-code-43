import sys

from typing import TypeVar, Generic, Dict, Set, List

import pandas as pd

from scipy.stats import fisher_exact
from statsmodels.sandbox.stats.multicomp import multipletests

from tqdm import tqdm as tqdm

from ..tools.list_chunk_parallelization import execute_parallel


T = TypeVar('T')


class SetEnrichmentComputer(Generic[T]):
    def __init__(
        self,
        groupings: Dict[str, Set[T]], background: Set[T],
        alternative_hypothesis: str = 'greater'
    ) -> None:
        self.groupings = groupings
        self.background = background
        self.alternative_hypothesis = alternative_hypothesis

        self.show_stats()

    def show_stats(self) -> None:
        """ Show input-database statistics
        """
        group_elements = set([e
                              for val in self.groupings.values()
                              for e in val])

        # general stats
        print(f'Number of groups: {len(self.groupings)}', file=sys.stderr)
        print(
            f'Unique group elements: {len(group_elements)}',
            file=sys.stderr)
        print(
            f'Background elements: {len(self.background)}',
            file=sys.stderr)

        # group/background overlap
        overlap = group_elements & self.background
        num = len(overlap)

        group_in_bg = num / len(group_elements)
        print(
            f'{round(group_in_bg*100, 1)}% of group elements in background',
            file=sys.stderr)

    def get_multiple_terms(
        self, item_set_list: List[Set[T]], n_jobs: int = 0, **kwargs
    ) -> List[pd.DataFrame]:
        """ Parallelized enrichment computation for many item sets
        """
        return execute_parallel(
            item_set_list, self._np_get_multiple_terms,
            kwargs=kwargs, n_jobs=n_jobs)

    def _np_get_multiple_terms(
        self, item_set_list: List[Set[T]], **kwargs
    ) -> List[pd.DataFrame]:
        """ Helper function for `get_multiple_terms`
        """
        term_list = []
        for item_set in tqdm(item_set_list):
            terms = self.get_terms(item_set, **kwargs)
            term_list.append(terms)
        return term_list

    def get_terms(
        self,
        item_set: Set[T], throw_on_assert: bool = True,
        verbose: bool = True
    ) -> pd.DataFrame:
        """ Compute enrichment of given item set over all groups
        """
        cur_background = self.background.copy()

        # check if all given entries are in background set
        # TODO: stop tinkering with data
        items_bg_diff = item_set - cur_background
        msg = f'Following genes not in background: {items_bg_diff}'
        if throw_on_assert:
            assert len(items_bg_diff) == 0, msg
        else:
            if len(items_bg_diff) != 0:
                cur_background.update(items_bg_diff)

                if verbose:
                    print(
                        msg + '. Appending to background set',
                        file=sys.stderr)

        # compute enrichments
        result = []
        for name, group in self.groupings.items():
            pv = self._compute_enrichment(
                item_set, group, cur_background,
                alternative_hypothesis=self.alternative_hypothesis)
            result.append((name, pv, item_set & group))
        df = pd.DataFrame(
            result, columns=['group_name', 'p_value', 'items_in_group'])

        # do multiple testing corrections
        _, pval_cor, _, _ = multipletests(
            df['p_value'].tolist(), method='fdr_bh')
        df['p_value_adj'] = pval_cor

        return df.sort_values('p_value')

    @staticmethod
    def _compute_enrichment(
        item_set: Set[T],
        group: Set[T], background: Set[T],
        alternative_hypothesis: str
    ) -> float:
        """Compute enrichment of item set in given groupself.

        Alternative hypothesis: 'two-sided', 'less', 'greater'
        """
        item_in_group = item_set & group
        item_notin_group = item_set - group
        bg_in_group = background & group
        bg_notint_group = background - group

        conting_table = [
            [len(item_in_group), len(item_notin_group)],
            [len(bg_in_group), len(bg_notint_group)]
        ]

        oddsratio, p_value = fisher_exact(
            conting_table,
            alternative=alternative_hypothesis)
        return p_value
