import datetime


def attr(obj, attribute, default=None):
    name = str(attribute).strip()
    result = None
    if obj is not None:
        if "." not in name:
            try:
                if isinstance(obj, dict):
                    result = obj.get(name, default)
                elif isinstance(obj, (list, tuple)):
                    result = obj[int(name)]
                elif hasattr(obj, name):
                    result = getattr(obj, name)
            except Exception:
                result = None
        else:
            parts = name.split(".", 1)
            result = attr(attr(obj, parts[0]), parts[1])

    if result is None:
        result = default
    return result


def display(obj, attribute):
    from redmin.models import Field, Choice
    if obj:
        result = attr(obj, attribute, default="")
        field = Field.get_default_field(obj.__class__, attribute)
        if field:
            for choice in Choice.get_choices(field) or []:
                if choice.value == f"{result}":
                    return choice.title

        if isinstance(result, bool):
            result = "是" if result else '否'
        elif isinstance(result, datetime.datetime):
            result = result.strftime("%Y-%m-%d %H:%M:%S")
        return result
    return ""
