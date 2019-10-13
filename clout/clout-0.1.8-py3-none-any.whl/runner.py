import attr


def run(obj):

    for k, v in attr.asdict(obj, recurse=False).items():
        function = attr.fields_dict(type(obj))[k].default
        if v != function:
            break

    return function(v)
