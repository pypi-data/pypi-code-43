import itkdb
import betamax


def test_list_test_types(auth_session):
    with betamax.Betamax(auth_session).use_cassette('test_tests.test_list_test_types'):
        response = auth_session.get(
            'listTestTypes', json={'project': 'S', 'componentType': 'HYBRID'}
        )
        assert response.status_code == 200
        response = response.json()
        assert response
        assert 'pageItemList' in response
        assert 'componentType' in response
        assert 'pageInfo' in response
        assert 'uuAppErrorMap' in response
