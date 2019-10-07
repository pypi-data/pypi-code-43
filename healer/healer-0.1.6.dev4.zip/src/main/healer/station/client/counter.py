"""
"""

from .assist import *
from .tags import *


class CounterFun:

    @staticmethod
    def counter_data(*_):
        counter = dict(
            count=0,
            value='hello-kitty',
        )
        return counter

    @staticmethod
    def state_count(*_):
        return this['$store'].state.count


class CounterUnit:

    tag = produce_tag('button-counter')

    template = lambda : CONTAINER([
        BUTTON('{{title}}: {{count}}', **{'v-on:click':'count++'}),
        BUTTON('{{state_count}}'),
    ]).outerHTML

    arkon = lambda : window.Vue.component(name_of_tag(CounterUnit.tag), {
        'props': [ 'title' ],
        'data': CounterFun.counter_data,
        'computed' : {
            'state_count' : CounterFun.state_count,
        },
        'template': CounterUnit.template(),
    })
