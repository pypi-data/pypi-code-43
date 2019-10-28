import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.core
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-greengrass", "1.15.0", __name__, "aws-greengrass@1.15.0.jsii.tgz")
class CfnConnectorDefinition(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-greengrass.CfnConnectorDefinition"):
    """A CloudFormation ``AWS::Greengrass::ConnectorDefinition``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-connectordefinition.html
    cloudformationResource:
    :cloudformationResource:: AWS::Greengrass::ConnectorDefinition
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, name: str, initial_version: typing.Optional[typing.Union[typing.Optional["ConnectorDefinitionVersionProperty"], typing.Optional[aws_cdk.core.IResolvable]]]=None, tags: typing.Any=None) -> None:
        """Create a new ``AWS::Greengrass::ConnectorDefinition``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param name: ``AWS::Greengrass::ConnectorDefinition.Name``.
        :param initial_version: ``AWS::Greengrass::ConnectorDefinition.InitialVersion``.
        :param tags: ``AWS::Greengrass::ConnectorDefinition.Tags``.
        """
        props = CfnConnectorDefinitionProps(name=name, initial_version=initial_version, tags=tags)

        jsii.create(CfnConnectorDefinition, self, [scope, id, props])

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
    @jsii.member(jsii_name="attrId")
    def attr_id(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: Id
        """
        return jsii.get(self, "attrId")

    @property
    @jsii.member(jsii_name="attrLatestVersionArn")
    def attr_latest_version_arn(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: LatestVersionArn
        """
        return jsii.get(self, "attrLatestVersionArn")

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
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        """``AWS::Greengrass::ConnectorDefinition.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-connectordefinition.html#cfn-greengrass-connectordefinition-tags
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> str:
        """``AWS::Greengrass::ConnectorDefinition.Name``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-connectordefinition.html#cfn-greengrass-connectordefinition-name
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: str):
        return jsii.set(self, "name", value)

    @property
    @jsii.member(jsii_name="initialVersion")
    def initial_version(self) -> typing.Optional[typing.Union[typing.Optional["ConnectorDefinitionVersionProperty"], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::Greengrass::ConnectorDefinition.InitialVersion``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-connectordefinition.html#cfn-greengrass-connectordefinition-initialversion
        """
        return jsii.get(self, "initialVersion")

    @initial_version.setter
    def initial_version(self, value: typing.Optional[typing.Union[typing.Optional["ConnectorDefinitionVersionProperty"], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "initialVersion", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnConnectorDefinition.ConnectorDefinitionVersionProperty", jsii_struct_bases=[], name_mapping={'connectors': 'connectors'})
    class ConnectorDefinitionVersionProperty():
        def __init__(self, *, connectors: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnConnectorDefinition.ConnectorProperty"]]]):
            """
            :param connectors: ``CfnConnectorDefinition.ConnectorDefinitionVersionProperty.Connectors``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-connectordefinition-connectordefinitionversion.html
            """
            self._values = {
                'connectors': connectors,
            }

        @property
        def connectors(self) -> typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnConnectorDefinition.ConnectorProperty"]]]:
            """``CfnConnectorDefinition.ConnectorDefinitionVersionProperty.Connectors``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-connectordefinition-connectordefinitionversion.html#cfn-greengrass-connectordefinition-connectordefinitionversion-connectors
            """
            return self._values.get('connectors')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'ConnectorDefinitionVersionProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnConnectorDefinition.ConnectorProperty", jsii_struct_bases=[], name_mapping={'connector_arn': 'connectorArn', 'id': 'id', 'parameters': 'parameters'})
    class ConnectorProperty():
        def __init__(self, *, connector_arn: str, id: str, parameters: typing.Any=None):
            """
            :param connector_arn: ``CfnConnectorDefinition.ConnectorProperty.ConnectorArn``.
            :param id: ``CfnConnectorDefinition.ConnectorProperty.Id``.
            :param parameters: ``CfnConnectorDefinition.ConnectorProperty.Parameters``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-connectordefinition-connector.html
            """
            self._values = {
                'connector_arn': connector_arn,
                'id': id,
            }
            if parameters is not None: self._values["parameters"] = parameters

        @property
        def connector_arn(self) -> str:
            """``CfnConnectorDefinition.ConnectorProperty.ConnectorArn``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-connectordefinition-connector.html#cfn-greengrass-connectordefinition-connector-connectorarn
            """
            return self._values.get('connector_arn')

        @property
        def id(self) -> str:
            """``CfnConnectorDefinition.ConnectorProperty.Id``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-connectordefinition-connector.html#cfn-greengrass-connectordefinition-connector-id
            """
            return self._values.get('id')

        @property
        def parameters(self) -> typing.Any:
            """``CfnConnectorDefinition.ConnectorProperty.Parameters``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-connectordefinition-connector.html#cfn-greengrass-connectordefinition-connector-parameters
            """
            return self._values.get('parameters')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'ConnectorProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



@jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnConnectorDefinitionProps", jsii_struct_bases=[], name_mapping={'name': 'name', 'initial_version': 'initialVersion', 'tags': 'tags'})
class CfnConnectorDefinitionProps():
    def __init__(self, *, name: str, initial_version: typing.Optional[typing.Union[typing.Optional["CfnConnectorDefinition.ConnectorDefinitionVersionProperty"], typing.Optional[aws_cdk.core.IResolvable]]]=None, tags: typing.Any=None):
        """Properties for defining a ``AWS::Greengrass::ConnectorDefinition``.

        :param name: ``AWS::Greengrass::ConnectorDefinition.Name``.
        :param initial_version: ``AWS::Greengrass::ConnectorDefinition.InitialVersion``.
        :param tags: ``AWS::Greengrass::ConnectorDefinition.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-connectordefinition.html
        """
        self._values = {
            'name': name,
        }
        if initial_version is not None: self._values["initial_version"] = initial_version
        if tags is not None: self._values["tags"] = tags

    @property
    def name(self) -> str:
        """``AWS::Greengrass::ConnectorDefinition.Name``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-connectordefinition.html#cfn-greengrass-connectordefinition-name
        """
        return self._values.get('name')

    @property
    def initial_version(self) -> typing.Optional[typing.Union[typing.Optional["CfnConnectorDefinition.ConnectorDefinitionVersionProperty"], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::Greengrass::ConnectorDefinition.InitialVersion``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-connectordefinition.html#cfn-greengrass-connectordefinition-initialversion
        """
        return self._values.get('initial_version')

    @property
    def tags(self) -> typing.Any:
        """``AWS::Greengrass::ConnectorDefinition.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-connectordefinition.html#cfn-greengrass-connectordefinition-tags
        """
        return self._values.get('tags')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnConnectorDefinitionProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnConnectorDefinitionVersion(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-greengrass.CfnConnectorDefinitionVersion"):
    """A CloudFormation ``AWS::Greengrass::ConnectorDefinitionVersion``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-connectordefinitionversion.html
    cloudformationResource:
    :cloudformationResource:: AWS::Greengrass::ConnectorDefinitionVersion
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, connector_definition_id: str, connectors: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "ConnectorProperty"]]]) -> None:
        """Create a new ``AWS::Greengrass::ConnectorDefinitionVersion``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param connector_definition_id: ``AWS::Greengrass::ConnectorDefinitionVersion.ConnectorDefinitionId``.
        :param connectors: ``AWS::Greengrass::ConnectorDefinitionVersion.Connectors``.
        """
        props = CfnConnectorDefinitionVersionProps(connector_definition_id=connector_definition_id, connectors=connectors)

        jsii.create(CfnConnectorDefinitionVersion, self, [scope, id, props])

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
    @jsii.member(jsii_name="connectorDefinitionId")
    def connector_definition_id(self) -> str:
        """``AWS::Greengrass::ConnectorDefinitionVersion.ConnectorDefinitionId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-connectordefinitionversion.html#cfn-greengrass-connectordefinitionversion-connectordefinitionid
        """
        return jsii.get(self, "connectorDefinitionId")

    @connector_definition_id.setter
    def connector_definition_id(self, value: str):
        return jsii.set(self, "connectorDefinitionId", value)

    @property
    @jsii.member(jsii_name="connectors")
    def connectors(self) -> typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "ConnectorProperty"]]]:
        """``AWS::Greengrass::ConnectorDefinitionVersion.Connectors``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-connectordefinitionversion.html#cfn-greengrass-connectordefinitionversion-connectors
        """
        return jsii.get(self, "connectors")

    @connectors.setter
    def connectors(self, value: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "ConnectorProperty"]]]):
        return jsii.set(self, "connectors", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnConnectorDefinitionVersion.ConnectorProperty", jsii_struct_bases=[], name_mapping={'connector_arn': 'connectorArn', 'id': 'id', 'parameters': 'parameters'})
    class ConnectorProperty():
        def __init__(self, *, connector_arn: str, id: str, parameters: typing.Any=None):
            """
            :param connector_arn: ``CfnConnectorDefinitionVersion.ConnectorProperty.ConnectorArn``.
            :param id: ``CfnConnectorDefinitionVersion.ConnectorProperty.Id``.
            :param parameters: ``CfnConnectorDefinitionVersion.ConnectorProperty.Parameters``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-connectordefinitionversion-connector.html
            """
            self._values = {
                'connector_arn': connector_arn,
                'id': id,
            }
            if parameters is not None: self._values["parameters"] = parameters

        @property
        def connector_arn(self) -> str:
            """``CfnConnectorDefinitionVersion.ConnectorProperty.ConnectorArn``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-connectordefinitionversion-connector.html#cfn-greengrass-connectordefinitionversion-connector-connectorarn
            """
            return self._values.get('connector_arn')

        @property
        def id(self) -> str:
            """``CfnConnectorDefinitionVersion.ConnectorProperty.Id``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-connectordefinitionversion-connector.html#cfn-greengrass-connectordefinitionversion-connector-id
            """
            return self._values.get('id')

        @property
        def parameters(self) -> typing.Any:
            """``CfnConnectorDefinitionVersion.ConnectorProperty.Parameters``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-connectordefinitionversion-connector.html#cfn-greengrass-connectordefinitionversion-connector-parameters
            """
            return self._values.get('parameters')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'ConnectorProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



@jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnConnectorDefinitionVersionProps", jsii_struct_bases=[], name_mapping={'connector_definition_id': 'connectorDefinitionId', 'connectors': 'connectors'})
class CfnConnectorDefinitionVersionProps():
    def __init__(self, *, connector_definition_id: str, connectors: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnConnectorDefinitionVersion.ConnectorProperty"]]]):
        """Properties for defining a ``AWS::Greengrass::ConnectorDefinitionVersion``.

        :param connector_definition_id: ``AWS::Greengrass::ConnectorDefinitionVersion.ConnectorDefinitionId``.
        :param connectors: ``AWS::Greengrass::ConnectorDefinitionVersion.Connectors``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-connectordefinitionversion.html
        """
        self._values = {
            'connector_definition_id': connector_definition_id,
            'connectors': connectors,
        }

    @property
    def connector_definition_id(self) -> str:
        """``AWS::Greengrass::ConnectorDefinitionVersion.ConnectorDefinitionId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-connectordefinitionversion.html#cfn-greengrass-connectordefinitionversion-connectordefinitionid
        """
        return self._values.get('connector_definition_id')

    @property
    def connectors(self) -> typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnConnectorDefinitionVersion.ConnectorProperty"]]]:
        """``AWS::Greengrass::ConnectorDefinitionVersion.Connectors``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-connectordefinitionversion.html#cfn-greengrass-connectordefinitionversion-connectors
        """
        return self._values.get('connectors')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnConnectorDefinitionVersionProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnCoreDefinition(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-greengrass.CfnCoreDefinition"):
    """A CloudFormation ``AWS::Greengrass::CoreDefinition``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-coredefinition.html
    cloudformationResource:
    :cloudformationResource:: AWS::Greengrass::CoreDefinition
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, name: str, initial_version: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CoreDefinitionVersionProperty"]]]=None, tags: typing.Any=None) -> None:
        """Create a new ``AWS::Greengrass::CoreDefinition``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param name: ``AWS::Greengrass::CoreDefinition.Name``.
        :param initial_version: ``AWS::Greengrass::CoreDefinition.InitialVersion``.
        :param tags: ``AWS::Greengrass::CoreDefinition.Tags``.
        """
        props = CfnCoreDefinitionProps(name=name, initial_version=initial_version, tags=tags)

        jsii.create(CfnCoreDefinition, self, [scope, id, props])

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
    @jsii.member(jsii_name="attrId")
    def attr_id(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: Id
        """
        return jsii.get(self, "attrId")

    @property
    @jsii.member(jsii_name="attrLatestVersionArn")
    def attr_latest_version_arn(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: LatestVersionArn
        """
        return jsii.get(self, "attrLatestVersionArn")

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
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        """``AWS::Greengrass::CoreDefinition.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-coredefinition.html#cfn-greengrass-coredefinition-tags
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> str:
        """``AWS::Greengrass::CoreDefinition.Name``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-coredefinition.html#cfn-greengrass-coredefinition-name
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: str):
        return jsii.set(self, "name", value)

    @property
    @jsii.member(jsii_name="initialVersion")
    def initial_version(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CoreDefinitionVersionProperty"]]]:
        """``AWS::Greengrass::CoreDefinition.InitialVersion``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-coredefinition.html#cfn-greengrass-coredefinition-initialversion
        """
        return jsii.get(self, "initialVersion")

    @initial_version.setter
    def initial_version(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CoreDefinitionVersionProperty"]]]):
        return jsii.set(self, "initialVersion", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnCoreDefinition.CoreDefinitionVersionProperty", jsii_struct_bases=[], name_mapping={'cores': 'cores'})
    class CoreDefinitionVersionProperty():
        def __init__(self, *, cores: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnCoreDefinition.CoreProperty"]]]):
            """
            :param cores: ``CfnCoreDefinition.CoreDefinitionVersionProperty.Cores``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-coredefinition-coredefinitionversion.html
            """
            self._values = {
                'cores': cores,
            }

        @property
        def cores(self) -> typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnCoreDefinition.CoreProperty"]]]:
            """``CfnCoreDefinition.CoreDefinitionVersionProperty.Cores``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-coredefinition-coredefinitionversion.html#cfn-greengrass-coredefinition-coredefinitionversion-cores
            """
            return self._values.get('cores')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'CoreDefinitionVersionProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnCoreDefinition.CoreProperty", jsii_struct_bases=[], name_mapping={'certificate_arn': 'certificateArn', 'id': 'id', 'thing_arn': 'thingArn', 'sync_shadow': 'syncShadow'})
    class CoreProperty():
        def __init__(self, *, certificate_arn: str, id: str, thing_arn: str, sync_shadow: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None):
            """
            :param certificate_arn: ``CfnCoreDefinition.CoreProperty.CertificateArn``.
            :param id: ``CfnCoreDefinition.CoreProperty.Id``.
            :param thing_arn: ``CfnCoreDefinition.CoreProperty.ThingArn``.
            :param sync_shadow: ``CfnCoreDefinition.CoreProperty.SyncShadow``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-coredefinition-core.html
            """
            self._values = {
                'certificate_arn': certificate_arn,
                'id': id,
                'thing_arn': thing_arn,
            }
            if sync_shadow is not None: self._values["sync_shadow"] = sync_shadow

        @property
        def certificate_arn(self) -> str:
            """``CfnCoreDefinition.CoreProperty.CertificateArn``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-coredefinition-core.html#cfn-greengrass-coredefinition-core-certificatearn
            """
            return self._values.get('certificate_arn')

        @property
        def id(self) -> str:
            """``CfnCoreDefinition.CoreProperty.Id``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-coredefinition-core.html#cfn-greengrass-coredefinition-core-id
            """
            return self._values.get('id')

        @property
        def thing_arn(self) -> str:
            """``CfnCoreDefinition.CoreProperty.ThingArn``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-coredefinition-core.html#cfn-greengrass-coredefinition-core-thingarn
            """
            return self._values.get('thing_arn')

        @property
        def sync_shadow(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
            """``CfnCoreDefinition.CoreProperty.SyncShadow``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-coredefinition-core.html#cfn-greengrass-coredefinition-core-syncshadow
            """
            return self._values.get('sync_shadow')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'CoreProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



@jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnCoreDefinitionProps", jsii_struct_bases=[], name_mapping={'name': 'name', 'initial_version': 'initialVersion', 'tags': 'tags'})
class CfnCoreDefinitionProps():
    def __init__(self, *, name: str, initial_version: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnCoreDefinition.CoreDefinitionVersionProperty"]]]=None, tags: typing.Any=None):
        """Properties for defining a ``AWS::Greengrass::CoreDefinition``.

        :param name: ``AWS::Greengrass::CoreDefinition.Name``.
        :param initial_version: ``AWS::Greengrass::CoreDefinition.InitialVersion``.
        :param tags: ``AWS::Greengrass::CoreDefinition.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-coredefinition.html
        """
        self._values = {
            'name': name,
        }
        if initial_version is not None: self._values["initial_version"] = initial_version
        if tags is not None: self._values["tags"] = tags

    @property
    def name(self) -> str:
        """``AWS::Greengrass::CoreDefinition.Name``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-coredefinition.html#cfn-greengrass-coredefinition-name
        """
        return self._values.get('name')

    @property
    def initial_version(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnCoreDefinition.CoreDefinitionVersionProperty"]]]:
        """``AWS::Greengrass::CoreDefinition.InitialVersion``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-coredefinition.html#cfn-greengrass-coredefinition-initialversion
        """
        return self._values.get('initial_version')

    @property
    def tags(self) -> typing.Any:
        """``AWS::Greengrass::CoreDefinition.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-coredefinition.html#cfn-greengrass-coredefinition-tags
        """
        return self._values.get('tags')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnCoreDefinitionProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnCoreDefinitionVersion(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-greengrass.CfnCoreDefinitionVersion"):
    """A CloudFormation ``AWS::Greengrass::CoreDefinitionVersion``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-coredefinitionversion.html
    cloudformationResource:
    :cloudformationResource:: AWS::Greengrass::CoreDefinitionVersion
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, core_definition_id: str, cores: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CoreProperty"]]]) -> None:
        """Create a new ``AWS::Greengrass::CoreDefinitionVersion``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param core_definition_id: ``AWS::Greengrass::CoreDefinitionVersion.CoreDefinitionId``.
        :param cores: ``AWS::Greengrass::CoreDefinitionVersion.Cores``.
        """
        props = CfnCoreDefinitionVersionProps(core_definition_id=core_definition_id, cores=cores)

        jsii.create(CfnCoreDefinitionVersion, self, [scope, id, props])

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
    @jsii.member(jsii_name="coreDefinitionId")
    def core_definition_id(self) -> str:
        """``AWS::Greengrass::CoreDefinitionVersion.CoreDefinitionId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-coredefinitionversion.html#cfn-greengrass-coredefinitionversion-coredefinitionid
        """
        return jsii.get(self, "coreDefinitionId")

    @core_definition_id.setter
    def core_definition_id(self, value: str):
        return jsii.set(self, "coreDefinitionId", value)

    @property
    @jsii.member(jsii_name="cores")
    def cores(self) -> typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CoreProperty"]]]:
        """``AWS::Greengrass::CoreDefinitionVersion.Cores``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-coredefinitionversion.html#cfn-greengrass-coredefinitionversion-cores
        """
        return jsii.get(self, "cores")

    @cores.setter
    def cores(self, value: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CoreProperty"]]]):
        return jsii.set(self, "cores", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnCoreDefinitionVersion.CoreProperty", jsii_struct_bases=[], name_mapping={'certificate_arn': 'certificateArn', 'id': 'id', 'thing_arn': 'thingArn', 'sync_shadow': 'syncShadow'})
    class CoreProperty():
        def __init__(self, *, certificate_arn: str, id: str, thing_arn: str, sync_shadow: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None):
            """
            :param certificate_arn: ``CfnCoreDefinitionVersion.CoreProperty.CertificateArn``.
            :param id: ``CfnCoreDefinitionVersion.CoreProperty.Id``.
            :param thing_arn: ``CfnCoreDefinitionVersion.CoreProperty.ThingArn``.
            :param sync_shadow: ``CfnCoreDefinitionVersion.CoreProperty.SyncShadow``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-coredefinitionversion-core.html
            """
            self._values = {
                'certificate_arn': certificate_arn,
                'id': id,
                'thing_arn': thing_arn,
            }
            if sync_shadow is not None: self._values["sync_shadow"] = sync_shadow

        @property
        def certificate_arn(self) -> str:
            """``CfnCoreDefinitionVersion.CoreProperty.CertificateArn``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-coredefinitionversion-core.html#cfn-greengrass-coredefinitionversion-core-certificatearn
            """
            return self._values.get('certificate_arn')

        @property
        def id(self) -> str:
            """``CfnCoreDefinitionVersion.CoreProperty.Id``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-coredefinitionversion-core.html#cfn-greengrass-coredefinitionversion-core-id
            """
            return self._values.get('id')

        @property
        def thing_arn(self) -> str:
            """``CfnCoreDefinitionVersion.CoreProperty.ThingArn``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-coredefinitionversion-core.html#cfn-greengrass-coredefinitionversion-core-thingarn
            """
            return self._values.get('thing_arn')

        @property
        def sync_shadow(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
            """``CfnCoreDefinitionVersion.CoreProperty.SyncShadow``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-coredefinitionversion-core.html#cfn-greengrass-coredefinitionversion-core-syncshadow
            """
            return self._values.get('sync_shadow')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'CoreProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



@jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnCoreDefinitionVersionProps", jsii_struct_bases=[], name_mapping={'core_definition_id': 'coreDefinitionId', 'cores': 'cores'})
class CfnCoreDefinitionVersionProps():
    def __init__(self, *, core_definition_id: str, cores: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnCoreDefinitionVersion.CoreProperty"]]]):
        """Properties for defining a ``AWS::Greengrass::CoreDefinitionVersion``.

        :param core_definition_id: ``AWS::Greengrass::CoreDefinitionVersion.CoreDefinitionId``.
        :param cores: ``AWS::Greengrass::CoreDefinitionVersion.Cores``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-coredefinitionversion.html
        """
        self._values = {
            'core_definition_id': core_definition_id,
            'cores': cores,
        }

    @property
    def core_definition_id(self) -> str:
        """``AWS::Greengrass::CoreDefinitionVersion.CoreDefinitionId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-coredefinitionversion.html#cfn-greengrass-coredefinitionversion-coredefinitionid
        """
        return self._values.get('core_definition_id')

    @property
    def cores(self) -> typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnCoreDefinitionVersion.CoreProperty"]]]:
        """``AWS::Greengrass::CoreDefinitionVersion.Cores``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-coredefinitionversion.html#cfn-greengrass-coredefinitionversion-cores
        """
        return self._values.get('cores')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnCoreDefinitionVersionProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnDeviceDefinition(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-greengrass.CfnDeviceDefinition"):
    """A CloudFormation ``AWS::Greengrass::DeviceDefinition``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-devicedefinition.html
    cloudformationResource:
    :cloudformationResource:: AWS::Greengrass::DeviceDefinition
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, name: str, initial_version: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["DeviceDefinitionVersionProperty"]]]=None, tags: typing.Any=None) -> None:
        """Create a new ``AWS::Greengrass::DeviceDefinition``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param name: ``AWS::Greengrass::DeviceDefinition.Name``.
        :param initial_version: ``AWS::Greengrass::DeviceDefinition.InitialVersion``.
        :param tags: ``AWS::Greengrass::DeviceDefinition.Tags``.
        """
        props = CfnDeviceDefinitionProps(name=name, initial_version=initial_version, tags=tags)

        jsii.create(CfnDeviceDefinition, self, [scope, id, props])

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
    @jsii.member(jsii_name="attrId")
    def attr_id(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: Id
        """
        return jsii.get(self, "attrId")

    @property
    @jsii.member(jsii_name="attrLatestVersionArn")
    def attr_latest_version_arn(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: LatestVersionArn
        """
        return jsii.get(self, "attrLatestVersionArn")

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
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        """``AWS::Greengrass::DeviceDefinition.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-devicedefinition.html#cfn-greengrass-devicedefinition-tags
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> str:
        """``AWS::Greengrass::DeviceDefinition.Name``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-devicedefinition.html#cfn-greengrass-devicedefinition-name
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: str):
        return jsii.set(self, "name", value)

    @property
    @jsii.member(jsii_name="initialVersion")
    def initial_version(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["DeviceDefinitionVersionProperty"]]]:
        """``AWS::Greengrass::DeviceDefinition.InitialVersion``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-devicedefinition.html#cfn-greengrass-devicedefinition-initialversion
        """
        return jsii.get(self, "initialVersion")

    @initial_version.setter
    def initial_version(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["DeviceDefinitionVersionProperty"]]]):
        return jsii.set(self, "initialVersion", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnDeviceDefinition.DeviceDefinitionVersionProperty", jsii_struct_bases=[], name_mapping={'devices': 'devices'})
    class DeviceDefinitionVersionProperty():
        def __init__(self, *, devices: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnDeviceDefinition.DeviceProperty"]]]):
            """
            :param devices: ``CfnDeviceDefinition.DeviceDefinitionVersionProperty.Devices``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-devicedefinition-devicedefinitionversion.html
            """
            self._values = {
                'devices': devices,
            }

        @property
        def devices(self) -> typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnDeviceDefinition.DeviceProperty"]]]:
            """``CfnDeviceDefinition.DeviceDefinitionVersionProperty.Devices``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-devicedefinition-devicedefinitionversion.html#cfn-greengrass-devicedefinition-devicedefinitionversion-devices
            """
            return self._values.get('devices')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'DeviceDefinitionVersionProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnDeviceDefinition.DeviceProperty", jsii_struct_bases=[], name_mapping={'certificate_arn': 'certificateArn', 'id': 'id', 'thing_arn': 'thingArn', 'sync_shadow': 'syncShadow'})
    class DeviceProperty():
        def __init__(self, *, certificate_arn: str, id: str, thing_arn: str, sync_shadow: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None):
            """
            :param certificate_arn: ``CfnDeviceDefinition.DeviceProperty.CertificateArn``.
            :param id: ``CfnDeviceDefinition.DeviceProperty.Id``.
            :param thing_arn: ``CfnDeviceDefinition.DeviceProperty.ThingArn``.
            :param sync_shadow: ``CfnDeviceDefinition.DeviceProperty.SyncShadow``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-devicedefinition-device.html
            """
            self._values = {
                'certificate_arn': certificate_arn,
                'id': id,
                'thing_arn': thing_arn,
            }
            if sync_shadow is not None: self._values["sync_shadow"] = sync_shadow

        @property
        def certificate_arn(self) -> str:
            """``CfnDeviceDefinition.DeviceProperty.CertificateArn``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-devicedefinition-device.html#cfn-greengrass-devicedefinition-device-certificatearn
            """
            return self._values.get('certificate_arn')

        @property
        def id(self) -> str:
            """``CfnDeviceDefinition.DeviceProperty.Id``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-devicedefinition-device.html#cfn-greengrass-devicedefinition-device-id
            """
            return self._values.get('id')

        @property
        def thing_arn(self) -> str:
            """``CfnDeviceDefinition.DeviceProperty.ThingArn``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-devicedefinition-device.html#cfn-greengrass-devicedefinition-device-thingarn
            """
            return self._values.get('thing_arn')

        @property
        def sync_shadow(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
            """``CfnDeviceDefinition.DeviceProperty.SyncShadow``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-devicedefinition-device.html#cfn-greengrass-devicedefinition-device-syncshadow
            """
            return self._values.get('sync_shadow')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'DeviceProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



@jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnDeviceDefinitionProps", jsii_struct_bases=[], name_mapping={'name': 'name', 'initial_version': 'initialVersion', 'tags': 'tags'})
class CfnDeviceDefinitionProps():
    def __init__(self, *, name: str, initial_version: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnDeviceDefinition.DeviceDefinitionVersionProperty"]]]=None, tags: typing.Any=None):
        """Properties for defining a ``AWS::Greengrass::DeviceDefinition``.

        :param name: ``AWS::Greengrass::DeviceDefinition.Name``.
        :param initial_version: ``AWS::Greengrass::DeviceDefinition.InitialVersion``.
        :param tags: ``AWS::Greengrass::DeviceDefinition.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-devicedefinition.html
        """
        self._values = {
            'name': name,
        }
        if initial_version is not None: self._values["initial_version"] = initial_version
        if tags is not None: self._values["tags"] = tags

    @property
    def name(self) -> str:
        """``AWS::Greengrass::DeviceDefinition.Name``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-devicedefinition.html#cfn-greengrass-devicedefinition-name
        """
        return self._values.get('name')

    @property
    def initial_version(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnDeviceDefinition.DeviceDefinitionVersionProperty"]]]:
        """``AWS::Greengrass::DeviceDefinition.InitialVersion``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-devicedefinition.html#cfn-greengrass-devicedefinition-initialversion
        """
        return self._values.get('initial_version')

    @property
    def tags(self) -> typing.Any:
        """``AWS::Greengrass::DeviceDefinition.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-devicedefinition.html#cfn-greengrass-devicedefinition-tags
        """
        return self._values.get('tags')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnDeviceDefinitionProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnDeviceDefinitionVersion(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-greengrass.CfnDeviceDefinitionVersion"):
    """A CloudFormation ``AWS::Greengrass::DeviceDefinitionVersion``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-devicedefinitionversion.html
    cloudformationResource:
    :cloudformationResource:: AWS::Greengrass::DeviceDefinitionVersion
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, device_definition_id: str, devices: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "DeviceProperty"]]]) -> None:
        """Create a new ``AWS::Greengrass::DeviceDefinitionVersion``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param device_definition_id: ``AWS::Greengrass::DeviceDefinitionVersion.DeviceDefinitionId``.
        :param devices: ``AWS::Greengrass::DeviceDefinitionVersion.Devices``.
        """
        props = CfnDeviceDefinitionVersionProps(device_definition_id=device_definition_id, devices=devices)

        jsii.create(CfnDeviceDefinitionVersion, self, [scope, id, props])

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
    @jsii.member(jsii_name="deviceDefinitionId")
    def device_definition_id(self) -> str:
        """``AWS::Greengrass::DeviceDefinitionVersion.DeviceDefinitionId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-devicedefinitionversion.html#cfn-greengrass-devicedefinitionversion-devicedefinitionid
        """
        return jsii.get(self, "deviceDefinitionId")

    @device_definition_id.setter
    def device_definition_id(self, value: str):
        return jsii.set(self, "deviceDefinitionId", value)

    @property
    @jsii.member(jsii_name="devices")
    def devices(self) -> typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "DeviceProperty"]]]:
        """``AWS::Greengrass::DeviceDefinitionVersion.Devices``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-devicedefinitionversion.html#cfn-greengrass-devicedefinitionversion-devices
        """
        return jsii.get(self, "devices")

    @devices.setter
    def devices(self, value: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "DeviceProperty"]]]):
        return jsii.set(self, "devices", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnDeviceDefinitionVersion.DeviceProperty", jsii_struct_bases=[], name_mapping={'certificate_arn': 'certificateArn', 'id': 'id', 'thing_arn': 'thingArn', 'sync_shadow': 'syncShadow'})
    class DeviceProperty():
        def __init__(self, *, certificate_arn: str, id: str, thing_arn: str, sync_shadow: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None):
            """
            :param certificate_arn: ``CfnDeviceDefinitionVersion.DeviceProperty.CertificateArn``.
            :param id: ``CfnDeviceDefinitionVersion.DeviceProperty.Id``.
            :param thing_arn: ``CfnDeviceDefinitionVersion.DeviceProperty.ThingArn``.
            :param sync_shadow: ``CfnDeviceDefinitionVersion.DeviceProperty.SyncShadow``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-devicedefinitionversion-device.html
            """
            self._values = {
                'certificate_arn': certificate_arn,
                'id': id,
                'thing_arn': thing_arn,
            }
            if sync_shadow is not None: self._values["sync_shadow"] = sync_shadow

        @property
        def certificate_arn(self) -> str:
            """``CfnDeviceDefinitionVersion.DeviceProperty.CertificateArn``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-devicedefinitionversion-device.html#cfn-greengrass-devicedefinitionversion-device-certificatearn
            """
            return self._values.get('certificate_arn')

        @property
        def id(self) -> str:
            """``CfnDeviceDefinitionVersion.DeviceProperty.Id``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-devicedefinitionversion-device.html#cfn-greengrass-devicedefinitionversion-device-id
            """
            return self._values.get('id')

        @property
        def thing_arn(self) -> str:
            """``CfnDeviceDefinitionVersion.DeviceProperty.ThingArn``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-devicedefinitionversion-device.html#cfn-greengrass-devicedefinitionversion-device-thingarn
            """
            return self._values.get('thing_arn')

        @property
        def sync_shadow(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
            """``CfnDeviceDefinitionVersion.DeviceProperty.SyncShadow``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-devicedefinitionversion-device.html#cfn-greengrass-devicedefinitionversion-device-syncshadow
            """
            return self._values.get('sync_shadow')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'DeviceProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



@jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnDeviceDefinitionVersionProps", jsii_struct_bases=[], name_mapping={'device_definition_id': 'deviceDefinitionId', 'devices': 'devices'})
class CfnDeviceDefinitionVersionProps():
    def __init__(self, *, device_definition_id: str, devices: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnDeviceDefinitionVersion.DeviceProperty"]]]):
        """Properties for defining a ``AWS::Greengrass::DeviceDefinitionVersion``.

        :param device_definition_id: ``AWS::Greengrass::DeviceDefinitionVersion.DeviceDefinitionId``.
        :param devices: ``AWS::Greengrass::DeviceDefinitionVersion.Devices``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-devicedefinitionversion.html
        """
        self._values = {
            'device_definition_id': device_definition_id,
            'devices': devices,
        }

    @property
    def device_definition_id(self) -> str:
        """``AWS::Greengrass::DeviceDefinitionVersion.DeviceDefinitionId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-devicedefinitionversion.html#cfn-greengrass-devicedefinitionversion-devicedefinitionid
        """
        return self._values.get('device_definition_id')

    @property
    def devices(self) -> typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnDeviceDefinitionVersion.DeviceProperty"]]]:
        """``AWS::Greengrass::DeviceDefinitionVersion.Devices``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-devicedefinitionversion.html#cfn-greengrass-devicedefinitionversion-devices
        """
        return self._values.get('devices')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnDeviceDefinitionVersionProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnFunctionDefinition(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-greengrass.CfnFunctionDefinition"):
    """A CloudFormation ``AWS::Greengrass::FunctionDefinition``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-functiondefinition.html
    cloudformationResource:
    :cloudformationResource:: AWS::Greengrass::FunctionDefinition
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, name: str, initial_version: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["FunctionDefinitionVersionProperty"]]]=None, tags: typing.Any=None) -> None:
        """Create a new ``AWS::Greengrass::FunctionDefinition``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param name: ``AWS::Greengrass::FunctionDefinition.Name``.
        :param initial_version: ``AWS::Greengrass::FunctionDefinition.InitialVersion``.
        :param tags: ``AWS::Greengrass::FunctionDefinition.Tags``.
        """
        props = CfnFunctionDefinitionProps(name=name, initial_version=initial_version, tags=tags)

        jsii.create(CfnFunctionDefinition, self, [scope, id, props])

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
    @jsii.member(jsii_name="attrId")
    def attr_id(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: Id
        """
        return jsii.get(self, "attrId")

    @property
    @jsii.member(jsii_name="attrLatestVersionArn")
    def attr_latest_version_arn(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: LatestVersionArn
        """
        return jsii.get(self, "attrLatestVersionArn")

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
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        """``AWS::Greengrass::FunctionDefinition.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-functiondefinition.html#cfn-greengrass-functiondefinition-tags
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> str:
        """``AWS::Greengrass::FunctionDefinition.Name``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-functiondefinition.html#cfn-greengrass-functiondefinition-name
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: str):
        return jsii.set(self, "name", value)

    @property
    @jsii.member(jsii_name="initialVersion")
    def initial_version(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["FunctionDefinitionVersionProperty"]]]:
        """``AWS::Greengrass::FunctionDefinition.InitialVersion``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-functiondefinition.html#cfn-greengrass-functiondefinition-initialversion
        """
        return jsii.get(self, "initialVersion")

    @initial_version.setter
    def initial_version(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["FunctionDefinitionVersionProperty"]]]):
        return jsii.set(self, "initialVersion", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnFunctionDefinition.DefaultConfigProperty", jsii_struct_bases=[], name_mapping={'execution': 'execution'})
    class DefaultConfigProperty():
        def __init__(self, *, execution: typing.Union[aws_cdk.core.IResolvable, "CfnFunctionDefinition.ExecutionProperty"]):
            """
            :param execution: ``CfnFunctionDefinition.DefaultConfigProperty.Execution``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-defaultconfig.html
            """
            self._values = {
                'execution': execution,
            }

        @property
        def execution(self) -> typing.Union[aws_cdk.core.IResolvable, "CfnFunctionDefinition.ExecutionProperty"]:
            """``CfnFunctionDefinition.DefaultConfigProperty.Execution``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-defaultconfig.html#cfn-greengrass-functiondefinition-defaultconfig-execution
            """
            return self._values.get('execution')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'DefaultConfigProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnFunctionDefinition.EnvironmentProperty", jsii_struct_bases=[], name_mapping={'access_sysfs': 'accessSysfs', 'execution': 'execution', 'resource_access_policies': 'resourceAccessPolicies', 'variables': 'variables'})
    class EnvironmentProperty():
        def __init__(self, *, access_sysfs: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, execution: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnFunctionDefinition.ExecutionProperty"]]]=None, resource_access_policies: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnFunctionDefinition.ResourceAccessPolicyProperty"]]]]]=None, variables: typing.Any=None):
            """
            :param access_sysfs: ``CfnFunctionDefinition.EnvironmentProperty.AccessSysfs``.
            :param execution: ``CfnFunctionDefinition.EnvironmentProperty.Execution``.
            :param resource_access_policies: ``CfnFunctionDefinition.EnvironmentProperty.ResourceAccessPolicies``.
            :param variables: ``CfnFunctionDefinition.EnvironmentProperty.Variables``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-environment.html
            """
            self._values = {
            }
            if access_sysfs is not None: self._values["access_sysfs"] = access_sysfs
            if execution is not None: self._values["execution"] = execution
            if resource_access_policies is not None: self._values["resource_access_policies"] = resource_access_policies
            if variables is not None: self._values["variables"] = variables

        @property
        def access_sysfs(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
            """``CfnFunctionDefinition.EnvironmentProperty.AccessSysfs``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-environment.html#cfn-greengrass-functiondefinition-environment-accesssysfs
            """
            return self._values.get('access_sysfs')

        @property
        def execution(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnFunctionDefinition.ExecutionProperty"]]]:
            """``CfnFunctionDefinition.EnvironmentProperty.Execution``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-environment.html#cfn-greengrass-functiondefinition-environment-execution
            """
            return self._values.get('execution')

        @property
        def resource_access_policies(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnFunctionDefinition.ResourceAccessPolicyProperty"]]]]]:
            """``CfnFunctionDefinition.EnvironmentProperty.ResourceAccessPolicies``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-environment.html#cfn-greengrass-functiondefinition-environment-resourceaccesspolicies
            """
            return self._values.get('resource_access_policies')

        @property
        def variables(self) -> typing.Any:
            """``CfnFunctionDefinition.EnvironmentProperty.Variables``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-environment.html#cfn-greengrass-functiondefinition-environment-variables
            """
            return self._values.get('variables')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'EnvironmentProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnFunctionDefinition.ExecutionProperty", jsii_struct_bases=[], name_mapping={'isolation_mode': 'isolationMode', 'run_as': 'runAs'})
    class ExecutionProperty():
        def __init__(self, *, isolation_mode: typing.Optional[str]=None, run_as: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnFunctionDefinition.RunAsProperty"]]]=None):
            """
            :param isolation_mode: ``CfnFunctionDefinition.ExecutionProperty.IsolationMode``.
            :param run_as: ``CfnFunctionDefinition.ExecutionProperty.RunAs``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-execution.html
            """
            self._values = {
            }
            if isolation_mode is not None: self._values["isolation_mode"] = isolation_mode
            if run_as is not None: self._values["run_as"] = run_as

        @property
        def isolation_mode(self) -> typing.Optional[str]:
            """``CfnFunctionDefinition.ExecutionProperty.IsolationMode``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-execution.html#cfn-greengrass-functiondefinition-execution-isolationmode
            """
            return self._values.get('isolation_mode')

        @property
        def run_as(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnFunctionDefinition.RunAsProperty"]]]:
            """``CfnFunctionDefinition.ExecutionProperty.RunAs``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-execution.html#cfn-greengrass-functiondefinition-execution-runas
            """
            return self._values.get('run_as')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'ExecutionProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnFunctionDefinition.FunctionConfigurationProperty", jsii_struct_bases=[], name_mapping={'encoding_type': 'encodingType', 'environment': 'environment', 'exec_args': 'execArgs', 'executable': 'executable', 'memory_size': 'memorySize', 'pinned': 'pinned', 'timeout': 'timeout'})
    class FunctionConfigurationProperty():
        def __init__(self, *, encoding_type: typing.Optional[str]=None, environment: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnFunctionDefinition.EnvironmentProperty"]]]=None, exec_args: typing.Optional[str]=None, executable: typing.Optional[str]=None, memory_size: typing.Optional[jsii.Number]=None, pinned: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, timeout: typing.Optional[jsii.Number]=None):
            """
            :param encoding_type: ``CfnFunctionDefinition.FunctionConfigurationProperty.EncodingType``.
            :param environment: ``CfnFunctionDefinition.FunctionConfigurationProperty.Environment``.
            :param exec_args: ``CfnFunctionDefinition.FunctionConfigurationProperty.ExecArgs``.
            :param executable: ``CfnFunctionDefinition.FunctionConfigurationProperty.Executable``.
            :param memory_size: ``CfnFunctionDefinition.FunctionConfigurationProperty.MemorySize``.
            :param pinned: ``CfnFunctionDefinition.FunctionConfigurationProperty.Pinned``.
            :param timeout: ``CfnFunctionDefinition.FunctionConfigurationProperty.Timeout``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-functionconfiguration.html
            """
            self._values = {
            }
            if encoding_type is not None: self._values["encoding_type"] = encoding_type
            if environment is not None: self._values["environment"] = environment
            if exec_args is not None: self._values["exec_args"] = exec_args
            if executable is not None: self._values["executable"] = executable
            if memory_size is not None: self._values["memory_size"] = memory_size
            if pinned is not None: self._values["pinned"] = pinned
            if timeout is not None: self._values["timeout"] = timeout

        @property
        def encoding_type(self) -> typing.Optional[str]:
            """``CfnFunctionDefinition.FunctionConfigurationProperty.EncodingType``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-functionconfiguration.html#cfn-greengrass-functiondefinition-functionconfiguration-encodingtype
            """
            return self._values.get('encoding_type')

        @property
        def environment(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnFunctionDefinition.EnvironmentProperty"]]]:
            """``CfnFunctionDefinition.FunctionConfigurationProperty.Environment``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-functionconfiguration.html#cfn-greengrass-functiondefinition-functionconfiguration-environment
            """
            return self._values.get('environment')

        @property
        def exec_args(self) -> typing.Optional[str]:
            """``CfnFunctionDefinition.FunctionConfigurationProperty.ExecArgs``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-functionconfiguration.html#cfn-greengrass-functiondefinition-functionconfiguration-execargs
            """
            return self._values.get('exec_args')

        @property
        def executable(self) -> typing.Optional[str]:
            """``CfnFunctionDefinition.FunctionConfigurationProperty.Executable``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-functionconfiguration.html#cfn-greengrass-functiondefinition-functionconfiguration-executable
            """
            return self._values.get('executable')

        @property
        def memory_size(self) -> typing.Optional[jsii.Number]:
            """``CfnFunctionDefinition.FunctionConfigurationProperty.MemorySize``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-functionconfiguration.html#cfn-greengrass-functiondefinition-functionconfiguration-memorysize
            """
            return self._values.get('memory_size')

        @property
        def pinned(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
            """``CfnFunctionDefinition.FunctionConfigurationProperty.Pinned``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-functionconfiguration.html#cfn-greengrass-functiondefinition-functionconfiguration-pinned
            """
            return self._values.get('pinned')

        @property
        def timeout(self) -> typing.Optional[jsii.Number]:
            """``CfnFunctionDefinition.FunctionConfigurationProperty.Timeout``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-functionconfiguration.html#cfn-greengrass-functiondefinition-functionconfiguration-timeout
            """
            return self._values.get('timeout')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'FunctionConfigurationProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnFunctionDefinition.FunctionDefinitionVersionProperty", jsii_struct_bases=[], name_mapping={'functions': 'functions', 'default_config': 'defaultConfig'})
    class FunctionDefinitionVersionProperty():
        def __init__(self, *, functions: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnFunctionDefinition.FunctionProperty"]]], default_config: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnFunctionDefinition.DefaultConfigProperty"]]]=None):
            """
            :param functions: ``CfnFunctionDefinition.FunctionDefinitionVersionProperty.Functions``.
            :param default_config: ``CfnFunctionDefinition.FunctionDefinitionVersionProperty.DefaultConfig``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-functiondefinitionversion.html
            """
            self._values = {
                'functions': functions,
            }
            if default_config is not None: self._values["default_config"] = default_config

        @property
        def functions(self) -> typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnFunctionDefinition.FunctionProperty"]]]:
            """``CfnFunctionDefinition.FunctionDefinitionVersionProperty.Functions``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-functiondefinitionversion.html#cfn-greengrass-functiondefinition-functiondefinitionversion-functions
            """
            return self._values.get('functions')

        @property
        def default_config(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnFunctionDefinition.DefaultConfigProperty"]]]:
            """``CfnFunctionDefinition.FunctionDefinitionVersionProperty.DefaultConfig``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-functiondefinitionversion.html#cfn-greengrass-functiondefinition-functiondefinitionversion-defaultconfig
            """
            return self._values.get('default_config')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'FunctionDefinitionVersionProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnFunctionDefinition.FunctionProperty", jsii_struct_bases=[], name_mapping={'function_arn': 'functionArn', 'function_configuration': 'functionConfiguration', 'id': 'id'})
    class FunctionProperty():
        def __init__(self, *, function_arn: str, function_configuration: typing.Union[aws_cdk.core.IResolvable, "CfnFunctionDefinition.FunctionConfigurationProperty"], id: str):
            """
            :param function_arn: ``CfnFunctionDefinition.FunctionProperty.FunctionArn``.
            :param function_configuration: ``CfnFunctionDefinition.FunctionProperty.FunctionConfiguration``.
            :param id: ``CfnFunctionDefinition.FunctionProperty.Id``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-function.html
            """
            self._values = {
                'function_arn': function_arn,
                'function_configuration': function_configuration,
                'id': id,
            }

        @property
        def function_arn(self) -> str:
            """``CfnFunctionDefinition.FunctionProperty.FunctionArn``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-function.html#cfn-greengrass-functiondefinition-function-functionarn
            """
            return self._values.get('function_arn')

        @property
        def function_configuration(self) -> typing.Union[aws_cdk.core.IResolvable, "CfnFunctionDefinition.FunctionConfigurationProperty"]:
            """``CfnFunctionDefinition.FunctionProperty.FunctionConfiguration``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-function.html#cfn-greengrass-functiondefinition-function-functionconfiguration
            """
            return self._values.get('function_configuration')

        @property
        def id(self) -> str:
            """``CfnFunctionDefinition.FunctionProperty.Id``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-function.html#cfn-greengrass-functiondefinition-function-id
            """
            return self._values.get('id')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'FunctionProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnFunctionDefinition.ResourceAccessPolicyProperty", jsii_struct_bases=[], name_mapping={'resource_id': 'resourceId', 'permission': 'permission'})
    class ResourceAccessPolicyProperty():
        def __init__(self, *, resource_id: str, permission: typing.Optional[str]=None):
            """
            :param resource_id: ``CfnFunctionDefinition.ResourceAccessPolicyProperty.ResourceId``.
            :param permission: ``CfnFunctionDefinition.ResourceAccessPolicyProperty.Permission``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-resourceaccesspolicy.html
            """
            self._values = {
                'resource_id': resource_id,
            }
            if permission is not None: self._values["permission"] = permission

        @property
        def resource_id(self) -> str:
            """``CfnFunctionDefinition.ResourceAccessPolicyProperty.ResourceId``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-resourceaccesspolicy.html#cfn-greengrass-functiondefinition-resourceaccesspolicy-resourceid
            """
            return self._values.get('resource_id')

        @property
        def permission(self) -> typing.Optional[str]:
            """``CfnFunctionDefinition.ResourceAccessPolicyProperty.Permission``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-resourceaccesspolicy.html#cfn-greengrass-functiondefinition-resourceaccesspolicy-permission
            """
            return self._values.get('permission')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'ResourceAccessPolicyProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnFunctionDefinition.RunAsProperty", jsii_struct_bases=[], name_mapping={'gid': 'gid', 'uid': 'uid'})
    class RunAsProperty():
        def __init__(self, *, gid: typing.Optional[jsii.Number]=None, uid: typing.Optional[jsii.Number]=None):
            """
            :param gid: ``CfnFunctionDefinition.RunAsProperty.Gid``.
            :param uid: ``CfnFunctionDefinition.RunAsProperty.Uid``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-runas.html
            """
            self._values = {
            }
            if gid is not None: self._values["gid"] = gid
            if uid is not None: self._values["uid"] = uid

        @property
        def gid(self) -> typing.Optional[jsii.Number]:
            """``CfnFunctionDefinition.RunAsProperty.Gid``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-runas.html#cfn-greengrass-functiondefinition-runas-gid
            """
            return self._values.get('gid')

        @property
        def uid(self) -> typing.Optional[jsii.Number]:
            """``CfnFunctionDefinition.RunAsProperty.Uid``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-runas.html#cfn-greengrass-functiondefinition-runas-uid
            """
            return self._values.get('uid')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'RunAsProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



@jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnFunctionDefinitionProps", jsii_struct_bases=[], name_mapping={'name': 'name', 'initial_version': 'initialVersion', 'tags': 'tags'})
class CfnFunctionDefinitionProps():
    def __init__(self, *, name: str, initial_version: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnFunctionDefinition.FunctionDefinitionVersionProperty"]]]=None, tags: typing.Any=None):
        """Properties for defining a ``AWS::Greengrass::FunctionDefinition``.

        :param name: ``AWS::Greengrass::FunctionDefinition.Name``.
        :param initial_version: ``AWS::Greengrass::FunctionDefinition.InitialVersion``.
        :param tags: ``AWS::Greengrass::FunctionDefinition.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-functiondefinition.html
        """
        self._values = {
            'name': name,
        }
        if initial_version is not None: self._values["initial_version"] = initial_version
        if tags is not None: self._values["tags"] = tags

    @property
    def name(self) -> str:
        """``AWS::Greengrass::FunctionDefinition.Name``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-functiondefinition.html#cfn-greengrass-functiondefinition-name
        """
        return self._values.get('name')

    @property
    def initial_version(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnFunctionDefinition.FunctionDefinitionVersionProperty"]]]:
        """``AWS::Greengrass::FunctionDefinition.InitialVersion``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-functiondefinition.html#cfn-greengrass-functiondefinition-initialversion
        """
        return self._values.get('initial_version')

    @property
    def tags(self) -> typing.Any:
        """``AWS::Greengrass::FunctionDefinition.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-functiondefinition.html#cfn-greengrass-functiondefinition-tags
        """
        return self._values.get('tags')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnFunctionDefinitionProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnFunctionDefinitionVersion(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-greengrass.CfnFunctionDefinitionVersion"):
    """A CloudFormation ``AWS::Greengrass::FunctionDefinitionVersion``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-functiondefinitionversion.html
    cloudformationResource:
    :cloudformationResource:: AWS::Greengrass::FunctionDefinitionVersion
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, function_definition_id: str, functions: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "FunctionProperty"]]], default_config: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["DefaultConfigProperty"]]]=None) -> None:
        """Create a new ``AWS::Greengrass::FunctionDefinitionVersion``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param function_definition_id: ``AWS::Greengrass::FunctionDefinitionVersion.FunctionDefinitionId``.
        :param functions: ``AWS::Greengrass::FunctionDefinitionVersion.Functions``.
        :param default_config: ``AWS::Greengrass::FunctionDefinitionVersion.DefaultConfig``.
        """
        props = CfnFunctionDefinitionVersionProps(function_definition_id=function_definition_id, functions=functions, default_config=default_config)

        jsii.create(CfnFunctionDefinitionVersion, self, [scope, id, props])

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
    @jsii.member(jsii_name="functionDefinitionId")
    def function_definition_id(self) -> str:
        """``AWS::Greengrass::FunctionDefinitionVersion.FunctionDefinitionId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-functiondefinitionversion.html#cfn-greengrass-functiondefinitionversion-functiondefinitionid
        """
        return jsii.get(self, "functionDefinitionId")

    @function_definition_id.setter
    def function_definition_id(self, value: str):
        return jsii.set(self, "functionDefinitionId", value)

    @property
    @jsii.member(jsii_name="functions")
    def functions(self) -> typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "FunctionProperty"]]]:
        """``AWS::Greengrass::FunctionDefinitionVersion.Functions``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-functiondefinitionversion.html#cfn-greengrass-functiondefinitionversion-functions
        """
        return jsii.get(self, "functions")

    @functions.setter
    def functions(self, value: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "FunctionProperty"]]]):
        return jsii.set(self, "functions", value)

    @property
    @jsii.member(jsii_name="defaultConfig")
    def default_config(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["DefaultConfigProperty"]]]:
        """``AWS::Greengrass::FunctionDefinitionVersion.DefaultConfig``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-functiondefinitionversion.html#cfn-greengrass-functiondefinitionversion-defaultconfig
        """
        return jsii.get(self, "defaultConfig")

    @default_config.setter
    def default_config(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["DefaultConfigProperty"]]]):
        return jsii.set(self, "defaultConfig", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnFunctionDefinitionVersion.DefaultConfigProperty", jsii_struct_bases=[], name_mapping={'execution': 'execution'})
    class DefaultConfigProperty():
        def __init__(self, *, execution: typing.Union[aws_cdk.core.IResolvable, "CfnFunctionDefinitionVersion.ExecutionProperty"]):
            """
            :param execution: ``CfnFunctionDefinitionVersion.DefaultConfigProperty.Execution``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-defaultconfig.html
            """
            self._values = {
                'execution': execution,
            }

        @property
        def execution(self) -> typing.Union[aws_cdk.core.IResolvable, "CfnFunctionDefinitionVersion.ExecutionProperty"]:
            """``CfnFunctionDefinitionVersion.DefaultConfigProperty.Execution``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-defaultconfig.html#cfn-greengrass-functiondefinitionversion-defaultconfig-execution
            """
            return self._values.get('execution')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'DefaultConfigProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnFunctionDefinitionVersion.EnvironmentProperty", jsii_struct_bases=[], name_mapping={'access_sysfs': 'accessSysfs', 'execution': 'execution', 'resource_access_policies': 'resourceAccessPolicies', 'variables': 'variables'})
    class EnvironmentProperty():
        def __init__(self, *, access_sysfs: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, execution: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnFunctionDefinitionVersion.ExecutionProperty"]]]=None, resource_access_policies: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnFunctionDefinitionVersion.ResourceAccessPolicyProperty"]]]]]=None, variables: typing.Any=None):
            """
            :param access_sysfs: ``CfnFunctionDefinitionVersion.EnvironmentProperty.AccessSysfs``.
            :param execution: ``CfnFunctionDefinitionVersion.EnvironmentProperty.Execution``.
            :param resource_access_policies: ``CfnFunctionDefinitionVersion.EnvironmentProperty.ResourceAccessPolicies``.
            :param variables: ``CfnFunctionDefinitionVersion.EnvironmentProperty.Variables``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-environment.html
            """
            self._values = {
            }
            if access_sysfs is not None: self._values["access_sysfs"] = access_sysfs
            if execution is not None: self._values["execution"] = execution
            if resource_access_policies is not None: self._values["resource_access_policies"] = resource_access_policies
            if variables is not None: self._values["variables"] = variables

        @property
        def access_sysfs(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
            """``CfnFunctionDefinitionVersion.EnvironmentProperty.AccessSysfs``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-environment.html#cfn-greengrass-functiondefinitionversion-environment-accesssysfs
            """
            return self._values.get('access_sysfs')

        @property
        def execution(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnFunctionDefinitionVersion.ExecutionProperty"]]]:
            """``CfnFunctionDefinitionVersion.EnvironmentProperty.Execution``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-environment.html#cfn-greengrass-functiondefinitionversion-environment-execution
            """
            return self._values.get('execution')

        @property
        def resource_access_policies(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnFunctionDefinitionVersion.ResourceAccessPolicyProperty"]]]]]:
            """``CfnFunctionDefinitionVersion.EnvironmentProperty.ResourceAccessPolicies``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-environment.html#cfn-greengrass-functiondefinitionversion-environment-resourceaccesspolicies
            """
            return self._values.get('resource_access_policies')

        @property
        def variables(self) -> typing.Any:
            """``CfnFunctionDefinitionVersion.EnvironmentProperty.Variables``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-environment.html#cfn-greengrass-functiondefinitionversion-environment-variables
            """
            return self._values.get('variables')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'EnvironmentProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnFunctionDefinitionVersion.ExecutionProperty", jsii_struct_bases=[], name_mapping={'isolation_mode': 'isolationMode', 'run_as': 'runAs'})
    class ExecutionProperty():
        def __init__(self, *, isolation_mode: typing.Optional[str]=None, run_as: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnFunctionDefinitionVersion.RunAsProperty"]]]=None):
            """
            :param isolation_mode: ``CfnFunctionDefinitionVersion.ExecutionProperty.IsolationMode``.
            :param run_as: ``CfnFunctionDefinitionVersion.ExecutionProperty.RunAs``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-execution.html
            """
            self._values = {
            }
            if isolation_mode is not None: self._values["isolation_mode"] = isolation_mode
            if run_as is not None: self._values["run_as"] = run_as

        @property
        def isolation_mode(self) -> typing.Optional[str]:
            """``CfnFunctionDefinitionVersion.ExecutionProperty.IsolationMode``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-execution.html#cfn-greengrass-functiondefinitionversion-execution-isolationmode
            """
            return self._values.get('isolation_mode')

        @property
        def run_as(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnFunctionDefinitionVersion.RunAsProperty"]]]:
            """``CfnFunctionDefinitionVersion.ExecutionProperty.RunAs``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-execution.html#cfn-greengrass-functiondefinitionversion-execution-runas
            """
            return self._values.get('run_as')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'ExecutionProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnFunctionDefinitionVersion.FunctionConfigurationProperty", jsii_struct_bases=[], name_mapping={'encoding_type': 'encodingType', 'environment': 'environment', 'exec_args': 'execArgs', 'executable': 'executable', 'memory_size': 'memorySize', 'pinned': 'pinned', 'timeout': 'timeout'})
    class FunctionConfigurationProperty():
        def __init__(self, *, encoding_type: typing.Optional[str]=None, environment: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnFunctionDefinitionVersion.EnvironmentProperty"]]]=None, exec_args: typing.Optional[str]=None, executable: typing.Optional[str]=None, memory_size: typing.Optional[jsii.Number]=None, pinned: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, timeout: typing.Optional[jsii.Number]=None):
            """
            :param encoding_type: ``CfnFunctionDefinitionVersion.FunctionConfigurationProperty.EncodingType``.
            :param environment: ``CfnFunctionDefinitionVersion.FunctionConfigurationProperty.Environment``.
            :param exec_args: ``CfnFunctionDefinitionVersion.FunctionConfigurationProperty.ExecArgs``.
            :param executable: ``CfnFunctionDefinitionVersion.FunctionConfigurationProperty.Executable``.
            :param memory_size: ``CfnFunctionDefinitionVersion.FunctionConfigurationProperty.MemorySize``.
            :param pinned: ``CfnFunctionDefinitionVersion.FunctionConfigurationProperty.Pinned``.
            :param timeout: ``CfnFunctionDefinitionVersion.FunctionConfigurationProperty.Timeout``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-functionconfiguration.html
            """
            self._values = {
            }
            if encoding_type is not None: self._values["encoding_type"] = encoding_type
            if environment is not None: self._values["environment"] = environment
            if exec_args is not None: self._values["exec_args"] = exec_args
            if executable is not None: self._values["executable"] = executable
            if memory_size is not None: self._values["memory_size"] = memory_size
            if pinned is not None: self._values["pinned"] = pinned
            if timeout is not None: self._values["timeout"] = timeout

        @property
        def encoding_type(self) -> typing.Optional[str]:
            """``CfnFunctionDefinitionVersion.FunctionConfigurationProperty.EncodingType``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-functionconfiguration.html#cfn-greengrass-functiondefinitionversion-functionconfiguration-encodingtype
            """
            return self._values.get('encoding_type')

        @property
        def environment(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnFunctionDefinitionVersion.EnvironmentProperty"]]]:
            """``CfnFunctionDefinitionVersion.FunctionConfigurationProperty.Environment``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-functionconfiguration.html#cfn-greengrass-functiondefinitionversion-functionconfiguration-environment
            """
            return self._values.get('environment')

        @property
        def exec_args(self) -> typing.Optional[str]:
            """``CfnFunctionDefinitionVersion.FunctionConfigurationProperty.ExecArgs``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-functionconfiguration.html#cfn-greengrass-functiondefinitionversion-functionconfiguration-execargs
            """
            return self._values.get('exec_args')

        @property
        def executable(self) -> typing.Optional[str]:
            """``CfnFunctionDefinitionVersion.FunctionConfigurationProperty.Executable``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-functionconfiguration.html#cfn-greengrass-functiondefinitionversion-functionconfiguration-executable
            """
            return self._values.get('executable')

        @property
        def memory_size(self) -> typing.Optional[jsii.Number]:
            """``CfnFunctionDefinitionVersion.FunctionConfigurationProperty.MemorySize``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-functionconfiguration.html#cfn-greengrass-functiondefinitionversion-functionconfiguration-memorysize
            """
            return self._values.get('memory_size')

        @property
        def pinned(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
            """``CfnFunctionDefinitionVersion.FunctionConfigurationProperty.Pinned``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-functionconfiguration.html#cfn-greengrass-functiondefinitionversion-functionconfiguration-pinned
            """
            return self._values.get('pinned')

        @property
        def timeout(self) -> typing.Optional[jsii.Number]:
            """``CfnFunctionDefinitionVersion.FunctionConfigurationProperty.Timeout``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-functionconfiguration.html#cfn-greengrass-functiondefinitionversion-functionconfiguration-timeout
            """
            return self._values.get('timeout')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'FunctionConfigurationProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnFunctionDefinitionVersion.FunctionProperty", jsii_struct_bases=[], name_mapping={'function_arn': 'functionArn', 'function_configuration': 'functionConfiguration', 'id': 'id'})
    class FunctionProperty():
        def __init__(self, *, function_arn: str, function_configuration: typing.Union[aws_cdk.core.IResolvable, "CfnFunctionDefinitionVersion.FunctionConfigurationProperty"], id: str):
            """
            :param function_arn: ``CfnFunctionDefinitionVersion.FunctionProperty.FunctionArn``.
            :param function_configuration: ``CfnFunctionDefinitionVersion.FunctionProperty.FunctionConfiguration``.
            :param id: ``CfnFunctionDefinitionVersion.FunctionProperty.Id``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-function.html
            """
            self._values = {
                'function_arn': function_arn,
                'function_configuration': function_configuration,
                'id': id,
            }

        @property
        def function_arn(self) -> str:
            """``CfnFunctionDefinitionVersion.FunctionProperty.FunctionArn``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-function.html#cfn-greengrass-functiondefinitionversion-function-functionarn
            """
            return self._values.get('function_arn')

        @property
        def function_configuration(self) -> typing.Union[aws_cdk.core.IResolvable, "CfnFunctionDefinitionVersion.FunctionConfigurationProperty"]:
            """``CfnFunctionDefinitionVersion.FunctionProperty.FunctionConfiguration``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-function.html#cfn-greengrass-functiondefinitionversion-function-functionconfiguration
            """
            return self._values.get('function_configuration')

        @property
        def id(self) -> str:
            """``CfnFunctionDefinitionVersion.FunctionProperty.Id``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-function.html#cfn-greengrass-functiondefinitionversion-function-id
            """
            return self._values.get('id')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'FunctionProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnFunctionDefinitionVersion.ResourceAccessPolicyProperty", jsii_struct_bases=[], name_mapping={'resource_id': 'resourceId', 'permission': 'permission'})
    class ResourceAccessPolicyProperty():
        def __init__(self, *, resource_id: str, permission: typing.Optional[str]=None):
            """
            :param resource_id: ``CfnFunctionDefinitionVersion.ResourceAccessPolicyProperty.ResourceId``.
            :param permission: ``CfnFunctionDefinitionVersion.ResourceAccessPolicyProperty.Permission``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-resourceaccesspolicy.html
            """
            self._values = {
                'resource_id': resource_id,
            }
            if permission is not None: self._values["permission"] = permission

        @property
        def resource_id(self) -> str:
            """``CfnFunctionDefinitionVersion.ResourceAccessPolicyProperty.ResourceId``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-resourceaccesspolicy.html#cfn-greengrass-functiondefinitionversion-resourceaccesspolicy-resourceid
            """
            return self._values.get('resource_id')

        @property
        def permission(self) -> typing.Optional[str]:
            """``CfnFunctionDefinitionVersion.ResourceAccessPolicyProperty.Permission``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-resourceaccesspolicy.html#cfn-greengrass-functiondefinitionversion-resourceaccesspolicy-permission
            """
            return self._values.get('permission')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'ResourceAccessPolicyProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnFunctionDefinitionVersion.RunAsProperty", jsii_struct_bases=[], name_mapping={'gid': 'gid', 'uid': 'uid'})
    class RunAsProperty():
        def __init__(self, *, gid: typing.Optional[jsii.Number]=None, uid: typing.Optional[jsii.Number]=None):
            """
            :param gid: ``CfnFunctionDefinitionVersion.RunAsProperty.Gid``.
            :param uid: ``CfnFunctionDefinitionVersion.RunAsProperty.Uid``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-runas.html
            """
            self._values = {
            }
            if gid is not None: self._values["gid"] = gid
            if uid is not None: self._values["uid"] = uid

        @property
        def gid(self) -> typing.Optional[jsii.Number]:
            """``CfnFunctionDefinitionVersion.RunAsProperty.Gid``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-runas.html#cfn-greengrass-functiondefinitionversion-runas-gid
            """
            return self._values.get('gid')

        @property
        def uid(self) -> typing.Optional[jsii.Number]:
            """``CfnFunctionDefinitionVersion.RunAsProperty.Uid``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-runas.html#cfn-greengrass-functiondefinitionversion-runas-uid
            """
            return self._values.get('uid')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'RunAsProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



@jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnFunctionDefinitionVersionProps", jsii_struct_bases=[], name_mapping={'function_definition_id': 'functionDefinitionId', 'functions': 'functions', 'default_config': 'defaultConfig'})
class CfnFunctionDefinitionVersionProps():
    def __init__(self, *, function_definition_id: str, functions: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnFunctionDefinitionVersion.FunctionProperty"]]], default_config: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnFunctionDefinitionVersion.DefaultConfigProperty"]]]=None):
        """Properties for defining a ``AWS::Greengrass::FunctionDefinitionVersion``.

        :param function_definition_id: ``AWS::Greengrass::FunctionDefinitionVersion.FunctionDefinitionId``.
        :param functions: ``AWS::Greengrass::FunctionDefinitionVersion.Functions``.
        :param default_config: ``AWS::Greengrass::FunctionDefinitionVersion.DefaultConfig``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-functiondefinitionversion.html
        """
        self._values = {
            'function_definition_id': function_definition_id,
            'functions': functions,
        }
        if default_config is not None: self._values["default_config"] = default_config

    @property
    def function_definition_id(self) -> str:
        """``AWS::Greengrass::FunctionDefinitionVersion.FunctionDefinitionId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-functiondefinitionversion.html#cfn-greengrass-functiondefinitionversion-functiondefinitionid
        """
        return self._values.get('function_definition_id')

    @property
    def functions(self) -> typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnFunctionDefinitionVersion.FunctionProperty"]]]:
        """``AWS::Greengrass::FunctionDefinitionVersion.Functions``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-functiondefinitionversion.html#cfn-greengrass-functiondefinitionversion-functions
        """
        return self._values.get('functions')

    @property
    def default_config(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnFunctionDefinitionVersion.DefaultConfigProperty"]]]:
        """``AWS::Greengrass::FunctionDefinitionVersion.DefaultConfig``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-functiondefinitionversion.html#cfn-greengrass-functiondefinitionversion-defaultconfig
        """
        return self._values.get('default_config')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnFunctionDefinitionVersionProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnGroup(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-greengrass.CfnGroup"):
    """A CloudFormation ``AWS::Greengrass::Group``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-group.html
    cloudformationResource:
    :cloudformationResource:: AWS::Greengrass::Group
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, name: str, initial_version: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["GroupVersionProperty"]]]=None, role_arn: typing.Optional[str]=None, tags: typing.Any=None) -> None:
        """Create a new ``AWS::Greengrass::Group``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param name: ``AWS::Greengrass::Group.Name``.
        :param initial_version: ``AWS::Greengrass::Group.InitialVersion``.
        :param role_arn: ``AWS::Greengrass::Group.RoleArn``.
        :param tags: ``AWS::Greengrass::Group.Tags``.
        """
        props = CfnGroupProps(name=name, initial_version=initial_version, role_arn=role_arn, tags=tags)

        jsii.create(CfnGroup, self, [scope, id, props])

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
    @jsii.member(jsii_name="attrId")
    def attr_id(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: Id
        """
        return jsii.get(self, "attrId")

    @property
    @jsii.member(jsii_name="attrLatestVersionArn")
    def attr_latest_version_arn(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: LatestVersionArn
        """
        return jsii.get(self, "attrLatestVersionArn")

    @property
    @jsii.member(jsii_name="attrName")
    def attr_name(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: Name
        """
        return jsii.get(self, "attrName")

    @property
    @jsii.member(jsii_name="attrRoleArn")
    def attr_role_arn(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: RoleArn
        """
        return jsii.get(self, "attrRoleArn")

    @property
    @jsii.member(jsii_name="attrRoleAttachedAt")
    def attr_role_attached_at(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: RoleAttachedAt
        """
        return jsii.get(self, "attrRoleAttachedAt")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        """``AWS::Greengrass::Group.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-group.html#cfn-greengrass-group-tags
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> str:
        """``AWS::Greengrass::Group.Name``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-group.html#cfn-greengrass-group-name
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: str):
        return jsii.set(self, "name", value)

    @property
    @jsii.member(jsii_name="initialVersion")
    def initial_version(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["GroupVersionProperty"]]]:
        """``AWS::Greengrass::Group.InitialVersion``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-group.html#cfn-greengrass-group-initialversion
        """
        return jsii.get(self, "initialVersion")

    @initial_version.setter
    def initial_version(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["GroupVersionProperty"]]]):
        return jsii.set(self, "initialVersion", value)

    @property
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> typing.Optional[str]:
        """``AWS::Greengrass::Group.RoleArn``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-group.html#cfn-greengrass-group-rolearn
        """
        return jsii.get(self, "roleArn")

    @role_arn.setter
    def role_arn(self, value: typing.Optional[str]):
        return jsii.set(self, "roleArn", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnGroup.GroupVersionProperty", jsii_struct_bases=[], name_mapping={'connector_definition_version_arn': 'connectorDefinitionVersionArn', 'core_definition_version_arn': 'coreDefinitionVersionArn', 'device_definition_version_arn': 'deviceDefinitionVersionArn', 'function_definition_version_arn': 'functionDefinitionVersionArn', 'logger_definition_version_arn': 'loggerDefinitionVersionArn', 'resource_definition_version_arn': 'resourceDefinitionVersionArn', 'subscription_definition_version_arn': 'subscriptionDefinitionVersionArn'})
    class GroupVersionProperty():
        def __init__(self, *, connector_definition_version_arn: typing.Optional[str]=None, core_definition_version_arn: typing.Optional[str]=None, device_definition_version_arn: typing.Optional[str]=None, function_definition_version_arn: typing.Optional[str]=None, logger_definition_version_arn: typing.Optional[str]=None, resource_definition_version_arn: typing.Optional[str]=None, subscription_definition_version_arn: typing.Optional[str]=None):
            """
            :param connector_definition_version_arn: ``CfnGroup.GroupVersionProperty.ConnectorDefinitionVersionArn``.
            :param core_definition_version_arn: ``CfnGroup.GroupVersionProperty.CoreDefinitionVersionArn``.
            :param device_definition_version_arn: ``CfnGroup.GroupVersionProperty.DeviceDefinitionVersionArn``.
            :param function_definition_version_arn: ``CfnGroup.GroupVersionProperty.FunctionDefinitionVersionArn``.
            :param logger_definition_version_arn: ``CfnGroup.GroupVersionProperty.LoggerDefinitionVersionArn``.
            :param resource_definition_version_arn: ``CfnGroup.GroupVersionProperty.ResourceDefinitionVersionArn``.
            :param subscription_definition_version_arn: ``CfnGroup.GroupVersionProperty.SubscriptionDefinitionVersionArn``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-group-groupversion.html
            """
            self._values = {
            }
            if connector_definition_version_arn is not None: self._values["connector_definition_version_arn"] = connector_definition_version_arn
            if core_definition_version_arn is not None: self._values["core_definition_version_arn"] = core_definition_version_arn
            if device_definition_version_arn is not None: self._values["device_definition_version_arn"] = device_definition_version_arn
            if function_definition_version_arn is not None: self._values["function_definition_version_arn"] = function_definition_version_arn
            if logger_definition_version_arn is not None: self._values["logger_definition_version_arn"] = logger_definition_version_arn
            if resource_definition_version_arn is not None: self._values["resource_definition_version_arn"] = resource_definition_version_arn
            if subscription_definition_version_arn is not None: self._values["subscription_definition_version_arn"] = subscription_definition_version_arn

        @property
        def connector_definition_version_arn(self) -> typing.Optional[str]:
            """``CfnGroup.GroupVersionProperty.ConnectorDefinitionVersionArn``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-group-groupversion.html#cfn-greengrass-group-groupversion-connectordefinitionversionarn
            """
            return self._values.get('connector_definition_version_arn')

        @property
        def core_definition_version_arn(self) -> typing.Optional[str]:
            """``CfnGroup.GroupVersionProperty.CoreDefinitionVersionArn``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-group-groupversion.html#cfn-greengrass-group-groupversion-coredefinitionversionarn
            """
            return self._values.get('core_definition_version_arn')

        @property
        def device_definition_version_arn(self) -> typing.Optional[str]:
            """``CfnGroup.GroupVersionProperty.DeviceDefinitionVersionArn``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-group-groupversion.html#cfn-greengrass-group-groupversion-devicedefinitionversionarn
            """
            return self._values.get('device_definition_version_arn')

        @property
        def function_definition_version_arn(self) -> typing.Optional[str]:
            """``CfnGroup.GroupVersionProperty.FunctionDefinitionVersionArn``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-group-groupversion.html#cfn-greengrass-group-groupversion-functiondefinitionversionarn
            """
            return self._values.get('function_definition_version_arn')

        @property
        def logger_definition_version_arn(self) -> typing.Optional[str]:
            """``CfnGroup.GroupVersionProperty.LoggerDefinitionVersionArn``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-group-groupversion.html#cfn-greengrass-group-groupversion-loggerdefinitionversionarn
            """
            return self._values.get('logger_definition_version_arn')

        @property
        def resource_definition_version_arn(self) -> typing.Optional[str]:
            """``CfnGroup.GroupVersionProperty.ResourceDefinitionVersionArn``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-group-groupversion.html#cfn-greengrass-group-groupversion-resourcedefinitionversionarn
            """
            return self._values.get('resource_definition_version_arn')

        @property
        def subscription_definition_version_arn(self) -> typing.Optional[str]:
            """``CfnGroup.GroupVersionProperty.SubscriptionDefinitionVersionArn``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-group-groupversion.html#cfn-greengrass-group-groupversion-subscriptiondefinitionversionarn
            """
            return self._values.get('subscription_definition_version_arn')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'GroupVersionProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



@jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnGroupProps", jsii_struct_bases=[], name_mapping={'name': 'name', 'initial_version': 'initialVersion', 'role_arn': 'roleArn', 'tags': 'tags'})
class CfnGroupProps():
    def __init__(self, *, name: str, initial_version: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnGroup.GroupVersionProperty"]]]=None, role_arn: typing.Optional[str]=None, tags: typing.Any=None):
        """Properties for defining a ``AWS::Greengrass::Group``.

        :param name: ``AWS::Greengrass::Group.Name``.
        :param initial_version: ``AWS::Greengrass::Group.InitialVersion``.
        :param role_arn: ``AWS::Greengrass::Group.RoleArn``.
        :param tags: ``AWS::Greengrass::Group.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-group.html
        """
        self._values = {
            'name': name,
        }
        if initial_version is not None: self._values["initial_version"] = initial_version
        if role_arn is not None: self._values["role_arn"] = role_arn
        if tags is not None: self._values["tags"] = tags

    @property
    def name(self) -> str:
        """``AWS::Greengrass::Group.Name``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-group.html#cfn-greengrass-group-name
        """
        return self._values.get('name')

    @property
    def initial_version(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnGroup.GroupVersionProperty"]]]:
        """``AWS::Greengrass::Group.InitialVersion``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-group.html#cfn-greengrass-group-initialversion
        """
        return self._values.get('initial_version')

    @property
    def role_arn(self) -> typing.Optional[str]:
        """``AWS::Greengrass::Group.RoleArn``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-group.html#cfn-greengrass-group-rolearn
        """
        return self._values.get('role_arn')

    @property
    def tags(self) -> typing.Any:
        """``AWS::Greengrass::Group.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-group.html#cfn-greengrass-group-tags
        """
        return self._values.get('tags')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnGroupProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnGroupVersion(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-greengrass.CfnGroupVersion"):
    """A CloudFormation ``AWS::Greengrass::GroupVersion``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-groupversion.html
    cloudformationResource:
    :cloudformationResource:: AWS::Greengrass::GroupVersion
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, group_id: str, connector_definition_version_arn: typing.Optional[str]=None, core_definition_version_arn: typing.Optional[str]=None, device_definition_version_arn: typing.Optional[str]=None, function_definition_version_arn: typing.Optional[str]=None, logger_definition_version_arn: typing.Optional[str]=None, resource_definition_version_arn: typing.Optional[str]=None, subscription_definition_version_arn: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::Greengrass::GroupVersion``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param group_id: ``AWS::Greengrass::GroupVersion.GroupId``.
        :param connector_definition_version_arn: ``AWS::Greengrass::GroupVersion.ConnectorDefinitionVersionArn``.
        :param core_definition_version_arn: ``AWS::Greengrass::GroupVersion.CoreDefinitionVersionArn``.
        :param device_definition_version_arn: ``AWS::Greengrass::GroupVersion.DeviceDefinitionVersionArn``.
        :param function_definition_version_arn: ``AWS::Greengrass::GroupVersion.FunctionDefinitionVersionArn``.
        :param logger_definition_version_arn: ``AWS::Greengrass::GroupVersion.LoggerDefinitionVersionArn``.
        :param resource_definition_version_arn: ``AWS::Greengrass::GroupVersion.ResourceDefinitionVersionArn``.
        :param subscription_definition_version_arn: ``AWS::Greengrass::GroupVersion.SubscriptionDefinitionVersionArn``.
        """
        props = CfnGroupVersionProps(group_id=group_id, connector_definition_version_arn=connector_definition_version_arn, core_definition_version_arn=core_definition_version_arn, device_definition_version_arn=device_definition_version_arn, function_definition_version_arn=function_definition_version_arn, logger_definition_version_arn=logger_definition_version_arn, resource_definition_version_arn=resource_definition_version_arn, subscription_definition_version_arn=subscription_definition_version_arn)

        jsii.create(CfnGroupVersion, self, [scope, id, props])

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
    @jsii.member(jsii_name="groupId")
    def group_id(self) -> str:
        """``AWS::Greengrass::GroupVersion.GroupId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-groupversion.html#cfn-greengrass-groupversion-groupid
        """
        return jsii.get(self, "groupId")

    @group_id.setter
    def group_id(self, value: str):
        return jsii.set(self, "groupId", value)

    @property
    @jsii.member(jsii_name="connectorDefinitionVersionArn")
    def connector_definition_version_arn(self) -> typing.Optional[str]:
        """``AWS::Greengrass::GroupVersion.ConnectorDefinitionVersionArn``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-groupversion.html#cfn-greengrass-groupversion-connectordefinitionversionarn
        """
        return jsii.get(self, "connectorDefinitionVersionArn")

    @connector_definition_version_arn.setter
    def connector_definition_version_arn(self, value: typing.Optional[str]):
        return jsii.set(self, "connectorDefinitionVersionArn", value)

    @property
    @jsii.member(jsii_name="coreDefinitionVersionArn")
    def core_definition_version_arn(self) -> typing.Optional[str]:
        """``AWS::Greengrass::GroupVersion.CoreDefinitionVersionArn``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-groupversion.html#cfn-greengrass-groupversion-coredefinitionversionarn
        """
        return jsii.get(self, "coreDefinitionVersionArn")

    @core_definition_version_arn.setter
    def core_definition_version_arn(self, value: typing.Optional[str]):
        return jsii.set(self, "coreDefinitionVersionArn", value)

    @property
    @jsii.member(jsii_name="deviceDefinitionVersionArn")
    def device_definition_version_arn(self) -> typing.Optional[str]:
        """``AWS::Greengrass::GroupVersion.DeviceDefinitionVersionArn``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-groupversion.html#cfn-greengrass-groupversion-devicedefinitionversionarn
        """
        return jsii.get(self, "deviceDefinitionVersionArn")

    @device_definition_version_arn.setter
    def device_definition_version_arn(self, value: typing.Optional[str]):
        return jsii.set(self, "deviceDefinitionVersionArn", value)

    @property
    @jsii.member(jsii_name="functionDefinitionVersionArn")
    def function_definition_version_arn(self) -> typing.Optional[str]:
        """``AWS::Greengrass::GroupVersion.FunctionDefinitionVersionArn``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-groupversion.html#cfn-greengrass-groupversion-functiondefinitionversionarn
        """
        return jsii.get(self, "functionDefinitionVersionArn")

    @function_definition_version_arn.setter
    def function_definition_version_arn(self, value: typing.Optional[str]):
        return jsii.set(self, "functionDefinitionVersionArn", value)

    @property
    @jsii.member(jsii_name="loggerDefinitionVersionArn")
    def logger_definition_version_arn(self) -> typing.Optional[str]:
        """``AWS::Greengrass::GroupVersion.LoggerDefinitionVersionArn``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-groupversion.html#cfn-greengrass-groupversion-loggerdefinitionversionarn
        """
        return jsii.get(self, "loggerDefinitionVersionArn")

    @logger_definition_version_arn.setter
    def logger_definition_version_arn(self, value: typing.Optional[str]):
        return jsii.set(self, "loggerDefinitionVersionArn", value)

    @property
    @jsii.member(jsii_name="resourceDefinitionVersionArn")
    def resource_definition_version_arn(self) -> typing.Optional[str]:
        """``AWS::Greengrass::GroupVersion.ResourceDefinitionVersionArn``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-groupversion.html#cfn-greengrass-groupversion-resourcedefinitionversionarn
        """
        return jsii.get(self, "resourceDefinitionVersionArn")

    @resource_definition_version_arn.setter
    def resource_definition_version_arn(self, value: typing.Optional[str]):
        return jsii.set(self, "resourceDefinitionVersionArn", value)

    @property
    @jsii.member(jsii_name="subscriptionDefinitionVersionArn")
    def subscription_definition_version_arn(self) -> typing.Optional[str]:
        """``AWS::Greengrass::GroupVersion.SubscriptionDefinitionVersionArn``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-groupversion.html#cfn-greengrass-groupversion-subscriptiondefinitionversionarn
        """
        return jsii.get(self, "subscriptionDefinitionVersionArn")

    @subscription_definition_version_arn.setter
    def subscription_definition_version_arn(self, value: typing.Optional[str]):
        return jsii.set(self, "subscriptionDefinitionVersionArn", value)


@jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnGroupVersionProps", jsii_struct_bases=[], name_mapping={'group_id': 'groupId', 'connector_definition_version_arn': 'connectorDefinitionVersionArn', 'core_definition_version_arn': 'coreDefinitionVersionArn', 'device_definition_version_arn': 'deviceDefinitionVersionArn', 'function_definition_version_arn': 'functionDefinitionVersionArn', 'logger_definition_version_arn': 'loggerDefinitionVersionArn', 'resource_definition_version_arn': 'resourceDefinitionVersionArn', 'subscription_definition_version_arn': 'subscriptionDefinitionVersionArn'})
class CfnGroupVersionProps():
    def __init__(self, *, group_id: str, connector_definition_version_arn: typing.Optional[str]=None, core_definition_version_arn: typing.Optional[str]=None, device_definition_version_arn: typing.Optional[str]=None, function_definition_version_arn: typing.Optional[str]=None, logger_definition_version_arn: typing.Optional[str]=None, resource_definition_version_arn: typing.Optional[str]=None, subscription_definition_version_arn: typing.Optional[str]=None):
        """Properties for defining a ``AWS::Greengrass::GroupVersion``.

        :param group_id: ``AWS::Greengrass::GroupVersion.GroupId``.
        :param connector_definition_version_arn: ``AWS::Greengrass::GroupVersion.ConnectorDefinitionVersionArn``.
        :param core_definition_version_arn: ``AWS::Greengrass::GroupVersion.CoreDefinitionVersionArn``.
        :param device_definition_version_arn: ``AWS::Greengrass::GroupVersion.DeviceDefinitionVersionArn``.
        :param function_definition_version_arn: ``AWS::Greengrass::GroupVersion.FunctionDefinitionVersionArn``.
        :param logger_definition_version_arn: ``AWS::Greengrass::GroupVersion.LoggerDefinitionVersionArn``.
        :param resource_definition_version_arn: ``AWS::Greengrass::GroupVersion.ResourceDefinitionVersionArn``.
        :param subscription_definition_version_arn: ``AWS::Greengrass::GroupVersion.SubscriptionDefinitionVersionArn``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-groupversion.html
        """
        self._values = {
            'group_id': group_id,
        }
        if connector_definition_version_arn is not None: self._values["connector_definition_version_arn"] = connector_definition_version_arn
        if core_definition_version_arn is not None: self._values["core_definition_version_arn"] = core_definition_version_arn
        if device_definition_version_arn is not None: self._values["device_definition_version_arn"] = device_definition_version_arn
        if function_definition_version_arn is not None: self._values["function_definition_version_arn"] = function_definition_version_arn
        if logger_definition_version_arn is not None: self._values["logger_definition_version_arn"] = logger_definition_version_arn
        if resource_definition_version_arn is not None: self._values["resource_definition_version_arn"] = resource_definition_version_arn
        if subscription_definition_version_arn is not None: self._values["subscription_definition_version_arn"] = subscription_definition_version_arn

    @property
    def group_id(self) -> str:
        """``AWS::Greengrass::GroupVersion.GroupId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-groupversion.html#cfn-greengrass-groupversion-groupid
        """
        return self._values.get('group_id')

    @property
    def connector_definition_version_arn(self) -> typing.Optional[str]:
        """``AWS::Greengrass::GroupVersion.ConnectorDefinitionVersionArn``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-groupversion.html#cfn-greengrass-groupversion-connectordefinitionversionarn
        """
        return self._values.get('connector_definition_version_arn')

    @property
    def core_definition_version_arn(self) -> typing.Optional[str]:
        """``AWS::Greengrass::GroupVersion.CoreDefinitionVersionArn``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-groupversion.html#cfn-greengrass-groupversion-coredefinitionversionarn
        """
        return self._values.get('core_definition_version_arn')

    @property
    def device_definition_version_arn(self) -> typing.Optional[str]:
        """``AWS::Greengrass::GroupVersion.DeviceDefinitionVersionArn``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-groupversion.html#cfn-greengrass-groupversion-devicedefinitionversionarn
        """
        return self._values.get('device_definition_version_arn')

    @property
    def function_definition_version_arn(self) -> typing.Optional[str]:
        """``AWS::Greengrass::GroupVersion.FunctionDefinitionVersionArn``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-groupversion.html#cfn-greengrass-groupversion-functiondefinitionversionarn
        """
        return self._values.get('function_definition_version_arn')

    @property
    def logger_definition_version_arn(self) -> typing.Optional[str]:
        """``AWS::Greengrass::GroupVersion.LoggerDefinitionVersionArn``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-groupversion.html#cfn-greengrass-groupversion-loggerdefinitionversionarn
        """
        return self._values.get('logger_definition_version_arn')

    @property
    def resource_definition_version_arn(self) -> typing.Optional[str]:
        """``AWS::Greengrass::GroupVersion.ResourceDefinitionVersionArn``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-groupversion.html#cfn-greengrass-groupversion-resourcedefinitionversionarn
        """
        return self._values.get('resource_definition_version_arn')

    @property
    def subscription_definition_version_arn(self) -> typing.Optional[str]:
        """``AWS::Greengrass::GroupVersion.SubscriptionDefinitionVersionArn``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-groupversion.html#cfn-greengrass-groupversion-subscriptiondefinitionversionarn
        """
        return self._values.get('subscription_definition_version_arn')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnGroupVersionProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnLoggerDefinition(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-greengrass.CfnLoggerDefinition"):
    """A CloudFormation ``AWS::Greengrass::LoggerDefinition``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-loggerdefinition.html
    cloudformationResource:
    :cloudformationResource:: AWS::Greengrass::LoggerDefinition
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, name: str, initial_version: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["LoggerDefinitionVersionProperty"]]]=None, tags: typing.Any=None) -> None:
        """Create a new ``AWS::Greengrass::LoggerDefinition``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param name: ``AWS::Greengrass::LoggerDefinition.Name``.
        :param initial_version: ``AWS::Greengrass::LoggerDefinition.InitialVersion``.
        :param tags: ``AWS::Greengrass::LoggerDefinition.Tags``.
        """
        props = CfnLoggerDefinitionProps(name=name, initial_version=initial_version, tags=tags)

        jsii.create(CfnLoggerDefinition, self, [scope, id, props])

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
    @jsii.member(jsii_name="attrId")
    def attr_id(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: Id
        """
        return jsii.get(self, "attrId")

    @property
    @jsii.member(jsii_name="attrLatestVersionArn")
    def attr_latest_version_arn(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: LatestVersionArn
        """
        return jsii.get(self, "attrLatestVersionArn")

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
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        """``AWS::Greengrass::LoggerDefinition.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-loggerdefinition.html#cfn-greengrass-loggerdefinition-tags
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> str:
        """``AWS::Greengrass::LoggerDefinition.Name``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-loggerdefinition.html#cfn-greengrass-loggerdefinition-name
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: str):
        return jsii.set(self, "name", value)

    @property
    @jsii.member(jsii_name="initialVersion")
    def initial_version(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["LoggerDefinitionVersionProperty"]]]:
        """``AWS::Greengrass::LoggerDefinition.InitialVersion``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-loggerdefinition.html#cfn-greengrass-loggerdefinition-initialversion
        """
        return jsii.get(self, "initialVersion")

    @initial_version.setter
    def initial_version(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["LoggerDefinitionVersionProperty"]]]):
        return jsii.set(self, "initialVersion", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnLoggerDefinition.LoggerDefinitionVersionProperty", jsii_struct_bases=[], name_mapping={'loggers': 'loggers'})
    class LoggerDefinitionVersionProperty():
        def __init__(self, *, loggers: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnLoggerDefinition.LoggerProperty"]]]):
            """
            :param loggers: ``CfnLoggerDefinition.LoggerDefinitionVersionProperty.Loggers``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-loggerdefinition-loggerdefinitionversion.html
            """
            self._values = {
                'loggers': loggers,
            }

        @property
        def loggers(self) -> typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnLoggerDefinition.LoggerProperty"]]]:
            """``CfnLoggerDefinition.LoggerDefinitionVersionProperty.Loggers``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-loggerdefinition-loggerdefinitionversion.html#cfn-greengrass-loggerdefinition-loggerdefinitionversion-loggers
            """
            return self._values.get('loggers')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'LoggerDefinitionVersionProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnLoggerDefinition.LoggerProperty", jsii_struct_bases=[], name_mapping={'component': 'component', 'id': 'id', 'level': 'level', 'type': 'type', 'space': 'space'})
    class LoggerProperty():
        def __init__(self, *, component: str, id: str, level: str, type: str, space: typing.Optional[jsii.Number]=None):
            """
            :param component: ``CfnLoggerDefinition.LoggerProperty.Component``.
            :param id: ``CfnLoggerDefinition.LoggerProperty.Id``.
            :param level: ``CfnLoggerDefinition.LoggerProperty.Level``.
            :param type: ``CfnLoggerDefinition.LoggerProperty.Type``.
            :param space: ``CfnLoggerDefinition.LoggerProperty.Space``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-loggerdefinition-logger.html
            """
            self._values = {
                'component': component,
                'id': id,
                'level': level,
                'type': type,
            }
            if space is not None: self._values["space"] = space

        @property
        def component(self) -> str:
            """``CfnLoggerDefinition.LoggerProperty.Component``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-loggerdefinition-logger.html#cfn-greengrass-loggerdefinition-logger-component
            """
            return self._values.get('component')

        @property
        def id(self) -> str:
            """``CfnLoggerDefinition.LoggerProperty.Id``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-loggerdefinition-logger.html#cfn-greengrass-loggerdefinition-logger-id
            """
            return self._values.get('id')

        @property
        def level(self) -> str:
            """``CfnLoggerDefinition.LoggerProperty.Level``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-loggerdefinition-logger.html#cfn-greengrass-loggerdefinition-logger-level
            """
            return self._values.get('level')

        @property
        def type(self) -> str:
            """``CfnLoggerDefinition.LoggerProperty.Type``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-loggerdefinition-logger.html#cfn-greengrass-loggerdefinition-logger-type
            """
            return self._values.get('type')

        @property
        def space(self) -> typing.Optional[jsii.Number]:
            """``CfnLoggerDefinition.LoggerProperty.Space``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-loggerdefinition-logger.html#cfn-greengrass-loggerdefinition-logger-space
            """
            return self._values.get('space')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'LoggerProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



@jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnLoggerDefinitionProps", jsii_struct_bases=[], name_mapping={'name': 'name', 'initial_version': 'initialVersion', 'tags': 'tags'})
class CfnLoggerDefinitionProps():
    def __init__(self, *, name: str, initial_version: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnLoggerDefinition.LoggerDefinitionVersionProperty"]]]=None, tags: typing.Any=None):
        """Properties for defining a ``AWS::Greengrass::LoggerDefinition``.

        :param name: ``AWS::Greengrass::LoggerDefinition.Name``.
        :param initial_version: ``AWS::Greengrass::LoggerDefinition.InitialVersion``.
        :param tags: ``AWS::Greengrass::LoggerDefinition.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-loggerdefinition.html
        """
        self._values = {
            'name': name,
        }
        if initial_version is not None: self._values["initial_version"] = initial_version
        if tags is not None: self._values["tags"] = tags

    @property
    def name(self) -> str:
        """``AWS::Greengrass::LoggerDefinition.Name``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-loggerdefinition.html#cfn-greengrass-loggerdefinition-name
        """
        return self._values.get('name')

    @property
    def initial_version(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnLoggerDefinition.LoggerDefinitionVersionProperty"]]]:
        """``AWS::Greengrass::LoggerDefinition.InitialVersion``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-loggerdefinition.html#cfn-greengrass-loggerdefinition-initialversion
        """
        return self._values.get('initial_version')

    @property
    def tags(self) -> typing.Any:
        """``AWS::Greengrass::LoggerDefinition.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-loggerdefinition.html#cfn-greengrass-loggerdefinition-tags
        """
        return self._values.get('tags')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnLoggerDefinitionProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnLoggerDefinitionVersion(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-greengrass.CfnLoggerDefinitionVersion"):
    """A CloudFormation ``AWS::Greengrass::LoggerDefinitionVersion``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-loggerdefinitionversion.html
    cloudformationResource:
    :cloudformationResource:: AWS::Greengrass::LoggerDefinitionVersion
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, logger_definition_id: str, loggers: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "LoggerProperty"]]]) -> None:
        """Create a new ``AWS::Greengrass::LoggerDefinitionVersion``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param logger_definition_id: ``AWS::Greengrass::LoggerDefinitionVersion.LoggerDefinitionId``.
        :param loggers: ``AWS::Greengrass::LoggerDefinitionVersion.Loggers``.
        """
        props = CfnLoggerDefinitionVersionProps(logger_definition_id=logger_definition_id, loggers=loggers)

        jsii.create(CfnLoggerDefinitionVersion, self, [scope, id, props])

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
    @jsii.member(jsii_name="loggerDefinitionId")
    def logger_definition_id(self) -> str:
        """``AWS::Greengrass::LoggerDefinitionVersion.LoggerDefinitionId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-loggerdefinitionversion.html#cfn-greengrass-loggerdefinitionversion-loggerdefinitionid
        """
        return jsii.get(self, "loggerDefinitionId")

    @logger_definition_id.setter
    def logger_definition_id(self, value: str):
        return jsii.set(self, "loggerDefinitionId", value)

    @property
    @jsii.member(jsii_name="loggers")
    def loggers(self) -> typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "LoggerProperty"]]]:
        """``AWS::Greengrass::LoggerDefinitionVersion.Loggers``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-loggerdefinitionversion.html#cfn-greengrass-loggerdefinitionversion-loggers
        """
        return jsii.get(self, "loggers")

    @loggers.setter
    def loggers(self, value: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "LoggerProperty"]]]):
        return jsii.set(self, "loggers", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnLoggerDefinitionVersion.LoggerProperty", jsii_struct_bases=[], name_mapping={'component': 'component', 'id': 'id', 'level': 'level', 'type': 'type', 'space': 'space'})
    class LoggerProperty():
        def __init__(self, *, component: str, id: str, level: str, type: str, space: typing.Optional[jsii.Number]=None):
            """
            :param component: ``CfnLoggerDefinitionVersion.LoggerProperty.Component``.
            :param id: ``CfnLoggerDefinitionVersion.LoggerProperty.Id``.
            :param level: ``CfnLoggerDefinitionVersion.LoggerProperty.Level``.
            :param type: ``CfnLoggerDefinitionVersion.LoggerProperty.Type``.
            :param space: ``CfnLoggerDefinitionVersion.LoggerProperty.Space``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-loggerdefinitionversion-logger.html
            """
            self._values = {
                'component': component,
                'id': id,
                'level': level,
                'type': type,
            }
            if space is not None: self._values["space"] = space

        @property
        def component(self) -> str:
            """``CfnLoggerDefinitionVersion.LoggerProperty.Component``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-loggerdefinitionversion-logger.html#cfn-greengrass-loggerdefinitionversion-logger-component
            """
            return self._values.get('component')

        @property
        def id(self) -> str:
            """``CfnLoggerDefinitionVersion.LoggerProperty.Id``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-loggerdefinitionversion-logger.html#cfn-greengrass-loggerdefinitionversion-logger-id
            """
            return self._values.get('id')

        @property
        def level(self) -> str:
            """``CfnLoggerDefinitionVersion.LoggerProperty.Level``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-loggerdefinitionversion-logger.html#cfn-greengrass-loggerdefinitionversion-logger-level
            """
            return self._values.get('level')

        @property
        def type(self) -> str:
            """``CfnLoggerDefinitionVersion.LoggerProperty.Type``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-loggerdefinitionversion-logger.html#cfn-greengrass-loggerdefinitionversion-logger-type
            """
            return self._values.get('type')

        @property
        def space(self) -> typing.Optional[jsii.Number]:
            """``CfnLoggerDefinitionVersion.LoggerProperty.Space``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-loggerdefinitionversion-logger.html#cfn-greengrass-loggerdefinitionversion-logger-space
            """
            return self._values.get('space')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'LoggerProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



@jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnLoggerDefinitionVersionProps", jsii_struct_bases=[], name_mapping={'logger_definition_id': 'loggerDefinitionId', 'loggers': 'loggers'})
class CfnLoggerDefinitionVersionProps():
    def __init__(self, *, logger_definition_id: str, loggers: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnLoggerDefinitionVersion.LoggerProperty"]]]):
        """Properties for defining a ``AWS::Greengrass::LoggerDefinitionVersion``.

        :param logger_definition_id: ``AWS::Greengrass::LoggerDefinitionVersion.LoggerDefinitionId``.
        :param loggers: ``AWS::Greengrass::LoggerDefinitionVersion.Loggers``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-loggerdefinitionversion.html
        """
        self._values = {
            'logger_definition_id': logger_definition_id,
            'loggers': loggers,
        }

    @property
    def logger_definition_id(self) -> str:
        """``AWS::Greengrass::LoggerDefinitionVersion.LoggerDefinitionId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-loggerdefinitionversion.html#cfn-greengrass-loggerdefinitionversion-loggerdefinitionid
        """
        return self._values.get('logger_definition_id')

    @property
    def loggers(self) -> typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnLoggerDefinitionVersion.LoggerProperty"]]]:
        """``AWS::Greengrass::LoggerDefinitionVersion.Loggers``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-loggerdefinitionversion.html#cfn-greengrass-loggerdefinitionversion-loggers
        """
        return self._values.get('loggers')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnLoggerDefinitionVersionProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnResourceDefinition(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-greengrass.CfnResourceDefinition"):
    """A CloudFormation ``AWS::Greengrass::ResourceDefinition``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-resourcedefinition.html
    cloudformationResource:
    :cloudformationResource:: AWS::Greengrass::ResourceDefinition
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, name: str, initial_version: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["ResourceDefinitionVersionProperty"]]]=None, tags: typing.Any=None) -> None:
        """Create a new ``AWS::Greengrass::ResourceDefinition``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param name: ``AWS::Greengrass::ResourceDefinition.Name``.
        :param initial_version: ``AWS::Greengrass::ResourceDefinition.InitialVersion``.
        :param tags: ``AWS::Greengrass::ResourceDefinition.Tags``.
        """
        props = CfnResourceDefinitionProps(name=name, initial_version=initial_version, tags=tags)

        jsii.create(CfnResourceDefinition, self, [scope, id, props])

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
    @jsii.member(jsii_name="attrId")
    def attr_id(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: Id
        """
        return jsii.get(self, "attrId")

    @property
    @jsii.member(jsii_name="attrLatestVersionArn")
    def attr_latest_version_arn(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: LatestVersionArn
        """
        return jsii.get(self, "attrLatestVersionArn")

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
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        """``AWS::Greengrass::ResourceDefinition.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-resourcedefinition.html#cfn-greengrass-resourcedefinition-tags
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> str:
        """``AWS::Greengrass::ResourceDefinition.Name``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-resourcedefinition.html#cfn-greengrass-resourcedefinition-name
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: str):
        return jsii.set(self, "name", value)

    @property
    @jsii.member(jsii_name="initialVersion")
    def initial_version(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["ResourceDefinitionVersionProperty"]]]:
        """``AWS::Greengrass::ResourceDefinition.InitialVersion``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-resourcedefinition.html#cfn-greengrass-resourcedefinition-initialversion
        """
        return jsii.get(self, "initialVersion")

    @initial_version.setter
    def initial_version(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["ResourceDefinitionVersionProperty"]]]):
        return jsii.set(self, "initialVersion", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnResourceDefinition.GroupOwnerSettingProperty", jsii_struct_bases=[], name_mapping={'auto_add_group_owner': 'autoAddGroupOwner', 'group_owner': 'groupOwner'})
    class GroupOwnerSettingProperty():
        def __init__(self, *, auto_add_group_owner: typing.Union[bool, aws_cdk.core.IResolvable], group_owner: typing.Optional[str]=None):
            """
            :param auto_add_group_owner: ``CfnResourceDefinition.GroupOwnerSettingProperty.AutoAddGroupOwner``.
            :param group_owner: ``CfnResourceDefinition.GroupOwnerSettingProperty.GroupOwner``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-groupownersetting.html
            """
            self._values = {
                'auto_add_group_owner': auto_add_group_owner,
            }
            if group_owner is not None: self._values["group_owner"] = group_owner

        @property
        def auto_add_group_owner(self) -> typing.Union[bool, aws_cdk.core.IResolvable]:
            """``CfnResourceDefinition.GroupOwnerSettingProperty.AutoAddGroupOwner``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-groupownersetting.html#cfn-greengrass-resourcedefinition-groupownersetting-autoaddgroupowner
            """
            return self._values.get('auto_add_group_owner')

        @property
        def group_owner(self) -> typing.Optional[str]:
            """``CfnResourceDefinition.GroupOwnerSettingProperty.GroupOwner``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-groupownersetting.html#cfn-greengrass-resourcedefinition-groupownersetting-groupowner
            """
            return self._values.get('group_owner')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'GroupOwnerSettingProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnResourceDefinition.LocalDeviceResourceDataProperty", jsii_struct_bases=[], name_mapping={'source_path': 'sourcePath', 'group_owner_setting': 'groupOwnerSetting'})
    class LocalDeviceResourceDataProperty():
        def __init__(self, *, source_path: str, group_owner_setting: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnResourceDefinition.GroupOwnerSettingProperty"]]]=None):
            """
            :param source_path: ``CfnResourceDefinition.LocalDeviceResourceDataProperty.SourcePath``.
            :param group_owner_setting: ``CfnResourceDefinition.LocalDeviceResourceDataProperty.GroupOwnerSetting``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-localdeviceresourcedata.html
            """
            self._values = {
                'source_path': source_path,
            }
            if group_owner_setting is not None: self._values["group_owner_setting"] = group_owner_setting

        @property
        def source_path(self) -> str:
            """``CfnResourceDefinition.LocalDeviceResourceDataProperty.SourcePath``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-localdeviceresourcedata.html#cfn-greengrass-resourcedefinition-localdeviceresourcedata-sourcepath
            """
            return self._values.get('source_path')

        @property
        def group_owner_setting(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnResourceDefinition.GroupOwnerSettingProperty"]]]:
            """``CfnResourceDefinition.LocalDeviceResourceDataProperty.GroupOwnerSetting``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-localdeviceresourcedata.html#cfn-greengrass-resourcedefinition-localdeviceresourcedata-groupownersetting
            """
            return self._values.get('group_owner_setting')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'LocalDeviceResourceDataProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnResourceDefinition.LocalVolumeResourceDataProperty", jsii_struct_bases=[], name_mapping={'destination_path': 'destinationPath', 'source_path': 'sourcePath', 'group_owner_setting': 'groupOwnerSetting'})
    class LocalVolumeResourceDataProperty():
        def __init__(self, *, destination_path: str, source_path: str, group_owner_setting: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnResourceDefinition.GroupOwnerSettingProperty"]]]=None):
            """
            :param destination_path: ``CfnResourceDefinition.LocalVolumeResourceDataProperty.DestinationPath``.
            :param source_path: ``CfnResourceDefinition.LocalVolumeResourceDataProperty.SourcePath``.
            :param group_owner_setting: ``CfnResourceDefinition.LocalVolumeResourceDataProperty.GroupOwnerSetting``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-localvolumeresourcedata.html
            """
            self._values = {
                'destination_path': destination_path,
                'source_path': source_path,
            }
            if group_owner_setting is not None: self._values["group_owner_setting"] = group_owner_setting

        @property
        def destination_path(self) -> str:
            """``CfnResourceDefinition.LocalVolumeResourceDataProperty.DestinationPath``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-localvolumeresourcedata.html#cfn-greengrass-resourcedefinition-localvolumeresourcedata-destinationpath
            """
            return self._values.get('destination_path')

        @property
        def source_path(self) -> str:
            """``CfnResourceDefinition.LocalVolumeResourceDataProperty.SourcePath``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-localvolumeresourcedata.html#cfn-greengrass-resourcedefinition-localvolumeresourcedata-sourcepath
            """
            return self._values.get('source_path')

        @property
        def group_owner_setting(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnResourceDefinition.GroupOwnerSettingProperty"]]]:
            """``CfnResourceDefinition.LocalVolumeResourceDataProperty.GroupOwnerSetting``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-localvolumeresourcedata.html#cfn-greengrass-resourcedefinition-localvolumeresourcedata-groupownersetting
            """
            return self._values.get('group_owner_setting')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'LocalVolumeResourceDataProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnResourceDefinition.ResourceDataContainerProperty", jsii_struct_bases=[], name_mapping={'local_device_resource_data': 'localDeviceResourceData', 'local_volume_resource_data': 'localVolumeResourceData', 's3_machine_learning_model_resource_data': 's3MachineLearningModelResourceData', 'sage_maker_machine_learning_model_resource_data': 'sageMakerMachineLearningModelResourceData', 'secrets_manager_secret_resource_data': 'secretsManagerSecretResourceData'})
    class ResourceDataContainerProperty():
        def __init__(self, *, local_device_resource_data: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnResourceDefinition.LocalDeviceResourceDataProperty"]]]=None, local_volume_resource_data: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnResourceDefinition.LocalVolumeResourceDataProperty"]]]=None, s3_machine_learning_model_resource_data: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnResourceDefinition.S3MachineLearningModelResourceDataProperty"]]]=None, sage_maker_machine_learning_model_resource_data: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnResourceDefinition.SageMakerMachineLearningModelResourceDataProperty"]]]=None, secrets_manager_secret_resource_data: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnResourceDefinition.SecretsManagerSecretResourceDataProperty"]]]=None):
            """
            :param local_device_resource_data: ``CfnResourceDefinition.ResourceDataContainerProperty.LocalDeviceResourceData``.
            :param local_volume_resource_data: ``CfnResourceDefinition.ResourceDataContainerProperty.LocalVolumeResourceData``.
            :param s3_machine_learning_model_resource_data: ``CfnResourceDefinition.ResourceDataContainerProperty.S3MachineLearningModelResourceData``.
            :param sage_maker_machine_learning_model_resource_data: ``CfnResourceDefinition.ResourceDataContainerProperty.SageMakerMachineLearningModelResourceData``.
            :param secrets_manager_secret_resource_data: ``CfnResourceDefinition.ResourceDataContainerProperty.SecretsManagerSecretResourceData``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-resourcedatacontainer.html
            """
            self._values = {
            }
            if local_device_resource_data is not None: self._values["local_device_resource_data"] = local_device_resource_data
            if local_volume_resource_data is not None: self._values["local_volume_resource_data"] = local_volume_resource_data
            if s3_machine_learning_model_resource_data is not None: self._values["s3_machine_learning_model_resource_data"] = s3_machine_learning_model_resource_data
            if sage_maker_machine_learning_model_resource_data is not None: self._values["sage_maker_machine_learning_model_resource_data"] = sage_maker_machine_learning_model_resource_data
            if secrets_manager_secret_resource_data is not None: self._values["secrets_manager_secret_resource_data"] = secrets_manager_secret_resource_data

        @property
        def local_device_resource_data(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnResourceDefinition.LocalDeviceResourceDataProperty"]]]:
            """``CfnResourceDefinition.ResourceDataContainerProperty.LocalDeviceResourceData``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-resourcedatacontainer.html#cfn-greengrass-resourcedefinition-resourcedatacontainer-localdeviceresourcedata
            """
            return self._values.get('local_device_resource_data')

        @property
        def local_volume_resource_data(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnResourceDefinition.LocalVolumeResourceDataProperty"]]]:
            """``CfnResourceDefinition.ResourceDataContainerProperty.LocalVolumeResourceData``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-resourcedatacontainer.html#cfn-greengrass-resourcedefinition-resourcedatacontainer-localvolumeresourcedata
            """
            return self._values.get('local_volume_resource_data')

        @property
        def s3_machine_learning_model_resource_data(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnResourceDefinition.S3MachineLearningModelResourceDataProperty"]]]:
            """``CfnResourceDefinition.ResourceDataContainerProperty.S3MachineLearningModelResourceData``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-resourcedatacontainer.html#cfn-greengrass-resourcedefinition-resourcedatacontainer-s3machinelearningmodelresourcedata
            """
            return self._values.get('s3_machine_learning_model_resource_data')

        @property
        def sage_maker_machine_learning_model_resource_data(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnResourceDefinition.SageMakerMachineLearningModelResourceDataProperty"]]]:
            """``CfnResourceDefinition.ResourceDataContainerProperty.SageMakerMachineLearningModelResourceData``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-resourcedatacontainer.html#cfn-greengrass-resourcedefinition-resourcedatacontainer-sagemakermachinelearningmodelresourcedata
            """
            return self._values.get('sage_maker_machine_learning_model_resource_data')

        @property
        def secrets_manager_secret_resource_data(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnResourceDefinition.SecretsManagerSecretResourceDataProperty"]]]:
            """``CfnResourceDefinition.ResourceDataContainerProperty.SecretsManagerSecretResourceData``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-resourcedatacontainer.html#cfn-greengrass-resourcedefinition-resourcedatacontainer-secretsmanagersecretresourcedata
            """
            return self._values.get('secrets_manager_secret_resource_data')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'ResourceDataContainerProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnResourceDefinition.ResourceDefinitionVersionProperty", jsii_struct_bases=[], name_mapping={'resources': 'resources'})
    class ResourceDefinitionVersionProperty():
        def __init__(self, *, resources: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnResourceDefinition.ResourceInstanceProperty"]]]):
            """
            :param resources: ``CfnResourceDefinition.ResourceDefinitionVersionProperty.Resources``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-resourcedefinitionversion.html
            """
            self._values = {
                'resources': resources,
            }

        @property
        def resources(self) -> typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnResourceDefinition.ResourceInstanceProperty"]]]:
            """``CfnResourceDefinition.ResourceDefinitionVersionProperty.Resources``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-resourcedefinitionversion.html#cfn-greengrass-resourcedefinition-resourcedefinitionversion-resources
            """
            return self._values.get('resources')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'ResourceDefinitionVersionProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnResourceDefinition.ResourceInstanceProperty", jsii_struct_bases=[], name_mapping={'id': 'id', 'name': 'name', 'resource_data_container': 'resourceDataContainer'})
    class ResourceInstanceProperty():
        def __init__(self, *, id: str, name: str, resource_data_container: typing.Union[aws_cdk.core.IResolvable, "CfnResourceDefinition.ResourceDataContainerProperty"]):
            """
            :param id: ``CfnResourceDefinition.ResourceInstanceProperty.Id``.
            :param name: ``CfnResourceDefinition.ResourceInstanceProperty.Name``.
            :param resource_data_container: ``CfnResourceDefinition.ResourceInstanceProperty.ResourceDataContainer``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-resourceinstance.html
            """
            self._values = {
                'id': id,
                'name': name,
                'resource_data_container': resource_data_container,
            }

        @property
        def id(self) -> str:
            """``CfnResourceDefinition.ResourceInstanceProperty.Id``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-resourceinstance.html#cfn-greengrass-resourcedefinition-resourceinstance-id
            """
            return self._values.get('id')

        @property
        def name(self) -> str:
            """``CfnResourceDefinition.ResourceInstanceProperty.Name``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-resourceinstance.html#cfn-greengrass-resourcedefinition-resourceinstance-name
            """
            return self._values.get('name')

        @property
        def resource_data_container(self) -> typing.Union[aws_cdk.core.IResolvable, "CfnResourceDefinition.ResourceDataContainerProperty"]:
            """``CfnResourceDefinition.ResourceInstanceProperty.ResourceDataContainer``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-resourceinstance.html#cfn-greengrass-resourcedefinition-resourceinstance-resourcedatacontainer
            """
            return self._values.get('resource_data_container')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'ResourceInstanceProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnResourceDefinition.S3MachineLearningModelResourceDataProperty", jsii_struct_bases=[], name_mapping={'destination_path': 'destinationPath', 's3_uri': 's3Uri'})
    class S3MachineLearningModelResourceDataProperty():
        def __init__(self, *, destination_path: str, s3_uri: str):
            """
            :param destination_path: ``CfnResourceDefinition.S3MachineLearningModelResourceDataProperty.DestinationPath``.
            :param s3_uri: ``CfnResourceDefinition.S3MachineLearningModelResourceDataProperty.S3Uri``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-s3machinelearningmodelresourcedata.html
            """
            self._values = {
                'destination_path': destination_path,
                's3_uri': s3_uri,
            }

        @property
        def destination_path(self) -> str:
            """``CfnResourceDefinition.S3MachineLearningModelResourceDataProperty.DestinationPath``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-s3machinelearningmodelresourcedata.html#cfn-greengrass-resourcedefinition-s3machinelearningmodelresourcedata-destinationpath
            """
            return self._values.get('destination_path')

        @property
        def s3_uri(self) -> str:
            """``CfnResourceDefinition.S3MachineLearningModelResourceDataProperty.S3Uri``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-s3machinelearningmodelresourcedata.html#cfn-greengrass-resourcedefinition-s3machinelearningmodelresourcedata-s3uri
            """
            return self._values.get('s3_uri')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'S3MachineLearningModelResourceDataProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnResourceDefinition.SageMakerMachineLearningModelResourceDataProperty", jsii_struct_bases=[], name_mapping={'destination_path': 'destinationPath', 'sage_maker_job_arn': 'sageMakerJobArn'})
    class SageMakerMachineLearningModelResourceDataProperty():
        def __init__(self, *, destination_path: str, sage_maker_job_arn: str):
            """
            :param destination_path: ``CfnResourceDefinition.SageMakerMachineLearningModelResourceDataProperty.DestinationPath``.
            :param sage_maker_job_arn: ``CfnResourceDefinition.SageMakerMachineLearningModelResourceDataProperty.SageMakerJobArn``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-sagemakermachinelearningmodelresourcedata.html
            """
            self._values = {
                'destination_path': destination_path,
                'sage_maker_job_arn': sage_maker_job_arn,
            }

        @property
        def destination_path(self) -> str:
            """``CfnResourceDefinition.SageMakerMachineLearningModelResourceDataProperty.DestinationPath``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-sagemakermachinelearningmodelresourcedata.html#cfn-greengrass-resourcedefinition-sagemakermachinelearningmodelresourcedata-destinationpath
            """
            return self._values.get('destination_path')

        @property
        def sage_maker_job_arn(self) -> str:
            """``CfnResourceDefinition.SageMakerMachineLearningModelResourceDataProperty.SageMakerJobArn``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-sagemakermachinelearningmodelresourcedata.html#cfn-greengrass-resourcedefinition-sagemakermachinelearningmodelresourcedata-sagemakerjobarn
            """
            return self._values.get('sage_maker_job_arn')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'SageMakerMachineLearningModelResourceDataProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnResourceDefinition.SecretsManagerSecretResourceDataProperty", jsii_struct_bases=[], name_mapping={'arn': 'arn', 'additional_staging_labels_to_download': 'additionalStagingLabelsToDownload'})
    class SecretsManagerSecretResourceDataProperty():
        def __init__(self, *, arn: str, additional_staging_labels_to_download: typing.Optional[typing.List[str]]=None):
            """
            :param arn: ``CfnResourceDefinition.SecretsManagerSecretResourceDataProperty.ARN``.
            :param additional_staging_labels_to_download: ``CfnResourceDefinition.SecretsManagerSecretResourceDataProperty.AdditionalStagingLabelsToDownload``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-secretsmanagersecretresourcedata.html
            """
            self._values = {
                'arn': arn,
            }
            if additional_staging_labels_to_download is not None: self._values["additional_staging_labels_to_download"] = additional_staging_labels_to_download

        @property
        def arn(self) -> str:
            """``CfnResourceDefinition.SecretsManagerSecretResourceDataProperty.ARN``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-secretsmanagersecretresourcedata.html#cfn-greengrass-resourcedefinition-secretsmanagersecretresourcedata-arn
            """
            return self._values.get('arn')

        @property
        def additional_staging_labels_to_download(self) -> typing.Optional[typing.List[str]]:
            """``CfnResourceDefinition.SecretsManagerSecretResourceDataProperty.AdditionalStagingLabelsToDownload``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-secretsmanagersecretresourcedata.html#cfn-greengrass-resourcedefinition-secretsmanagersecretresourcedata-additionalstaginglabelstodownload
            """
            return self._values.get('additional_staging_labels_to_download')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'SecretsManagerSecretResourceDataProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



@jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnResourceDefinitionProps", jsii_struct_bases=[], name_mapping={'name': 'name', 'initial_version': 'initialVersion', 'tags': 'tags'})
class CfnResourceDefinitionProps():
    def __init__(self, *, name: str, initial_version: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnResourceDefinition.ResourceDefinitionVersionProperty"]]]=None, tags: typing.Any=None):
        """Properties for defining a ``AWS::Greengrass::ResourceDefinition``.

        :param name: ``AWS::Greengrass::ResourceDefinition.Name``.
        :param initial_version: ``AWS::Greengrass::ResourceDefinition.InitialVersion``.
        :param tags: ``AWS::Greengrass::ResourceDefinition.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-resourcedefinition.html
        """
        self._values = {
            'name': name,
        }
        if initial_version is not None: self._values["initial_version"] = initial_version
        if tags is not None: self._values["tags"] = tags

    @property
    def name(self) -> str:
        """``AWS::Greengrass::ResourceDefinition.Name``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-resourcedefinition.html#cfn-greengrass-resourcedefinition-name
        """
        return self._values.get('name')

    @property
    def initial_version(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnResourceDefinition.ResourceDefinitionVersionProperty"]]]:
        """``AWS::Greengrass::ResourceDefinition.InitialVersion``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-resourcedefinition.html#cfn-greengrass-resourcedefinition-initialversion
        """
        return self._values.get('initial_version')

    @property
    def tags(self) -> typing.Any:
        """``AWS::Greengrass::ResourceDefinition.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-resourcedefinition.html#cfn-greengrass-resourcedefinition-tags
        """
        return self._values.get('tags')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnResourceDefinitionProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnResourceDefinitionVersion(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-greengrass.CfnResourceDefinitionVersion"):
    """A CloudFormation ``AWS::Greengrass::ResourceDefinitionVersion``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-resourcedefinitionversion.html
    cloudformationResource:
    :cloudformationResource:: AWS::Greengrass::ResourceDefinitionVersion
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, resource_definition_id: str, resources: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "ResourceInstanceProperty"]]]) -> None:
        """Create a new ``AWS::Greengrass::ResourceDefinitionVersion``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param resource_definition_id: ``AWS::Greengrass::ResourceDefinitionVersion.ResourceDefinitionId``.
        :param resources: ``AWS::Greengrass::ResourceDefinitionVersion.Resources``.
        """
        props = CfnResourceDefinitionVersionProps(resource_definition_id=resource_definition_id, resources=resources)

        jsii.create(CfnResourceDefinitionVersion, self, [scope, id, props])

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
    @jsii.member(jsii_name="resourceDefinitionId")
    def resource_definition_id(self) -> str:
        """``AWS::Greengrass::ResourceDefinitionVersion.ResourceDefinitionId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-resourcedefinitionversion.html#cfn-greengrass-resourcedefinitionversion-resourcedefinitionid
        """
        return jsii.get(self, "resourceDefinitionId")

    @resource_definition_id.setter
    def resource_definition_id(self, value: str):
        return jsii.set(self, "resourceDefinitionId", value)

    @property
    @jsii.member(jsii_name="resources")
    def resources(self) -> typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "ResourceInstanceProperty"]]]:
        """``AWS::Greengrass::ResourceDefinitionVersion.Resources``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-resourcedefinitionversion.html#cfn-greengrass-resourcedefinitionversion-resources
        """
        return jsii.get(self, "resources")

    @resources.setter
    def resources(self, value: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "ResourceInstanceProperty"]]]):
        return jsii.set(self, "resources", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnResourceDefinitionVersion.GroupOwnerSettingProperty", jsii_struct_bases=[], name_mapping={'auto_add_group_owner': 'autoAddGroupOwner', 'group_owner': 'groupOwner'})
    class GroupOwnerSettingProperty():
        def __init__(self, *, auto_add_group_owner: typing.Union[bool, aws_cdk.core.IResolvable], group_owner: typing.Optional[str]=None):
            """
            :param auto_add_group_owner: ``CfnResourceDefinitionVersion.GroupOwnerSettingProperty.AutoAddGroupOwner``.
            :param group_owner: ``CfnResourceDefinitionVersion.GroupOwnerSettingProperty.GroupOwner``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-groupownersetting.html
            """
            self._values = {
                'auto_add_group_owner': auto_add_group_owner,
            }
            if group_owner is not None: self._values["group_owner"] = group_owner

        @property
        def auto_add_group_owner(self) -> typing.Union[bool, aws_cdk.core.IResolvable]:
            """``CfnResourceDefinitionVersion.GroupOwnerSettingProperty.AutoAddGroupOwner``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-groupownersetting.html#cfn-greengrass-resourcedefinitionversion-groupownersetting-autoaddgroupowner
            """
            return self._values.get('auto_add_group_owner')

        @property
        def group_owner(self) -> typing.Optional[str]:
            """``CfnResourceDefinitionVersion.GroupOwnerSettingProperty.GroupOwner``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-groupownersetting.html#cfn-greengrass-resourcedefinitionversion-groupownersetting-groupowner
            """
            return self._values.get('group_owner')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'GroupOwnerSettingProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnResourceDefinitionVersion.LocalDeviceResourceDataProperty", jsii_struct_bases=[], name_mapping={'source_path': 'sourcePath', 'group_owner_setting': 'groupOwnerSetting'})
    class LocalDeviceResourceDataProperty():
        def __init__(self, *, source_path: str, group_owner_setting: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnResourceDefinitionVersion.GroupOwnerSettingProperty"]]]=None):
            """
            :param source_path: ``CfnResourceDefinitionVersion.LocalDeviceResourceDataProperty.SourcePath``.
            :param group_owner_setting: ``CfnResourceDefinitionVersion.LocalDeviceResourceDataProperty.GroupOwnerSetting``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-localdeviceresourcedata.html
            """
            self._values = {
                'source_path': source_path,
            }
            if group_owner_setting is not None: self._values["group_owner_setting"] = group_owner_setting

        @property
        def source_path(self) -> str:
            """``CfnResourceDefinitionVersion.LocalDeviceResourceDataProperty.SourcePath``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-localdeviceresourcedata.html#cfn-greengrass-resourcedefinitionversion-localdeviceresourcedata-sourcepath
            """
            return self._values.get('source_path')

        @property
        def group_owner_setting(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnResourceDefinitionVersion.GroupOwnerSettingProperty"]]]:
            """``CfnResourceDefinitionVersion.LocalDeviceResourceDataProperty.GroupOwnerSetting``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-localdeviceresourcedata.html#cfn-greengrass-resourcedefinitionversion-localdeviceresourcedata-groupownersetting
            """
            return self._values.get('group_owner_setting')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'LocalDeviceResourceDataProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnResourceDefinitionVersion.LocalVolumeResourceDataProperty", jsii_struct_bases=[], name_mapping={'destination_path': 'destinationPath', 'source_path': 'sourcePath', 'group_owner_setting': 'groupOwnerSetting'})
    class LocalVolumeResourceDataProperty():
        def __init__(self, *, destination_path: str, source_path: str, group_owner_setting: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnResourceDefinitionVersion.GroupOwnerSettingProperty"]]]=None):
            """
            :param destination_path: ``CfnResourceDefinitionVersion.LocalVolumeResourceDataProperty.DestinationPath``.
            :param source_path: ``CfnResourceDefinitionVersion.LocalVolumeResourceDataProperty.SourcePath``.
            :param group_owner_setting: ``CfnResourceDefinitionVersion.LocalVolumeResourceDataProperty.GroupOwnerSetting``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-localvolumeresourcedata.html
            """
            self._values = {
                'destination_path': destination_path,
                'source_path': source_path,
            }
            if group_owner_setting is not None: self._values["group_owner_setting"] = group_owner_setting

        @property
        def destination_path(self) -> str:
            """``CfnResourceDefinitionVersion.LocalVolumeResourceDataProperty.DestinationPath``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-localvolumeresourcedata.html#cfn-greengrass-resourcedefinitionversion-localvolumeresourcedata-destinationpath
            """
            return self._values.get('destination_path')

        @property
        def source_path(self) -> str:
            """``CfnResourceDefinitionVersion.LocalVolumeResourceDataProperty.SourcePath``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-localvolumeresourcedata.html#cfn-greengrass-resourcedefinitionversion-localvolumeresourcedata-sourcepath
            """
            return self._values.get('source_path')

        @property
        def group_owner_setting(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnResourceDefinitionVersion.GroupOwnerSettingProperty"]]]:
            """``CfnResourceDefinitionVersion.LocalVolumeResourceDataProperty.GroupOwnerSetting``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-localvolumeresourcedata.html#cfn-greengrass-resourcedefinitionversion-localvolumeresourcedata-groupownersetting
            """
            return self._values.get('group_owner_setting')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'LocalVolumeResourceDataProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnResourceDefinitionVersion.ResourceDataContainerProperty", jsii_struct_bases=[], name_mapping={'local_device_resource_data': 'localDeviceResourceData', 'local_volume_resource_data': 'localVolumeResourceData', 's3_machine_learning_model_resource_data': 's3MachineLearningModelResourceData', 'sage_maker_machine_learning_model_resource_data': 'sageMakerMachineLearningModelResourceData', 'secrets_manager_secret_resource_data': 'secretsManagerSecretResourceData'})
    class ResourceDataContainerProperty():
        def __init__(self, *, local_device_resource_data: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnResourceDefinitionVersion.LocalDeviceResourceDataProperty"]]]=None, local_volume_resource_data: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnResourceDefinitionVersion.LocalVolumeResourceDataProperty"]]]=None, s3_machine_learning_model_resource_data: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnResourceDefinitionVersion.S3MachineLearningModelResourceDataProperty"]]]=None, sage_maker_machine_learning_model_resource_data: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnResourceDefinitionVersion.SageMakerMachineLearningModelResourceDataProperty"]]]=None, secrets_manager_secret_resource_data: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnResourceDefinitionVersion.SecretsManagerSecretResourceDataProperty"]]]=None):
            """
            :param local_device_resource_data: ``CfnResourceDefinitionVersion.ResourceDataContainerProperty.LocalDeviceResourceData``.
            :param local_volume_resource_data: ``CfnResourceDefinitionVersion.ResourceDataContainerProperty.LocalVolumeResourceData``.
            :param s3_machine_learning_model_resource_data: ``CfnResourceDefinitionVersion.ResourceDataContainerProperty.S3MachineLearningModelResourceData``.
            :param sage_maker_machine_learning_model_resource_data: ``CfnResourceDefinitionVersion.ResourceDataContainerProperty.SageMakerMachineLearningModelResourceData``.
            :param secrets_manager_secret_resource_data: ``CfnResourceDefinitionVersion.ResourceDataContainerProperty.SecretsManagerSecretResourceData``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-resourcedatacontainer.html
            """
            self._values = {
            }
            if local_device_resource_data is not None: self._values["local_device_resource_data"] = local_device_resource_data
            if local_volume_resource_data is not None: self._values["local_volume_resource_data"] = local_volume_resource_data
            if s3_machine_learning_model_resource_data is not None: self._values["s3_machine_learning_model_resource_data"] = s3_machine_learning_model_resource_data
            if sage_maker_machine_learning_model_resource_data is not None: self._values["sage_maker_machine_learning_model_resource_data"] = sage_maker_machine_learning_model_resource_data
            if secrets_manager_secret_resource_data is not None: self._values["secrets_manager_secret_resource_data"] = secrets_manager_secret_resource_data

        @property
        def local_device_resource_data(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnResourceDefinitionVersion.LocalDeviceResourceDataProperty"]]]:
            """``CfnResourceDefinitionVersion.ResourceDataContainerProperty.LocalDeviceResourceData``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-resourcedatacontainer.html#cfn-greengrass-resourcedefinitionversion-resourcedatacontainer-localdeviceresourcedata
            """
            return self._values.get('local_device_resource_data')

        @property
        def local_volume_resource_data(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnResourceDefinitionVersion.LocalVolumeResourceDataProperty"]]]:
            """``CfnResourceDefinitionVersion.ResourceDataContainerProperty.LocalVolumeResourceData``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-resourcedatacontainer.html#cfn-greengrass-resourcedefinitionversion-resourcedatacontainer-localvolumeresourcedata
            """
            return self._values.get('local_volume_resource_data')

        @property
        def s3_machine_learning_model_resource_data(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnResourceDefinitionVersion.S3MachineLearningModelResourceDataProperty"]]]:
            """``CfnResourceDefinitionVersion.ResourceDataContainerProperty.S3MachineLearningModelResourceData``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-resourcedatacontainer.html#cfn-greengrass-resourcedefinitionversion-resourcedatacontainer-s3machinelearningmodelresourcedata
            """
            return self._values.get('s3_machine_learning_model_resource_data')

        @property
        def sage_maker_machine_learning_model_resource_data(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnResourceDefinitionVersion.SageMakerMachineLearningModelResourceDataProperty"]]]:
            """``CfnResourceDefinitionVersion.ResourceDataContainerProperty.SageMakerMachineLearningModelResourceData``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-resourcedatacontainer.html#cfn-greengrass-resourcedefinitionversion-resourcedatacontainer-sagemakermachinelearningmodelresourcedata
            """
            return self._values.get('sage_maker_machine_learning_model_resource_data')

        @property
        def secrets_manager_secret_resource_data(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnResourceDefinitionVersion.SecretsManagerSecretResourceDataProperty"]]]:
            """``CfnResourceDefinitionVersion.ResourceDataContainerProperty.SecretsManagerSecretResourceData``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-resourcedatacontainer.html#cfn-greengrass-resourcedefinitionversion-resourcedatacontainer-secretsmanagersecretresourcedata
            """
            return self._values.get('secrets_manager_secret_resource_data')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'ResourceDataContainerProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnResourceDefinitionVersion.ResourceInstanceProperty", jsii_struct_bases=[], name_mapping={'id': 'id', 'name': 'name', 'resource_data_container': 'resourceDataContainer'})
    class ResourceInstanceProperty():
        def __init__(self, *, id: str, name: str, resource_data_container: typing.Union[aws_cdk.core.IResolvable, "CfnResourceDefinitionVersion.ResourceDataContainerProperty"]):
            """
            :param id: ``CfnResourceDefinitionVersion.ResourceInstanceProperty.Id``.
            :param name: ``CfnResourceDefinitionVersion.ResourceInstanceProperty.Name``.
            :param resource_data_container: ``CfnResourceDefinitionVersion.ResourceInstanceProperty.ResourceDataContainer``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-resourceinstance.html
            """
            self._values = {
                'id': id,
                'name': name,
                'resource_data_container': resource_data_container,
            }

        @property
        def id(self) -> str:
            """``CfnResourceDefinitionVersion.ResourceInstanceProperty.Id``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-resourceinstance.html#cfn-greengrass-resourcedefinitionversion-resourceinstance-id
            """
            return self._values.get('id')

        @property
        def name(self) -> str:
            """``CfnResourceDefinitionVersion.ResourceInstanceProperty.Name``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-resourceinstance.html#cfn-greengrass-resourcedefinitionversion-resourceinstance-name
            """
            return self._values.get('name')

        @property
        def resource_data_container(self) -> typing.Union[aws_cdk.core.IResolvable, "CfnResourceDefinitionVersion.ResourceDataContainerProperty"]:
            """``CfnResourceDefinitionVersion.ResourceInstanceProperty.ResourceDataContainer``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-resourceinstance.html#cfn-greengrass-resourcedefinitionversion-resourceinstance-resourcedatacontainer
            """
            return self._values.get('resource_data_container')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'ResourceInstanceProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnResourceDefinitionVersion.S3MachineLearningModelResourceDataProperty", jsii_struct_bases=[], name_mapping={'destination_path': 'destinationPath', 's3_uri': 's3Uri'})
    class S3MachineLearningModelResourceDataProperty():
        def __init__(self, *, destination_path: str, s3_uri: str):
            """
            :param destination_path: ``CfnResourceDefinitionVersion.S3MachineLearningModelResourceDataProperty.DestinationPath``.
            :param s3_uri: ``CfnResourceDefinitionVersion.S3MachineLearningModelResourceDataProperty.S3Uri``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-s3machinelearningmodelresourcedata.html
            """
            self._values = {
                'destination_path': destination_path,
                's3_uri': s3_uri,
            }

        @property
        def destination_path(self) -> str:
            """``CfnResourceDefinitionVersion.S3MachineLearningModelResourceDataProperty.DestinationPath``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-s3machinelearningmodelresourcedata.html#cfn-greengrass-resourcedefinitionversion-s3machinelearningmodelresourcedata-destinationpath
            """
            return self._values.get('destination_path')

        @property
        def s3_uri(self) -> str:
            """``CfnResourceDefinitionVersion.S3MachineLearningModelResourceDataProperty.S3Uri``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-s3machinelearningmodelresourcedata.html#cfn-greengrass-resourcedefinitionversion-s3machinelearningmodelresourcedata-s3uri
            """
            return self._values.get('s3_uri')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'S3MachineLearningModelResourceDataProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnResourceDefinitionVersion.SageMakerMachineLearningModelResourceDataProperty", jsii_struct_bases=[], name_mapping={'destination_path': 'destinationPath', 'sage_maker_job_arn': 'sageMakerJobArn'})
    class SageMakerMachineLearningModelResourceDataProperty():
        def __init__(self, *, destination_path: str, sage_maker_job_arn: str):
            """
            :param destination_path: ``CfnResourceDefinitionVersion.SageMakerMachineLearningModelResourceDataProperty.DestinationPath``.
            :param sage_maker_job_arn: ``CfnResourceDefinitionVersion.SageMakerMachineLearningModelResourceDataProperty.SageMakerJobArn``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-sagemakermachinelearningmodelresourcedata.html
            """
            self._values = {
                'destination_path': destination_path,
                'sage_maker_job_arn': sage_maker_job_arn,
            }

        @property
        def destination_path(self) -> str:
            """``CfnResourceDefinitionVersion.SageMakerMachineLearningModelResourceDataProperty.DestinationPath``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-sagemakermachinelearningmodelresourcedata.html#cfn-greengrass-resourcedefinitionversion-sagemakermachinelearningmodelresourcedata-destinationpath
            """
            return self._values.get('destination_path')

        @property
        def sage_maker_job_arn(self) -> str:
            """``CfnResourceDefinitionVersion.SageMakerMachineLearningModelResourceDataProperty.SageMakerJobArn``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-sagemakermachinelearningmodelresourcedata.html#cfn-greengrass-resourcedefinitionversion-sagemakermachinelearningmodelresourcedata-sagemakerjobarn
            """
            return self._values.get('sage_maker_job_arn')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'SageMakerMachineLearningModelResourceDataProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnResourceDefinitionVersion.SecretsManagerSecretResourceDataProperty", jsii_struct_bases=[], name_mapping={'arn': 'arn', 'additional_staging_labels_to_download': 'additionalStagingLabelsToDownload'})
    class SecretsManagerSecretResourceDataProperty():
        def __init__(self, *, arn: str, additional_staging_labels_to_download: typing.Optional[typing.List[str]]=None):
            """
            :param arn: ``CfnResourceDefinitionVersion.SecretsManagerSecretResourceDataProperty.ARN``.
            :param additional_staging_labels_to_download: ``CfnResourceDefinitionVersion.SecretsManagerSecretResourceDataProperty.AdditionalStagingLabelsToDownload``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-secretsmanagersecretresourcedata.html
            """
            self._values = {
                'arn': arn,
            }
            if additional_staging_labels_to_download is not None: self._values["additional_staging_labels_to_download"] = additional_staging_labels_to_download

        @property
        def arn(self) -> str:
            """``CfnResourceDefinitionVersion.SecretsManagerSecretResourceDataProperty.ARN``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-secretsmanagersecretresourcedata.html#cfn-greengrass-resourcedefinitionversion-secretsmanagersecretresourcedata-arn
            """
            return self._values.get('arn')

        @property
        def additional_staging_labels_to_download(self) -> typing.Optional[typing.List[str]]:
            """``CfnResourceDefinitionVersion.SecretsManagerSecretResourceDataProperty.AdditionalStagingLabelsToDownload``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-secretsmanagersecretresourcedata.html#cfn-greengrass-resourcedefinitionversion-secretsmanagersecretresourcedata-additionalstaginglabelstodownload
            """
            return self._values.get('additional_staging_labels_to_download')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'SecretsManagerSecretResourceDataProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



@jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnResourceDefinitionVersionProps", jsii_struct_bases=[], name_mapping={'resource_definition_id': 'resourceDefinitionId', 'resources': 'resources'})
class CfnResourceDefinitionVersionProps():
    def __init__(self, *, resource_definition_id: str, resources: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnResourceDefinitionVersion.ResourceInstanceProperty"]]]):
        """Properties for defining a ``AWS::Greengrass::ResourceDefinitionVersion``.

        :param resource_definition_id: ``AWS::Greengrass::ResourceDefinitionVersion.ResourceDefinitionId``.
        :param resources: ``AWS::Greengrass::ResourceDefinitionVersion.Resources``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-resourcedefinitionversion.html
        """
        self._values = {
            'resource_definition_id': resource_definition_id,
            'resources': resources,
        }

    @property
    def resource_definition_id(self) -> str:
        """``AWS::Greengrass::ResourceDefinitionVersion.ResourceDefinitionId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-resourcedefinitionversion.html#cfn-greengrass-resourcedefinitionversion-resourcedefinitionid
        """
        return self._values.get('resource_definition_id')

    @property
    def resources(self) -> typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnResourceDefinitionVersion.ResourceInstanceProperty"]]]:
        """``AWS::Greengrass::ResourceDefinitionVersion.Resources``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-resourcedefinitionversion.html#cfn-greengrass-resourcedefinitionversion-resources
        """
        return self._values.get('resources')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnResourceDefinitionVersionProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnSubscriptionDefinition(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-greengrass.CfnSubscriptionDefinition"):
    """A CloudFormation ``AWS::Greengrass::SubscriptionDefinition``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-subscriptiondefinition.html
    cloudformationResource:
    :cloudformationResource:: AWS::Greengrass::SubscriptionDefinition
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, name: str, initial_version: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["SubscriptionDefinitionVersionProperty"]]]=None, tags: typing.Any=None) -> None:
        """Create a new ``AWS::Greengrass::SubscriptionDefinition``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param name: ``AWS::Greengrass::SubscriptionDefinition.Name``.
        :param initial_version: ``AWS::Greengrass::SubscriptionDefinition.InitialVersion``.
        :param tags: ``AWS::Greengrass::SubscriptionDefinition.Tags``.
        """
        props = CfnSubscriptionDefinitionProps(name=name, initial_version=initial_version, tags=tags)

        jsii.create(CfnSubscriptionDefinition, self, [scope, id, props])

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
    @jsii.member(jsii_name="attrId")
    def attr_id(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: Id
        """
        return jsii.get(self, "attrId")

    @property
    @jsii.member(jsii_name="attrLatestVersionArn")
    def attr_latest_version_arn(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: LatestVersionArn
        """
        return jsii.get(self, "attrLatestVersionArn")

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
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        """``AWS::Greengrass::SubscriptionDefinition.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-subscriptiondefinition.html#cfn-greengrass-subscriptiondefinition-tags
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> str:
        """``AWS::Greengrass::SubscriptionDefinition.Name``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-subscriptiondefinition.html#cfn-greengrass-subscriptiondefinition-name
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: str):
        return jsii.set(self, "name", value)

    @property
    @jsii.member(jsii_name="initialVersion")
    def initial_version(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["SubscriptionDefinitionVersionProperty"]]]:
        """``AWS::Greengrass::SubscriptionDefinition.InitialVersion``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-subscriptiondefinition.html#cfn-greengrass-subscriptiondefinition-initialversion
        """
        return jsii.get(self, "initialVersion")

    @initial_version.setter
    def initial_version(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["SubscriptionDefinitionVersionProperty"]]]):
        return jsii.set(self, "initialVersion", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnSubscriptionDefinition.SubscriptionDefinitionVersionProperty", jsii_struct_bases=[], name_mapping={'subscriptions': 'subscriptions'})
    class SubscriptionDefinitionVersionProperty():
        def __init__(self, *, subscriptions: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnSubscriptionDefinition.SubscriptionProperty"]]]):
            """
            :param subscriptions: ``CfnSubscriptionDefinition.SubscriptionDefinitionVersionProperty.Subscriptions``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-subscriptiondefinition-subscriptiondefinitionversion.html
            """
            self._values = {
                'subscriptions': subscriptions,
            }

        @property
        def subscriptions(self) -> typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnSubscriptionDefinition.SubscriptionProperty"]]]:
            """``CfnSubscriptionDefinition.SubscriptionDefinitionVersionProperty.Subscriptions``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-subscriptiondefinition-subscriptiondefinitionversion.html#cfn-greengrass-subscriptiondefinition-subscriptiondefinitionversion-subscriptions
            """
            return self._values.get('subscriptions')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'SubscriptionDefinitionVersionProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnSubscriptionDefinition.SubscriptionProperty", jsii_struct_bases=[], name_mapping={'id': 'id', 'source': 'source', 'subject': 'subject', 'target': 'target'})
    class SubscriptionProperty():
        def __init__(self, *, id: str, source: str, subject: str, target: str):
            """
            :param id: ``CfnSubscriptionDefinition.SubscriptionProperty.Id``.
            :param source: ``CfnSubscriptionDefinition.SubscriptionProperty.Source``.
            :param subject: ``CfnSubscriptionDefinition.SubscriptionProperty.Subject``.
            :param target: ``CfnSubscriptionDefinition.SubscriptionProperty.Target``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-subscriptiondefinition-subscription.html
            """
            self._values = {
                'id': id,
                'source': source,
                'subject': subject,
                'target': target,
            }

        @property
        def id(self) -> str:
            """``CfnSubscriptionDefinition.SubscriptionProperty.Id``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-subscriptiondefinition-subscription.html#cfn-greengrass-subscriptiondefinition-subscription-id
            """
            return self._values.get('id')

        @property
        def source(self) -> str:
            """``CfnSubscriptionDefinition.SubscriptionProperty.Source``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-subscriptiondefinition-subscription.html#cfn-greengrass-subscriptiondefinition-subscription-source
            """
            return self._values.get('source')

        @property
        def subject(self) -> str:
            """``CfnSubscriptionDefinition.SubscriptionProperty.Subject``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-subscriptiondefinition-subscription.html#cfn-greengrass-subscriptiondefinition-subscription-subject
            """
            return self._values.get('subject')

        @property
        def target(self) -> str:
            """``CfnSubscriptionDefinition.SubscriptionProperty.Target``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-subscriptiondefinition-subscription.html#cfn-greengrass-subscriptiondefinition-subscription-target
            """
            return self._values.get('target')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'SubscriptionProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



@jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnSubscriptionDefinitionProps", jsii_struct_bases=[], name_mapping={'name': 'name', 'initial_version': 'initialVersion', 'tags': 'tags'})
class CfnSubscriptionDefinitionProps():
    def __init__(self, *, name: str, initial_version: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnSubscriptionDefinition.SubscriptionDefinitionVersionProperty"]]]=None, tags: typing.Any=None):
        """Properties for defining a ``AWS::Greengrass::SubscriptionDefinition``.

        :param name: ``AWS::Greengrass::SubscriptionDefinition.Name``.
        :param initial_version: ``AWS::Greengrass::SubscriptionDefinition.InitialVersion``.
        :param tags: ``AWS::Greengrass::SubscriptionDefinition.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-subscriptiondefinition.html
        """
        self._values = {
            'name': name,
        }
        if initial_version is not None: self._values["initial_version"] = initial_version
        if tags is not None: self._values["tags"] = tags

    @property
    def name(self) -> str:
        """``AWS::Greengrass::SubscriptionDefinition.Name``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-subscriptiondefinition.html#cfn-greengrass-subscriptiondefinition-name
        """
        return self._values.get('name')

    @property
    def initial_version(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnSubscriptionDefinition.SubscriptionDefinitionVersionProperty"]]]:
        """``AWS::Greengrass::SubscriptionDefinition.InitialVersion``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-subscriptiondefinition.html#cfn-greengrass-subscriptiondefinition-initialversion
        """
        return self._values.get('initial_version')

    @property
    def tags(self) -> typing.Any:
        """``AWS::Greengrass::SubscriptionDefinition.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-subscriptiondefinition.html#cfn-greengrass-subscriptiondefinition-tags
        """
        return self._values.get('tags')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnSubscriptionDefinitionProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnSubscriptionDefinitionVersion(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-greengrass.CfnSubscriptionDefinitionVersion"):
    """A CloudFormation ``AWS::Greengrass::SubscriptionDefinitionVersion``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-subscriptiondefinitionversion.html
    cloudformationResource:
    :cloudformationResource:: AWS::Greengrass::SubscriptionDefinitionVersion
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, subscription_definition_id: str, subscriptions: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "SubscriptionProperty"]]]) -> None:
        """Create a new ``AWS::Greengrass::SubscriptionDefinitionVersion``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param subscription_definition_id: ``AWS::Greengrass::SubscriptionDefinitionVersion.SubscriptionDefinitionId``.
        :param subscriptions: ``AWS::Greengrass::SubscriptionDefinitionVersion.Subscriptions``.
        """
        props = CfnSubscriptionDefinitionVersionProps(subscription_definition_id=subscription_definition_id, subscriptions=subscriptions)

        jsii.create(CfnSubscriptionDefinitionVersion, self, [scope, id, props])

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
    @jsii.member(jsii_name="subscriptionDefinitionId")
    def subscription_definition_id(self) -> str:
        """``AWS::Greengrass::SubscriptionDefinitionVersion.SubscriptionDefinitionId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-subscriptiondefinitionversion.html#cfn-greengrass-subscriptiondefinitionversion-subscriptiondefinitionid
        """
        return jsii.get(self, "subscriptionDefinitionId")

    @subscription_definition_id.setter
    def subscription_definition_id(self, value: str):
        return jsii.set(self, "subscriptionDefinitionId", value)

    @property
    @jsii.member(jsii_name="subscriptions")
    def subscriptions(self) -> typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "SubscriptionProperty"]]]:
        """``AWS::Greengrass::SubscriptionDefinitionVersion.Subscriptions``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-subscriptiondefinitionversion.html#cfn-greengrass-subscriptiondefinitionversion-subscriptions
        """
        return jsii.get(self, "subscriptions")

    @subscriptions.setter
    def subscriptions(self, value: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "SubscriptionProperty"]]]):
        return jsii.set(self, "subscriptions", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnSubscriptionDefinitionVersion.SubscriptionProperty", jsii_struct_bases=[], name_mapping={'id': 'id', 'source': 'source', 'subject': 'subject', 'target': 'target'})
    class SubscriptionProperty():
        def __init__(self, *, id: str, source: str, subject: str, target: str):
            """
            :param id: ``CfnSubscriptionDefinitionVersion.SubscriptionProperty.Id``.
            :param source: ``CfnSubscriptionDefinitionVersion.SubscriptionProperty.Source``.
            :param subject: ``CfnSubscriptionDefinitionVersion.SubscriptionProperty.Subject``.
            :param target: ``CfnSubscriptionDefinitionVersion.SubscriptionProperty.Target``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-subscriptiondefinitionversion-subscription.html
            """
            self._values = {
                'id': id,
                'source': source,
                'subject': subject,
                'target': target,
            }

        @property
        def id(self) -> str:
            """``CfnSubscriptionDefinitionVersion.SubscriptionProperty.Id``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-subscriptiondefinitionversion-subscription.html#cfn-greengrass-subscriptiondefinitionversion-subscription-id
            """
            return self._values.get('id')

        @property
        def source(self) -> str:
            """``CfnSubscriptionDefinitionVersion.SubscriptionProperty.Source``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-subscriptiondefinitionversion-subscription.html#cfn-greengrass-subscriptiondefinitionversion-subscription-source
            """
            return self._values.get('source')

        @property
        def subject(self) -> str:
            """``CfnSubscriptionDefinitionVersion.SubscriptionProperty.Subject``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-subscriptiondefinitionversion-subscription.html#cfn-greengrass-subscriptiondefinitionversion-subscription-subject
            """
            return self._values.get('subject')

        @property
        def target(self) -> str:
            """``CfnSubscriptionDefinitionVersion.SubscriptionProperty.Target``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-subscriptiondefinitionversion-subscription.html#cfn-greengrass-subscriptiondefinitionversion-subscription-target
            """
            return self._values.get('target')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'SubscriptionProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



@jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnSubscriptionDefinitionVersionProps", jsii_struct_bases=[], name_mapping={'subscription_definition_id': 'subscriptionDefinitionId', 'subscriptions': 'subscriptions'})
class CfnSubscriptionDefinitionVersionProps():
    def __init__(self, *, subscription_definition_id: str, subscriptions: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnSubscriptionDefinitionVersion.SubscriptionProperty"]]]):
        """Properties for defining a ``AWS::Greengrass::SubscriptionDefinitionVersion``.

        :param subscription_definition_id: ``AWS::Greengrass::SubscriptionDefinitionVersion.SubscriptionDefinitionId``.
        :param subscriptions: ``AWS::Greengrass::SubscriptionDefinitionVersion.Subscriptions``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-subscriptiondefinitionversion.html
        """
        self._values = {
            'subscription_definition_id': subscription_definition_id,
            'subscriptions': subscriptions,
        }

    @property
    def subscription_definition_id(self) -> str:
        """``AWS::Greengrass::SubscriptionDefinitionVersion.SubscriptionDefinitionId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-subscriptiondefinitionversion.html#cfn-greengrass-subscriptiondefinitionversion-subscriptiondefinitionid
        """
        return self._values.get('subscription_definition_id')

    @property
    def subscriptions(self) -> typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnSubscriptionDefinitionVersion.SubscriptionProperty"]]]:
        """``AWS::Greengrass::SubscriptionDefinitionVersion.Subscriptions``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-subscriptiondefinitionversion.html#cfn-greengrass-subscriptiondefinitionversion-subscriptions
        """
        return self._values.get('subscriptions')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnSubscriptionDefinitionVersionProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


__all__ = ["CfnConnectorDefinition", "CfnConnectorDefinitionProps", "CfnConnectorDefinitionVersion", "CfnConnectorDefinitionVersionProps", "CfnCoreDefinition", "CfnCoreDefinitionProps", "CfnCoreDefinitionVersion", "CfnCoreDefinitionVersionProps", "CfnDeviceDefinition", "CfnDeviceDefinitionProps", "CfnDeviceDefinitionVersion", "CfnDeviceDefinitionVersionProps", "CfnFunctionDefinition", "CfnFunctionDefinitionProps", "CfnFunctionDefinitionVersion", "CfnFunctionDefinitionVersionProps", "CfnGroup", "CfnGroupProps", "CfnGroupVersion", "CfnGroupVersionProps", "CfnLoggerDefinition", "CfnLoggerDefinitionProps", "CfnLoggerDefinitionVersion", "CfnLoggerDefinitionVersionProps", "CfnResourceDefinition", "CfnResourceDefinitionProps", "CfnResourceDefinitionVersion", "CfnResourceDefinitionVersionProps", "CfnSubscriptionDefinition", "CfnSubscriptionDefinitionProps", "CfnSubscriptionDefinitionVersion", "CfnSubscriptionDefinitionVersionProps", "__jsii_assembly__"]

publication.publish()
