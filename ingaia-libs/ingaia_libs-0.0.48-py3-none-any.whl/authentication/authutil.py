import os
import requests
import base64


class AuthUtil:
    TOKEN_URL = 'https://ingaia-authentication-api.appspot.com/operations/auth/token'

    APP_ID = os.environ.get('AUTH_APP_ID')
    APP_SECRET = os.environ.get('AUTH_APP_SECRET')

    @staticmethod
    def get_token():
        # concat app id with secret
        app_id_plus_secret = f'{AuthUtil.APP_ID}:{AuthUtil.APP_SECRET}'
        b64_user_pass = base64.b64encode(app_id_plus_secret.encode('latin1'))
        b64_user_pass_str = b64_user_pass.decode('latin1')

        headers = {
            'Authorization': f'Basic {b64_user_pass_str}',
            'Content-Type': 'application/x-www-form-urlencoded',
        }

        data = {'grant_type': 'client_credentials'}

        return requests.post(AuthUtil.TOKEN_URL, data=data, headers=headers).json()

    @staticmethod
    def get_authenticated_header():
        return {'Authorization': 'Bearer {}'.format(AuthUtil.get_token())}


if __name__ == '__main__':
    print(AuthUtil.get_token())
