from jiratag_commitizen import out
from jiratag_commitizen.cz import registry


class ListCz:
    """List currently installed rules."""

    def __init__(self, config: dict, *args):
        self.config: dict = config

    def __call__(self):
        out.write("\n".join(registry.keys()))
