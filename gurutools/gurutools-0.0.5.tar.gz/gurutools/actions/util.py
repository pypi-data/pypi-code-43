from enum import Enum

class STATUS(Enum):
    TODO = 'todo'
    ALPHA = 'alpha'
    BETA = 'beta'
    PROD = 'prod'

class ACTION_TYPE(Enum):
    BULK = 'bulk'
    INSTANCE = 'instance'

def get_instance_action_path(context, collection, id, action):
    return '/api/v3/{}/{}/{}/actions/{}/'.format(
        context,
        collection,
        id,
        action
    )