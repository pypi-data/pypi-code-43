from pgnosql.user import GlobalUser
from pgnosql.models import KV

class SPACE_ROLES:
    ADMIN_ROLES = ['Owner', 'Admin']

def get_spaces(user_id, roles = None):
    if not user_id: return []
    user = GlobalUser(user_id).get()
    if not user: return []
    all_spaces = user.get('spaces', [])

    if roles is not None:
        spaces = []
        for space in all_spaces:
            if space.get('role') in roles:
                spaces.append(space.get('service'))
        return spaces
    else:
        return [space.get('service') for space in all_spaces]

def get_channel(user_id):
    user = GlobalUser(user_id).get()
    if user is not None:
        return user.get('user', {}).get('channel', None)
    return None

def get_relationship(practitioner_id, client_id):
    key = 'relationship:{}/{}'.format(practitioner_id, client_id)
    return KV.objects.get(key=key).value