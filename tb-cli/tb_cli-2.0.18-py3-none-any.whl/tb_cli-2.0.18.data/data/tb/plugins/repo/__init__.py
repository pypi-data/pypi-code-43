from .cmd_repo import RepoController


def load(app):
    app.handler.register(RepoController)
