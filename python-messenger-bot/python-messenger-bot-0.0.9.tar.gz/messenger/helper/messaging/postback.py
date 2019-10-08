class Postback:

    def __init__(self, **kwargs):
        self.title = ''
        self.payload = ''
        
        return super().__init__(**kwargs)

    def json_to_message(self, json):
        self.title = json['title']
        self.payload = json['payload']