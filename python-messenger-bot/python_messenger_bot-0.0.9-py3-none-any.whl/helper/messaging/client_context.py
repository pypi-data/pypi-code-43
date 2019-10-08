class ClientContext:

    def __init__(self, **kwargs):
        self.thread_type = ''
        self.tid = ''
        self.psid = ''
        self.signed_request = ''
        
        return super().__init__(**kwargs)

    def json_to_var(self, json):
        self.thread_type = json['thread_type']
        self.tid = json['tid']
        self.psid = json['psid']
        self.signed_request = json['signed_request']