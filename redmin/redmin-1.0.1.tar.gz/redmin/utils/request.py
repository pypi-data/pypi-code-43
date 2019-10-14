from django.http import JsonResponse
from python_utils import converters


def param(request, key, default=None):
    if isinstance(key, list):
        return [param(request, item, default) for item in key]
    value = request.GET.get(key)
    if value is None:
        value = request.POST.get(key)
    if value is None:
        value = default
    return value


def int_param(request, param_name, default=0):
    return converters.to_int(param(request, param_name), default)


def bool_param(request, param_name):
    value = param(request, param_name, "")
    return value.upper() in ["TRUE", "1", "OK"]


def json_response(data, safe=True):
    return JsonResponse(data, safe=safe)


def get_url_prefix(request):
    meta = request.META
    host_name = meta.get('HTTP_X_HOST')
    scheme = meta.get('HTTP_X_SCHEME') or meta.get('wsgi.url_scheme')
    port = meta.get('HTTP_X_PORT')
    if host_name and port and scheme:
        port = '' if (scheme == 'https' and port == '443') or (scheme == 'http' and port == '80') else f':{port}'
        http_host = f'{host_name}{port}'
    else:
        http_host = meta.get('HTTP_HOST')
    prefix = f'{scheme}://{http_host}'
    return prefix
