# -*- coding: utf-8 -*-

from .apigw import HttpMethod

DEFAULT_LBD_HANDLER_FUNC_NAME = "handler"
VALID_LBD_HANDLER_FUNC_NAME_LIST = HttpMethod.get_all_valid_func_name() + [DEFAULT_LBD_HANDLER_FUNC_NAME, ]
