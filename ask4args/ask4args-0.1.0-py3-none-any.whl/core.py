import inspect
from inspect import _empty, Parameter
from typing import Any, Dict, List, _alias, _GenericAlias, _SpecialForm

from PyInquirer import (Token, ValidationError, Validator, prompt,
                        style_from_dict)

custom_style_1 = style_from_dict({
    Token.Separator: '#cc5454',
    Token.QuestionMark: '#673ab7 bold',
    Token.Selected: '#cc5454',  # default
    Token.Pointer: '#673ab7 bold',
    Token.Instruction: '',  # default
    Token.Answer: '#f44336 bold',
    Token.Question: '',
})

custom_style_2 = style_from_dict({
    Token.Separator: '#6C6C6C',
    Token.QuestionMark: '#FF9D00 bold',
    # Token.Selected: '',  # default
    Token.Selected: '#5F819D',
    Token.Pointer: '#FF9D00 bold',
    Token.Instruction: '',  # default
    Token.Answer: '#5F819D bold',
    Token.Question: '',
})

custom_style_3 = style_from_dict({
    Token.QuestionMark: '#E91E63 bold',
    Token.Selected: '#673AB7 bold',
    Token.Instruction: '',  # default
    Token.Answer: '#2196f3 bold',
    Token.Question: '',
})
Validators: Dict[str, Validator] = {}


def check_type(obj, _type):
    # only process 2 level inner
    origin_type = getattr(_type, '__origin__', _type)
    if not isinstance(obj, origin_type):
        return False
    key_type, value_type, *_ = getattr(_type, '__args__',
                                       (object,)) + (object, object)
    if origin_type is dict:
        for k, v in obj.items():
            if not (isinstance(k, key_type) and isinstance(v, value_type)):
                return False
    elif origin_type is list:
        for v in obj:
            if not isinstance(v, value_type):
                return False
    return True


def gen_validate(value_type):
    name = value_type.__name__
    if name in Validators:
        return Validators[name]

    def validate(self, document):
        try:
            value_type(document.text)
        except ValueError:
            raise ValidationError(message=f'Please enter a {name}',
                                  cursor_position=len(document.text))

    cls = type(name, (Validator,), {'validate': validate})
    Validators[name] = cls
    return cls


class Ask4Args(object):
    sep_sig = f'{"=" * 40}\n'
    valid_types = {list, int, bool, str, tuple, set, float, dict}
    NOT_SUPPORT_KIND = {Parameter.POSITIONAL_ONLY, Parameter.VAR_POSITIONAL}

    def __init__(self,
                 function,
                 choices: Dict[str, list] = None,
                 checkboxes: Dict[str, list] = None,
                 defaults: Dict[str, Any] = None,
                 custom_style: Dict = None,
                 read_doc: bool = True,
                 use_raw_list: bool = False):
        """Set the function and ask for args with REPL mode.

        :param function: callable function
        :type function: callable
        :param choices: default choices for some variables, use it like {'arg_name': [1, 2, 3]}, defaults to None
        :type choices: Dict[str, list], optional
        :param checkboxes: multi-choice values for some variables, use it like {'arg_name': [1, 2, 3]}, defaults to None
        :type checkboxes: Dict[str, list], optional
        :param defaults: default values for some difficultly-input variables object, use it like {'arg_name': SomeComplexObject}, defaults to None
        :type defaults: Dict[str, list], optional
        """
        if not callable(function):
            raise ValueError
        self.function = function
        self.custom_style = custom_style
        self.use_raw_list = use_raw_list
        self.choices = choices or {}
        self.checkboxes = checkboxes or {}
        self.defaults = defaults or {}
        self._schema_args = None
        self._kwargs = None

    def run(self, kwargs=None):
        if kwargs is None:
            kwargs = self.ask_for_args()
        func_to_run = f'{self.function.__name__}(**{kwargs})'
        print(f'{self.sep_sig}Start to run {func_to_run}\n{self.sep_sig}')
        result = self.function(**kwargs)
        print(
            f'{self.sep_sig}{func_to_run} and return {type(result)}:\n{result}')

    def handle_input_decorator(self, param, kw=False):
        """kw means Dict handler."""

        def wrap(is_using_default):
            # nonlocal param
            ops = param.annotation.__args__ or (str, str)
            type_func1 = ops[0]
            if kw:
                type_func2 = ops[1]
            if is_using_default and param.default is not Parameter.empty:
                if check_type(param.default, param.annotation):
                    return param.default
                else:
                    print(
                        f'default value `{param.default}` not fit {param.annotation}, you can set default by self.defaults.'
                    )
            print('Invalid default value, should input one by one.')
            if kw:
                result = {}
            else:
                result = []
            while 1:
                if kw:
                    key = input('Input the dict\'s key(null for break): ')
                    if not key.strip():
                        break
                    key = type_func1(key) if callable(type_func1) else key
                    try:
                        key = type_func1(key) if callable(type_func1) else key
                    except ValueError:
                        print(f'bad value {key}, {type_func1} needed.')
                        continue
                    value = input('Input the dict\'s value: ')
                    try:
                        value = type_func2(value) if callable(
                            type_func2) else value
                    except ValueError:
                        print(f'bad value {value}, {type_func2} needed.')
                        continue
                    result[key] = value
                else:
                    value = input('Input the list\'s value(null for break): ')
                    if not value.strip():
                        break
                    try:
                        value = type_func1(value) if callable(
                            type_func1) else value
                    except ValueError:
                        print(f'bad value {value}, {type_func1} needed.')
                        continue
                    result.append(value)
            return result

        return wrap

    def print_doc(self, value):
        doc = self.function.__doc__
        if value:
            if doc.strip():
                print(f'Documentary:\n{doc}')
            else:
                print('no doc.')
        return value

    def make_question(self, param) -> Dict:
        if param.default is Parameter.empty:
            default = '[required]'
        else:
            default = f'default to {param.default}'
        msg = f'Input the value of `{param.name}` (type: {param.annotation}; {default};):\n'
        question = {
            'qmark': self.sep_sig,
            'type': 'input',
            'name': param.name,
        }
        question['message'] = msg
        question['validate'] = gen_validate(str)
        origin_type = param.annotation.__origin__
        if param.kind in self.NOT_SUPPORT_KIND:
            question['name'] = '_ask4args_ignore_name'
            question['type'] = 'confirm'
            question[
                'message'] = f'_POSITIONAL_ONLY / VAR_POSITIONAL ({param}) not support for now, will ignore this param.'
        elif param.name in self.choices:
            if self.use_raw_list:
                question['type'] = 'rawlist'
            else:
                question['type'] = 'list'
            question['choices'] = [{
                'name': str(item),
                'value': item
            } for item in self.choices[param.name]]
        elif origin_type in {int, float}:
            # use default value if fits annotation
            if check_type(param.default, param.annotation):
                question['default'] = str(param.default)
            if origin_type is int:
                question['validate'] = gen_validate(int)
                question['filter'] = lambda val: int(val)
            else:
                question['validate'] = gen_validate(float)
                question['filter'] = lambda val: float(val)
        elif origin_type is bool:
            question['type'] = 'confirm'
            if param.default is not Parameter.empty:
                question['default'] = param.default
        elif origin_type in {list, tuple, set}:
            if param.default is not Parameter.empty:
                print(
                    '[Warning] [list, tuple, set, dict] will ignore default value, use self.defaults instead.'
                )
            if self.use_raw_list:
                question['type'] = 'rawlist'
            else:
                question['type'] = 'list'
            if param.name in self.checkboxes:
                question['type'] = 'checkbox'
                question['choices'] = [{
                    'name': str(item),
                    'value': item
                } for item in self.checkboxes[param.name]]
            else:
                question['type'] = 'confirm'
                question['default'] = True
                question[
                    'message'] += f'\nThere is no choice / checkbox, use the default value [{param.default}](press Y / enter) or input your custom value(press N)'
                question['filter'] = self.handle_input_decorator(param)
        elif origin_type is dict:
            if param.default is not Parameter.empty:
                print(
                    '[Warning] [list, tuple, set, dict] will ignore default value, use self.defaults instead.'
                )
            question['type'] = 'confirm'
            question['default'] = True
            question[
                'message'] += f'\nThere is no choice / checkbox, use the default value [{param.default}](press Y / enter) or input your custom value(press N)'
            question['filter'] = self.handle_input_decorator(param, kw=True)
        else:
            # treate as str
            question['filter'] = lambda r: str(r)
            if param.default is not Parameter.empty:
                question['default'] = param.default
        return question

    def deal_with_arg(self, param: Parameter, questions: List, _kwargs: Dict):
        if param.name in self.defaults:
            # use default value instead, no need to ask question
            _kwargs[param.name] = self.defaults[param.name]
        else:
            # ask for param value
            question = self.make_question(param)
            if question:
                questions.append(question)

    def ask_for_args(self):
        args: dict = self.schema_args
        _kwargs = {}
        questions = []
        if self.function.__doc__:
            questions.append({
                'type': 'confirm',
                'name': '_ask4args_ignore_name',
                'message': 'Would you want to read the function doc?',
                'default': False,
                'filter': self.print_doc
            })
        for param in args['kwargs']:
            self.deal_with_arg(param, questions, _kwargs)

        answers = prompt(questions, style=self.custom_style)
        for name in list(answers.keys()):
            if name == '_ask4args_ignore_name':
                answers.pop(name, None)
        if args['varkw_name']:
            varkw = answers.pop(args['varkw_name'], {})
            _kwargs.update(varkw)
        if answers:
            _kwargs.update(answers)
        return _kwargs

    @property
    def schema_args(self):
        if self._schema_args is None:
            self._schema_args = self.make_schema()
        return self._schema_args

    @classmethod
    def ensure_type(cls, arg_type):
        # ignore _SpecialForm
        if arg_type is Parameter.empty or isinstance(arg_type, _SpecialForm):
            arg_type = str
        bad_type = getattr(arg_type, '__origin__',
                           arg_type) not in cls.valid_types
        bad_sub_type = any((_arg not in cls.valid_types
                            for _arg in getattr(arg_type, '__args__', ())))
        # check cls.valid_types
        if bad_type or bad_sub_type:
            raise TypeError(
                f'As an input should be the base types {cls.valid_types}, but given {arg_type}.'
            )
        if not isinstance(arg_type, _GenericAlias):
            arg_type = _alias(arg_type, ())
        return arg_type

    def make_schema(self) -> Dict[str, Any]:
        sig = inspect.signature(self.function)
        print(
            f'{self.sep_sig}Preparing {self.function.__name__}{sig}\n{self.sep_sig}'
        )
        kwargs: List[Parameter] = []
        varkw_name = ''
        for param in sig.parameters.values():
            if param.kind == Parameter.VAR_KEYWORD:
                varkw_name = param.name
            if param.kind in self.NOT_SUPPORT_KIND:
                kwargs.append(param)
                continue
            arg_type = param.annotation if param.annotation is not Parameter.empty else str
            arg_type = self.ensure_type(param.annotation)
            param = param.replace(annotation=arg_type)
            # normalizing

            kwargs.append(param)
        return {'kwargs': kwargs, 'varkw_name': varkw_name}

    def __str__(self):
        return f'{self.__class__.__name__}{self.schema_args}'
