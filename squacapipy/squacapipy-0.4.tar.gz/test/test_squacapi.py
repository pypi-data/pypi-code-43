from squacapipy.squacapi import Response, Network, Channel
from unittest.mock import patch
'''to run

    $:pytest --verbose -s test/test_squacapi.py && flake8
    or
    pytest && flake8
'''

'''Tests are really just testing class instantiaion since the response
    object is mocked.
'''
@patch.object(Network, 'get')
def test_get_networks(mock_get):
    res = Response(200, [{'code': 'uw'}, {'code': 'cc'}])
    mock_get.return_value = res
    '''should get all networks '''
    net = Network()
    response = net.get()
    assert response.status_code == 200
    assert len(response.body) > 1


@patch.object(Network, 'post')
def test_create_network(mock_post):
    res = Response(201, [{'code': 'uw'}])
    mock_post.return_value = res
    net = Network()
    payload = {
        'code': 'f2',
        'name': 'FU'
    }
    response = net.post(payload)
    assert response.status_code == 201


@patch.object(Network, 'put')
def test_update_network(mock_put):
    res = Response(200, [{'code': 'f1', 'name': 'FR',
                          'description': 'This is the description'}])
    mock_put.return_value = res
    net = Network()
    payload = {
        'code': 'f2',
        'name': 'FR',
        'description': "This is the description"
    }
    response = net.put('f2', payload)
    assert response.status_code == 200


@patch.object(Channel, 'get')
def test_get_channels(mock_get):
    res = Response(200, [
        {'code': 'EHZ', 'name': "EHZ", 'station_code': 'RCM',
         'station_name': 'Muir', "sample_rate": 200, 'loc': '--',
         'lat': 45.0, 'lon': -122.0, 'elev': 2000, 'network_id': 1},
        {'code': 'EHE', 'name': "EHE", 'station_code': 'RCM',
         'station_name': 'Muir', "sample_rate": 200, 'loc': '--',
         'lat': 45.0, 'lon': -122.0, 'elev': 2000, 'network_id': 1}])
    mock_get.return_value = res
    '''should get all networks '''
    channel = Channel()
    response = channel.get()
    assert response.status_code == 200
    assert len(response.body) > 1
