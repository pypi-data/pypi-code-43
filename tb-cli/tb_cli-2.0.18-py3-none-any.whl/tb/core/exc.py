
class TbError(Exception):
    """Generic errors."""

    def __init__(self, *args: object, exit_code=1) -> None:
        super().__init__(*args)
        self.exit_code = exit_code

