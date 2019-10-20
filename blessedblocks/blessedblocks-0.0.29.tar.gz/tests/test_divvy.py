import pytest
import sys
from blessedblocks.runner import Plot, Runner, Grid
from blessedblocks.blocks import BareBlock
from blessedblocks.block import SizePref, DEFAULT_SIZE_PREF

print_plots = True  # set to True for visual debug help when tests fail
dsp = DEFAULT_SIZE_PREF
block1 = BareBlock(name='1', text="1", w_sizepref=dsp, h_sizepref=dsp)
block2 = BareBlock(name='2', text="2", w_sizepref=dsp, h_sizepref=dsp)

def empty_handler(grid, cmd, args, kwargs):
    pass

def build_display(plot, size=10):
    out_array = [[' '] * size for i in range(size)]
    def build(plot, out_array):
        for key, val in plot.items():
            if type(val) == tuple:
                x, y, w, h = val
                for i in range(x, x+w):
                    for j in range(y, y+h):
                        out_array[j][i] = key
            else:
                build(val, out_array)
    build(plot, out_array)
    out = '\n'
    for line in out_array:
        out += ''.join(line) + '\n'
    return out

def calc_plot(plot, x, y, w, h, plot_id, out):
    if plot.block:
        out[plot.block.name] = (x, y, w, h)
    else:
        out[plot_id] = {}
        new_plot_id = chr(ord(plot_id)+1)
        for subplot, new_x, new_y, new_w, new_h in Runner.divvy(plot.subplots, x, y, w, h, plot.horizontal):
            calc_plot(subplot, new_x, new_y, new_w, new_h, new_plot_id, out[plot_id])
            plot_id = new_plot_id
            new_plot_id = chr(ord(plot_id)+1)
            out[plot_id] = {}
    print(out)
    return out

def plot_runner(xywh, layout, blocks, expected, length=10):
    x, y, w, h = xywh
    g = Grid(layout, blocks=blocks, handler=empty_handler)
    r = Runner(grid=g)
    p = r.build_plot(g._layout, g._slots)
    got = build_display(calc_plot(p, x, y, w, h, 'a', {}), size=length)
    if print_plots:
        print('\nexpected', end='')
        print(expected)
        print('got', end='')
        print(got)
    assert expected == got

def test_default_w_even():
    block1.w_sizepref, block1.h_sizepref = dsp, dsp
    block2.w_sizepref, block2.h_sizepref = dsp, dsp
    wh = 4
    xywh, layout = (0, 0, wh, wh), [1,2]
    blocks = {1: block1, 2: block2}
    expected = '''
1122
1122
1122
1122
'''
    plot_runner(xywh, layout, blocks, expected, length=wh)

def test_default_h_even():
    block1.w_sizepref, block1.h_sizepref = dsp, dsp
    block2.w_sizepref, block2.h_sizepref = dsp, dsp
    wh = 4
    xywh, layout = (0, 0, wh, wh), [(1,2)]
    blocks = {1: block1, 2: block2}
    expected = '''
1111
1111
2222
2222
'''
    plot_runner(xywh, layout, blocks, expected, length=wh)

def test_default_w_odd():
    block1.w_sizepref, block1.h_sizepref = dsp, dsp
    block2.w_sizepref, block2.h_sizepref = dsp, dsp
    wh = 5
    xywh, layout = (0, 0, wh, wh), [1,2]
    blocks = {1: block1, 2: block2}
    expected = '''
11122
11122
11122
11122
11122
'''
    plot_runner(xywh, layout, blocks, expected, length=wh)

def test_default_h_even():
    block1.w_sizepref, block1.h_sizepref = dsp, dsp
    block2.w_sizepref, block2.h_sizepref = dsp, dsp
    wh = 5
    xywh, layout = (0, 0, wh, wh), [(1,2)]
    blocks = {1: block1, 2: block2}
    expected = '''
11111
11111
11111
22222
22222
'''
    plot_runner(xywh, layout, blocks, expected, length=wh)

def test_default_unlimited_middle_width():
    block1.w_sizepref, block1.h_sizepref = SizePref(hard_min=1, hard_max=1), dsp
    block2.w_sizepref, block2.h_sizepref = SizePref(hard_min=1, hard_max=1), dsp
    block3 = BareBlock(name='3', text='3', w_sizepref=dsp, h_sizepref=dsp)
    wh = 5
    xywh, layout = (0, 0, wh, wh), [1,3,2]
    blocks = {1: block1, 2: block2, 3:block3}
    expected = '''
13332
13332
13332
13332
13332
'''
    plot_runner(xywh, layout, blocks, expected, length=wh)

def test_default_unlimited_middle_height():
    block1.w_sizepref, block1.h_sizepref = dsp, SizePref(hard_min=1, hard_max=1)
    block2.w_sizepref, block2.h_sizepref = dsp, SizePref(hard_min=1, hard_max=1)
    block3 = BareBlock(name='3', text='3', w_sizepref=dsp, h_sizepref=dsp)
    wh = 5
    xywh, layout = (0, 0, wh, wh), [(1,3,2)]
    blocks = {1: block1, 2: block2, 3:block3}
    expected = '''
11111
33333
33333
33333
22222
'''
    plot_runner(xywh, layout, blocks, expected, length=wh)

def test_default_single_fixed_width():
    block1.w_sizepref, block1.h_sizepref = dsp, dsp
    block2.w_sizepref, block2.h_sizepref = SizePref(hard_min=1, hard_max=1), dsp
    block3 = BareBlock(name='3', text='3', w_sizepref=dsp, h_sizepref=dsp)
    wh = 5
    xywh, layout = (0, 0, wh, wh), [1,3,2]
    blocks = {1: block1, 2: block2, 3:block3}
    expected = '''
11332
11332
11332
11332
11332
'''
    plot_runner(xywh, layout, blocks, expected, length=wh)

def test_default_single_fixed_height():
    block1.w_sizepref, block1.h_sizepref = dsp, dsp
    block2.w_sizepref, block2.h_sizepref = dsp, SizePref(hard_min=1, hard_max=1)
    block3 = BareBlock(name='3', text='3', w_sizepref=dsp, h_sizepref=dsp)
    wh = 5
    xywh, layout = (0, 0, wh, wh), [(1,3,2)]
    blocks = {1: block1, 2: block2, 3:block3}
    expected = '''
11111
11111
33333
33333
22222
'''
    plot_runner(xywh, layout, blocks, expected, length=wh)

def test_two_ways():
    block1.w_sizepref, block1.h_sizepref = dsp, dsp
    block2.w_sizepref, block2.h_sizepref = dsp, dsp
    block3 = BareBlock(name='3', text='3', w_sizepref=dsp, h_sizepref=dsp)
    wh = 5
    xywh, layout = (0, 0, wh, wh), [(1,3),2]
    blocks = {1: block1, 2: block2, 3:block3}
    expected = '''
11122
11122
11122
33322
33322
'''
    plot_runner(xywh, layout, blocks, expected, length=wh)

def test_broken_width():
    block1.w_sizepref, block1.h_sizepref = dsp, dsp
    block2.w_sizepref, block2.h_sizepref = dsp, dsp
    block3 = BareBlock(name='3', text='3', w_sizepref=dsp, h_sizepref=dsp)
    block4 = BareBlock(name='4', text='4', w_sizepref=dsp, h_sizepref=dsp)
    block5 = BareBlock(name='5', text='5', w_sizepref=dsp, h_sizepref=dsp)    
    wh = 10
    xywh, layout = (0, 0, wh, wh), [1,(2,3),(4,5)]
    blocks = {1: block1, 2: block2, 3: block3, 4: block4, 5: block5}
    expected = '''
1111222444
1111222444
1111222444
1111222444
1111222444
1111333555
1111333555
1111333555
1111333555
1111333555
'''
    plot_runner(xywh, layout, blocks, expected, length=wh)

def test_broken_fixed():
    wsp = SizePref(hard_min=1, hard_max=1)
    block1.w_sizepref, block1.h_sizepref = dsp, dsp
    block2.w_sizepref, block2.h_sizepref = wsp, dsp
    block3 = BareBlock(name='3', text='3', w_sizepref=wsp, h_sizepref=dsp)
    block4 = BareBlock(name='4', text='4', w_sizepref=wsp, h_sizepref=dsp)
    block5 = BareBlock(name='5', text='5', w_sizepref=wsp, h_sizepref=dsp)    
    wh = 10
    xywh, layout = (0, 0, wh, wh), [1,(2,3),(4,5)]
    blocks = {1: block1, 2: block2, 3: block3, 4: block4, 5: block5}
    expected = '''
1111111124
1111111124
1111111124
1111111124
1111111124
1111111135
1111111135
1111111135
1111111135
1111111135
'''
    plot_runner(xywh, layout, blocks, expected, length=wh)

def test_broken_hard_max():
    wsp = SizePref(hard_min=1, hard_max=float('inf'))
    block1.w_sizepref, block1.h_sizepref = dsp, dsp
    block2.w_sizepref, block2.h_sizepref = wsp, dsp
    block3 = BareBlock(name='3', text='3', w_sizepref=wsp, h_sizepref=dsp)
    block4 = BareBlock(name='4', text='4', w_sizepref=wsp, h_sizepref=dsp)
    block5 = BareBlock(name='5', text='5', w_sizepref=wsp, h_sizepref=dsp)
    wh = 10
    xywh, layout = (0, 0, wh, wh), [1,(2,3),(4,5)]
    blocks = {1: block1, 2: block2, 3: block3, 4: block4, 5: block5}
    expected = '''
1112222444
1112222444
1112222444
1112222444
1112222444
1113333555
1113333555
1113333555
1113333555
1113333555
'''
    plot_runner(xywh, layout, blocks, expected, length=wh)

def test_empty_space():
    wsp = SizePref(hard_min=1, hard_max=1)
    block1.w_sizepref, block1.h_sizepref = wsp, dsp
    block2.w_sizepref, block2.h_sizepref = wsp, dsp
    block3 = BareBlock(name='3', text='3', w_sizepref=wsp, h_sizepref=dsp)
    block4 = BareBlock(name='x', text='4', w_sizepref=dsp, h_sizepref=dsp)
    block5 = BareBlock(name='y', text='5', w_sizepref=dsp, h_sizepref=dsp)    
    wh = 10
    xywh, layout = (0, 0, wh, wh), [1,4,2,5,3]
    blocks = {1: block1, 2: block2, 3: block3, 4: block4, 5: block5}
    expected = '''
1xxxx2yyy3
1xxxx2yyy3
1xxxx2yyy3
1xxxx2yyy3
1xxxx2yyy3
1xxxx2yyy3
1xxxx2yyy3
1xxxx2yyy3
1xxxx2yyy3
1xxxx2yyy3
'''
    plot_runner(xywh, layout, blocks, expected, length=wh)
