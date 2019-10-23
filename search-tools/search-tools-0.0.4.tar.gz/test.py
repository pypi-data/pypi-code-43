import unittest
import numpy as np
import pandas as pd

from search_tools.metrics import ndcg_at_k, dcg_with_rel, ranking_ndcg_at_k
from search_tools.metrics import ndcg_at_k_constructor, ranking_ndcg_at_k_constructor
from search_tools.models import ClickModel

def generate_data():
    pos_distr = np.random.random(size=(4,))
    queries = np.array(['do a search', 'i like to search', 'things for me', 'shopping item'])
    results = np.array(['doc0', 'doc1', 'doc2', 'doc3', 'doc4', 'doc5', 'doc6', 'doc7'])
    affinities = pd.DataFrame(columns=queries, index=results, data=np.random.random(size=(len(results), len(queries))))
    cols = ['_query', '_result', '_position', '_click']
    outcomes = {
        'do a search':[
            ['doc0', 'doc2', 'doc4', 'doc5'],
            ['doc2', 'doc0', 'doc5', 'doc6'],
            ['doc5', 'doc6', 'doc0', 'doc4']
        ],
        'i like to search':[
            ['doc2', 'doc7', 'doc6', 'doc1'],
            ['doc2', 'doc1', 'doc0', 'doc7'],
            ['doc1', 'doc6', 'doc7', 'doc2']
        ],
        'things for me':[
            ['doc5', 'doc4', 'doc3', 'doc2'],
            ['doc3', 'doc2', 'doc5', 'doc6'],
            ['doc2', 'doc3', 'doc4', 'doc5']
        ],
        'shopping item':[
            ['doc0', 'doc1', 'doc3', 'doc2'],
            ['doc5', 'doc2', 'doc3', 'doc0'],
            ['doc5', 'doc0', 'doc1', 'doc2']
        ]
    }

    dataset = pd.DataFrame(columns=cols)

    for i in range(100):
        search_term = np.random.choice(queries)
        returned_results = np.random.randint(0, 3)
        results = outcomes[search_term][returned_results]
        rows = pd.DataFrame(columns=cols)
        rows['_result'] = results
        rows['_query'] = search_term
        rows['_position'] = np.arange(4)
        ps = []
        for i, row in rows.iterrows():
            p_pos = pos_distr[i]
            p_qr = affinities.loc[row['_result'], row['_query']]
            ps.append(p_qr * p_pos)
        outcome = np.random.random(size=(4,))
        rows['_click'] = (ps > outcome).astype(int)
        dataset = pd.concat([dataset, rows], axis=0)

    clicks = dataset.groupby(['_query', '_result', '_position']).apply(lambda x: x['_click'].sum())
    count = dataset.groupby(['_query', '_result', '_position']).count()

    df = pd.concat([clicks, count], axis=1)
    df.columns = ['total_clicks', 'total_sessions']
    return df.reset_index(), pos_distr, affinities

class ModelsTest(unittest.TestCase):

    def setUp(self):
        self.df, _, _ = generate_data()

    def test_run_click_model(self):
        data = self.df
        model = ClickModel(
            data,
            query_col='_query',
            result_col='_result',
            position_col='_position',
            sessions_count='total_sessions',
            events_count='total_clicks',
            history=True,
            strategy='prior'
        )
        qr, pos = model.fit(n_iterations=4, alternate=True)
        assert isinstance(qr, pd.DataFrame)
        assert isinstance(pos, pd.DataFrame)


class MetricsTest(unittest.TestCase):

    def test_dcg_with_rel(self):
        rels = [.5, .3, .6, .8]
        result = dcg_with_rel(rels)
        assert np.abs((result - 1.137)) < 0.01


    def test_ndcg_at_k(self):
        rels = [.5, .3, .6, .8]
        result = ndcg_at_k(rels)
        best = 1.373
        expected = 1.137/best
        assert np.abs((result - expected)) < 0.01

    def test_ndcg_at_k_with_k(self):
        rels = [.5, .3, .6, .8]
        result = ndcg_at_k(rels, k=4)
        best = 1.373
        expected = 1.137/best
        assert np.abs((result - expected)) < 0.01

    def test_big_k(self):
        rels = [.5, .3, .6, .8]
        result = ndcg_at_k(rels, k=10)
        best = 1.373
        expected = 1.137/best
        assert np.abs((result - expected)) < 0.01

    def test_little_k(self):
        rels = [.5, .3, .6, .8]
        result = ndcg_at_k(rels, k=2)
        best = 1.373
        expected = 1.137/best
        assert np.abs((result - expected)) > 0.01

    def test_ndcgatk_with_zeros(self):
        rels = [0, 0, 0, 0]
        result = ndcg_at_k(rels, k=None)
        assert result == 0

    def test_ordered_ndcgatk(self):
        best = [123, 332, 101, 100, 777, 9, 456]
        best = [str(x) for x in best]
        other = [101, 456, 332, 100, 999]
        other = [str(x) for x in other]

        return ranking_ndcg_at_k(best, other, k=None)

    def test_constructors(self):
        func = ndcg_at_k_constructor(k=5)
        func = ranking_ndcg_at_k_constructor(k=5)

if __name__ in "__main__":
    unittest.main()
