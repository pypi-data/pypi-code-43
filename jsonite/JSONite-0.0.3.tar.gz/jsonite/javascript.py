from inspect import isclass
import os

from jsonite.transformer import Transformer


class Javascript:

    data = {}
    script_string = "<script>\nlet {} = {}\n</script>"
    native_types = ('int', 'float', 'list', 'tuple', 'set')

    @staticmethod
    def put(*args, **kwargs):
        """Add the provided parameters to the Javascript object.

        Examples:
            Javascript.put({'foo': 'bar'})
            Javascript.put(person={'name': 'Jane Doe', 'age': 24})
            Javascript.put(user=user_object)
        """
        for arg in args:
            if isinstance(arg, list):
                raise TypeError('Pass lists as a keyword argument.')

            arg = Javascript.parse_arg(arg)
            Javascript.data.update(arg)

        for kw in kwargs:
            arg = Javascript.parse_arg(kwargs[kw], kw)
            Javascript.data.update(arg)

    @staticmethod
    def render():
        if not Javascript.data:
            return ''

        tran = Transformer()
        data = [tran.convert(k, v) for k, v in Javascript.data.items()]

        identifier = os.getenv('JS_NAMESPACE', 'jsonite')
        data_string = '\n    '.join(data)

        result = Javascript.script_string.format(
            identifier, '{\n    ' + data_string + '\n};'
        )

        Javascript.data = dict()
        return result

    @staticmethod
    def parse_arg(arg, keyword=None):
        name = arg.__class__.__name__
        try:
            data = arg
            if name not in Javascript.native_types:
                data = arg.__dict__

            return { name: data } if not keyword else { keyword.lower(): data }
        except Exception as e:
            pass

        return arg if keyword is None else {keyword.lower(): arg}

