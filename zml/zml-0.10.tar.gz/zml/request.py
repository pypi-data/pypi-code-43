class Request:

    def __init__(self, path=None, get_params=dict(), post_params=dict()):
        self.path = path
        self.get_params = get_params
        self.post_params = post_params
