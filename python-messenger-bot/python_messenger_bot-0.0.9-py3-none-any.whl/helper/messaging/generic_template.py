class GenericTemplate:

    def __init__(self, **kwargs):
        self.attachment_type = 'template'
        
        self.payload_template_type = 'generic'
        self.payload_elements = []
                
        return super().__init__(**kwargs)