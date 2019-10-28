import inspect


def get_inject_params(func, data):
    params = {}
    parameters = inspect.signature(func).parameters
    for name, parameter in parameters.items():
        if parameter.default is parameter.empty: # no default value, this parameter is required
            value = data[name]
        else:
            value = data.get(name, parameter.default)
        if not parameter.annotation is parameter.empty:
            value = parameter.annotation(value)
        params[name] = value
    return params


def call_with_inject(func, data):
    params = get_inject_params(func, data)
    return func(**params)
