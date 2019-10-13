from zuper_auth.interpret import Interpreter
from zuper_auth_tests.test_parsing1 import assert_true, assert_false


def test_user_after():
    src = """
TYPE user
TYPE server
ABILITY server admin
NEW server local
NEW user alice
TYPE group
    PARENT user group
NEW group admins
ALLOW group:admins TO admin IN server:local

SUB user:* group:admins

NEW user bob
SHOW_STATE
    """

    i = Interpreter()
    i.parse_and_interpret(src)

    print(i.info())

    assert_true(i, 'IS user:alice ALLOWED admin IN server:local')
    assert_true(i, 'IS user:bob ALLOWED admin IN server:local')

