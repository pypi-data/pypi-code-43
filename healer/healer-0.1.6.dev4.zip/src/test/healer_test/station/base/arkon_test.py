"""
"""

from healer.station.base.arkon import DataBean


def test_data_bean():
    print()

    source = DataBean()
    print(source)

    binary = source.into_wire()
    print(binary)

    target = DataBean.from_wire(binary)
    print(target)

    assert source == target, f"{source} vs {target}"
