

def deep_merge(target, data):
    for key2, value2 in data.items():
        value1 = target.get(key2, None)
        if isinstance(value1, dict) and isinstance(value2, dict):
            deep_merge(value1, value2)
        else:
            target[key2] = value2


def select(data, path, default_value=None):
    paths = path.split(".")
    for path in paths:
        if isinstance(data, dict) and path in data:
            data = data[path]
        elif isinstance(data, (list, tuple)) and path.isdigit() and int(path) < len(data):
            data = data[int(path)]
        else:
            return default_value
    return data


def update(data, path, value):
    paths = path.split(".")
    for index in range(0, len(paths) - 1):
        path = paths[index]
        path_next = paths[index + 1]

        if isinstance(data, dict) and path in data:
            data = data[path]
        elif isinstance(data, list) and int(path) < len(data):
            data = data[int(path)]
        else:
            if isinstance(data, list) and int(path) >= len(data):
                for _ in range(int(path) + 1 - len(data)):
                    data.append(None)
            if path_next.isdigit():
                next_value = []
            else:
                next_value = {}
            if path.isdigit():
                data[int(path)] = next_value
                data = data[int(path)]
            else:
                data[path] = next_value
                data = data[path]
    path = paths[-1]
    if path.isdigit():
        for _ in range(int(path) + 1 - len(data)):
            data.append(None)
        data[int(path)] = value
    else:
        data[path] = value
