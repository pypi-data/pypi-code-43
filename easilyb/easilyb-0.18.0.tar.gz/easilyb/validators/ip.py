def _get_ip_object(ip):
    from ipaddress import ip_address
    try:
        ip_object = ip_address(ip)
        return ip_object
    except:
        return None

def validate_ip(ip):
    if _get_ip_object(ip) is None:
        return False
    return True


def validate_ipv4(ip):
    obj = _get_ip_object(ip)
    if obj is None or obj.version != 4:
        return False
    return True


def validate_ipv6(ip):
    obj = _get_ip_object(ip)
    if obj is None or obj.version != 6:
        return False
    return True