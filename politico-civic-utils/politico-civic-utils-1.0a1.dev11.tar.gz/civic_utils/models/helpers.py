def extract_nested_key(key, cls, prefix=""):
    nested_key = cls.get_natural_key_fields()
    local_fields = {field.name: field for field in cls._meta.local_fields}
    values = []
    has_val = False
    if prefix:
        prefix += "__"
    for nname in nested_key:
        val = key.pop(prefix + nname, None)
        if val is None and nname in local_fields:
            if type(local_fields[nname]).__name__ == "DateTimeField":
                date = key.pop(nname + "_date", None)
                time = key.pop(nname + "_time", None)
                if date and time:
                    val = "%s %s" % (date, time)

        if val is not None:
            has_val = True
        values.append(val)
    if has_val:
        return values
    else:
        return None
