class QlikAuth():
    """

    Classe base para criação dos Headers exigidos pela API do QLIK

    """

    def __init__(self,
                 hostname='localhost',
                 sslfile=None,
                 sslfile_key=None,
                 verify=True
                 ):

        self.xrfkey = '0123456789abcdef'
        self.hostname = hostname
        self.uri = f'https://{hostname}:4242/qrs/'
        self.verify = verify
        self.headers = {}
        self.headers['x-qlik-xrfkey']= self.xrfkey
        self.headers['X-Qlik-User'] = 'UserDirectory=internal;UserId=sa_repository'
        self.headers['Content-Type']= 'application/json'
        self.headers['Cache-Control']= 'no-cache'
        self.headers['Accept']='*/*'
        self.sslfile = sslfile
        self.sslfile_key = sslfile_key