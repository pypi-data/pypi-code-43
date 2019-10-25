from django.urls import reverse

def get_instance_action_url(resource, pk, action_id, context=None):
    url = "/{}/{}/actions/{}/".format(resource, pk, action_id)
    if context is not None:
        return "/{}{}".format(context, url)
    return url

def get_bulk_action_url(resource, action_id, context=None):
    url = "/{}/actions/{}/".format(resource, action_id)
    if context is not None:
        return "/{}{}".format(context, url)
    return url

def assert_in_registry(client, resource, bulk_actions=[], instance_actions=[]):
    '''
    validate the the required actions are available in the registry
    '''
    url = '/{}/actions/list/'.format(resource)
    res = client.get(url)
    data = res.json()
    bulk = [action.get('id') for action in data.get('bulk_actions')]
    instance = [action.get('id') for action in data.get('instance_actions')]
    for bulk_action in bulk_actions:
        assert bulk_action in bulk, \
            'Expected to find {} registered in: {}'.format(bulk_action, bulk)

    for instance_action in instance_actions:
        assert instance_action in instance, \
            'Expected to find {} registered in: {}'.format(instance_action, instance)
