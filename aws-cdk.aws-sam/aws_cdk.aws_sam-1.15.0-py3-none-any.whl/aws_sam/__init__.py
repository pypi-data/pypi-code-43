import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.core
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-sam", "1.15.0", __name__, "aws-sam@1.15.0.jsii.tgz")
class CfnApi(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-sam.CfnApi"):
    """A CloudFormation ``AWS::Serverless::Api``.

    see
    :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessapi
    cloudformationResource:
    :cloudformationResource:: AWS::Serverless::Api
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, stage_name: str, access_log_setting: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["AccessLogSettingProperty"]]]=None, auth: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["AuthProperty"]]]=None, binary_media_types: typing.Optional[typing.List[str]]=None, cache_cluster_enabled: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, cache_cluster_size: typing.Optional[str]=None, cors: typing.Optional[str]=None, definition_body: typing.Any=None, definition_uri: typing.Optional[typing.Union[typing.Optional[str], typing.Optional[aws_cdk.core.IResolvable], typing.Optional["S3LocationProperty"]]]=None, endpoint_configuration: typing.Optional[str]=None, method_settings: typing.Any=None, name: typing.Optional[str]=None, tracing_enabled: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, variables: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.Mapping[str,str]]]]=None) -> None:
        """Create a new ``AWS::Serverless::Api``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param stage_name: ``AWS::Serverless::Api.StageName``.
        :param access_log_setting: ``AWS::Serverless::Api.AccessLogSetting``.
        :param auth: ``AWS::Serverless::Api.Auth``.
        :param binary_media_types: ``AWS::Serverless::Api.BinaryMediaTypes``.
        :param cache_cluster_enabled: ``AWS::Serverless::Api.CacheClusterEnabled``.
        :param cache_cluster_size: ``AWS::Serverless::Api.CacheClusterSize``.
        :param cors: ``AWS::Serverless::Api.Cors``.
        :param definition_body: ``AWS::Serverless::Api.DefinitionBody``.
        :param definition_uri: ``AWS::Serverless::Api.DefinitionUri``.
        :param endpoint_configuration: ``AWS::Serverless::Api.EndpointConfiguration``.
        :param method_settings: ``AWS::Serverless::Api.MethodSettings``.
        :param name: ``AWS::Serverless::Api.Name``.
        :param tracing_enabled: ``AWS::Serverless::Api.TracingEnabled``.
        :param variables: ``AWS::Serverless::Api.Variables``.
        """
        props = CfnApiProps(stage_name=stage_name, access_log_setting=access_log_setting, auth=auth, binary_media_types=binary_media_types, cache_cluster_enabled=cache_cluster_enabled, cache_cluster_size=cache_cluster_size, cors=cors, definition_body=definition_body, definition_uri=definition_uri, endpoint_configuration=endpoint_configuration, method_settings=method_settings, name=name, tracing_enabled=tracing_enabled, variables=variables)

        jsii.create(CfnApi, self, [scope, id, props])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(self, props: typing.Mapping[str,typing.Any]) -> typing.Mapping[str,typing.Any]:
        """
        :param props: -
        """
        return jsii.invoke(self, "renderProperties", [props])

    @classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class."""
        return jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME")

    @classproperty
    @jsii.member(jsii_name="REQUIRED_TRANSFORM")
    def REQUIRED_TRANSFORM(cls) -> str:
        """The ``Transform`` a template must use in order to use this resource."""
        return jsii.sget(cls, "REQUIRED_TRANSFORM")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="definitionBody")
    def definition_body(self) -> typing.Any:
        """``AWS::Serverless::Api.DefinitionBody``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessapi
        """
        return jsii.get(self, "definitionBody")

    @definition_body.setter
    def definition_body(self, value: typing.Any):
        return jsii.set(self, "definitionBody", value)

    @property
    @jsii.member(jsii_name="methodSettings")
    def method_settings(self) -> typing.Any:
        """``AWS::Serverless::Api.MethodSettings``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessapi
        """
        return jsii.get(self, "methodSettings")

    @method_settings.setter
    def method_settings(self, value: typing.Any):
        return jsii.set(self, "methodSettings", value)

    @property
    @jsii.member(jsii_name="stageName")
    def stage_name(self) -> str:
        """``AWS::Serverless::Api.StageName``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessapi
        """
        return jsii.get(self, "stageName")

    @stage_name.setter
    def stage_name(self, value: str):
        return jsii.set(self, "stageName", value)

    @property
    @jsii.member(jsii_name="accessLogSetting")
    def access_log_setting(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["AccessLogSettingProperty"]]]:
        """``AWS::Serverless::Api.AccessLogSetting``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessapi
        """
        return jsii.get(self, "accessLogSetting")

    @access_log_setting.setter
    def access_log_setting(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["AccessLogSettingProperty"]]]):
        return jsii.set(self, "accessLogSetting", value)

    @property
    @jsii.member(jsii_name="auth")
    def auth(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["AuthProperty"]]]:
        """``AWS::Serverless::Api.Auth``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessapi
        """
        return jsii.get(self, "auth")

    @auth.setter
    def auth(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["AuthProperty"]]]):
        return jsii.set(self, "auth", value)

    @property
    @jsii.member(jsii_name="binaryMediaTypes")
    def binary_media_types(self) -> typing.Optional[typing.List[str]]:
        """``AWS::Serverless::Api.BinaryMediaTypes``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessapi
        """
        return jsii.get(self, "binaryMediaTypes")

    @binary_media_types.setter
    def binary_media_types(self, value: typing.Optional[typing.List[str]]):
        return jsii.set(self, "binaryMediaTypes", value)

    @property
    @jsii.member(jsii_name="cacheClusterEnabled")
    def cache_cluster_enabled(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::Serverless::Api.CacheClusterEnabled``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessapi
        """
        return jsii.get(self, "cacheClusterEnabled")

    @cache_cluster_enabled.setter
    def cache_cluster_enabled(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "cacheClusterEnabled", value)

    @property
    @jsii.member(jsii_name="cacheClusterSize")
    def cache_cluster_size(self) -> typing.Optional[str]:
        """``AWS::Serverless::Api.CacheClusterSize``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessapi
        """
        return jsii.get(self, "cacheClusterSize")

    @cache_cluster_size.setter
    def cache_cluster_size(self, value: typing.Optional[str]):
        return jsii.set(self, "cacheClusterSize", value)

    @property
    @jsii.member(jsii_name="cors")
    def cors(self) -> typing.Optional[str]:
        """``AWS::Serverless::Api.Cors``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessapi
        """
        return jsii.get(self, "cors")

    @cors.setter
    def cors(self, value: typing.Optional[str]):
        return jsii.set(self, "cors", value)

    @property
    @jsii.member(jsii_name="definitionUri")
    def definition_uri(self) -> typing.Optional[typing.Union[typing.Optional[str], typing.Optional[aws_cdk.core.IResolvable], typing.Optional["S3LocationProperty"]]]:
        """``AWS::Serverless::Api.DefinitionUri``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessapi
        """
        return jsii.get(self, "definitionUri")

    @definition_uri.setter
    def definition_uri(self, value: typing.Optional[typing.Union[typing.Optional[str], typing.Optional[aws_cdk.core.IResolvable], typing.Optional["S3LocationProperty"]]]):
        return jsii.set(self, "definitionUri", value)

    @property
    @jsii.member(jsii_name="endpointConfiguration")
    def endpoint_configuration(self) -> typing.Optional[str]:
        """``AWS::Serverless::Api.EndpointConfiguration``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessapi
        """
        return jsii.get(self, "endpointConfiguration")

    @endpoint_configuration.setter
    def endpoint_configuration(self, value: typing.Optional[str]):
        return jsii.set(self, "endpointConfiguration", value)

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[str]:
        """``AWS::Serverless::Api.Name``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessapi
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: typing.Optional[str]):
        return jsii.set(self, "name", value)

    @property
    @jsii.member(jsii_name="tracingEnabled")
    def tracing_enabled(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::Serverless::Api.TracingEnabled``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessapi
        """
        return jsii.get(self, "tracingEnabled")

    @tracing_enabled.setter
    def tracing_enabled(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "tracingEnabled", value)

    @property
    @jsii.member(jsii_name="variables")
    def variables(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.Mapping[str,str]]]]:
        """``AWS::Serverless::Api.Variables``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessapi
        """
        return jsii.get(self, "variables")

    @variables.setter
    def variables(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.Mapping[str,str]]]]):
        return jsii.set(self, "variables", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-sam.CfnApi.AccessLogSettingProperty", jsii_struct_bases=[], name_mapping={'destination_arn': 'destinationArn', 'format': 'format'})
    class AccessLogSettingProperty():
        def __init__(self, *, destination_arn: typing.Optional[str]=None, format: typing.Optional[str]=None):
            """
            :param destination_arn: ``CfnApi.AccessLogSettingProperty.DestinationArn``.
            :param format: ``CfnApi.AccessLogSettingProperty.Format``.

            see
            :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigateway-stage-accesslogsetting.html
            """
            self._values = {
            }
            if destination_arn is not None: self._values["destination_arn"] = destination_arn
            if format is not None: self._values["format"] = format

        @property
        def destination_arn(self) -> typing.Optional[str]:
            """``CfnApi.AccessLogSettingProperty.DestinationArn``.

            see
            :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigateway-stage-accesslogsetting.html#cfn-apigateway-stage-accesslogsetting-destinationarn
            """
            return self._values.get('destination_arn')

        @property
        def format(self) -> typing.Optional[str]:
            """``CfnApi.AccessLogSettingProperty.Format``.

            see
            :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigateway-stage-accesslogsetting.html#cfn-apigateway-stage-accesslogsetting-format
            """
            return self._values.get('format')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'AccessLogSettingProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-sam.CfnApi.AuthProperty", jsii_struct_bases=[], name_mapping={'authorizers': 'authorizers', 'default_authorizer': 'defaultAuthorizer'})
    class AuthProperty():
        def __init__(self, *, authorizers: typing.Any=None, default_authorizer: typing.Optional[str]=None):
            """
            :param authorizers: ``CfnApi.AuthProperty.Authorizers``.
            :param default_authorizer: ``CfnApi.AuthProperty.DefaultAuthorizer``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#api-auth-object
            """
            self._values = {
            }
            if authorizers is not None: self._values["authorizers"] = authorizers
            if default_authorizer is not None: self._values["default_authorizer"] = default_authorizer

        @property
        def authorizers(self) -> typing.Any:
            """``CfnApi.AuthProperty.Authorizers``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#api-auth-object
            """
            return self._values.get('authorizers')

        @property
        def default_authorizer(self) -> typing.Optional[str]:
            """``CfnApi.AuthProperty.DefaultAuthorizer``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#api-auth-object
            """
            return self._values.get('default_authorizer')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'AuthProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-sam.CfnApi.S3LocationProperty", jsii_struct_bases=[], name_mapping={'bucket': 'bucket', 'key': 'key', 'version': 'version'})
    class S3LocationProperty():
        def __init__(self, *, bucket: str, key: str, version: jsii.Number):
            """
            :param bucket: ``CfnApi.S3LocationProperty.Bucket``.
            :param key: ``CfnApi.S3LocationProperty.Key``.
            :param version: ``CfnApi.S3LocationProperty.Version``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#s3-location-object
            """
            self._values = {
                'bucket': bucket,
                'key': key,
                'version': version,
            }

        @property
        def bucket(self) -> str:
            """``CfnApi.S3LocationProperty.Bucket``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessfunction
            """
            return self._values.get('bucket')

        @property
        def key(self) -> str:
            """``CfnApi.S3LocationProperty.Key``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessfunction
            """
            return self._values.get('key')

        @property
        def version(self) -> jsii.Number:
            """``CfnApi.S3LocationProperty.Version``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessfunction
            """
            return self._values.get('version')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'S3LocationProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



@jsii.data_type(jsii_type="@aws-cdk/aws-sam.CfnApiProps", jsii_struct_bases=[], name_mapping={'stage_name': 'stageName', 'access_log_setting': 'accessLogSetting', 'auth': 'auth', 'binary_media_types': 'binaryMediaTypes', 'cache_cluster_enabled': 'cacheClusterEnabled', 'cache_cluster_size': 'cacheClusterSize', 'cors': 'cors', 'definition_body': 'definitionBody', 'definition_uri': 'definitionUri', 'endpoint_configuration': 'endpointConfiguration', 'method_settings': 'methodSettings', 'name': 'name', 'tracing_enabled': 'tracingEnabled', 'variables': 'variables'})
class CfnApiProps():
    def __init__(self, *, stage_name: str, access_log_setting: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnApi.AccessLogSettingProperty"]]]=None, auth: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnApi.AuthProperty"]]]=None, binary_media_types: typing.Optional[typing.List[str]]=None, cache_cluster_enabled: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, cache_cluster_size: typing.Optional[str]=None, cors: typing.Optional[str]=None, definition_body: typing.Any=None, definition_uri: typing.Optional[typing.Union[typing.Optional[str], typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnApi.S3LocationProperty"]]]=None, endpoint_configuration: typing.Optional[str]=None, method_settings: typing.Any=None, name: typing.Optional[str]=None, tracing_enabled: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, variables: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.Mapping[str,str]]]]=None):
        """Properties for defining a ``AWS::Serverless::Api``.

        :param stage_name: ``AWS::Serverless::Api.StageName``.
        :param access_log_setting: ``AWS::Serverless::Api.AccessLogSetting``.
        :param auth: ``AWS::Serverless::Api.Auth``.
        :param binary_media_types: ``AWS::Serverless::Api.BinaryMediaTypes``.
        :param cache_cluster_enabled: ``AWS::Serverless::Api.CacheClusterEnabled``.
        :param cache_cluster_size: ``AWS::Serverless::Api.CacheClusterSize``.
        :param cors: ``AWS::Serverless::Api.Cors``.
        :param definition_body: ``AWS::Serverless::Api.DefinitionBody``.
        :param definition_uri: ``AWS::Serverless::Api.DefinitionUri``.
        :param endpoint_configuration: ``AWS::Serverless::Api.EndpointConfiguration``.
        :param method_settings: ``AWS::Serverless::Api.MethodSettings``.
        :param name: ``AWS::Serverless::Api.Name``.
        :param tracing_enabled: ``AWS::Serverless::Api.TracingEnabled``.
        :param variables: ``AWS::Serverless::Api.Variables``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessapi
        """
        self._values = {
            'stage_name': stage_name,
        }
        if access_log_setting is not None: self._values["access_log_setting"] = access_log_setting
        if auth is not None: self._values["auth"] = auth
        if binary_media_types is not None: self._values["binary_media_types"] = binary_media_types
        if cache_cluster_enabled is not None: self._values["cache_cluster_enabled"] = cache_cluster_enabled
        if cache_cluster_size is not None: self._values["cache_cluster_size"] = cache_cluster_size
        if cors is not None: self._values["cors"] = cors
        if definition_body is not None: self._values["definition_body"] = definition_body
        if definition_uri is not None: self._values["definition_uri"] = definition_uri
        if endpoint_configuration is not None: self._values["endpoint_configuration"] = endpoint_configuration
        if method_settings is not None: self._values["method_settings"] = method_settings
        if name is not None: self._values["name"] = name
        if tracing_enabled is not None: self._values["tracing_enabled"] = tracing_enabled
        if variables is not None: self._values["variables"] = variables

    @property
    def stage_name(self) -> str:
        """``AWS::Serverless::Api.StageName``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessapi
        """
        return self._values.get('stage_name')

    @property
    def access_log_setting(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnApi.AccessLogSettingProperty"]]]:
        """``AWS::Serverless::Api.AccessLogSetting``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessapi
        """
        return self._values.get('access_log_setting')

    @property
    def auth(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnApi.AuthProperty"]]]:
        """``AWS::Serverless::Api.Auth``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessapi
        """
        return self._values.get('auth')

    @property
    def binary_media_types(self) -> typing.Optional[typing.List[str]]:
        """``AWS::Serverless::Api.BinaryMediaTypes``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessapi
        """
        return self._values.get('binary_media_types')

    @property
    def cache_cluster_enabled(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::Serverless::Api.CacheClusterEnabled``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessapi
        """
        return self._values.get('cache_cluster_enabled')

    @property
    def cache_cluster_size(self) -> typing.Optional[str]:
        """``AWS::Serverless::Api.CacheClusterSize``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessapi
        """
        return self._values.get('cache_cluster_size')

    @property
    def cors(self) -> typing.Optional[str]:
        """``AWS::Serverless::Api.Cors``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessapi
        """
        return self._values.get('cors')

    @property
    def definition_body(self) -> typing.Any:
        """``AWS::Serverless::Api.DefinitionBody``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessapi
        """
        return self._values.get('definition_body')

    @property
    def definition_uri(self) -> typing.Optional[typing.Union[typing.Optional[str], typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnApi.S3LocationProperty"]]]:
        """``AWS::Serverless::Api.DefinitionUri``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessapi
        """
        return self._values.get('definition_uri')

    @property
    def endpoint_configuration(self) -> typing.Optional[str]:
        """``AWS::Serverless::Api.EndpointConfiguration``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessapi
        """
        return self._values.get('endpoint_configuration')

    @property
    def method_settings(self) -> typing.Any:
        """``AWS::Serverless::Api.MethodSettings``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessapi
        """
        return self._values.get('method_settings')

    @property
    def name(self) -> typing.Optional[str]:
        """``AWS::Serverless::Api.Name``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessapi
        """
        return self._values.get('name')

    @property
    def tracing_enabled(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::Serverless::Api.TracingEnabled``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessapi
        """
        return self._values.get('tracing_enabled')

    @property
    def variables(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.Mapping[str,str]]]]:
        """``AWS::Serverless::Api.Variables``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessapi
        """
        return self._values.get('variables')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnApiProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnApplication(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-sam.CfnApplication"):
    """A CloudFormation ``AWS::Serverless::Application``.

    see
    :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessapplication
    cloudformationResource:
    :cloudformationResource:: AWS::Serverless::Application
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, location: typing.Union[str, "ApplicationLocationProperty", aws_cdk.core.IResolvable], notification_arns: typing.Optional[typing.List[str]]=None, parameters: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.Mapping[str,str]]]]=None, tags: typing.Optional[typing.Mapping[str,str]]=None, timeout_in_minutes: typing.Optional[jsii.Number]=None) -> None:
        """Create a new ``AWS::Serverless::Application``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param location: ``AWS::Serverless::Application.Location``.
        :param notification_arns: ``AWS::Serverless::Application.NotificationArns``.
        :param parameters: ``AWS::Serverless::Application.Parameters``.
        :param tags: ``AWS::Serverless::Application.Tags``.
        :param timeout_in_minutes: ``AWS::Serverless::Application.TimeoutInMinutes``.
        """
        props = CfnApplicationProps(location=location, notification_arns=notification_arns, parameters=parameters, tags=tags, timeout_in_minutes=timeout_in_minutes)

        jsii.create(CfnApplication, self, [scope, id, props])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(self, props: typing.Mapping[str,typing.Any]) -> typing.Mapping[str,typing.Any]:
        """
        :param props: -
        """
        return jsii.invoke(self, "renderProperties", [props])

    @classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class."""
        return jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME")

    @classproperty
    @jsii.member(jsii_name="REQUIRED_TRANSFORM")
    def REQUIRED_TRANSFORM(cls) -> str:
        """The ``Transform`` a template must use in order to use this resource."""
        return jsii.sget(cls, "REQUIRED_TRANSFORM")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        """``AWS::Serverless::Application.Tags``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessapplication
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="location")
    def location(self) -> typing.Union[str, "ApplicationLocationProperty", aws_cdk.core.IResolvable]:
        """``AWS::Serverless::Application.Location``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessapplication
        """
        return jsii.get(self, "location")

    @location.setter
    def location(self, value: typing.Union[str, "ApplicationLocationProperty", aws_cdk.core.IResolvable]):
        return jsii.set(self, "location", value)

    @property
    @jsii.member(jsii_name="notificationArns")
    def notification_arns(self) -> typing.Optional[typing.List[str]]:
        """``AWS::Serverless::Application.NotificationArns``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessapplication
        """
        return jsii.get(self, "notificationArns")

    @notification_arns.setter
    def notification_arns(self, value: typing.Optional[typing.List[str]]):
        return jsii.set(self, "notificationArns", value)

    @property
    @jsii.member(jsii_name="parameters")
    def parameters(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.Mapping[str,str]]]]:
        """``AWS::Serverless::Application.Parameters``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessapplication
        """
        return jsii.get(self, "parameters")

    @parameters.setter
    def parameters(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.Mapping[str,str]]]]):
        return jsii.set(self, "parameters", value)

    @property
    @jsii.member(jsii_name="timeoutInMinutes")
    def timeout_in_minutes(self) -> typing.Optional[jsii.Number]:
        """``AWS::Serverless::Application.TimeoutInMinutes``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessapplication
        """
        return jsii.get(self, "timeoutInMinutes")

    @timeout_in_minutes.setter
    def timeout_in_minutes(self, value: typing.Optional[jsii.Number]):
        return jsii.set(self, "timeoutInMinutes", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-sam.CfnApplication.ApplicationLocationProperty", jsii_struct_bases=[], name_mapping={'application_id': 'applicationId', 'semantic_version': 'semanticVersion'})
    class ApplicationLocationProperty():
        def __init__(self, *, application_id: str, semantic_version: str):
            """
            :param application_id: ``CfnApplication.ApplicationLocationProperty.ApplicationId``.
            :param semantic_version: ``CfnApplication.ApplicationLocationProperty.SemanticVersion``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessapplication
            """
            self._values = {
                'application_id': application_id,
                'semantic_version': semantic_version,
            }

        @property
        def application_id(self) -> str:
            """``CfnApplication.ApplicationLocationProperty.ApplicationId``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessapplication
            """
            return self._values.get('application_id')

        @property
        def semantic_version(self) -> str:
            """``CfnApplication.ApplicationLocationProperty.SemanticVersion``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessapplication
            """
            return self._values.get('semantic_version')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'ApplicationLocationProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



@jsii.data_type(jsii_type="@aws-cdk/aws-sam.CfnApplicationProps", jsii_struct_bases=[], name_mapping={'location': 'location', 'notification_arns': 'notificationArns', 'parameters': 'parameters', 'tags': 'tags', 'timeout_in_minutes': 'timeoutInMinutes'})
class CfnApplicationProps():
    def __init__(self, *, location: typing.Union[str, "CfnApplication.ApplicationLocationProperty", aws_cdk.core.IResolvable], notification_arns: typing.Optional[typing.List[str]]=None, parameters: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.Mapping[str,str]]]]=None, tags: typing.Optional[typing.Mapping[str,str]]=None, timeout_in_minutes: typing.Optional[jsii.Number]=None):
        """Properties for defining a ``AWS::Serverless::Application``.

        :param location: ``AWS::Serverless::Application.Location``.
        :param notification_arns: ``AWS::Serverless::Application.NotificationArns``.
        :param parameters: ``AWS::Serverless::Application.Parameters``.
        :param tags: ``AWS::Serverless::Application.Tags``.
        :param timeout_in_minutes: ``AWS::Serverless::Application.TimeoutInMinutes``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessapplication
        """
        self._values = {
            'location': location,
        }
        if notification_arns is not None: self._values["notification_arns"] = notification_arns
        if parameters is not None: self._values["parameters"] = parameters
        if tags is not None: self._values["tags"] = tags
        if timeout_in_minutes is not None: self._values["timeout_in_minutes"] = timeout_in_minutes

    @property
    def location(self) -> typing.Union[str, "CfnApplication.ApplicationLocationProperty", aws_cdk.core.IResolvable]:
        """``AWS::Serverless::Application.Location``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessapplication
        """
        return self._values.get('location')

    @property
    def notification_arns(self) -> typing.Optional[typing.List[str]]:
        """``AWS::Serverless::Application.NotificationArns``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessapplication
        """
        return self._values.get('notification_arns')

    @property
    def parameters(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.Mapping[str,str]]]]:
        """``AWS::Serverless::Application.Parameters``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessapplication
        """
        return self._values.get('parameters')

    @property
    def tags(self) -> typing.Optional[typing.Mapping[str,str]]:
        """``AWS::Serverless::Application.Tags``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessapplication
        """
        return self._values.get('tags')

    @property
    def timeout_in_minutes(self) -> typing.Optional[jsii.Number]:
        """``AWS::Serverless::Application.TimeoutInMinutes``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessapplication
        """
        return self._values.get('timeout_in_minutes')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnApplicationProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnFunction(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-sam.CfnFunction"):
    """A CloudFormation ``AWS::Serverless::Function``.

    see
    :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessfunction
    cloudformationResource:
    :cloudformationResource:: AWS::Serverless::Function
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, code_uri: typing.Union[str, aws_cdk.core.IResolvable, "S3LocationProperty"], handler: str, runtime: str, auto_publish_alias: typing.Optional[str]=None, dead_letter_queue: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["DeadLetterQueueProperty"]]]=None, deployment_preference: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["DeploymentPreferenceProperty"]]]=None, description: typing.Optional[str]=None, environment: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["FunctionEnvironmentProperty"]]]=None, events: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.Mapping[str,typing.Union[aws_cdk.core.IResolvable, "EventSourceProperty"]]]]]=None, function_name: typing.Optional[str]=None, kms_key_arn: typing.Optional[str]=None, layers: typing.Optional[typing.List[str]]=None, memory_size: typing.Optional[jsii.Number]=None, permissions_boundary: typing.Optional[str]=None, policies: typing.Optional[typing.Union[typing.Optional[str], typing.Optional[aws_cdk.core.IResolvable], typing.Optional["IAMPolicyDocumentProperty"], typing.Optional[typing.List[typing.Union[str, aws_cdk.core.IResolvable, "IAMPolicyDocumentProperty", "SAMPolicyTemplateProperty"]]]]]=None, reserved_concurrent_executions: typing.Optional[jsii.Number]=None, role: typing.Optional[str]=None, tags: typing.Optional[typing.Mapping[str,str]]=None, timeout: typing.Optional[jsii.Number]=None, tracing: typing.Optional[str]=None, vpc_config: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["VpcConfigProperty"]]]=None) -> None:
        """Create a new ``AWS::Serverless::Function``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param code_uri: ``AWS::Serverless::Function.CodeUri``.
        :param handler: ``AWS::Serverless::Function.Handler``.
        :param runtime: ``AWS::Serverless::Function.Runtime``.
        :param auto_publish_alias: ``AWS::Serverless::Function.AutoPublishAlias``.
        :param dead_letter_queue: ``AWS::Serverless::Function.DeadLetterQueue``.
        :param deployment_preference: ``AWS::Serverless::Function.DeploymentPreference``.
        :param description: ``AWS::Serverless::Function.Description``.
        :param environment: ``AWS::Serverless::Function.Environment``.
        :param events: ``AWS::Serverless::Function.Events``.
        :param function_name: ``AWS::Serverless::Function.FunctionName``.
        :param kms_key_arn: ``AWS::Serverless::Function.KmsKeyArn``.
        :param layers: ``AWS::Serverless::Function.Layers``.
        :param memory_size: ``AWS::Serverless::Function.MemorySize``.
        :param permissions_boundary: ``AWS::Serverless::Function.PermissionsBoundary``.
        :param policies: ``AWS::Serverless::Function.Policies``.
        :param reserved_concurrent_executions: ``AWS::Serverless::Function.ReservedConcurrentExecutions``.
        :param role: ``AWS::Serverless::Function.Role``.
        :param tags: ``AWS::Serverless::Function.Tags``.
        :param timeout: ``AWS::Serverless::Function.Timeout``.
        :param tracing: ``AWS::Serverless::Function.Tracing``.
        :param vpc_config: ``AWS::Serverless::Function.VpcConfig``.
        """
        props = CfnFunctionProps(code_uri=code_uri, handler=handler, runtime=runtime, auto_publish_alias=auto_publish_alias, dead_letter_queue=dead_letter_queue, deployment_preference=deployment_preference, description=description, environment=environment, events=events, function_name=function_name, kms_key_arn=kms_key_arn, layers=layers, memory_size=memory_size, permissions_boundary=permissions_boundary, policies=policies, reserved_concurrent_executions=reserved_concurrent_executions, role=role, tags=tags, timeout=timeout, tracing=tracing, vpc_config=vpc_config)

        jsii.create(CfnFunction, self, [scope, id, props])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(self, props: typing.Mapping[str,typing.Any]) -> typing.Mapping[str,typing.Any]:
        """
        :param props: -
        """
        return jsii.invoke(self, "renderProperties", [props])

    @classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class."""
        return jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME")

    @classproperty
    @jsii.member(jsii_name="REQUIRED_TRANSFORM")
    def REQUIRED_TRANSFORM(cls) -> str:
        """The ``Transform`` a template must use in order to use this resource."""
        return jsii.sget(cls, "REQUIRED_TRANSFORM")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        """``AWS::Serverless::Function.Tags``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessfunction
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="codeUri")
    def code_uri(self) -> typing.Union[str, aws_cdk.core.IResolvable, "S3LocationProperty"]:
        """``AWS::Serverless::Function.CodeUri``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessfunction
        """
        return jsii.get(self, "codeUri")

    @code_uri.setter
    def code_uri(self, value: typing.Union[str, aws_cdk.core.IResolvable, "S3LocationProperty"]):
        return jsii.set(self, "codeUri", value)

    @property
    @jsii.member(jsii_name="handler")
    def handler(self) -> str:
        """``AWS::Serverless::Function.Handler``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessfunction
        """
        return jsii.get(self, "handler")

    @handler.setter
    def handler(self, value: str):
        return jsii.set(self, "handler", value)

    @property
    @jsii.member(jsii_name="runtime")
    def runtime(self) -> str:
        """``AWS::Serverless::Function.Runtime``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessfunction
        """
        return jsii.get(self, "runtime")

    @runtime.setter
    def runtime(self, value: str):
        return jsii.set(self, "runtime", value)

    @property
    @jsii.member(jsii_name="autoPublishAlias")
    def auto_publish_alias(self) -> typing.Optional[str]:
        """``AWS::Serverless::Function.AutoPublishAlias``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessfunction
        """
        return jsii.get(self, "autoPublishAlias")

    @auto_publish_alias.setter
    def auto_publish_alias(self, value: typing.Optional[str]):
        return jsii.set(self, "autoPublishAlias", value)

    @property
    @jsii.member(jsii_name="deadLetterQueue")
    def dead_letter_queue(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["DeadLetterQueueProperty"]]]:
        """``AWS::Serverless::Function.DeadLetterQueue``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessfunction
        """
        return jsii.get(self, "deadLetterQueue")

    @dead_letter_queue.setter
    def dead_letter_queue(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["DeadLetterQueueProperty"]]]):
        return jsii.set(self, "deadLetterQueue", value)

    @property
    @jsii.member(jsii_name="deploymentPreference")
    def deployment_preference(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["DeploymentPreferenceProperty"]]]:
        """``AWS::Serverless::Function.DeploymentPreference``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#deploymentpreference-object
        """
        return jsii.get(self, "deploymentPreference")

    @deployment_preference.setter
    def deployment_preference(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["DeploymentPreferenceProperty"]]]):
        return jsii.set(self, "deploymentPreference", value)

    @property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[str]:
        """``AWS::Serverless::Function.Description``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessfunction
        """
        return jsii.get(self, "description")

    @description.setter
    def description(self, value: typing.Optional[str]):
        return jsii.set(self, "description", value)

    @property
    @jsii.member(jsii_name="environment")
    def environment(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["FunctionEnvironmentProperty"]]]:
        """``AWS::Serverless::Function.Environment``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessfunction
        """
        return jsii.get(self, "environment")

    @environment.setter
    def environment(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["FunctionEnvironmentProperty"]]]):
        return jsii.set(self, "environment", value)

    @property
    @jsii.member(jsii_name="events")
    def events(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.Mapping[str,typing.Union[aws_cdk.core.IResolvable, "EventSourceProperty"]]]]]:
        """``AWS::Serverless::Function.Events``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessfunction
        """
        return jsii.get(self, "events")

    @events.setter
    def events(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.Mapping[str,typing.Union[aws_cdk.core.IResolvable, "EventSourceProperty"]]]]]):
        return jsii.set(self, "events", value)

    @property
    @jsii.member(jsii_name="functionName")
    def function_name(self) -> typing.Optional[str]:
        """``AWS::Serverless::Function.FunctionName``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessfunction
        """
        return jsii.get(self, "functionName")

    @function_name.setter
    def function_name(self, value: typing.Optional[str]):
        return jsii.set(self, "functionName", value)

    @property
    @jsii.member(jsii_name="kmsKeyArn")
    def kms_key_arn(self) -> typing.Optional[str]:
        """``AWS::Serverless::Function.KmsKeyArn``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessfunction
        """
        return jsii.get(self, "kmsKeyArn")

    @kms_key_arn.setter
    def kms_key_arn(self, value: typing.Optional[str]):
        return jsii.set(self, "kmsKeyArn", value)

    @property
    @jsii.member(jsii_name="layers")
    def layers(self) -> typing.Optional[typing.List[str]]:
        """``AWS::Serverless::Function.Layers``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessfunction
        """
        return jsii.get(self, "layers")

    @layers.setter
    def layers(self, value: typing.Optional[typing.List[str]]):
        return jsii.set(self, "layers", value)

    @property
    @jsii.member(jsii_name="memorySize")
    def memory_size(self) -> typing.Optional[jsii.Number]:
        """``AWS::Serverless::Function.MemorySize``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessfunction
        """
        return jsii.get(self, "memorySize")

    @memory_size.setter
    def memory_size(self, value: typing.Optional[jsii.Number]):
        return jsii.set(self, "memorySize", value)

    @property
    @jsii.member(jsii_name="permissionsBoundary")
    def permissions_boundary(self) -> typing.Optional[str]:
        """``AWS::Serverless::Function.PermissionsBoundary``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessfunction
        """
        return jsii.get(self, "permissionsBoundary")

    @permissions_boundary.setter
    def permissions_boundary(self, value: typing.Optional[str]):
        return jsii.set(self, "permissionsBoundary", value)

    @property
    @jsii.member(jsii_name="policies")
    def policies(self) -> typing.Optional[typing.Union[typing.Optional[str], typing.Optional[aws_cdk.core.IResolvable], typing.Optional["IAMPolicyDocumentProperty"], typing.Optional[typing.List[typing.Union[str, aws_cdk.core.IResolvable, "IAMPolicyDocumentProperty", "SAMPolicyTemplateProperty"]]]]]:
        """``AWS::Serverless::Function.Policies``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessfunction
        """
        return jsii.get(self, "policies")

    @policies.setter
    def policies(self, value: typing.Optional[typing.Union[typing.Optional[str], typing.Optional[aws_cdk.core.IResolvable], typing.Optional["IAMPolicyDocumentProperty"], typing.Optional[typing.List[typing.Union[str, aws_cdk.core.IResolvable, "IAMPolicyDocumentProperty", "SAMPolicyTemplateProperty"]]]]]):
        return jsii.set(self, "policies", value)

    @property
    @jsii.member(jsii_name="reservedConcurrentExecutions")
    def reserved_concurrent_executions(self) -> typing.Optional[jsii.Number]:
        """``AWS::Serverless::Function.ReservedConcurrentExecutions``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessfunction
        """
        return jsii.get(self, "reservedConcurrentExecutions")

    @reserved_concurrent_executions.setter
    def reserved_concurrent_executions(self, value: typing.Optional[jsii.Number]):
        return jsii.set(self, "reservedConcurrentExecutions", value)

    @property
    @jsii.member(jsii_name="role")
    def role(self) -> typing.Optional[str]:
        """``AWS::Serverless::Function.Role``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessfunction
        """
        return jsii.get(self, "role")

    @role.setter
    def role(self, value: typing.Optional[str]):
        return jsii.set(self, "role", value)

    @property
    @jsii.member(jsii_name="timeout")
    def timeout(self) -> typing.Optional[jsii.Number]:
        """``AWS::Serverless::Function.Timeout``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessfunction
        """
        return jsii.get(self, "timeout")

    @timeout.setter
    def timeout(self, value: typing.Optional[jsii.Number]):
        return jsii.set(self, "timeout", value)

    @property
    @jsii.member(jsii_name="tracing")
    def tracing(self) -> typing.Optional[str]:
        """``AWS::Serverless::Function.Tracing``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessfunction
        """
        return jsii.get(self, "tracing")

    @tracing.setter
    def tracing(self, value: typing.Optional[str]):
        return jsii.set(self, "tracing", value)

    @property
    @jsii.member(jsii_name="vpcConfig")
    def vpc_config(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["VpcConfigProperty"]]]:
        """``AWS::Serverless::Function.VpcConfig``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessfunction
        """
        return jsii.get(self, "vpcConfig")

    @vpc_config.setter
    def vpc_config(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["VpcConfigProperty"]]]):
        return jsii.set(self, "vpcConfig", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-sam.CfnFunction.AlexaSkillEventProperty", jsii_struct_bases=[], name_mapping={'variables': 'variables'})
    class AlexaSkillEventProperty():
        def __init__(self, *, variables: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.Mapping[str,str]]]]=None):
            """
            :param variables: ``CfnFunction.AlexaSkillEventProperty.Variables``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#alexaskill
            """
            self._values = {
            }
            if variables is not None: self._values["variables"] = variables

        @property
        def variables(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.Mapping[str,str]]]]:
            """``CfnFunction.AlexaSkillEventProperty.Variables``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#alexaskill
            """
            return self._values.get('variables')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'AlexaSkillEventProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-sam.CfnFunction.ApiEventProperty", jsii_struct_bases=[], name_mapping={'method': 'method', 'path': 'path', 'rest_api_id': 'restApiId'})
    class ApiEventProperty():
        def __init__(self, *, method: str, path: str, rest_api_id: typing.Optional[str]=None):
            """
            :param method: ``CfnFunction.ApiEventProperty.Method``.
            :param path: ``CfnFunction.ApiEventProperty.Path``.
            :param rest_api_id: ``CfnFunction.ApiEventProperty.RestApiId``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#api
            """
            self._values = {
                'method': method,
                'path': path,
            }
            if rest_api_id is not None: self._values["rest_api_id"] = rest_api_id

        @property
        def method(self) -> str:
            """``CfnFunction.ApiEventProperty.Method``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#api
            """
            return self._values.get('method')

        @property
        def path(self) -> str:
            """``CfnFunction.ApiEventProperty.Path``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#api
            """
            return self._values.get('path')

        @property
        def rest_api_id(self) -> typing.Optional[str]:
            """``CfnFunction.ApiEventProperty.RestApiId``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#api
            """
            return self._values.get('rest_api_id')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'ApiEventProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-sam.CfnFunction.BucketSAMPTProperty", jsii_struct_bases=[], name_mapping={'bucket_name': 'bucketName'})
    class BucketSAMPTProperty():
        def __init__(self, *, bucket_name: str):
            """
            :param bucket_name: ``CfnFunction.BucketSAMPTProperty.BucketName``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/docs/policy_templates.rst
            """
            self._values = {
                'bucket_name': bucket_name,
            }

        @property
        def bucket_name(self) -> str:
            """``CfnFunction.BucketSAMPTProperty.BucketName``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/docs/policy_templates.rst
            """
            return self._values.get('bucket_name')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'BucketSAMPTProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-sam.CfnFunction.CloudWatchEventEventProperty", jsii_struct_bases=[], name_mapping={'pattern': 'pattern', 'input': 'input', 'input_path': 'inputPath'})
    class CloudWatchEventEventProperty():
        def __init__(self, *, pattern: typing.Any, input: typing.Optional[str]=None, input_path: typing.Optional[str]=None):
            """
            :param pattern: ``CfnFunction.CloudWatchEventEventProperty.Pattern``.
            :param input: ``CfnFunction.CloudWatchEventEventProperty.Input``.
            :param input_path: ``CfnFunction.CloudWatchEventEventProperty.InputPath``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#cloudwatchevent
            """
            self._values = {
                'pattern': pattern,
            }
            if input is not None: self._values["input"] = input
            if input_path is not None: self._values["input_path"] = input_path

        @property
        def pattern(self) -> typing.Any:
            """``CfnFunction.CloudWatchEventEventProperty.Pattern``.

            see
            :see: http://docs.aws.amazon.com/AmazonCloudWatch/latest/events/CloudWatchEventsandEventPatterns.html
            """
            return self._values.get('pattern')

        @property
        def input(self) -> typing.Optional[str]:
            """``CfnFunction.CloudWatchEventEventProperty.Input``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#cloudwatchevent
            """
            return self._values.get('input')

        @property
        def input_path(self) -> typing.Optional[str]:
            """``CfnFunction.CloudWatchEventEventProperty.InputPath``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#cloudwatchevent
            """
            return self._values.get('input_path')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'CloudWatchEventEventProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-sam.CfnFunction.CollectionSAMPTProperty", jsii_struct_bases=[], name_mapping={'collection_id': 'collectionId'})
    class CollectionSAMPTProperty():
        def __init__(self, *, collection_id: str):
            """
            :param collection_id: ``CfnFunction.CollectionSAMPTProperty.CollectionId``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/docs/policy_templates.rst
            """
            self._values = {
                'collection_id': collection_id,
            }

        @property
        def collection_id(self) -> str:
            """``CfnFunction.CollectionSAMPTProperty.CollectionId``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/docs/policy_templates.rst
            """
            return self._values.get('collection_id')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'CollectionSAMPTProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-sam.CfnFunction.DeadLetterQueueProperty", jsii_struct_bases=[], name_mapping={'target_arn': 'targetArn', 'type': 'type'})
    class DeadLetterQueueProperty():
        def __init__(self, *, target_arn: str, type: str):
            """
            :param target_arn: ``CfnFunction.DeadLetterQueueProperty.TargetArn``.
            :param type: ``CfnFunction.DeadLetterQueueProperty.Type``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#deadletterqueue-object
            """
            self._values = {
                'target_arn': target_arn,
                'type': type,
            }

        @property
        def target_arn(self) -> str:
            """``CfnFunction.DeadLetterQueueProperty.TargetArn``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessfunction
            """
            return self._values.get('target_arn')

        @property
        def type(self) -> str:
            """``CfnFunction.DeadLetterQueueProperty.Type``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessfunction
            """
            return self._values.get('type')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'DeadLetterQueueProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-sam.CfnFunction.DeploymentPreferenceProperty", jsii_struct_bases=[], name_mapping={'enabled': 'enabled', 'type': 'type', 'alarms': 'alarms', 'hooks': 'hooks'})
    class DeploymentPreferenceProperty():
        def __init__(self, *, enabled: typing.Union[bool, aws_cdk.core.IResolvable], type: str, alarms: typing.Optional[typing.List[str]]=None, hooks: typing.Optional[typing.List[str]]=None):
            """
            :param enabled: ``CfnFunction.DeploymentPreferenceProperty.Enabled``.
            :param type: ``CfnFunction.DeploymentPreferenceProperty.Type``.
            :param alarms: ``CfnFunction.DeploymentPreferenceProperty.Alarms``.
            :param hooks: ``CfnFunction.DeploymentPreferenceProperty.Hooks``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/docs/safe_lambda_deployments.rst
            """
            self._values = {
                'enabled': enabled,
                'type': type,
            }
            if alarms is not None: self._values["alarms"] = alarms
            if hooks is not None: self._values["hooks"] = hooks

        @property
        def enabled(self) -> typing.Union[bool, aws_cdk.core.IResolvable]:
            """``CfnFunction.DeploymentPreferenceProperty.Enabled``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#deploymentpreference-object
            """
            return self._values.get('enabled')

        @property
        def type(self) -> str:
            """``CfnFunction.DeploymentPreferenceProperty.Type``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#deploymentpreference-object
            """
            return self._values.get('type')

        @property
        def alarms(self) -> typing.Optional[typing.List[str]]:
            """``CfnFunction.DeploymentPreferenceProperty.Alarms``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#deploymentpreference-object
            """
            return self._values.get('alarms')

        @property
        def hooks(self) -> typing.Optional[typing.List[str]]:
            """``CfnFunction.DeploymentPreferenceProperty.Hooks``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#deploymentpreference-object
            """
            return self._values.get('hooks')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'DeploymentPreferenceProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-sam.CfnFunction.DomainSAMPTProperty", jsii_struct_bases=[], name_mapping={'domain_name': 'domainName'})
    class DomainSAMPTProperty():
        def __init__(self, *, domain_name: str):
            """
            :param domain_name: ``CfnFunction.DomainSAMPTProperty.DomainName``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/docs/policy_templates.rst
            """
            self._values = {
                'domain_name': domain_name,
            }

        @property
        def domain_name(self) -> str:
            """``CfnFunction.DomainSAMPTProperty.DomainName``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/docs/policy_templates.rst
            """
            return self._values.get('domain_name')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'DomainSAMPTProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-sam.CfnFunction.DynamoDBEventProperty", jsii_struct_bases=[], name_mapping={'starting_position': 'startingPosition', 'stream': 'stream', 'batch_size': 'batchSize', 'enabled': 'enabled'})
    class DynamoDBEventProperty():
        def __init__(self, *, starting_position: str, stream: str, batch_size: typing.Optional[jsii.Number]=None, enabled: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None):
            """
            :param starting_position: ``CfnFunction.DynamoDBEventProperty.StartingPosition``.
            :param stream: ``CfnFunction.DynamoDBEventProperty.Stream``.
            :param batch_size: ``CfnFunction.DynamoDBEventProperty.BatchSize``.
            :param enabled: ``CfnFunction.DynamoDBEventProperty.Enabled``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#dynamodb
            """
            self._values = {
                'starting_position': starting_position,
                'stream': stream,
            }
            if batch_size is not None: self._values["batch_size"] = batch_size
            if enabled is not None: self._values["enabled"] = enabled

        @property
        def starting_position(self) -> str:
            """``CfnFunction.DynamoDBEventProperty.StartingPosition``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#dynamodb
            """
            return self._values.get('starting_position')

        @property
        def stream(self) -> str:
            """``CfnFunction.DynamoDBEventProperty.Stream``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#dynamodb
            """
            return self._values.get('stream')

        @property
        def batch_size(self) -> typing.Optional[jsii.Number]:
            """``CfnFunction.DynamoDBEventProperty.BatchSize``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#dynamodb
            """
            return self._values.get('batch_size')

        @property
        def enabled(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
            """``CfnFunction.DynamoDBEventProperty.Enabled``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#dynamodb
            """
            return self._values.get('enabled')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'DynamoDBEventProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-sam.CfnFunction.EmptySAMPTProperty", jsii_struct_bases=[], name_mapping={})
    class EmptySAMPTProperty():
        def __init__(self):
            """
            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/docs/policy_templates.rst
            """
            self._values = {
            }

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'EmptySAMPTProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-sam.CfnFunction.EventSourceProperty", jsii_struct_bases=[], name_mapping={'properties': 'properties', 'type': 'type'})
    class EventSourceProperty():
        def __init__(self, *, properties: typing.Union[aws_cdk.core.IResolvable, "CfnFunction.AlexaSkillEventProperty", "CfnFunction.ApiEventProperty", "CfnFunction.CloudWatchEventEventProperty", "CfnFunction.DynamoDBEventProperty", "CfnFunction.IoTRuleEventProperty", "CfnFunction.KinesisEventProperty", "CfnFunction.S3EventProperty", "CfnFunction.SNSEventProperty", "CfnFunction.SQSEventProperty", "CfnFunction.ScheduleEventProperty"], type: str):
            """
            :param properties: ``CfnFunction.EventSourceProperty.Properties``.
            :param type: ``CfnFunction.EventSourceProperty.Type``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#event-source-object
            """
            self._values = {
                'properties': properties,
                'type': type,
            }

        @property
        def properties(self) -> typing.Union[aws_cdk.core.IResolvable, "CfnFunction.AlexaSkillEventProperty", "CfnFunction.ApiEventProperty", "CfnFunction.CloudWatchEventEventProperty", "CfnFunction.DynamoDBEventProperty", "CfnFunction.IoTRuleEventProperty", "CfnFunction.KinesisEventProperty", "CfnFunction.S3EventProperty", "CfnFunction.SNSEventProperty", "CfnFunction.SQSEventProperty", "CfnFunction.ScheduleEventProperty"]:
            """``CfnFunction.EventSourceProperty.Properties``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#event-source-types
            """
            return self._values.get('properties')

        @property
        def type(self) -> str:
            """``CfnFunction.EventSourceProperty.Type``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#event-source-object
            """
            return self._values.get('type')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'EventSourceProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-sam.CfnFunction.FunctionEnvironmentProperty", jsii_struct_bases=[], name_mapping={'variables': 'variables'})
    class FunctionEnvironmentProperty():
        def __init__(self, *, variables: typing.Union[aws_cdk.core.IResolvable, typing.Mapping[str,str]]):
            """
            :param variables: ``CfnFunction.FunctionEnvironmentProperty.Variables``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#environment-object
            """
            self._values = {
                'variables': variables,
            }

        @property
        def variables(self) -> typing.Union[aws_cdk.core.IResolvable, typing.Mapping[str,str]]:
            """``CfnFunction.FunctionEnvironmentProperty.Variables``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#environment-object
            """
            return self._values.get('variables')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'FunctionEnvironmentProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-sam.CfnFunction.FunctionSAMPTProperty", jsii_struct_bases=[], name_mapping={'function_name': 'functionName'})
    class FunctionSAMPTProperty():
        def __init__(self, *, function_name: str):
            """
            :param function_name: ``CfnFunction.FunctionSAMPTProperty.FunctionName``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/docs/policy_templates.rst
            """
            self._values = {
                'function_name': function_name,
            }

        @property
        def function_name(self) -> str:
            """``CfnFunction.FunctionSAMPTProperty.FunctionName``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/docs/policy_templates.rst
            """
            return self._values.get('function_name')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'FunctionSAMPTProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.interface(jsii_type="@aws-cdk/aws-sam.CfnFunction.IAMPolicyDocumentProperty")
    class IAMPolicyDocumentProperty(jsii.compat.Protocol):
        """
        see
        :see: http://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies.html
        """
        @staticmethod
        def __jsii_proxy_class__():
            return _IAMPolicyDocumentPropertyProxy

        @property
        @jsii.member(jsii_name="statement")
        def statement(self) -> typing.Any:
            """``CfnFunction.IAMPolicyDocumentProperty.Statement``.

            see
            :see: http://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies.html
            """
            ...


    class _IAMPolicyDocumentPropertyProxy():
        """
        see
        :see: http://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies.html
        """
        __jsii_type__ = "@aws-cdk/aws-sam.CfnFunction.IAMPolicyDocumentProperty"
        @property
        @jsii.member(jsii_name="statement")
        def statement(self) -> typing.Any:
            """``CfnFunction.IAMPolicyDocumentProperty.Statement``.

            see
            :see: http://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies.html
            """
            return jsii.get(self, "statement")


    @jsii.data_type(jsii_type="@aws-cdk/aws-sam.CfnFunction.IdentitySAMPTProperty", jsii_struct_bases=[], name_mapping={'identity_name': 'identityName'})
    class IdentitySAMPTProperty():
        def __init__(self, *, identity_name: str):
            """
            :param identity_name: ``CfnFunction.IdentitySAMPTProperty.IdentityName``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/docs/policy_templates.rst
            """
            self._values = {
                'identity_name': identity_name,
            }

        @property
        def identity_name(self) -> str:
            """``CfnFunction.IdentitySAMPTProperty.IdentityName``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/docs/policy_templates.rst
            """
            return self._values.get('identity_name')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'IdentitySAMPTProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-sam.CfnFunction.IoTRuleEventProperty", jsii_struct_bases=[], name_mapping={'sql': 'sql', 'aws_iot_sql_version': 'awsIotSqlVersion'})
    class IoTRuleEventProperty():
        def __init__(self, *, sql: str, aws_iot_sql_version: typing.Optional[str]=None):
            """
            :param sql: ``CfnFunction.IoTRuleEventProperty.Sql``.
            :param aws_iot_sql_version: ``CfnFunction.IoTRuleEventProperty.AwsIotSqlVersion``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#iotrule
            """
            self._values = {
                'sql': sql,
            }
            if aws_iot_sql_version is not None: self._values["aws_iot_sql_version"] = aws_iot_sql_version

        @property
        def sql(self) -> str:
            """``CfnFunction.IoTRuleEventProperty.Sql``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#iotrule
            """
            return self._values.get('sql')

        @property
        def aws_iot_sql_version(self) -> typing.Optional[str]:
            """``CfnFunction.IoTRuleEventProperty.AwsIotSqlVersion``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#iotrule
            """
            return self._values.get('aws_iot_sql_version')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'IoTRuleEventProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-sam.CfnFunction.KeySAMPTProperty", jsii_struct_bases=[], name_mapping={'key_id': 'keyId'})
    class KeySAMPTProperty():
        def __init__(self, *, key_id: str):
            """
            :param key_id: ``CfnFunction.KeySAMPTProperty.KeyId``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/docs/policy_templates.rst
            """
            self._values = {
                'key_id': key_id,
            }

        @property
        def key_id(self) -> str:
            """``CfnFunction.KeySAMPTProperty.KeyId``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/docs/policy_templates.rst
            """
            return self._values.get('key_id')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'KeySAMPTProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-sam.CfnFunction.KinesisEventProperty", jsii_struct_bases=[], name_mapping={'starting_position': 'startingPosition', 'stream': 'stream', 'batch_size': 'batchSize', 'enabled': 'enabled'})
    class KinesisEventProperty():
        def __init__(self, *, starting_position: str, stream: str, batch_size: typing.Optional[jsii.Number]=None, enabled: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None):
            """
            :param starting_position: ``CfnFunction.KinesisEventProperty.StartingPosition``.
            :param stream: ``CfnFunction.KinesisEventProperty.Stream``.
            :param batch_size: ``CfnFunction.KinesisEventProperty.BatchSize``.
            :param enabled: ``CfnFunction.KinesisEventProperty.Enabled``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#kinesis
            """
            self._values = {
                'starting_position': starting_position,
                'stream': stream,
            }
            if batch_size is not None: self._values["batch_size"] = batch_size
            if enabled is not None: self._values["enabled"] = enabled

        @property
        def starting_position(self) -> str:
            """``CfnFunction.KinesisEventProperty.StartingPosition``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#kinesis
            """
            return self._values.get('starting_position')

        @property
        def stream(self) -> str:
            """``CfnFunction.KinesisEventProperty.Stream``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#kinesis
            """
            return self._values.get('stream')

        @property
        def batch_size(self) -> typing.Optional[jsii.Number]:
            """``CfnFunction.KinesisEventProperty.BatchSize``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#kinesis
            """
            return self._values.get('batch_size')

        @property
        def enabled(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
            """``CfnFunction.KinesisEventProperty.Enabled``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#kinesis
            """
            return self._values.get('enabled')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'KinesisEventProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-sam.CfnFunction.LogGroupSAMPTProperty", jsii_struct_bases=[], name_mapping={'log_group_name': 'logGroupName'})
    class LogGroupSAMPTProperty():
        def __init__(self, *, log_group_name: str):
            """
            :param log_group_name: ``CfnFunction.LogGroupSAMPTProperty.LogGroupName``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/docs/policy_templates.rst
            """
            self._values = {
                'log_group_name': log_group_name,
            }

        @property
        def log_group_name(self) -> str:
            """``CfnFunction.LogGroupSAMPTProperty.LogGroupName``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/docs/policy_templates.rst
            """
            return self._values.get('log_group_name')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'LogGroupSAMPTProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-sam.CfnFunction.QueueSAMPTProperty", jsii_struct_bases=[], name_mapping={'queue_name': 'queueName'})
    class QueueSAMPTProperty():
        def __init__(self, *, queue_name: str):
            """
            :param queue_name: ``CfnFunction.QueueSAMPTProperty.QueueName``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/docs/policy_templates.rst
            """
            self._values = {
                'queue_name': queue_name,
            }

        @property
        def queue_name(self) -> str:
            """``CfnFunction.QueueSAMPTProperty.QueueName``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/docs/policy_templates.rst
            """
            return self._values.get('queue_name')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'QueueSAMPTProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-sam.CfnFunction.S3EventProperty", jsii_struct_bases=[], name_mapping={'bucket': 'bucket', 'events': 'events', 'filter': 'filter'})
    class S3EventProperty():
        def __init__(self, *, bucket: str, events: typing.Union[str, aws_cdk.core.IResolvable, typing.List[str]], filter: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnFunction.S3NotificationFilterProperty"]]]=None):
            """
            :param bucket: ``CfnFunction.S3EventProperty.Bucket``.
            :param events: ``CfnFunction.S3EventProperty.Events``.
            :param filter: ``CfnFunction.S3EventProperty.Filter``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#s3
            """
            self._values = {
                'bucket': bucket,
                'events': events,
            }
            if filter is not None: self._values["filter"] = filter

        @property
        def bucket(self) -> str:
            """``CfnFunction.S3EventProperty.Bucket``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#s3
            """
            return self._values.get('bucket')

        @property
        def events(self) -> typing.Union[str, aws_cdk.core.IResolvable, typing.List[str]]:
            """``CfnFunction.S3EventProperty.Events``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#s3
            """
            return self._values.get('events')

        @property
        def filter(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnFunction.S3NotificationFilterProperty"]]]:
            """``CfnFunction.S3EventProperty.Filter``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#s3
            """
            return self._values.get('filter')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'S3EventProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-sam.CfnFunction.S3LocationProperty", jsii_struct_bases=[], name_mapping={'bucket': 'bucket', 'key': 'key', 'version': 'version'})
    class S3LocationProperty():
        def __init__(self, *, bucket: str, key: str, version: typing.Optional[jsii.Number]=None):
            """
            :param bucket: ``CfnFunction.S3LocationProperty.Bucket``.
            :param key: ``CfnFunction.S3LocationProperty.Key``.
            :param version: ``CfnFunction.S3LocationProperty.Version``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#s3-location-object
            """
            self._values = {
                'bucket': bucket,
                'key': key,
            }
            if version is not None: self._values["version"] = version

        @property
        def bucket(self) -> str:
            """``CfnFunction.S3LocationProperty.Bucket``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessfunction
            """
            return self._values.get('bucket')

        @property
        def key(self) -> str:
            """``CfnFunction.S3LocationProperty.Key``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessfunction
            """
            return self._values.get('key')

        @property
        def version(self) -> typing.Optional[jsii.Number]:
            """``CfnFunction.S3LocationProperty.Version``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessfunction
            """
            return self._values.get('version')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'S3LocationProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-sam.CfnFunction.S3NotificationFilterProperty", jsii_struct_bases=[], name_mapping={'s3_key': 's3Key'})
    class S3NotificationFilterProperty():
        def __init__(self, *, s3_key: str):
            """
            :param s3_key: ``CfnFunction.S3NotificationFilterProperty.S3Key``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-notificationconfiguration-config-filter.html
            """
            self._values = {
                's3_key': s3_key,
            }

        @property
        def s3_key(self) -> str:
            """``CfnFunction.S3NotificationFilterProperty.S3Key``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-notificationconfiguration-config-filter.html
            """
            return self._values.get('s3_key')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'S3NotificationFilterProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-sam.CfnFunction.SAMPolicyTemplateProperty", jsii_struct_bases=[], name_mapping={'ami_describe_policy': 'amiDescribePolicy', 'cloud_formation_describe_stacks_policy': 'cloudFormationDescribeStacksPolicy', 'cloud_watch_put_metric_policy': 'cloudWatchPutMetricPolicy', 'dynamo_db_crud_policy': 'dynamoDbCrudPolicy', 'dynamo_db_read_policy': 'dynamoDbReadPolicy', 'dynamo_db_stream_read_policy': 'dynamoDbStreamReadPolicy', 'ec2_describe_policy': 'ec2DescribePolicy', 'elasticsearch_http_post_policy': 'elasticsearchHttpPostPolicy', 'filter_log_events_policy': 'filterLogEventsPolicy', 'kinesis_crud_policy': 'kinesisCrudPolicy', 'kinesis_stream_read_policy': 'kinesisStreamReadPolicy', 'kms_decrypt_policy': 'kmsDecryptPolicy', 'lambda_invoke_policy': 'lambdaInvokePolicy', 'rekognition_detect_only_policy': 'rekognitionDetectOnlyPolicy', 'rekognition_labels_policy': 'rekognitionLabelsPolicy', 'rekognition_no_data_access_policy': 'rekognitionNoDataAccessPolicy', 'rekognition_read_policy': 'rekognitionReadPolicy', 'rekognition_write_only_access_policy': 'rekognitionWriteOnlyAccessPolicy', 's3_crud_policy': 's3CrudPolicy', 's3_read_policy': 's3ReadPolicy', 'ses_bulk_templated_crud_policy': 'sesBulkTemplatedCrudPolicy', 'ses_crud_policy': 'sesCrudPolicy', 'ses_email_template_crud_policy': 'sesEmailTemplateCrudPolicy', 'ses_send_bounce_policy': 'sesSendBouncePolicy', 'sns_crud_policy': 'snsCrudPolicy', 'sns_publish_message_policy': 'snsPublishMessagePolicy', 'sqs_poller_policy': 'sqsPollerPolicy', 'sqs_send_message_policy': 'sqsSendMessagePolicy', 'step_functions_execution_policy': 'stepFunctionsExecutionPolicy', 'vpc_access_policy': 'vpcAccessPolicy'})
    class SAMPolicyTemplateProperty():
        def __init__(self, *, ami_describe_policy: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnFunction.EmptySAMPTProperty"]]]=None, cloud_formation_describe_stacks_policy: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnFunction.EmptySAMPTProperty"]]]=None, cloud_watch_put_metric_policy: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnFunction.EmptySAMPTProperty"]]]=None, dynamo_db_crud_policy: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnFunction.TableSAMPTProperty"]]]=None, dynamo_db_read_policy: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnFunction.TableSAMPTProperty"]]]=None, dynamo_db_stream_read_policy: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnFunction.TableStreamSAMPTProperty"]]]=None, ec2_describe_policy: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnFunction.EmptySAMPTProperty"]]]=None, elasticsearch_http_post_policy: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnFunction.DomainSAMPTProperty"]]]=None, filter_log_events_policy: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnFunction.LogGroupSAMPTProperty"]]]=None, kinesis_crud_policy: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnFunction.StreamSAMPTProperty"]]]=None, kinesis_stream_read_policy: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnFunction.StreamSAMPTProperty"]]]=None, kms_decrypt_policy: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnFunction.KeySAMPTProperty"]]]=None, lambda_invoke_policy: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnFunction.FunctionSAMPTProperty"]]]=None, rekognition_detect_only_policy: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnFunction.EmptySAMPTProperty"]]]=None, rekognition_labels_policy: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnFunction.EmptySAMPTProperty"]]]=None, rekognition_no_data_access_policy: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnFunction.CollectionSAMPTProperty"]]]=None, rekognition_read_policy: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnFunction.CollectionSAMPTProperty"]]]=None, rekognition_write_only_access_policy: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnFunction.CollectionSAMPTProperty"]]]=None, s3_crud_policy: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnFunction.BucketSAMPTProperty"]]]=None, s3_read_policy: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnFunction.BucketSAMPTProperty"]]]=None, ses_bulk_templated_crud_policy: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnFunction.IdentitySAMPTProperty"]]]=None, ses_crud_policy: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnFunction.IdentitySAMPTProperty"]]]=None, ses_email_template_crud_policy: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnFunction.EmptySAMPTProperty"]]]=None, ses_send_bounce_policy: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnFunction.IdentitySAMPTProperty"]]]=None, sns_crud_policy: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnFunction.TopicSAMPTProperty"]]]=None, sns_publish_message_policy: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnFunction.TopicSAMPTProperty"]]]=None, sqs_poller_policy: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnFunction.QueueSAMPTProperty"]]]=None, sqs_send_message_policy: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnFunction.QueueSAMPTProperty"]]]=None, step_functions_execution_policy: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnFunction.StateMachineSAMPTProperty"]]]=None, vpc_access_policy: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnFunction.EmptySAMPTProperty"]]]=None):
            """
            :param ami_describe_policy: ``CfnFunction.SAMPolicyTemplateProperty.AMIDescribePolicy``.
            :param cloud_formation_describe_stacks_policy: ``CfnFunction.SAMPolicyTemplateProperty.CloudFormationDescribeStacksPolicy``.
            :param cloud_watch_put_metric_policy: ``CfnFunction.SAMPolicyTemplateProperty.CloudWatchPutMetricPolicy``.
            :param dynamo_db_crud_policy: ``CfnFunction.SAMPolicyTemplateProperty.DynamoDBCrudPolicy``.
            :param dynamo_db_read_policy: ``CfnFunction.SAMPolicyTemplateProperty.DynamoDBReadPolicy``.
            :param dynamo_db_stream_read_policy: ``CfnFunction.SAMPolicyTemplateProperty.DynamoDBStreamReadPolicy``.
            :param ec2_describe_policy: ``CfnFunction.SAMPolicyTemplateProperty.EC2DescribePolicy``.
            :param elasticsearch_http_post_policy: ``CfnFunction.SAMPolicyTemplateProperty.ElasticsearchHttpPostPolicy``.
            :param filter_log_events_policy: ``CfnFunction.SAMPolicyTemplateProperty.FilterLogEventsPolicy``.
            :param kinesis_crud_policy: ``CfnFunction.SAMPolicyTemplateProperty.KinesisCrudPolicy``.
            :param kinesis_stream_read_policy: ``CfnFunction.SAMPolicyTemplateProperty.KinesisStreamReadPolicy``.
            :param kms_decrypt_policy: ``CfnFunction.SAMPolicyTemplateProperty.KMSDecryptPolicy``.
            :param lambda_invoke_policy: ``CfnFunction.SAMPolicyTemplateProperty.LambdaInvokePolicy``.
            :param rekognition_detect_only_policy: ``CfnFunction.SAMPolicyTemplateProperty.RekognitionDetectOnlyPolicy``.
            :param rekognition_labels_policy: ``CfnFunction.SAMPolicyTemplateProperty.RekognitionLabelsPolicy``.
            :param rekognition_no_data_access_policy: ``CfnFunction.SAMPolicyTemplateProperty.RekognitionNoDataAccessPolicy``.
            :param rekognition_read_policy: ``CfnFunction.SAMPolicyTemplateProperty.RekognitionReadPolicy``.
            :param rekognition_write_only_access_policy: ``CfnFunction.SAMPolicyTemplateProperty.RekognitionWriteOnlyAccessPolicy``.
            :param s3_crud_policy: ``CfnFunction.SAMPolicyTemplateProperty.S3CrudPolicy``.
            :param s3_read_policy: ``CfnFunction.SAMPolicyTemplateProperty.S3ReadPolicy``.
            :param ses_bulk_templated_crud_policy: ``CfnFunction.SAMPolicyTemplateProperty.SESBulkTemplatedCrudPolicy``.
            :param ses_crud_policy: ``CfnFunction.SAMPolicyTemplateProperty.SESCrudPolicy``.
            :param ses_email_template_crud_policy: ``CfnFunction.SAMPolicyTemplateProperty.SESEmailTemplateCrudPolicy``.
            :param ses_send_bounce_policy: ``CfnFunction.SAMPolicyTemplateProperty.SESSendBouncePolicy``.
            :param sns_crud_policy: ``CfnFunction.SAMPolicyTemplateProperty.SNSCrudPolicy``.
            :param sns_publish_message_policy: ``CfnFunction.SAMPolicyTemplateProperty.SNSPublishMessagePolicy``.
            :param sqs_poller_policy: ``CfnFunction.SAMPolicyTemplateProperty.SQSPollerPolicy``.
            :param sqs_send_message_policy: ``CfnFunction.SAMPolicyTemplateProperty.SQSSendMessagePolicy``.
            :param step_functions_execution_policy: ``CfnFunction.SAMPolicyTemplateProperty.StepFunctionsExecutionPolicy``.
            :param vpc_access_policy: ``CfnFunction.SAMPolicyTemplateProperty.VPCAccessPolicy``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/docs/policy_templates.rst
            """
            self._values = {
            }
            if ami_describe_policy is not None: self._values["ami_describe_policy"] = ami_describe_policy
            if cloud_formation_describe_stacks_policy is not None: self._values["cloud_formation_describe_stacks_policy"] = cloud_formation_describe_stacks_policy
            if cloud_watch_put_metric_policy is not None: self._values["cloud_watch_put_metric_policy"] = cloud_watch_put_metric_policy
            if dynamo_db_crud_policy is not None: self._values["dynamo_db_crud_policy"] = dynamo_db_crud_policy
            if dynamo_db_read_policy is not None: self._values["dynamo_db_read_policy"] = dynamo_db_read_policy
            if dynamo_db_stream_read_policy is not None: self._values["dynamo_db_stream_read_policy"] = dynamo_db_stream_read_policy
            if ec2_describe_policy is not None: self._values["ec2_describe_policy"] = ec2_describe_policy
            if elasticsearch_http_post_policy is not None: self._values["elasticsearch_http_post_policy"] = elasticsearch_http_post_policy
            if filter_log_events_policy is not None: self._values["filter_log_events_policy"] = filter_log_events_policy
            if kinesis_crud_policy is not None: self._values["kinesis_crud_policy"] = kinesis_crud_policy
            if kinesis_stream_read_policy is not None: self._values["kinesis_stream_read_policy"] = kinesis_stream_read_policy
            if kms_decrypt_policy is not None: self._values["kms_decrypt_policy"] = kms_decrypt_policy
            if lambda_invoke_policy is not None: self._values["lambda_invoke_policy"] = lambda_invoke_policy
            if rekognition_detect_only_policy is not None: self._values["rekognition_detect_only_policy"] = rekognition_detect_only_policy
            if rekognition_labels_policy is not None: self._values["rekognition_labels_policy"] = rekognition_labels_policy
            if rekognition_no_data_access_policy is not None: self._values["rekognition_no_data_access_policy"] = rekognition_no_data_access_policy
            if rekognition_read_policy is not None: self._values["rekognition_read_policy"] = rekognition_read_policy
            if rekognition_write_only_access_policy is not None: self._values["rekognition_write_only_access_policy"] = rekognition_write_only_access_policy
            if s3_crud_policy is not None: self._values["s3_crud_policy"] = s3_crud_policy
            if s3_read_policy is not None: self._values["s3_read_policy"] = s3_read_policy
            if ses_bulk_templated_crud_policy is not None: self._values["ses_bulk_templated_crud_policy"] = ses_bulk_templated_crud_policy
            if ses_crud_policy is not None: self._values["ses_crud_policy"] = ses_crud_policy
            if ses_email_template_crud_policy is not None: self._values["ses_email_template_crud_policy"] = ses_email_template_crud_policy
            if ses_send_bounce_policy is not None: self._values["ses_send_bounce_policy"] = ses_send_bounce_policy
            if sns_crud_policy is not None: self._values["sns_crud_policy"] = sns_crud_policy
            if sns_publish_message_policy is not None: self._values["sns_publish_message_policy"] = sns_publish_message_policy
            if sqs_poller_policy is not None: self._values["sqs_poller_policy"] = sqs_poller_policy
            if sqs_send_message_policy is not None: self._values["sqs_send_message_policy"] = sqs_send_message_policy
            if step_functions_execution_policy is not None: self._values["step_functions_execution_policy"] = step_functions_execution_policy
            if vpc_access_policy is not None: self._values["vpc_access_policy"] = vpc_access_policy

        @property
        def ami_describe_policy(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnFunction.EmptySAMPTProperty"]]]:
            """``CfnFunction.SAMPolicyTemplateProperty.AMIDescribePolicy``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/docs/policy_templates.rst
            """
            return self._values.get('ami_describe_policy')

        @property
        def cloud_formation_describe_stacks_policy(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnFunction.EmptySAMPTProperty"]]]:
            """``CfnFunction.SAMPolicyTemplateProperty.CloudFormationDescribeStacksPolicy``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/docs/policy_templates.rst
            """
            return self._values.get('cloud_formation_describe_stacks_policy')

        @property
        def cloud_watch_put_metric_policy(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnFunction.EmptySAMPTProperty"]]]:
            """``CfnFunction.SAMPolicyTemplateProperty.CloudWatchPutMetricPolicy``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/docs/policy_templates.rst
            """
            return self._values.get('cloud_watch_put_metric_policy')

        @property
        def dynamo_db_crud_policy(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnFunction.TableSAMPTProperty"]]]:
            """``CfnFunction.SAMPolicyTemplateProperty.DynamoDBCrudPolicy``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/docs/policy_templates.rst
            """
            return self._values.get('dynamo_db_crud_policy')

        @property
        def dynamo_db_read_policy(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnFunction.TableSAMPTProperty"]]]:
            """``CfnFunction.SAMPolicyTemplateProperty.DynamoDBReadPolicy``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/docs/policy_templates.rst
            """
            return self._values.get('dynamo_db_read_policy')

        @property
        def dynamo_db_stream_read_policy(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnFunction.TableStreamSAMPTProperty"]]]:
            """``CfnFunction.SAMPolicyTemplateProperty.DynamoDBStreamReadPolicy``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/docs/policy_templates.rst
            """
            return self._values.get('dynamo_db_stream_read_policy')

        @property
        def ec2_describe_policy(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnFunction.EmptySAMPTProperty"]]]:
            """``CfnFunction.SAMPolicyTemplateProperty.EC2DescribePolicy``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/docs/policy_templates.rst
            """
            return self._values.get('ec2_describe_policy')

        @property
        def elasticsearch_http_post_policy(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnFunction.DomainSAMPTProperty"]]]:
            """``CfnFunction.SAMPolicyTemplateProperty.ElasticsearchHttpPostPolicy``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/docs/policy_templates.rst
            """
            return self._values.get('elasticsearch_http_post_policy')

        @property
        def filter_log_events_policy(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnFunction.LogGroupSAMPTProperty"]]]:
            """``CfnFunction.SAMPolicyTemplateProperty.FilterLogEventsPolicy``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/docs/policy_templates.rst
            """
            return self._values.get('filter_log_events_policy')

        @property
        def kinesis_crud_policy(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnFunction.StreamSAMPTProperty"]]]:
            """``CfnFunction.SAMPolicyTemplateProperty.KinesisCrudPolicy``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/docs/policy_templates.rst
            """
            return self._values.get('kinesis_crud_policy')

        @property
        def kinesis_stream_read_policy(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnFunction.StreamSAMPTProperty"]]]:
            """``CfnFunction.SAMPolicyTemplateProperty.KinesisStreamReadPolicy``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/docs/policy_templates.rst
            """
            return self._values.get('kinesis_stream_read_policy')

        @property
        def kms_decrypt_policy(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnFunction.KeySAMPTProperty"]]]:
            """``CfnFunction.SAMPolicyTemplateProperty.KMSDecryptPolicy``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/docs/policy_templates.rst
            """
            return self._values.get('kms_decrypt_policy')

        @property
        def lambda_invoke_policy(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnFunction.FunctionSAMPTProperty"]]]:
            """``CfnFunction.SAMPolicyTemplateProperty.LambdaInvokePolicy``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/docs/policy_templates.rst
            """
            return self._values.get('lambda_invoke_policy')

        @property
        def rekognition_detect_only_policy(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnFunction.EmptySAMPTProperty"]]]:
            """``CfnFunction.SAMPolicyTemplateProperty.RekognitionDetectOnlyPolicy``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/docs/policy_templates.rst
            """
            return self._values.get('rekognition_detect_only_policy')

        @property
        def rekognition_labels_policy(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnFunction.EmptySAMPTProperty"]]]:
            """``CfnFunction.SAMPolicyTemplateProperty.RekognitionLabelsPolicy``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/docs/policy_templates.rst
            """
            return self._values.get('rekognition_labels_policy')

        @property
        def rekognition_no_data_access_policy(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnFunction.CollectionSAMPTProperty"]]]:
            """``CfnFunction.SAMPolicyTemplateProperty.RekognitionNoDataAccessPolicy``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/docs/policy_templates.rst
            """
            return self._values.get('rekognition_no_data_access_policy')

        @property
        def rekognition_read_policy(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnFunction.CollectionSAMPTProperty"]]]:
            """``CfnFunction.SAMPolicyTemplateProperty.RekognitionReadPolicy``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/docs/policy_templates.rst
            """
            return self._values.get('rekognition_read_policy')

        @property
        def rekognition_write_only_access_policy(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnFunction.CollectionSAMPTProperty"]]]:
            """``CfnFunction.SAMPolicyTemplateProperty.RekognitionWriteOnlyAccessPolicy``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/docs/policy_templates.rst
            """
            return self._values.get('rekognition_write_only_access_policy')

        @property
        def s3_crud_policy(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnFunction.BucketSAMPTProperty"]]]:
            """``CfnFunction.SAMPolicyTemplateProperty.S3CrudPolicy``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/docs/policy_templates.rst
            """
            return self._values.get('s3_crud_policy')

        @property
        def s3_read_policy(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnFunction.BucketSAMPTProperty"]]]:
            """``CfnFunction.SAMPolicyTemplateProperty.S3ReadPolicy``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/docs/policy_templates.rst
            """
            return self._values.get('s3_read_policy')

        @property
        def ses_bulk_templated_crud_policy(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnFunction.IdentitySAMPTProperty"]]]:
            """``CfnFunction.SAMPolicyTemplateProperty.SESBulkTemplatedCrudPolicy``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/docs/policy_templates.rst
            """
            return self._values.get('ses_bulk_templated_crud_policy')

        @property
        def ses_crud_policy(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnFunction.IdentitySAMPTProperty"]]]:
            """``CfnFunction.SAMPolicyTemplateProperty.SESCrudPolicy``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/docs/policy_templates.rst
            """
            return self._values.get('ses_crud_policy')

        @property
        def ses_email_template_crud_policy(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnFunction.EmptySAMPTProperty"]]]:
            """``CfnFunction.SAMPolicyTemplateProperty.SESEmailTemplateCrudPolicy``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/docs/policy_templates.rst
            """
            return self._values.get('ses_email_template_crud_policy')

        @property
        def ses_send_bounce_policy(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnFunction.IdentitySAMPTProperty"]]]:
            """``CfnFunction.SAMPolicyTemplateProperty.SESSendBouncePolicy``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/docs/policy_templates.rst
            """
            return self._values.get('ses_send_bounce_policy')

        @property
        def sns_crud_policy(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnFunction.TopicSAMPTProperty"]]]:
            """``CfnFunction.SAMPolicyTemplateProperty.SNSCrudPolicy``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/docs/policy_templates.rst
            """
            return self._values.get('sns_crud_policy')

        @property
        def sns_publish_message_policy(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnFunction.TopicSAMPTProperty"]]]:
            """``CfnFunction.SAMPolicyTemplateProperty.SNSPublishMessagePolicy``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/docs/policy_templates.rst
            """
            return self._values.get('sns_publish_message_policy')

        @property
        def sqs_poller_policy(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnFunction.QueueSAMPTProperty"]]]:
            """``CfnFunction.SAMPolicyTemplateProperty.SQSPollerPolicy``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/docs/policy_templates.rst
            """
            return self._values.get('sqs_poller_policy')

        @property
        def sqs_send_message_policy(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnFunction.QueueSAMPTProperty"]]]:
            """``CfnFunction.SAMPolicyTemplateProperty.SQSSendMessagePolicy``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/docs/policy_templates.rst
            """
            return self._values.get('sqs_send_message_policy')

        @property
        def step_functions_execution_policy(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnFunction.StateMachineSAMPTProperty"]]]:
            """``CfnFunction.SAMPolicyTemplateProperty.StepFunctionsExecutionPolicy``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/docs/policy_templates.rst
            """
            return self._values.get('step_functions_execution_policy')

        @property
        def vpc_access_policy(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnFunction.EmptySAMPTProperty"]]]:
            """``CfnFunction.SAMPolicyTemplateProperty.VPCAccessPolicy``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/docs/policy_templates.rst
            """
            return self._values.get('vpc_access_policy')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'SAMPolicyTemplateProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-sam.CfnFunction.SNSEventProperty", jsii_struct_bases=[], name_mapping={'topic': 'topic'})
    class SNSEventProperty():
        def __init__(self, *, topic: str):
            """
            :param topic: ``CfnFunction.SNSEventProperty.Topic``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#sns
            """
            self._values = {
                'topic': topic,
            }

        @property
        def topic(self) -> str:
            """``CfnFunction.SNSEventProperty.Topic``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#sns
            """
            return self._values.get('topic')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'SNSEventProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-sam.CfnFunction.SQSEventProperty", jsii_struct_bases=[], name_mapping={'queue': 'queue', 'batch_size': 'batchSize', 'enabled': 'enabled'})
    class SQSEventProperty():
        def __init__(self, *, queue: str, batch_size: typing.Optional[jsii.Number]=None, enabled: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None):
            """
            :param queue: ``CfnFunction.SQSEventProperty.Queue``.
            :param batch_size: ``CfnFunction.SQSEventProperty.BatchSize``.
            :param enabled: ``CfnFunction.SQSEventProperty.Enabled``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#sqs
            """
            self._values = {
                'queue': queue,
            }
            if batch_size is not None: self._values["batch_size"] = batch_size
            if enabled is not None: self._values["enabled"] = enabled

        @property
        def queue(self) -> str:
            """``CfnFunction.SQSEventProperty.Queue``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#sqs
            """
            return self._values.get('queue')

        @property
        def batch_size(self) -> typing.Optional[jsii.Number]:
            """``CfnFunction.SQSEventProperty.BatchSize``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#sqs
            """
            return self._values.get('batch_size')

        @property
        def enabled(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
            """``CfnFunction.SQSEventProperty.Enabled``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#sqs
            """
            return self._values.get('enabled')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'SQSEventProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-sam.CfnFunction.ScheduleEventProperty", jsii_struct_bases=[], name_mapping={'schedule': 'schedule', 'input': 'input'})
    class ScheduleEventProperty():
        def __init__(self, *, schedule: str, input: typing.Optional[str]=None):
            """
            :param schedule: ``CfnFunction.ScheduleEventProperty.Schedule``.
            :param input: ``CfnFunction.ScheduleEventProperty.Input``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#schedule
            """
            self._values = {
                'schedule': schedule,
            }
            if input is not None: self._values["input"] = input

        @property
        def schedule(self) -> str:
            """``CfnFunction.ScheduleEventProperty.Schedule``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#schedule
            """
            return self._values.get('schedule')

        @property
        def input(self) -> typing.Optional[str]:
            """``CfnFunction.ScheduleEventProperty.Input``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#schedule
            """
            return self._values.get('input')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'ScheduleEventProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-sam.CfnFunction.StateMachineSAMPTProperty", jsii_struct_bases=[], name_mapping={'state_machine_name': 'stateMachineName'})
    class StateMachineSAMPTProperty():
        def __init__(self, *, state_machine_name: str):
            """
            :param state_machine_name: ``CfnFunction.StateMachineSAMPTProperty.StateMachineName``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/docs/policy_templates.rst
            """
            self._values = {
                'state_machine_name': state_machine_name,
            }

        @property
        def state_machine_name(self) -> str:
            """``CfnFunction.StateMachineSAMPTProperty.StateMachineName``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/docs/policy_templates.rst
            """
            return self._values.get('state_machine_name')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'StateMachineSAMPTProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-sam.CfnFunction.StreamSAMPTProperty", jsii_struct_bases=[], name_mapping={'stream_name': 'streamName'})
    class StreamSAMPTProperty():
        def __init__(self, *, stream_name: str):
            """
            :param stream_name: ``CfnFunction.StreamSAMPTProperty.StreamName``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/docs/policy_templates.rst
            """
            self._values = {
                'stream_name': stream_name,
            }

        @property
        def stream_name(self) -> str:
            """``CfnFunction.StreamSAMPTProperty.StreamName``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/docs/policy_templates.rst
            """
            return self._values.get('stream_name')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'StreamSAMPTProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-sam.CfnFunction.TableSAMPTProperty", jsii_struct_bases=[], name_mapping={'table_name': 'tableName'})
    class TableSAMPTProperty():
        def __init__(self, *, table_name: str):
            """
            :param table_name: ``CfnFunction.TableSAMPTProperty.TableName``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/docs/policy_templates.rst
            """
            self._values = {
                'table_name': table_name,
            }

        @property
        def table_name(self) -> str:
            """``CfnFunction.TableSAMPTProperty.TableName``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/docs/policy_templates.rst
            """
            return self._values.get('table_name')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'TableSAMPTProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-sam.CfnFunction.TableStreamSAMPTProperty", jsii_struct_bases=[], name_mapping={'stream_name': 'streamName', 'table_name': 'tableName'})
    class TableStreamSAMPTProperty():
        def __init__(self, *, stream_name: str, table_name: str):
            """
            :param stream_name: ``CfnFunction.TableStreamSAMPTProperty.StreamName``.
            :param table_name: ``CfnFunction.TableStreamSAMPTProperty.TableName``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/docs/policy_templates.rst
            """
            self._values = {
                'stream_name': stream_name,
                'table_name': table_name,
            }

        @property
        def stream_name(self) -> str:
            """``CfnFunction.TableStreamSAMPTProperty.StreamName``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/docs/policy_templates.rst
            """
            return self._values.get('stream_name')

        @property
        def table_name(self) -> str:
            """``CfnFunction.TableStreamSAMPTProperty.TableName``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/docs/policy_templates.rst
            """
            return self._values.get('table_name')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'TableStreamSAMPTProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-sam.CfnFunction.TopicSAMPTProperty", jsii_struct_bases=[], name_mapping={'topic_name': 'topicName'})
    class TopicSAMPTProperty():
        def __init__(self, *, topic_name: str):
            """
            :param topic_name: ``CfnFunction.TopicSAMPTProperty.TopicName``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/docs/policy_templates.rst
            """
            self._values = {
                'topic_name': topic_name,
            }

        @property
        def topic_name(self) -> str:
            """``CfnFunction.TopicSAMPTProperty.TopicName``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/docs/policy_templates.rst
            """
            return self._values.get('topic_name')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'TopicSAMPTProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-sam.CfnFunction.VpcConfigProperty", jsii_struct_bases=[], name_mapping={'security_group_ids': 'securityGroupIds', 'subnet_ids': 'subnetIds'})
    class VpcConfigProperty():
        def __init__(self, *, security_group_ids: typing.List[str], subnet_ids: typing.List[str]):
            """
            :param security_group_ids: ``CfnFunction.VpcConfigProperty.SecurityGroupIds``.
            :param subnet_ids: ``CfnFunction.VpcConfigProperty.SubnetIds``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-lambda-function-vpcconfig.html
            """
            self._values = {
                'security_group_ids': security_group_ids,
                'subnet_ids': subnet_ids,
            }

        @property
        def security_group_ids(self) -> typing.List[str]:
            """``CfnFunction.VpcConfigProperty.SecurityGroupIds``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-lambda-function-vpcconfig.html
            """
            return self._values.get('security_group_ids')

        @property
        def subnet_ids(self) -> typing.List[str]:
            """``CfnFunction.VpcConfigProperty.SubnetIds``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-lambda-function-vpcconfig.html
            """
            return self._values.get('subnet_ids')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'VpcConfigProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



@jsii.data_type(jsii_type="@aws-cdk/aws-sam.CfnFunctionProps", jsii_struct_bases=[], name_mapping={'code_uri': 'codeUri', 'handler': 'handler', 'runtime': 'runtime', 'auto_publish_alias': 'autoPublishAlias', 'dead_letter_queue': 'deadLetterQueue', 'deployment_preference': 'deploymentPreference', 'description': 'description', 'environment': 'environment', 'events': 'events', 'function_name': 'functionName', 'kms_key_arn': 'kmsKeyArn', 'layers': 'layers', 'memory_size': 'memorySize', 'permissions_boundary': 'permissionsBoundary', 'policies': 'policies', 'reserved_concurrent_executions': 'reservedConcurrentExecutions', 'role': 'role', 'tags': 'tags', 'timeout': 'timeout', 'tracing': 'tracing', 'vpc_config': 'vpcConfig'})
class CfnFunctionProps():
    def __init__(self, *, code_uri: typing.Union[str, aws_cdk.core.IResolvable, "CfnFunction.S3LocationProperty"], handler: str, runtime: str, auto_publish_alias: typing.Optional[str]=None, dead_letter_queue: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnFunction.DeadLetterQueueProperty"]]]=None, deployment_preference: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnFunction.DeploymentPreferenceProperty"]]]=None, description: typing.Optional[str]=None, environment: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnFunction.FunctionEnvironmentProperty"]]]=None, events: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.Mapping[str,typing.Union[aws_cdk.core.IResolvable, "CfnFunction.EventSourceProperty"]]]]]=None, function_name: typing.Optional[str]=None, kms_key_arn: typing.Optional[str]=None, layers: typing.Optional[typing.List[str]]=None, memory_size: typing.Optional[jsii.Number]=None, permissions_boundary: typing.Optional[str]=None, policies: typing.Optional[typing.Union[typing.Optional[str], typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnFunction.IAMPolicyDocumentProperty"], typing.Optional[typing.List[typing.Union[str, aws_cdk.core.IResolvable, "CfnFunction.IAMPolicyDocumentProperty", "CfnFunction.SAMPolicyTemplateProperty"]]]]]=None, reserved_concurrent_executions: typing.Optional[jsii.Number]=None, role: typing.Optional[str]=None, tags: typing.Optional[typing.Mapping[str,str]]=None, timeout: typing.Optional[jsii.Number]=None, tracing: typing.Optional[str]=None, vpc_config: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnFunction.VpcConfigProperty"]]]=None):
        """Properties for defining a ``AWS::Serverless::Function``.

        :param code_uri: ``AWS::Serverless::Function.CodeUri``.
        :param handler: ``AWS::Serverless::Function.Handler``.
        :param runtime: ``AWS::Serverless::Function.Runtime``.
        :param auto_publish_alias: ``AWS::Serverless::Function.AutoPublishAlias``.
        :param dead_letter_queue: ``AWS::Serverless::Function.DeadLetterQueue``.
        :param deployment_preference: ``AWS::Serverless::Function.DeploymentPreference``.
        :param description: ``AWS::Serverless::Function.Description``.
        :param environment: ``AWS::Serverless::Function.Environment``.
        :param events: ``AWS::Serverless::Function.Events``.
        :param function_name: ``AWS::Serverless::Function.FunctionName``.
        :param kms_key_arn: ``AWS::Serverless::Function.KmsKeyArn``.
        :param layers: ``AWS::Serverless::Function.Layers``.
        :param memory_size: ``AWS::Serverless::Function.MemorySize``.
        :param permissions_boundary: ``AWS::Serverless::Function.PermissionsBoundary``.
        :param policies: ``AWS::Serverless::Function.Policies``.
        :param reserved_concurrent_executions: ``AWS::Serverless::Function.ReservedConcurrentExecutions``.
        :param role: ``AWS::Serverless::Function.Role``.
        :param tags: ``AWS::Serverless::Function.Tags``.
        :param timeout: ``AWS::Serverless::Function.Timeout``.
        :param tracing: ``AWS::Serverless::Function.Tracing``.
        :param vpc_config: ``AWS::Serverless::Function.VpcConfig``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessfunction
        """
        self._values = {
            'code_uri': code_uri,
            'handler': handler,
            'runtime': runtime,
        }
        if auto_publish_alias is not None: self._values["auto_publish_alias"] = auto_publish_alias
        if dead_letter_queue is not None: self._values["dead_letter_queue"] = dead_letter_queue
        if deployment_preference is not None: self._values["deployment_preference"] = deployment_preference
        if description is not None: self._values["description"] = description
        if environment is not None: self._values["environment"] = environment
        if events is not None: self._values["events"] = events
        if function_name is not None: self._values["function_name"] = function_name
        if kms_key_arn is not None: self._values["kms_key_arn"] = kms_key_arn
        if layers is not None: self._values["layers"] = layers
        if memory_size is not None: self._values["memory_size"] = memory_size
        if permissions_boundary is not None: self._values["permissions_boundary"] = permissions_boundary
        if policies is not None: self._values["policies"] = policies
        if reserved_concurrent_executions is not None: self._values["reserved_concurrent_executions"] = reserved_concurrent_executions
        if role is not None: self._values["role"] = role
        if tags is not None: self._values["tags"] = tags
        if timeout is not None: self._values["timeout"] = timeout
        if tracing is not None: self._values["tracing"] = tracing
        if vpc_config is not None: self._values["vpc_config"] = vpc_config

    @property
    def code_uri(self) -> typing.Union[str, aws_cdk.core.IResolvable, "CfnFunction.S3LocationProperty"]:
        """``AWS::Serverless::Function.CodeUri``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessfunction
        """
        return self._values.get('code_uri')

    @property
    def handler(self) -> str:
        """``AWS::Serverless::Function.Handler``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessfunction
        """
        return self._values.get('handler')

    @property
    def runtime(self) -> str:
        """``AWS::Serverless::Function.Runtime``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessfunction
        """
        return self._values.get('runtime')

    @property
    def auto_publish_alias(self) -> typing.Optional[str]:
        """``AWS::Serverless::Function.AutoPublishAlias``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessfunction
        """
        return self._values.get('auto_publish_alias')

    @property
    def dead_letter_queue(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnFunction.DeadLetterQueueProperty"]]]:
        """``AWS::Serverless::Function.DeadLetterQueue``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessfunction
        """
        return self._values.get('dead_letter_queue')

    @property
    def deployment_preference(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnFunction.DeploymentPreferenceProperty"]]]:
        """``AWS::Serverless::Function.DeploymentPreference``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#deploymentpreference-object
        """
        return self._values.get('deployment_preference')

    @property
    def description(self) -> typing.Optional[str]:
        """``AWS::Serverless::Function.Description``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessfunction
        """
        return self._values.get('description')

    @property
    def environment(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnFunction.FunctionEnvironmentProperty"]]]:
        """``AWS::Serverless::Function.Environment``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessfunction
        """
        return self._values.get('environment')

    @property
    def events(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.Mapping[str,typing.Union[aws_cdk.core.IResolvable, "CfnFunction.EventSourceProperty"]]]]]:
        """``AWS::Serverless::Function.Events``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessfunction
        """
        return self._values.get('events')

    @property
    def function_name(self) -> typing.Optional[str]:
        """``AWS::Serverless::Function.FunctionName``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessfunction
        """
        return self._values.get('function_name')

    @property
    def kms_key_arn(self) -> typing.Optional[str]:
        """``AWS::Serverless::Function.KmsKeyArn``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessfunction
        """
        return self._values.get('kms_key_arn')

    @property
    def layers(self) -> typing.Optional[typing.List[str]]:
        """``AWS::Serverless::Function.Layers``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessfunction
        """
        return self._values.get('layers')

    @property
    def memory_size(self) -> typing.Optional[jsii.Number]:
        """``AWS::Serverless::Function.MemorySize``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessfunction
        """
        return self._values.get('memory_size')

    @property
    def permissions_boundary(self) -> typing.Optional[str]:
        """``AWS::Serverless::Function.PermissionsBoundary``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessfunction
        """
        return self._values.get('permissions_boundary')

    @property
    def policies(self) -> typing.Optional[typing.Union[typing.Optional[str], typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnFunction.IAMPolicyDocumentProperty"], typing.Optional[typing.List[typing.Union[str, aws_cdk.core.IResolvable, "CfnFunction.IAMPolicyDocumentProperty", "CfnFunction.SAMPolicyTemplateProperty"]]]]]:
        """``AWS::Serverless::Function.Policies``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessfunction
        """
        return self._values.get('policies')

    @property
    def reserved_concurrent_executions(self) -> typing.Optional[jsii.Number]:
        """``AWS::Serverless::Function.ReservedConcurrentExecutions``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessfunction
        """
        return self._values.get('reserved_concurrent_executions')

    @property
    def role(self) -> typing.Optional[str]:
        """``AWS::Serverless::Function.Role``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessfunction
        """
        return self._values.get('role')

    @property
    def tags(self) -> typing.Optional[typing.Mapping[str,str]]:
        """``AWS::Serverless::Function.Tags``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessfunction
        """
        return self._values.get('tags')

    @property
    def timeout(self) -> typing.Optional[jsii.Number]:
        """``AWS::Serverless::Function.Timeout``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessfunction
        """
        return self._values.get('timeout')

    @property
    def tracing(self) -> typing.Optional[str]:
        """``AWS::Serverless::Function.Tracing``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessfunction
        """
        return self._values.get('tracing')

    @property
    def vpc_config(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnFunction.VpcConfigProperty"]]]:
        """``AWS::Serverless::Function.VpcConfig``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessfunction
        """
        return self._values.get('vpc_config')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnFunctionProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnLayerVersion(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-sam.CfnLayerVersion"):
    """A CloudFormation ``AWS::Serverless::LayerVersion``.

    see
    :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlesslayerversion
    cloudformationResource:
    :cloudformationResource:: AWS::Serverless::LayerVersion
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, compatible_runtimes: typing.Optional[typing.List[str]]=None, content_uri: typing.Optional[str]=None, description: typing.Optional[str]=None, layer_name: typing.Optional[str]=None, license_info: typing.Optional[str]=None, retention_policy: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::Serverless::LayerVersion``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param compatible_runtimes: ``AWS::Serverless::LayerVersion.CompatibleRuntimes``.
        :param content_uri: ``AWS::Serverless::LayerVersion.ContentUri``.
        :param description: ``AWS::Serverless::LayerVersion.Description``.
        :param layer_name: ``AWS::Serverless::LayerVersion.LayerName``.
        :param license_info: ``AWS::Serverless::LayerVersion.LicenseInfo``.
        :param retention_policy: ``AWS::Serverless::LayerVersion.RetentionPolicy``.
        """
        props = CfnLayerVersionProps(compatible_runtimes=compatible_runtimes, content_uri=content_uri, description=description, layer_name=layer_name, license_info=license_info, retention_policy=retention_policy)

        jsii.create(CfnLayerVersion, self, [scope, id, props])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(self, props: typing.Mapping[str,typing.Any]) -> typing.Mapping[str,typing.Any]:
        """
        :param props: -
        """
        return jsii.invoke(self, "renderProperties", [props])

    @classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class."""
        return jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME")

    @classproperty
    @jsii.member(jsii_name="REQUIRED_TRANSFORM")
    def REQUIRED_TRANSFORM(cls) -> str:
        """The ``Transform`` a template must use in order to use this resource."""
        return jsii.sget(cls, "REQUIRED_TRANSFORM")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="compatibleRuntimes")
    def compatible_runtimes(self) -> typing.Optional[typing.List[str]]:
        """``AWS::Serverless::LayerVersion.CompatibleRuntimes``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlesslayerversion
        """
        return jsii.get(self, "compatibleRuntimes")

    @compatible_runtimes.setter
    def compatible_runtimes(self, value: typing.Optional[typing.List[str]]):
        return jsii.set(self, "compatibleRuntimes", value)

    @property
    @jsii.member(jsii_name="contentUri")
    def content_uri(self) -> typing.Optional[str]:
        """``AWS::Serverless::LayerVersion.ContentUri``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlesslayerversion
        """
        return jsii.get(self, "contentUri")

    @content_uri.setter
    def content_uri(self, value: typing.Optional[str]):
        return jsii.set(self, "contentUri", value)

    @property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[str]:
        """``AWS::Serverless::LayerVersion.Description``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlesslayerversion
        """
        return jsii.get(self, "description")

    @description.setter
    def description(self, value: typing.Optional[str]):
        return jsii.set(self, "description", value)

    @property
    @jsii.member(jsii_name="layerName")
    def layer_name(self) -> typing.Optional[str]:
        """``AWS::Serverless::LayerVersion.LayerName``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlesslayerversion
        """
        return jsii.get(self, "layerName")

    @layer_name.setter
    def layer_name(self, value: typing.Optional[str]):
        return jsii.set(self, "layerName", value)

    @property
    @jsii.member(jsii_name="licenseInfo")
    def license_info(self) -> typing.Optional[str]:
        """``AWS::Serverless::LayerVersion.LicenseInfo``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlesslayerversion
        """
        return jsii.get(self, "licenseInfo")

    @license_info.setter
    def license_info(self, value: typing.Optional[str]):
        return jsii.set(self, "licenseInfo", value)

    @property
    @jsii.member(jsii_name="retentionPolicy")
    def retention_policy(self) -> typing.Optional[str]:
        """``AWS::Serverless::LayerVersion.RetentionPolicy``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlesslayerversion
        """
        return jsii.get(self, "retentionPolicy")

    @retention_policy.setter
    def retention_policy(self, value: typing.Optional[str]):
        return jsii.set(self, "retentionPolicy", value)


@jsii.data_type(jsii_type="@aws-cdk/aws-sam.CfnLayerVersionProps", jsii_struct_bases=[], name_mapping={'compatible_runtimes': 'compatibleRuntimes', 'content_uri': 'contentUri', 'description': 'description', 'layer_name': 'layerName', 'license_info': 'licenseInfo', 'retention_policy': 'retentionPolicy'})
class CfnLayerVersionProps():
    def __init__(self, *, compatible_runtimes: typing.Optional[typing.List[str]]=None, content_uri: typing.Optional[str]=None, description: typing.Optional[str]=None, layer_name: typing.Optional[str]=None, license_info: typing.Optional[str]=None, retention_policy: typing.Optional[str]=None):
        """Properties for defining a ``AWS::Serverless::LayerVersion``.

        :param compatible_runtimes: ``AWS::Serverless::LayerVersion.CompatibleRuntimes``.
        :param content_uri: ``AWS::Serverless::LayerVersion.ContentUri``.
        :param description: ``AWS::Serverless::LayerVersion.Description``.
        :param layer_name: ``AWS::Serverless::LayerVersion.LayerName``.
        :param license_info: ``AWS::Serverless::LayerVersion.LicenseInfo``.
        :param retention_policy: ``AWS::Serverless::LayerVersion.RetentionPolicy``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlesslayerversion
        """
        self._values = {
        }
        if compatible_runtimes is not None: self._values["compatible_runtimes"] = compatible_runtimes
        if content_uri is not None: self._values["content_uri"] = content_uri
        if description is not None: self._values["description"] = description
        if layer_name is not None: self._values["layer_name"] = layer_name
        if license_info is not None: self._values["license_info"] = license_info
        if retention_policy is not None: self._values["retention_policy"] = retention_policy

    @property
    def compatible_runtimes(self) -> typing.Optional[typing.List[str]]:
        """``AWS::Serverless::LayerVersion.CompatibleRuntimes``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlesslayerversion
        """
        return self._values.get('compatible_runtimes')

    @property
    def content_uri(self) -> typing.Optional[str]:
        """``AWS::Serverless::LayerVersion.ContentUri``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlesslayerversion
        """
        return self._values.get('content_uri')

    @property
    def description(self) -> typing.Optional[str]:
        """``AWS::Serverless::LayerVersion.Description``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlesslayerversion
        """
        return self._values.get('description')

    @property
    def layer_name(self) -> typing.Optional[str]:
        """``AWS::Serverless::LayerVersion.LayerName``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlesslayerversion
        """
        return self._values.get('layer_name')

    @property
    def license_info(self) -> typing.Optional[str]:
        """``AWS::Serverless::LayerVersion.LicenseInfo``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlesslayerversion
        """
        return self._values.get('license_info')

    @property
    def retention_policy(self) -> typing.Optional[str]:
        """``AWS::Serverless::LayerVersion.RetentionPolicy``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlesslayerversion
        """
        return self._values.get('retention_policy')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnLayerVersionProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnSimpleTable(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-sam.CfnSimpleTable"):
    """A CloudFormation ``AWS::Serverless::SimpleTable``.

    see
    :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlesssimpletable
    cloudformationResource:
    :cloudformationResource:: AWS::Serverless::SimpleTable
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, primary_key: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["PrimaryKeyProperty"]]]=None, provisioned_throughput: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["ProvisionedThroughputProperty"]]]=None, sse_specification: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["SSESpecificationProperty"]]]=None, table_name: typing.Optional[str]=None, tags: typing.Optional[typing.Mapping[str,str]]=None) -> None:
        """Create a new ``AWS::Serverless::SimpleTable``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param primary_key: ``AWS::Serverless::SimpleTable.PrimaryKey``.
        :param provisioned_throughput: ``AWS::Serverless::SimpleTable.ProvisionedThroughput``.
        :param sse_specification: ``AWS::Serverless::SimpleTable.SSESpecification``.
        :param table_name: ``AWS::Serverless::SimpleTable.TableName``.
        :param tags: ``AWS::Serverless::SimpleTable.Tags``.
        """
        props = CfnSimpleTableProps(primary_key=primary_key, provisioned_throughput=provisioned_throughput, sse_specification=sse_specification, table_name=table_name, tags=tags)

        jsii.create(CfnSimpleTable, self, [scope, id, props])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(self, props: typing.Mapping[str,typing.Any]) -> typing.Mapping[str,typing.Any]:
        """
        :param props: -
        """
        return jsii.invoke(self, "renderProperties", [props])

    @classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class."""
        return jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME")

    @classproperty
    @jsii.member(jsii_name="REQUIRED_TRANSFORM")
    def REQUIRED_TRANSFORM(cls) -> str:
        """The ``Transform`` a template must use in order to use this resource."""
        return jsii.sget(cls, "REQUIRED_TRANSFORM")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        """``AWS::Serverless::SimpleTable.Tags``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlesssimpletable
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="primaryKey")
    def primary_key(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["PrimaryKeyProperty"]]]:
        """``AWS::Serverless::SimpleTable.PrimaryKey``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#primary-key-object
        """
        return jsii.get(self, "primaryKey")

    @primary_key.setter
    def primary_key(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["PrimaryKeyProperty"]]]):
        return jsii.set(self, "primaryKey", value)

    @property
    @jsii.member(jsii_name="provisionedThroughput")
    def provisioned_throughput(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["ProvisionedThroughputProperty"]]]:
        """``AWS::Serverless::SimpleTable.ProvisionedThroughput``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dynamodb-provisionedthroughput.html
        """
        return jsii.get(self, "provisionedThroughput")

    @provisioned_throughput.setter
    def provisioned_throughput(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["ProvisionedThroughputProperty"]]]):
        return jsii.set(self, "provisionedThroughput", value)

    @property
    @jsii.member(jsii_name="sseSpecification")
    def sse_specification(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["SSESpecificationProperty"]]]:
        """``AWS::Serverless::SimpleTable.SSESpecification``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlesssimpletable
        """
        return jsii.get(self, "sseSpecification")

    @sse_specification.setter
    def sse_specification(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["SSESpecificationProperty"]]]):
        return jsii.set(self, "sseSpecification", value)

    @property
    @jsii.member(jsii_name="tableName")
    def table_name(self) -> typing.Optional[str]:
        """``AWS::Serverless::SimpleTable.TableName``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlesssimpletable
        """
        return jsii.get(self, "tableName")

    @table_name.setter
    def table_name(self, value: typing.Optional[str]):
        return jsii.set(self, "tableName", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-sam.CfnSimpleTable.PrimaryKeyProperty", jsii_struct_bases=[], name_mapping={'type': 'type', 'name': 'name'})
    class PrimaryKeyProperty():
        def __init__(self, *, type: str, name: typing.Optional[str]=None):
            """
            :param type: ``CfnSimpleTable.PrimaryKeyProperty.Type``.
            :param name: ``CfnSimpleTable.PrimaryKeyProperty.Name``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#primary-key-object
            """
            self._values = {
                'type': type,
            }
            if name is not None: self._values["name"] = name

        @property
        def type(self) -> str:
            """``CfnSimpleTable.PrimaryKeyProperty.Type``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#primary-key-object
            """
            return self._values.get('type')

        @property
        def name(self) -> typing.Optional[str]:
            """``CfnSimpleTable.PrimaryKeyProperty.Name``.

            see
            :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#primary-key-object
            """
            return self._values.get('name')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'PrimaryKeyProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-sam.CfnSimpleTable.ProvisionedThroughputProperty", jsii_struct_bases=[], name_mapping={'write_capacity_units': 'writeCapacityUnits', 'read_capacity_units': 'readCapacityUnits'})
    class ProvisionedThroughputProperty():
        def __init__(self, *, write_capacity_units: jsii.Number, read_capacity_units: typing.Optional[jsii.Number]=None):
            """
            :param write_capacity_units: ``CfnSimpleTable.ProvisionedThroughputProperty.WriteCapacityUnits``.
            :param read_capacity_units: ``CfnSimpleTable.ProvisionedThroughputProperty.ReadCapacityUnits``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dynamodb-provisionedthroughput.html
            """
            self._values = {
                'write_capacity_units': write_capacity_units,
            }
            if read_capacity_units is not None: self._values["read_capacity_units"] = read_capacity_units

        @property
        def write_capacity_units(self) -> jsii.Number:
            """``CfnSimpleTable.ProvisionedThroughputProperty.WriteCapacityUnits``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dynamodb-provisionedthroughput.html
            """
            return self._values.get('write_capacity_units')

        @property
        def read_capacity_units(self) -> typing.Optional[jsii.Number]:
            """``CfnSimpleTable.ProvisionedThroughputProperty.ReadCapacityUnits``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dynamodb-provisionedthroughput.html
            """
            return self._values.get('read_capacity_units')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'ProvisionedThroughputProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-sam.CfnSimpleTable.SSESpecificationProperty", jsii_struct_bases=[], name_mapping={'sse_enabled': 'sseEnabled'})
    class SSESpecificationProperty():
        def __init__(self, *, sse_enabled: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None):
            """
            :param sse_enabled: ``CfnSimpleTable.SSESpecificationProperty.SSEEnabled``.

            see
            :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dynamodb-table-ssespecification.html
            """
            self._values = {
            }
            if sse_enabled is not None: self._values["sse_enabled"] = sse_enabled

        @property
        def sse_enabled(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
            """``CfnSimpleTable.SSESpecificationProperty.SSEEnabled``.

            see
            :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dynamodb-table-ssespecification.html
            """
            return self._values.get('sse_enabled')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'SSESpecificationProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



@jsii.data_type(jsii_type="@aws-cdk/aws-sam.CfnSimpleTableProps", jsii_struct_bases=[], name_mapping={'primary_key': 'primaryKey', 'provisioned_throughput': 'provisionedThroughput', 'sse_specification': 'sseSpecification', 'table_name': 'tableName', 'tags': 'tags'})
class CfnSimpleTableProps():
    def __init__(self, *, primary_key: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnSimpleTable.PrimaryKeyProperty"]]]=None, provisioned_throughput: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnSimpleTable.ProvisionedThroughputProperty"]]]=None, sse_specification: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnSimpleTable.SSESpecificationProperty"]]]=None, table_name: typing.Optional[str]=None, tags: typing.Optional[typing.Mapping[str,str]]=None):
        """Properties for defining a ``AWS::Serverless::SimpleTable``.

        :param primary_key: ``AWS::Serverless::SimpleTable.PrimaryKey``.
        :param provisioned_throughput: ``AWS::Serverless::SimpleTable.ProvisionedThroughput``.
        :param sse_specification: ``AWS::Serverless::SimpleTable.SSESpecification``.
        :param table_name: ``AWS::Serverless::SimpleTable.TableName``.
        :param tags: ``AWS::Serverless::SimpleTable.Tags``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlesssimpletable
        """
        self._values = {
        }
        if primary_key is not None: self._values["primary_key"] = primary_key
        if provisioned_throughput is not None: self._values["provisioned_throughput"] = provisioned_throughput
        if sse_specification is not None: self._values["sse_specification"] = sse_specification
        if table_name is not None: self._values["table_name"] = table_name
        if tags is not None: self._values["tags"] = tags

    @property
    def primary_key(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnSimpleTable.PrimaryKeyProperty"]]]:
        """``AWS::Serverless::SimpleTable.PrimaryKey``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#primary-key-object
        """
        return self._values.get('primary_key')

    @property
    def provisioned_throughput(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnSimpleTable.ProvisionedThroughputProperty"]]]:
        """``AWS::Serverless::SimpleTable.ProvisionedThroughput``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dynamodb-provisionedthroughput.html
        """
        return self._values.get('provisioned_throughput')

    @property
    def sse_specification(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnSimpleTable.SSESpecificationProperty"]]]:
        """``AWS::Serverless::SimpleTable.SSESpecification``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlesssimpletable
        """
        return self._values.get('sse_specification')

    @property
    def table_name(self) -> typing.Optional[str]:
        """``AWS::Serverless::SimpleTable.TableName``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlesssimpletable
        """
        return self._values.get('table_name')

    @property
    def tags(self) -> typing.Optional[typing.Mapping[str,str]]:
        """``AWS::Serverless::SimpleTable.Tags``.

        see
        :see: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlesssimpletable
        """
        return self._values.get('tags')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnSimpleTableProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


__all__ = ["CfnApi", "CfnApiProps", "CfnApplication", "CfnApplicationProps", "CfnFunction", "CfnFunctionProps", "CfnLayerVersion", "CfnLayerVersionProps", "CfnSimpleTable", "CfnSimpleTableProps", "__jsii_assembly__"]

publication.publish()
