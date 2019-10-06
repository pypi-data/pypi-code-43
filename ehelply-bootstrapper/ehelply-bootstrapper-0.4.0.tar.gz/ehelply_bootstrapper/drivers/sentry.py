from ehelply_bootstrapper.drivers.driver import Driver
from ehelply_bootstrapper.utils.state import State
import sentry_sdk


class Sentry(Driver):
    def setup(self):
        sentry_sdk.init(State.config.bootstrap.sentry.dsn)


