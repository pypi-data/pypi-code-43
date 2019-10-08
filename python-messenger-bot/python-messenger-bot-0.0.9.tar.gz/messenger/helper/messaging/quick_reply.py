class QuickReply:

    def __init__(self, **kwargs):
        self.content_type = 'text'
        self.title = ''
        self.payload = ''
        self.image_url = ''

        self.mid = ''
        self.text = ''

        return super().__init__(**kwargs)

    def set_content_type(self, content_type):
        self.content_type = content_type

    def set_title(self, title):
        self.title = title

    def set_payload(self, payload):
        self.payload = payload

    def set_image_url(self, image_url):
        self.image_url = image_url

    
    def json_to_var(self, json):
        self.mid = json['mid']
        self.text = json['text']
        self.payload = json['quick_reply']['payload']