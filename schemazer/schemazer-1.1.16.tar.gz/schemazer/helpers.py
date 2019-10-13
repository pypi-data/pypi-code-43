def remote_addr(request):
    addr = request.environ.get('HTTP_X_FORWARDED_FOR',
                               request.remote_addr).split(',')
    return addr[0] or request.environ.get('HTTP_X_REAL_IP', None)
