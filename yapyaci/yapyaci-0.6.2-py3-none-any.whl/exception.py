class AuthFailure(Exception):
    pass

class InvalidToken(Exception):
    pass

class AuthRefreshFailure(Exception):
    pass

class SubRefreshFailure(Exception):
    pass

class InvalidJsonPayload(Exception):
    pass

class InvalidLookupRequest(Exception):
    pass

class CastingFailure(Exception):
    pass

class WsOpenFailure(Exception):
    pass