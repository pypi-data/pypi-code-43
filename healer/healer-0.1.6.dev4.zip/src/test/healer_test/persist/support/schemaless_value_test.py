
from healer.persist.support.schemaless import *


def test_value():
    print()

    tree = lambda : defaultdict(tree)

    data_one = {
        'a':{
            'a': 'aa',
        },
        'b':{
            'b': 'bb',
        }
    }
    print(data_one)
    print(json.dumps(data_one))

    data_two = tree()
    data_two['a']['b']['c'] = 'abc'

    print(data_two)
    print(json.dumps(data_two))

    def make_tree(src:dict):
        result = tree()
        for key, value in src.items():
            if isinstance(value, dict):
                value = make_tree(value)
            result[key] = value
        return result

#
    data_tree = make_tree(data_one)
    data_tree['c']['c'] = 'cc'
    print(data_tree)
    print(json.dumps(data_tree))
