from typing import Any, Callable, List, Type, cast, TypeVar, Dict, Union

T = TypeVar("T")


class InvalidTypeException(Exception):
    pass


class NotNoneException(InvalidTypeException):
    pass


class NotIntException(InvalidTypeException):
    pass


class NotFloatException(InvalidTypeException):
    pass


class NotStrException(InvalidTypeException):
    pass


class NotBoolException(InvalidTypeException):
    pass


class NotListException(InvalidTypeException):
    pass


class NotTypeException(InvalidTypeException):
    pass


class NotDictException(InvalidTypeException):
    pass


class NotNAException(InvalidTypeException):
    pass


class CouldNotParseResponseException(Exception):

    def __init__(self, exceptions: List[Exception], x: Any):
        self.exceptions = exceptions
        self.x = x
        super().__init__(self.exceptions_str)

    @property
    def exceptions_str(self) -> str:
        out_str = f'Could not parse {self.x} across multiple parsers. Got errors:\n'
        for exc in self.exceptions:
            out_str += f'{str(type(exc))}: {exc}\n'
        return out_str


def from_na(x: Any) -> None:
    if not isinstance(x, str) or x != 'N/A':
        raise NotNAException(x)
    return None


def from_int(x: Any) -> int:
    if isinstance(x, int) and not isinstance(x, bool):
        return x
    raise NotIntException(x)


def from_none(x: Any) -> Any:
    if x is not None:
        raise NotNoneException(x)
    return x


def from_union(fs, x):
    excs = []
    for f in fs:
        try:
            return f(x)
        except InvalidTypeException as e:
            excs.append(e)
    raise CouldNotParseResponseException(excs, x)


def from_float(x: Any) -> float:
    if isinstance(x, (float, int)) and not isinstance(x, bool):
        return float(x)
    raise NotFloatException(x)


def from_str(x: Any) -> str:
    if isinstance(x, str):
        return x
    raise NotStrException(x)


def to_float(x: Any) -> float:
    if isinstance(x, float):
        return x
    raise NotFloatException(x)


def from_bool(x: Any) -> bool:
    if isinstance(x, bool):
        return x
    raise NotBoolException(x)


def from_list(f: Callable[[Any], T], x: Any) -> List[T]:
    if isinstance(x, list):
        return [f(y) for y in x]
    raise NotListException(x)


def from_int_or_str(x: Any) -> Union[str, int]:
    try:
        return int(from_str(x))
    except ValueError:
        return from_str(x)


def from_str_number(x: Any) -> Union[int, float]:
    x = from_str(x)
    x = x.replace(',', '')  # strip thousands separators
    x = x.replace(' ', '').replace('\u200b', '')  # strip white spacve

    # Some numbers are coming with . as thousands separator, while others use it as decimal. Try to detect
    # where it is actually a thousands separator and remove it
    if x.count('.') > 1 or (x.count('.') == 1 and x.endswith('0')):
        x = x.replace('.', '')

    try:
        num = float(x)
    except ValueError:
        raise NotFloatException(x)

    # Got float, need to check if actually int
    if int(num) == num:
        return int(num)

    # Not int, return as float
    return num


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


def is_type(t: Type[T], x: Any) -> T:
    if not isinstance(x, t):
        raise NotTypeException(f'{x} is not type {t}')
    return x


def from_dict(f: Callable[[Any], T], x: Any) -> Dict[str, T]:
    if not isinstance(x, dict):
        raise NotDictException(x)
    return { k: f(v) for (k, v) in x.items() }


def from_plain_dict(x: dict) -> dict:
    if not isinstance(x, dict):
        raise NotDictException(x)
    return x
