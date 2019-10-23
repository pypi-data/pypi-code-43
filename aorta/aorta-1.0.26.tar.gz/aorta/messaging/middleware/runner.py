import aorta


class MiddlewareRunner:
    """Runs messaging middleware on incoming message at
    various stages.
    """

    def pre_handle(self, context):
        pass

    def post_handle(self, context, results):
        pass

    def drop(self, context):
        pass

    def unknown(self, context):
        pass
