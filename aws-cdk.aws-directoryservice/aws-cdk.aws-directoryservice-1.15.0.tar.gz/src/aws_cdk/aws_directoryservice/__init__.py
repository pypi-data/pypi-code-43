import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.core
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-directoryservice", "1.15.0", __name__, "aws-directoryservice@1.15.0.jsii.tgz")
class CfnMicrosoftAD(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-directoryservice.CfnMicrosoftAD"):
    """A CloudFormation ``AWS::DirectoryService::MicrosoftAD``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-directoryservice-microsoftad.html
    cloudformationResource:
    :cloudformationResource:: AWS::DirectoryService::MicrosoftAD
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, name: str, password: str, vpc_settings: typing.Union["VpcSettingsProperty", aws_cdk.core.IResolvable], create_alias: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, edition: typing.Optional[str]=None, enable_sso: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, short_name: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::DirectoryService::MicrosoftAD``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param name: ``AWS::DirectoryService::MicrosoftAD.Name``.
        :param password: ``AWS::DirectoryService::MicrosoftAD.Password``.
        :param vpc_settings: ``AWS::DirectoryService::MicrosoftAD.VpcSettings``.
        :param create_alias: ``AWS::DirectoryService::MicrosoftAD.CreateAlias``.
        :param edition: ``AWS::DirectoryService::MicrosoftAD.Edition``.
        :param enable_sso: ``AWS::DirectoryService::MicrosoftAD.EnableSso``.
        :param short_name: ``AWS::DirectoryService::MicrosoftAD.ShortName``.
        """
        props = CfnMicrosoftADProps(name=name, password=password, vpc_settings=vpc_settings, create_alias=create_alias, edition=edition, enable_sso=enable_sso, short_name=short_name)

        jsii.create(CfnMicrosoftAD, self, [scope, id, props])

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
    @jsii.member(jsii_name="attrAlias")
    def attr_alias(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: Alias
        """
        return jsii.get(self, "attrAlias")

    @property
    @jsii.member(jsii_name="attrDnsIpAddresses")
    def attr_dns_ip_addresses(self) -> typing.List[str]:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: DnsIpAddresses
        """
        return jsii.get(self, "attrDnsIpAddresses")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> str:
        """``AWS::DirectoryService::MicrosoftAD.Name``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-directoryservice-microsoftad.html#cfn-directoryservice-microsoftad-name
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: str):
        return jsii.set(self, "name", value)

    @property
    @jsii.member(jsii_name="password")
    def password(self) -> str:
        """``AWS::DirectoryService::MicrosoftAD.Password``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-directoryservice-microsoftad.html#cfn-directoryservice-microsoftad-password
        """
        return jsii.get(self, "password")

    @password.setter
    def password(self, value: str):
        return jsii.set(self, "password", value)

    @property
    @jsii.member(jsii_name="vpcSettings")
    def vpc_settings(self) -> typing.Union["VpcSettingsProperty", aws_cdk.core.IResolvable]:
        """``AWS::DirectoryService::MicrosoftAD.VpcSettings``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-directoryservice-microsoftad.html#cfn-directoryservice-microsoftad-vpcsettings
        """
        return jsii.get(self, "vpcSettings")

    @vpc_settings.setter
    def vpc_settings(self, value: typing.Union["VpcSettingsProperty", aws_cdk.core.IResolvable]):
        return jsii.set(self, "vpcSettings", value)

    @property
    @jsii.member(jsii_name="createAlias")
    def create_alias(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::DirectoryService::MicrosoftAD.CreateAlias``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-directoryservice-microsoftad.html#cfn-directoryservice-microsoftad-createalias
        """
        return jsii.get(self, "createAlias")

    @create_alias.setter
    def create_alias(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "createAlias", value)

    @property
    @jsii.member(jsii_name="edition")
    def edition(self) -> typing.Optional[str]:
        """``AWS::DirectoryService::MicrosoftAD.Edition``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-directoryservice-microsoftad.html#cfn-directoryservice-microsoftad-edition
        """
        return jsii.get(self, "edition")

    @edition.setter
    def edition(self, value: typing.Optional[str]):
        return jsii.set(self, "edition", value)

    @property
    @jsii.member(jsii_name="enableSso")
    def enable_sso(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::DirectoryService::MicrosoftAD.EnableSso``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-directoryservice-microsoftad.html#cfn-directoryservice-microsoftad-enablesso
        """
        return jsii.get(self, "enableSso")

    @enable_sso.setter
    def enable_sso(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "enableSso", value)

    @property
    @jsii.member(jsii_name="shortName")
    def short_name(self) -> typing.Optional[str]:
        """``AWS::DirectoryService::MicrosoftAD.ShortName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-directoryservice-microsoftad.html#cfn-directoryservice-microsoftad-shortname
        """
        return jsii.get(self, "shortName")

    @short_name.setter
    def short_name(self, value: typing.Optional[str]):
        return jsii.set(self, "shortName", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-directoryservice.CfnMicrosoftAD.VpcSettingsProperty", jsii_struct_bases=[], name_mapping={'subnet_ids': 'subnetIds', 'vpc_id': 'vpcId'})
    class VpcSettingsProperty():
        def __init__(self, *, subnet_ids: typing.List[str], vpc_id: str):
            """
            :param subnet_ids: ``CfnMicrosoftAD.VpcSettingsProperty.SubnetIds``.
            :param vpc_id: ``CfnMicrosoftAD.VpcSettingsProperty.VpcId``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-directoryservice-microsoftad-vpcsettings.html
            """
            self._values = {
                'subnet_ids': subnet_ids,
                'vpc_id': vpc_id,
            }

        @property
        def subnet_ids(self) -> typing.List[str]:
            """``CfnMicrosoftAD.VpcSettingsProperty.SubnetIds``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-directoryservice-microsoftad-vpcsettings.html#cfn-directoryservice-microsoftad-vpcsettings-subnetids
            """
            return self._values.get('subnet_ids')

        @property
        def vpc_id(self) -> str:
            """``CfnMicrosoftAD.VpcSettingsProperty.VpcId``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-directoryservice-microsoftad-vpcsettings.html#cfn-directoryservice-microsoftad-vpcsettings-vpcid
            """
            return self._values.get('vpc_id')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'VpcSettingsProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



@jsii.data_type(jsii_type="@aws-cdk/aws-directoryservice.CfnMicrosoftADProps", jsii_struct_bases=[], name_mapping={'name': 'name', 'password': 'password', 'vpc_settings': 'vpcSettings', 'create_alias': 'createAlias', 'edition': 'edition', 'enable_sso': 'enableSso', 'short_name': 'shortName'})
class CfnMicrosoftADProps():
    def __init__(self, *, name: str, password: str, vpc_settings: typing.Union["CfnMicrosoftAD.VpcSettingsProperty", aws_cdk.core.IResolvable], create_alias: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, edition: typing.Optional[str]=None, enable_sso: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, short_name: typing.Optional[str]=None):
        """Properties for defining a ``AWS::DirectoryService::MicrosoftAD``.

        :param name: ``AWS::DirectoryService::MicrosoftAD.Name``.
        :param password: ``AWS::DirectoryService::MicrosoftAD.Password``.
        :param vpc_settings: ``AWS::DirectoryService::MicrosoftAD.VpcSettings``.
        :param create_alias: ``AWS::DirectoryService::MicrosoftAD.CreateAlias``.
        :param edition: ``AWS::DirectoryService::MicrosoftAD.Edition``.
        :param enable_sso: ``AWS::DirectoryService::MicrosoftAD.EnableSso``.
        :param short_name: ``AWS::DirectoryService::MicrosoftAD.ShortName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-directoryservice-microsoftad.html
        """
        self._values = {
            'name': name,
            'password': password,
            'vpc_settings': vpc_settings,
        }
        if create_alias is not None: self._values["create_alias"] = create_alias
        if edition is not None: self._values["edition"] = edition
        if enable_sso is not None: self._values["enable_sso"] = enable_sso
        if short_name is not None: self._values["short_name"] = short_name

    @property
    def name(self) -> str:
        """``AWS::DirectoryService::MicrosoftAD.Name``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-directoryservice-microsoftad.html#cfn-directoryservice-microsoftad-name
        """
        return self._values.get('name')

    @property
    def password(self) -> str:
        """``AWS::DirectoryService::MicrosoftAD.Password``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-directoryservice-microsoftad.html#cfn-directoryservice-microsoftad-password
        """
        return self._values.get('password')

    @property
    def vpc_settings(self) -> typing.Union["CfnMicrosoftAD.VpcSettingsProperty", aws_cdk.core.IResolvable]:
        """``AWS::DirectoryService::MicrosoftAD.VpcSettings``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-directoryservice-microsoftad.html#cfn-directoryservice-microsoftad-vpcsettings
        """
        return self._values.get('vpc_settings')

    @property
    def create_alias(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::DirectoryService::MicrosoftAD.CreateAlias``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-directoryservice-microsoftad.html#cfn-directoryservice-microsoftad-createalias
        """
        return self._values.get('create_alias')

    @property
    def edition(self) -> typing.Optional[str]:
        """``AWS::DirectoryService::MicrosoftAD.Edition``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-directoryservice-microsoftad.html#cfn-directoryservice-microsoftad-edition
        """
        return self._values.get('edition')

    @property
    def enable_sso(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::DirectoryService::MicrosoftAD.EnableSso``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-directoryservice-microsoftad.html#cfn-directoryservice-microsoftad-enablesso
        """
        return self._values.get('enable_sso')

    @property
    def short_name(self) -> typing.Optional[str]:
        """``AWS::DirectoryService::MicrosoftAD.ShortName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-directoryservice-microsoftad.html#cfn-directoryservice-microsoftad-shortname
        """
        return self._values.get('short_name')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnMicrosoftADProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnSimpleAD(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-directoryservice.CfnSimpleAD"):
    """A CloudFormation ``AWS::DirectoryService::SimpleAD``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-directoryservice-simplead.html
    cloudformationResource:
    :cloudformationResource:: AWS::DirectoryService::SimpleAD
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, name: str, password: str, size: str, vpc_settings: typing.Union[aws_cdk.core.IResolvable, "VpcSettingsProperty"], create_alias: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, description: typing.Optional[str]=None, enable_sso: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, short_name: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::DirectoryService::SimpleAD``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param name: ``AWS::DirectoryService::SimpleAD.Name``.
        :param password: ``AWS::DirectoryService::SimpleAD.Password``.
        :param size: ``AWS::DirectoryService::SimpleAD.Size``.
        :param vpc_settings: ``AWS::DirectoryService::SimpleAD.VpcSettings``.
        :param create_alias: ``AWS::DirectoryService::SimpleAD.CreateAlias``.
        :param description: ``AWS::DirectoryService::SimpleAD.Description``.
        :param enable_sso: ``AWS::DirectoryService::SimpleAD.EnableSso``.
        :param short_name: ``AWS::DirectoryService::SimpleAD.ShortName``.
        """
        props = CfnSimpleADProps(name=name, password=password, size=size, vpc_settings=vpc_settings, create_alias=create_alias, description=description, enable_sso=enable_sso, short_name=short_name)

        jsii.create(CfnSimpleAD, self, [scope, id, props])

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
    @jsii.member(jsii_name="attrAlias")
    def attr_alias(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: Alias
        """
        return jsii.get(self, "attrAlias")

    @property
    @jsii.member(jsii_name="attrDnsIpAddresses")
    def attr_dns_ip_addresses(self) -> typing.List[str]:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: DnsIpAddresses
        """
        return jsii.get(self, "attrDnsIpAddresses")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> str:
        """``AWS::DirectoryService::SimpleAD.Name``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-directoryservice-simplead.html#cfn-directoryservice-simplead-name
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: str):
        return jsii.set(self, "name", value)

    @property
    @jsii.member(jsii_name="password")
    def password(self) -> str:
        """``AWS::DirectoryService::SimpleAD.Password``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-directoryservice-simplead.html#cfn-directoryservice-simplead-password
        """
        return jsii.get(self, "password")

    @password.setter
    def password(self, value: str):
        return jsii.set(self, "password", value)

    @property
    @jsii.member(jsii_name="size")
    def size(self) -> str:
        """``AWS::DirectoryService::SimpleAD.Size``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-directoryservice-simplead.html#cfn-directoryservice-simplead-size
        """
        return jsii.get(self, "size")

    @size.setter
    def size(self, value: str):
        return jsii.set(self, "size", value)

    @property
    @jsii.member(jsii_name="vpcSettings")
    def vpc_settings(self) -> typing.Union[aws_cdk.core.IResolvable, "VpcSettingsProperty"]:
        """``AWS::DirectoryService::SimpleAD.VpcSettings``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-directoryservice-simplead.html#cfn-directoryservice-simplead-vpcsettings
        """
        return jsii.get(self, "vpcSettings")

    @vpc_settings.setter
    def vpc_settings(self, value: typing.Union[aws_cdk.core.IResolvable, "VpcSettingsProperty"]):
        return jsii.set(self, "vpcSettings", value)

    @property
    @jsii.member(jsii_name="createAlias")
    def create_alias(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::DirectoryService::SimpleAD.CreateAlias``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-directoryservice-simplead.html#cfn-directoryservice-simplead-createalias
        """
        return jsii.get(self, "createAlias")

    @create_alias.setter
    def create_alias(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "createAlias", value)

    @property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[str]:
        """``AWS::DirectoryService::SimpleAD.Description``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-directoryservice-simplead.html#cfn-directoryservice-simplead-description
        """
        return jsii.get(self, "description")

    @description.setter
    def description(self, value: typing.Optional[str]):
        return jsii.set(self, "description", value)

    @property
    @jsii.member(jsii_name="enableSso")
    def enable_sso(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::DirectoryService::SimpleAD.EnableSso``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-directoryservice-simplead.html#cfn-directoryservice-simplead-enablesso
        """
        return jsii.get(self, "enableSso")

    @enable_sso.setter
    def enable_sso(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "enableSso", value)

    @property
    @jsii.member(jsii_name="shortName")
    def short_name(self) -> typing.Optional[str]:
        """``AWS::DirectoryService::SimpleAD.ShortName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-directoryservice-simplead.html#cfn-directoryservice-simplead-shortname
        """
        return jsii.get(self, "shortName")

    @short_name.setter
    def short_name(self, value: typing.Optional[str]):
        return jsii.set(self, "shortName", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-directoryservice.CfnSimpleAD.VpcSettingsProperty", jsii_struct_bases=[], name_mapping={'subnet_ids': 'subnetIds', 'vpc_id': 'vpcId'})
    class VpcSettingsProperty():
        def __init__(self, *, subnet_ids: typing.List[str], vpc_id: str):
            """
            :param subnet_ids: ``CfnSimpleAD.VpcSettingsProperty.SubnetIds``.
            :param vpc_id: ``CfnSimpleAD.VpcSettingsProperty.VpcId``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-directoryservice-simplead-vpcsettings.html
            """
            self._values = {
                'subnet_ids': subnet_ids,
                'vpc_id': vpc_id,
            }

        @property
        def subnet_ids(self) -> typing.List[str]:
            """``CfnSimpleAD.VpcSettingsProperty.SubnetIds``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-directoryservice-simplead-vpcsettings.html#cfn-directoryservice-simplead-vpcsettings-subnetids
            """
            return self._values.get('subnet_ids')

        @property
        def vpc_id(self) -> str:
            """``CfnSimpleAD.VpcSettingsProperty.VpcId``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-directoryservice-simplead-vpcsettings.html#cfn-directoryservice-simplead-vpcsettings-vpcid
            """
            return self._values.get('vpc_id')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'VpcSettingsProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



@jsii.data_type(jsii_type="@aws-cdk/aws-directoryservice.CfnSimpleADProps", jsii_struct_bases=[], name_mapping={'name': 'name', 'password': 'password', 'size': 'size', 'vpc_settings': 'vpcSettings', 'create_alias': 'createAlias', 'description': 'description', 'enable_sso': 'enableSso', 'short_name': 'shortName'})
class CfnSimpleADProps():
    def __init__(self, *, name: str, password: str, size: str, vpc_settings: typing.Union[aws_cdk.core.IResolvable, "CfnSimpleAD.VpcSettingsProperty"], create_alias: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, description: typing.Optional[str]=None, enable_sso: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, short_name: typing.Optional[str]=None):
        """Properties for defining a ``AWS::DirectoryService::SimpleAD``.

        :param name: ``AWS::DirectoryService::SimpleAD.Name``.
        :param password: ``AWS::DirectoryService::SimpleAD.Password``.
        :param size: ``AWS::DirectoryService::SimpleAD.Size``.
        :param vpc_settings: ``AWS::DirectoryService::SimpleAD.VpcSettings``.
        :param create_alias: ``AWS::DirectoryService::SimpleAD.CreateAlias``.
        :param description: ``AWS::DirectoryService::SimpleAD.Description``.
        :param enable_sso: ``AWS::DirectoryService::SimpleAD.EnableSso``.
        :param short_name: ``AWS::DirectoryService::SimpleAD.ShortName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-directoryservice-simplead.html
        """
        self._values = {
            'name': name,
            'password': password,
            'size': size,
            'vpc_settings': vpc_settings,
        }
        if create_alias is not None: self._values["create_alias"] = create_alias
        if description is not None: self._values["description"] = description
        if enable_sso is not None: self._values["enable_sso"] = enable_sso
        if short_name is not None: self._values["short_name"] = short_name

    @property
    def name(self) -> str:
        """``AWS::DirectoryService::SimpleAD.Name``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-directoryservice-simplead.html#cfn-directoryservice-simplead-name
        """
        return self._values.get('name')

    @property
    def password(self) -> str:
        """``AWS::DirectoryService::SimpleAD.Password``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-directoryservice-simplead.html#cfn-directoryservice-simplead-password
        """
        return self._values.get('password')

    @property
    def size(self) -> str:
        """``AWS::DirectoryService::SimpleAD.Size``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-directoryservice-simplead.html#cfn-directoryservice-simplead-size
        """
        return self._values.get('size')

    @property
    def vpc_settings(self) -> typing.Union[aws_cdk.core.IResolvable, "CfnSimpleAD.VpcSettingsProperty"]:
        """``AWS::DirectoryService::SimpleAD.VpcSettings``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-directoryservice-simplead.html#cfn-directoryservice-simplead-vpcsettings
        """
        return self._values.get('vpc_settings')

    @property
    def create_alias(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::DirectoryService::SimpleAD.CreateAlias``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-directoryservice-simplead.html#cfn-directoryservice-simplead-createalias
        """
        return self._values.get('create_alias')

    @property
    def description(self) -> typing.Optional[str]:
        """``AWS::DirectoryService::SimpleAD.Description``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-directoryservice-simplead.html#cfn-directoryservice-simplead-description
        """
        return self._values.get('description')

    @property
    def enable_sso(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::DirectoryService::SimpleAD.EnableSso``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-directoryservice-simplead.html#cfn-directoryservice-simplead-enablesso
        """
        return self._values.get('enable_sso')

    @property
    def short_name(self) -> typing.Optional[str]:
        """``AWS::DirectoryService::SimpleAD.ShortName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-directoryservice-simplead.html#cfn-directoryservice-simplead-shortname
        """
        return self._values.get('short_name')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnSimpleADProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


__all__ = ["CfnMicrosoftAD", "CfnMicrosoftADProps", "CfnSimpleAD", "CfnSimpleADProps", "__jsii_assembly__"]

publication.publish()
