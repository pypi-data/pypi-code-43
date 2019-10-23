import click


class Context(object):
    def __init__(self, store):
        self.store = store


ctx = click.make_pass_decorator(Context)
