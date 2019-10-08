class Element:

    def __init__(self, **kwargs):
        self.title = ''
        self.image_url = ''
        self.subtitle = ''
        self.default_action = {}
        self.buttons = []
        
        return super().__init__(**kwargs)