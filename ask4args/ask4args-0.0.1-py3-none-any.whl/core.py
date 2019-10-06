import inspect
import re
from collections import namedtuple
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
Schema = namedtuple('Schema', ['name', 'type', 'default'])


class NumberValidator(Validator):

    def validate(self, document):
        try:
            if document.text.count('.') == 1:
                float(document.text)
            else:
                int(document.text)
        except ValueError:
            raise ValidationError(message='Please enter a number',
                                  cursor_position=len(
                                      document.text))  # Move cursor to end


class Ask4Args(object):
    sep_sig = f'{"=" * 40}\n'

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
        self.arg_docs = self.parse_function_doc(function)
        self.function = function
        self.custom_style = custom_style
        self.use_raw_list = use_raw_list
        self.choices = choices or {}
        self.checkboxes = checkboxes or {}
        self.defaults = defaults or {}

    def run(self):
        args = self.kwargs
        kwargs = args['kwargs']
        kwargs.update(args['varkw'])
        func_to_run = f'{self.function.__name__}(**{kwargs})'
        print(f'{self.sep_sig}Start to run {func_to_run}')
        result = self.function(**kwargs)
        print(
            f'{self.sep_sig}{func_to_run} and return {type(result)}:\n{result}')

    def parse_function_doc(self, function) -> Dict[str, str]:
        arg_docs: Dict[str, str] = {}
        doc = function.__doc__
        doc_template = '''
[summary]

    :param arg1: [description]
    :type arg1: [type]'''
        # check valid doc
        if doc:
            doc = re.sub(r'^[\s\S]*?:param ', ':param ', doc)
            items = [
                item for item in re.split(r'(?=:param)', doc) if item.strip()
            ]
            for item in items:
                matched = re.search(':param (.+?):', item)
                if matched:
                    key = matched.group(1).strip()
                    desc = re.sub(r':type [\s\S]*', '', item).strip()
                    arg_docs[key] = desc
        if not arg_docs:
            print(
                f'No valid sphinx documentary for function[{function.__name__}], format like:{doc_template}'
            )
            return arg_docs
        return arg_docs

    def handle_input_decorator(self, arg, kw=False):
        """kw means Dict handler."""

        def wrap(is_using_default):
            # nonlocal arg
            ops = arg.type.__args__ or (str, str)
            type_func1 = ops[0]
            if kw:
                type_func2 = ops[1]
            if is_using_default and arg.default != ...:
                value = type_func1(
                    arg.default) if callable(type_func1) else arg.default
                return arg.default
            elif arg.default == ...:
                print('no default value, should input one by one.')
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
                    value = input('Input the dict\'s value: ')
                    value = type_func2(value) if callable(type_func2) else value
                    result[key] = value
                else:
                    value = input('Input the list\'s value(null for break): ')
                    if not value.strip():
                        break
                    value = type_func1(value) if callable(type_func1) else value
                    result.append(value)
            return result

        return wrap

    def print_doc(self, value):
        if value:
            print(
                f'Function({self.function.__name__})\'s doc:\n{self.function.__doc__}'
            )
        return value

    def make_question(self, arg) -> Dict:
        if arg.default == ...:
            default = '[required]'
        else:
            default = f'default to {arg.default}'
        msg = f'Input the value of `{arg.name}`:\n(name: {arg.name}; type: {arg.type}; {default}; {self.arg_docs.get(arg.name, "")})\n'
        question = {
            'qmark': self.sep_sig,
            'type': 'input',
            'name': arg.name,
        }
        question['message'] = msg
        origin_type = arg.type.__origin__
        if arg.name in self.choices:
            if self.use_raw_list:
                question['type'] = 'rawlist'
            else:
                question['type'] = 'list'
            question['choices'] = [{
                'name': str(item),
                'value': item
            } for item in self.choices[arg.name]]
        elif origin_type in {int, float}:
            if arg.default != ...:
                question['default'] = str(arg.default)
            question['validate'] = NumberValidator
            if origin_type is int:
                question['filter'] = lambda val: int(val)
            else:
                question['filter'] = lambda val: float(val)
        elif origin_type is bool:
            question['type'] = 'confirm'
            if arg.default == ...:
                question['default'] = True
            else:
                question['default'] = arg.default
        elif origin_type in {list, tuple, set}:
            if arg.default != ...:
                raise ValueError(
                    'type [list, tuple, dict] can not set default value. Please use BaseSchema `defaults` attr.'
                )
            if self.use_raw_list:
                question['type'] = 'rawlist'
            else:
                question['type'] = 'list'
            if arg.name in self.checkboxes:
                question['type'] = 'checkbox'
                question['choices'] = [{
                    'name': str(item),
                    'value': item
                } for item in self.checkboxes[arg.name]]
            else:
                question['type'] = 'confirm'
                question['default'] = True
                question[
                    'message'] += f'\nThere is no choice / checkbox, use the default value [{arg.default}](press Y / enter) or input your custom value(press N)'
                question['filter'] = self.handle_input_decorator(arg)
        elif origin_type is dict:
            if arg.default != ...:
                raise ValueError(
                    'type [list, tuple, dict] can not set default value. Please use BaseSchema `defaults` attr.'
                )
            question['type'] = 'confirm'
            question['default'] = True
            question[
                'message'] += f'\nThere is no choice / checkbox, use the default value [{arg.default}](press Y / enter) or input your custom value(press N)'
            question['filter'] = self.handle_input_decorator(arg, kw=True)
        else:
            # treate as str
            question['filter'] = lambda r: str(r)
            if arg.default != ...:
                question['default'] = arg.default
        return question

    def ask_for_args(self):
        args: dict = self.schema_args
        print(
            f'function({self.function.__name__})[rtype: {args["kwargs"].pop("return", Schema(0,Any,0)).type}] starts asking for args:'
        )
        self._kwargs = {'kwargs': {}, 'varkw': {}}
        questions = []
        if self.function.__doc__:
            questions.append({
                'type': 'confirm',
                'name': '_will_show_doc_of_function',
                'message': 'Would you want to read the function doc?',
                'default': False,
                'filter': self.print_doc
            })
        for name, arg in args['kwargs'].items():
            if arg.name in self.defaults:
                # use default value instead
                self._kwargs['kwargs'][name] = self.defaults[arg.name]
            else:
                question = self.make_question(arg)
                if question:
                    questions.append(question)
        answers = prompt(questions, style=self.custom_style)
        answers.pop('_will_show_doc_of_function', None)
        if answers:
            # self._kwargs['varargs'] = answers.pop(args['varargs_name'], [])
            self._kwargs['varkw'] = answers.pop(args['varkw_name'], {})
            self._kwargs['kwargs'] = answers
        return self._kwargs

    @property
    def kwargs(self):
        return self.ask_for_args()

    @property
    def schema_args(self):
        return self.make_schema(self.function)

    def ensure_type(self, value_type):
        if isinstance(value_type, _SpecialForm):
            value_type = object
        if not isinstance(value_type, _GenericAlias):
            value_type = _alias(value_type, ())
        return value_type

    def make_schema(self, function) -> Dict[str, Any]:
        args = inspect.getfullargspec(function)
        print(args)
        result: Dict[str, Any] = {}
        normal_args: List[Schema] = []
        # add normal_args args
        defaults = list(args.defaults or ())
        for name in reversed(args.args):
            if defaults:
                default_value = defaults.pop(-1)
            else:
                default_value = ...
            value_type = args.annotations.get(name, Any)
            normal_args.insert(
                0, Schema(name, self.ensure_type(value_type), default_value))
        kwargs = {schema.name: schema for schema in normal_args}
        for name in args.kwonlyargs:
            default_value = args.kwonlydefaults.get(name, ...)
            value_type = args.annotations.get(name, Any)
            kwargs[name] = Schema(name, self.ensure_type(value_type),
                                  default_value)
        # process the *varargs
        if args.varargs is not None:
            raise ValueError('do not support varargs like *args.')
        # process the **varkw
        if args.varkw is not None:
            kwargs[args.varkw] = Schema(
                args.varkw,
                self.ensure_type(
                    args.annotations.get(args.varkw, Dict[str, str])), ...)
        # # process the return annotation
        # kwargs['return'] = Schema(
        #     'return', self.ensure_type(args.annotations.get('return', object)),
        #     ...)
        kwargs.pop('return', None)
        valid_types = {list, int, bool, str, tuple, set, float, dict}
        for index, arg in enumerate(list(kwargs.values())):
            if index == 0 and arg.name in {
                    'self', 'cls'
            } and arg.default == ... and inspect.ismethod(self.function):
                # ignore method's cls / self
                kwargs.pop(arg.name, None)
                continue
            if arg.type.__origin__ not in valid_types:
                raise TypeError(
                    f'arg type only support the {valid_types}, but given {arg.type.__origin__}'
                )
        result['kwargs'] = kwargs
        # result['varargs_name'] = args.varargs
        result['varkw_name'] = args.varkw
        return result

    def __str__(self):
        """example: BaseSchema{'return': Schema(name='return', type=typing.Any, default=Ellipsis), 'all_args': {'a': Schema(name='a', type=<class 'int'>, default=Ellipsis), 'b': Schema(name='b', type=<class 'int'>, default=4), 'args_list': Schema(name='args_list', type=typing.List[str], default=Ellipsis), 'args_dict': Schema(name='args_dict', type=typing.Dict[str, str], default=Ellipsis)}}"""
        return f'{self.__class__.__name__}{self.schema_args}'
