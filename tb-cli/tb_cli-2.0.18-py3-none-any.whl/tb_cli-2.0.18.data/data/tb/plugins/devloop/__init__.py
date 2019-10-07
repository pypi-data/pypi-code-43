from .cmd_devloop import DevloopController


def load(app):
    app.handler.register(DevloopController)
