import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.core
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-iot1click", "1.15.0", __name__, "aws-iot1click@1.15.0.jsii.tgz")
class CfnDevice(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-iot1click.CfnDevice"):
    """A CloudFormation ``AWS::IoT1Click::Device``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot1click-device.html
    cloudformationResource:
    :cloudformationResource:: AWS::IoT1Click::Device
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, device_id: str, enabled: typing.Union[bool, aws_cdk.core.IResolvable]) -> None:
        """Create a new ``AWS::IoT1Click::Device``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param device_id: ``AWS::IoT1Click::Device.DeviceId``.
        :param enabled: ``AWS::IoT1Click::Device.Enabled``.
        """
        props = CfnDeviceProps(device_id=device_id, enabled=enabled)

        jsii.create(CfnDevice, self, [scope, id, props])

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
    @jsii.member(jsii_name="attrDeviceId")
    def attr_device_id(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: DeviceId
        """
        return jsii.get(self, "attrDeviceId")

    @property
    @jsii.member(jsii_name="attrEnabled")
    def attr_enabled(self) -> aws_cdk.core.IResolvable:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: Enabled
        """
        return jsii.get(self, "attrEnabled")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="deviceId")
    def device_id(self) -> str:
        """``AWS::IoT1Click::Device.DeviceId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot1click-device.html#cfn-iot1click-device-deviceid
        """
        return jsii.get(self, "deviceId")

    @device_id.setter
    def device_id(self, value: str):
        return jsii.set(self, "deviceId", value)

    @property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Union[bool, aws_cdk.core.IResolvable]:
        """``AWS::IoT1Click::Device.Enabled``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot1click-device.html#cfn-iot1click-device-enabled
        """
        return jsii.get(self, "enabled")

    @enabled.setter
    def enabled(self, value: typing.Union[bool, aws_cdk.core.IResolvable]):
        return jsii.set(self, "enabled", value)


@jsii.data_type(jsii_type="@aws-cdk/aws-iot1click.CfnDeviceProps", jsii_struct_bases=[], name_mapping={'device_id': 'deviceId', 'enabled': 'enabled'})
class CfnDeviceProps():
    def __init__(self, *, device_id: str, enabled: typing.Union[bool, aws_cdk.core.IResolvable]):
        """Properties for defining a ``AWS::IoT1Click::Device``.

        :param device_id: ``AWS::IoT1Click::Device.DeviceId``.
        :param enabled: ``AWS::IoT1Click::Device.Enabled``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot1click-device.html
        """
        self._values = {
            'device_id': device_id,
            'enabled': enabled,
        }

    @property
    def device_id(self) -> str:
        """``AWS::IoT1Click::Device.DeviceId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot1click-device.html#cfn-iot1click-device-deviceid
        """
        return self._values.get('device_id')

    @property
    def enabled(self) -> typing.Union[bool, aws_cdk.core.IResolvable]:
        """``AWS::IoT1Click::Device.Enabled``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot1click-device.html#cfn-iot1click-device-enabled
        """
        return self._values.get('enabled')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnDeviceProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnPlacement(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-iot1click.CfnPlacement"):
    """A CloudFormation ``AWS::IoT1Click::Placement``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot1click-placement.html
    cloudformationResource:
    :cloudformationResource:: AWS::IoT1Click::Placement
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, project_name: str, associated_devices: typing.Any=None, attributes: typing.Any=None, placement_name: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::IoT1Click::Placement``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param project_name: ``AWS::IoT1Click::Placement.ProjectName``.
        :param associated_devices: ``AWS::IoT1Click::Placement.AssociatedDevices``.
        :param attributes: ``AWS::IoT1Click::Placement.Attributes``.
        :param placement_name: ``AWS::IoT1Click::Placement.PlacementName``.
        """
        props = CfnPlacementProps(project_name=project_name, associated_devices=associated_devices, attributes=attributes, placement_name=placement_name)

        jsii.create(CfnPlacement, self, [scope, id, props])

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
    @jsii.member(jsii_name="attrPlacementName")
    def attr_placement_name(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: PlacementName
        """
        return jsii.get(self, "attrPlacementName")

    @property
    @jsii.member(jsii_name="attrProjectName")
    def attr_project_name(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: ProjectName
        """
        return jsii.get(self, "attrProjectName")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="associatedDevices")
    def associated_devices(self) -> typing.Any:
        """``AWS::IoT1Click::Placement.AssociatedDevices``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot1click-placement.html#cfn-iot1click-placement-associateddevices
        """
        return jsii.get(self, "associatedDevices")

    @associated_devices.setter
    def associated_devices(self, value: typing.Any):
        return jsii.set(self, "associatedDevices", value)

    @property
    @jsii.member(jsii_name="attributes")
    def attributes(self) -> typing.Any:
        """``AWS::IoT1Click::Placement.Attributes``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot1click-placement.html#cfn-iot1click-placement-attributes
        """
        return jsii.get(self, "attributes")

    @attributes.setter
    def attributes(self, value: typing.Any):
        return jsii.set(self, "attributes", value)

    @property
    @jsii.member(jsii_name="projectName")
    def project_name(self) -> str:
        """``AWS::IoT1Click::Placement.ProjectName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot1click-placement.html#cfn-iot1click-placement-projectname
        """
        return jsii.get(self, "projectName")

    @project_name.setter
    def project_name(self, value: str):
        return jsii.set(self, "projectName", value)

    @property
    @jsii.member(jsii_name="placementName")
    def placement_name(self) -> typing.Optional[str]:
        """``AWS::IoT1Click::Placement.PlacementName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot1click-placement.html#cfn-iot1click-placement-placementname
        """
        return jsii.get(self, "placementName")

    @placement_name.setter
    def placement_name(self, value: typing.Optional[str]):
        return jsii.set(self, "placementName", value)


@jsii.data_type(jsii_type="@aws-cdk/aws-iot1click.CfnPlacementProps", jsii_struct_bases=[], name_mapping={'project_name': 'projectName', 'associated_devices': 'associatedDevices', 'attributes': 'attributes', 'placement_name': 'placementName'})
class CfnPlacementProps():
    def __init__(self, *, project_name: str, associated_devices: typing.Any=None, attributes: typing.Any=None, placement_name: typing.Optional[str]=None):
        """Properties for defining a ``AWS::IoT1Click::Placement``.

        :param project_name: ``AWS::IoT1Click::Placement.ProjectName``.
        :param associated_devices: ``AWS::IoT1Click::Placement.AssociatedDevices``.
        :param attributes: ``AWS::IoT1Click::Placement.Attributes``.
        :param placement_name: ``AWS::IoT1Click::Placement.PlacementName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot1click-placement.html
        """
        self._values = {
            'project_name': project_name,
        }
        if associated_devices is not None: self._values["associated_devices"] = associated_devices
        if attributes is not None: self._values["attributes"] = attributes
        if placement_name is not None: self._values["placement_name"] = placement_name

    @property
    def project_name(self) -> str:
        """``AWS::IoT1Click::Placement.ProjectName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot1click-placement.html#cfn-iot1click-placement-projectname
        """
        return self._values.get('project_name')

    @property
    def associated_devices(self) -> typing.Any:
        """``AWS::IoT1Click::Placement.AssociatedDevices``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot1click-placement.html#cfn-iot1click-placement-associateddevices
        """
        return self._values.get('associated_devices')

    @property
    def attributes(self) -> typing.Any:
        """``AWS::IoT1Click::Placement.Attributes``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot1click-placement.html#cfn-iot1click-placement-attributes
        """
        return self._values.get('attributes')

    @property
    def placement_name(self) -> typing.Optional[str]:
        """``AWS::IoT1Click::Placement.PlacementName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot1click-placement.html#cfn-iot1click-placement-placementname
        """
        return self._values.get('placement_name')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnPlacementProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnProject(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-iot1click.CfnProject"):
    """A CloudFormation ``AWS::IoT1Click::Project``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot1click-project.html
    cloudformationResource:
    :cloudformationResource:: AWS::IoT1Click::Project
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, placement_template: typing.Union["PlacementTemplateProperty", aws_cdk.core.IResolvable], description: typing.Optional[str]=None, project_name: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::IoT1Click::Project``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param placement_template: ``AWS::IoT1Click::Project.PlacementTemplate``.
        :param description: ``AWS::IoT1Click::Project.Description``.
        :param project_name: ``AWS::IoT1Click::Project.ProjectName``.
        """
        props = CfnProjectProps(placement_template=placement_template, description=description, project_name=project_name)

        jsii.create(CfnProject, self, [scope, id, props])

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
    @jsii.member(jsii_name="attrProjectName")
    def attr_project_name(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: ProjectName
        """
        return jsii.get(self, "attrProjectName")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="placementTemplate")
    def placement_template(self) -> typing.Union["PlacementTemplateProperty", aws_cdk.core.IResolvable]:
        """``AWS::IoT1Click::Project.PlacementTemplate``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot1click-project.html#cfn-iot1click-project-placementtemplate
        """
        return jsii.get(self, "placementTemplate")

    @placement_template.setter
    def placement_template(self, value: typing.Union["PlacementTemplateProperty", aws_cdk.core.IResolvable]):
        return jsii.set(self, "placementTemplate", value)

    @property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[str]:
        """``AWS::IoT1Click::Project.Description``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot1click-project.html#cfn-iot1click-project-description
        """
        return jsii.get(self, "description")

    @description.setter
    def description(self, value: typing.Optional[str]):
        return jsii.set(self, "description", value)

    @property
    @jsii.member(jsii_name="projectName")
    def project_name(self) -> typing.Optional[str]:
        """``AWS::IoT1Click::Project.ProjectName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot1click-project.html#cfn-iot1click-project-projectname
        """
        return jsii.get(self, "projectName")

    @project_name.setter
    def project_name(self, value: typing.Optional[str]):
        return jsii.set(self, "projectName", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-iot1click.CfnProject.DeviceTemplateProperty", jsii_struct_bases=[], name_mapping={'callback_overrides': 'callbackOverrides', 'device_type': 'deviceType'})
    class DeviceTemplateProperty():
        def __init__(self, *, callback_overrides: typing.Any=None, device_type: typing.Optional[str]=None):
            """
            :param callback_overrides: ``CfnProject.DeviceTemplateProperty.CallbackOverrides``.
            :param device_type: ``CfnProject.DeviceTemplateProperty.DeviceType``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot1click-project-devicetemplate.html
            """
            self._values = {
            }
            if callback_overrides is not None: self._values["callback_overrides"] = callback_overrides
            if device_type is not None: self._values["device_type"] = device_type

        @property
        def callback_overrides(self) -> typing.Any:
            """``CfnProject.DeviceTemplateProperty.CallbackOverrides``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot1click-project-devicetemplate.html#cfn-iot1click-project-devicetemplate-callbackoverrides
            """
            return self._values.get('callback_overrides')

        @property
        def device_type(self) -> typing.Optional[str]:
            """``CfnProject.DeviceTemplateProperty.DeviceType``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot1click-project-devicetemplate.html#cfn-iot1click-project-devicetemplate-devicetype
            """
            return self._values.get('device_type')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'DeviceTemplateProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-iot1click.CfnProject.PlacementTemplateProperty", jsii_struct_bases=[], name_mapping={'default_attributes': 'defaultAttributes', 'device_templates': 'deviceTemplates'})
    class PlacementTemplateProperty():
        def __init__(self, *, default_attributes: typing.Any=None, device_templates: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnProject.DeviceTemplateProperty"]]]=None):
            """
            :param default_attributes: ``CfnProject.PlacementTemplateProperty.DefaultAttributes``.
            :param device_templates: ``CfnProject.PlacementTemplateProperty.DeviceTemplates``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot1click-project-placementtemplate.html
            """
            self._values = {
            }
            if default_attributes is not None: self._values["default_attributes"] = default_attributes
            if device_templates is not None: self._values["device_templates"] = device_templates

        @property
        def default_attributes(self) -> typing.Any:
            """``CfnProject.PlacementTemplateProperty.DefaultAttributes``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot1click-project-placementtemplate.html#cfn-iot1click-project-placementtemplate-defaultattributes
            """
            return self._values.get('default_attributes')

        @property
        def device_templates(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnProject.DeviceTemplateProperty"]]]:
            """``CfnProject.PlacementTemplateProperty.DeviceTemplates``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot1click-project-placementtemplate.html#cfn-iot1click-project-placementtemplate-devicetemplates
            """
            return self._values.get('device_templates')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'PlacementTemplateProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



@jsii.data_type(jsii_type="@aws-cdk/aws-iot1click.CfnProjectProps", jsii_struct_bases=[], name_mapping={'placement_template': 'placementTemplate', 'description': 'description', 'project_name': 'projectName'})
class CfnProjectProps():
    def __init__(self, *, placement_template: typing.Union["CfnProject.PlacementTemplateProperty", aws_cdk.core.IResolvable], description: typing.Optional[str]=None, project_name: typing.Optional[str]=None):
        """Properties for defining a ``AWS::IoT1Click::Project``.

        :param placement_template: ``AWS::IoT1Click::Project.PlacementTemplate``.
        :param description: ``AWS::IoT1Click::Project.Description``.
        :param project_name: ``AWS::IoT1Click::Project.ProjectName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot1click-project.html
        """
        self._values = {
            'placement_template': placement_template,
        }
        if description is not None: self._values["description"] = description
        if project_name is not None: self._values["project_name"] = project_name

    @property
    def placement_template(self) -> typing.Union["CfnProject.PlacementTemplateProperty", aws_cdk.core.IResolvable]:
        """``AWS::IoT1Click::Project.PlacementTemplate``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot1click-project.html#cfn-iot1click-project-placementtemplate
        """
        return self._values.get('placement_template')

    @property
    def description(self) -> typing.Optional[str]:
        """``AWS::IoT1Click::Project.Description``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot1click-project.html#cfn-iot1click-project-description
        """
        return self._values.get('description')

    @property
    def project_name(self) -> typing.Optional[str]:
        """``AWS::IoT1Click::Project.ProjectName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot1click-project.html#cfn-iot1click-project-projectname
        """
        return self._values.get('project_name')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnProjectProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


__all__ = ["CfnDevice", "CfnDeviceProps", "CfnPlacement", "CfnPlacementProps", "CfnProject", "CfnProjectProps", "__jsii_assembly__"]

publication.publish()
