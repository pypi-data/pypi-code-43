# -*- coding: utf-8 -*-

"""

**中文文档**




"""

import attr
import typing
from troposphere_mate.core.sentiel import Sentinel, NOTHING, REQUIRED
from .iterator import walk_lbd_handler


@attr.s
class BaseConfig(object):
    """
    Lambda Function Level Config.

    Every child function under a resource inherits :class:`ResourceConfig``.

    **中文文档**

    一个特殊的用于指定配置的数据类型. 该基础类用于指定 Lambda Function, API Gateway Method
    等配置.

    - 所有必要的属性都给予 ``REQUIRED`` 默认值
    - 所有可选的属性都给予 ``NOTHING`` 默认值
    - ``_default`` 中只定义那些 一定会有用到, 但是值不一定的值
    """
    _default = dict()  # type: dict

    def absorb(self, other):
        """
        inherit values from other config if the current one is a Sentinel.

        :type other: FunctionConfig

        **中文文档**

        从另一个 实例 当中吸取那些被数值化的数据.
        """
        this_data = attr.asdict(self)
        other_data = attr.asdict(other)
        for key, value in this_data.items():
            if isinstance(value, Sentinel):
                if key in other_data:
                    setattr(self, key, other_data[key])

    def fill_na_with_default(self):
        """
        Fill default value into current instance, if the field already has
        a value, then skip that field.

        **中文文档**

        针对于可选属性, 如果用户未指定初始值, 则使用 ``_default`` 变量中的值.
        """
        for key, value in self._default.items():
            if isinstance(getattr(self, key), Sentinel):
                setattr(self, key, value)

    def post_init_hooker(self):
        """
        """
        pass


def config_inherit_handler(module_name: str,
                           config_field: str,
                           config_class: typing.Type[BaseConfig],
                           valid_func_name_list: typing.List[str]):
    """
    Recursively iterate all sub modules and potential lambda handler functions.
    assign them a instance lambda function config class. sub module will inherit
    parent module's config, lambda handler function will inherit module's config.

    :param module_name:
    :param config_field:
    :param config_class:
    :param valid_func_name_list:

    **中文文档**

    从 ``module_name`` 模块开始, 使用遍历算法遍历所有子模块. 检查所有子模块中的
    ``config_field`` 这一属性, 默认这一属性是一个 ``config_class`` 的实例. 如果
    该属性未被定义, 则创建一个新的 ``config_class`` 实例.

    同时, 尝试检查在 ``valid_func_name_list`` 中定义的函数名, 假设这些函数名是
    lambda_handler 函数, 检查这些函数的 ``config_field`` 属性.

    对于 ``config_class`` 的实例, 我们遵循, 子模块继承母模块, 函数继承当前模块.
    子 ``config_class`` 中的值覆盖继承而来的值.

    **功能**

    此函数的作用是使得 :class:`~lbdrabbit.config_inherit.base.BaseConfig`` 实例能够以
    package -> module -> function 的顺序 继承设定值.

    举例来说, 我们自定义了一个 ``LbdFuncConfig``类, 并将其指定给 lambda handler 函数的
    __func_config__ 属性. 其中有一个设定值叫 timeout.

    然后对于一个 handler 函数, 我们定义了 ``LbdFuncConfig``, 但没有指定 timeout.

    1. 那么我们会去 module 级别寻找 __func_config__ 属性, 如果在 module 级压根没有被定义,
    那么去更上一层的 package 中的 __func_config__ 属性寻找, 直到找到为止.
    2. 如果直到最顶层的 package 中都没有找到, 那么最后检查这个值, 如果是 REQUIRED, 就报错.

    如果我们指定了 timeout, 那么以我们的指定值为准, 忽略上层 module 中的定义值.
    """
    for py_current_module, py_parent_module, py_handler_func in walk_lbd_handler(
            module_name, valid_func_name_list):

        current_module_config = py_current_module.__dict__.get(
            config_field, config_class()
        )  # type: BaseConfig

        try:
            parent_module_config = py_parent_module.__dict__.get(
                config_field, config_class()
            )  # type: BaseConfig
        except:
            parent_module_config = config_class()

        current_module_config.absorb(parent_module_config)
        setattr(py_current_module, config_field, current_module_config)

        if py_handler_func is not None:
            py_handler_func_config = py_handler_func.__dict__.get(
                config_field, config_class()
            )  # type: BaseConfig
            py_handler_func_config.absorb(current_module_config)
            setattr(py_handler_func, config_field, py_handler_func_config)
