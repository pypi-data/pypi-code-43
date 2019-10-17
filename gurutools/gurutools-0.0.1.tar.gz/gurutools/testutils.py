from pgnosql.user import GlobalUser

def put_global_user(user_id, spaces):
    """
    spaces = [
        (space_id, role)
    ]
    usage: put_global_user(1, )
    """
    space_data = [{'service': space_id, 'role': role} for space_id, role in spaces]

    data = {
        "user": {"id": user_id},
        "spaces": space_data
    }
    user = GlobalUser(user_id)
    user.set(data)
    return user
