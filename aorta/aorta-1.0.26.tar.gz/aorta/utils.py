import proton


def get_peer_address(container, obj):
    """Return the peer address of the given object."""
    if isinstance(obj, proton.Link):
        obj = obj.connection
    return container.get_connection_address(obj)
