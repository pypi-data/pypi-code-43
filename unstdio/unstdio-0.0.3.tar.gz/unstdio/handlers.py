from unstdio.formats import direct
import io


class Inp(io.StringIO):
    def __init__(self, *args, frmt=direct, **kwargs):
        super().__init__(*args, **kwargs)
        self.frmt = frmt

    def read(self, *args, **kwargs):
        super().read(*self.frmt(*args, **kwargs))

    def write(self, *args, **kwargs):
        super().write(*args, **kwargs)


class Out(io.StringIO):
    def __init__(self, *args, frmt=direct, **kwargs):
        super().__init__(*args, **kwargs)
        self.frmt = frmt

    def read(self, *args, **kwargs):
        super().read(*args, **kwargs)

    def write(self, *args, **kwargs):
        super().write(*self.frmt(*args, **kwargs))


class Err(io.StringIO):
    def __init__(self, *args, frmt=direct, **kwargs):
        super().__init__(*args, **kwargs)
        self.frmt = frmt

    def read(self, *args, **kwargs):
        super().read(self, *args, **kwargs)

    def write(self, *args, **kwargs):
        super().write(*self.frmt(*args, **kwargs))
