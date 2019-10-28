import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.core
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-lakeformation", "1.15.0", __name__, "aws-lakeformation@1.15.0.jsii.tgz")
class CfnDataLakeSettings(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-lakeformation.CfnDataLakeSettings"):
    """A CloudFormation ``AWS::LakeFormation::DataLakeSettings``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lakeformation-datalakesettings.html
    cloudformationResource:
    :cloudformationResource:: AWS::LakeFormation::DataLakeSettings
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, admins: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union["DataLakePrincipalProperty", aws_cdk.core.IResolvable]]]]]=None) -> None:
        """Create a new ``AWS::LakeFormation::DataLakeSettings``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param admins: ``AWS::LakeFormation::DataLakeSettings.Admins``.
        """
        props = CfnDataLakeSettingsProps(admins=admins)

        jsii.create(CfnDataLakeSettings, self, [scope, id, props])

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
    @jsii.member(jsii_name="admins")
    def admins(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union["DataLakePrincipalProperty", aws_cdk.core.IResolvable]]]]]:
        """``AWS::LakeFormation::DataLakeSettings.Admins``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lakeformation-datalakesettings.html#cfn-lakeformation-datalakesettings-admins
        """
        return jsii.get(self, "admins")

    @admins.setter
    def admins(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union["DataLakePrincipalProperty", aws_cdk.core.IResolvable]]]]]):
        return jsii.set(self, "admins", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-lakeformation.CfnDataLakeSettings.DataLakePrincipalProperty", jsii_struct_bases=[], name_mapping={'data_lake_principal_identifier': 'dataLakePrincipalIdentifier'})
    class DataLakePrincipalProperty():
        def __init__(self, *, data_lake_principal_identifier: typing.Optional[str]=None):
            """
            :param data_lake_principal_identifier: ``CfnDataLakeSettings.DataLakePrincipalProperty.DataLakePrincipalIdentifier``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-lakeformation-datalakesettings-datalakeprincipal.html
            """
            self._values = {
            }
            if data_lake_principal_identifier is not None: self._values["data_lake_principal_identifier"] = data_lake_principal_identifier

        @property
        def data_lake_principal_identifier(self) -> typing.Optional[str]:
            """``CfnDataLakeSettings.DataLakePrincipalProperty.DataLakePrincipalIdentifier``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-lakeformation-datalakesettings-datalakeprincipal.html#cfn-lakeformation-datalakesettings-datalakeprincipal-datalakeprincipalidentifier
            """
            return self._values.get('data_lake_principal_identifier')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'DataLakePrincipalProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



@jsii.data_type(jsii_type="@aws-cdk/aws-lakeformation.CfnDataLakeSettingsProps", jsii_struct_bases=[], name_mapping={'admins': 'admins'})
class CfnDataLakeSettingsProps():
    def __init__(self, *, admins: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union["CfnDataLakeSettings.DataLakePrincipalProperty", aws_cdk.core.IResolvable]]]]]=None):
        """Properties for defining a ``AWS::LakeFormation::DataLakeSettings``.

        :param admins: ``AWS::LakeFormation::DataLakeSettings.Admins``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lakeformation-datalakesettings.html
        """
        self._values = {
        }
        if admins is not None: self._values["admins"] = admins

    @property
    def admins(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union["CfnDataLakeSettings.DataLakePrincipalProperty", aws_cdk.core.IResolvable]]]]]:
        """``AWS::LakeFormation::DataLakeSettings.Admins``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lakeformation-datalakesettings.html#cfn-lakeformation-datalakesettings-admins
        """
        return self._values.get('admins')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnDataLakeSettingsProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnPermissions(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-lakeformation.CfnPermissions"):
    """A CloudFormation ``AWS::LakeFormation::Permissions``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lakeformation-permissions.html
    cloudformationResource:
    :cloudformationResource:: AWS::LakeFormation::Permissions
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, data_lake_principal: typing.Union[aws_cdk.core.IResolvable, "DataLakePrincipalProperty"], resource: typing.Union[aws_cdk.core.IResolvable, "ResourceProperty"], permissions: typing.Optional[typing.List[str]]=None, permissions_with_grant_option: typing.Optional[typing.List[str]]=None) -> None:
        """Create a new ``AWS::LakeFormation::Permissions``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param data_lake_principal: ``AWS::LakeFormation::Permissions.DataLakePrincipal``.
        :param resource: ``AWS::LakeFormation::Permissions.Resource``.
        :param permissions: ``AWS::LakeFormation::Permissions.Permissions``.
        :param permissions_with_grant_option: ``AWS::LakeFormation::Permissions.PermissionsWithGrantOption``.
        """
        props = CfnPermissionsProps(data_lake_principal=data_lake_principal, resource=resource, permissions=permissions, permissions_with_grant_option=permissions_with_grant_option)

        jsii.create(CfnPermissions, self, [scope, id, props])

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
    @jsii.member(jsii_name="dataLakePrincipal")
    def data_lake_principal(self) -> typing.Union[aws_cdk.core.IResolvable, "DataLakePrincipalProperty"]:
        """``AWS::LakeFormation::Permissions.DataLakePrincipal``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lakeformation-permissions.html#cfn-lakeformation-permissions-datalakeprincipal
        """
        return jsii.get(self, "dataLakePrincipal")

    @data_lake_principal.setter
    def data_lake_principal(self, value: typing.Union[aws_cdk.core.IResolvable, "DataLakePrincipalProperty"]):
        return jsii.set(self, "dataLakePrincipal", value)

    @property
    @jsii.member(jsii_name="resource")
    def resource(self) -> typing.Union[aws_cdk.core.IResolvable, "ResourceProperty"]:
        """``AWS::LakeFormation::Permissions.Resource``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lakeformation-permissions.html#cfn-lakeformation-permissions-resource
        """
        return jsii.get(self, "resource")

    @resource.setter
    def resource(self, value: typing.Union[aws_cdk.core.IResolvable, "ResourceProperty"]):
        return jsii.set(self, "resource", value)

    @property
    @jsii.member(jsii_name="permissions")
    def permissions(self) -> typing.Optional[typing.List[str]]:
        """``AWS::LakeFormation::Permissions.Permissions``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lakeformation-permissions.html#cfn-lakeformation-permissions-permissions
        """
        return jsii.get(self, "permissions")

    @permissions.setter
    def permissions(self, value: typing.Optional[typing.List[str]]):
        return jsii.set(self, "permissions", value)

    @property
    @jsii.member(jsii_name="permissionsWithGrantOption")
    def permissions_with_grant_option(self) -> typing.Optional[typing.List[str]]:
        """``AWS::LakeFormation::Permissions.PermissionsWithGrantOption``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lakeformation-permissions.html#cfn-lakeformation-permissions-permissionswithgrantoption
        """
        return jsii.get(self, "permissionsWithGrantOption")

    @permissions_with_grant_option.setter
    def permissions_with_grant_option(self, value: typing.Optional[typing.List[str]]):
        return jsii.set(self, "permissionsWithGrantOption", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-lakeformation.CfnPermissions.DataLakePrincipalProperty", jsii_struct_bases=[], name_mapping={'data_lake_principal_identifier': 'dataLakePrincipalIdentifier'})
    class DataLakePrincipalProperty():
        def __init__(self, *, data_lake_principal_identifier: typing.Optional[str]=None):
            """
            :param data_lake_principal_identifier: ``CfnPermissions.DataLakePrincipalProperty.DataLakePrincipalIdentifier``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-lakeformation-permissions-datalakeprincipal.html
            """
            self._values = {
            }
            if data_lake_principal_identifier is not None: self._values["data_lake_principal_identifier"] = data_lake_principal_identifier

        @property
        def data_lake_principal_identifier(self) -> typing.Optional[str]:
            """``CfnPermissions.DataLakePrincipalProperty.DataLakePrincipalIdentifier``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-lakeformation-permissions-datalakeprincipal.html#cfn-lakeformation-permissions-datalakeprincipal-datalakeprincipalidentifier
            """
            return self._values.get('data_lake_principal_identifier')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'DataLakePrincipalProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-lakeformation.CfnPermissions.DatabaseResourceProperty", jsii_struct_bases=[], name_mapping={'name': 'name'})
    class DatabaseResourceProperty():
        def __init__(self, *, name: typing.Optional[str]=None):
            """
            :param name: ``CfnPermissions.DatabaseResourceProperty.Name``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-lakeformation-permissions-databaseresource.html
            """
            self._values = {
            }
            if name is not None: self._values["name"] = name

        @property
        def name(self) -> typing.Optional[str]:
            """``CfnPermissions.DatabaseResourceProperty.Name``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-lakeformation-permissions-databaseresource.html#cfn-lakeformation-permissions-databaseresource-name
            """
            return self._values.get('name')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'DatabaseResourceProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-lakeformation.CfnPermissions.ResourceProperty", jsii_struct_bases=[], name_mapping={'database_resource': 'databaseResource', 'table_resource': 'tableResource'})
    class ResourceProperty():
        def __init__(self, *, database_resource: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnPermissions.DatabaseResourceProperty"]]]=None, table_resource: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnPermissions.TableResourceProperty"]]]=None):
            """
            :param database_resource: ``CfnPermissions.ResourceProperty.DatabaseResource``.
            :param table_resource: ``CfnPermissions.ResourceProperty.TableResource``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-lakeformation-permissions-resource.html
            """
            self._values = {
            }
            if database_resource is not None: self._values["database_resource"] = database_resource
            if table_resource is not None: self._values["table_resource"] = table_resource

        @property
        def database_resource(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnPermissions.DatabaseResourceProperty"]]]:
            """``CfnPermissions.ResourceProperty.DatabaseResource``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-lakeformation-permissions-resource.html#cfn-lakeformation-permissions-resource-databaseresource
            """
            return self._values.get('database_resource')

        @property
        def table_resource(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnPermissions.TableResourceProperty"]]]:
            """``CfnPermissions.ResourceProperty.TableResource``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-lakeformation-permissions-resource.html#cfn-lakeformation-permissions-resource-tableresource
            """
            return self._values.get('table_resource')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'ResourceProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-lakeformation.CfnPermissions.TableResourceProperty", jsii_struct_bases=[], name_mapping={'database_name': 'databaseName', 'name': 'name'})
    class TableResourceProperty():
        def __init__(self, *, database_name: typing.Optional[str]=None, name: typing.Optional[str]=None):
            """
            :param database_name: ``CfnPermissions.TableResourceProperty.DatabaseName``.
            :param name: ``CfnPermissions.TableResourceProperty.Name``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-lakeformation-permissions-tableresource.html
            """
            self._values = {
            }
            if database_name is not None: self._values["database_name"] = database_name
            if name is not None: self._values["name"] = name

        @property
        def database_name(self) -> typing.Optional[str]:
            """``CfnPermissions.TableResourceProperty.DatabaseName``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-lakeformation-permissions-tableresource.html#cfn-lakeformation-permissions-tableresource-databasename
            """
            return self._values.get('database_name')

        @property
        def name(self) -> typing.Optional[str]:
            """``CfnPermissions.TableResourceProperty.Name``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-lakeformation-permissions-tableresource.html#cfn-lakeformation-permissions-tableresource-name
            """
            return self._values.get('name')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'TableResourceProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



@jsii.data_type(jsii_type="@aws-cdk/aws-lakeformation.CfnPermissionsProps", jsii_struct_bases=[], name_mapping={'data_lake_principal': 'dataLakePrincipal', 'resource': 'resource', 'permissions': 'permissions', 'permissions_with_grant_option': 'permissionsWithGrantOption'})
class CfnPermissionsProps():
    def __init__(self, *, data_lake_principal: typing.Union[aws_cdk.core.IResolvable, "CfnPermissions.DataLakePrincipalProperty"], resource: typing.Union[aws_cdk.core.IResolvable, "CfnPermissions.ResourceProperty"], permissions: typing.Optional[typing.List[str]]=None, permissions_with_grant_option: typing.Optional[typing.List[str]]=None):
        """Properties for defining a ``AWS::LakeFormation::Permissions``.

        :param data_lake_principal: ``AWS::LakeFormation::Permissions.DataLakePrincipal``.
        :param resource: ``AWS::LakeFormation::Permissions.Resource``.
        :param permissions: ``AWS::LakeFormation::Permissions.Permissions``.
        :param permissions_with_grant_option: ``AWS::LakeFormation::Permissions.PermissionsWithGrantOption``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lakeformation-permissions.html
        """
        self._values = {
            'data_lake_principal': data_lake_principal,
            'resource': resource,
        }
        if permissions is not None: self._values["permissions"] = permissions
        if permissions_with_grant_option is not None: self._values["permissions_with_grant_option"] = permissions_with_grant_option

    @property
    def data_lake_principal(self) -> typing.Union[aws_cdk.core.IResolvable, "CfnPermissions.DataLakePrincipalProperty"]:
        """``AWS::LakeFormation::Permissions.DataLakePrincipal``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lakeformation-permissions.html#cfn-lakeformation-permissions-datalakeprincipal
        """
        return self._values.get('data_lake_principal')

    @property
    def resource(self) -> typing.Union[aws_cdk.core.IResolvable, "CfnPermissions.ResourceProperty"]:
        """``AWS::LakeFormation::Permissions.Resource``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lakeformation-permissions.html#cfn-lakeformation-permissions-resource
        """
        return self._values.get('resource')

    @property
    def permissions(self) -> typing.Optional[typing.List[str]]:
        """``AWS::LakeFormation::Permissions.Permissions``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lakeformation-permissions.html#cfn-lakeformation-permissions-permissions
        """
        return self._values.get('permissions')

    @property
    def permissions_with_grant_option(self) -> typing.Optional[typing.List[str]]:
        """``AWS::LakeFormation::Permissions.PermissionsWithGrantOption``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lakeformation-permissions.html#cfn-lakeformation-permissions-permissionswithgrantoption
        """
        return self._values.get('permissions_with_grant_option')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnPermissionsProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnResource(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-lakeformation.CfnResource"):
    """A CloudFormation ``AWS::LakeFormation::Resource``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lakeformation-resource.html
    cloudformationResource:
    :cloudformationResource:: AWS::LakeFormation::Resource
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, resource_arn: str, use_service_linked_role: typing.Union[bool, aws_cdk.core.IResolvable], role_arn: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::LakeFormation::Resource``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param resource_arn: ``AWS::LakeFormation::Resource.ResourceArn``.
        :param use_service_linked_role: ``AWS::LakeFormation::Resource.UseServiceLinkedRole``.
        :param role_arn: ``AWS::LakeFormation::Resource.RoleArn``.
        """
        props = CfnResourceProps(resource_arn=resource_arn, use_service_linked_role=use_service_linked_role, role_arn=role_arn)

        jsii.create(CfnResource, self, [scope, id, props])

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
    @jsii.member(jsii_name="resourceArn")
    def resource_arn(self) -> str:
        """``AWS::LakeFormation::Resource.ResourceArn``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lakeformation-resource.html#cfn-lakeformation-resource-resourcearn
        """
        return jsii.get(self, "resourceArn")

    @resource_arn.setter
    def resource_arn(self, value: str):
        return jsii.set(self, "resourceArn", value)

    @property
    @jsii.member(jsii_name="useServiceLinkedRole")
    def use_service_linked_role(self) -> typing.Union[bool, aws_cdk.core.IResolvable]:
        """``AWS::LakeFormation::Resource.UseServiceLinkedRole``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lakeformation-resource.html#cfn-lakeformation-resource-useservicelinkedrole
        """
        return jsii.get(self, "useServiceLinkedRole")

    @use_service_linked_role.setter
    def use_service_linked_role(self, value: typing.Union[bool, aws_cdk.core.IResolvable]):
        return jsii.set(self, "useServiceLinkedRole", value)

    @property
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> typing.Optional[str]:
        """``AWS::LakeFormation::Resource.RoleArn``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lakeformation-resource.html#cfn-lakeformation-resource-rolearn
        """
        return jsii.get(self, "roleArn")

    @role_arn.setter
    def role_arn(self, value: typing.Optional[str]):
        return jsii.set(self, "roleArn", value)


@jsii.data_type(jsii_type="@aws-cdk/aws-lakeformation.CfnResourceProps", jsii_struct_bases=[], name_mapping={'resource_arn': 'resourceArn', 'use_service_linked_role': 'useServiceLinkedRole', 'role_arn': 'roleArn'})
class CfnResourceProps():
    def __init__(self, *, resource_arn: str, use_service_linked_role: typing.Union[bool, aws_cdk.core.IResolvable], role_arn: typing.Optional[str]=None):
        """Properties for defining a ``AWS::LakeFormation::Resource``.

        :param resource_arn: ``AWS::LakeFormation::Resource.ResourceArn``.
        :param use_service_linked_role: ``AWS::LakeFormation::Resource.UseServiceLinkedRole``.
        :param role_arn: ``AWS::LakeFormation::Resource.RoleArn``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lakeformation-resource.html
        """
        self._values = {
            'resource_arn': resource_arn,
            'use_service_linked_role': use_service_linked_role,
        }
        if role_arn is not None: self._values["role_arn"] = role_arn

    @property
    def resource_arn(self) -> str:
        """``AWS::LakeFormation::Resource.ResourceArn``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lakeformation-resource.html#cfn-lakeformation-resource-resourcearn
        """
        return self._values.get('resource_arn')

    @property
    def use_service_linked_role(self) -> typing.Union[bool, aws_cdk.core.IResolvable]:
        """``AWS::LakeFormation::Resource.UseServiceLinkedRole``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lakeformation-resource.html#cfn-lakeformation-resource-useservicelinkedrole
        """
        return self._values.get('use_service_linked_role')

    @property
    def role_arn(self) -> typing.Optional[str]:
        """``AWS::LakeFormation::Resource.RoleArn``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lakeformation-resource.html#cfn-lakeformation-resource-rolearn
        """
        return self._values.get('role_arn')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnResourceProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


__all__ = ["CfnDataLakeSettings", "CfnDataLakeSettingsProps", "CfnPermissions", "CfnPermissionsProps", "CfnResource", "CfnResourceProps", "__jsii_assembly__"]

publication.publish()
