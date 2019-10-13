from nose.tools import assert_equal

from zuper_auth.interpret import Interpreter


def test1():
    src = """
TYPE domain
TYPE organization
TYPE user
PROPERTY user organization-owner

PARENT organization domain
ABILITY organization create-repos

NEW domain global
NEW organization aido
SUB organization:aido domain:global

NEW user yes-because-owner-aido
NEW user yes-because-owner-global
NEW user yes-because-direct
NEW user no

FOR user:yes-because-owner-aido SET organization-owner IN organization:aido
FOR user:yes-because-owner-global SET organization-owner IN domain:global

ALLOW user:* TO create-repos IN organization:* IF organization-owner
ALLOW user:yes-because-direct TO create-repos IN organization:aido

 
    """

    i = Interpreter()
    i.parse_and_interpret(src)

    assert_true(i, 'HAS user:yes-because-owner-aido PROPERTY organization-owner IN organization:aido')
    assert_true(i, 'IS user:yes-because-owner-aido ALLOWED create-repos IN organization:aido')

    assert_true(i, 'HAS user:yes-because-owner-global PROPERTY organization-owner IN domain:global')
    assert_true(i, 'HAS user:yes-because-owner-global PROPERTY organization-owner IN organization:aido')
    assert_true(i, 'IS user:yes-because-owner-global ALLOWED create-repos IN organization:aido')

    assert_false(i, 'HAS user:yes-because-direct PROPERTY organization-owner IN organization:aido')
    assert_true(i, 'IS user:yes-because-direct ALLOWED create-repos IN organization:aido')

    assert_false(i, 'IS user:no ALLOWED create-repos IN organization:aido')


def test2_attrs():
    src = """
TYPE challenge
PROPERTY challenge private
PROPERTY challenge public
TYPE user
ABILITY challenge read

NEW challenge pri1
FOR challenge:pri1 SET private
NEW challenge pub1
FOR challenge:pub1 SET public

NEW user john
 
ALLOW user:* TO read IN challenge:* [ public ]


    """

    i = Interpreter()
    i.parse_and_interpret(src)

    assert_true(i, 'IS user:john ALLOWED read IN challenge:pub1')
    assert_false(i, 'IS user:john ALLOWED read IN challenge:pri1')


def test_rem():
    src = """
REM comment

REM comment two 

    """

    i = Interpreter()
    i.parse_and_interpret(src)


def assert_eq(i: Interpreter, val, s):
    ress = i.parse_and_interpret(s)
    res = ress[0]
    print(res.msg)
    if not res.ok:
        raise Exception(res)

    assert_equal(res.query_result, val, s)


def assert_true(i, s):
    assert_eq(i, True, s)


def assert_false(i, s):
    assert_eq(i, False, s)


if __name__ == '__main__':
    test1()
