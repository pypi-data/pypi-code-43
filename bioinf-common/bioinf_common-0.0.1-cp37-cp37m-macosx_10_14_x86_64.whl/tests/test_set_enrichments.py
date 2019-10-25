from pytest import approx

from ..algorithms.set_enrichment import SetEnrichmentComputer


def test_simple_grouping():
    # setup environment
    g = {
        'A': set([0, 1, 2]),
        'B': set([3, 4, 5])
    }
    b = set(range(50))

    # compute enrichments
    senr = SetEnrichmentComputer(g, b)  # [int]
    terms = senr.get_multiple_terms([
        set([1, 2, 8, 51]),
        set([0, 1, 2]),
        set([0, 1, 2, 3, 4, 5])
    ], throw_on_assert=False)

    # test result
    assert len(terms) == 3
    a = lambda arg: approx(arg, abs=.000001)

    assert terms[0]['group_name'].tolist() == ['A', 'B']
    assert terms[0]['p_value'].tolist() == a([.037399, 1.])
    assert terms[0]['items_in_group'].tolist() == [{1, 2}, set()]
    assert terms[0]['p_value_adj'].tolist() == a([.074797, 1.])

    assert terms[1]['group_name'].tolist() == ['A', 'B']
    assert terms[1]['p_value'].tolist() == a([.000854, 1.])
    assert terms[1]['items_in_group'].tolist() == [{0, 1, 2}, set()]
    assert terms[1]['p_value_adj'].tolist() == a([.001708, 1.])

    assert terms[2]['group_name'].tolist() == ['A', 'B']
    assert terms[2]['p_value'].tolist() == a([.012648, .012648])
    assert terms[2]['items_in_group'].tolist() == [{0, 1, 2}, {3, 4, 5}]
    assert terms[2]['p_value_adj'].tolist() == a([.012648, .012648])
