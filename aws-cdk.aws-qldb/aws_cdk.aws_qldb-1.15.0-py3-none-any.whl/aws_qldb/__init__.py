import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.core
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-qldb", "1.15.0", __name__, "aws-qldb@1.15.0.jsii.tgz")
class CfnLedger(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-qldb.CfnLedger"):
    """A CloudFormation ``AWS::QLDB::Ledger``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-qldb-ledger.html
    cloudformationResource:
    :cloudformationResource:: AWS::QLDB::Ledger
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, permissions_mode: str, deletion_protection: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, name: typing.Optional[str]=None, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None) -> None:
        """Create a new ``AWS::QLDB::Ledger``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param permissions_mode: ``AWS::QLDB::Ledger.PermissionsMode``.
        :param deletion_protection: ``AWS::QLDB::Ledger.DeletionProtection``.
        :param name: ``AWS::QLDB::Ledger.Name``.
        :param tags: ``AWS::QLDB::Ledger.Tags``.
        """
        props = CfnLedgerProps(permissions_mode=permissions_mode, deletion_protection=deletion_protection, name=name, tags=tags)

        jsii.create(CfnLedger, self, [scope, id, props])

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
        """``AWS::QLDB::Ledger.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-qldb-ledger.html#cfn-qldb-ledger-tags
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="permissionsMode")
    def permissions_mode(self) -> str:
        """``AWS::QLDB::Ledger.PermissionsMode``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-qldb-ledger.html#cfn-qldb-ledger-permissionsmode
        """
        return jsii.get(self, "permissionsMode")

    @permissions_mode.setter
    def permissions_mode(self, value: str):
        return jsii.set(self, "permissionsMode", value)

    @property
    @jsii.member(jsii_name="deletionProtection")
    def deletion_protection(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::QLDB::Ledger.DeletionProtection``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-qldb-ledger.html#cfn-qldb-ledger-deletionprotection
        """
        return jsii.get(self, "deletionProtection")

    @deletion_protection.setter
    def deletion_protection(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "deletionProtection", value)

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[str]:
        """``AWS::QLDB::Ledger.Name``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-qldb-ledger.html#cfn-qldb-ledger-name
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: typing.Optional[str]):
        return jsii.set(self, "name", value)


@jsii.data_type(jsii_type="@aws-cdk/aws-qldb.CfnLedgerProps", jsii_struct_bases=[], name_mapping={'permissions_mode': 'permissionsMode', 'deletion_protection': 'deletionProtection', 'name': 'name', 'tags': 'tags'})
class CfnLedgerProps():
    def __init__(self, *, permissions_mode: str, deletion_protection: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, name: typing.Optional[str]=None, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None):
        """Properties for defining a ``AWS::QLDB::Ledger``.

        :param permissions_mode: ``AWS::QLDB::Ledger.PermissionsMode``.
        :param deletion_protection: ``AWS::QLDB::Ledger.DeletionProtection``.
        :param name: ``AWS::QLDB::Ledger.Name``.
        :param tags: ``AWS::QLDB::Ledger.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-qldb-ledger.html
        """
        self._values = {
            'permissions_mode': permissions_mode,
        }
        if deletion_protection is not None: self._values["deletion_protection"] = deletion_protection
        if name is not None: self._values["name"] = name
        if tags is not None: self._values["tags"] = tags

    @property
    def permissions_mode(self) -> str:
        """``AWS::QLDB::Ledger.PermissionsMode``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-qldb-ledger.html#cfn-qldb-ledger-permissionsmode
        """
        return self._values.get('permissions_mode')

    @property
    def deletion_protection(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::QLDB::Ledger.DeletionProtection``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-qldb-ledger.html#cfn-qldb-ledger-deletionprotection
        """
        return self._values.get('deletion_protection')

    @property
    def name(self) -> typing.Optional[str]:
        """``AWS::QLDB::Ledger.Name``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-qldb-ledger.html#cfn-qldb-ledger-name
        """
        return self._values.get('name')

    @property
    def tags(self) -> typing.Optional[typing.List[aws_cdk.core.CfnTag]]:
        """``AWS::QLDB::Ledger.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-qldb-ledger.html#cfn-qldb-ledger-tags
        """
        return self._values.get('tags')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnLedgerProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


__all__ = ["CfnLedger", "CfnLedgerProps", "__jsii_assembly__"]

publication.publish()
