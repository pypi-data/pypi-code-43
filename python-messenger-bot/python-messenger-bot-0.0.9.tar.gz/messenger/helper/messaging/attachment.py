class Attachment:

    def __init__(self, **kwargs):
        self.mid = self.sticker_id = ''
        self.attachments = []
        return super().__init__(**kwargs)

    def json_to_var(self, json):
        self.mid = json['mid']
        self.attachments = json['attachments']