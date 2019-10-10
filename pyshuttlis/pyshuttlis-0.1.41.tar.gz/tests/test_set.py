from shuttlis.set import KeyedSet


class Foo(object):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "%s(%r)" % (type(self).__name__, self.name)


def getname(o):
    return o.name


def test_keyed_set_with_overlapping_values():
    objs = [Foo("Joe"), Foo("Jim"), Foo("Tom"), Foo("Jim")]

    s = KeyedSet(objs, key=getname)
    assert s == KeyedSet([Foo("Jim"), Foo("Joe"), Foo("Tom")], key=getname)


def test_adding_same_items_to_keyed_set():
    s1 = KeyedSet([Foo("Jim"), Foo("Joe"), Foo("Tom")], key=getname)
    n_set = KeyedSet([Foo("Jim"), Foo("Joe"), Foo("Tom")], key=getname)
    s1.add(Foo("Joe"))

    assert s1 == n_set


def test_membership_in_keyed_set():
    s1 = KeyedSet([Foo("Jim"), Foo("Joe"), Foo("Tom")], key=getname)

    assert Foo("Jim") in s1


def test_membershipt_with_key_returns_false():
    s1 = KeyedSet([Foo("Jim"), Foo("Joe"), Foo("Tom")], key=getname)

    assert "Jim" not in s1


def test_union_with_normal_set():
    s1 = KeyedSet([Foo("Jim"), Foo("Joe"), Foo("Tom")], key=getname)
    s2 = {Foo("Luc"), Foo("Jim"), Foo("Dan")}

    expected = KeyedSet([Foo("Dan"), Foo("Jim"), Foo("Luc"), Foo("Joe"), Foo("Tom")])

    assert expected == s1 | s2


def test_intersection_with_other_keyed_set():
    s1 = KeyedSet([Foo("Jim"), Foo("Joe"), Foo("Tom")], key=getname)
    s2 = {Foo("Luc"), Foo("Jim"), Foo("Dan")}

    assert KeyedSet([Foo("Jim")]) == s1 & s2


def test_asymtric_diff_with_keyed_set():
    s1 = KeyedSet([Foo("Jim"), Foo("Joe"), Foo("Tom")], key=getname)
    s2 = KeyedSet([Foo("Luc"), Foo("Jim"), Foo("Dan")], key=getname)

    assert KeyedSet([Foo("Joe"), Foo("Tom")]) == s1 - s2
    assert KeyedSet([Foo("Luc"), Foo("Dan")]) == s2 - s1
