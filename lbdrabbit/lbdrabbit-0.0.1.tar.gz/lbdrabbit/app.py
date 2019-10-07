# -*- coding: utf-8 -*-

from picage import Package
from configirl import Constant, Derivable, ConfigClass
from .lbd_func_config import (
    walk_lbd_handler,
    config_inherit_handler,
    DEFAULT_LBD_FUNC_CONFIG_FIELD, LbdFuncConfig, lbd_func_config_value_handler
)
from .apigw import HttpMethod
from .const import VALID_LBD_HANDLER_FUNC_NAME_LIST, DEFAULT_LBD_HANDLER_FUNC_NAME
from importlib import import_module
from troposphere_mate import Template


class AppConfig(ConfigClass):
    METADATA = Constant(default=dict())

    PROJECT_NAME = Constant()
    PROJECT_NAME_SLUG = Derivable()

    @PROJECT_NAME_SLUG.getter
    def get_project_name_slug(self):
        return self.PROJECT_NAME.get_value().replace("_", "-")

    STAGE = Constant()  # example dev / test / prod

    ENVIRONMENT_NAME = Derivable()

    @ENVIRONMENT_NAME.getter
    def get_ENVIRONMENT_NAME(self):
        return "{}-{}".format(self.PROJECT_NAME_SLUG.get_value(self), self.STAGE.get_value())

    HANDLER_MODULE_NAME = Constant()
    """
    The root path of the lambda handler folder. lbdrabbit automatically create
    lambda function for each sub module
    """

    @HANDLER_MODULE_NAME.validator
    def check_HANDLER_MODULE_NAME(self, value):
        from importlib import import_module
        import_module(value)

    S3_BUCKET_FOR_DEPLOY = Constant()
    """
    A prerequisite for deployment. Need to be manually created. Recommended
    bucket name would be ``{account_id}-for-everything``.
    """

    AWS_PROFILE_FOR_DEPLOY = Constant()
    """
    The AWS profile name used for your local machine to deploy cloudformation. 
    """

    AWS_PROFILE_FOR_BOTO3 = Derivable()

    @AWS_PROFILE_FOR_BOTO3.getter
    def get_AWS_PROFILE_FOR_BOTO3(self):
        if self.is_aws_lambda_runtime():
            return None
        else:
            return self.AWS_PROFILE_FOR_DEPLOY.get_value()

    LAMBDA_CODE_S3_KEY = Constant()
    LAMBDA_CODE_S3_BUCKET = Constant()
    LAMBDA_LAYER_ARN = Constant()

    STACK_NAME = Derivable()

    @STACK_NAME.getter
    def get_STACK_NAME(self):
        return self.ENVIRONMENT_NAME.get_value()

    # --- lbdrabbit framework related ---
    DEFAULT_LBD_FUNC_CONFIG_FIELD = Constant(default=DEFAULT_LBD_FUNC_CONFIG_FIELD)
    DEFAULT_LBD_HANDLER_FUNC_NAME = Constant(default=DEFAULT_LBD_HANDLER_FUNC_NAME)
    VALID_LBD_HANDLER_FUNC_NAME_LIST = Constant(default=VALID_LBD_HANDLER_FUNC_NAME_LIST)


class App(object):
    def __init__(self,
                 import_name: str,
                 app_config: AppConfig = None):
        self.import_name = import_name

        if app_config is None:
            app_config = AppConfig()

        self.config = app_config
        self.cf_tpl = None  # type: Template

    def inherit_lbd_func_config(self):
        config_inherit_handler(
            module_name=self.config.HANDLER_MODULE_NAME.get_value(),
            config_field=DEFAULT_LBD_FUNC_CONFIG_FIELD,
            config_class=LbdFuncConfig,
            valid_func_name_list=VALID_LBD_HANDLER_FUNC_NAME_LIST,
        )

    def derive_lbd_func_config_value(self):
        lbd_func_config_value_handler(
            module_name=self.config.HANDLER_MODULE_NAME.get_value(),
            config_field=DEFAULT_LBD_FUNC_CONFIG_FIELD,
            config_class=LbdFuncConfig,
            valid_func_name_list=VALID_LBD_HANDLER_FUNC_NAME_LIST,
            default_lbd_handler_name=DEFAULT_LBD_HANDLER_FUNC_NAME,
        )

    def create_cf_template(self):
        root_module = Package(self.config.HANDLER_MODULE_NAME.get_value())
        # sub_packages = list(root_module.sub_packages.values())
        # sub_modules = list(root_module.sub_modules.values())
        #
        # py_module = import_module(root_module.fullname)
        # print(current_pkg)

        for py_current_module, py_parent_module, py_handler_func in walk_lbd_handler(
                self.config.HANDLER_MODULE_NAME.get_value(), VALID_LBD_HANDLER_FUNC_NAME_LIST):
            if py_handler_func is not None:
                lbd_func_config = getattr(py_handler_func,
                                          self.config.DEFAULT_LBD_FUNC_CONFIG_FIELD.get_value())  # type: LbdFuncConfig
                lbd_func_config.create_aws_resource(template=template)

                # print(py_current_module.__name__)

    def deploy(self):
        self.inherit_lbd_func_config()
        self.derive_lbd_func_config_value()
        self.create_cf_template()
