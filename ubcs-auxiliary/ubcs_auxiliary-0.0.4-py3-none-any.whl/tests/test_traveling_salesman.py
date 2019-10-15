from numpy import zeros, array_equal

from ubcs_auxiliary import traveling_salesman as ts

def test_euclidian_distance():
    x = (1,2,3)
    y = (2,3,4)
    assert (ts.euclidean_distance(x,y) == 3**0.5)
    x = (1,2,3)
    y = (2,4,4)
    assert (ts.euclidean_distance(x,y) == (1**2+2**2+1**2)**0.5)

def test_create_test_sequence():
    N = 20
    dim = 2
    arr,vary = ts.create_test_sequence(N,dim = dim)
    assert arr.shape == (N,dim)
    assert vary[0] == 0
    assert vary[-1] == 0
    assert vary.sum() == N-2

def test_total_distance():
    from numpy import array
    arr = array([[ 0.        ,  0.        ],
       [-3.16353381, -4.95307408],
       [-2.73465273, -3.9936309 ],
       [ 3.90539788, -0.03624822],
       [-3.26566328,  3.78071339],
       [ 4.05165855, -1.08678949],
       [ 2.27780317,  3.78714615],
       [ 4.76618918, -4.29571196],
       [ 0.89862702, -4.12542064],
       [ 0.        ,  0.        ]])
    vary = array([0., 1., 1., 1., 1., 1., 1., 1., 1., 0.])
    assert round(ts.total_distance(arr),7) == round(53.30737952083856,7)
    # rounded to 7 decimals due to precisiob in arr
