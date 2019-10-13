import requests
from social_core.backends.oauth import BaseOAuth2
from django_auth0_backend.jwt import decode
try:
    from nameparser import HumanName
except ImportError:
    pass

CLAIMS_PREFIX = 'https://{auth_domain}/claims/'
JWKS_URL = 'https://{auth0_domain}/.well-known/jwks.json'


class Auth0Backend(BaseOAuth2):
    name = 'auth0'
    SCOPE_SEPARATOR = ' '
    ACCESS_TOKEN_METHOD = 'POST'
    EXTRA_DATA = [
        ('picture', 'picture'),
        ('email_verified', 'email_verified'),
        ('claims', 'claims'),
    ]

    def authorization_url(self):
        return "https://{auth0_domain}/authorize".format(
            auth0_domain=self.setting('DOMAIN'),
        )

    def access_token_url(self):
        return "https://{auth0_domain}/oauth/token".format(
            auth0_domain=self.setting('DOMAIN'),
        )

    def get_user_id(self, details, response):
        return details['user_id']

    def _get_name(self, userinfo):
        if all(key in userinfo for key in ('given_name', 'family_name')):
            return userinfo['given_name'], userinfo['family_name']
        if 'name' in userinfo:
            try: 
                name = HumanName(userinfo['name'])
                return name.first, name.last
            except Exception:
                pass
        return userinfo['nickname'], ''


    def get_user_details(self, response):
        url = "https://{auth0_domain}/userinfo".format(
            auth0_domain=self.setting('DOMAIN'),
        )
        headers = {'Authorization': "Bearer {access_token}".format(
            access_token=response['access_token'],
        )}
        resp = requests.get(url, headers=headers)
        userinfo = resp.json()
        jwks_url = JWKS_URL.format(
            auth0_domain=self.setting('DOMAIN'),
        )
        userinfo = decode(
            response['id_token'],
            self.setting('KEY'),
            jwks_url,
        )
        claims = {
            k[len(CLAIMS_PREFIX):]: v
            for k, v in userinfo.items()
            if k.startswith(CLAIMS_PREFIX)
        }
        first_name, last_name = self._get_name(userinfo)
        return {
            'claims': claims,
            'username': userinfo['nickname'],
            'first_name': first_name,
            'last_name': last_name,
            'picture': userinfo['picture'],
            'user_id': userinfo['sub'],
            'email': userinfo['email'],
            'email_verified': userinfo.get('email_verified', None),

        }
