class MessageTemplate:

    def __init__(self, **kwargs):
        self.text=''
        
        return super().__init__(**kwargs)

    def json_to_message(self, json):
        self.text = json['text']