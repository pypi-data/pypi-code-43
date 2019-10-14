import dataclasses


@dataclasses.dataclass(frozen=True)
class FormatConfig:
    format_py_code: bool = True
    inplace: bool = False
