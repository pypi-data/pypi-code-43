class State:
    level = -1


class NotAuthenticated(State):
    level = 0


class WaitingAuthenticationData(State):

    def __init__(self, method):
        self.method = method

    level = 1


class Authenticated(State):
    level = 2


class Connected(State):
    level = 3
