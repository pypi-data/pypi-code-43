import base64


def b64encode(obj):
    if isinstance(obj, str):
        obj = obj.encode("utf-8")
    base64code = base64.b64encode(obj).decode("utf-8")
    return base64code


def b64decode(code):
    if isinstance(code, str):
        code = code.encode("utf-8")
    content = base64.b64decode(code).decode("utf-8")
    return content
