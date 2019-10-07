"""
"""

from .assist import *
from .native import *
from .tags import *

# __pragma__ ('noalias')


class DualListFun:

    produce_list = lambda : []

    produce_view = lambda entry_list : LIST_GROUP(DRAGGABLE(
        LIST_ITEM('{{entry.name}}',
            v_for=f"entry in {entry_list}", v_bind_key="entry.id",
        ), group="dual-list" , v_on_change='react_change', v_bind_list=entry_list,
    ))

    @staticmethod
    def react_change(event):
        if 'added' in event:
            entry = event.added.element
            print(f'add {entry.id}')
        elif 'removed' in event:
            entry = event.removed.element
            print(f'rem {entry.id}')
        else:
            return


class DualListUnit:

    tag = produce_tag('dual-list-unit')

    list_one = lambda : DualListFun.produce_view('list_one')
    list_two = lambda : DualListFun.produce_view('list_two')

    template = lambda : DIV([
        ALERT('User list', show='', fade='', variant="info"),
        ALERT(ROW([
            COL(DualListUnit.list_one(),), COL(DualListUnit.list_two(),),
        ]), show='', fade='', variant="info"),
    ]).outerHTML

    arkon = lambda : window.Vue.component(name_of_tag(DualListUnit.tag), new_dict(
        data=lambda : new_dict(
            list_one=[new_dict(id='a-1', name='a-one'), new_dict(id='a-2', name='a-two')],
            list_two=[new_dict(id='b-1', name='b-one'), new_dict(id='b-2', name='b-two')],
        ),
        methods=new_dict(
            react_change=DualListFun.react_change,
        ),
        template=DualListUnit.template(),
    ))


DualListUnit.arkon()
