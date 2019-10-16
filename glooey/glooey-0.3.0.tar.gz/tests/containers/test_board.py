#!/usr/bin/env python3

import pytest, glooey
from pytest import approx
from glooey import Board, UsageError

@pytest.fixture
def w():
    child = glooey.Widget()
    child._claimed_width = 1
    return lambda **pin: Board._calc_min_board_size('width', child, pin)

@pytest.fixture
def h():
    child = glooey.Widget()
    child._claimed_height = 1
    return lambda **pin: Board._calc_min_board_size('height', child, pin)


@pytest.mark.skip
def test_make_pin__underspecify():
    f = lambda **kwargs: Board._make_pin(kwargs)

    legal = {
        'rect': Rect(0, 0, 1, 1),

        'left': 0,
        'left_percent': 0.0,
        'center_x': 5,
        'center_x_percent': 0.5,
        'right': 10,
        'right_percent': 1.0,
        'top': 10,
        'top_percent': 1.0,
        'center_y': 5,
        'center_y_percent': 0.5,
        'bottom': 0,
        'bottom_percent': 0.0,

        'top_left': (0, 10),
        'top_left_percent': (0.0, 1.0),
        'top_center': (5, 10),
        'top_center_percent': (0.5, 1.0),
        'top_right': (10, 10),
        'top_right_percent': (1.0, 1.0),
        'center_left': (0, 5),
        'center_left_percent': (0.0, 0.5),
        'center': (5, 5),
        'center_percent': (0.5, 0.5),
        'center_right': (10, 5),
        'center_right_percent': (1.0, 0.5),
        'bottom_left': (0, 0),
        'bottom_left_percent': (0.0, 0.0),
        'bottom_center': (5, 0),
        'bottom_center_percent': (0.5, 0.0),
        'bottom_right': (10, 0),
        'bottom_right_percent': (1.0, 0.0),

        'height': 1,
        'height_percent': 0.1,
        'width': 1,
        'width_percent': 0.1,

        'layer': 0,
    }

    underspecified = [
            'left', 'left_percent',
            'center_x', 'center_x_percent',
            'right', 'right_percent',
            'top', 'top_percent',
            'center_y', 'center_y_percent',
            'bottom', 'bottom_percent',
            'width', 'width_percent',
            'height', 'height_percent',
    ]

    # Allow user to specify top-left and bottom-right?
    #
    #   - If any args redundant: error
    #   - 3 position args: error
    #   - 2 position args: size implied, must not get size arg
    #   - 1 position arg: must get size
    #   - 0 position arg: underspecified
    #
    # It will really be too hard to calculate things if pixel positions are 
    # mixed with percent positions, or if positive mixed with negative. 
    #
    # I think this is just too hard.  I would have to make the pin a real class 
    # that could abstract away some of the complexity, e.g. with min_width() 
    # and real_width(board_width) methods.
    #
    # Allow negative widths (i.e. width of container minus given value).

    over_specified = [
            'rect',
            'top_left', 'top_left_percent',
            'top_center', 'top_center_percent',
            'top_right', 'top_right_percent',
            'center_left', 'center_left_percent',
            'center', 'center_percent',
            'center_right', 'center_right_percent',
            'bottom_left', 'bottom_left_percent',
            'bottom_center', 'bottom_center_percent',
            'bottom_right', 'bottom_right_percent',
    ]

    for a in underspecified:
        with pytest.raises(UsageError):
            f(**kw)

    for a, b in itertools.combinations(overspecified, 2):
        with pytest.raises(UsageError):
            f(**kw)

def test_calc_min_board_size__width_absolute__anchor_absolute(w):
    assert w(left=0, width=1) == 1
    assert w(left=1, width=1) == 2
    assert w(left=-1, width=1) == 1

    assert w(center_x=1, width=1) == approx(1.5)
    assert w(center_x=-1, width=1) == approx(1.5)

    assert w(right=-0., width=1) == 1
    assert w(right=1, width=1) == 1
    assert w(right=-1, width=1) == 2

    with pytest.raises(UsageError):
        w(left=-0., width=1)
    with pytest.raises(UsageError):
        w(center_x=0, width=1)
    with pytest.raises(UsageError):
        w(center_x=-0., width=1)
    with pytest.raises(UsageError):
        w(right=0, width=1)

def test_calc_min_board_size__width_absolute__anchor_percent(w):
    assert w(left_percent=0.0, width=1) == 1
    assert w(left_percent=0.5, width=1) == 2
    
    assert w(center_x_percent=0.5, width=1) == 1

    assert w(right_percent=0.5, width=1) == 2
    assert w(right_percent=1.0, width=1) == 1
    
    with pytest.raises(UsageError):
        w(left_percent=1.0, width=1)
    with pytest.raises(UsageError):
        w(center_x_percent=0.0, width=1)
    with pytest.raises(UsageError):
        w(center_x_percent=1.0, width=1)
    with pytest.raises(UsageError):
        w(right_percent=0.0, width=1)
    
def test_calc_min_board_size__width_percent__anchor_absolute(w):
    assert w(left=0, width_percent=0.5) == 2
    assert w(left=1, width_percent=0.5) == 2
    assert w(left=-1, width_percent=0.5) == 2

    assert w(center_x=1, width_percent=0.5) == 2
    assert w(center_x=-1, width_percent=0.5) == 2

    assert w(right=-0., width_percent=0.5) == 2
    assert w(right=1, width_percent=0.5) == 2
    assert w(right=-1, width_percent=0.5) == 2

    with pytest.raises(UsageError):
        w(left=-0., width_percent=0.5)
    with pytest.raises(UsageError):
        w(center_x=0, width_percent=0.5)
    with pytest.raises(UsageError):
        w(center_x=-0., width_percent=0.5)
    with pytest.raises(UsageError):
        w(right=0, width_percent=0.5)

def test_calc_min_board_size__width_percent__anchor_percent(w):
    assert w(left_percent=0.0, width_percent=0.5) == 2
    assert w(left_percent=0.5, width_percent=0.5) == 2
    
    assert w(center_x_percent=0.5, width_percent=0.5) == 2

    assert w(right_percent=0.5, width_percent=0.5) == 2
    assert w(right_percent=1.0, width_percent=0.5) == 2
    
    with pytest.raises(UsageError):
        w(left_percent=1.0, width_percent=0.5)
    with pytest.raises(UsageError):
        w(center_x_percent=0.0, width_percent=0.5)
    with pytest.raises(UsageError):
        w(center_x_percent=1.0, width_percent=0.5)
    with pytest.raises(UsageError):
        w(right_percent=0.0, width_percent=0.5)
    
# The "height" tests are identical to the "width" tests, with the following 
# substitutions:
#
#   width    => height
#   left     => bottom
#   center_x => center_y
#   right    => top
#   \<w\>    => h

def test_calc_min_board_size__height_absolute__anchor_absolute(h):
    assert h(bottom=0, height=1) == 1
    assert h(bottom=1, height=1) == 2
    assert h(bottom=-1, height=1) == 1

    assert h(center_y=1, height=1) == approx(1.5)
    assert h(center_y=-1, height=1) == approx(1.5)

    assert h(top=-0., height=1) == 1
    assert h(top=1, height=1) == 1
    assert h(top=-1, height=1) == 2

    with pytest.raises(UsageError):
        h(bottom=-0., height=1)
    with pytest.raises(UsageError):
        h(center_y=0, height=1)
    with pytest.raises(UsageError):
        h(center_y=-0., height=1)
    with pytest.raises(UsageError):
        h(top=0, height=1)

def test_calc_min_board_size__height_absolute__anchor_percent(h):
    assert h(bottom_percent=0.0, height=1) == 1
    assert h(bottom_percent=0.5, height=1) == 2
    
    assert h(center_y_percent=0.5, height=1) == 1

    assert h(top_percent=0.5, height=1) == 2
    assert h(top_percent=1.0, height=1) == 1
    
    with pytest.raises(UsageError):
        h(bottom_percent=1.0, height=1)
    with pytest.raises(UsageError):
        h(center_y_percent=0.0, height=1)
    with pytest.raises(UsageError):
        h(center_y_percent=1.0, height=1)
    with pytest.raises(UsageError):
        h(top_percent=0.0, height=1)
    
def test_calc_min_board_size__height_percent__anchor_absolute(h):
    assert h(bottom=0, height_percent=0.5) == 2
    assert h(bottom=1, height_percent=0.5) == 2
    assert h(bottom=-1, height_percent=0.5) == 2

    assert h(center_y=1, height_percent=0.5) == 2
    assert h(center_y=-1, height_percent=0.5) == 2

    assert h(top=-0., height_percent=0.5) == 2
    assert h(top=1, height_percent=0.5) == 2
    assert h(top=-1, height_percent=0.5) == 2

    with pytest.raises(UsageError):
        h(bottom=-0., height_percent=0.5)
    with pytest.raises(UsageError):
        h(center_y=0, height_percent=0.5)
    with pytest.raises(UsageError):
        h(center_y=-0., height_percent=0.5)
    with pytest.raises(UsageError):
        h(top=0, height_percent=0.5)

def test_calc_min_board_size__height_percent__anchor_percent(h):
    assert h(bottom_percent=0.0, height_percent=0.5) == 2
    assert h(bottom_percent=0.5, height_percent=0.5) == 2
    
    assert h(center_y_percent=0.5, height_percent=0.5) == 2

    assert h(top_percent=0.5, height_percent=0.5) == 2
    assert h(top_percent=1.0, height_percent=0.5) == 2
    
    with pytest.raises(UsageError):
        h(bottom_percent=1.0, height_percent=0.5)
    with pytest.raises(UsageError):
        h(center_y_percent=0.0, height_percent=0.5)
    with pytest.raises(UsageError):
        h(center_y_percent=1.0, height_percent=0.5)
    with pytest.raises(UsageError):
        h(top_percent=0.0, height_percent=0.5)
    

