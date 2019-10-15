class Credentials:
    # A class that accepts username and password. Automatically fetch
    #  cookie by itself so there's no need to check portal again and again
    
    def __init__(self, username, password):
        self._username = username
        self._password = password
    
    def fetch_refresh_cookie(self):
        pass

    def fetch_refresh_api_key(self):
        pass

    def get_cookie(self):
        if self._cookie == None:
            # fetch cookie
            self._cookie = fetch_refresh_cookie()
            # self._cookie = fetch_refresh_api_key()
        return get_cookie()
