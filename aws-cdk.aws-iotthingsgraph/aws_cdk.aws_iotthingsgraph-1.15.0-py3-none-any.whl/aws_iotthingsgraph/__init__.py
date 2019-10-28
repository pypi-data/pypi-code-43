import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.core
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-iotthingsgraph", "1.15.0", __name__, "aws-iotthingsgraph@1.15.0.jsii.tgz")
class CfnFlowTemplate(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-iotthingsgraph.CfnFlowTemplate"):
    """A CloudFormation ``AWS::IoTThingsGraph::FlowTemplate``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotthingsgraph-flowtemplate.html
    cloudformationResource:
    :cloudformationResource:: AWS::IoTThingsGraph::FlowTemplate
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, definition: typing.Union["DefinitionDocumentProperty", aws_cdk.core.IResolvable], compatible_namespace_version: typing.Optional[jsii.Number]=None) -> None:
        """Create a new ``AWS::IoTThingsGraph::FlowTemplate``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param definition: ``AWS::IoTThingsGraph::FlowTemplate.Definition``.
        :param compatible_namespace_version: ``AWS::IoTThingsGraph::FlowTemplate.CompatibleNamespaceVersion``.
        """
        props = CfnFlowTemplateProps(definition=definition, compatible_namespace_version=compatible_namespace_version)

        jsii.create(CfnFlowTemplate, self, [scope, id, props])

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
    @jsii.member(jsii_name="definition")
    def definition(self) -> typing.Union["DefinitionDocumentProperty", aws_cdk.core.IResolvable]:
        """``AWS::IoTThingsGraph::FlowTemplate.Definition``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotthingsgraph-flowtemplate.html#cfn-iotthingsgraph-flowtemplate-definition
        """
        return jsii.get(self, "definition")

    @definition.setter
    def definition(self, value: typing.Union["DefinitionDocumentProperty", aws_cdk.core.IResolvable]):
        return jsii.set(self, "definition", value)

    @property
    @jsii.member(jsii_name="compatibleNamespaceVersion")
    def compatible_namespace_version(self) -> typing.Optional[jsii.Number]:
        """``AWS::IoTThingsGraph::FlowTemplate.CompatibleNamespaceVersion``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotthingsgraph-flowtemplate.html#cfn-iotthingsgraph-flowtemplate-compatiblenamespaceversion
        """
        return jsii.get(self, "compatibleNamespaceVersion")

    @compatible_namespace_version.setter
    def compatible_namespace_version(self, value: typing.Optional[jsii.Number]):
        return jsii.set(self, "compatibleNamespaceVersion", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-iotthingsgraph.CfnFlowTemplate.DefinitionDocumentProperty", jsii_struct_bases=[], name_mapping={'language': 'language', 'text': 'text'})
    class DefinitionDocumentProperty():
        def __init__(self, *, language: str, text: str):
            """
            :param language: ``CfnFlowTemplate.DefinitionDocumentProperty.Language``.
            :param text: ``CfnFlowTemplate.DefinitionDocumentProperty.Text``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotthingsgraph-flowtemplate-definitiondocument.html
            """
            self._values = {
                'language': language,
                'text': text,
            }

        @property
        def language(self) -> str:
            """``CfnFlowTemplate.DefinitionDocumentProperty.Language``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotthingsgraph-flowtemplate-definitiondocument.html#cfn-iotthingsgraph-flowtemplate-definitiondocument-language
            """
            return self._values.get('language')

        @property
        def text(self) -> str:
            """``CfnFlowTemplate.DefinitionDocumentProperty.Text``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotthingsgraph-flowtemplate-definitiondocument.html#cfn-iotthingsgraph-flowtemplate-definitiondocument-text
            """
            return self._values.get('text')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'DefinitionDocumentProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



@jsii.data_type(jsii_type="@aws-cdk/aws-iotthingsgraph.CfnFlowTemplateProps", jsii_struct_bases=[], name_mapping={'definition': 'definition', 'compatible_namespace_version': 'compatibleNamespaceVersion'})
class CfnFlowTemplateProps():
    def __init__(self, *, definition: typing.Union["CfnFlowTemplate.DefinitionDocumentProperty", aws_cdk.core.IResolvable], compatible_namespace_version: typing.Optional[jsii.Number]=None):
        """Properties for defining a ``AWS::IoTThingsGraph::FlowTemplate``.

        :param definition: ``AWS::IoTThingsGraph::FlowTemplate.Definition``.
        :param compatible_namespace_version: ``AWS::IoTThingsGraph::FlowTemplate.CompatibleNamespaceVersion``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotthingsgraph-flowtemplate.html
        """
        self._values = {
            'definition': definition,
        }
        if compatible_namespace_version is not None: self._values["compatible_namespace_version"] = compatible_namespace_version

    @property
    def definition(self) -> typing.Union["CfnFlowTemplate.DefinitionDocumentProperty", aws_cdk.core.IResolvable]:
        """``AWS::IoTThingsGraph::FlowTemplate.Definition``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotthingsgraph-flowtemplate.html#cfn-iotthingsgraph-flowtemplate-definition
        """
        return self._values.get('definition')

    @property
    def compatible_namespace_version(self) -> typing.Optional[jsii.Number]:
        """``AWS::IoTThingsGraph::FlowTemplate.CompatibleNamespaceVersion``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotthingsgraph-flowtemplate.html#cfn-iotthingsgraph-flowtemplate-compatiblenamespaceversion
        """
        return self._values.get('compatible_namespace_version')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnFlowTemplateProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


__all__ = ["CfnFlowTemplate", "CfnFlowTemplateProps", "__jsii_assembly__"]

publication.publish()
