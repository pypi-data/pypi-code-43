import re
import typing
import inspect


__all__ = ['check_param']


def get_types(type_: typing.Any) -> typing.Tuple[typing.Optional[type]]:
    types_list: typing.Dict[str, type] = {
        'int': int,
        'str': str,
        'bool': bool,
        'NoneType': type(None)
    }

    def non_in_types_list(i: str) -> type:
        if 'typing.List' in i:
            return list
        return eval(i.split('.')[1])

    stype = str(type_)
    if type_ in (str, int, bool, type(None)):
        return type_
    # check is custom class
    if '<class' in stype:
        return type_
    if 'typing.Union' in stype:
        in_types = re.search(r'typing\.Union\[(.*)\]', stype)[1].split(', ')
        return tuple([types_list.get(i) or non_in_types_list(i) for i in in_types])

    raise Exception('all bad')


class NotInParam:
    pass


def check_param():
    def wrapper(func):
        def func_wrapper(*args, **kwargs):
            args_spec = inspect.getfullargspec(func)
            result = func(*args, **kwargs)

            in_params = {
                **{key: value for key, value in zip(args_spec.args, args)},
                **kwargs
            }
            # check result type
            for key, value in args_spec.annotations.items():
                if key == 'return':
                    continue

                corrected_types = get_types(value)
                in_param = in_params.get(key, NotInParam)
                if corrected_types and in_param is not NotInParam:
                    if not isinstance(in_params.get(key), corrected_types):
                        raise Exception('In param {} is not {}'.format(in_params.get(key), corrected_types))

            return result
        return func_wrapper
    return wrapper


if __name__ == '__main__':
    import decimal

    class MyClass:
        pass

    @check_param()
    def test(
            a: typing.Union[int, str, None, MyClass],
            b: MyClass,
            c: typing.Optional[typing.List[int]],
            d: decimal.Decimal = 4,
            e: typing.Optional[int] = None
    ) -> typing.Union[int, str, None]:
        return a


    print(test(4, MyClass(), None, e=54))
    try:
        test(1, None, None, None, None)
    except:
        import traceback
        print(traceback.format_exc())
