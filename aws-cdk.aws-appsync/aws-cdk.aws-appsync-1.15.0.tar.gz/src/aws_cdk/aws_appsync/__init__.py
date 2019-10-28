import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.core
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-appsync", "1.15.0", __name__, "aws-appsync@1.15.0.jsii.tgz")
class CfnApiKey(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-appsync.CfnApiKey"):
    """A CloudFormation ``AWS::AppSync::ApiKey``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-apikey.html
    cloudformationResource:
    :cloudformationResource:: AWS::AppSync::ApiKey
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, api_id: str, description: typing.Optional[str]=None, expires: typing.Optional[jsii.Number]=None) -> None:
        """Create a new ``AWS::AppSync::ApiKey``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param api_id: ``AWS::AppSync::ApiKey.ApiId``.
        :param description: ``AWS::AppSync::ApiKey.Description``.
        :param expires: ``AWS::AppSync::ApiKey.Expires``.
        """
        props = CfnApiKeyProps(api_id=api_id, description=description, expires=expires)

        jsii.create(CfnApiKey, self, [scope, id, props])

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
    @jsii.member(jsii_name="attrApiKey")
    def attr_api_key(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: ApiKey
        """
        return jsii.get(self, "attrApiKey")

    @property
    @jsii.member(jsii_name="attrArn")
    def attr_arn(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: Arn
        """
        return jsii.get(self, "attrArn")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="apiId")
    def api_id(self) -> str:
        """``AWS::AppSync::ApiKey.ApiId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-apikey.html#cfn-appsync-apikey-apiid
        """
        return jsii.get(self, "apiId")

    @api_id.setter
    def api_id(self, value: str):
        return jsii.set(self, "apiId", value)

    @property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[str]:
        """``AWS::AppSync::ApiKey.Description``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-apikey.html#cfn-appsync-apikey-description
        """
        return jsii.get(self, "description")

    @description.setter
    def description(self, value: typing.Optional[str]):
        return jsii.set(self, "description", value)

    @property
    @jsii.member(jsii_name="expires")
    def expires(self) -> typing.Optional[jsii.Number]:
        """``AWS::AppSync::ApiKey.Expires``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-apikey.html#cfn-appsync-apikey-expires
        """
        return jsii.get(self, "expires")

    @expires.setter
    def expires(self, value: typing.Optional[jsii.Number]):
        return jsii.set(self, "expires", value)


@jsii.data_type(jsii_type="@aws-cdk/aws-appsync.CfnApiKeyProps", jsii_struct_bases=[], name_mapping={'api_id': 'apiId', 'description': 'description', 'expires': 'expires'})
class CfnApiKeyProps():
    def __init__(self, *, api_id: str, description: typing.Optional[str]=None, expires: typing.Optional[jsii.Number]=None):
        """Properties for defining a ``AWS::AppSync::ApiKey``.

        :param api_id: ``AWS::AppSync::ApiKey.ApiId``.
        :param description: ``AWS::AppSync::ApiKey.Description``.
        :param expires: ``AWS::AppSync::ApiKey.Expires``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-apikey.html
        """
        self._values = {
            'api_id': api_id,
        }
        if description is not None: self._values["description"] = description
        if expires is not None: self._values["expires"] = expires

    @property
    def api_id(self) -> str:
        """``AWS::AppSync::ApiKey.ApiId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-apikey.html#cfn-appsync-apikey-apiid
        """
        return self._values.get('api_id')

    @property
    def description(self) -> typing.Optional[str]:
        """``AWS::AppSync::ApiKey.Description``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-apikey.html#cfn-appsync-apikey-description
        """
        return self._values.get('description')

    @property
    def expires(self) -> typing.Optional[jsii.Number]:
        """``AWS::AppSync::ApiKey.Expires``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-apikey.html#cfn-appsync-apikey-expires
        """
        return self._values.get('expires')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnApiKeyProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnDataSource(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-appsync.CfnDataSource"):
    """A CloudFormation ``AWS::AppSync::DataSource``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-datasource.html
    cloudformationResource:
    :cloudformationResource:: AWS::AppSync::DataSource
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, api_id: str, name: str, type: str, description: typing.Optional[str]=None, dynamo_db_config: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["DynamoDBConfigProperty"]]]=None, elasticsearch_config: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["ElasticsearchConfigProperty"]]]=None, http_config: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["HttpConfigProperty"]]]=None, lambda_config: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["LambdaConfigProperty"]]]=None, relational_database_config: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["RelationalDatabaseConfigProperty"]]]=None, service_role_arn: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::AppSync::DataSource``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param api_id: ``AWS::AppSync::DataSource.ApiId``.
        :param name: ``AWS::AppSync::DataSource.Name``.
        :param type: ``AWS::AppSync::DataSource.Type``.
        :param description: ``AWS::AppSync::DataSource.Description``.
        :param dynamo_db_config: ``AWS::AppSync::DataSource.DynamoDBConfig``.
        :param elasticsearch_config: ``AWS::AppSync::DataSource.ElasticsearchConfig``.
        :param http_config: ``AWS::AppSync::DataSource.HttpConfig``.
        :param lambda_config: ``AWS::AppSync::DataSource.LambdaConfig``.
        :param relational_database_config: ``AWS::AppSync::DataSource.RelationalDatabaseConfig``.
        :param service_role_arn: ``AWS::AppSync::DataSource.ServiceRoleArn``.
        """
        props = CfnDataSourceProps(api_id=api_id, name=name, type=type, description=description, dynamo_db_config=dynamo_db_config, elasticsearch_config=elasticsearch_config, http_config=http_config, lambda_config=lambda_config, relational_database_config=relational_database_config, service_role_arn=service_role_arn)

        jsii.create(CfnDataSource, self, [scope, id, props])

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
    @jsii.member(jsii_name="attrDataSourceArn")
    def attr_data_source_arn(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: DataSourceArn
        """
        return jsii.get(self, "attrDataSourceArn")

    @property
    @jsii.member(jsii_name="attrName")
    def attr_name(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: Name
        """
        return jsii.get(self, "attrName")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="apiId")
    def api_id(self) -> str:
        """``AWS::AppSync::DataSource.ApiId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-datasource.html#cfn-appsync-datasource-apiid
        """
        return jsii.get(self, "apiId")

    @api_id.setter
    def api_id(self, value: str):
        return jsii.set(self, "apiId", value)

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> str:
        """``AWS::AppSync::DataSource.Name``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-datasource.html#cfn-appsync-datasource-name
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: str):
        return jsii.set(self, "name", value)

    @property
    @jsii.member(jsii_name="type")
    def type(self) -> str:
        """``AWS::AppSync::DataSource.Type``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-datasource.html#cfn-appsync-datasource-type
        """
        return jsii.get(self, "type")

    @type.setter
    def type(self, value: str):
        return jsii.set(self, "type", value)

    @property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[str]:
        """``AWS::AppSync::DataSource.Description``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-datasource.html#cfn-appsync-datasource-description
        """
        return jsii.get(self, "description")

    @description.setter
    def description(self, value: typing.Optional[str]):
        return jsii.set(self, "description", value)

    @property
    @jsii.member(jsii_name="dynamoDbConfig")
    def dynamo_db_config(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["DynamoDBConfigProperty"]]]:
        """``AWS::AppSync::DataSource.DynamoDBConfig``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-datasource.html#cfn-appsync-datasource-dynamodbconfig
        """
        return jsii.get(self, "dynamoDbConfig")

    @dynamo_db_config.setter
    def dynamo_db_config(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["DynamoDBConfigProperty"]]]):
        return jsii.set(self, "dynamoDbConfig", value)

    @property
    @jsii.member(jsii_name="elasticsearchConfig")
    def elasticsearch_config(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["ElasticsearchConfigProperty"]]]:
        """``AWS::AppSync::DataSource.ElasticsearchConfig``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-datasource.html#cfn-appsync-datasource-elasticsearchconfig
        """
        return jsii.get(self, "elasticsearchConfig")

    @elasticsearch_config.setter
    def elasticsearch_config(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["ElasticsearchConfigProperty"]]]):
        return jsii.set(self, "elasticsearchConfig", value)

    @property
    @jsii.member(jsii_name="httpConfig")
    def http_config(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["HttpConfigProperty"]]]:
        """``AWS::AppSync::DataSource.HttpConfig``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-datasource.html#cfn-appsync-datasource-httpconfig
        """
        return jsii.get(self, "httpConfig")

    @http_config.setter
    def http_config(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["HttpConfigProperty"]]]):
        return jsii.set(self, "httpConfig", value)

    @property
    @jsii.member(jsii_name="lambdaConfig")
    def lambda_config(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["LambdaConfigProperty"]]]:
        """``AWS::AppSync::DataSource.LambdaConfig``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-datasource.html#cfn-appsync-datasource-lambdaconfig
        """
        return jsii.get(self, "lambdaConfig")

    @lambda_config.setter
    def lambda_config(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["LambdaConfigProperty"]]]):
        return jsii.set(self, "lambdaConfig", value)

    @property
    @jsii.member(jsii_name="relationalDatabaseConfig")
    def relational_database_config(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["RelationalDatabaseConfigProperty"]]]:
        """``AWS::AppSync::DataSource.RelationalDatabaseConfig``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-datasource.html#cfn-appsync-datasource-relationaldatabaseconfig
        """
        return jsii.get(self, "relationalDatabaseConfig")

    @relational_database_config.setter
    def relational_database_config(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["RelationalDatabaseConfigProperty"]]]):
        return jsii.set(self, "relationalDatabaseConfig", value)

    @property
    @jsii.member(jsii_name="serviceRoleArn")
    def service_role_arn(self) -> typing.Optional[str]:
        """``AWS::AppSync::DataSource.ServiceRoleArn``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-datasource.html#cfn-appsync-datasource-servicerolearn
        """
        return jsii.get(self, "serviceRoleArn")

    @service_role_arn.setter
    def service_role_arn(self, value: typing.Optional[str]):
        return jsii.set(self, "serviceRoleArn", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-appsync.CfnDataSource.AuthorizationConfigProperty", jsii_struct_bases=[], name_mapping={'authorization_type': 'authorizationType', 'aws_iam_config': 'awsIamConfig'})
    class AuthorizationConfigProperty():
        def __init__(self, *, authorization_type: str, aws_iam_config: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnDataSource.AwsIamConfigProperty"]]]=None):
            """
            :param authorization_type: ``CfnDataSource.AuthorizationConfigProperty.AuthorizationType``.
            :param aws_iam_config: ``CfnDataSource.AuthorizationConfigProperty.AwsIamConfig``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-datasource-authorizationconfig.html
            """
            self._values = {
                'authorization_type': authorization_type,
            }
            if aws_iam_config is not None: self._values["aws_iam_config"] = aws_iam_config

        @property
        def authorization_type(self) -> str:
            """``CfnDataSource.AuthorizationConfigProperty.AuthorizationType``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-datasource-authorizationconfig.html#cfn-appsync-datasource-authorizationconfig-authorizationtype
            """
            return self._values.get('authorization_type')

        @property
        def aws_iam_config(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnDataSource.AwsIamConfigProperty"]]]:
            """``CfnDataSource.AuthorizationConfigProperty.AwsIamConfig``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-datasource-authorizationconfig.html#cfn-appsync-datasource-authorizationconfig-awsiamconfig
            """
            return self._values.get('aws_iam_config')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'AuthorizationConfigProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-appsync.CfnDataSource.AwsIamConfigProperty", jsii_struct_bases=[], name_mapping={'signing_region': 'signingRegion', 'signing_service_name': 'signingServiceName'})
    class AwsIamConfigProperty():
        def __init__(self, *, signing_region: typing.Optional[str]=None, signing_service_name: typing.Optional[str]=None):
            """
            :param signing_region: ``CfnDataSource.AwsIamConfigProperty.SigningRegion``.
            :param signing_service_name: ``CfnDataSource.AwsIamConfigProperty.SigningServiceName``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-datasource-awsiamconfig.html
            """
            self._values = {
            }
            if signing_region is not None: self._values["signing_region"] = signing_region
            if signing_service_name is not None: self._values["signing_service_name"] = signing_service_name

        @property
        def signing_region(self) -> typing.Optional[str]:
            """``CfnDataSource.AwsIamConfigProperty.SigningRegion``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-datasource-awsiamconfig.html#cfn-appsync-datasource-awsiamconfig-signingregion
            """
            return self._values.get('signing_region')

        @property
        def signing_service_name(self) -> typing.Optional[str]:
            """``CfnDataSource.AwsIamConfigProperty.SigningServiceName``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-datasource-awsiamconfig.html#cfn-appsync-datasource-awsiamconfig-signingservicename
            """
            return self._values.get('signing_service_name')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'AwsIamConfigProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-appsync.CfnDataSource.DynamoDBConfigProperty", jsii_struct_bases=[], name_mapping={'aws_region': 'awsRegion', 'table_name': 'tableName', 'use_caller_credentials': 'useCallerCredentials'})
    class DynamoDBConfigProperty():
        def __init__(self, *, aws_region: str, table_name: str, use_caller_credentials: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None):
            """
            :param aws_region: ``CfnDataSource.DynamoDBConfigProperty.AwsRegion``.
            :param table_name: ``CfnDataSource.DynamoDBConfigProperty.TableName``.
            :param use_caller_credentials: ``CfnDataSource.DynamoDBConfigProperty.UseCallerCredentials``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-datasource-dynamodbconfig.html
            """
            self._values = {
                'aws_region': aws_region,
                'table_name': table_name,
            }
            if use_caller_credentials is not None: self._values["use_caller_credentials"] = use_caller_credentials

        @property
        def aws_region(self) -> str:
            """``CfnDataSource.DynamoDBConfigProperty.AwsRegion``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-datasource-dynamodbconfig.html#cfn-appsync-datasource-dynamodbconfig-awsregion
            """
            return self._values.get('aws_region')

        @property
        def table_name(self) -> str:
            """``CfnDataSource.DynamoDBConfigProperty.TableName``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-datasource-dynamodbconfig.html#cfn-appsync-datasource-dynamodbconfig-tablename
            """
            return self._values.get('table_name')

        @property
        def use_caller_credentials(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
            """``CfnDataSource.DynamoDBConfigProperty.UseCallerCredentials``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-datasource-dynamodbconfig.html#cfn-appsync-datasource-dynamodbconfig-usecallercredentials
            """
            return self._values.get('use_caller_credentials')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'DynamoDBConfigProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-appsync.CfnDataSource.ElasticsearchConfigProperty", jsii_struct_bases=[], name_mapping={'aws_region': 'awsRegion', 'endpoint': 'endpoint'})
    class ElasticsearchConfigProperty():
        def __init__(self, *, aws_region: str, endpoint: str):
            """
            :param aws_region: ``CfnDataSource.ElasticsearchConfigProperty.AwsRegion``.
            :param endpoint: ``CfnDataSource.ElasticsearchConfigProperty.Endpoint``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-datasource-elasticsearchconfig.html
            """
            self._values = {
                'aws_region': aws_region,
                'endpoint': endpoint,
            }

        @property
        def aws_region(self) -> str:
            """``CfnDataSource.ElasticsearchConfigProperty.AwsRegion``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-datasource-elasticsearchconfig.html#cfn-appsync-datasource-elasticsearchconfig-awsregion
            """
            return self._values.get('aws_region')

        @property
        def endpoint(self) -> str:
            """``CfnDataSource.ElasticsearchConfigProperty.Endpoint``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-datasource-elasticsearchconfig.html#cfn-appsync-datasource-elasticsearchconfig-endpoint
            """
            return self._values.get('endpoint')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'ElasticsearchConfigProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-appsync.CfnDataSource.HttpConfigProperty", jsii_struct_bases=[], name_mapping={'endpoint': 'endpoint', 'authorization_config': 'authorizationConfig'})
    class HttpConfigProperty():
        def __init__(self, *, endpoint: str, authorization_config: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnDataSource.AuthorizationConfigProperty"]]]=None):
            """
            :param endpoint: ``CfnDataSource.HttpConfigProperty.Endpoint``.
            :param authorization_config: ``CfnDataSource.HttpConfigProperty.AuthorizationConfig``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-datasource-httpconfig.html
            """
            self._values = {
                'endpoint': endpoint,
            }
            if authorization_config is not None: self._values["authorization_config"] = authorization_config

        @property
        def endpoint(self) -> str:
            """``CfnDataSource.HttpConfigProperty.Endpoint``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-datasource-httpconfig.html#cfn-appsync-datasource-httpconfig-endpoint
            """
            return self._values.get('endpoint')

        @property
        def authorization_config(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnDataSource.AuthorizationConfigProperty"]]]:
            """``CfnDataSource.HttpConfigProperty.AuthorizationConfig``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-datasource-httpconfig.html#cfn-appsync-datasource-httpconfig-authorizationconfig
            """
            return self._values.get('authorization_config')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'HttpConfigProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-appsync.CfnDataSource.LambdaConfigProperty", jsii_struct_bases=[], name_mapping={'lambda_function_arn': 'lambdaFunctionArn'})
    class LambdaConfigProperty():
        def __init__(self, *, lambda_function_arn: str):
            """
            :param lambda_function_arn: ``CfnDataSource.LambdaConfigProperty.LambdaFunctionArn``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-datasource-lambdaconfig.html
            """
            self._values = {
                'lambda_function_arn': lambda_function_arn,
            }

        @property
        def lambda_function_arn(self) -> str:
            """``CfnDataSource.LambdaConfigProperty.LambdaFunctionArn``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-datasource-lambdaconfig.html#cfn-appsync-datasource-lambdaconfig-lambdafunctionarn
            """
            return self._values.get('lambda_function_arn')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'LambdaConfigProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-appsync.CfnDataSource.RdsHttpEndpointConfigProperty", jsii_struct_bases=[], name_mapping={'aws_region': 'awsRegion', 'aws_secret_store_arn': 'awsSecretStoreArn', 'db_cluster_identifier': 'dbClusterIdentifier', 'database_name': 'databaseName', 'schema': 'schema'})
    class RdsHttpEndpointConfigProperty():
        def __init__(self, *, aws_region: str, aws_secret_store_arn: str, db_cluster_identifier: str, database_name: typing.Optional[str]=None, schema: typing.Optional[str]=None):
            """
            :param aws_region: ``CfnDataSource.RdsHttpEndpointConfigProperty.AwsRegion``.
            :param aws_secret_store_arn: ``CfnDataSource.RdsHttpEndpointConfigProperty.AwsSecretStoreArn``.
            :param db_cluster_identifier: ``CfnDataSource.RdsHttpEndpointConfigProperty.DbClusterIdentifier``.
            :param database_name: ``CfnDataSource.RdsHttpEndpointConfigProperty.DatabaseName``.
            :param schema: ``CfnDataSource.RdsHttpEndpointConfigProperty.Schema``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-datasource-rdshttpendpointconfig.html
            """
            self._values = {
                'aws_region': aws_region,
                'aws_secret_store_arn': aws_secret_store_arn,
                'db_cluster_identifier': db_cluster_identifier,
            }
            if database_name is not None: self._values["database_name"] = database_name
            if schema is not None: self._values["schema"] = schema

        @property
        def aws_region(self) -> str:
            """``CfnDataSource.RdsHttpEndpointConfigProperty.AwsRegion``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-datasource-rdshttpendpointconfig.html#cfn-appsync-datasource-rdshttpendpointconfig-awsregion
            """
            return self._values.get('aws_region')

        @property
        def aws_secret_store_arn(self) -> str:
            """``CfnDataSource.RdsHttpEndpointConfigProperty.AwsSecretStoreArn``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-datasource-rdshttpendpointconfig.html#cfn-appsync-datasource-rdshttpendpointconfig-awssecretstorearn
            """
            return self._values.get('aws_secret_store_arn')

        @property
        def db_cluster_identifier(self) -> str:
            """``CfnDataSource.RdsHttpEndpointConfigProperty.DbClusterIdentifier``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-datasource-rdshttpendpointconfig.html#cfn-appsync-datasource-rdshttpendpointconfig-dbclusteridentifier
            """
            return self._values.get('db_cluster_identifier')

        @property
        def database_name(self) -> typing.Optional[str]:
            """``CfnDataSource.RdsHttpEndpointConfigProperty.DatabaseName``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-datasource-rdshttpendpointconfig.html#cfn-appsync-datasource-rdshttpendpointconfig-databasename
            """
            return self._values.get('database_name')

        @property
        def schema(self) -> typing.Optional[str]:
            """``CfnDataSource.RdsHttpEndpointConfigProperty.Schema``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-datasource-rdshttpendpointconfig.html#cfn-appsync-datasource-rdshttpendpointconfig-schema
            """
            return self._values.get('schema')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'RdsHttpEndpointConfigProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-appsync.CfnDataSource.RelationalDatabaseConfigProperty", jsii_struct_bases=[], name_mapping={'relational_database_source_type': 'relationalDatabaseSourceType', 'rds_http_endpoint_config': 'rdsHttpEndpointConfig'})
    class RelationalDatabaseConfigProperty():
        def __init__(self, *, relational_database_source_type: str, rds_http_endpoint_config: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnDataSource.RdsHttpEndpointConfigProperty"]]]=None):
            """
            :param relational_database_source_type: ``CfnDataSource.RelationalDatabaseConfigProperty.RelationalDatabaseSourceType``.
            :param rds_http_endpoint_config: ``CfnDataSource.RelationalDatabaseConfigProperty.RdsHttpEndpointConfig``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-datasource-relationaldatabaseconfig.html
            """
            self._values = {
                'relational_database_source_type': relational_database_source_type,
            }
            if rds_http_endpoint_config is not None: self._values["rds_http_endpoint_config"] = rds_http_endpoint_config

        @property
        def relational_database_source_type(self) -> str:
            """``CfnDataSource.RelationalDatabaseConfigProperty.RelationalDatabaseSourceType``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-datasource-relationaldatabaseconfig.html#cfn-appsync-datasource-relationaldatabaseconfig-relationaldatabasesourcetype
            """
            return self._values.get('relational_database_source_type')

        @property
        def rds_http_endpoint_config(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnDataSource.RdsHttpEndpointConfigProperty"]]]:
            """``CfnDataSource.RelationalDatabaseConfigProperty.RdsHttpEndpointConfig``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-datasource-relationaldatabaseconfig.html#cfn-appsync-datasource-relationaldatabaseconfig-rdshttpendpointconfig
            """
            return self._values.get('rds_http_endpoint_config')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'RelationalDatabaseConfigProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



@jsii.data_type(jsii_type="@aws-cdk/aws-appsync.CfnDataSourceProps", jsii_struct_bases=[], name_mapping={'api_id': 'apiId', 'name': 'name', 'type': 'type', 'description': 'description', 'dynamo_db_config': 'dynamoDbConfig', 'elasticsearch_config': 'elasticsearchConfig', 'http_config': 'httpConfig', 'lambda_config': 'lambdaConfig', 'relational_database_config': 'relationalDatabaseConfig', 'service_role_arn': 'serviceRoleArn'})
class CfnDataSourceProps():
    def __init__(self, *, api_id: str, name: str, type: str, description: typing.Optional[str]=None, dynamo_db_config: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnDataSource.DynamoDBConfigProperty"]]]=None, elasticsearch_config: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnDataSource.ElasticsearchConfigProperty"]]]=None, http_config: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnDataSource.HttpConfigProperty"]]]=None, lambda_config: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnDataSource.LambdaConfigProperty"]]]=None, relational_database_config: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnDataSource.RelationalDatabaseConfigProperty"]]]=None, service_role_arn: typing.Optional[str]=None):
        """Properties for defining a ``AWS::AppSync::DataSource``.

        :param api_id: ``AWS::AppSync::DataSource.ApiId``.
        :param name: ``AWS::AppSync::DataSource.Name``.
        :param type: ``AWS::AppSync::DataSource.Type``.
        :param description: ``AWS::AppSync::DataSource.Description``.
        :param dynamo_db_config: ``AWS::AppSync::DataSource.DynamoDBConfig``.
        :param elasticsearch_config: ``AWS::AppSync::DataSource.ElasticsearchConfig``.
        :param http_config: ``AWS::AppSync::DataSource.HttpConfig``.
        :param lambda_config: ``AWS::AppSync::DataSource.LambdaConfig``.
        :param relational_database_config: ``AWS::AppSync::DataSource.RelationalDatabaseConfig``.
        :param service_role_arn: ``AWS::AppSync::DataSource.ServiceRoleArn``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-datasource.html
        """
        self._values = {
            'api_id': api_id,
            'name': name,
            'type': type,
        }
        if description is not None: self._values["description"] = description
        if dynamo_db_config is not None: self._values["dynamo_db_config"] = dynamo_db_config
        if elasticsearch_config is not None: self._values["elasticsearch_config"] = elasticsearch_config
        if http_config is not None: self._values["http_config"] = http_config
        if lambda_config is not None: self._values["lambda_config"] = lambda_config
        if relational_database_config is not None: self._values["relational_database_config"] = relational_database_config
        if service_role_arn is not None: self._values["service_role_arn"] = service_role_arn

    @property
    def api_id(self) -> str:
        """``AWS::AppSync::DataSource.ApiId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-datasource.html#cfn-appsync-datasource-apiid
        """
        return self._values.get('api_id')

    @property
    def name(self) -> str:
        """``AWS::AppSync::DataSource.Name``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-datasource.html#cfn-appsync-datasource-name
        """
        return self._values.get('name')

    @property
    def type(self) -> str:
        """``AWS::AppSync::DataSource.Type``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-datasource.html#cfn-appsync-datasource-type
        """
        return self._values.get('type')

    @property
    def description(self) -> typing.Optional[str]:
        """``AWS::AppSync::DataSource.Description``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-datasource.html#cfn-appsync-datasource-description
        """
        return self._values.get('description')

    @property
    def dynamo_db_config(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnDataSource.DynamoDBConfigProperty"]]]:
        """``AWS::AppSync::DataSource.DynamoDBConfig``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-datasource.html#cfn-appsync-datasource-dynamodbconfig
        """
        return self._values.get('dynamo_db_config')

    @property
    def elasticsearch_config(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnDataSource.ElasticsearchConfigProperty"]]]:
        """``AWS::AppSync::DataSource.ElasticsearchConfig``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-datasource.html#cfn-appsync-datasource-elasticsearchconfig
        """
        return self._values.get('elasticsearch_config')

    @property
    def http_config(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnDataSource.HttpConfigProperty"]]]:
        """``AWS::AppSync::DataSource.HttpConfig``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-datasource.html#cfn-appsync-datasource-httpconfig
        """
        return self._values.get('http_config')

    @property
    def lambda_config(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnDataSource.LambdaConfigProperty"]]]:
        """``AWS::AppSync::DataSource.LambdaConfig``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-datasource.html#cfn-appsync-datasource-lambdaconfig
        """
        return self._values.get('lambda_config')

    @property
    def relational_database_config(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnDataSource.RelationalDatabaseConfigProperty"]]]:
        """``AWS::AppSync::DataSource.RelationalDatabaseConfig``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-datasource.html#cfn-appsync-datasource-relationaldatabaseconfig
        """
        return self._values.get('relational_database_config')

    @property
    def service_role_arn(self) -> typing.Optional[str]:
        """``AWS::AppSync::DataSource.ServiceRoleArn``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-datasource.html#cfn-appsync-datasource-servicerolearn
        """
        return self._values.get('service_role_arn')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnDataSourceProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnFunctionConfiguration(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-appsync.CfnFunctionConfiguration"):
    """A CloudFormation ``AWS::AppSync::FunctionConfiguration``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-functionconfiguration.html
    cloudformationResource:
    :cloudformationResource:: AWS::AppSync::FunctionConfiguration
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, api_id: str, data_source_name: str, function_version: str, name: str, description: typing.Optional[str]=None, request_mapping_template: typing.Optional[str]=None, request_mapping_template_s3_location: typing.Optional[str]=None, response_mapping_template: typing.Optional[str]=None, response_mapping_template_s3_location: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::AppSync::FunctionConfiguration``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param api_id: ``AWS::AppSync::FunctionConfiguration.ApiId``.
        :param data_source_name: ``AWS::AppSync::FunctionConfiguration.DataSourceName``.
        :param function_version: ``AWS::AppSync::FunctionConfiguration.FunctionVersion``.
        :param name: ``AWS::AppSync::FunctionConfiguration.Name``.
        :param description: ``AWS::AppSync::FunctionConfiguration.Description``.
        :param request_mapping_template: ``AWS::AppSync::FunctionConfiguration.RequestMappingTemplate``.
        :param request_mapping_template_s3_location: ``AWS::AppSync::FunctionConfiguration.RequestMappingTemplateS3Location``.
        :param response_mapping_template: ``AWS::AppSync::FunctionConfiguration.ResponseMappingTemplate``.
        :param response_mapping_template_s3_location: ``AWS::AppSync::FunctionConfiguration.ResponseMappingTemplateS3Location``.
        """
        props = CfnFunctionConfigurationProps(api_id=api_id, data_source_name=data_source_name, function_version=function_version, name=name, description=description, request_mapping_template=request_mapping_template, request_mapping_template_s3_location=request_mapping_template_s3_location, response_mapping_template=response_mapping_template, response_mapping_template_s3_location=response_mapping_template_s3_location)

        jsii.create(CfnFunctionConfiguration, self, [scope, id, props])

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
    @jsii.member(jsii_name="attrDataSourceName")
    def attr_data_source_name(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: DataSourceName
        """
        return jsii.get(self, "attrDataSourceName")

    @property
    @jsii.member(jsii_name="attrFunctionArn")
    def attr_function_arn(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: FunctionArn
        """
        return jsii.get(self, "attrFunctionArn")

    @property
    @jsii.member(jsii_name="attrFunctionId")
    def attr_function_id(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: FunctionId
        """
        return jsii.get(self, "attrFunctionId")

    @property
    @jsii.member(jsii_name="attrName")
    def attr_name(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: Name
        """
        return jsii.get(self, "attrName")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="apiId")
    def api_id(self) -> str:
        """``AWS::AppSync::FunctionConfiguration.ApiId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-functionconfiguration.html#cfn-appsync-functionconfiguration-apiid
        """
        return jsii.get(self, "apiId")

    @api_id.setter
    def api_id(self, value: str):
        return jsii.set(self, "apiId", value)

    @property
    @jsii.member(jsii_name="dataSourceName")
    def data_source_name(self) -> str:
        """``AWS::AppSync::FunctionConfiguration.DataSourceName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-functionconfiguration.html#cfn-appsync-functionconfiguration-datasourcename
        """
        return jsii.get(self, "dataSourceName")

    @data_source_name.setter
    def data_source_name(self, value: str):
        return jsii.set(self, "dataSourceName", value)

    @property
    @jsii.member(jsii_name="functionVersion")
    def function_version(self) -> str:
        """``AWS::AppSync::FunctionConfiguration.FunctionVersion``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-functionconfiguration.html#cfn-appsync-functionconfiguration-functionversion
        """
        return jsii.get(self, "functionVersion")

    @function_version.setter
    def function_version(self, value: str):
        return jsii.set(self, "functionVersion", value)

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> str:
        """``AWS::AppSync::FunctionConfiguration.Name``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-functionconfiguration.html#cfn-appsync-functionconfiguration-name
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: str):
        return jsii.set(self, "name", value)

    @property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[str]:
        """``AWS::AppSync::FunctionConfiguration.Description``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-functionconfiguration.html#cfn-appsync-functionconfiguration-description
        """
        return jsii.get(self, "description")

    @description.setter
    def description(self, value: typing.Optional[str]):
        return jsii.set(self, "description", value)

    @property
    @jsii.member(jsii_name="requestMappingTemplate")
    def request_mapping_template(self) -> typing.Optional[str]:
        """``AWS::AppSync::FunctionConfiguration.RequestMappingTemplate``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-functionconfiguration.html#cfn-appsync-functionconfiguration-requestmappingtemplate
        """
        return jsii.get(self, "requestMappingTemplate")

    @request_mapping_template.setter
    def request_mapping_template(self, value: typing.Optional[str]):
        return jsii.set(self, "requestMappingTemplate", value)

    @property
    @jsii.member(jsii_name="requestMappingTemplateS3Location")
    def request_mapping_template_s3_location(self) -> typing.Optional[str]:
        """``AWS::AppSync::FunctionConfiguration.RequestMappingTemplateS3Location``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-functionconfiguration.html#cfn-appsync-functionconfiguration-requestmappingtemplates3location
        """
        return jsii.get(self, "requestMappingTemplateS3Location")

    @request_mapping_template_s3_location.setter
    def request_mapping_template_s3_location(self, value: typing.Optional[str]):
        return jsii.set(self, "requestMappingTemplateS3Location", value)

    @property
    @jsii.member(jsii_name="responseMappingTemplate")
    def response_mapping_template(self) -> typing.Optional[str]:
        """``AWS::AppSync::FunctionConfiguration.ResponseMappingTemplate``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-functionconfiguration.html#cfn-appsync-functionconfiguration-responsemappingtemplate
        """
        return jsii.get(self, "responseMappingTemplate")

    @response_mapping_template.setter
    def response_mapping_template(self, value: typing.Optional[str]):
        return jsii.set(self, "responseMappingTemplate", value)

    @property
    @jsii.member(jsii_name="responseMappingTemplateS3Location")
    def response_mapping_template_s3_location(self) -> typing.Optional[str]:
        """``AWS::AppSync::FunctionConfiguration.ResponseMappingTemplateS3Location``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-functionconfiguration.html#cfn-appsync-functionconfiguration-responsemappingtemplates3location
        """
        return jsii.get(self, "responseMappingTemplateS3Location")

    @response_mapping_template_s3_location.setter
    def response_mapping_template_s3_location(self, value: typing.Optional[str]):
        return jsii.set(self, "responseMappingTemplateS3Location", value)


@jsii.data_type(jsii_type="@aws-cdk/aws-appsync.CfnFunctionConfigurationProps", jsii_struct_bases=[], name_mapping={'api_id': 'apiId', 'data_source_name': 'dataSourceName', 'function_version': 'functionVersion', 'name': 'name', 'description': 'description', 'request_mapping_template': 'requestMappingTemplate', 'request_mapping_template_s3_location': 'requestMappingTemplateS3Location', 'response_mapping_template': 'responseMappingTemplate', 'response_mapping_template_s3_location': 'responseMappingTemplateS3Location'})
class CfnFunctionConfigurationProps():
    def __init__(self, *, api_id: str, data_source_name: str, function_version: str, name: str, description: typing.Optional[str]=None, request_mapping_template: typing.Optional[str]=None, request_mapping_template_s3_location: typing.Optional[str]=None, response_mapping_template: typing.Optional[str]=None, response_mapping_template_s3_location: typing.Optional[str]=None):
        """Properties for defining a ``AWS::AppSync::FunctionConfiguration``.

        :param api_id: ``AWS::AppSync::FunctionConfiguration.ApiId``.
        :param data_source_name: ``AWS::AppSync::FunctionConfiguration.DataSourceName``.
        :param function_version: ``AWS::AppSync::FunctionConfiguration.FunctionVersion``.
        :param name: ``AWS::AppSync::FunctionConfiguration.Name``.
        :param description: ``AWS::AppSync::FunctionConfiguration.Description``.
        :param request_mapping_template: ``AWS::AppSync::FunctionConfiguration.RequestMappingTemplate``.
        :param request_mapping_template_s3_location: ``AWS::AppSync::FunctionConfiguration.RequestMappingTemplateS3Location``.
        :param response_mapping_template: ``AWS::AppSync::FunctionConfiguration.ResponseMappingTemplate``.
        :param response_mapping_template_s3_location: ``AWS::AppSync::FunctionConfiguration.ResponseMappingTemplateS3Location``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-functionconfiguration.html
        """
        self._values = {
            'api_id': api_id,
            'data_source_name': data_source_name,
            'function_version': function_version,
            'name': name,
        }
        if description is not None: self._values["description"] = description
        if request_mapping_template is not None: self._values["request_mapping_template"] = request_mapping_template
        if request_mapping_template_s3_location is not None: self._values["request_mapping_template_s3_location"] = request_mapping_template_s3_location
        if response_mapping_template is not None: self._values["response_mapping_template"] = response_mapping_template
        if response_mapping_template_s3_location is not None: self._values["response_mapping_template_s3_location"] = response_mapping_template_s3_location

    @property
    def api_id(self) -> str:
        """``AWS::AppSync::FunctionConfiguration.ApiId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-functionconfiguration.html#cfn-appsync-functionconfiguration-apiid
        """
        return self._values.get('api_id')

    @property
    def data_source_name(self) -> str:
        """``AWS::AppSync::FunctionConfiguration.DataSourceName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-functionconfiguration.html#cfn-appsync-functionconfiguration-datasourcename
        """
        return self._values.get('data_source_name')

    @property
    def function_version(self) -> str:
        """``AWS::AppSync::FunctionConfiguration.FunctionVersion``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-functionconfiguration.html#cfn-appsync-functionconfiguration-functionversion
        """
        return self._values.get('function_version')

    @property
    def name(self) -> str:
        """``AWS::AppSync::FunctionConfiguration.Name``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-functionconfiguration.html#cfn-appsync-functionconfiguration-name
        """
        return self._values.get('name')

    @property
    def description(self) -> typing.Optional[str]:
        """``AWS::AppSync::FunctionConfiguration.Description``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-functionconfiguration.html#cfn-appsync-functionconfiguration-description
        """
        return self._values.get('description')

    @property
    def request_mapping_template(self) -> typing.Optional[str]:
        """``AWS::AppSync::FunctionConfiguration.RequestMappingTemplate``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-functionconfiguration.html#cfn-appsync-functionconfiguration-requestmappingtemplate
        """
        return self._values.get('request_mapping_template')

    @property
    def request_mapping_template_s3_location(self) -> typing.Optional[str]:
        """``AWS::AppSync::FunctionConfiguration.RequestMappingTemplateS3Location``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-functionconfiguration.html#cfn-appsync-functionconfiguration-requestmappingtemplates3location
        """
        return self._values.get('request_mapping_template_s3_location')

    @property
    def response_mapping_template(self) -> typing.Optional[str]:
        """``AWS::AppSync::FunctionConfiguration.ResponseMappingTemplate``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-functionconfiguration.html#cfn-appsync-functionconfiguration-responsemappingtemplate
        """
        return self._values.get('response_mapping_template')

    @property
    def response_mapping_template_s3_location(self) -> typing.Optional[str]:
        """``AWS::AppSync::FunctionConfiguration.ResponseMappingTemplateS3Location``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-functionconfiguration.html#cfn-appsync-functionconfiguration-responsemappingtemplates3location
        """
        return self._values.get('response_mapping_template_s3_location')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnFunctionConfigurationProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnGraphQLApi(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-appsync.CfnGraphQLApi"):
    """A CloudFormation ``AWS::AppSync::GraphQLApi``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-graphqlapi.html
    cloudformationResource:
    :cloudformationResource:: AWS::AppSync::GraphQLApi
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, authentication_type: str, name: str, additional_authentication_providers: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union["AdditionalAuthenticationProviderProperty", aws_cdk.core.IResolvable]]]]]=None, log_config: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["LogConfigProperty"]]]=None, open_id_connect_config: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["OpenIDConnectConfigProperty"]]]=None, tags: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, aws_cdk.core.CfnTag]]]]]=None, user_pool_config: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["UserPoolConfigProperty"]]]=None) -> None:
        """Create a new ``AWS::AppSync::GraphQLApi``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param authentication_type: ``AWS::AppSync::GraphQLApi.AuthenticationType``.
        :param name: ``AWS::AppSync::GraphQLApi.Name``.
        :param additional_authentication_providers: ``AWS::AppSync::GraphQLApi.AdditionalAuthenticationProviders``.
        :param log_config: ``AWS::AppSync::GraphQLApi.LogConfig``.
        :param open_id_connect_config: ``AWS::AppSync::GraphQLApi.OpenIDConnectConfig``.
        :param tags: ``AWS::AppSync::GraphQLApi.Tags``.
        :param user_pool_config: ``AWS::AppSync::GraphQLApi.UserPoolConfig``.
        """
        props = CfnGraphQLApiProps(authentication_type=authentication_type, name=name, additional_authentication_providers=additional_authentication_providers, log_config=log_config, open_id_connect_config=open_id_connect_config, tags=tags, user_pool_config=user_pool_config)

        jsii.create(CfnGraphQLApi, self, [scope, id, props])

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
    @jsii.member(jsii_name="attrApiId")
    def attr_api_id(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: ApiId
        """
        return jsii.get(self, "attrApiId")

    @property
    @jsii.member(jsii_name="attrArn")
    def attr_arn(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: Arn
        """
        return jsii.get(self, "attrArn")

    @property
    @jsii.member(jsii_name="attrGraphQlUrl")
    def attr_graph_ql_url(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: GraphQLUrl
        """
        return jsii.get(self, "attrGraphQlUrl")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        """``AWS::AppSync::GraphQLApi.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-graphqlapi.html#cfn-appsync-graphqlapi-tags
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="authenticationType")
    def authentication_type(self) -> str:
        """``AWS::AppSync::GraphQLApi.AuthenticationType``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-graphqlapi.html#cfn-appsync-graphqlapi-authenticationtype
        """
        return jsii.get(self, "authenticationType")

    @authentication_type.setter
    def authentication_type(self, value: str):
        return jsii.set(self, "authenticationType", value)

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> str:
        """``AWS::AppSync::GraphQLApi.Name``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-graphqlapi.html#cfn-appsync-graphqlapi-name
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: str):
        return jsii.set(self, "name", value)

    @property
    @jsii.member(jsii_name="additionalAuthenticationProviders")
    def additional_authentication_providers(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union["AdditionalAuthenticationProviderProperty", aws_cdk.core.IResolvable]]]]]:
        """``AWS::AppSync::GraphQLApi.AdditionalAuthenticationProviders``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-graphqlapi.html#cfn-appsync-graphqlapi-additionalauthenticationproviders
        """
        return jsii.get(self, "additionalAuthenticationProviders")

    @additional_authentication_providers.setter
    def additional_authentication_providers(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union["AdditionalAuthenticationProviderProperty", aws_cdk.core.IResolvable]]]]]):
        return jsii.set(self, "additionalAuthenticationProviders", value)

    @property
    @jsii.member(jsii_name="logConfig")
    def log_config(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["LogConfigProperty"]]]:
        """``AWS::AppSync::GraphQLApi.LogConfig``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-graphqlapi.html#cfn-appsync-graphqlapi-logconfig
        """
        return jsii.get(self, "logConfig")

    @log_config.setter
    def log_config(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["LogConfigProperty"]]]):
        return jsii.set(self, "logConfig", value)

    @property
    @jsii.member(jsii_name="openIdConnectConfig")
    def open_id_connect_config(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["OpenIDConnectConfigProperty"]]]:
        """``AWS::AppSync::GraphQLApi.OpenIDConnectConfig``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-graphqlapi.html#cfn-appsync-graphqlapi-openidconnectconfig
        """
        return jsii.get(self, "openIdConnectConfig")

    @open_id_connect_config.setter
    def open_id_connect_config(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["OpenIDConnectConfigProperty"]]]):
        return jsii.set(self, "openIdConnectConfig", value)

    @property
    @jsii.member(jsii_name="userPoolConfig")
    def user_pool_config(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["UserPoolConfigProperty"]]]:
        """``AWS::AppSync::GraphQLApi.UserPoolConfig``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-graphqlapi.html#cfn-appsync-graphqlapi-userpoolconfig
        """
        return jsii.get(self, "userPoolConfig")

    @user_pool_config.setter
    def user_pool_config(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["UserPoolConfigProperty"]]]):
        return jsii.set(self, "userPoolConfig", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-appsync.CfnGraphQLApi.AdditionalAuthenticationProviderProperty", jsii_struct_bases=[], name_mapping={'authentication_type': 'authenticationType', 'open_id_connect_config': 'openIdConnectConfig', 'user_pool_config': 'userPoolConfig'})
    class AdditionalAuthenticationProviderProperty():
        def __init__(self, *, authentication_type: str, open_id_connect_config: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnGraphQLApi.OpenIDConnectConfigProperty"]]]=None, user_pool_config: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnGraphQLApi.CognitoUserPoolConfigProperty"]]]=None):
            """
            :param authentication_type: ``CfnGraphQLApi.AdditionalAuthenticationProviderProperty.AuthenticationType``.
            :param open_id_connect_config: ``CfnGraphQLApi.AdditionalAuthenticationProviderProperty.OpenIDConnectConfig``.
            :param user_pool_config: ``CfnGraphQLApi.AdditionalAuthenticationProviderProperty.UserPoolConfig``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-graphqlapi-additionalauthenticationprovider.html
            """
            self._values = {
                'authentication_type': authentication_type,
            }
            if open_id_connect_config is not None: self._values["open_id_connect_config"] = open_id_connect_config
            if user_pool_config is not None: self._values["user_pool_config"] = user_pool_config

        @property
        def authentication_type(self) -> str:
            """``CfnGraphQLApi.AdditionalAuthenticationProviderProperty.AuthenticationType``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-graphqlapi-additionalauthenticationprovider.html#cfn-appsync-graphqlapi-additionalauthenticationprovider-authenticationtype
            """
            return self._values.get('authentication_type')

        @property
        def open_id_connect_config(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnGraphQLApi.OpenIDConnectConfigProperty"]]]:
            """``CfnGraphQLApi.AdditionalAuthenticationProviderProperty.OpenIDConnectConfig``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-graphqlapi-additionalauthenticationprovider.html#cfn-appsync-graphqlapi-additionalauthenticationprovider-openidconnectconfig
            """
            return self._values.get('open_id_connect_config')

        @property
        def user_pool_config(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnGraphQLApi.CognitoUserPoolConfigProperty"]]]:
            """``CfnGraphQLApi.AdditionalAuthenticationProviderProperty.UserPoolConfig``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-graphqlapi-additionalauthenticationprovider.html#cfn-appsync-graphqlapi-additionalauthenticationprovider-userpoolconfig
            """
            return self._values.get('user_pool_config')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'AdditionalAuthenticationProviderProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-appsync.CfnGraphQLApi.CognitoUserPoolConfigProperty", jsii_struct_bases=[], name_mapping={'app_id_client_regex': 'appIdClientRegex', 'aws_region': 'awsRegion', 'user_pool_id': 'userPoolId'})
    class CognitoUserPoolConfigProperty():
        def __init__(self, *, app_id_client_regex: typing.Optional[str]=None, aws_region: typing.Optional[str]=None, user_pool_id: typing.Optional[str]=None):
            """
            :param app_id_client_regex: ``CfnGraphQLApi.CognitoUserPoolConfigProperty.AppIdClientRegex``.
            :param aws_region: ``CfnGraphQLApi.CognitoUserPoolConfigProperty.AwsRegion``.
            :param user_pool_id: ``CfnGraphQLApi.CognitoUserPoolConfigProperty.UserPoolId``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-graphqlapi-cognitouserpoolconfig.html
            """
            self._values = {
            }
            if app_id_client_regex is not None: self._values["app_id_client_regex"] = app_id_client_regex
            if aws_region is not None: self._values["aws_region"] = aws_region
            if user_pool_id is not None: self._values["user_pool_id"] = user_pool_id

        @property
        def app_id_client_regex(self) -> typing.Optional[str]:
            """``CfnGraphQLApi.CognitoUserPoolConfigProperty.AppIdClientRegex``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-graphqlapi-cognitouserpoolconfig.html#cfn-appsync-graphqlapi-cognitouserpoolconfig-appidclientregex
            """
            return self._values.get('app_id_client_regex')

        @property
        def aws_region(self) -> typing.Optional[str]:
            """``CfnGraphQLApi.CognitoUserPoolConfigProperty.AwsRegion``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-graphqlapi-cognitouserpoolconfig.html#cfn-appsync-graphqlapi-cognitouserpoolconfig-awsregion
            """
            return self._values.get('aws_region')

        @property
        def user_pool_id(self) -> typing.Optional[str]:
            """``CfnGraphQLApi.CognitoUserPoolConfigProperty.UserPoolId``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-graphqlapi-cognitouserpoolconfig.html#cfn-appsync-graphqlapi-cognitouserpoolconfig-userpoolid
            """
            return self._values.get('user_pool_id')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'CognitoUserPoolConfigProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-appsync.CfnGraphQLApi.LogConfigProperty", jsii_struct_bases=[], name_mapping={'cloud_watch_logs_role_arn': 'cloudWatchLogsRoleArn', 'exclude_verbose_content': 'excludeVerboseContent', 'field_log_level': 'fieldLogLevel'})
    class LogConfigProperty():
        def __init__(self, *, cloud_watch_logs_role_arn: typing.Optional[str]=None, exclude_verbose_content: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, field_log_level: typing.Optional[str]=None):
            """
            :param cloud_watch_logs_role_arn: ``CfnGraphQLApi.LogConfigProperty.CloudWatchLogsRoleArn``.
            :param exclude_verbose_content: ``CfnGraphQLApi.LogConfigProperty.ExcludeVerboseContent``.
            :param field_log_level: ``CfnGraphQLApi.LogConfigProperty.FieldLogLevel``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-graphqlapi-logconfig.html
            """
            self._values = {
            }
            if cloud_watch_logs_role_arn is not None: self._values["cloud_watch_logs_role_arn"] = cloud_watch_logs_role_arn
            if exclude_verbose_content is not None: self._values["exclude_verbose_content"] = exclude_verbose_content
            if field_log_level is not None: self._values["field_log_level"] = field_log_level

        @property
        def cloud_watch_logs_role_arn(self) -> typing.Optional[str]:
            """``CfnGraphQLApi.LogConfigProperty.CloudWatchLogsRoleArn``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-graphqlapi-logconfig.html#cfn-appsync-graphqlapi-logconfig-cloudwatchlogsrolearn
            """
            return self._values.get('cloud_watch_logs_role_arn')

        @property
        def exclude_verbose_content(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
            """``CfnGraphQLApi.LogConfigProperty.ExcludeVerboseContent``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-graphqlapi-logconfig.html#cfn-appsync-graphqlapi-logconfig-excludeverbosecontent
            """
            return self._values.get('exclude_verbose_content')

        @property
        def field_log_level(self) -> typing.Optional[str]:
            """``CfnGraphQLApi.LogConfigProperty.FieldLogLevel``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-graphqlapi-logconfig.html#cfn-appsync-graphqlapi-logconfig-fieldloglevel
            """
            return self._values.get('field_log_level')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'LogConfigProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-appsync.CfnGraphQLApi.OpenIDConnectConfigProperty", jsii_struct_bases=[], name_mapping={'auth_ttl': 'authTtl', 'client_id': 'clientId', 'iat_ttl': 'iatTtl', 'issuer': 'issuer'})
    class OpenIDConnectConfigProperty():
        def __init__(self, *, auth_ttl: typing.Optional[jsii.Number]=None, client_id: typing.Optional[str]=None, iat_ttl: typing.Optional[jsii.Number]=None, issuer: typing.Optional[str]=None):
            """
            :param auth_ttl: ``CfnGraphQLApi.OpenIDConnectConfigProperty.AuthTTL``.
            :param client_id: ``CfnGraphQLApi.OpenIDConnectConfigProperty.ClientId``.
            :param iat_ttl: ``CfnGraphQLApi.OpenIDConnectConfigProperty.IatTTL``.
            :param issuer: ``CfnGraphQLApi.OpenIDConnectConfigProperty.Issuer``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-graphqlapi-openidconnectconfig.html
            """
            self._values = {
            }
            if auth_ttl is not None: self._values["auth_ttl"] = auth_ttl
            if client_id is not None: self._values["client_id"] = client_id
            if iat_ttl is not None: self._values["iat_ttl"] = iat_ttl
            if issuer is not None: self._values["issuer"] = issuer

        @property
        def auth_ttl(self) -> typing.Optional[jsii.Number]:
            """``CfnGraphQLApi.OpenIDConnectConfigProperty.AuthTTL``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-graphqlapi-openidconnectconfig.html#cfn-appsync-graphqlapi-openidconnectconfig-authttl
            """
            return self._values.get('auth_ttl')

        @property
        def client_id(self) -> typing.Optional[str]:
            """``CfnGraphQLApi.OpenIDConnectConfigProperty.ClientId``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-graphqlapi-openidconnectconfig.html#cfn-appsync-graphqlapi-openidconnectconfig-clientid
            """
            return self._values.get('client_id')

        @property
        def iat_ttl(self) -> typing.Optional[jsii.Number]:
            """``CfnGraphQLApi.OpenIDConnectConfigProperty.IatTTL``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-graphqlapi-openidconnectconfig.html#cfn-appsync-graphqlapi-openidconnectconfig-iatttl
            """
            return self._values.get('iat_ttl')

        @property
        def issuer(self) -> typing.Optional[str]:
            """``CfnGraphQLApi.OpenIDConnectConfigProperty.Issuer``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-graphqlapi-openidconnectconfig.html#cfn-appsync-graphqlapi-openidconnectconfig-issuer
            """
            return self._values.get('issuer')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'OpenIDConnectConfigProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-appsync.CfnGraphQLApi.UserPoolConfigProperty", jsii_struct_bases=[], name_mapping={'app_id_client_regex': 'appIdClientRegex', 'aws_region': 'awsRegion', 'default_action': 'defaultAction', 'user_pool_id': 'userPoolId'})
    class UserPoolConfigProperty():
        def __init__(self, *, app_id_client_regex: typing.Optional[str]=None, aws_region: typing.Optional[str]=None, default_action: typing.Optional[str]=None, user_pool_id: typing.Optional[str]=None):
            """
            :param app_id_client_regex: ``CfnGraphQLApi.UserPoolConfigProperty.AppIdClientRegex``.
            :param aws_region: ``CfnGraphQLApi.UserPoolConfigProperty.AwsRegion``.
            :param default_action: ``CfnGraphQLApi.UserPoolConfigProperty.DefaultAction``.
            :param user_pool_id: ``CfnGraphQLApi.UserPoolConfigProperty.UserPoolId``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-graphqlapi-userpoolconfig.html
            """
            self._values = {
            }
            if app_id_client_regex is not None: self._values["app_id_client_regex"] = app_id_client_regex
            if aws_region is not None: self._values["aws_region"] = aws_region
            if default_action is not None: self._values["default_action"] = default_action
            if user_pool_id is not None: self._values["user_pool_id"] = user_pool_id

        @property
        def app_id_client_regex(self) -> typing.Optional[str]:
            """``CfnGraphQLApi.UserPoolConfigProperty.AppIdClientRegex``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-graphqlapi-userpoolconfig.html#cfn-appsync-graphqlapi-userpoolconfig-appidclientregex
            """
            return self._values.get('app_id_client_regex')

        @property
        def aws_region(self) -> typing.Optional[str]:
            """``CfnGraphQLApi.UserPoolConfigProperty.AwsRegion``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-graphqlapi-userpoolconfig.html#cfn-appsync-graphqlapi-userpoolconfig-awsregion
            """
            return self._values.get('aws_region')

        @property
        def default_action(self) -> typing.Optional[str]:
            """``CfnGraphQLApi.UserPoolConfigProperty.DefaultAction``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-graphqlapi-userpoolconfig.html#cfn-appsync-graphqlapi-userpoolconfig-defaultaction
            """
            return self._values.get('default_action')

        @property
        def user_pool_id(self) -> typing.Optional[str]:
            """``CfnGraphQLApi.UserPoolConfigProperty.UserPoolId``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-graphqlapi-userpoolconfig.html#cfn-appsync-graphqlapi-userpoolconfig-userpoolid
            """
            return self._values.get('user_pool_id')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'UserPoolConfigProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



@jsii.data_type(jsii_type="@aws-cdk/aws-appsync.CfnGraphQLApiProps", jsii_struct_bases=[], name_mapping={'authentication_type': 'authenticationType', 'name': 'name', 'additional_authentication_providers': 'additionalAuthenticationProviders', 'log_config': 'logConfig', 'open_id_connect_config': 'openIdConnectConfig', 'tags': 'tags', 'user_pool_config': 'userPoolConfig'})
class CfnGraphQLApiProps():
    def __init__(self, *, authentication_type: str, name: str, additional_authentication_providers: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union["CfnGraphQLApi.AdditionalAuthenticationProviderProperty", aws_cdk.core.IResolvable]]]]]=None, log_config: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnGraphQLApi.LogConfigProperty"]]]=None, open_id_connect_config: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnGraphQLApi.OpenIDConnectConfigProperty"]]]=None, tags: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, aws_cdk.core.CfnTag]]]]]=None, user_pool_config: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnGraphQLApi.UserPoolConfigProperty"]]]=None):
        """Properties for defining a ``AWS::AppSync::GraphQLApi``.

        :param authentication_type: ``AWS::AppSync::GraphQLApi.AuthenticationType``.
        :param name: ``AWS::AppSync::GraphQLApi.Name``.
        :param additional_authentication_providers: ``AWS::AppSync::GraphQLApi.AdditionalAuthenticationProviders``.
        :param log_config: ``AWS::AppSync::GraphQLApi.LogConfig``.
        :param open_id_connect_config: ``AWS::AppSync::GraphQLApi.OpenIDConnectConfig``.
        :param tags: ``AWS::AppSync::GraphQLApi.Tags``.
        :param user_pool_config: ``AWS::AppSync::GraphQLApi.UserPoolConfig``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-graphqlapi.html
        """
        self._values = {
            'authentication_type': authentication_type,
            'name': name,
        }
        if additional_authentication_providers is not None: self._values["additional_authentication_providers"] = additional_authentication_providers
        if log_config is not None: self._values["log_config"] = log_config
        if open_id_connect_config is not None: self._values["open_id_connect_config"] = open_id_connect_config
        if tags is not None: self._values["tags"] = tags
        if user_pool_config is not None: self._values["user_pool_config"] = user_pool_config

    @property
    def authentication_type(self) -> str:
        """``AWS::AppSync::GraphQLApi.AuthenticationType``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-graphqlapi.html#cfn-appsync-graphqlapi-authenticationtype
        """
        return self._values.get('authentication_type')

    @property
    def name(self) -> str:
        """``AWS::AppSync::GraphQLApi.Name``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-graphqlapi.html#cfn-appsync-graphqlapi-name
        """
        return self._values.get('name')

    @property
    def additional_authentication_providers(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union["CfnGraphQLApi.AdditionalAuthenticationProviderProperty", aws_cdk.core.IResolvable]]]]]:
        """``AWS::AppSync::GraphQLApi.AdditionalAuthenticationProviders``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-graphqlapi.html#cfn-appsync-graphqlapi-additionalauthenticationproviders
        """
        return self._values.get('additional_authentication_providers')

    @property
    def log_config(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnGraphQLApi.LogConfigProperty"]]]:
        """``AWS::AppSync::GraphQLApi.LogConfig``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-graphqlapi.html#cfn-appsync-graphqlapi-logconfig
        """
        return self._values.get('log_config')

    @property
    def open_id_connect_config(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnGraphQLApi.OpenIDConnectConfigProperty"]]]:
        """``AWS::AppSync::GraphQLApi.OpenIDConnectConfig``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-graphqlapi.html#cfn-appsync-graphqlapi-openidconnectconfig
        """
        return self._values.get('open_id_connect_config')

    @property
    def tags(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, aws_cdk.core.CfnTag]]]]]:
        """``AWS::AppSync::GraphQLApi.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-graphqlapi.html#cfn-appsync-graphqlapi-tags
        """
        return self._values.get('tags')

    @property
    def user_pool_config(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnGraphQLApi.UserPoolConfigProperty"]]]:
        """``AWS::AppSync::GraphQLApi.UserPoolConfig``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-graphqlapi.html#cfn-appsync-graphqlapi-userpoolconfig
        """
        return self._values.get('user_pool_config')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnGraphQLApiProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnGraphQLSchema(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-appsync.CfnGraphQLSchema"):
    """A CloudFormation ``AWS::AppSync::GraphQLSchema``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-graphqlschema.html
    cloudformationResource:
    :cloudformationResource:: AWS::AppSync::GraphQLSchema
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, api_id: str, definition: typing.Optional[str]=None, definition_s3_location: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::AppSync::GraphQLSchema``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param api_id: ``AWS::AppSync::GraphQLSchema.ApiId``.
        :param definition: ``AWS::AppSync::GraphQLSchema.Definition``.
        :param definition_s3_location: ``AWS::AppSync::GraphQLSchema.DefinitionS3Location``.
        """
        props = CfnGraphQLSchemaProps(api_id=api_id, definition=definition, definition_s3_location=definition_s3_location)

        jsii.create(CfnGraphQLSchema, self, [scope, id, props])

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
    @jsii.member(jsii_name="apiId")
    def api_id(self) -> str:
        """``AWS::AppSync::GraphQLSchema.ApiId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-graphqlschema.html#cfn-appsync-graphqlschema-apiid
        """
        return jsii.get(self, "apiId")

    @api_id.setter
    def api_id(self, value: str):
        return jsii.set(self, "apiId", value)

    @property
    @jsii.member(jsii_name="definition")
    def definition(self) -> typing.Optional[str]:
        """``AWS::AppSync::GraphQLSchema.Definition``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-graphqlschema.html#cfn-appsync-graphqlschema-definition
        """
        return jsii.get(self, "definition")

    @definition.setter
    def definition(self, value: typing.Optional[str]):
        return jsii.set(self, "definition", value)

    @property
    @jsii.member(jsii_name="definitionS3Location")
    def definition_s3_location(self) -> typing.Optional[str]:
        """``AWS::AppSync::GraphQLSchema.DefinitionS3Location``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-graphqlschema.html#cfn-appsync-graphqlschema-definitions3location
        """
        return jsii.get(self, "definitionS3Location")

    @definition_s3_location.setter
    def definition_s3_location(self, value: typing.Optional[str]):
        return jsii.set(self, "definitionS3Location", value)


@jsii.data_type(jsii_type="@aws-cdk/aws-appsync.CfnGraphQLSchemaProps", jsii_struct_bases=[], name_mapping={'api_id': 'apiId', 'definition': 'definition', 'definition_s3_location': 'definitionS3Location'})
class CfnGraphQLSchemaProps():
    def __init__(self, *, api_id: str, definition: typing.Optional[str]=None, definition_s3_location: typing.Optional[str]=None):
        """Properties for defining a ``AWS::AppSync::GraphQLSchema``.

        :param api_id: ``AWS::AppSync::GraphQLSchema.ApiId``.
        :param definition: ``AWS::AppSync::GraphQLSchema.Definition``.
        :param definition_s3_location: ``AWS::AppSync::GraphQLSchema.DefinitionS3Location``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-graphqlschema.html
        """
        self._values = {
            'api_id': api_id,
        }
        if definition is not None: self._values["definition"] = definition
        if definition_s3_location is not None: self._values["definition_s3_location"] = definition_s3_location

    @property
    def api_id(self) -> str:
        """``AWS::AppSync::GraphQLSchema.ApiId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-graphqlschema.html#cfn-appsync-graphqlschema-apiid
        """
        return self._values.get('api_id')

    @property
    def definition(self) -> typing.Optional[str]:
        """``AWS::AppSync::GraphQLSchema.Definition``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-graphqlschema.html#cfn-appsync-graphqlschema-definition
        """
        return self._values.get('definition')

    @property
    def definition_s3_location(self) -> typing.Optional[str]:
        """``AWS::AppSync::GraphQLSchema.DefinitionS3Location``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-graphqlschema.html#cfn-appsync-graphqlschema-definitions3location
        """
        return self._values.get('definition_s3_location')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnGraphQLSchemaProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnResolver(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-appsync.CfnResolver"):
    """A CloudFormation ``AWS::AppSync::Resolver``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-resolver.html
    cloudformationResource:
    :cloudformationResource:: AWS::AppSync::Resolver
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, api_id: str, field_name: str, type_name: str, data_source_name: typing.Optional[str]=None, kind: typing.Optional[str]=None, pipeline_config: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["PipelineConfigProperty"]]]=None, request_mapping_template: typing.Optional[str]=None, request_mapping_template_s3_location: typing.Optional[str]=None, response_mapping_template: typing.Optional[str]=None, response_mapping_template_s3_location: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::AppSync::Resolver``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param api_id: ``AWS::AppSync::Resolver.ApiId``.
        :param field_name: ``AWS::AppSync::Resolver.FieldName``.
        :param type_name: ``AWS::AppSync::Resolver.TypeName``.
        :param data_source_name: ``AWS::AppSync::Resolver.DataSourceName``.
        :param kind: ``AWS::AppSync::Resolver.Kind``.
        :param pipeline_config: ``AWS::AppSync::Resolver.PipelineConfig``.
        :param request_mapping_template: ``AWS::AppSync::Resolver.RequestMappingTemplate``.
        :param request_mapping_template_s3_location: ``AWS::AppSync::Resolver.RequestMappingTemplateS3Location``.
        :param response_mapping_template: ``AWS::AppSync::Resolver.ResponseMappingTemplate``.
        :param response_mapping_template_s3_location: ``AWS::AppSync::Resolver.ResponseMappingTemplateS3Location``.
        """
        props = CfnResolverProps(api_id=api_id, field_name=field_name, type_name=type_name, data_source_name=data_source_name, kind=kind, pipeline_config=pipeline_config, request_mapping_template=request_mapping_template, request_mapping_template_s3_location=request_mapping_template_s3_location, response_mapping_template=response_mapping_template, response_mapping_template_s3_location=response_mapping_template_s3_location)

        jsii.create(CfnResolver, self, [scope, id, props])

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
    @jsii.member(jsii_name="attrFieldName")
    def attr_field_name(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: FieldName
        """
        return jsii.get(self, "attrFieldName")

    @property
    @jsii.member(jsii_name="attrResolverArn")
    def attr_resolver_arn(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: ResolverArn
        """
        return jsii.get(self, "attrResolverArn")

    @property
    @jsii.member(jsii_name="attrTypeName")
    def attr_type_name(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: TypeName
        """
        return jsii.get(self, "attrTypeName")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="apiId")
    def api_id(self) -> str:
        """``AWS::AppSync::Resolver.ApiId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-resolver.html#cfn-appsync-resolver-apiid
        """
        return jsii.get(self, "apiId")

    @api_id.setter
    def api_id(self, value: str):
        return jsii.set(self, "apiId", value)

    @property
    @jsii.member(jsii_name="fieldName")
    def field_name(self) -> str:
        """``AWS::AppSync::Resolver.FieldName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-resolver.html#cfn-appsync-resolver-fieldname
        """
        return jsii.get(self, "fieldName")

    @field_name.setter
    def field_name(self, value: str):
        return jsii.set(self, "fieldName", value)

    @property
    @jsii.member(jsii_name="typeName")
    def type_name(self) -> str:
        """``AWS::AppSync::Resolver.TypeName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-resolver.html#cfn-appsync-resolver-typename
        """
        return jsii.get(self, "typeName")

    @type_name.setter
    def type_name(self, value: str):
        return jsii.set(self, "typeName", value)

    @property
    @jsii.member(jsii_name="dataSourceName")
    def data_source_name(self) -> typing.Optional[str]:
        """``AWS::AppSync::Resolver.DataSourceName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-resolver.html#cfn-appsync-resolver-datasourcename
        """
        return jsii.get(self, "dataSourceName")

    @data_source_name.setter
    def data_source_name(self, value: typing.Optional[str]):
        return jsii.set(self, "dataSourceName", value)

    @property
    @jsii.member(jsii_name="kind")
    def kind(self) -> typing.Optional[str]:
        """``AWS::AppSync::Resolver.Kind``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-resolver.html#cfn-appsync-resolver-kind
        """
        return jsii.get(self, "kind")

    @kind.setter
    def kind(self, value: typing.Optional[str]):
        return jsii.set(self, "kind", value)

    @property
    @jsii.member(jsii_name="pipelineConfig")
    def pipeline_config(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["PipelineConfigProperty"]]]:
        """``AWS::AppSync::Resolver.PipelineConfig``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-resolver.html#cfn-appsync-resolver-pipelineconfig
        """
        return jsii.get(self, "pipelineConfig")

    @pipeline_config.setter
    def pipeline_config(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["PipelineConfigProperty"]]]):
        return jsii.set(self, "pipelineConfig", value)

    @property
    @jsii.member(jsii_name="requestMappingTemplate")
    def request_mapping_template(self) -> typing.Optional[str]:
        """``AWS::AppSync::Resolver.RequestMappingTemplate``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-resolver.html#cfn-appsync-resolver-requestmappingtemplate
        """
        return jsii.get(self, "requestMappingTemplate")

    @request_mapping_template.setter
    def request_mapping_template(self, value: typing.Optional[str]):
        return jsii.set(self, "requestMappingTemplate", value)

    @property
    @jsii.member(jsii_name="requestMappingTemplateS3Location")
    def request_mapping_template_s3_location(self) -> typing.Optional[str]:
        """``AWS::AppSync::Resolver.RequestMappingTemplateS3Location``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-resolver.html#cfn-appsync-resolver-requestmappingtemplates3location
        """
        return jsii.get(self, "requestMappingTemplateS3Location")

    @request_mapping_template_s3_location.setter
    def request_mapping_template_s3_location(self, value: typing.Optional[str]):
        return jsii.set(self, "requestMappingTemplateS3Location", value)

    @property
    @jsii.member(jsii_name="responseMappingTemplate")
    def response_mapping_template(self) -> typing.Optional[str]:
        """``AWS::AppSync::Resolver.ResponseMappingTemplate``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-resolver.html#cfn-appsync-resolver-responsemappingtemplate
        """
        return jsii.get(self, "responseMappingTemplate")

    @response_mapping_template.setter
    def response_mapping_template(self, value: typing.Optional[str]):
        return jsii.set(self, "responseMappingTemplate", value)

    @property
    @jsii.member(jsii_name="responseMappingTemplateS3Location")
    def response_mapping_template_s3_location(self) -> typing.Optional[str]:
        """``AWS::AppSync::Resolver.ResponseMappingTemplateS3Location``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-resolver.html#cfn-appsync-resolver-responsemappingtemplates3location
        """
        return jsii.get(self, "responseMappingTemplateS3Location")

    @response_mapping_template_s3_location.setter
    def response_mapping_template_s3_location(self, value: typing.Optional[str]):
        return jsii.set(self, "responseMappingTemplateS3Location", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-appsync.CfnResolver.PipelineConfigProperty", jsii_struct_bases=[], name_mapping={'functions': 'functions'})
    class PipelineConfigProperty():
        def __init__(self, *, functions: typing.Optional[typing.List[str]]=None):
            """
            :param functions: ``CfnResolver.PipelineConfigProperty.Functions``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-resolver-pipelineconfig.html
            """
            self._values = {
            }
            if functions is not None: self._values["functions"] = functions

        @property
        def functions(self) -> typing.Optional[typing.List[str]]:
            """``CfnResolver.PipelineConfigProperty.Functions``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-resolver-pipelineconfig.html#cfn-appsync-resolver-pipelineconfig-functions
            """
            return self._values.get('functions')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'PipelineConfigProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



@jsii.data_type(jsii_type="@aws-cdk/aws-appsync.CfnResolverProps", jsii_struct_bases=[], name_mapping={'api_id': 'apiId', 'field_name': 'fieldName', 'type_name': 'typeName', 'data_source_name': 'dataSourceName', 'kind': 'kind', 'pipeline_config': 'pipelineConfig', 'request_mapping_template': 'requestMappingTemplate', 'request_mapping_template_s3_location': 'requestMappingTemplateS3Location', 'response_mapping_template': 'responseMappingTemplate', 'response_mapping_template_s3_location': 'responseMappingTemplateS3Location'})
class CfnResolverProps():
    def __init__(self, *, api_id: str, field_name: str, type_name: str, data_source_name: typing.Optional[str]=None, kind: typing.Optional[str]=None, pipeline_config: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnResolver.PipelineConfigProperty"]]]=None, request_mapping_template: typing.Optional[str]=None, request_mapping_template_s3_location: typing.Optional[str]=None, response_mapping_template: typing.Optional[str]=None, response_mapping_template_s3_location: typing.Optional[str]=None):
        """Properties for defining a ``AWS::AppSync::Resolver``.

        :param api_id: ``AWS::AppSync::Resolver.ApiId``.
        :param field_name: ``AWS::AppSync::Resolver.FieldName``.
        :param type_name: ``AWS::AppSync::Resolver.TypeName``.
        :param data_source_name: ``AWS::AppSync::Resolver.DataSourceName``.
        :param kind: ``AWS::AppSync::Resolver.Kind``.
        :param pipeline_config: ``AWS::AppSync::Resolver.PipelineConfig``.
        :param request_mapping_template: ``AWS::AppSync::Resolver.RequestMappingTemplate``.
        :param request_mapping_template_s3_location: ``AWS::AppSync::Resolver.RequestMappingTemplateS3Location``.
        :param response_mapping_template: ``AWS::AppSync::Resolver.ResponseMappingTemplate``.
        :param response_mapping_template_s3_location: ``AWS::AppSync::Resolver.ResponseMappingTemplateS3Location``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-resolver.html
        """
        self._values = {
            'api_id': api_id,
            'field_name': field_name,
            'type_name': type_name,
        }
        if data_source_name is not None: self._values["data_source_name"] = data_source_name
        if kind is not None: self._values["kind"] = kind
        if pipeline_config is not None: self._values["pipeline_config"] = pipeline_config
        if request_mapping_template is not None: self._values["request_mapping_template"] = request_mapping_template
        if request_mapping_template_s3_location is not None: self._values["request_mapping_template_s3_location"] = request_mapping_template_s3_location
        if response_mapping_template is not None: self._values["response_mapping_template"] = response_mapping_template
        if response_mapping_template_s3_location is not None: self._values["response_mapping_template_s3_location"] = response_mapping_template_s3_location

    @property
    def api_id(self) -> str:
        """``AWS::AppSync::Resolver.ApiId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-resolver.html#cfn-appsync-resolver-apiid
        """
        return self._values.get('api_id')

    @property
    def field_name(self) -> str:
        """``AWS::AppSync::Resolver.FieldName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-resolver.html#cfn-appsync-resolver-fieldname
        """
        return self._values.get('field_name')

    @property
    def type_name(self) -> str:
        """``AWS::AppSync::Resolver.TypeName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-resolver.html#cfn-appsync-resolver-typename
        """
        return self._values.get('type_name')

    @property
    def data_source_name(self) -> typing.Optional[str]:
        """``AWS::AppSync::Resolver.DataSourceName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-resolver.html#cfn-appsync-resolver-datasourcename
        """
        return self._values.get('data_source_name')

    @property
    def kind(self) -> typing.Optional[str]:
        """``AWS::AppSync::Resolver.Kind``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-resolver.html#cfn-appsync-resolver-kind
        """
        return self._values.get('kind')

    @property
    def pipeline_config(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnResolver.PipelineConfigProperty"]]]:
        """``AWS::AppSync::Resolver.PipelineConfig``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-resolver.html#cfn-appsync-resolver-pipelineconfig
        """
        return self._values.get('pipeline_config')

    @property
    def request_mapping_template(self) -> typing.Optional[str]:
        """``AWS::AppSync::Resolver.RequestMappingTemplate``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-resolver.html#cfn-appsync-resolver-requestmappingtemplate
        """
        return self._values.get('request_mapping_template')

    @property
    def request_mapping_template_s3_location(self) -> typing.Optional[str]:
        """``AWS::AppSync::Resolver.RequestMappingTemplateS3Location``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-resolver.html#cfn-appsync-resolver-requestmappingtemplates3location
        """
        return self._values.get('request_mapping_template_s3_location')

    @property
    def response_mapping_template(self) -> typing.Optional[str]:
        """``AWS::AppSync::Resolver.ResponseMappingTemplate``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-resolver.html#cfn-appsync-resolver-responsemappingtemplate
        """
        return self._values.get('response_mapping_template')

    @property
    def response_mapping_template_s3_location(self) -> typing.Optional[str]:
        """``AWS::AppSync::Resolver.ResponseMappingTemplateS3Location``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-resolver.html#cfn-appsync-resolver-responsemappingtemplates3location
        """
        return self._values.get('response_mapping_template_s3_location')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnResolverProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


__all__ = ["CfnApiKey", "CfnApiKeyProps", "CfnDataSource", "CfnDataSourceProps", "CfnFunctionConfiguration", "CfnFunctionConfigurationProps", "CfnGraphQLApi", "CfnGraphQLApiProps", "CfnGraphQLSchema", "CfnGraphQLSchemaProps", "CfnResolver", "CfnResolverProps", "__jsii_assembly__"]

publication.publish()
