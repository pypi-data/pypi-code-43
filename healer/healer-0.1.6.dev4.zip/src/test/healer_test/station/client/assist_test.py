
from healer.station.client.assist import *


def test_mapper():
    print()

    entry_list = [
        ('v_if', 'v-if'),
        ('v_show', 'v-show'),
        ('v_on_click', 'v-on:click'),
        ('v_bind_invalid_feedback', 'v-bind:invalid-feedback'),
    ]

    for entry in entry_list:
        source = entry[0]
        target = entry[1]
        print(f"{source} -> {target}")
        assert target == Assist.translate_attribute(source)
