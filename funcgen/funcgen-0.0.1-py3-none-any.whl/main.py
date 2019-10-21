'''This module implements the API'''

from inspect import Signature, Parameter, _ParameterKind
from itertools import chain, product
from typing import Any, Callable, Generator, Iterable, List, Sequence, Tuple, Type


ParamTuple = Tuple[Sequence[str], Sequence[Any], Sequence[Type]]
VarParamTuple = Tuple[Sequence[str], Sequence[Type]]
ParamCombo = List[Parameter]


def valid_parameters(param_kind: _ParameterKind,
                     params: Sequence[ParamTuple]) -> Generator[ParamCombo, None, None]:
    '''Takes in parameter names, defaults, and annotations and generates
    every sequence of parameters possible from every combination of
    those attributes.

    A ``ParamTuple`` is a tuple of three sequences: names, default
    values, and annotations, respectively. ``params`` is a sequence of
    ``ParamTuples`` such that the cross product of ``params[i]``
    represents the range of desired values for the *ith* parameter.

    Given every subset ``params[:i]`` for ``i`` in
    ``range(len(params))``, this function will yield items from the
    cross product of the desired values for those parameters in the
    subset as a list of ``Parameters``.

    If ``param_kind`` is ``Parameter.POSITIONAL_OR_KEYWORD`` or
    ``Parameter.POSITIONAL_ONLY``, then those lists where some
    parameter has a default value and previous parameter does not are
    not yielded because they would be invalid.

    Use ``Parameter.empty`` to specify the abscence of type annotation
    or default value.

    .. testsetup::

       from funcgen import valid_parameters
       from inspect import Parameter, Signature

    >>> [str(x) for x in valid_parameters(Parameter.POSITIONAL_OR_KEYWORD,
    ...                                   [(['arg1'],
    ...                                     [42, Parameter.empty],
    ...                                     [int, Parameter.empty])])]
    ['[]',
     '[<Parameter "arg1:int=42">]',
     '[<Parameter "arg1=42">]',
     '[<Parameter "arg1:int">]',
     '[<Parameter "arg1">]']

    >>> [str(x) for x in valid_parameters(Parameter.POSITIONAL_OR_KEYWORD,
    ...                                   [(['arg1'], [42, Parameter.empty], [int]),
    ...                                    (['arg2'], [107.7, Parameter.empty], [float])])]
    ['[]',
     '[<Parameter "arg1:int=42">]',
     '[<Parameter "arg1:int">]',
     '[<Parameter "arg1:int=42">, <Parameter "arg2:float=107.7">]',
     '[<Parameter "arg1:int">, <Parameter "arg2:float=107.7">]',
     '[<Parameter "arg1:int">, <Parameter "arg2:float">]']


    >>> [str(x) for x in valid_parameters(Parameter.KEYWORD_ONLY,
    ...                                   [(['arg1'], [42, Parameter.empty], [int]),
    ...                                    (['arg2'], [107.7, Parameter.empty], [float])])]
    ['[]',
     '[<Parameter "arg1:int=42">]',
     '[<Parameter "arg1:int">]',
     '[<Parameter "arg1:int=42">, <Parameter "arg2:float=107.7">]',
     '[<Parameter "arg1:int">, <Parameter "arg2:float=107.7">]',
     '[<Parameter "arg1:int=42">, <Parameter "arg2:float">]',
     '[<Parameter "arg1:int">, <Parameter "arg2:float">]']

    :param param_kind: must be ``Parameter.POSITIONAL_ONLY``, ``Parameter.KEYWORD_ONLY``, or ``Parameter.POSITIONAL_OR_KEYWORD``.
    :param Sequence[ParamTuple] params:

    '''
    if param_kind in (Parameter.POSITIONAL_ONLY, Parameter.POSITIONAL_OR_KEYWORD):
        return _valid_positional_param_combinations(param_kind, params)
    if param_kind == Parameter.KEYWORD_ONLY:
        return _valid_keyword_param_combinations(param_kind, params)
    raise ValueError('Cannot make combinations of parameter kind ({param_kind}')


def _valid_positional_param_combinations(param_kind: _ParameterKind,
                                         params: Sequence[ParamTuple]) \
                                         -> Generator[ParamCombo, None, None]:
    old_combos: List[ParamCombo] = [[]]
    yield old_combos[0]
    for param_names, param_defaults, param_annotations in params:
        new_combos = []
        param_combos = product(param_names, param_defaults, param_annotations)
        for (param_name, param_default, param_annotation), old_combo in product(param_combos, old_combos):
            prev_default = old_combo[-1].default if old_combo else Parameter.empty
            if prev_default != Parameter.empty and param_default == Parameter.empty:
                continue
            param = Parameter(param_name, param_kind, default=param_default, annotation=param_annotation)
            new_combos.append(old_combo + [param])
            yield new_combos[-1]
        old_combos = new_combos


def _valid_keyword_param_combinations(param_kind: _ParameterKind,
                                      params: Sequence[ParamTuple]) \
                                      -> Generator[ParamCombo, None, None]:
    old_combos: List[ParamCombo] = [[]]
    yield old_combos[0]
    for param_names, param_defaults, param_annotations in params:
        new_combos = []
        param_combos = product(param_names, param_defaults, param_annotations)
        for (param_name, param_default, param_annotation), old_combo in product(param_combos, old_combos):
            param = Parameter(param_name, param_kind, default=param_default, annotation=param_annotation)
            new_combos.append(old_combo + [param])
            yield new_combos[-1]
        old_combos = new_combos


def valid_signatures(args: Sequence[ParamTuple] = [], kwargs: Sequence[ParamTuple] = [],  # pylint: disable=dangerous-default-value
                     var_args: VarParamTuple = ([], []), var_kwargs: VarParamTuple = ([], []),
                     return_annotations: Sequence[object] = [Signature.empty]) \
                     -> Generator[Signature, None, None]:
    '''This will generate every combination of the parameters and
    parameter attributes passed to it, if that combination results in
    a valid Python function signature.

    A ``VarParamTuple`` describes the range of attributes to give a
    variadic parameter. It is a tuple of two sequences: names and type
    annotations, respectively. The cross product of that tuple
    represents the range of attributes to give that parameter in the
    results.

    Use ``Parameter.empty`` to specify a missing type annotation or
    default value, and ``Signature.empty`` to specify a missing return
    type annotation.

    .. testsetup::

       from funcgen import valid_signatures
       from inspect import Parameter, Signature

    >>> args = [(['arg1'], [Parameter.empty, 42], [int])]
    >>> kwargs = []
    >>> var_args = (['args'], [float])
    >>> var_kwargs = ([], [])
    >>> return_annotations = [Signature.empty, int]
    >>> [str(s) for s in valid_signatures(args, kwargs, var_args, var_kwargs, return_annotations)]
    ['()',
     '() -> int',
     '(*args:float)',
     '(*args:float) -> int',
     '(arg1:int)',
     '(arg1:int) -> int',
     '(arg1:int, *args:float)',
     '(arg1:int, *args:float) -> int',
     '(arg1:int=42)',
     '(arg1:int=42) -> int',
     '(arg1:int=42, *args:float)',
     '(arg1:int=42, *args:float) -> int']

    :param Sequence[ParamTuple] args: A sequence of ``ParamTuples`` used to create ``Parameter.POSITIONAL_OR_KEYWORD`` ``Parameters`` (see ``valid_parameters``)
    :param Sequence[ParamTuple] kwargs: A sequence of ``ParamTuples`` used to create ``Parameter.KEYWORD_ONLY`` ``Parameters`` (see ``valid_parameters``)
    :param Sequence[VarParamTuple] var_args: A sequence of ``VarParamTuples`` used to create ``Parameter.VAR_POSITIONAL`` ``Parameters`` (see above)
    :param Sequence[VarParamTuple] var_kwargs: A sequence of ``VarParamTuples`` used to create ``Parameter.VAR_KEYWORD`` ``Parameters`` (see above)
    :param return_annotations: A sequence of return annotations.

    '''
    arg_combos = list(valid_parameters(Parameter.POSITIONAL_OR_KEYWORD, args))

    kwarg_combos = list(valid_parameters(Parameter.KEYWORD_ONLY, kwargs))

    var_args_vector = [[]] + [[Parameter(name, Parameter.VAR_POSITIONAL, annotation=ann)]
                              for name, ann in product(*var_args)]

    var_kwargs_vector = [[]] + [[Parameter(name, Parameter.VAR_KEYWORD, annotation=ann)]
                                for name, ann in product(*var_kwargs)]

    for params_products in product(arg_combos, var_args_vector, kwarg_combos, var_kwargs_vector):
        params = list(chain.from_iterable(params_products))
        for return_ann in return_annotations:
            yield Signature(params, return_annotation=return_ann)


def all_valid_signatures() -> Generator[Signature, None, None]:
    '''A convenience function that will generate an example of every
    category of valid function signature for Python. That is all
    combinations of

    - Zero, one, and two positional parameters with and without type
      annotations and default values.
    - Zero, one, and two keyword only parameters with and without type
      annotations and default values.
    - With and without `*args`, with and without a type annotation.
    - With and without `**kwargs`, with and without a type annotation.
    - With and without a return type annotation.

    See the source for the call to ``valid_signatures``

    '''
    args = [(['arg1'], [Parameter.empty, None], [Parameter.empty, None]),
            (['arg2'], [Parameter.empty, None], [Parameter.empty, None])]
    kwargs = [(['kwarg1'], [Parameter.empty, None], [Parameter.empty, None]),
              (['kwarg2'], [Parameter.empty, None], [Parameter.empty, None])]
    var_args = (['args'], [Parameter.empty, None])
    var_kwargs = (['kwargs'], [Parameter.empty, None])
    return_annotations = [Signature.empty, None]
    return valid_signatures(args, kwargs, var_args, var_kwargs, return_annotations)


# def valid_functions(signatures: Iterable[Signature], body: Callable = lambda: None) -> Generator[Sequence[Callable], None, None]:
def valid_functions(signatures: Iterable[Signature]) -> Generator[Sequence[Callable], None, None]:
    '''For every signature in ``signatures`` this function will yield a
    sequence of callable objects representing various forms that
    signature could take.

    Given an example signature like::

      (arg1:int=42, *args:str, kwarg1=False, kwarg2:bool) -> bytes

    The sequence yielded is equivalent to this::

      # Regular function
      def f(arg1:int=42, *args:str, kwarg1=False, kwarg2:bool) -> bytes:
          pass

      # Bound Method
      class Foo:
          def f(arg1:int=42, *args:str, kwarg1=False, kwarg2:bool) -> bytes:
              pass

      # Static Class Method
      class FooStatic:
          @staticmethod
          def f(arg1:int=42, *args:str, kwarg1=False, kwarg2:bool) -> bytes:
              pass

      # Sequence yielded
      return f, Foo().f, FooStatic.f, FooStatic().f

    :param signatures:

    '''

    self_param = Parameter('self', Parameter.POSITIONAL_OR_KEYWORD)

    for signature in signatures:
        method_signature = signature.replace(parameters=[self_param] + list(signature.parameters.values()))

        # body_call = signature2call(signature)

        # test_scope = {'body': body}
        # exec(f'def f{signature}: return body{body_call}\n'
        #      f'class C:\n'
        #      f'    @staticmethod\n'
        #      f'    def fs{signature}: return body{body_call}\n'
        #      f'    def f{method_signature}: return body{body_call}', test_scope)
        test_scope = dict()
        exec(f'def f{signature}: pass\n'  # pylint: disable=W0122
             f'class C:\n'
             f'    @staticmethod\n'
             f'    def fs{signature}: pass\n'
             f'    def f{method_signature}: pass', test_scope)

        f = test_scope['f']  # pylint: disable=C0103
        C = test_scope['C']  # pylint: disable=C0103

        yield f, C.fs, C().fs, C().f


def all_valid_functions() -> Generator[Sequence[Callable], None, None]:
    '''A convenience function that feeds ``all_valid_signatures`` into
    ``valid_functions`` to produce all callable forms of all valid
    signatures.

    '''
    return valid_functions(all_valid_signatures())


# def signature2call(signature: Signature) -> str:
#     args = []
#     var_args = None
#     kwargs = []
#     var_kwargs = None
#     for name, param in signature.parameters.items():
#         if param.kind in (Parameter.POSITIONAL_ONLY, Parameter.POSITIONAL_OR_KEYWORD):
#             args.append(name)
#         elif param.kind == Parameter.VAR_POSITIONAL:
#             var_args = name
#         elif param.kind == Parameter.KEYWORD_ONLY:
#             kwargs.append(name)
#         elif param.kind == Parameter.VAR_KEYWORD:
#             var_kwargs = name
#
#     call = ''
#
#     call += ', '.join(args)
#
#     if var_args:
#         if call: call += ', '
#         call += f'*{var_args}'
#
#     if kwargs:
#         if call: call += ', '
#         call += ', '.join([f'{x}={x}' for x in kwargs])
#
#     if var_kwargs:
#         if call: call += ', '
#         call += f'*{var_kwargs}'
#     call = f'({call})'
#
#     return call
