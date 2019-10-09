'''error classes '''


class APITokenMissingError(Exception):
    '''raise error on missing key'''
    pass


class APIBaseUrlError(Exception):
    '''raise error on base url param'''
    pass
