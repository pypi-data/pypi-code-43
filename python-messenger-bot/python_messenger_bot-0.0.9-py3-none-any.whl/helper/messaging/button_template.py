class ButtonTemplate:

    def __init__(self, **kwargs):
        self.attachment_type = 'template'
        self.payload_template_type = 'button'
        self.payload_text = ''
        self.payload_buttons = []
        
        return super().__init__(**kwargs)