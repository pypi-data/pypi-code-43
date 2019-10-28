import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.core
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-securityhub", "1.15.0", __name__, "aws-securityhub@1.15.0.jsii.tgz")
class CfnHub(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-securityhub.CfnHub"):
    """A CloudFormation ``AWS::SecurityHub::Hub``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-securityhub-hub.html
    cloudformationResource:
    :cloudformationResource:: AWS::SecurityHub::Hub
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, tags: typing.Any=None) -> None:
        """Create a new ``AWS::SecurityHub::Hub``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param tags: ``AWS::SecurityHub::Hub.Tags``.
        """
        props = CfnHubProps(tags=tags)

        jsii.create(CfnHub, self, [scope, id, props])

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
        """``AWS::SecurityHub::Hub.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-securityhub-hub.html#cfn-securityhub-hub-tags
        """
        return jsii.get(self, "tags")


@jsii.data_type(jsii_type="@aws-cdk/aws-securityhub.CfnHubProps", jsii_struct_bases=[], name_mapping={'tags': 'tags'})
class CfnHubProps():
    def __init__(self, *, tags: typing.Any=None):
        """Properties for defining a ``AWS::SecurityHub::Hub``.

        :param tags: ``AWS::SecurityHub::Hub.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-securityhub-hub.html
        """
        self._values = {
        }
        if tags is not None: self._values["tags"] = tags

    @property
    def tags(self) -> typing.Any:
        """``AWS::SecurityHub::Hub.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-securityhub-hub.html#cfn-securityhub-hub-tags
        """
        return self._values.get('tags')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnHubProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


__all__ = ["CfnHub", "CfnHubProps", "__jsii_assembly__"]

publication.publish()
