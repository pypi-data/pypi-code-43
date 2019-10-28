def wrap_string_to_list(payload):
    if payload == None: return None
    if isinstance(payload, str): payload = [payload]
    return payload