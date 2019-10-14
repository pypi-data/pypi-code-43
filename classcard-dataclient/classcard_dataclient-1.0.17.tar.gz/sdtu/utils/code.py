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


def create_unique(container, obj, salt=None):
    unique_obj = obj
    if obj in container:
        if salt and (obj + salt) not in container:
            unique_obj = obj + salt
        else:
            index = 0
            while True:
                if (obj + str(index)) not in container:
                    unique_obj = obj + str(index)
                    break
                index += 1
    return unique_obj
