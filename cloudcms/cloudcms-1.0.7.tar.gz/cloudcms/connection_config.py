class ConnectionConfig:
    
    required_keys = set(['baseURL', 'username', 'password', 'clientKey', 'clientSecret'])

    def __init__(self, config):
        if not (self.required_keys.issubset(set(config.keys()))):
            raise ValueError('Invalid Gitana Configuration')

        self.username = config['username']
        self.password = config['password']
        self.client_id = config['clientKey']
        self.client_secret = config['clientSecret']

        self.base_url = config['baseURL']
        self.token_url = config['baseURL'] + '/oauth/token'

    def extra(self):
        return {
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }