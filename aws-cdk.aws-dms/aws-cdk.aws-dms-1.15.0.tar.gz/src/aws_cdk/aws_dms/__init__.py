import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.core
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-dms", "1.15.0", __name__, "aws-dms@1.15.0.jsii.tgz")
class CfnCertificate(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-dms.CfnCertificate"):
    """A CloudFormation ``AWS::DMS::Certificate``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-certificate.html
    cloudformationResource:
    :cloudformationResource:: AWS::DMS::Certificate
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, certificate_identifier: typing.Optional[str]=None, certificate_pem: typing.Optional[str]=None, certificate_wallet: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::DMS::Certificate``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param certificate_identifier: ``AWS::DMS::Certificate.CertificateIdentifier``.
        :param certificate_pem: ``AWS::DMS::Certificate.CertificatePem``.
        :param certificate_wallet: ``AWS::DMS::Certificate.CertificateWallet``.
        """
        props = CfnCertificateProps(certificate_identifier=certificate_identifier, certificate_pem=certificate_pem, certificate_wallet=certificate_wallet)

        jsii.create(CfnCertificate, self, [scope, id, props])

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

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="certificateIdentifier")
    def certificate_identifier(self) -> typing.Optional[str]:
        """``AWS::DMS::Certificate.CertificateIdentifier``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-certificate.html#cfn-dms-certificate-certificateidentifier
        """
        return jsii.get(self, "certificateIdentifier")

    @certificate_identifier.setter
    def certificate_identifier(self, value: typing.Optional[str]):
        return jsii.set(self, "certificateIdentifier", value)

    @property
    @jsii.member(jsii_name="certificatePem")
    def certificate_pem(self) -> typing.Optional[str]:
        """``AWS::DMS::Certificate.CertificatePem``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-certificate.html#cfn-dms-certificate-certificatepem
        """
        return jsii.get(self, "certificatePem")

    @certificate_pem.setter
    def certificate_pem(self, value: typing.Optional[str]):
        return jsii.set(self, "certificatePem", value)

    @property
    @jsii.member(jsii_name="certificateWallet")
    def certificate_wallet(self) -> typing.Optional[str]:
        """``AWS::DMS::Certificate.CertificateWallet``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-certificate.html#cfn-dms-certificate-certificatewallet
        """
        return jsii.get(self, "certificateWallet")

    @certificate_wallet.setter
    def certificate_wallet(self, value: typing.Optional[str]):
        return jsii.set(self, "certificateWallet", value)


@jsii.data_type(jsii_type="@aws-cdk/aws-dms.CfnCertificateProps", jsii_struct_bases=[], name_mapping={'certificate_identifier': 'certificateIdentifier', 'certificate_pem': 'certificatePem', 'certificate_wallet': 'certificateWallet'})
class CfnCertificateProps():
    def __init__(self, *, certificate_identifier: typing.Optional[str]=None, certificate_pem: typing.Optional[str]=None, certificate_wallet: typing.Optional[str]=None):
        """Properties for defining a ``AWS::DMS::Certificate``.

        :param certificate_identifier: ``AWS::DMS::Certificate.CertificateIdentifier``.
        :param certificate_pem: ``AWS::DMS::Certificate.CertificatePem``.
        :param certificate_wallet: ``AWS::DMS::Certificate.CertificateWallet``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-certificate.html
        """
        self._values = {
        }
        if certificate_identifier is not None: self._values["certificate_identifier"] = certificate_identifier
        if certificate_pem is not None: self._values["certificate_pem"] = certificate_pem
        if certificate_wallet is not None: self._values["certificate_wallet"] = certificate_wallet

    @property
    def certificate_identifier(self) -> typing.Optional[str]:
        """``AWS::DMS::Certificate.CertificateIdentifier``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-certificate.html#cfn-dms-certificate-certificateidentifier
        """
        return self._values.get('certificate_identifier')

    @property
    def certificate_pem(self) -> typing.Optional[str]:
        """``AWS::DMS::Certificate.CertificatePem``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-certificate.html#cfn-dms-certificate-certificatepem
        """
        return self._values.get('certificate_pem')

    @property
    def certificate_wallet(self) -> typing.Optional[str]:
        """``AWS::DMS::Certificate.CertificateWallet``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-certificate.html#cfn-dms-certificate-certificatewallet
        """
        return self._values.get('certificate_wallet')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnCertificateProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnEndpoint(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-dms.CfnEndpoint"):
    """A CloudFormation ``AWS::DMS::Endpoint``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html
    cloudformationResource:
    :cloudformationResource:: AWS::DMS::Endpoint
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, endpoint_type: str, engine_name: str, certificate_arn: typing.Optional[str]=None, database_name: typing.Optional[str]=None, dynamo_db_settings: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["DynamoDbSettingsProperty"]]]=None, elasticsearch_settings: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["ElasticsearchSettingsProperty"]]]=None, endpoint_identifier: typing.Optional[str]=None, extra_connection_attributes: typing.Optional[str]=None, kinesis_settings: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["KinesisSettingsProperty"]]]=None, kms_key_id: typing.Optional[str]=None, mongo_db_settings: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["MongoDbSettingsProperty"]]]=None, password: typing.Optional[str]=None, port: typing.Optional[jsii.Number]=None, s3_settings: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["S3SettingsProperty"]]]=None, server_name: typing.Optional[str]=None, ssl_mode: typing.Optional[str]=None, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None, username: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::DMS::Endpoint``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param endpoint_type: ``AWS::DMS::Endpoint.EndpointType``.
        :param engine_name: ``AWS::DMS::Endpoint.EngineName``.
        :param certificate_arn: ``AWS::DMS::Endpoint.CertificateArn``.
        :param database_name: ``AWS::DMS::Endpoint.DatabaseName``.
        :param dynamo_db_settings: ``AWS::DMS::Endpoint.DynamoDbSettings``.
        :param elasticsearch_settings: ``AWS::DMS::Endpoint.ElasticsearchSettings``.
        :param endpoint_identifier: ``AWS::DMS::Endpoint.EndpointIdentifier``.
        :param extra_connection_attributes: ``AWS::DMS::Endpoint.ExtraConnectionAttributes``.
        :param kinesis_settings: ``AWS::DMS::Endpoint.KinesisSettings``.
        :param kms_key_id: ``AWS::DMS::Endpoint.KmsKeyId``.
        :param mongo_db_settings: ``AWS::DMS::Endpoint.MongoDbSettings``.
        :param password: ``AWS::DMS::Endpoint.Password``.
        :param port: ``AWS::DMS::Endpoint.Port``.
        :param s3_settings: ``AWS::DMS::Endpoint.S3Settings``.
        :param server_name: ``AWS::DMS::Endpoint.ServerName``.
        :param ssl_mode: ``AWS::DMS::Endpoint.SslMode``.
        :param tags: ``AWS::DMS::Endpoint.Tags``.
        :param username: ``AWS::DMS::Endpoint.Username``.
        """
        props = CfnEndpointProps(endpoint_type=endpoint_type, engine_name=engine_name, certificate_arn=certificate_arn, database_name=database_name, dynamo_db_settings=dynamo_db_settings, elasticsearch_settings=elasticsearch_settings, endpoint_identifier=endpoint_identifier, extra_connection_attributes=extra_connection_attributes, kinesis_settings=kinesis_settings, kms_key_id=kms_key_id, mongo_db_settings=mongo_db_settings, password=password, port=port, s3_settings=s3_settings, server_name=server_name, ssl_mode=ssl_mode, tags=tags, username=username)

        jsii.create(CfnEndpoint, self, [scope, id, props])

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

    @property
    @jsii.member(jsii_name="attrExternalId")
    def attr_external_id(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: ExternalId
        """
        return jsii.get(self, "attrExternalId")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        """``AWS::DMS::Endpoint.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-tags
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="endpointType")
    def endpoint_type(self) -> str:
        """``AWS::DMS::Endpoint.EndpointType``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-endpointtype
        """
        return jsii.get(self, "endpointType")

    @endpoint_type.setter
    def endpoint_type(self, value: str):
        return jsii.set(self, "endpointType", value)

    @property
    @jsii.member(jsii_name="engineName")
    def engine_name(self) -> str:
        """``AWS::DMS::Endpoint.EngineName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-enginename
        """
        return jsii.get(self, "engineName")

    @engine_name.setter
    def engine_name(self, value: str):
        return jsii.set(self, "engineName", value)

    @property
    @jsii.member(jsii_name="certificateArn")
    def certificate_arn(self) -> typing.Optional[str]:
        """``AWS::DMS::Endpoint.CertificateArn``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-certificatearn
        """
        return jsii.get(self, "certificateArn")

    @certificate_arn.setter
    def certificate_arn(self, value: typing.Optional[str]):
        return jsii.set(self, "certificateArn", value)

    @property
    @jsii.member(jsii_name="databaseName")
    def database_name(self) -> typing.Optional[str]:
        """``AWS::DMS::Endpoint.DatabaseName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-databasename
        """
        return jsii.get(self, "databaseName")

    @database_name.setter
    def database_name(self, value: typing.Optional[str]):
        return jsii.set(self, "databaseName", value)

    @property
    @jsii.member(jsii_name="dynamoDbSettings")
    def dynamo_db_settings(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["DynamoDbSettingsProperty"]]]:
        """``AWS::DMS::Endpoint.DynamoDbSettings``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-dynamodbsettings
        """
        return jsii.get(self, "dynamoDbSettings")

    @dynamo_db_settings.setter
    def dynamo_db_settings(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["DynamoDbSettingsProperty"]]]):
        return jsii.set(self, "dynamoDbSettings", value)

    @property
    @jsii.member(jsii_name="elasticsearchSettings")
    def elasticsearch_settings(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["ElasticsearchSettingsProperty"]]]:
        """``AWS::DMS::Endpoint.ElasticsearchSettings``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-elasticsearchsettings
        """
        return jsii.get(self, "elasticsearchSettings")

    @elasticsearch_settings.setter
    def elasticsearch_settings(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["ElasticsearchSettingsProperty"]]]):
        return jsii.set(self, "elasticsearchSettings", value)

    @property
    @jsii.member(jsii_name="endpointIdentifier")
    def endpoint_identifier(self) -> typing.Optional[str]:
        """``AWS::DMS::Endpoint.EndpointIdentifier``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-endpointidentifier
        """
        return jsii.get(self, "endpointIdentifier")

    @endpoint_identifier.setter
    def endpoint_identifier(self, value: typing.Optional[str]):
        return jsii.set(self, "endpointIdentifier", value)

    @property
    @jsii.member(jsii_name="extraConnectionAttributes")
    def extra_connection_attributes(self) -> typing.Optional[str]:
        """``AWS::DMS::Endpoint.ExtraConnectionAttributes``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-extraconnectionattributes
        """
        return jsii.get(self, "extraConnectionAttributes")

    @extra_connection_attributes.setter
    def extra_connection_attributes(self, value: typing.Optional[str]):
        return jsii.set(self, "extraConnectionAttributes", value)

    @property
    @jsii.member(jsii_name="kinesisSettings")
    def kinesis_settings(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["KinesisSettingsProperty"]]]:
        """``AWS::DMS::Endpoint.KinesisSettings``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-kinesissettings
        """
        return jsii.get(self, "kinesisSettings")

    @kinesis_settings.setter
    def kinesis_settings(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["KinesisSettingsProperty"]]]):
        return jsii.set(self, "kinesisSettings", value)

    @property
    @jsii.member(jsii_name="kmsKeyId")
    def kms_key_id(self) -> typing.Optional[str]:
        """``AWS::DMS::Endpoint.KmsKeyId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-kmskeyid
        """
        return jsii.get(self, "kmsKeyId")

    @kms_key_id.setter
    def kms_key_id(self, value: typing.Optional[str]):
        return jsii.set(self, "kmsKeyId", value)

    @property
    @jsii.member(jsii_name="mongoDbSettings")
    def mongo_db_settings(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["MongoDbSettingsProperty"]]]:
        """``AWS::DMS::Endpoint.MongoDbSettings``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-mongodbsettings
        """
        return jsii.get(self, "mongoDbSettings")

    @mongo_db_settings.setter
    def mongo_db_settings(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["MongoDbSettingsProperty"]]]):
        return jsii.set(self, "mongoDbSettings", value)

    @property
    @jsii.member(jsii_name="password")
    def password(self) -> typing.Optional[str]:
        """``AWS::DMS::Endpoint.Password``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-password
        """
        return jsii.get(self, "password")

    @password.setter
    def password(self, value: typing.Optional[str]):
        return jsii.set(self, "password", value)

    @property
    @jsii.member(jsii_name="port")
    def port(self) -> typing.Optional[jsii.Number]:
        """``AWS::DMS::Endpoint.Port``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-port
        """
        return jsii.get(self, "port")

    @port.setter
    def port(self, value: typing.Optional[jsii.Number]):
        return jsii.set(self, "port", value)

    @property
    @jsii.member(jsii_name="s3Settings")
    def s3_settings(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["S3SettingsProperty"]]]:
        """``AWS::DMS::Endpoint.S3Settings``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-s3settings
        """
        return jsii.get(self, "s3Settings")

    @s3_settings.setter
    def s3_settings(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["S3SettingsProperty"]]]):
        return jsii.set(self, "s3Settings", value)

    @property
    @jsii.member(jsii_name="serverName")
    def server_name(self) -> typing.Optional[str]:
        """``AWS::DMS::Endpoint.ServerName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-servername
        """
        return jsii.get(self, "serverName")

    @server_name.setter
    def server_name(self, value: typing.Optional[str]):
        return jsii.set(self, "serverName", value)

    @property
    @jsii.member(jsii_name="sslMode")
    def ssl_mode(self) -> typing.Optional[str]:
        """``AWS::DMS::Endpoint.SslMode``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-sslmode
        """
        return jsii.get(self, "sslMode")

    @ssl_mode.setter
    def ssl_mode(self, value: typing.Optional[str]):
        return jsii.set(self, "sslMode", value)

    @property
    @jsii.member(jsii_name="username")
    def username(self) -> typing.Optional[str]:
        """``AWS::DMS::Endpoint.Username``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-username
        """
        return jsii.get(self, "username")

    @username.setter
    def username(self, value: typing.Optional[str]):
        return jsii.set(self, "username", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-dms.CfnEndpoint.DynamoDbSettingsProperty", jsii_struct_bases=[], name_mapping={'service_access_role_arn': 'serviceAccessRoleArn'})
    class DynamoDbSettingsProperty():
        def __init__(self, *, service_access_role_arn: typing.Optional[str]=None):
            """
            :param service_access_role_arn: ``CfnEndpoint.DynamoDbSettingsProperty.ServiceAccessRoleArn``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-dynamodbsettings.html
            """
            self._values = {
            }
            if service_access_role_arn is not None: self._values["service_access_role_arn"] = service_access_role_arn

        @property
        def service_access_role_arn(self) -> typing.Optional[str]:
            """``CfnEndpoint.DynamoDbSettingsProperty.ServiceAccessRoleArn``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-dynamodbsettings.html#cfn-dms-endpoint-dynamodbsettings-serviceaccessrolearn
            """
            return self._values.get('service_access_role_arn')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'DynamoDbSettingsProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-dms.CfnEndpoint.ElasticsearchSettingsProperty", jsii_struct_bases=[], name_mapping={'endpoint_uri': 'endpointUri', 'error_retry_duration': 'errorRetryDuration', 'full_load_error_percentage': 'fullLoadErrorPercentage', 'service_access_role_arn': 'serviceAccessRoleArn'})
    class ElasticsearchSettingsProperty():
        def __init__(self, *, endpoint_uri: typing.Optional[str]=None, error_retry_duration: typing.Optional[jsii.Number]=None, full_load_error_percentage: typing.Optional[jsii.Number]=None, service_access_role_arn: typing.Optional[str]=None):
            """
            :param endpoint_uri: ``CfnEndpoint.ElasticsearchSettingsProperty.EndpointUri``.
            :param error_retry_duration: ``CfnEndpoint.ElasticsearchSettingsProperty.ErrorRetryDuration``.
            :param full_load_error_percentage: ``CfnEndpoint.ElasticsearchSettingsProperty.FullLoadErrorPercentage``.
            :param service_access_role_arn: ``CfnEndpoint.ElasticsearchSettingsProperty.ServiceAccessRoleArn``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-elasticsearchsettings.html
            """
            self._values = {
            }
            if endpoint_uri is not None: self._values["endpoint_uri"] = endpoint_uri
            if error_retry_duration is not None: self._values["error_retry_duration"] = error_retry_duration
            if full_load_error_percentage is not None: self._values["full_load_error_percentage"] = full_load_error_percentage
            if service_access_role_arn is not None: self._values["service_access_role_arn"] = service_access_role_arn

        @property
        def endpoint_uri(self) -> typing.Optional[str]:
            """``CfnEndpoint.ElasticsearchSettingsProperty.EndpointUri``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-elasticsearchsettings.html#cfn-dms-endpoint-elasticsearchsettings-endpointuri
            """
            return self._values.get('endpoint_uri')

        @property
        def error_retry_duration(self) -> typing.Optional[jsii.Number]:
            """``CfnEndpoint.ElasticsearchSettingsProperty.ErrorRetryDuration``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-elasticsearchsettings.html#cfn-dms-endpoint-elasticsearchsettings-errorretryduration
            """
            return self._values.get('error_retry_duration')

        @property
        def full_load_error_percentage(self) -> typing.Optional[jsii.Number]:
            """``CfnEndpoint.ElasticsearchSettingsProperty.FullLoadErrorPercentage``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-elasticsearchsettings.html#cfn-dms-endpoint-elasticsearchsettings-fullloaderrorpercentage
            """
            return self._values.get('full_load_error_percentage')

        @property
        def service_access_role_arn(self) -> typing.Optional[str]:
            """``CfnEndpoint.ElasticsearchSettingsProperty.ServiceAccessRoleArn``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-elasticsearchsettings.html#cfn-dms-endpoint-elasticsearchsettings-serviceaccessrolearn
            """
            return self._values.get('service_access_role_arn')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'ElasticsearchSettingsProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-dms.CfnEndpoint.KinesisSettingsProperty", jsii_struct_bases=[], name_mapping={'message_format': 'messageFormat', 'service_access_role_arn': 'serviceAccessRoleArn', 'stream_arn': 'streamArn'})
    class KinesisSettingsProperty():
        def __init__(self, *, message_format: typing.Optional[str]=None, service_access_role_arn: typing.Optional[str]=None, stream_arn: typing.Optional[str]=None):
            """
            :param message_format: ``CfnEndpoint.KinesisSettingsProperty.MessageFormat``.
            :param service_access_role_arn: ``CfnEndpoint.KinesisSettingsProperty.ServiceAccessRoleArn``.
            :param stream_arn: ``CfnEndpoint.KinesisSettingsProperty.StreamArn``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-kinesissettings.html
            """
            self._values = {
            }
            if message_format is not None: self._values["message_format"] = message_format
            if service_access_role_arn is not None: self._values["service_access_role_arn"] = service_access_role_arn
            if stream_arn is not None: self._values["stream_arn"] = stream_arn

        @property
        def message_format(self) -> typing.Optional[str]:
            """``CfnEndpoint.KinesisSettingsProperty.MessageFormat``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-kinesissettings.html#cfn-dms-endpoint-kinesissettings-messageformat
            """
            return self._values.get('message_format')

        @property
        def service_access_role_arn(self) -> typing.Optional[str]:
            """``CfnEndpoint.KinesisSettingsProperty.ServiceAccessRoleArn``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-kinesissettings.html#cfn-dms-endpoint-kinesissettings-serviceaccessrolearn
            """
            return self._values.get('service_access_role_arn')

        @property
        def stream_arn(self) -> typing.Optional[str]:
            """``CfnEndpoint.KinesisSettingsProperty.StreamArn``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-kinesissettings.html#cfn-dms-endpoint-kinesissettings-streamarn
            """
            return self._values.get('stream_arn')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'KinesisSettingsProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-dms.CfnEndpoint.MongoDbSettingsProperty", jsii_struct_bases=[], name_mapping={'auth_mechanism': 'authMechanism', 'auth_source': 'authSource', 'auth_type': 'authType', 'database_name': 'databaseName', 'docs_to_investigate': 'docsToInvestigate', 'extract_doc_id': 'extractDocId', 'nesting_level': 'nestingLevel', 'password': 'password', 'port': 'port', 'server_name': 'serverName', 'username': 'username'})
    class MongoDbSettingsProperty():
        def __init__(self, *, auth_mechanism: typing.Optional[str]=None, auth_source: typing.Optional[str]=None, auth_type: typing.Optional[str]=None, database_name: typing.Optional[str]=None, docs_to_investigate: typing.Optional[str]=None, extract_doc_id: typing.Optional[str]=None, nesting_level: typing.Optional[str]=None, password: typing.Optional[str]=None, port: typing.Optional[jsii.Number]=None, server_name: typing.Optional[str]=None, username: typing.Optional[str]=None):
            """
            :param auth_mechanism: ``CfnEndpoint.MongoDbSettingsProperty.AuthMechanism``.
            :param auth_source: ``CfnEndpoint.MongoDbSettingsProperty.AuthSource``.
            :param auth_type: ``CfnEndpoint.MongoDbSettingsProperty.AuthType``.
            :param database_name: ``CfnEndpoint.MongoDbSettingsProperty.DatabaseName``.
            :param docs_to_investigate: ``CfnEndpoint.MongoDbSettingsProperty.DocsToInvestigate``.
            :param extract_doc_id: ``CfnEndpoint.MongoDbSettingsProperty.ExtractDocId``.
            :param nesting_level: ``CfnEndpoint.MongoDbSettingsProperty.NestingLevel``.
            :param password: ``CfnEndpoint.MongoDbSettingsProperty.Password``.
            :param port: ``CfnEndpoint.MongoDbSettingsProperty.Port``.
            :param server_name: ``CfnEndpoint.MongoDbSettingsProperty.ServerName``.
            :param username: ``CfnEndpoint.MongoDbSettingsProperty.Username``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-mongodbsettings.html
            """
            self._values = {
            }
            if auth_mechanism is not None: self._values["auth_mechanism"] = auth_mechanism
            if auth_source is not None: self._values["auth_source"] = auth_source
            if auth_type is not None: self._values["auth_type"] = auth_type
            if database_name is not None: self._values["database_name"] = database_name
            if docs_to_investigate is not None: self._values["docs_to_investigate"] = docs_to_investigate
            if extract_doc_id is not None: self._values["extract_doc_id"] = extract_doc_id
            if nesting_level is not None: self._values["nesting_level"] = nesting_level
            if password is not None: self._values["password"] = password
            if port is not None: self._values["port"] = port
            if server_name is not None: self._values["server_name"] = server_name
            if username is not None: self._values["username"] = username

        @property
        def auth_mechanism(self) -> typing.Optional[str]:
            """``CfnEndpoint.MongoDbSettingsProperty.AuthMechanism``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-mongodbsettings.html#cfn-dms-endpoint-mongodbsettings-authmechanism
            """
            return self._values.get('auth_mechanism')

        @property
        def auth_source(self) -> typing.Optional[str]:
            """``CfnEndpoint.MongoDbSettingsProperty.AuthSource``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-mongodbsettings.html#cfn-dms-endpoint-mongodbsettings-authsource
            """
            return self._values.get('auth_source')

        @property
        def auth_type(self) -> typing.Optional[str]:
            """``CfnEndpoint.MongoDbSettingsProperty.AuthType``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-mongodbsettings.html#cfn-dms-endpoint-mongodbsettings-authtype
            """
            return self._values.get('auth_type')

        @property
        def database_name(self) -> typing.Optional[str]:
            """``CfnEndpoint.MongoDbSettingsProperty.DatabaseName``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-mongodbsettings.html#cfn-dms-endpoint-mongodbsettings-databasename
            """
            return self._values.get('database_name')

        @property
        def docs_to_investigate(self) -> typing.Optional[str]:
            """``CfnEndpoint.MongoDbSettingsProperty.DocsToInvestigate``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-mongodbsettings.html#cfn-dms-endpoint-mongodbsettings-docstoinvestigate
            """
            return self._values.get('docs_to_investigate')

        @property
        def extract_doc_id(self) -> typing.Optional[str]:
            """``CfnEndpoint.MongoDbSettingsProperty.ExtractDocId``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-mongodbsettings.html#cfn-dms-endpoint-mongodbsettings-extractdocid
            """
            return self._values.get('extract_doc_id')

        @property
        def nesting_level(self) -> typing.Optional[str]:
            """``CfnEndpoint.MongoDbSettingsProperty.NestingLevel``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-mongodbsettings.html#cfn-dms-endpoint-mongodbsettings-nestinglevel
            """
            return self._values.get('nesting_level')

        @property
        def password(self) -> typing.Optional[str]:
            """``CfnEndpoint.MongoDbSettingsProperty.Password``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-mongodbsettings.html#cfn-dms-endpoint-mongodbsettings-password
            """
            return self._values.get('password')

        @property
        def port(self) -> typing.Optional[jsii.Number]:
            """``CfnEndpoint.MongoDbSettingsProperty.Port``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-mongodbsettings.html#cfn-dms-endpoint-mongodbsettings-port
            """
            return self._values.get('port')

        @property
        def server_name(self) -> typing.Optional[str]:
            """``CfnEndpoint.MongoDbSettingsProperty.ServerName``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-mongodbsettings.html#cfn-dms-endpoint-mongodbsettings-servername
            """
            return self._values.get('server_name')

        @property
        def username(self) -> typing.Optional[str]:
            """``CfnEndpoint.MongoDbSettingsProperty.Username``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-mongodbsettings.html#cfn-dms-endpoint-mongodbsettings-username
            """
            return self._values.get('username')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'MongoDbSettingsProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-dms.CfnEndpoint.S3SettingsProperty", jsii_struct_bases=[], name_mapping={'bucket_folder': 'bucketFolder', 'bucket_name': 'bucketName', 'compression_type': 'compressionType', 'csv_delimiter': 'csvDelimiter', 'csv_row_delimiter': 'csvRowDelimiter', 'external_table_definition': 'externalTableDefinition', 'service_access_role_arn': 'serviceAccessRoleArn'})
    class S3SettingsProperty():
        def __init__(self, *, bucket_folder: typing.Optional[str]=None, bucket_name: typing.Optional[str]=None, compression_type: typing.Optional[str]=None, csv_delimiter: typing.Optional[str]=None, csv_row_delimiter: typing.Optional[str]=None, external_table_definition: typing.Optional[str]=None, service_access_role_arn: typing.Optional[str]=None):
            """
            :param bucket_folder: ``CfnEndpoint.S3SettingsProperty.BucketFolder``.
            :param bucket_name: ``CfnEndpoint.S3SettingsProperty.BucketName``.
            :param compression_type: ``CfnEndpoint.S3SettingsProperty.CompressionType``.
            :param csv_delimiter: ``CfnEndpoint.S3SettingsProperty.CsvDelimiter``.
            :param csv_row_delimiter: ``CfnEndpoint.S3SettingsProperty.CsvRowDelimiter``.
            :param external_table_definition: ``CfnEndpoint.S3SettingsProperty.ExternalTableDefinition``.
            :param service_access_role_arn: ``CfnEndpoint.S3SettingsProperty.ServiceAccessRoleArn``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-s3settings.html
            """
            self._values = {
            }
            if bucket_folder is not None: self._values["bucket_folder"] = bucket_folder
            if bucket_name is not None: self._values["bucket_name"] = bucket_name
            if compression_type is not None: self._values["compression_type"] = compression_type
            if csv_delimiter is not None: self._values["csv_delimiter"] = csv_delimiter
            if csv_row_delimiter is not None: self._values["csv_row_delimiter"] = csv_row_delimiter
            if external_table_definition is not None: self._values["external_table_definition"] = external_table_definition
            if service_access_role_arn is not None: self._values["service_access_role_arn"] = service_access_role_arn

        @property
        def bucket_folder(self) -> typing.Optional[str]:
            """``CfnEndpoint.S3SettingsProperty.BucketFolder``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-s3settings.html#cfn-dms-endpoint-s3settings-bucketfolder
            """
            return self._values.get('bucket_folder')

        @property
        def bucket_name(self) -> typing.Optional[str]:
            """``CfnEndpoint.S3SettingsProperty.BucketName``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-s3settings.html#cfn-dms-endpoint-s3settings-bucketname
            """
            return self._values.get('bucket_name')

        @property
        def compression_type(self) -> typing.Optional[str]:
            """``CfnEndpoint.S3SettingsProperty.CompressionType``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-s3settings.html#cfn-dms-endpoint-s3settings-compressiontype
            """
            return self._values.get('compression_type')

        @property
        def csv_delimiter(self) -> typing.Optional[str]:
            """``CfnEndpoint.S3SettingsProperty.CsvDelimiter``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-s3settings.html#cfn-dms-endpoint-s3settings-csvdelimiter
            """
            return self._values.get('csv_delimiter')

        @property
        def csv_row_delimiter(self) -> typing.Optional[str]:
            """``CfnEndpoint.S3SettingsProperty.CsvRowDelimiter``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-s3settings.html#cfn-dms-endpoint-s3settings-csvrowdelimiter
            """
            return self._values.get('csv_row_delimiter')

        @property
        def external_table_definition(self) -> typing.Optional[str]:
            """``CfnEndpoint.S3SettingsProperty.ExternalTableDefinition``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-s3settings.html#cfn-dms-endpoint-s3settings-externaltabledefinition
            """
            return self._values.get('external_table_definition')

        @property
        def service_access_role_arn(self) -> typing.Optional[str]:
            """``CfnEndpoint.S3SettingsProperty.ServiceAccessRoleArn``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-s3settings.html#cfn-dms-endpoint-s3settings-serviceaccessrolearn
            """
            return self._values.get('service_access_role_arn')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'S3SettingsProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



@jsii.data_type(jsii_type="@aws-cdk/aws-dms.CfnEndpointProps", jsii_struct_bases=[], name_mapping={'endpoint_type': 'endpointType', 'engine_name': 'engineName', 'certificate_arn': 'certificateArn', 'database_name': 'databaseName', 'dynamo_db_settings': 'dynamoDbSettings', 'elasticsearch_settings': 'elasticsearchSettings', 'endpoint_identifier': 'endpointIdentifier', 'extra_connection_attributes': 'extraConnectionAttributes', 'kinesis_settings': 'kinesisSettings', 'kms_key_id': 'kmsKeyId', 'mongo_db_settings': 'mongoDbSettings', 'password': 'password', 'port': 'port', 's3_settings': 's3Settings', 'server_name': 'serverName', 'ssl_mode': 'sslMode', 'tags': 'tags', 'username': 'username'})
class CfnEndpointProps():
    def __init__(self, *, endpoint_type: str, engine_name: str, certificate_arn: typing.Optional[str]=None, database_name: typing.Optional[str]=None, dynamo_db_settings: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnEndpoint.DynamoDbSettingsProperty"]]]=None, elasticsearch_settings: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnEndpoint.ElasticsearchSettingsProperty"]]]=None, endpoint_identifier: typing.Optional[str]=None, extra_connection_attributes: typing.Optional[str]=None, kinesis_settings: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnEndpoint.KinesisSettingsProperty"]]]=None, kms_key_id: typing.Optional[str]=None, mongo_db_settings: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnEndpoint.MongoDbSettingsProperty"]]]=None, password: typing.Optional[str]=None, port: typing.Optional[jsii.Number]=None, s3_settings: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnEndpoint.S3SettingsProperty"]]]=None, server_name: typing.Optional[str]=None, ssl_mode: typing.Optional[str]=None, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None, username: typing.Optional[str]=None):
        """Properties for defining a ``AWS::DMS::Endpoint``.

        :param endpoint_type: ``AWS::DMS::Endpoint.EndpointType``.
        :param engine_name: ``AWS::DMS::Endpoint.EngineName``.
        :param certificate_arn: ``AWS::DMS::Endpoint.CertificateArn``.
        :param database_name: ``AWS::DMS::Endpoint.DatabaseName``.
        :param dynamo_db_settings: ``AWS::DMS::Endpoint.DynamoDbSettings``.
        :param elasticsearch_settings: ``AWS::DMS::Endpoint.ElasticsearchSettings``.
        :param endpoint_identifier: ``AWS::DMS::Endpoint.EndpointIdentifier``.
        :param extra_connection_attributes: ``AWS::DMS::Endpoint.ExtraConnectionAttributes``.
        :param kinesis_settings: ``AWS::DMS::Endpoint.KinesisSettings``.
        :param kms_key_id: ``AWS::DMS::Endpoint.KmsKeyId``.
        :param mongo_db_settings: ``AWS::DMS::Endpoint.MongoDbSettings``.
        :param password: ``AWS::DMS::Endpoint.Password``.
        :param port: ``AWS::DMS::Endpoint.Port``.
        :param s3_settings: ``AWS::DMS::Endpoint.S3Settings``.
        :param server_name: ``AWS::DMS::Endpoint.ServerName``.
        :param ssl_mode: ``AWS::DMS::Endpoint.SslMode``.
        :param tags: ``AWS::DMS::Endpoint.Tags``.
        :param username: ``AWS::DMS::Endpoint.Username``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html
        """
        self._values = {
            'endpoint_type': endpoint_type,
            'engine_name': engine_name,
        }
        if certificate_arn is not None: self._values["certificate_arn"] = certificate_arn
        if database_name is not None: self._values["database_name"] = database_name
        if dynamo_db_settings is not None: self._values["dynamo_db_settings"] = dynamo_db_settings
        if elasticsearch_settings is not None: self._values["elasticsearch_settings"] = elasticsearch_settings
        if endpoint_identifier is not None: self._values["endpoint_identifier"] = endpoint_identifier
        if extra_connection_attributes is not None: self._values["extra_connection_attributes"] = extra_connection_attributes
        if kinesis_settings is not None: self._values["kinesis_settings"] = kinesis_settings
        if kms_key_id is not None: self._values["kms_key_id"] = kms_key_id
        if mongo_db_settings is not None: self._values["mongo_db_settings"] = mongo_db_settings
        if password is not None: self._values["password"] = password
        if port is not None: self._values["port"] = port
        if s3_settings is not None: self._values["s3_settings"] = s3_settings
        if server_name is not None: self._values["server_name"] = server_name
        if ssl_mode is not None: self._values["ssl_mode"] = ssl_mode
        if tags is not None: self._values["tags"] = tags
        if username is not None: self._values["username"] = username

    @property
    def endpoint_type(self) -> str:
        """``AWS::DMS::Endpoint.EndpointType``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-endpointtype
        """
        return self._values.get('endpoint_type')

    @property
    def engine_name(self) -> str:
        """``AWS::DMS::Endpoint.EngineName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-enginename
        """
        return self._values.get('engine_name')

    @property
    def certificate_arn(self) -> typing.Optional[str]:
        """``AWS::DMS::Endpoint.CertificateArn``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-certificatearn
        """
        return self._values.get('certificate_arn')

    @property
    def database_name(self) -> typing.Optional[str]:
        """``AWS::DMS::Endpoint.DatabaseName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-databasename
        """
        return self._values.get('database_name')

    @property
    def dynamo_db_settings(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnEndpoint.DynamoDbSettingsProperty"]]]:
        """``AWS::DMS::Endpoint.DynamoDbSettings``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-dynamodbsettings
        """
        return self._values.get('dynamo_db_settings')

    @property
    def elasticsearch_settings(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnEndpoint.ElasticsearchSettingsProperty"]]]:
        """``AWS::DMS::Endpoint.ElasticsearchSettings``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-elasticsearchsettings
        """
        return self._values.get('elasticsearch_settings')

    @property
    def endpoint_identifier(self) -> typing.Optional[str]:
        """``AWS::DMS::Endpoint.EndpointIdentifier``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-endpointidentifier
        """
        return self._values.get('endpoint_identifier')

    @property
    def extra_connection_attributes(self) -> typing.Optional[str]:
        """``AWS::DMS::Endpoint.ExtraConnectionAttributes``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-extraconnectionattributes
        """
        return self._values.get('extra_connection_attributes')

    @property
    def kinesis_settings(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnEndpoint.KinesisSettingsProperty"]]]:
        """``AWS::DMS::Endpoint.KinesisSettings``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-kinesissettings
        """
        return self._values.get('kinesis_settings')

    @property
    def kms_key_id(self) -> typing.Optional[str]:
        """``AWS::DMS::Endpoint.KmsKeyId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-kmskeyid
        """
        return self._values.get('kms_key_id')

    @property
    def mongo_db_settings(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnEndpoint.MongoDbSettingsProperty"]]]:
        """``AWS::DMS::Endpoint.MongoDbSettings``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-mongodbsettings
        """
        return self._values.get('mongo_db_settings')

    @property
    def password(self) -> typing.Optional[str]:
        """``AWS::DMS::Endpoint.Password``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-password
        """
        return self._values.get('password')

    @property
    def port(self) -> typing.Optional[jsii.Number]:
        """``AWS::DMS::Endpoint.Port``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-port
        """
        return self._values.get('port')

    @property
    def s3_settings(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnEndpoint.S3SettingsProperty"]]]:
        """``AWS::DMS::Endpoint.S3Settings``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-s3settings
        """
        return self._values.get('s3_settings')

    @property
    def server_name(self) -> typing.Optional[str]:
        """``AWS::DMS::Endpoint.ServerName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-servername
        """
        return self._values.get('server_name')

    @property
    def ssl_mode(self) -> typing.Optional[str]:
        """``AWS::DMS::Endpoint.SslMode``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-sslmode
        """
        return self._values.get('ssl_mode')

    @property
    def tags(self) -> typing.Optional[typing.List[aws_cdk.core.CfnTag]]:
        """``AWS::DMS::Endpoint.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-tags
        """
        return self._values.get('tags')

    @property
    def username(self) -> typing.Optional[str]:
        """``AWS::DMS::Endpoint.Username``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-username
        """
        return self._values.get('username')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnEndpointProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnEventSubscription(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-dms.CfnEventSubscription"):
    """A CloudFormation ``AWS::DMS::EventSubscription``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-eventsubscription.html
    cloudformationResource:
    :cloudformationResource:: AWS::DMS::EventSubscription
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, sns_topic_arn: str, enabled: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, event_categories: typing.Optional[typing.List[str]]=None, source_ids: typing.Optional[typing.List[str]]=None, source_type: typing.Optional[str]=None, subscription_name: typing.Optional[str]=None, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None) -> None:
        """Create a new ``AWS::DMS::EventSubscription``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param sns_topic_arn: ``AWS::DMS::EventSubscription.SnsTopicArn``.
        :param enabled: ``AWS::DMS::EventSubscription.Enabled``.
        :param event_categories: ``AWS::DMS::EventSubscription.EventCategories``.
        :param source_ids: ``AWS::DMS::EventSubscription.SourceIds``.
        :param source_type: ``AWS::DMS::EventSubscription.SourceType``.
        :param subscription_name: ``AWS::DMS::EventSubscription.SubscriptionName``.
        :param tags: ``AWS::DMS::EventSubscription.Tags``.
        """
        props = CfnEventSubscriptionProps(sns_topic_arn=sns_topic_arn, enabled=enabled, event_categories=event_categories, source_ids=source_ids, source_type=source_type, subscription_name=subscription_name, tags=tags)

        jsii.create(CfnEventSubscription, self, [scope, id, props])

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

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        """``AWS::DMS::EventSubscription.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-eventsubscription.html#cfn-dms-eventsubscription-tags
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="snsTopicArn")
    def sns_topic_arn(self) -> str:
        """``AWS::DMS::EventSubscription.SnsTopicArn``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-eventsubscription.html#cfn-dms-eventsubscription-snstopicarn
        """
        return jsii.get(self, "snsTopicArn")

    @sns_topic_arn.setter
    def sns_topic_arn(self, value: str):
        return jsii.set(self, "snsTopicArn", value)

    @property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::DMS::EventSubscription.Enabled``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-eventsubscription.html#cfn-dms-eventsubscription-enabled
        """
        return jsii.get(self, "enabled")

    @enabled.setter
    def enabled(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "enabled", value)

    @property
    @jsii.member(jsii_name="eventCategories")
    def event_categories(self) -> typing.Optional[typing.List[str]]:
        """``AWS::DMS::EventSubscription.EventCategories``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-eventsubscription.html#cfn-dms-eventsubscription-eventcategories
        """
        return jsii.get(self, "eventCategories")

    @event_categories.setter
    def event_categories(self, value: typing.Optional[typing.List[str]]):
        return jsii.set(self, "eventCategories", value)

    @property
    @jsii.member(jsii_name="sourceIds")
    def source_ids(self) -> typing.Optional[typing.List[str]]:
        """``AWS::DMS::EventSubscription.SourceIds``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-eventsubscription.html#cfn-dms-eventsubscription-sourceids
        """
        return jsii.get(self, "sourceIds")

    @source_ids.setter
    def source_ids(self, value: typing.Optional[typing.List[str]]):
        return jsii.set(self, "sourceIds", value)

    @property
    @jsii.member(jsii_name="sourceType")
    def source_type(self) -> typing.Optional[str]:
        """``AWS::DMS::EventSubscription.SourceType``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-eventsubscription.html#cfn-dms-eventsubscription-sourcetype
        """
        return jsii.get(self, "sourceType")

    @source_type.setter
    def source_type(self, value: typing.Optional[str]):
        return jsii.set(self, "sourceType", value)

    @property
    @jsii.member(jsii_name="subscriptionName")
    def subscription_name(self) -> typing.Optional[str]:
        """``AWS::DMS::EventSubscription.SubscriptionName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-eventsubscription.html#cfn-dms-eventsubscription-subscriptionname
        """
        return jsii.get(self, "subscriptionName")

    @subscription_name.setter
    def subscription_name(self, value: typing.Optional[str]):
        return jsii.set(self, "subscriptionName", value)


@jsii.data_type(jsii_type="@aws-cdk/aws-dms.CfnEventSubscriptionProps", jsii_struct_bases=[], name_mapping={'sns_topic_arn': 'snsTopicArn', 'enabled': 'enabled', 'event_categories': 'eventCategories', 'source_ids': 'sourceIds', 'source_type': 'sourceType', 'subscription_name': 'subscriptionName', 'tags': 'tags'})
class CfnEventSubscriptionProps():
    def __init__(self, *, sns_topic_arn: str, enabled: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, event_categories: typing.Optional[typing.List[str]]=None, source_ids: typing.Optional[typing.List[str]]=None, source_type: typing.Optional[str]=None, subscription_name: typing.Optional[str]=None, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None):
        """Properties for defining a ``AWS::DMS::EventSubscription``.

        :param sns_topic_arn: ``AWS::DMS::EventSubscription.SnsTopicArn``.
        :param enabled: ``AWS::DMS::EventSubscription.Enabled``.
        :param event_categories: ``AWS::DMS::EventSubscription.EventCategories``.
        :param source_ids: ``AWS::DMS::EventSubscription.SourceIds``.
        :param source_type: ``AWS::DMS::EventSubscription.SourceType``.
        :param subscription_name: ``AWS::DMS::EventSubscription.SubscriptionName``.
        :param tags: ``AWS::DMS::EventSubscription.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-eventsubscription.html
        """
        self._values = {
            'sns_topic_arn': sns_topic_arn,
        }
        if enabled is not None: self._values["enabled"] = enabled
        if event_categories is not None: self._values["event_categories"] = event_categories
        if source_ids is not None: self._values["source_ids"] = source_ids
        if source_type is not None: self._values["source_type"] = source_type
        if subscription_name is not None: self._values["subscription_name"] = subscription_name
        if tags is not None: self._values["tags"] = tags

    @property
    def sns_topic_arn(self) -> str:
        """``AWS::DMS::EventSubscription.SnsTopicArn``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-eventsubscription.html#cfn-dms-eventsubscription-snstopicarn
        """
        return self._values.get('sns_topic_arn')

    @property
    def enabled(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::DMS::EventSubscription.Enabled``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-eventsubscription.html#cfn-dms-eventsubscription-enabled
        """
        return self._values.get('enabled')

    @property
    def event_categories(self) -> typing.Optional[typing.List[str]]:
        """``AWS::DMS::EventSubscription.EventCategories``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-eventsubscription.html#cfn-dms-eventsubscription-eventcategories
        """
        return self._values.get('event_categories')

    @property
    def source_ids(self) -> typing.Optional[typing.List[str]]:
        """``AWS::DMS::EventSubscription.SourceIds``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-eventsubscription.html#cfn-dms-eventsubscription-sourceids
        """
        return self._values.get('source_ids')

    @property
    def source_type(self) -> typing.Optional[str]:
        """``AWS::DMS::EventSubscription.SourceType``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-eventsubscription.html#cfn-dms-eventsubscription-sourcetype
        """
        return self._values.get('source_type')

    @property
    def subscription_name(self) -> typing.Optional[str]:
        """``AWS::DMS::EventSubscription.SubscriptionName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-eventsubscription.html#cfn-dms-eventsubscription-subscriptionname
        """
        return self._values.get('subscription_name')

    @property
    def tags(self) -> typing.Optional[typing.List[aws_cdk.core.CfnTag]]:
        """``AWS::DMS::EventSubscription.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-eventsubscription.html#cfn-dms-eventsubscription-tags
        """
        return self._values.get('tags')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnEventSubscriptionProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnReplicationInstance(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-dms.CfnReplicationInstance"):
    """A CloudFormation ``AWS::DMS::ReplicationInstance``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationinstance.html
    cloudformationResource:
    :cloudformationResource:: AWS::DMS::ReplicationInstance
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, replication_instance_class: str, allocated_storage: typing.Optional[jsii.Number]=None, allow_major_version_upgrade: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, auto_minor_version_upgrade: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, availability_zone: typing.Optional[str]=None, engine_version: typing.Optional[str]=None, kms_key_id: typing.Optional[str]=None, multi_az: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, preferred_maintenance_window: typing.Optional[str]=None, publicly_accessible: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, replication_instance_identifier: typing.Optional[str]=None, replication_subnet_group_identifier: typing.Optional[str]=None, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None, vpc_security_group_ids: typing.Optional[typing.List[str]]=None) -> None:
        """Create a new ``AWS::DMS::ReplicationInstance``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param replication_instance_class: ``AWS::DMS::ReplicationInstance.ReplicationInstanceClass``.
        :param allocated_storage: ``AWS::DMS::ReplicationInstance.AllocatedStorage``.
        :param allow_major_version_upgrade: ``AWS::DMS::ReplicationInstance.AllowMajorVersionUpgrade``.
        :param auto_minor_version_upgrade: ``AWS::DMS::ReplicationInstance.AutoMinorVersionUpgrade``.
        :param availability_zone: ``AWS::DMS::ReplicationInstance.AvailabilityZone``.
        :param engine_version: ``AWS::DMS::ReplicationInstance.EngineVersion``.
        :param kms_key_id: ``AWS::DMS::ReplicationInstance.KmsKeyId``.
        :param multi_az: ``AWS::DMS::ReplicationInstance.MultiAZ``.
        :param preferred_maintenance_window: ``AWS::DMS::ReplicationInstance.PreferredMaintenanceWindow``.
        :param publicly_accessible: ``AWS::DMS::ReplicationInstance.PubliclyAccessible``.
        :param replication_instance_identifier: ``AWS::DMS::ReplicationInstance.ReplicationInstanceIdentifier``.
        :param replication_subnet_group_identifier: ``AWS::DMS::ReplicationInstance.ReplicationSubnetGroupIdentifier``.
        :param tags: ``AWS::DMS::ReplicationInstance.Tags``.
        :param vpc_security_group_ids: ``AWS::DMS::ReplicationInstance.VpcSecurityGroupIds``.
        """
        props = CfnReplicationInstanceProps(replication_instance_class=replication_instance_class, allocated_storage=allocated_storage, allow_major_version_upgrade=allow_major_version_upgrade, auto_minor_version_upgrade=auto_minor_version_upgrade, availability_zone=availability_zone, engine_version=engine_version, kms_key_id=kms_key_id, multi_az=multi_az, preferred_maintenance_window=preferred_maintenance_window, publicly_accessible=publicly_accessible, replication_instance_identifier=replication_instance_identifier, replication_subnet_group_identifier=replication_subnet_group_identifier, tags=tags, vpc_security_group_ids=vpc_security_group_ids)

        jsii.create(CfnReplicationInstance, self, [scope, id, props])

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

    @property
    @jsii.member(jsii_name="attrReplicationInstancePrivateIpAddresses")
    def attr_replication_instance_private_ip_addresses(self) -> typing.List[str]:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: ReplicationInstancePrivateIpAddresses
        """
        return jsii.get(self, "attrReplicationInstancePrivateIpAddresses")

    @property
    @jsii.member(jsii_name="attrReplicationInstancePublicIpAddresses")
    def attr_replication_instance_public_ip_addresses(self) -> typing.List[str]:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: ReplicationInstancePublicIpAddresses
        """
        return jsii.get(self, "attrReplicationInstancePublicIpAddresses")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        """``AWS::DMS::ReplicationInstance.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationinstance.html#cfn-dms-replicationinstance-tags
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="replicationInstanceClass")
    def replication_instance_class(self) -> str:
        """``AWS::DMS::ReplicationInstance.ReplicationInstanceClass``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationinstance.html#cfn-dms-replicationinstance-replicationinstanceclass
        """
        return jsii.get(self, "replicationInstanceClass")

    @replication_instance_class.setter
    def replication_instance_class(self, value: str):
        return jsii.set(self, "replicationInstanceClass", value)

    @property
    @jsii.member(jsii_name="allocatedStorage")
    def allocated_storage(self) -> typing.Optional[jsii.Number]:
        """``AWS::DMS::ReplicationInstance.AllocatedStorage``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationinstance.html#cfn-dms-replicationinstance-allocatedstorage
        """
        return jsii.get(self, "allocatedStorage")

    @allocated_storage.setter
    def allocated_storage(self, value: typing.Optional[jsii.Number]):
        return jsii.set(self, "allocatedStorage", value)

    @property
    @jsii.member(jsii_name="allowMajorVersionUpgrade")
    def allow_major_version_upgrade(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::DMS::ReplicationInstance.AllowMajorVersionUpgrade``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationinstance.html#cfn-dms-replicationinstance-allowmajorversionupgrade
        """
        return jsii.get(self, "allowMajorVersionUpgrade")

    @allow_major_version_upgrade.setter
    def allow_major_version_upgrade(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "allowMajorVersionUpgrade", value)

    @property
    @jsii.member(jsii_name="autoMinorVersionUpgrade")
    def auto_minor_version_upgrade(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::DMS::ReplicationInstance.AutoMinorVersionUpgrade``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationinstance.html#cfn-dms-replicationinstance-autominorversionupgrade
        """
        return jsii.get(self, "autoMinorVersionUpgrade")

    @auto_minor_version_upgrade.setter
    def auto_minor_version_upgrade(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "autoMinorVersionUpgrade", value)

    @property
    @jsii.member(jsii_name="availabilityZone")
    def availability_zone(self) -> typing.Optional[str]:
        """``AWS::DMS::ReplicationInstance.AvailabilityZone``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationinstance.html#cfn-dms-replicationinstance-availabilityzone
        """
        return jsii.get(self, "availabilityZone")

    @availability_zone.setter
    def availability_zone(self, value: typing.Optional[str]):
        return jsii.set(self, "availabilityZone", value)

    @property
    @jsii.member(jsii_name="engineVersion")
    def engine_version(self) -> typing.Optional[str]:
        """``AWS::DMS::ReplicationInstance.EngineVersion``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationinstance.html#cfn-dms-replicationinstance-engineversion
        """
        return jsii.get(self, "engineVersion")

    @engine_version.setter
    def engine_version(self, value: typing.Optional[str]):
        return jsii.set(self, "engineVersion", value)

    @property
    @jsii.member(jsii_name="kmsKeyId")
    def kms_key_id(self) -> typing.Optional[str]:
        """``AWS::DMS::ReplicationInstance.KmsKeyId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationinstance.html#cfn-dms-replicationinstance-kmskeyid
        """
        return jsii.get(self, "kmsKeyId")

    @kms_key_id.setter
    def kms_key_id(self, value: typing.Optional[str]):
        return jsii.set(self, "kmsKeyId", value)

    @property
    @jsii.member(jsii_name="multiAz")
    def multi_az(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::DMS::ReplicationInstance.MultiAZ``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationinstance.html#cfn-dms-replicationinstance-multiaz
        """
        return jsii.get(self, "multiAz")

    @multi_az.setter
    def multi_az(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "multiAz", value)

    @property
    @jsii.member(jsii_name="preferredMaintenanceWindow")
    def preferred_maintenance_window(self) -> typing.Optional[str]:
        """``AWS::DMS::ReplicationInstance.PreferredMaintenanceWindow``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationinstance.html#cfn-dms-replicationinstance-preferredmaintenancewindow
        """
        return jsii.get(self, "preferredMaintenanceWindow")

    @preferred_maintenance_window.setter
    def preferred_maintenance_window(self, value: typing.Optional[str]):
        return jsii.set(self, "preferredMaintenanceWindow", value)

    @property
    @jsii.member(jsii_name="publiclyAccessible")
    def publicly_accessible(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::DMS::ReplicationInstance.PubliclyAccessible``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationinstance.html#cfn-dms-replicationinstance-publiclyaccessible
        """
        return jsii.get(self, "publiclyAccessible")

    @publicly_accessible.setter
    def publicly_accessible(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "publiclyAccessible", value)

    @property
    @jsii.member(jsii_name="replicationInstanceIdentifier")
    def replication_instance_identifier(self) -> typing.Optional[str]:
        """``AWS::DMS::ReplicationInstance.ReplicationInstanceIdentifier``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationinstance.html#cfn-dms-replicationinstance-replicationinstanceidentifier
        """
        return jsii.get(self, "replicationInstanceIdentifier")

    @replication_instance_identifier.setter
    def replication_instance_identifier(self, value: typing.Optional[str]):
        return jsii.set(self, "replicationInstanceIdentifier", value)

    @property
    @jsii.member(jsii_name="replicationSubnetGroupIdentifier")
    def replication_subnet_group_identifier(self) -> typing.Optional[str]:
        """``AWS::DMS::ReplicationInstance.ReplicationSubnetGroupIdentifier``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationinstance.html#cfn-dms-replicationinstance-replicationsubnetgroupidentifier
        """
        return jsii.get(self, "replicationSubnetGroupIdentifier")

    @replication_subnet_group_identifier.setter
    def replication_subnet_group_identifier(self, value: typing.Optional[str]):
        return jsii.set(self, "replicationSubnetGroupIdentifier", value)

    @property
    @jsii.member(jsii_name="vpcSecurityGroupIds")
    def vpc_security_group_ids(self) -> typing.Optional[typing.List[str]]:
        """``AWS::DMS::ReplicationInstance.VpcSecurityGroupIds``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationinstance.html#cfn-dms-replicationinstance-vpcsecuritygroupids
        """
        return jsii.get(self, "vpcSecurityGroupIds")

    @vpc_security_group_ids.setter
    def vpc_security_group_ids(self, value: typing.Optional[typing.List[str]]):
        return jsii.set(self, "vpcSecurityGroupIds", value)


@jsii.data_type(jsii_type="@aws-cdk/aws-dms.CfnReplicationInstanceProps", jsii_struct_bases=[], name_mapping={'replication_instance_class': 'replicationInstanceClass', 'allocated_storage': 'allocatedStorage', 'allow_major_version_upgrade': 'allowMajorVersionUpgrade', 'auto_minor_version_upgrade': 'autoMinorVersionUpgrade', 'availability_zone': 'availabilityZone', 'engine_version': 'engineVersion', 'kms_key_id': 'kmsKeyId', 'multi_az': 'multiAz', 'preferred_maintenance_window': 'preferredMaintenanceWindow', 'publicly_accessible': 'publiclyAccessible', 'replication_instance_identifier': 'replicationInstanceIdentifier', 'replication_subnet_group_identifier': 'replicationSubnetGroupIdentifier', 'tags': 'tags', 'vpc_security_group_ids': 'vpcSecurityGroupIds'})
class CfnReplicationInstanceProps():
    def __init__(self, *, replication_instance_class: str, allocated_storage: typing.Optional[jsii.Number]=None, allow_major_version_upgrade: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, auto_minor_version_upgrade: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, availability_zone: typing.Optional[str]=None, engine_version: typing.Optional[str]=None, kms_key_id: typing.Optional[str]=None, multi_az: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, preferred_maintenance_window: typing.Optional[str]=None, publicly_accessible: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, replication_instance_identifier: typing.Optional[str]=None, replication_subnet_group_identifier: typing.Optional[str]=None, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None, vpc_security_group_ids: typing.Optional[typing.List[str]]=None):
        """Properties for defining a ``AWS::DMS::ReplicationInstance``.

        :param replication_instance_class: ``AWS::DMS::ReplicationInstance.ReplicationInstanceClass``.
        :param allocated_storage: ``AWS::DMS::ReplicationInstance.AllocatedStorage``.
        :param allow_major_version_upgrade: ``AWS::DMS::ReplicationInstance.AllowMajorVersionUpgrade``.
        :param auto_minor_version_upgrade: ``AWS::DMS::ReplicationInstance.AutoMinorVersionUpgrade``.
        :param availability_zone: ``AWS::DMS::ReplicationInstance.AvailabilityZone``.
        :param engine_version: ``AWS::DMS::ReplicationInstance.EngineVersion``.
        :param kms_key_id: ``AWS::DMS::ReplicationInstance.KmsKeyId``.
        :param multi_az: ``AWS::DMS::ReplicationInstance.MultiAZ``.
        :param preferred_maintenance_window: ``AWS::DMS::ReplicationInstance.PreferredMaintenanceWindow``.
        :param publicly_accessible: ``AWS::DMS::ReplicationInstance.PubliclyAccessible``.
        :param replication_instance_identifier: ``AWS::DMS::ReplicationInstance.ReplicationInstanceIdentifier``.
        :param replication_subnet_group_identifier: ``AWS::DMS::ReplicationInstance.ReplicationSubnetGroupIdentifier``.
        :param tags: ``AWS::DMS::ReplicationInstance.Tags``.
        :param vpc_security_group_ids: ``AWS::DMS::ReplicationInstance.VpcSecurityGroupIds``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationinstance.html
        """
        self._values = {
            'replication_instance_class': replication_instance_class,
        }
        if allocated_storage is not None: self._values["allocated_storage"] = allocated_storage
        if allow_major_version_upgrade is not None: self._values["allow_major_version_upgrade"] = allow_major_version_upgrade
        if auto_minor_version_upgrade is not None: self._values["auto_minor_version_upgrade"] = auto_minor_version_upgrade
        if availability_zone is not None: self._values["availability_zone"] = availability_zone
        if engine_version is not None: self._values["engine_version"] = engine_version
        if kms_key_id is not None: self._values["kms_key_id"] = kms_key_id
        if multi_az is not None: self._values["multi_az"] = multi_az
        if preferred_maintenance_window is not None: self._values["preferred_maintenance_window"] = preferred_maintenance_window
        if publicly_accessible is not None: self._values["publicly_accessible"] = publicly_accessible
        if replication_instance_identifier is not None: self._values["replication_instance_identifier"] = replication_instance_identifier
        if replication_subnet_group_identifier is not None: self._values["replication_subnet_group_identifier"] = replication_subnet_group_identifier
        if tags is not None: self._values["tags"] = tags
        if vpc_security_group_ids is not None: self._values["vpc_security_group_ids"] = vpc_security_group_ids

    @property
    def replication_instance_class(self) -> str:
        """``AWS::DMS::ReplicationInstance.ReplicationInstanceClass``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationinstance.html#cfn-dms-replicationinstance-replicationinstanceclass
        """
        return self._values.get('replication_instance_class')

    @property
    def allocated_storage(self) -> typing.Optional[jsii.Number]:
        """``AWS::DMS::ReplicationInstance.AllocatedStorage``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationinstance.html#cfn-dms-replicationinstance-allocatedstorage
        """
        return self._values.get('allocated_storage')

    @property
    def allow_major_version_upgrade(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::DMS::ReplicationInstance.AllowMajorVersionUpgrade``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationinstance.html#cfn-dms-replicationinstance-allowmajorversionupgrade
        """
        return self._values.get('allow_major_version_upgrade')

    @property
    def auto_minor_version_upgrade(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::DMS::ReplicationInstance.AutoMinorVersionUpgrade``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationinstance.html#cfn-dms-replicationinstance-autominorversionupgrade
        """
        return self._values.get('auto_minor_version_upgrade')

    @property
    def availability_zone(self) -> typing.Optional[str]:
        """``AWS::DMS::ReplicationInstance.AvailabilityZone``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationinstance.html#cfn-dms-replicationinstance-availabilityzone
        """
        return self._values.get('availability_zone')

    @property
    def engine_version(self) -> typing.Optional[str]:
        """``AWS::DMS::ReplicationInstance.EngineVersion``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationinstance.html#cfn-dms-replicationinstance-engineversion
        """
        return self._values.get('engine_version')

    @property
    def kms_key_id(self) -> typing.Optional[str]:
        """``AWS::DMS::ReplicationInstance.KmsKeyId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationinstance.html#cfn-dms-replicationinstance-kmskeyid
        """
        return self._values.get('kms_key_id')

    @property
    def multi_az(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::DMS::ReplicationInstance.MultiAZ``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationinstance.html#cfn-dms-replicationinstance-multiaz
        """
        return self._values.get('multi_az')

    @property
    def preferred_maintenance_window(self) -> typing.Optional[str]:
        """``AWS::DMS::ReplicationInstance.PreferredMaintenanceWindow``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationinstance.html#cfn-dms-replicationinstance-preferredmaintenancewindow
        """
        return self._values.get('preferred_maintenance_window')

    @property
    def publicly_accessible(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::DMS::ReplicationInstance.PubliclyAccessible``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationinstance.html#cfn-dms-replicationinstance-publiclyaccessible
        """
        return self._values.get('publicly_accessible')

    @property
    def replication_instance_identifier(self) -> typing.Optional[str]:
        """``AWS::DMS::ReplicationInstance.ReplicationInstanceIdentifier``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationinstance.html#cfn-dms-replicationinstance-replicationinstanceidentifier
        """
        return self._values.get('replication_instance_identifier')

    @property
    def replication_subnet_group_identifier(self) -> typing.Optional[str]:
        """``AWS::DMS::ReplicationInstance.ReplicationSubnetGroupIdentifier``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationinstance.html#cfn-dms-replicationinstance-replicationsubnetgroupidentifier
        """
        return self._values.get('replication_subnet_group_identifier')

    @property
    def tags(self) -> typing.Optional[typing.List[aws_cdk.core.CfnTag]]:
        """``AWS::DMS::ReplicationInstance.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationinstance.html#cfn-dms-replicationinstance-tags
        """
        return self._values.get('tags')

    @property
    def vpc_security_group_ids(self) -> typing.Optional[typing.List[str]]:
        """``AWS::DMS::ReplicationInstance.VpcSecurityGroupIds``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationinstance.html#cfn-dms-replicationinstance-vpcsecuritygroupids
        """
        return self._values.get('vpc_security_group_ids')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnReplicationInstanceProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnReplicationSubnetGroup(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-dms.CfnReplicationSubnetGroup"):
    """A CloudFormation ``AWS::DMS::ReplicationSubnetGroup``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationsubnetgroup.html
    cloudformationResource:
    :cloudformationResource:: AWS::DMS::ReplicationSubnetGroup
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, replication_subnet_group_description: str, subnet_ids: typing.List[str], replication_subnet_group_identifier: typing.Optional[str]=None, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None) -> None:
        """Create a new ``AWS::DMS::ReplicationSubnetGroup``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param replication_subnet_group_description: ``AWS::DMS::ReplicationSubnetGroup.ReplicationSubnetGroupDescription``.
        :param subnet_ids: ``AWS::DMS::ReplicationSubnetGroup.SubnetIds``.
        :param replication_subnet_group_identifier: ``AWS::DMS::ReplicationSubnetGroup.ReplicationSubnetGroupIdentifier``.
        :param tags: ``AWS::DMS::ReplicationSubnetGroup.Tags``.
        """
        props = CfnReplicationSubnetGroupProps(replication_subnet_group_description=replication_subnet_group_description, subnet_ids=subnet_ids, replication_subnet_group_identifier=replication_subnet_group_identifier, tags=tags)

        jsii.create(CfnReplicationSubnetGroup, self, [scope, id, props])

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

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        """``AWS::DMS::ReplicationSubnetGroup.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationsubnetgroup.html#cfn-dms-replicationsubnetgroup-tags
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="replicationSubnetGroupDescription")
    def replication_subnet_group_description(self) -> str:
        """``AWS::DMS::ReplicationSubnetGroup.ReplicationSubnetGroupDescription``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationsubnetgroup.html#cfn-dms-replicationsubnetgroup-replicationsubnetgroupdescription
        """
        return jsii.get(self, "replicationSubnetGroupDescription")

    @replication_subnet_group_description.setter
    def replication_subnet_group_description(self, value: str):
        return jsii.set(self, "replicationSubnetGroupDescription", value)

    @property
    @jsii.member(jsii_name="subnetIds")
    def subnet_ids(self) -> typing.List[str]:
        """``AWS::DMS::ReplicationSubnetGroup.SubnetIds``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationsubnetgroup.html#cfn-dms-replicationsubnetgroup-subnetids
        """
        return jsii.get(self, "subnetIds")

    @subnet_ids.setter
    def subnet_ids(self, value: typing.List[str]):
        return jsii.set(self, "subnetIds", value)

    @property
    @jsii.member(jsii_name="replicationSubnetGroupIdentifier")
    def replication_subnet_group_identifier(self) -> typing.Optional[str]:
        """``AWS::DMS::ReplicationSubnetGroup.ReplicationSubnetGroupIdentifier``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationsubnetgroup.html#cfn-dms-replicationsubnetgroup-replicationsubnetgroupidentifier
        """
        return jsii.get(self, "replicationSubnetGroupIdentifier")

    @replication_subnet_group_identifier.setter
    def replication_subnet_group_identifier(self, value: typing.Optional[str]):
        return jsii.set(self, "replicationSubnetGroupIdentifier", value)


@jsii.data_type(jsii_type="@aws-cdk/aws-dms.CfnReplicationSubnetGroupProps", jsii_struct_bases=[], name_mapping={'replication_subnet_group_description': 'replicationSubnetGroupDescription', 'subnet_ids': 'subnetIds', 'replication_subnet_group_identifier': 'replicationSubnetGroupIdentifier', 'tags': 'tags'})
class CfnReplicationSubnetGroupProps():
    def __init__(self, *, replication_subnet_group_description: str, subnet_ids: typing.List[str], replication_subnet_group_identifier: typing.Optional[str]=None, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None):
        """Properties for defining a ``AWS::DMS::ReplicationSubnetGroup``.

        :param replication_subnet_group_description: ``AWS::DMS::ReplicationSubnetGroup.ReplicationSubnetGroupDescription``.
        :param subnet_ids: ``AWS::DMS::ReplicationSubnetGroup.SubnetIds``.
        :param replication_subnet_group_identifier: ``AWS::DMS::ReplicationSubnetGroup.ReplicationSubnetGroupIdentifier``.
        :param tags: ``AWS::DMS::ReplicationSubnetGroup.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationsubnetgroup.html
        """
        self._values = {
            'replication_subnet_group_description': replication_subnet_group_description,
            'subnet_ids': subnet_ids,
        }
        if replication_subnet_group_identifier is not None: self._values["replication_subnet_group_identifier"] = replication_subnet_group_identifier
        if tags is not None: self._values["tags"] = tags

    @property
    def replication_subnet_group_description(self) -> str:
        """``AWS::DMS::ReplicationSubnetGroup.ReplicationSubnetGroupDescription``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationsubnetgroup.html#cfn-dms-replicationsubnetgroup-replicationsubnetgroupdescription
        """
        return self._values.get('replication_subnet_group_description')

    @property
    def subnet_ids(self) -> typing.List[str]:
        """``AWS::DMS::ReplicationSubnetGroup.SubnetIds``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationsubnetgroup.html#cfn-dms-replicationsubnetgroup-subnetids
        """
        return self._values.get('subnet_ids')

    @property
    def replication_subnet_group_identifier(self) -> typing.Optional[str]:
        """``AWS::DMS::ReplicationSubnetGroup.ReplicationSubnetGroupIdentifier``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationsubnetgroup.html#cfn-dms-replicationsubnetgroup-replicationsubnetgroupidentifier
        """
        return self._values.get('replication_subnet_group_identifier')

    @property
    def tags(self) -> typing.Optional[typing.List[aws_cdk.core.CfnTag]]:
        """``AWS::DMS::ReplicationSubnetGroup.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationsubnetgroup.html#cfn-dms-replicationsubnetgroup-tags
        """
        return self._values.get('tags')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnReplicationSubnetGroupProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnReplicationTask(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-dms.CfnReplicationTask"):
    """A CloudFormation ``AWS::DMS::ReplicationTask``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationtask.html
    cloudformationResource:
    :cloudformationResource:: AWS::DMS::ReplicationTask
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, migration_type: str, replication_instance_arn: str, source_endpoint_arn: str, table_mappings: str, target_endpoint_arn: str, cdc_start_position: typing.Optional[str]=None, cdc_start_time: typing.Optional[jsii.Number]=None, cdc_stop_position: typing.Optional[str]=None, replication_task_identifier: typing.Optional[str]=None, replication_task_settings: typing.Optional[str]=None, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None) -> None:
        """Create a new ``AWS::DMS::ReplicationTask``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param migration_type: ``AWS::DMS::ReplicationTask.MigrationType``.
        :param replication_instance_arn: ``AWS::DMS::ReplicationTask.ReplicationInstanceArn``.
        :param source_endpoint_arn: ``AWS::DMS::ReplicationTask.SourceEndpointArn``.
        :param table_mappings: ``AWS::DMS::ReplicationTask.TableMappings``.
        :param target_endpoint_arn: ``AWS::DMS::ReplicationTask.TargetEndpointArn``.
        :param cdc_start_position: ``AWS::DMS::ReplicationTask.CdcStartPosition``.
        :param cdc_start_time: ``AWS::DMS::ReplicationTask.CdcStartTime``.
        :param cdc_stop_position: ``AWS::DMS::ReplicationTask.CdcStopPosition``.
        :param replication_task_identifier: ``AWS::DMS::ReplicationTask.ReplicationTaskIdentifier``.
        :param replication_task_settings: ``AWS::DMS::ReplicationTask.ReplicationTaskSettings``.
        :param tags: ``AWS::DMS::ReplicationTask.Tags``.
        """
        props = CfnReplicationTaskProps(migration_type=migration_type, replication_instance_arn=replication_instance_arn, source_endpoint_arn=source_endpoint_arn, table_mappings=table_mappings, target_endpoint_arn=target_endpoint_arn, cdc_start_position=cdc_start_position, cdc_start_time=cdc_start_time, cdc_stop_position=cdc_stop_position, replication_task_identifier=replication_task_identifier, replication_task_settings=replication_task_settings, tags=tags)

        jsii.create(CfnReplicationTask, self, [scope, id, props])

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

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        """``AWS::DMS::ReplicationTask.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationtask.html#cfn-dms-replicationtask-tags
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="migrationType")
    def migration_type(self) -> str:
        """``AWS::DMS::ReplicationTask.MigrationType``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationtask.html#cfn-dms-replicationtask-migrationtype
        """
        return jsii.get(self, "migrationType")

    @migration_type.setter
    def migration_type(self, value: str):
        return jsii.set(self, "migrationType", value)

    @property
    @jsii.member(jsii_name="replicationInstanceArn")
    def replication_instance_arn(self) -> str:
        """``AWS::DMS::ReplicationTask.ReplicationInstanceArn``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationtask.html#cfn-dms-replicationtask-replicationinstancearn
        """
        return jsii.get(self, "replicationInstanceArn")

    @replication_instance_arn.setter
    def replication_instance_arn(self, value: str):
        return jsii.set(self, "replicationInstanceArn", value)

    @property
    @jsii.member(jsii_name="sourceEndpointArn")
    def source_endpoint_arn(self) -> str:
        """``AWS::DMS::ReplicationTask.SourceEndpointArn``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationtask.html#cfn-dms-replicationtask-sourceendpointarn
        """
        return jsii.get(self, "sourceEndpointArn")

    @source_endpoint_arn.setter
    def source_endpoint_arn(self, value: str):
        return jsii.set(self, "sourceEndpointArn", value)

    @property
    @jsii.member(jsii_name="tableMappings")
    def table_mappings(self) -> str:
        """``AWS::DMS::ReplicationTask.TableMappings``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationtask.html#cfn-dms-replicationtask-tablemappings
        """
        return jsii.get(self, "tableMappings")

    @table_mappings.setter
    def table_mappings(self, value: str):
        return jsii.set(self, "tableMappings", value)

    @property
    @jsii.member(jsii_name="targetEndpointArn")
    def target_endpoint_arn(self) -> str:
        """``AWS::DMS::ReplicationTask.TargetEndpointArn``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationtask.html#cfn-dms-replicationtask-targetendpointarn
        """
        return jsii.get(self, "targetEndpointArn")

    @target_endpoint_arn.setter
    def target_endpoint_arn(self, value: str):
        return jsii.set(self, "targetEndpointArn", value)

    @property
    @jsii.member(jsii_name="cdcStartPosition")
    def cdc_start_position(self) -> typing.Optional[str]:
        """``AWS::DMS::ReplicationTask.CdcStartPosition``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationtask.html#cfn-dms-replicationtask-cdcstartposition
        """
        return jsii.get(self, "cdcStartPosition")

    @cdc_start_position.setter
    def cdc_start_position(self, value: typing.Optional[str]):
        return jsii.set(self, "cdcStartPosition", value)

    @property
    @jsii.member(jsii_name="cdcStartTime")
    def cdc_start_time(self) -> typing.Optional[jsii.Number]:
        """``AWS::DMS::ReplicationTask.CdcStartTime``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationtask.html#cfn-dms-replicationtask-cdcstarttime
        """
        return jsii.get(self, "cdcStartTime")

    @cdc_start_time.setter
    def cdc_start_time(self, value: typing.Optional[jsii.Number]):
        return jsii.set(self, "cdcStartTime", value)

    @property
    @jsii.member(jsii_name="cdcStopPosition")
    def cdc_stop_position(self) -> typing.Optional[str]:
        """``AWS::DMS::ReplicationTask.CdcStopPosition``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationtask.html#cfn-dms-replicationtask-cdcstopposition
        """
        return jsii.get(self, "cdcStopPosition")

    @cdc_stop_position.setter
    def cdc_stop_position(self, value: typing.Optional[str]):
        return jsii.set(self, "cdcStopPosition", value)

    @property
    @jsii.member(jsii_name="replicationTaskIdentifier")
    def replication_task_identifier(self) -> typing.Optional[str]:
        """``AWS::DMS::ReplicationTask.ReplicationTaskIdentifier``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationtask.html#cfn-dms-replicationtask-replicationtaskidentifier
        """
        return jsii.get(self, "replicationTaskIdentifier")

    @replication_task_identifier.setter
    def replication_task_identifier(self, value: typing.Optional[str]):
        return jsii.set(self, "replicationTaskIdentifier", value)

    @property
    @jsii.member(jsii_name="replicationTaskSettings")
    def replication_task_settings(self) -> typing.Optional[str]:
        """``AWS::DMS::ReplicationTask.ReplicationTaskSettings``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationtask.html#cfn-dms-replicationtask-replicationtasksettings
        """
        return jsii.get(self, "replicationTaskSettings")

    @replication_task_settings.setter
    def replication_task_settings(self, value: typing.Optional[str]):
        return jsii.set(self, "replicationTaskSettings", value)


@jsii.data_type(jsii_type="@aws-cdk/aws-dms.CfnReplicationTaskProps", jsii_struct_bases=[], name_mapping={'migration_type': 'migrationType', 'replication_instance_arn': 'replicationInstanceArn', 'source_endpoint_arn': 'sourceEndpointArn', 'table_mappings': 'tableMappings', 'target_endpoint_arn': 'targetEndpointArn', 'cdc_start_position': 'cdcStartPosition', 'cdc_start_time': 'cdcStartTime', 'cdc_stop_position': 'cdcStopPosition', 'replication_task_identifier': 'replicationTaskIdentifier', 'replication_task_settings': 'replicationTaskSettings', 'tags': 'tags'})
class CfnReplicationTaskProps():
    def __init__(self, *, migration_type: str, replication_instance_arn: str, source_endpoint_arn: str, table_mappings: str, target_endpoint_arn: str, cdc_start_position: typing.Optional[str]=None, cdc_start_time: typing.Optional[jsii.Number]=None, cdc_stop_position: typing.Optional[str]=None, replication_task_identifier: typing.Optional[str]=None, replication_task_settings: typing.Optional[str]=None, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None):
        """Properties for defining a ``AWS::DMS::ReplicationTask``.

        :param migration_type: ``AWS::DMS::ReplicationTask.MigrationType``.
        :param replication_instance_arn: ``AWS::DMS::ReplicationTask.ReplicationInstanceArn``.
        :param source_endpoint_arn: ``AWS::DMS::ReplicationTask.SourceEndpointArn``.
        :param table_mappings: ``AWS::DMS::ReplicationTask.TableMappings``.
        :param target_endpoint_arn: ``AWS::DMS::ReplicationTask.TargetEndpointArn``.
        :param cdc_start_position: ``AWS::DMS::ReplicationTask.CdcStartPosition``.
        :param cdc_start_time: ``AWS::DMS::ReplicationTask.CdcStartTime``.
        :param cdc_stop_position: ``AWS::DMS::ReplicationTask.CdcStopPosition``.
        :param replication_task_identifier: ``AWS::DMS::ReplicationTask.ReplicationTaskIdentifier``.
        :param replication_task_settings: ``AWS::DMS::ReplicationTask.ReplicationTaskSettings``.
        :param tags: ``AWS::DMS::ReplicationTask.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationtask.html
        """
        self._values = {
            'migration_type': migration_type,
            'replication_instance_arn': replication_instance_arn,
            'source_endpoint_arn': source_endpoint_arn,
            'table_mappings': table_mappings,
            'target_endpoint_arn': target_endpoint_arn,
        }
        if cdc_start_position is not None: self._values["cdc_start_position"] = cdc_start_position
        if cdc_start_time is not None: self._values["cdc_start_time"] = cdc_start_time
        if cdc_stop_position is not None: self._values["cdc_stop_position"] = cdc_stop_position
        if replication_task_identifier is not None: self._values["replication_task_identifier"] = replication_task_identifier
        if replication_task_settings is not None: self._values["replication_task_settings"] = replication_task_settings
        if tags is not None: self._values["tags"] = tags

    @property
    def migration_type(self) -> str:
        """``AWS::DMS::ReplicationTask.MigrationType``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationtask.html#cfn-dms-replicationtask-migrationtype
        """
        return self._values.get('migration_type')

    @property
    def replication_instance_arn(self) -> str:
        """``AWS::DMS::ReplicationTask.ReplicationInstanceArn``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationtask.html#cfn-dms-replicationtask-replicationinstancearn
        """
        return self._values.get('replication_instance_arn')

    @property
    def source_endpoint_arn(self) -> str:
        """``AWS::DMS::ReplicationTask.SourceEndpointArn``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationtask.html#cfn-dms-replicationtask-sourceendpointarn
        """
        return self._values.get('source_endpoint_arn')

    @property
    def table_mappings(self) -> str:
        """``AWS::DMS::ReplicationTask.TableMappings``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationtask.html#cfn-dms-replicationtask-tablemappings
        """
        return self._values.get('table_mappings')

    @property
    def target_endpoint_arn(self) -> str:
        """``AWS::DMS::ReplicationTask.TargetEndpointArn``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationtask.html#cfn-dms-replicationtask-targetendpointarn
        """
        return self._values.get('target_endpoint_arn')

    @property
    def cdc_start_position(self) -> typing.Optional[str]:
        """``AWS::DMS::ReplicationTask.CdcStartPosition``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationtask.html#cfn-dms-replicationtask-cdcstartposition
        """
        return self._values.get('cdc_start_position')

    @property
    def cdc_start_time(self) -> typing.Optional[jsii.Number]:
        """``AWS::DMS::ReplicationTask.CdcStartTime``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationtask.html#cfn-dms-replicationtask-cdcstarttime
        """
        return self._values.get('cdc_start_time')

    @property
    def cdc_stop_position(self) -> typing.Optional[str]:
        """``AWS::DMS::ReplicationTask.CdcStopPosition``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationtask.html#cfn-dms-replicationtask-cdcstopposition
        """
        return self._values.get('cdc_stop_position')

    @property
    def replication_task_identifier(self) -> typing.Optional[str]:
        """``AWS::DMS::ReplicationTask.ReplicationTaskIdentifier``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationtask.html#cfn-dms-replicationtask-replicationtaskidentifier
        """
        return self._values.get('replication_task_identifier')

    @property
    def replication_task_settings(self) -> typing.Optional[str]:
        """``AWS::DMS::ReplicationTask.ReplicationTaskSettings``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationtask.html#cfn-dms-replicationtask-replicationtasksettings
        """
        return self._values.get('replication_task_settings')

    @property
    def tags(self) -> typing.Optional[typing.List[aws_cdk.core.CfnTag]]:
        """``AWS::DMS::ReplicationTask.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationtask.html#cfn-dms-replicationtask-tags
        """
        return self._values.get('tags')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnReplicationTaskProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


__all__ = ["CfnCertificate", "CfnCertificateProps", "CfnEndpoint", "CfnEndpointProps", "CfnEventSubscription", "CfnEventSubscriptionProps", "CfnReplicationInstance", "CfnReplicationInstanceProps", "CfnReplicationSubnetGroup", "CfnReplicationSubnetGroupProps", "CfnReplicationTask", "CfnReplicationTaskProps", "__jsii_assembly__"]

publication.publish()
