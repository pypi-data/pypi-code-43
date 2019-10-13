from zuper_auth.interpret import Interpreter
from zuper_auth_tests.test_parsing1 import assert_eq


def test1():
    src = """
    TYPE domain
    TYPE organization
    TYPE user
    PROPERTY user domain-owner
    PARENT organization domain
    NEW domain global
    NEW organization aido
    SUB organization:aido domain:global

    NEW user tizio

    FOR user:tizio SET domain-owner IN domain:global
    """

    i = Interpreter()
    i.parse_and_interpret(src)

    assert_eq(i, {'domain-owner': True}, 'PROPERTIES user:tizio IN domain:global')
    assert_eq(i, {'domain-owner': True}, 'PROPERTIES user:tizio IN organization:aido')


def test2():
    src = """
    TYPE user
    TYPE user-group
    PARENT user user-group
    
    TYPE resource
    ABILITY resource read 
    NEW user tizio
    NEW user-group G
    SUB user:tizio user-group:G
    NEW resource r1
    
    
    ALLOW user-group:G TO * IN resource:r1
    
    """

    i = Interpreter()
    i.parse_and_interpret(src)

    assert_eq(i, True, 'IS user:tizio ALLOWED read IN resource:r1')



if __name__ == '__main__':
    test1()
