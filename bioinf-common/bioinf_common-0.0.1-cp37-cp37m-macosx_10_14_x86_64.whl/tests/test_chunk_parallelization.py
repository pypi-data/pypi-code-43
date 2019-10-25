import pytest
from packaging import version

import joblib

from ..tools.list_chunk_parallelization import execute_parallel, parallel_chunks, _yield_chunks


def _f(xs, arg, denom=1):
    return [(x**2 + arg) / denom for x in xs]
def _g(xs):
    return {f'key_{x}': x**3 for i, x in enumerate(xs)}
def _h(xs):
    return xs[0]
def _i(xs):
    return {f'key_{x}': x for x in xs}

@parallel_chunks
def _deco(xs):
    return _g(xs)

def test_yield_chunks():
    data = list(range(5))

    with pytest.raises(RuntimeError):
        list(_yield_chunks(data, 0))

    assert list(_yield_chunks(data, 1)) == [[0,1,2,3,4]]
    assert list(_yield_chunks(data, 2)) == [[0,1,2], [3,4]]
    assert list(_yield_chunks(data, 3)) == [[0,1], [2,3], [4]]
    assert list(_yield_chunks(data, 4)) == [[0,1], [2], [3], [4]]
    assert list(_yield_chunks(data, 5)) == [[0], [1], [2], [3], [4]]
    assert list(_yield_chunks(data, 6)) == [[0], [1], [2], [3], [4], []]
    assert list(_yield_chunks(data, 7)) == [[0], [1], [2], [3], [4], [], []]

def test_simple_function():
    input_data = list(range(10))
    expected_result = _f(input_data, 3, denom=4)

    res = execute_parallel(input_data, _f, args=(3,), kwargs={'denom': 4})
    assert res == expected_result

@pytest.mark.parametrize('input_data', [[], [1], [1,2], [1,2,3], [1,2,3,4]])
def test_shortlist_input(input_data):
    expected_result = _f(input_data, 0)
    res = execute_parallel(input_data, _f, args=(0,), n_jobs=3)
    assert res == expected_result

def test_dict_output():
    input_data = list(range(10))
    expected_result = _g(input_data)

    res = execute_parallel(input_data, _g)
    assert res == expected_result

@pytest.mark.parametrize('input_data', [42, 'foo', False])
def test_invalid_input(input_data):
    with pytest.raises(TypeError):
        execute_parallel(input_data, _h)

@pytest.mark.parametrize('input_data', [[12], ['bar'], [True]])
def test_invalid_output(input_data):
    with pytest.raises(RuntimeError):
        execute_parallel(input_data, _h)

@pytest.mark.skipif(
    version.parse(joblib.__version__) < version.parse('0.11.1'),
    reason='joblib not recent enough')
def test_decorator():
    input_data = list(range(-5, 5))
    expected_result = _g(input_data)

    res = _deco(input_data)
    assert res == expected_result

@pytest.mark.parametrize('extra_data', [['1', '2'], {'1': 2}])
def test_nested_input(extra_data):
    input_data = [('t1', extra_data), ('t2', extra_data)]
    expected_result = _i(input_data)

    res = execute_parallel(input_data, _i)
    assert res == expected_result
