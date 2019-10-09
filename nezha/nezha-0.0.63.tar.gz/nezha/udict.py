import json
import typing as ty

from nezha.container import is_iterable
from nezha.func import loop


def is_immutable(self: ty.Any) -> None:
    raise TypeError("%r objects are immutable" % self.__class__.__name__)


class Dict(dict):

    def sort_keys(self, sort_by_ascii: bool = True) -> str:
        """
        sort dict value by dict key's order in ascii.
        :param data_dict:
        :return:
        """
        if sort_by_ascii:
            sign_data = ''
            for key in sorted(self.keys()):
                value = self[key]
                if isinstance(value, (dict, list)):
                    sign_data += json.dumps(self[key], ensure_ascii=False, sort_keys=True)
                else:
                    sign_data += str(value)
            return sign_data
        else:
            raise NotImplementedError(f'sort_by_ascii {sort_by_ascii}')

    @staticmethod
    def filter(data: ty.Dict[str, ty.Any],
               exclude: ty.Tuple[str, ...] = ('self', 'cls'),
               forbid_empty_val: bool = True) -> ty.Dict[str, ty.Any]:
        """

        :param data:
        :param exclude:
        :param forbid_empty_val:
        :return:
        """
        copied = data.copy()
        loop(map(lambda x: x in exclude and copied.pop(x), data))
        empty_val = ('', 0, None)
        _copied = copied.copy()
        forbid_empty_val and loop(map(lambda x: x[1] in empty_val and copied.pop(x[0], None), _copied.items()))
        return copied

    def remove(self, data: ty.Union[ty.Iterable, str]) -> 'Dict':
        """
        remove data and return instance
        :param data:
        :return:
        """
        data = data if is_iterable(data) else (data,)
        for k in data:
            self.pop(k, None)
        return self


class ImmutableDict(dict):
    """
    immutable dict。It referred to from werkzeug.datastructures import ImmutableMultiDict
    """

    def setdefault(self, key: ty.Any, default: ty.Optional[ty.Any] = None) -> None:
        is_immutable(self)

    def update(self, *args: ty.Any, **kwargs: ty.Any) -> None:
        is_immutable(self)

    def pop(self, key: ty.Any, default: ty.Any = None) -> None:
        is_immutable(self)

    def popitem(self):  # type: ignore
        is_immutable(self)

    def __setitem__(self, key: ty.Any, value: ty.Any) -> None:
        is_immutable(self)

    def __delitem__(self, key: ty.Any) -> None:
        is_immutable(self)

    def clear(self) -> None:
        is_immutable(self)


if __name__ == '__main__':
    im = ImmutableDict(a=1, b=2, c=3)
    print(im['a'])
