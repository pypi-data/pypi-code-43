import base64


UTF8 = 'utf-8'


def bytes_to_b64(val):
    return base64.b64encode(val).decode(UTF8)


def b64_to_bytes(val):
    return base64.b64decode(val)


def str_to_b64(val):
    return base64.b64encode(val.encode(UTF8)).decode(UTF8)


def b64_to_str(val):
    return base64.b64decode(val).decode(UTF8)
