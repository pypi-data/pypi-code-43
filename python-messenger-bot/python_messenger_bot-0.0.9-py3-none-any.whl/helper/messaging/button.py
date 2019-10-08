class Button:

    def __init__(self, **kwargs):
        self.type = ''
        self.url = ''
        self.title = ''
        self.payload = ''
        self.webview_height_ratio = ''
        self.messenger_extensions = True
        
        return super().__init__(**kwargs)