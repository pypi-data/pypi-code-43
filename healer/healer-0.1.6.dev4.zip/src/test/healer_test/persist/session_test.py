
from healer.persist.session import *


def test_identity():
    print()
    identity = SessionIdentity()
    print(f"identity: '{identity}'")


def test_session():
    print()

    session = SessionSupport.produce_session()
    print(session)

    session.open()
    session.open()

    session.context_put('ctx1', 'value1')
    session.context_put('ctx2', 'value2')
    session.context_put('ctx3', 'value3')

    assert session.context_get('ctx0') == None
    assert session.context_get('ctx1') == 'value1'
    assert session.context_get('ctx2') == 'value2'
    assert session.context_get('ctx3') == 'value3'

    session.message_put('ses1', 'value4')
    session.message_put('ses2', 'value5')
    session.message_put('ses3', 'value6')

    assert session.message_get('ses0') == None
    assert session.message_get('ses1') == 'value4'
    assert session.message_get('ses2') == 'value5'
    assert session.message_get('ses3') == 'value6'

    print(session)
#     session.commit()

    session.close()
    session.close()

    print(session)

    with session:
        for key in  session.context_dict:
            print(f"context_dict: {key}={session.context_dict[key]}")
        for key in  session.message_dict:
            print(f"message_dict: {key}={session.message_dict[key]}")

    SessionSupport.move_to_cluster(session)
    SessionSupport.move_to_private(session)
    SessionSupport.destroy_session(session)


def test_session_visit():
    print()

    def visitor_function(session_path:str) -> None:
        if session_path.endswith(".db"):
            print(f"session_path: {session_path}")
            session_identity = SessionSupport.extract_identity(session_path)
            print(f"session_identity: {session_identity}")
            session_file = os.path.basename(session_path)
            assert session_file == session_identity.file_name

    session_list = [
        #
        SessionSupport.produce_session(SessionIdentity(DateTime(2010, 10, 11, 1, 2, 3))),
        SessionSupport.produce_session(SessionIdentity(DateTime(2010, 10, 12, 4, 5, 6))),
        SessionSupport.produce_session(SessionIdentity(DateTime(2010, 10, 1, 7, 8, 9))),
        #
        SessionSupport.produce_session(SessionIdentity(DateTime(2010, 11, 11, 1, 2, 3))),
        SessionSupport.produce_session(SessionIdentity(DateTime(2010, 12, 11, 4, 5, 6))),
        SessionSupport.produce_session(SessionIdentity(DateTime(2010, 1, 11, 7, 8, 9))),
        #
        SessionSupport.produce_session(SessionIdentity(DateTime(2010, 10, 11, 1, 2, 3))),
        SessionSupport.produce_session(SessionIdentity(DateTime(2011, 10, 11, 4, 5, 6))),
        SessionSupport.produce_session(SessionIdentity(DateTime(2012, 10, 11, 7, 8, 9))),
    ]

    for session in session_list:
        session.close()

    SessionSupport.session_visit(SessionType.tempdir, visitor_function),
