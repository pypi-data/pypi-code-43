import inspect
from functools import partial
from inspect import Parameter
from typing import Any, AnyStr, Dict, List, _alias, _GenericAlias, _SpecialForm
import os
import PySimpleGUI as sg
from pydantic import create_model
from pydantic.error_wrappers import ValidationError as ValidateError
from PyInquirer import (Token, Validator, prompt, style_from_dict)

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


class Param(object):
    __slots__ = ('name', 'kind', 'annotation', 'default')

    def __init__(self, name, kind, annotation=..., default=...):
        self.name = name
        self.kind = kind
        self.annotation = annotation
        self.default = default

    def __str__(self):
        return f'Param(name={self.name}, kind={self.kind}, annotation={self.annotation}, default={self.default})'


class BaseSchema(object):
    sep_sig = f'{"=" * 30}\n'
    valid_types = {list, int, bool, str, tuple, set, float, dict}
    NOT_SUPPORT_KIND = {Parameter.POSITIONAL_ONLY, Parameter.VAR_POSITIONAL}

    def __init__(self,
                 function,
                 choices: Dict[str, list] = None,
                 checkboxes: Dict[str, List[Any]] = None,
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
        self.varkw_name = None
        self.custom_style = custom_style
        self.use_raw_list = use_raw_list
        self.choices = choices or {}
        self.checkboxes = checkboxes or {}
        self.defaults = defaults or {}
        self.NOT_SUPPORT_KIND_MSG: List[str] = []

    def run(self):
        raise NotImplementedError

    def ask_for_args(self, *args, **kwargs):
        raise NotImplementedError

    def print_doc(self, value=True):
        doc = self.function.__doc__
        if value:
            if doc.strip():
                print(f'Documentary:\n{doc}')
            else:
                print('no doc.')
        return value

    def empty_to_ellipsis(self, obj, default=...):
        if obj is Parameter.empty:
            return default
        else:
            return obj

    def get_type_null(self, _type, default=''):
        if _type in (Parameter.empty, ...):
            return default
        otype = getattr(_type, '__origin__', _type)
        try:
            if callable(otype):
                return otype()
            else:
                return default
        except TypeError:
            return default

    @property
    def schema_args(self):
        return self.make_schema()

    def make_schema(self):
        sig = inspect.signature(self.function)
        print(
            f'{self.sep_sig}Preparing {self.function.__name__}{sig}\n{self.sep_sig}'
        )
        kwargs: List[Parameter] = []
        for param in sig.parameters.values():
            if param.name in self.defaults:
                continue
            if param.kind == Parameter.VAR_KEYWORD:
                self.varkw_name = param.name
            if param.kind in self.NOT_SUPPORT_KIND:
                msg = f'Not support {param} will be ignored.'
                print(msg)
                self.NOT_SUPPORT_KIND_MSG.append(msg)
                continue
            kwargs.append(
                Param(param.name, param.kind,
                      self.empty_to_ellipsis(param.annotation, str),
                      {} if param.kind == Parameter.VAR_KEYWORD else
                      self.empty_to_ellipsis(
                          param.default, self.get_type_null(param.annotation))))
        model_kwargs = {p.name: (p.annotation, p.default) for p in kwargs}
        self.FuncSchema = create_model('FuncSchema', **model_kwargs)

        return kwargs

    def __str__(self):
        return f'{self.__class__.__name__}{self.schema_args}'


class Ask4Args(BaseSchema):
    """Terminal UI automatic generator"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.share_kwargs: Dict[str, Any] = {}

    def validate(self, key, text):
        try:
            self.share_kwargs[key] = text
            self.FuncSchema(**self.share_kwargs)
            return True
        except ValidateError as err:
            return f'{err}'.replace('\n', ' ')

    def gen_validator(self, key):
        return partial(self.validate, key)

    def run(self, kwargs=None):
        if kwargs is None:
            kwargs = self.ask_for_args()
        if self.varkw_name:
            varkw = kwargs.pop(self.varkw_name, {})
            kwargs.update(varkw)
        if self.defaults:
            kwargs.update(self.defaults)
        func_to_run = f'{self.function.__name__}(**{kwargs})'
        print(f'{self.sep_sig}Start to run {func_to_run}\n{self.sep_sig}')
        result = self.function(**kwargs)
        print(f'{self.sep_sig}{func_to_run}:\n{result}')

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
            self.share_kwargs[param.name] = result
            return result

        return wrap

    def make_question(self, param) -> Dict:
        if param.default is Parameter.empty:
            default_template = '[required]'
        else:
            default_template = f'default to {param.default!r}'
        msg = f'Input the value of `{param.name}` ({default_template}) {param.annotation}:'
        question = {
            # 'qmark': self.sep_sig,
            'type': 'input',
            'name': param.name,
            'message': msg,
            'validate': self.gen_validator(param.name),
        }
        origin_type = getattr(param.annotation, '__origin__', param.annotation)
        if isinstance(param.default, (origin_type,)) and param.default:
            question['default'] = str(param.default)
        else:
            question['default'] = ''
        if param.name in self.choices:
            if self.use_raw_list:
                question['type'] = 'rawlist'
            else:
                question['type'] = 'list'
            question['choices'] = [{
                'name': str(item),
                'value': item
            } for item in self.choices[param.name]]
            # question.pop('validate', None)
        elif origin_type is bool:
            question['type'] = 'confirm'
        elif origin_type in {list, tuple, set}:
            if self.use_raw_list:
                question['type'] = 'rawlist'
            else:
                question['type'] = 'list'
            if param.name in self.checkboxes:
                question['type'] = 'checkbox'
                question.pop('default', None)
                question['choices'] = [{
                    'name': str(item),
                    'value': item
                } for item in self.checkboxes[param.name]]
            else:
                question['type'] = 'confirm'
                question[
                    'message'] += f'\nThere is no choice / checkbox, use the default value {param.default!r} (press Y / enter) or input your custom value(press N)'
                question['filter'] = self.handle_input_decorator(param)
        elif origin_type is dict:
            question['type'] = 'confirm'
            question[
                'message'] += f'\nThere is no choice / checkbox, use the default value {param.default!r} (press Y / enter) or input your custom value(press N)'
            question['filter'] = self.handle_input_decorator(param, kw=True)
        return question

    def deal_with_arg(self, param: Parameter, questions: List):
        # ask for param value
        question = self.make_question(param)
        if question:
            questions.append(question)

    def ask_for_args(self):
        kwargs: dict = self.schema_args
        questions = []
        if self.function.__doc__:
            questions.append({
                'type': 'confirm',
                'name': '_ask4args_ignore_name',
                'message': 'Would you want to read the function doc?',
                'default': False,
                'filter': self.print_doc
            })
        for param in kwargs:
            self.deal_with_arg(param, questions)
        answers = prompt(questions, style=self.custom_style)
        answers.pop('_ask4args_ignore_name', None)
        self.share_kwargs.update(answers)
        self.share_kwargs = self.FuncSchema(**self.share_kwargs).dict()
        return self.share_kwargs


class Ask4ArgsGUI(BaseSchema):
    """GUI automatic generator"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.checkbox_maps: Dict[str, Any] = {}
        self.list_type_names = set()
        self.dict_type_names = set()
        for key, value in self.checkboxes.items():
            for v in value:
                self.checkbox_maps[f'{key}-{v}'] = v

    def input_type_handler(self, param):
        otype = getattr(param.annotation, '__origin__', param.annotation)
        if param.name in self.choices:
            return sg.Combo(
                values=self.choices[param.name], size=(40, 1), key=param.name)
        elif param.name in self.checkboxes:
            cb = self.checkboxes[param.name]
            return sg.Listbox(
                values=[str(item) for item in cb],
                select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE,
                size=(45, 3),
                key=param.name)
        elif otype in (list, dict):
            return sg.Multiline('', size=(45, 2), key=param.name)
        elif otype is bool:
            return sg.Checkbox(
                'True',
                default=param.default
                if param.default in {True, False} else False,
                key=param.name)
        else:
            return sg.InputText(str(param.default or ''), key=param.name)

    def ensure_defaults(self, values):
        if self.defaults:
            values.update(self.defaults)
        return values

    def run(self):
        params: List = self.schema_args
        layout = [
            [sg.Text('Fill in the blanks', font=("Helvetica", 25))],
        ]
        for param in params:
            if param.kind == Parameter.VAR_KEYWORD:
                self.varkw_name = param.name
            if param.default is Parameter.empty:
                default_template = '[required]'
            else:
                default_template = f'default to {param.default!r}'
            msg = f'{param.name}, {param.annotation}, {default_template}'
            otype = getattr(param.annotation, '__origin__', param.annotation)
            if otype is list:
                self.list_type_names.add(param.name)
                msg = f'{msg} (splits by \\n)'
            elif otype is dict:
                self.dict_type_names.add(param.name)
                msg = f'{msg} (splits by \\t & \\n)'
            _text = sg.Text(msg, font=("Helvetica", 14))
            _input = self.input_type_handler(param)
            line = [[_text], [_input]]
            layout.extend(line)
        for msg in self.NOT_SUPPORT_KIND_MSG:
            layout.append([sg.Text(msg, font=("Helvetica", 12))])
        layout.append([
            sg.Button(
                'Ok', size=(8, 1), button_color=('black', 'white'), key='ok'),
            sg.Button('Cancel', size=(8, 1), button_color=('black', 'white')),
            sg.Button('Doc', size=(8, 1), button_color=('black', 'white')),
            sg.Button('Clear', size=(8, 1), button_color=('black', 'white'))
        ])

        layout.append([
            sg.Output(
                size=(60, 15), font=('Helvetica', 12), key='Ask4ArgsGUIOutput')
        ])
        window = sg.Window(f'{self.function.__name__} - Ask4ArgsGUI', layout)
        while True:
            event, values = window.Read()
            if event == 'Clear':
                window.FindElement('Ask4ArgsGUIOutput').Update('')
                continue
            elif event == 'ok':
                # trans str into list
                if self.list_type_names:
                    for name in self.list_type_names:
                        if isinstance(values[name], list):
                            continue
                        value = values[name].strip()
                        if value:
                            values[name] = value.split('\n')
                        else:
                            values[name] = []
                if self.dict_type_names:
                    for name in self.dict_type_names:
                        if isinstance(values[name], dict):
                            continue
                        value = {}
                        if values[name].strip():
                            for line in values[name].split('\n'):
                                line = line.strip()
                                if line:
                                    k, v = line.split('\t')
                                    value[k] = v
                        values[name] = value
                values = self.ensure_defaults(values)
                func_to_run = f'{self.function.__name__}(**{values})'
                print(
                    f'{self.sep_sig}Start to run {func_to_run}\n{self.sep_sig}')
                try:
                    kwargs = self.FuncSchema(**values).dict()
                    kwargs = self.ensure_defaults(kwargs)
                    if self.varkw_name:
                        _values = kwargs.pop(self.varkw_name, {})
                        kwargs.update(_values)
                    result = self.function(**kwargs)
                except ValidateError as err:
                    result = f'{err}'
                print(f'[Return]\n{self.sep_sig}{result}')
                continue
            elif event in (None, 'Cancel'):
                quit()
            elif event == 'Doc':
                self.print_doc()
                continue

        window.Close()


class Ask4ArgsWeb(BaseSchema):
    """GUI automatic generator"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        raise NotImplementedError
