from ..tools.datastructure_conversion import infer_design_matrix


def test_default_parameters():
    df = infer_design_matrix({
        'sample01': ['A', 'B', 'C'],
        'sample03': ['D', 'A', 'B'],
        'sample04': ['F', 'C', 'E', 'D'],
        'sample02': ['G', 'H']
    })

    assert df.index.tolist() == ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    assert df.columns.tolist() == ['sample01', 'sample02', 'sample03', 'sample04']

    assert df.values.tolist() == [
        [1., 0., 1., 0.],
        [1., 0., 1., 0.],
        [1., 0., 0., 1.],
        [0., 0., 1., 1.],
        [0., 0., 0., 1.],
        [0., 0., 0., 1.],
        [0., 1., 0., 0.],
        [0., 1., 0., 0.]
    ]

def test_special_parameters():
    feature_dict = {
        'S01': ['A', 'C'],
        'S02': ['B', 'C']
    }
    value_dict = {
        'S01': {'A': .3, 'C': .1},
        'S02': {'B': .9, 'C': .7}
    }

    df = infer_design_matrix(
        feature_dict,
        feature_value_dict=value_dict,
        default_value=-1)

    assert df.index.tolist() == ['A', 'B', 'C']
    assert df.columns.tolist() == ['S01', 'S02']

    assert df.values.tolist() == [
        [.3, -1],
        [-1, .9],
        [.1, .7]
    ]
