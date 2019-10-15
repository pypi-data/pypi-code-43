from pathlib import Path

from p10s.values import value


class BaseContext:
    def __init__(self, input=None, output=None):
        if input is None:
            self.input = value("p10s", {}).get("file", None)
        else:
            self.input = Path(input)

        if output is not None:
            self.output = Path(output)
        elif self.input is not None:
            if hasattr(self, "output_file_extension"):
                self.output = self.input.with_suffix(self.output_file_extension)
            else:
                raise Exception(
                    "Required property output_file_extension missing on %s." % self
                )
        else:
            self.output = None

    def render(self):
        with self._output_stream() as stream:
            self.render_to_stream(stream)

    def render_to_stream(self, stream):
        raise NotImplementedError()  # pragma: no cover

    def _output_stream(self):
        self.output.parent.mkdir(parents=True, exist_ok=True)
        return self.output.open("w")

    def __repr__(self):
        return "<" + self.__module__ + "." + self.__class__.__name__ + ">"
