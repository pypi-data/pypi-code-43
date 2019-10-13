import requests
from jose.jwt import decode as jose_decode

def _get_jwks(jwks_url):
    resp = requests.get(jwks_url)
    return resp.json()


def decode(
    token,
    audience,
    jwks_url,
    **kwargs
):
    algorithms = ['RS256']
    key = _get_jwks(jwks_url)

    return jose_decode(
        token,
        key,
        algorithms=algorithms,
        audience=audience,
        **kwargs
    )
