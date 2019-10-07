# -*- coding: utf-8 -*-

import typing
import attr
import string
from importlib import import_module
from picage import Package
from constant2 import Constant
from troposphere_mate import Template, Parameter, Tags, Ref, GetAtt, Sub, ImportValue
from troposphere_mate import awslambda, apigateway, iam, events, s3
from troposphere_mate import slugify, camelcase, helper_fn_sub
from troposphere_mate import AWS_ACCOUNT_ID

from .base import BaseConfig, REQUIRED, NOTHING, walk_lbd_handler
from ..pkg.fingerprint import fingerprint

DEFAULT_LBD_FUNC_CONFIG_FIELD = "__lbd_func_config__"


@attr.s
class LbdFuncConfig(BaseConfig):
    """
    Lambda Function Level Config.

    Every child function under a resource inherits :class:`ResourceConfig``.


    :param apigw_authorizer_yes: indicate if this lambda function is used
        as a custom authorizer.

    **中文文档**



    **设计**

    - something_aws_object: 以 aws_object 结尾的 property 方法, 返回的是一个具体的
        ``troposphere_mate.AWSObject`` 对象
    - pre_exam
    - create_something: 以 create 开头的方法会调用响应的 something_aws_object
        方法, 不过在那之前,


    **生成 AWS Object 的设计模式**

    比如, 我们有一个 property method 叫做 lbd_func_aws_object 用于生成
    ``troposphere_mate.awslambda.Function`` 对象. 而对应的 AWS Resource 名称
    则是 lbd_func, 这里我们用 <aws_resource_name> 来表示.

    1. ``_<aws_resource_name>_aws_object_cache = attr.ib(default=NOTHING)`` 用于缓存
    2. ``def <aws_resource_name>_aws_object_pre_check(self)`` 函数, 用于检查是否满足创建
    ``<aws_resource_name>_aws_object`` 的条件. 如果不满足, 则抛出对应异常, 并给出详细信息.
    3. ``def <aws_resource_name>_aws_object_ready(self)`` 函数, 返回一个布尔值, 表示是否满足
    创建 ``<aws_resource_name>_aws_object`` 的条件. 不抛出任何异常.
    4. ``<aws_resource_name>_yes = attr.ib(default=NOTHING)``, 用于手动开启和关闭
    该资源的生成. 例如我们手动关闭了, 就算之前的条件检查函数判定满足, 我们依然不会创建之.
    如果我们手动开启了, 如果条件检查不满足, 那么我们还是不会创建之.

    """
    param_env_name = attr.ib(default=REQUIRED)  # type: Parameter

    lbd_func_yes = attr.ib(default=REQUIRED)  # type: str
    lbd_func_name = attr.ib(default=REQUIRED)  # type: str
    lbd_func_description = attr.ib(default=NOTHING)  # type: str
    lbd_func_memory_size = attr.ib(default=NOTHING)  # type: int
    lbd_func_iam_role = attr.ib(default=REQUIRED)  # type: typing.Union[iam.Role, Ref, GetAtt, Parameter, str]
    lbd_func_timeout = attr.ib(default=NOTHING)  # type: int
    lbd_func_runtime = attr.ib(default=REQUIRED)  # type: str
    lbd_func_code = attr.ib(default=REQUIRED)  # type: awslambda.Code
    lbd_func_layers = attr.ib(default=NOTHING)  # type: list
    lbd_func_reserved_concurrency = attr.ib(default=NOTHING)  # type: int
    lbd_func_environment_vars = attr.ib(default=NOTHING)  # type: awslambda.Environment
    lbd_func_kms_key_arn = attr.ib(default=NOTHING)  # type: str
    lbd_func_vpc_config = attr.ib(default=NOTHING)  # type: awslambda.VPCConfig
    lbd_func_dead_letter_config = attr.ib(default=NOTHING)  # type: awslambda.DeadLetterConfig
    lbd_func_tracing_config = attr.ib(default=NOTHING)  # type: awslambda.TracingConfig

    _lbd_func_aws_object_cache = attr.ib(default=NOTHING)  # type: awslambda.Function

    lbd_func_metadata = attr.ib(default=NOTHING)  # type: dict
    lbd_func_tags = attr.ib(default=NOTHING)  # type: Tags

    apigw_resource_yes = attr.ib(default=NOTHING)  # type: bool
    apigw_restapi = attr.ib(default=NOTHING)  # type: apigateway.RestApi
    _apigw_resource_aws_object_cache = attr.ib(default=NOTHING)  # type: apigateway.Resource

    # apigateway.Method related
    class ApiMethodIntType(Constant):
        rest = "rest"
        rpc = "rpc"
        html = "html"

    class ApigwMethodAuthorizationType(Constant):
        none = "NONE"
        aws_iam = "AWS_IAM"
        custom = "CUSTOM"
        cognito_user_pools = "COGNITO_USER_POOLS"

    apigw_method_yes = attr.ib(default=NOTHING)  # type: bool
    apigw_method_int_type = attr.ib(default=NOTHING)  # type: str
    _apigw_method_aws_object_cache = attr.ib(default=NOTHING)  # type: apigateway.Method
    _apigw_method_lbd_permission_aws_object_cache = attr.ib(default=NOTHING)  # type: awslambda.Permission

    apigw_method_int_passthrough_behavior = attr.ib(default=NOTHING)  # type: str
    apigw_method_int_timeout_in_milli = attr.ib(default=NOTHING)  # type: int
    apigw_method_authorization_type = attr.ib(default=NOTHING)  # type: str
    apigw_method_authorizer = attr.ib(
        default=NOTHING)  # type: typing.Union[apigateway.Authorizer, Ref, GetAtt, ImportValue, Parameter, str]

    apigw_method_enable_cors_yes = attr.ib(default=NOTHING)  # type: str
    apigw_method_enable_cors_access_control_allow_origin = attr.ib(default=NOTHING)  # type: str
    apigw_method_enable_cors_access_control_allow_headers = attr.ib(default=NOTHING)  # type: str
    _apigw_method_options_for_cors_aws_object_cache = attr.ib(default=NOTHING)  # type: apigateway.Method

    apigw_authorizer_yes = attr.ib(default=NOTHING)  # type: bool
    apigw_authorizer_name = attr.ib(default=NOTHING)  # type: bool
    apigw_authorizer_token_type_header_field = attr.ib(default=NOTHING)  # type: bool

    _apigw_authorizer_aws_object_cache = attr.ib(default=NOTHING)  # type: apigateway.Authorizer
    _apigw_authorizer_lbd_permission_aws_object_cache = attr.ib(default=NOTHING)  # type: awslambda.Permission

    scheduled_job_yes = attr.ib(default=NOTHING)  # type: bool
    scheduled_job_expression = attr.ib(default=NOTHING)  # type: typing.Union[str, typing.List[str]]
    _scheduled_job_event_rule_aws_objects_cache = attr.ib(default=NOTHING)  # type: typing.Dict[str, events.Rule]
    _scheduled_job_event_lbd_permission_aws_objects_cache = attr.ib(
        default=NOTHING)  # type: typing.Dict[str, awslambda.Permission]

    boto3_ses = attr.ib(default=NOTHING)

    # Implementation related private functions
    def _ready_checker_shortener(self, res_name):
        """
        Implementation use helper function for ``<resource_name>_aws_object_ready``
        method.

        :type res_name: str
        :param res_name: resource name. For example: awslambda.Function is
            lbd_func

        :rtype: bool
        """
        try:
            if getattr(self, "{}_yes".format(res_name)) is not True:
                return False
        except:
            pass
        try:
            getattr(self, "{}_aws_object_pre_check".format(res_name))()
            return True
        except:
            return False

    # S3 Event Trigger

    @attr.s
    class S3EventLambdaConfig(object):
        event = attr.ib(default=NOTHING)
        filter = attr.ib(default=NOTHING)

        class EventEnum(Constant):
            created = "s3:ObjectCreated:*"
            created_put = "s3:ObjectCreated:Put"
            created_post = "s3:ObjectCreated:Post"
            created_copy = "s3:ObjectCreated:Copy"
            created_multipart_upload = "s3:ObjectCreated:CompleteMultipartUpload"

            removed = "s3:ObjectRemoved:*"
            removed_delete = "s3:ObjectRemoved:Delete"
            removed_delete_marker_created = "s3:ObjectRemoved:DeleteMarkerCreated"

            restore = "s3:ObjectRestore:Post"
            restore_completed = "s3:ObjectRestore:Completed"

            reduced_redundancy_lost_object = "s3:ReducedRedundancyLostObject"

    s3_event_bucket_basename = attr.ib(default=NOTHING)  # type: str

    @property
    def s3_event_bucket_logic_id(self):
        """
        logic id for ``s3.Bucket`` of the Lambda Event Mapping S3 Bucket.

        :rtype: str
        """
        if self.s3_event_bucket_basename is NOTHING:
            raise TypeError
        if isinstance(self.s3_event_bucket_basename, str):
            return "S3Bucket{}".format(camelcase(self.s3_event_bucket_basename))
        else:
            raise TypeError

    @property
    def s3_event_bucket_name_for_cf(self) -> typing.Union[str, Sub]:
        """
        ``s3.Bucket.BucketName`` field value. ``AWS::AccountId`` is included as
        prefix.

        :rtype: Sub

        **中文文档**

        生成存储桶的名称. 由于存储桶的名字是全球唯一的, 并且不分 Region, 所以需要加上
        AWS Account Id 作为名字的前缀, 以避免冲突.
        """
        if self.s3_event_bucket_basename is NOTHING:
            raise TypeError
        if isinstance(self.s3_event_bucket_basename, str):
            return Sub(
                "${AccountId}-${EnvName}-${BucketBasename}",
                {
                    "AccountId": Ref(AWS_ACCOUNT_ID),
                    "EnvName": Ref(self.param_env_name),
                    "BucketBasename": self.s3_event_bucket_basename,
                },
            )
        else:
            raise TypeError

    s3_event_lbd_config_list = attr.ib(default=NOTHING)  # type: typing.List[LbdFuncConfig.S3EventLambdaConfig]

    @property
    def s3_notification_configuration_aws_property(self):
        s3_notification_configuration = s3.NotificationConfiguration()
        if self.s3_event_lbd_config_list is not NOTHING:
            if isinstance(self.s3_event_lbd_config_list, list):
                s3_notification_configuration.LambdaConfigurations = [
                    s3.LambdaConfigurations(
                        Event=s3_event_lbd_config.event,
                        Function=GetAtt(self.lbd_func_aws_object, "Arn"),
                        Filter=s3_event_lbd_config.filter,
                    )
                    for s3_event_lbd_config in self.s3_event_lbd_config_list
                ]

        return s3_notification_configuration

    s3_event_bucket_yes = attr.ib(default=NOTHING)

    def s3_event_bucket_aws_object_pre_check(self):
        if self.s3_event_lbd_config_list is NOTHING:
            raise ValueError(
                ("{}.s3_event_lbd_config_list has to be a list of "
                 "LbdFuncConfig.S3EventLambdaConfig object").format(
                    self.identifier
                )
            )
        if isinstance(self.s3_event_lbd_config_list, list):
            if len(self.s3_event_lbd_config_list) == 0:
                raise ValueError(
                    "{}.s3_event_lbd_config_list can't be a empty list!" \
                        .format(self.identifier)
                )

    def s3_event_bucket_aws_object_ready(self) -> bool:
        return self._ready_checker_shortener("s3_event_bucket")

    _s3_event_bucket_aws_object_cache = attr.ib(default=NOTHING)  # type: s3.Bucket

    @property
    def s3_event_bucket_aws_object(self) -> s3.Bucket:
        if self._s3_event_bucket_aws_object_cache is NOTHING:
            s3_bucket = s3.Bucket(
                self.s3_event_bucket_logic_id,
                BucketName=self.s3_event_bucket_name_for_cf,
            )
            s3_bucket.NotificationConfiguration = self.s3_notification_configuration_aws_property
            self._s3_event_bucket_aws_object_cache = s3_bucket
        return self._s3_event_bucket_aws_object_cache

    _s3_event_bucket_lbd_permission_aws_object_cache = attr.ib(default=NOTHING) # type: awslambda.Permission

    def s3_event_bucket_lbd_permission_aws_object_pre_check(self):
        self.s3_event_bucket_aws_object_pre_check()

    def s3_event_bucket_lbd_permission_aws_object_ready(self):
        return self._ready_checker_shortener("s3_event_bucket_lbd_permission")

    @property
    def s3_event_bucket_lbd_permission_aws_object(self) -> awslambda.Permission:
        if self._s3_event_bucket_lbd_permission_aws_object_cache is NOTHING:
            s3_event_bucket_lbd_permission_logic_id = "LbdPermission{}".format(self.s3_event_bucket_logic_id)
            s3_event_bucket_lbd_permission = awslambda.Permission(
                title=s3_event_bucket_lbd_permission_logic_id,
                Action="lambda:InvokeFunction",
                FunctionName=GetAtt(self.lbd_func_aws_object, "Arn"),
                Principal="s3.amazonaws.com",
                SourceArn=GetAtt(self.s3_event_bucket_aws_object, "Arn"),
                DependsOn=[
                    self.s3_event_bucket_aws_object,
                    self.lbd_func_aws_object,
                ]
            )
            self._s3_event_bucket_lbd_permission_aws_object_cache = s3_event_bucket_lbd_permission
        return self._s3_event_bucket_lbd_permission_aws_object_cache

    _root_module_name = attr.ib(default=NOTHING)
    _py_module = attr.ib(default=NOTHING)
    _py_function = attr.ib(default=NOTHING)
    _py_parent_module = attr.ib(default=NOTHING)

    _default = dict(
        lbd_func_yes=True,
        memory_size=128,
        timeout=3,
        apigw_resource_yes=False,
        apigw_method_yes=False,
        apigw_method_int_passthrough_behavior="WHEN_NO_MATCH",
        apigw_method_int_timeout_in_milli=29000,
        apigw_authorizer_yes=False,
        apigw_authorizer_token_type_header_field="auth",
    )

    @property
    def identifier(self) -> str:
        try:
            return "{}.{}.{}".format(
                self._py_module.__name__, self._py_function.__name__, DEFAULT_LBD_FUNC_CONFIG_FIELD
            )
        except:
            return "{}.{}".format(
                self._py_module.__name__, DEFAULT_LBD_FUNC_CONFIG_FIELD
            )

    @property
    def parent_config(self) -> 'LbdFuncConfig':
        """
        Access the parent lambda function config.
        """
        # it is a module level config
        if self._py_function is NOTHING:
            return getattr(self._py_parent_module, DEFAULT_LBD_FUNC_CONFIG_FIELD)
        # it is a function level config
        else:
            return getattr(self._py_parent_module, DEFAULT_LBD_FUNC_CONFIG_FIELD)

    @property
    def rel_module_name(self) -> str:
        """
        Relative module name, compared to the root module

        For example, if the root module is ``"a.b"``, and this module is ``"a.b.c.d"``,
        then the relative module name is ``"c.d"``; if this module is ``"a.b"``,
        then the relative module name is ``""``
        """
        rel_module_name = self._py_module.__name__.replace(self._root_module_name, "")
        if rel_module_name.startswith("."):
            rel_module_name = rel_module_name[1:]
        return rel_module_name

    def is_module(self):
        if self._py_function is NOTHING:
            return True
        else:
            return False

    def is_function(self):
        if self._py_function is NOTHING:
            return False
        else:
            return True

    @property
    def lbd_func_logic_id(self) -> str:
        return "LbdFunc{}".format(
            camelcase(self.rel_module_name.replace(".", "-")) + camelcase(self._py_function.__name__)
        )

    @property
    def lbd_func_iam_role_arn(self):
        if isinstance(self.lbd_func_iam_role, iam.Role):  # a troposphere_mate IAM Role object
            return GetAtt(self.lbd_func_iam_role, "Arn")
        elif isinstance(self.lbd_func_iam_role,
                        (Ref, GetAtt)):  # reference of a parameter or get attribute instrinct function
            return self.lbd_func_iam_role
        elif isinstance(self.lbd_func_iam_role, Parameter):  # a parameter represent a iam role ARN
            return Ref(self.lbd_func_iam_role)
        elif isinstance(self.lbd_func_iam_role, str):  # an ARN string
            return self.lbd_func_iam_role
        else:
            raise TypeError(
                "{}.lbd_func_iam_role has to be one of "
                "troposphere_mate.iam.Role, "
                "Ref of a Parameter, "
                "GetAtt of a troposphere_mate.iam.Role, "
                "a Parameter represent a iam role ARN, "
                "a string represent a iam role ARN".format(self.identifier))

    def lbd_func_aws_object_pre_check(self):
        if callable(self._py_function):
            try:
                self._py_function.__name__
            except AttributeError:
                raise TypeError("{}.{} is not a valid function".format(self._py_module.__name__, self._py_function))
            if self.lbd_func_code is NOTHING:
                raise ValueError(
                    "{}.lbd_func_code is not valid!".format(self.identifier)
                )
            if self.lbd_func_runtime is NOTHING:
                raise ValueError(
                    "{}.lbd_func_runtime is not valid!".format(self.identifier)
                )
        else:
            raise TypeError("{}.{} is not a valid function".format(self._py_module.__name__, self._py_function))

    def lbd_func_aws_object_ready(self):
        return self._ready_checker_shortener("lbd_func")

    @property
    def lbd_func_aws_object(self) -> awslambda.Function:
        if self._lbd_func_aws_object_cache is NOTHING:
            lbd_func = awslambda.Function(
                self.lbd_func_logic_id,
                FunctionName=helper_fn_sub("{}-%s" % self.lbd_func_name, self.param_env_name),
                Handler="{}.{}".format(self._py_module.__name__, self._py_function.__name__),
                Code=self.lbd_func_code,
                Role=self.lbd_func_iam_role_arn,
                Runtime=self.lbd_func_runtime,
            )
            if self.lbd_func_memory_size is not NOTHING:
                lbd_func.MemorySize = self.lbd_func_memory_size
            if self.lbd_func_timeout is not NOTHING:
                lbd_func.Timeout = self.lbd_func_timeout
            if self.lbd_func_layers is not NOTHING:
                lbd_func.Layers = self.lbd_func_layers
            if self.lbd_func_reserved_concurrency is not NOTHING:
                lbd_func.ReservedConcurrentExecutions = self.lbd_func_reserved_concurrency
            if self.lbd_func_environment_vars is not NOTHING:
                lbd_func.Environment = self.lbd_func_environment_vars
            if self.lbd_func_kms_key_arn is not NOTHING:
                lbd_func.KmsKeyArn = self.lbd_func_kms_key_arn
            if self.lbd_func_vpc_config is not NOTHING:
                lbd_func.VpcConfig = self.lbd_func_vpc_config
            if self.lbd_func_dead_letter_config is not NOTHING:
                lbd_func.DeadLetterConfig = self.lbd_func_dead_letter_config
            if self.lbd_func_tracing_config is not NOTHING:
                lbd_func.TracingConfig = self.lbd_func_tracing_config

            self._lbd_func_aws_object_cache = lbd_func

        return self._lbd_func_aws_object_cache

    @property
    def apigw_resource_logic_id(self) -> str:
        """
        Api Gateway Resource Logic Id is Full Resource Path in Camelcase format
        with a Prefix.
        """
        return "ApigwResource{}".format(
            camelcase(self.rel_module_name.replace(".", "-")))

    @property
    def apigw_resource_parent_id(self) -> typing.Union[Ref, GetAtt]:
        # it is the root module, use RootResourceId as parent id
        if ("." not in self.rel_module_name) and bool(self.rel_module_name):
            return GetAtt(self.apigw_restapi, "RootResourceId")
        else:
            return Ref(self.parent_config.apigw_resource_aws_object)

    @property
    def apigw_resource_path_part(self) -> str:
        """
        The file name (without .py extension) of current module becomes
        api gateway resource.
        """
        return slugify(self._py_module.__name__.split(".")[-1])

    @property
    def apigw_resource_full_path(self) -> str:
        """
        if current_module = lbdrabbit.examples.handlers.rest.users.py,
        root_module = lbdrabbit.examples.handlers

        then the api gateway resource full path should be
        ``rest/users``
        """
        return "/".join([
            slugify(fname)
            for fname in self.rel_module_name.split(".")
        ])

    def apigw_resource_aws_object_pre_check(self):
        """

        **中文文档**

        检查根据当前的设置, 是否满足自动创建 troposphere_mate.apigateway.Resource 的条件

        - LbdFuncConfig._py_function 必须为 None, 因为如果当前绑定了一个函数,
            说明我们需要的是 Api Method 而不是 Api Resource
        - LbdFuncConfig.apigw_restapi 必须被指定.
        """
        if not self.rel_module_name:
            raise ValueError("can't create root resource!")

        if self._py_function is not NOTHING:
            raise ValueError("to create a apigateway.Resource, "
                             "the config should not bound with a python function!")

        if self.apigw_restapi is NOTHING:
            raise ValueError("to create a apigateway.Resource, "
                             "LbdFuncConfig.apigw_restapi has to be specified")

    def apigw_resource_aws_object_ready(self):
        return self._ready_checker_shortener("apigw_resource")

    @property
    def apigw_resource_aws_object(self) -> apigateway.Resource:
        if self._apigw_resource_aws_object_cache is NOTHING:
            apigw_resource = apigateway.Resource(
                self.apigw_resource_logic_id,
                RestApiId=Ref(self.apigw_restapi),
                ParentId=self.apigw_resource_parent_id,
                PathPart=self.apigw_resource_path_part,
                DependsOn=[self.apigw_restapi],
            )
            self._apigw_resource_aws_object_cache = apigw_resource
        return self._apigw_resource_aws_object_cache

    @property
    def apigw_method_logic_id(self) -> str:
        return "ApigwMethod{}".format(
            camelcase(self.rel_module_name.replace(".", "-")) + camelcase(self._py_function.__name__)
        )

    def check_apigw_method_authorization_type(self):
        allowed_values = ["NONE", "AWS_IAM", "CUSTOM", "COGNITO_USER_POOLS"]
        if self.apigw_method_authorization_type.upper() not in allowed_values:
            raise ValueError(
                "{}.apigw_method_authorization_type can only be one of {}". \
                    format(self.identifier, allowed_values)
            )

    def check_apigw_method_int_type(self):
        if self.apigw_method_int_type not in self.ApiMethodIntType.Values():
            raise ValueError(
                "{}.apigw_method_int_type can only be one of {}". \
                    format(self.identifier, self.ApiMethodIntType.Values())
            )

    @property
    def apigw_method_http_method(self):
        if self.apigw_method_int_type == self.ApiMethodIntType.rest:
            return self._py_function.__name__.upper()
        elif self.apigw_method_int_type == self.ApiMethodIntType.rpc:
            return "POST"
        elif self.apigw_method_int_type == self.ApiMethodIntType.html:
            return "GET"
        else:
            return "POST"

    @property
    def apigw_method_use_authorizer_yes(self) -> bool:
        """
        Test if this Api Method need an Authorizer.

        :rtype: bool
        """
        if isinstance(self.apigw_method_authorization_type, str):
            if self.apigw_method_authorization_type.upper() == self.ApigwMethodAuthorizationType.none:
                return False
            if self.apigw_method_authorization_type.upper() in self.ApigwMethodAuthorizationType.Values():
                return True
        return False

    @property
    def apigw_method_authorizer_id_for_cf(self):
        """
        Resolve the value that will be assigned to ``apigateway.Method.AuthorizerId``
        property.
        """
        if self.apigw_method_authorizer is NOTHING:
            raise TypeError
        if isinstance(self.apigw_method_authorizer, (apigateway.Authorizer, Parameter)):
            return Ref(self.apigw_method_authorizer)
        elif isinstance(self.apigw_method_authorizer, (Ref, GetAtt, ImportValue)):
            return self.apigw_method_authorizer
        elif isinstance(self.apigw_method_authorizer, str):
            # hard coded authorizer id (from console)
            if len(self.apigw_method_authorizer) \
                    and len(set(self.apigw_method_authorizer) \
                                    .difference(set(string.ascii_lowercase + string.digits))):
                return self.apigw_method_authorizer
            # hard coded apigateway.Authorizer logic id
            else:
                return Ref(self.apigw_method_authorizer)
        else:
            raise TypeError

    def apigw_method_aws_object_pre_check(self):
        """
        **中文文档**

        检查根据当前的设置, 是否满足自动创建 troposphere_mate.apigateway.Method 的条件

        - LbdFuncConfig._py_function 必须为Python函数, 不然没有LambdaFunction支持,
            Api Method 就无法工作.
        - LbdFuncConfig.apigw_restapi 必须被指定.
        """
        if self._py_function is NOTHING:
            raise ValueError("to create a apigateway.Method, "
                             "the config must be bound with a python function!")

        if self.apigw_restapi is NOTHING:
            raise ValueError("to create a apigateway.Resource, "
                             "LbdFuncConfig.apigw_restapi has to be specified")

    def apigw_method_aws_object_ready(self):
        return self._ready_checker_shortener("apigw_method")

    @property
    def apigw_method_aws_object(self) -> apigateway.Method:
        if self._apigw_method_aws_object_cache is NOTHING:
            depends_on = [
                self.apigw_resource_aws_object,
                self.lbd_func_aws_object,
            ]

            # Integration Request
            request_template = {"application/json": "$input.json('$')"}

            # Integration Response
            if self.apigw_method_int_type == self.ApiMethodIntType.html:
                integration_response_200 = apigateway.IntegrationResponse(
                    StatusCode="200",
                    ResponseParameters={
                        "method.response.header.Access-Control-Allow-Origin": "'*'",
                        "method.response.header.Content-Type": "'text/html'"
                    },
                    ResponseTemplates={"text/html": "$input.path('$')"},
                )
                method_response_200 = apigateway.MethodResponse(
                    StatusCode="200",
                    ResponseParameters={
                        "method.response.header.Access-Control-Allow-Origin": False,
                        "method.response.header.Content-Type": False,
                    },
                    ResponseModels={"application/json": "Empty"},
                )
            elif self.apigw_method_int_type == self.ApiMethodIntType.rpc:
                integration_response_200 = apigateway.IntegrationResponse(
                    StatusCode="200",
                    ContentHandling="CONVERT_TO_TEXT",
                    ResponseParameters={},
                    ResponseTemplates={"application/json": ""}
                )
                method_response_200 = apigateway.MethodResponse(
                    StatusCode="200",
                    ResponseParameters={},
                    ResponseModels={"application/json": "Empty"},
                )
            elif self.apigw_method_int_type == self.ApiMethodIntType.rest:
                integration_response_200 = apigateway.IntegrationResponse(
                    StatusCode="200",
                    ContentHandling="CONVERT_TO_TEXT",
                    ResponseParameters={},
                    ResponseTemplates={"application/json": ""}
                )
                method_response_200 = apigateway.MethodResponse(
                    StatusCode="200",
                    ResponseParameters={},
                    ResponseModels={"application/json": "Empty"},
                )
            else:
                raise TypeError

            integration_responses = [
                integration_response_200,
            ]

            integration = apigateway.Integration(
                Type="AWS",
                IntegrationHttpMethod="POST",
                Uri=Sub(
                    "arn:aws:apigateway:${Region}:lambda:path/2015-03-31/functions/${LambdaArn}/invocations",
                    {
                        "Region": {"Ref": "AWS::Region"},
                        "LambdaArn": GetAtt(self.lbd_func_aws_object, "Arn"),
                    }
                ),
                RequestTemplates=request_template,
                IntegrationResponses=integration_responses,
            )

            if self.apigw_method_int_passthrough_behavior is not NOTHING:
                integration.PassthroughBehavior = self.apigw_method_int_passthrough_behavior
            if self.apigw_method_int_timeout_in_milli is not NOTHING:
                integration.TimeoutInMillis = self.apigw_method_int_timeout_in_milli

            # Method Response
            method_responses = [
                method_response_200,
            ]

            if self.apigw_method_enable_cors_yes is True:
                for integration_response in integration.IntegrationResponses:
                    integration_response.ResponseParameters[
                        "method.response.header.Access-Control-Allow-Origin"] = "'*'"

                for method_response in method_responses:
                    method_response.ResponseParameters["method.response.header.Access-Control-Allow-Origin"] = False

            self.check_apigw_method_authorization_type()
            self.check_apigw_method_int_type()

            apigw_method = apigateway.Method(
                title=self.apigw_method_logic_id,
                RestApiId=Ref(self.apigw_restapi),
                ResourceId=Ref(self.apigw_resource_aws_object),
                AuthorizationType=self.apigw_method_authorization_type,
                HttpMethod=self.apigw_method_http_method,
                MethodResponses=method_responses,
                Integration=integration,
            )

            if self.apigw_method_use_authorizer_yes:
                apigw_method.AuthorizerId = Ref(self.apigw_method_authorizer)
                depends_on.append(self.apigw_method_authorizer)

            apigw_method.DependsOn = depends_on

            self._apigw_method_aws_object_cache = apigw_method

        return self._apigw_method_aws_object_cache

    def apigw_method_lbd_permission_aws_object_pre_check(self):
        self.apigw_method_aws_object_pre_check()
        self.lbd_func_aws_object_pre_check()

    def apigw_method_lbd_permission_aws_object_ready(self):
        return self.apigw_method_aws_object_ready() and self.lbd_func_aws_object_ready()

    @property
    def apigw_method_lbd_permission_aws_object(self) -> awslambda.Permission:
        if self._apigw_method_lbd_permission_aws_object_cache is NOTHING:
            apigw_method_lbd_permission_logic_id = "LbdPermission{}".format(self.apigw_method_logic_id)
            apigw_method_lbd_permission = awslambda.Permission(
                title=apigw_method_lbd_permission_logic_id,
                Action="lambda:InvokeFunction",
                FunctionName=GetAtt(self.lbd_func_aws_object, "Arn"),
                Principal="apigateway.amazonaws.com",
                SourceArn=Sub(
                    "arn:aws:execute-api:${Region}:${AccountId}:${RestApiId}/*/%s/%s" % \
                    (
                        self.apigw_method_http_method,
                        self.apigw_resource_full_path
                    ),
                    {
                        "Region": {"Ref": "AWS::Region"},
                        "AccountId": {"Ref": "AWS::AccountId"},
                        "RestApiId": Ref(self.apigw_restapi),
                    }
                ),
                DependsOn=[
                    self.apigw_method_aws_object,
                    self.lbd_func_aws_object,
                ]
            )
            self._apigw_method_lbd_permission_aws_object_cache = apigw_method_lbd_permission
        return self._apigw_method_lbd_permission_aws_object_cache

    def apigw_method_options_for_cors_aws_object_pre_check(self):
        if self._py_function is NOTHING:
            raise ValueError("to create a apigateway.Method, "
                             "the config must be bound with a python function!")

        if self.apigw_restapi is NOTHING:
            raise ValueError("to create a apigateway.Resource, "
                             "LbdFuncConfig.apigw_restapi has to be specified")

    def apigw_method_options_for_cors_aws_object_ready(self):
        if self.apigw_method_enable_cors_yes is not True:
            return False
        try:
            self.apigw_method_options_for_cors_aws_object_pre_check()
            return True
        except:
            return False

    @property
    def apigw_method_options_for_cors_aws_object(self) -> apigateway.Method:
        """

        **中文文档**

        为了开启 Cors, 对于 Api Resource 是需要一个 Options Method 专门用于获取
        服务器的设置. 这事因为浏览器在检查到跨站请求时, 会使用 Options 方法获取服务器的
        跨站访问设置, 如果不满则, 浏览爱则会返回错误信息.
        """
        # For cors, options method doesn't need a lambda function
        depends_on = [
            self.apigw_resource_aws_object,
        ]

        # Integration Request
        request_template = {"application/json": "{\"statusCode\": 200}"}

        # Integration Response
        access_control_allow_headers = "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token"

        if self.apigw_method_authorizer is not NOTHING:
            if self.apigw_authorizer_token_type_header_field is not NOTHING:
                access_control_allow_headers = access_control_allow_headers \
                                               + ",{}".format(self.apigw_authorizer_token_type_header_field)

        response_parameters = {
            "method.response.header.Access-Control-Allow-Origin": "'*'",
            "method.response.header.Access-Control-Allow-Methods": "'OPTIONS,GET,POST'",
            "method.response.header.Access-Control-Allow-Headers": "'{}'".format(
                access_control_allow_headers),
        }
        response_templates = {"application/json": ""}
        integration = apigateway.Integration(
            Type="MOCK",
            RequestTemplates=request_template,
            IntegrationResponses=[
                apigateway.IntegrationResponse(
                    StatusCode="200",
                    ContentHandling="CONVERT_TO_TEXT",
                    ResponseParameters=response_parameters,
                    ResponseTemplates=response_templates,
                )
            ],
            PassthroughBehavior="WHEN_NO_MATCH",
        )
        if self.apigw_method_int_passthrough_behavior is not NOTHING:
            integration.PassthroughBehavior = self.apigw_method_int_passthrough_behavior
        if self.apigw_method_int_timeout_in_milli is not NOTHING:
            integration.TimeoutInMillis = self.apigw_method_int_timeout_in_milli

        # Method Response
        method_responses = [
            apigateway.MethodResponse(
                StatusCode="200",
                ResponseModels={"application/json": "Empty"},
                ResponseParameters={
                    "method.response.header.Access-Control-Allow-Origin": False,
                    "method.response.header.Access-Control-Allow-Methods": False,
                    "method.response.header.Access-Control-Allow-Headers": False,
                }
            )
        ]

        apigw_method = apigateway.Method(
            title="ApigwMethod{}Options".format(
                camelcase(self.rel_module_name.replace(".", "-"))
            ),
            RestApiId=Ref(self.apigw_restapi),
            ResourceId=Ref(self.apigw_resource_aws_object),
            AuthorizationType="NONE",
            HttpMethod="OPTIONS",
            MethodResponses=method_responses,
            Integration=integration,
        )

        apigw_method.DependsOn = depends_on

        return apigw_method

    # apigateway.Authorizer related
    @classmethod
    def get_authorizer_id(cls, rel_module_name):
        return "ApigwAuthorizer{}".format(
            camelcase(rel_module_name.replace(".", "-"))
        )

    @property
    def apigw_authorizer_logic_id(self) -> str:
        return self.get_authorizer_id(self.rel_module_name)

    def apigw_authorizer_aws_object_pre_check(self):
        """
        **中文文档**

        检查根据当前的设置, 是否满足自动创建 troposphere_mate.apigateway.Authorizer 的条件

        目前只支持 CUSTOM 的 Lambda Authorizer

        - LbdFuncConfig._py_function 必须为Python函数, 不然没有LambdaFunction支持,
            Api Authorizer 就无法工作.
        - LbdFuncConfig.apigw_restapi 必须被指定.
        """
        if self._py_function is NOTHING:
            raise ValueError("to create a apigateway.Authorizer, "
                             "the config must be bound with a python function!")

        if self.apigw_restapi is NOTHING:
            raise ValueError("to create a apigateway.Resource, "
                             "LbdFuncConfig.apigw_restapi has to be specified")

    def apigw_authorizer_aws_object_ready(self):
        return self._ready_checker_shortener("apigw_authorizer")

    @property
    def apigw_authorizer_aws_object(self) -> apigateway.Authorizer:
        if self._apigw_authorizer_aws_object_cache is NOTHING:
            if self.apigw_authorizer_name is NOTHING:
                apigw_authorizer_name = self.apigw_authorizer_logic_id
            else:
                apigw_authorizer_name = self.apigw_authorizer_name

            if len(set(apigw_authorizer_name).difference(set(string.ascii_letters + string.digits))):
                raise ValueError(
                    "{}.apigw_authorizer_name can only have letter and digits".format(
                        self.identifier
                    )
                )
            apigw_authorizer = apigateway.Authorizer(
                title=self.apigw_authorizer_logic_id,
                Name=apigw_authorizer_name,
                RestApiId=Ref(self.apigw_restapi),
                AuthType="custom",
                Type="TOKEN",
                IdentitySource="method.request.header.{}".format(self.apigw_authorizer_token_type_header_field),
                AuthorizerResultTtlInSeconds=300,
                AuthorizerUri=Sub(
                    "arn:aws:apigateway:${Region}:lambda:path/2015-03-31/functions/${AuthorizerFunctionArn}/invocations",
                    {
                        "Region": {"Ref": "AWS::Region"},
                        "AuthorizerFunctionArn": GetAtt(self.lbd_func_aws_object, "Arn"),
                    }
                ),
                DependsOn=[
                    self.lbd_func_aws_object,
                    self.apigw_restapi,
                ]
            )
            self._apigw_authorizer_aws_object_cache = apigw_authorizer
        return self._apigw_authorizer_aws_object_cache

    def apigw_authorizer_lbd_permission_aws_object_pre_check(self):
        """
        **中文文档**

        检查根据当前的设置, 是否满足自动创建 troposphere_mate.awslambda.Permission 的条件
        """
        self.lbd_func_aws_object_pre_check()
        self.apigw_authorizer_aws_object_pre_check()

    def apigw_authorizer_lbd_permission_aws_object_ready(self):
        return self.apigw_authorizer_aws_object_ready() and self.lbd_func_aws_object_ready()

    @property
    def apigw_authorizer_lbd_permission_aws_object(self) -> awslambda.Permission:
        if self._apigw_authorizer_lbd_permission_aws_object_cache is NOTHING:
            apigw_authorizer_lbd_permission_logic_id = "LbdPermission{}".format(self.apigw_authorizer_logic_id)
            apigw_authorizer_lbd_permission = awslambda.Permission(
                title=apigw_authorizer_lbd_permission_logic_id,
                Action="lambda:InvokeFunction",
                FunctionName=GetAtt(self.lbd_func_aws_object, "Arn"),
                Principal="apigateway.amazonaws.com",
                SourceArn=Sub(
                    "arn:aws:execute-api:${Region}:${AccountId}:${RestApiId}/authorizers/${AuthorizerId}",
                    {
                        "Region": {"Ref": "AWS::Region"},
                        "AccountId": {"Ref": "AWS::AccountId"},
                        "RestApiId": Ref(self.apigw_restapi),
                        "AuthorizerId": Ref(self.apigw_authorizer_aws_object),
                    }
                ),
                DependsOn=[
                    self.apigw_authorizer_aws_object,
                    self.lbd_func_aws_object,
                ]
            )
            self._apigw_authorizer_lbd_permission_aws_object_cache = apigw_authorizer_lbd_permission
        return self._apigw_authorizer_lbd_permission_aws_object_cache

    # --- Cloudwatch Event ---
    @property
    def scheduled_job_expression_list(self):
        if self.scheduled_job_expression is NOTHING:
            return self.scheduled_job_expression
        elif isinstance(self.scheduled_job_expression, str):
            return [self.scheduled_job_expression, ]
        elif isinstance(self.scheduled_job_expression, list):
            return self.scheduled_job_expression
        else:
            raise TypeError(
                "{}.cron_job_expression".format(self.identifier)
            )

    def scheduled_job_event_rule_aws_objects_pre_check(self):
        """
        **中文文档**

        检查根据当前的设置, 是否满足自动创建 troposphere_mate.events.Rule 的条件

        目前只支持 CUSTOM 的 Lambda Authorizer

        - :attr:`LbdFuncConfig.scheduled_job_expression`: 必须为Python函数,
            不然没有 Lambda Function 的支持, Event.Rule 就无意义.
        - :attr:`LbdFuncConfig.scheduled_job_expression`: 必须被定义
        - 必须满足所有创建 Lambda Function AWS Object 的条件
        """
        self.lbd_func_aws_object_pre_check()
        if self.scheduled_job_expression is NOTHING:
            raise ValueError("scheduled_job_expression is not defined yet!")

    def scheduled_job_event_rule_aws_objects_ready(self):
        return self._ready_checker_shortener("scheduled_job_event_rule")

    @property
    def scheduled_job_event_rule_aws_objects(self) -> typing.Dict[str, events.Rule]:
        """
        Returns a key value pair of scheduled job expression and
        ``troposphere_mate.events.Rule`` object. Since
        """
        if self._scheduled_job_event_rule_aws_objects_cache is NOTHING:
            dct = dict()
            for expression in self.scheduled_job_expression_list:
                event_rule_logic_id = "EventRule{}".format(
                    fingerprint.of_text(expression + self.lbd_func_name)
                )
                event_rule = events.Rule(
                    title=event_rule_logic_id,
                    State="ENABLED",
                    ScheduleExpression=expression,
                    Targets=[
                        events.Target(
                            Id="EventRuleStartCrawlerGitHubDataTrigger",
                            Arn=GetAtt(self.lbd_func_aws_object, "Arn"),
                        )
                    ],
                    DependsOn=[
                        self.lbd_func_aws_object,
                    ]
                )
                dct[expression] = event_rule
            self._scheduled_job_event_rule_aws_objects_cache = dct
        return self._scheduled_job_event_rule_aws_objects_cache

    def scheduled_job_event_lbd_permission_aws_objects_pre_check(self):
        self.scheduled_job_event_rule_aws_objects_pre_check()
        self.lbd_func_aws_object_pre_check()

    def scheduled_job_event_lbd_permission_aws_objects_ready(self):
        return self.scheduled_job_event_rule_aws_objects_ready() and self.lbd_func_aws_object_ready()

    @property
    def scheduled_job_event_lbd_permission_aws_objects(self) -> typing.Dict[str, awslambda.Permission]:
        if self._scheduled_job_event_lbd_permission_aws_objects_cache is NOTHING:
            dct = dict()
            for expression in self.scheduled_job_expression_list:
                event_rule_lambda_permission_logic_id = "LbdPermissionEventRule{}".format(
                    fingerprint.of_text(expression + self.lbd_func_name)
                )
                event_rule = self.scheduled_job_event_rule_aws_objects[expression]
                event_rule_lambda_permission = awslambda.Permission(
                    title=event_rule_lambda_permission_logic_id,
                    Action="lambda:InvokeFunction",
                    FunctionName=GetAtt(self.lbd_func_aws_object, "Arn"),
                    Principal="events.amazonaws.com",
                    SourceArn=GetAtt(event_rule, "Arn"),
                    DependsOn=[
                        event_rule,
                        self.lbd_func_aws_object,
                    ]
                )
                dct[expression] = event_rule_lambda_permission
            self._scheduled_job_event_lbd_permission_aws_objects_cache = dct
        return self._scheduled_job_event_lbd_permission_aws_objects_cache

    def create_aws_resource(self, template):
        self.create_lbd_func(template)
        self.create_apigw_resource(template)
        self.create_apigw_method(template)
        self.create_apigw_method_options_for_cors(template)
        self.create_apigw_authorizer(template)
        self.create_scheduled_job_event(template)
        self.create_s3_event_bucket(template)

    def create_lbd_func(self, template: Template):
        if self.lbd_func_aws_object_ready():
            template.add_resource(self.lbd_func_aws_object, ignore_duplicate=True)

    def create_apigw_resource(self, template: Template):
        if self.apigw_resource_aws_object_ready():
            template.add_resource(self.apigw_resource_aws_object, ignore_duplicate=True)

    def create_apigw_method(self, template: Template):
        if self.apigw_method_aws_object_ready():
            template.add_resource(self.apigw_method_aws_object, ignore_duplicate=True)
        if self.apigw_method_lbd_permission_aws_object_ready():
            template.add_resource(self.apigw_method_lbd_permission_aws_object, ignore_duplicate=True)

    def create_apigw_method_options_for_cors(self, template: Template):
        if self.apigw_method_options_for_cors_aws_object_ready():
            template.add_resource(self.apigw_method_options_for_cors_aws_object, ignore_duplicate=True)

    def create_apigw_authorizer(self, template: Template):
        if self.apigw_authorizer_aws_object_ready():
            template.add_resource(self.apigw_authorizer_aws_object, ignore_duplicate=True)
        if self.apigw_authorizer_lbd_permission_aws_object_ready():
            template.add_resource(self.apigw_authorizer_lbd_permission_aws_object, ignore_duplicate=True)

    def create_scheduled_job_event(self, template: Template):
        if self.scheduled_job_event_rule_aws_objects_ready():
            for _, value in self.scheduled_job_event_rule_aws_objects.items():
                template.add_resource(value, ignore_duplicate=True)
        if self.scheduled_job_event_lbd_permission_aws_objects_ready():
            for _, value in self.scheduled_job_event_lbd_permission_aws_objects.items():
                template.add_resource(value, ignore_duplicate=True)

    def create_s3_event_bucket(self, template: Template):
        if self.s3_event_bucket_aws_object_ready():
            template.add_resource(self.s3_event_bucket_aws_object, ignore_duplicate=True)
        if self.s3_event_bucket_lbd_permission_aws_object_ready():
            template.add_resource(self.s3_event_bucket_lbd_permission_aws_object, ignore_duplicate=True)


def lbd_func_config_value_handler(module_name: str,
                                  config_field: str,
                                  config_class: typing.Type[LbdFuncConfig],
                                  valid_func_name_list: typing.List[str],
                                  default_lbd_handler_name: str):
    root_module_name = module_name
    for py_current_module, py_parent_module, py_handler_func in walk_lbd_handler(
            module_name, valid_func_name_list):
        # print(py_current_module.__name__)

        current_module_config = getattr(py_current_module, config_field)  # type: LbdFuncConfig
        current_module_config._root_module_name = root_module_name
        current_module_config._py_module = py_current_module
        current_module_config._py_parent_module = py_parent_module

        # print(py_current_module.__name__, py_parent_module.__name__, py_handler_func.__name__)

        if py_handler_func is not None:
            py_handler_func_config = getattr(py_handler_func, config_field)  # type: LbdFuncConfig
            py_handler_func_config._root_module_name = root_module_name
            py_handler_func_config._py_module = py_current_module
            py_handler_func_config._py_parent_module = py_parent_module
            py_handler_func_config._py_function = py_handler_func
            if py_handler_func_config.lbd_func_name is REQUIRED:
                py_handler_func_config.lbd_func_name = \
                    slugify(py_handler_func_config.rel_module_name.replace(".", "-")) + "-" + slugify(
                        py_handler_func.__name__)


def template_creation_handler(module_name: str,
                              config_field: str,
                              config_class: typing.Type[LbdFuncConfig],
                              valid_func_name_list: typing.List[str],
                              template: Template):
    for py_current_module, py_parent_module, py_handler_func in walk_lbd_handler(
            module_name, valid_func_name_list):
        current_module_config = getattr(py_current_module, config_field)  # type: LbdFuncConfig
        print("create aws resource for {}".format(current_module_config.identifier))
        current_module_config.create_aws_resource(template)

        if py_handler_func is not None:
            py_handler_func_config = getattr(py_handler_func, config_field)  # type: LbdFuncConfig
            print("create aws resource for {}".format(py_handler_func_config.identifier))
            py_handler_func_config.create_aws_resource(template)
