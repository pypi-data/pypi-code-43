from collections import OrderedDict as OD

from asciitree import LeftAligned
from asciitree.drawing import BoxStyle, BOX_DOUBLE

tr = LeftAligned()

# a basic tree
# OrderedDict is used in some places where node order is important, otherwise
# a normal dict is used for the sake of readabilitiy
tree = {
    'asciitree': OD([
        ('sometimes',
            {'you': {}}),
        ('just',
            {'want': OD([
                ('to', {}),
                ('draw', {}),
            ])}),
        ('trees', {}),
        ('in', {
            'your': {
                'terminal': {}
            }
        })
    ])
}

# construct a more complex tree by copying the tree and grafting it onto itself
# use a box style
box_tr = LeftAligned(draw=BoxStyle(gfx=BOX_DOUBLE, horiz_len=1, indent=1))
print(box_tr(tree))
