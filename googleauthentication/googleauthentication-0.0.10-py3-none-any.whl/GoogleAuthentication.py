import json
import os
import webbrowser

from google.oauth2 import service_account, credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from dbstream import DBStream

from googleauthentication.core.encrypt import decrypt_secure, secure


def _write_cred(cred, file_path):
    f = open(file_path, "w")
    f.write(json.dumps(cred))
    f.close()


def _get_credentials(dbstream, user_credentials_email):
    query = """SELECT token FROM "ga"."_credentials" WHERE email='%s'""" % user_credentials_email
    try:
        r = dbstream.execute_query(query)
    except Exception as e:
        r = []
    if not r:
        return None
    return eval(decrypt_secure(r[0]["token"]))


def _save_credentials_in_db(_credentials, user_credentials_email, dbstream):
    credentials_dict = {
        'token': _credentials.token,
        'refresh_token': _credentials.refresh_token,
        'token_uri': _credentials.token_uri,
        'client_id': _credentials.client_id,
        'client_secret': _credentials.client_secret,
        'scopes': _credentials.scopes}
    token = secure(str(credentials_dict))
    try:
        query = """
    DELETE FROM "ga"."_credentials" WHERE email='%s';
    """
        dbstream.execute_query(query)
    except:
        pass
    data = {
        "table_name": """ "ga"."_credentials" """,
        "columns_name": ["token", "email"],
        "rows": [[token, user_credentials_email]]
    }
    dbstream.send_data(data, replace=False)


class GoogleAuthentication:
    def __init__(self, client_secret_file_path, user_credentials_email=None, dbstream: DBStream = None, scopes=None):
        self.client_secret_file_path = client_secret_file_path
        self.user_credentials_email = user_credentials_email
        self.dbstream = dbstream
        self.scopes = scopes

    def credentials(self):
        f = open(self.client_secret_file_path, "r")
        cred = json.load(f)
        f.close()
        cred["private_key"] = os.environ["GOOGLE_PRIVATE_KEY"]
        _write_cred(cred, self.client_secret_file_path)
        credentials = service_account.Credentials.from_service_account_file(self.client_secret_file_path)
        del cred["private_key"]
        _write_cred(cred, self.client_secret_file_path)
        return credentials

    def user_credentials(self):
        if not self.dbstream:
            print("No DBStream set")
            exit()
        if not os.environ.get("GOOGLE_ENCRYPT_CREDENTIALS_KEY"):
            print("No GOOGLE_ENCRYPT_CREDENTIALS_KEY set")
            exit()
        google_credentials = _get_credentials(self.dbstream, self.user_credentials_email)
        if google_credentials:
            return credentials.Credentials(**google_credentials)
        flow = Flow.from_client_secrets_file(
            self.client_secret_file_path,
            scopes=self.scopes,
            redirect_uri='urn:ietf:wg:oauth:2.0:oob')
        auth_uri = flow.authorization_url()
        webbrowser.open_new(auth_uri[0])
        code = input('Enter the authorization code: ')
        flow.fetch_token(code=code)
        _credentials = flow.credentials
        _save_credentials_in_db(_credentials, self.user_credentials_email, self.dbstream)
        return _credentials

    def get_account(self, api, version="v4"):
        if self.user_credentials_email:
            credentials = self.user_credentials()
        else:
            credentials = self.credentials()
        account = build(api, version, credentials=credentials)
        return account
