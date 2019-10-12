from .candidate import ErConnector, Candidate

def validate(username, password):
    # using REST API. If valid, returns Candidate object. If not, returns False
    connector = ErConnector(api_version='rest')
    path = 'User/Validate?UserName={UserName}&Password={Password}&EntityID={EntityID}'.format(
        UserName=username,
        Password=password,
        EntityID=connector.rest_entity_id
    )
    params = {}
    params['UserName'] = username
    params['Password'] = password
    params['EntityID'] = connector.rest_entity_id
    try:
        result = Candidate(connector.send_request(
            path,
            payload=params,
            verb='POST',
        )['Data']['ReferenceID'])
    except:
        result = False

    return result

def lookup(email):
    # using REST API.
    connector = ErConnector(api_version='rest')
    path = 'User/{entityid}/{email}'.format(
        email=email,
        entityid=connector.rest_entity_id
    )
    result = connector.send_request(
        path,
        verb='GET',
    )
    try:
        return Candidate(result['Data']['Candidate']['CandidateID'])
    except:
        return False