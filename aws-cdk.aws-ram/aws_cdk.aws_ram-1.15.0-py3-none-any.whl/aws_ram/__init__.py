import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.core
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-ram", "1.15.0", __name__, "aws-ram@1.15.0.jsii.tgz")
class CfnResourceShare(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ram.CfnResourceShare"):
    """A CloudFormation ``AWS::RAM::ResourceShare``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ram-resourceshare.html
    cloudformationResource:
    :cloudformationResource:: AWS::RAM::ResourceShare
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, name: str, allow_external_principals: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, principals: typing.Optional[typing.List[str]]=None, resource_arns: typing.Optional[typing.List[str]]=None, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None) -> None:
        """Create a new ``AWS::RAM::ResourceShare``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param name: ``AWS::RAM::ResourceShare.Name``.
        :param allow_external_principals: ``AWS::RAM::ResourceShare.AllowExternalPrincipals``.
        :param principals: ``AWS::RAM::ResourceShare.Principals``.
        :param resource_arns: ``AWS::RAM::ResourceShare.ResourceArns``.
        :param tags: ``AWS::RAM::ResourceShare.Tags``.
        """
        props = CfnResourceShareProps(name=name, allow_external_principals=allow_external_principals, principals=principals, resource_arns=resource_arns, tags=tags)

        jsii.create(CfnResourceShare, self, [scope, id, props])

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
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        """``AWS::RAM::ResourceShare.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ram-resourceshare.html#cfn-ram-resourceshare-tags
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> str:
        """``AWS::RAM::ResourceShare.Name``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ram-resourceshare.html#cfn-ram-resourceshare-name
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: str):
        return jsii.set(self, "name", value)

    @property
    @jsii.member(jsii_name="allowExternalPrincipals")
    def allow_external_principals(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::RAM::ResourceShare.AllowExternalPrincipals``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ram-resourceshare.html#cfn-ram-resourceshare-allowexternalprincipals
        """
        return jsii.get(self, "allowExternalPrincipals")

    @allow_external_principals.setter
    def allow_external_principals(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "allowExternalPrincipals", value)

    @property
    @jsii.member(jsii_name="principals")
    def principals(self) -> typing.Optional[typing.List[str]]:
        """``AWS::RAM::ResourceShare.Principals``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ram-resourceshare.html#cfn-ram-resourceshare-principals
        """
        return jsii.get(self, "principals")

    @principals.setter
    def principals(self, value: typing.Optional[typing.List[str]]):
        return jsii.set(self, "principals", value)

    @property
    @jsii.member(jsii_name="resourceArns")
    def resource_arns(self) -> typing.Optional[typing.List[str]]:
        """``AWS::RAM::ResourceShare.ResourceArns``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ram-resourceshare.html#cfn-ram-resourceshare-resourcearns
        """
        return jsii.get(self, "resourceArns")

    @resource_arns.setter
    def resource_arns(self, value: typing.Optional[typing.List[str]]):
        return jsii.set(self, "resourceArns", value)


@jsii.data_type(jsii_type="@aws-cdk/aws-ram.CfnResourceShareProps", jsii_struct_bases=[], name_mapping={'name': 'name', 'allow_external_principals': 'allowExternalPrincipals', 'principals': 'principals', 'resource_arns': 'resourceArns', 'tags': 'tags'})
class CfnResourceShareProps():
    def __init__(self, *, name: str, allow_external_principals: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, principals: typing.Optional[typing.List[str]]=None, resource_arns: typing.Optional[typing.List[str]]=None, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None):
        """Properties for defining a ``AWS::RAM::ResourceShare``.

        :param name: ``AWS::RAM::ResourceShare.Name``.
        :param allow_external_principals: ``AWS::RAM::ResourceShare.AllowExternalPrincipals``.
        :param principals: ``AWS::RAM::ResourceShare.Principals``.
        :param resource_arns: ``AWS::RAM::ResourceShare.ResourceArns``.
        :param tags: ``AWS::RAM::ResourceShare.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ram-resourceshare.html
        """
        self._values = {
            'name': name,
        }
        if allow_external_principals is not None: self._values["allow_external_principals"] = allow_external_principals
        if principals is not None: self._values["principals"] = principals
        if resource_arns is not None: self._values["resource_arns"] = resource_arns
        if tags is not None: self._values["tags"] = tags

    @property
    def name(self) -> str:
        """``AWS::RAM::ResourceShare.Name``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ram-resourceshare.html#cfn-ram-resourceshare-name
        """
        return self._values.get('name')

    @property
    def allow_external_principals(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::RAM::ResourceShare.AllowExternalPrincipals``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ram-resourceshare.html#cfn-ram-resourceshare-allowexternalprincipals
        """
        return self._values.get('allow_external_principals')

    @property
    def principals(self) -> typing.Optional[typing.List[str]]:
        """``AWS::RAM::ResourceShare.Principals``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ram-resourceshare.html#cfn-ram-resourceshare-principals
        """
        return self._values.get('principals')

    @property
    def resource_arns(self) -> typing.Optional[typing.List[str]]:
        """``AWS::RAM::ResourceShare.ResourceArns``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ram-resourceshare.html#cfn-ram-resourceshare-resourcearns
        """
        return self._values.get('resource_arns')

    @property
    def tags(self) -> typing.Optional[typing.List[aws_cdk.core.CfnTag]]:
        """``AWS::RAM::ResourceShare.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ram-resourceshare.html#cfn-ram-resourceshare-tags
        """
        return self._values.get('tags')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnResourceShareProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


__all__ = ["CfnResourceShare", "CfnResourceShareProps", "__jsii_assembly__"]

publication.publish()
