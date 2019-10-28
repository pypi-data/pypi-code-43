import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.core
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-workspaces", "1.15.0", __name__, "aws-workspaces@1.15.0.jsii.tgz")
class CfnWorkspace(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-workspaces.CfnWorkspace"):
    """A CloudFormation ``AWS::WorkSpaces::Workspace``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-workspaces-workspace.html
    cloudformationResource:
    :cloudformationResource:: AWS::WorkSpaces::Workspace
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, bundle_id: str, directory_id: str, user_name: str, root_volume_encryption_enabled: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None, user_volume_encryption_enabled: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, volume_encryption_key: typing.Optional[str]=None, workspace_properties: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["WorkspacePropertiesProperty"]]]=None) -> None:
        """Create a new ``AWS::WorkSpaces::Workspace``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param bundle_id: ``AWS::WorkSpaces::Workspace.BundleId``.
        :param directory_id: ``AWS::WorkSpaces::Workspace.DirectoryId``.
        :param user_name: ``AWS::WorkSpaces::Workspace.UserName``.
        :param root_volume_encryption_enabled: ``AWS::WorkSpaces::Workspace.RootVolumeEncryptionEnabled``.
        :param tags: ``AWS::WorkSpaces::Workspace.Tags``.
        :param user_volume_encryption_enabled: ``AWS::WorkSpaces::Workspace.UserVolumeEncryptionEnabled``.
        :param volume_encryption_key: ``AWS::WorkSpaces::Workspace.VolumeEncryptionKey``.
        :param workspace_properties: ``AWS::WorkSpaces::Workspace.WorkspaceProperties``.
        """
        props = CfnWorkspaceProps(bundle_id=bundle_id, directory_id=directory_id, user_name=user_name, root_volume_encryption_enabled=root_volume_encryption_enabled, tags=tags, user_volume_encryption_enabled=user_volume_encryption_enabled, volume_encryption_key=volume_encryption_key, workspace_properties=workspace_properties)

        jsii.create(CfnWorkspace, self, [scope, id, props])

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
        """``AWS::WorkSpaces::Workspace.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-workspaces-workspace.html#cfn-workspaces-workspace-tags
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="bundleId")
    def bundle_id(self) -> str:
        """``AWS::WorkSpaces::Workspace.BundleId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-workspaces-workspace.html#cfn-workspaces-workspace-bundleid
        """
        return jsii.get(self, "bundleId")

    @bundle_id.setter
    def bundle_id(self, value: str):
        return jsii.set(self, "bundleId", value)

    @property
    @jsii.member(jsii_name="directoryId")
    def directory_id(self) -> str:
        """``AWS::WorkSpaces::Workspace.DirectoryId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-workspaces-workspace.html#cfn-workspaces-workspace-directoryid
        """
        return jsii.get(self, "directoryId")

    @directory_id.setter
    def directory_id(self, value: str):
        return jsii.set(self, "directoryId", value)

    @property
    @jsii.member(jsii_name="userName")
    def user_name(self) -> str:
        """``AWS::WorkSpaces::Workspace.UserName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-workspaces-workspace.html#cfn-workspaces-workspace-username
        """
        return jsii.get(self, "userName")

    @user_name.setter
    def user_name(self, value: str):
        return jsii.set(self, "userName", value)

    @property
    @jsii.member(jsii_name="rootVolumeEncryptionEnabled")
    def root_volume_encryption_enabled(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::WorkSpaces::Workspace.RootVolumeEncryptionEnabled``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-workspaces-workspace.html#cfn-workspaces-workspace-rootvolumeencryptionenabled
        """
        return jsii.get(self, "rootVolumeEncryptionEnabled")

    @root_volume_encryption_enabled.setter
    def root_volume_encryption_enabled(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "rootVolumeEncryptionEnabled", value)

    @property
    @jsii.member(jsii_name="userVolumeEncryptionEnabled")
    def user_volume_encryption_enabled(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::WorkSpaces::Workspace.UserVolumeEncryptionEnabled``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-workspaces-workspace.html#cfn-workspaces-workspace-uservolumeencryptionenabled
        """
        return jsii.get(self, "userVolumeEncryptionEnabled")

    @user_volume_encryption_enabled.setter
    def user_volume_encryption_enabled(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "userVolumeEncryptionEnabled", value)

    @property
    @jsii.member(jsii_name="volumeEncryptionKey")
    def volume_encryption_key(self) -> typing.Optional[str]:
        """``AWS::WorkSpaces::Workspace.VolumeEncryptionKey``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-workspaces-workspace.html#cfn-workspaces-workspace-volumeencryptionkey
        """
        return jsii.get(self, "volumeEncryptionKey")

    @volume_encryption_key.setter
    def volume_encryption_key(self, value: typing.Optional[str]):
        return jsii.set(self, "volumeEncryptionKey", value)

    @property
    @jsii.member(jsii_name="workspaceProperties")
    def workspace_properties(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["WorkspacePropertiesProperty"]]]:
        """``AWS::WorkSpaces::Workspace.WorkspaceProperties``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-workspaces-workspace.html#cfn-workspaces-workspace-workspaceproperties
        """
        return jsii.get(self, "workspaceProperties")

    @workspace_properties.setter
    def workspace_properties(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["WorkspacePropertiesProperty"]]]):
        return jsii.set(self, "workspaceProperties", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-workspaces.CfnWorkspace.WorkspacePropertiesProperty", jsii_struct_bases=[], name_mapping={'compute_type_name': 'computeTypeName', 'root_volume_size_gib': 'rootVolumeSizeGib', 'running_mode': 'runningMode', 'running_mode_auto_stop_timeout_in_minutes': 'runningModeAutoStopTimeoutInMinutes', 'user_volume_size_gib': 'userVolumeSizeGib'})
    class WorkspacePropertiesProperty():
        def __init__(self, *, compute_type_name: typing.Optional[str]=None, root_volume_size_gib: typing.Optional[jsii.Number]=None, running_mode: typing.Optional[str]=None, running_mode_auto_stop_timeout_in_minutes: typing.Optional[jsii.Number]=None, user_volume_size_gib: typing.Optional[jsii.Number]=None):
            """
            :param compute_type_name: ``CfnWorkspace.WorkspacePropertiesProperty.ComputeTypeName``.
            :param root_volume_size_gib: ``CfnWorkspace.WorkspacePropertiesProperty.RootVolumeSizeGib``.
            :param running_mode: ``CfnWorkspace.WorkspacePropertiesProperty.RunningMode``.
            :param running_mode_auto_stop_timeout_in_minutes: ``CfnWorkspace.WorkspacePropertiesProperty.RunningModeAutoStopTimeoutInMinutes``.
            :param user_volume_size_gib: ``CfnWorkspace.WorkspacePropertiesProperty.UserVolumeSizeGib``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-workspaces-workspace-workspaceproperties.html
            """
            self._values = {
            }
            if compute_type_name is not None: self._values["compute_type_name"] = compute_type_name
            if root_volume_size_gib is not None: self._values["root_volume_size_gib"] = root_volume_size_gib
            if running_mode is not None: self._values["running_mode"] = running_mode
            if running_mode_auto_stop_timeout_in_minutes is not None: self._values["running_mode_auto_stop_timeout_in_minutes"] = running_mode_auto_stop_timeout_in_minutes
            if user_volume_size_gib is not None: self._values["user_volume_size_gib"] = user_volume_size_gib

        @property
        def compute_type_name(self) -> typing.Optional[str]:
            """``CfnWorkspace.WorkspacePropertiesProperty.ComputeTypeName``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-workspaces-workspace-workspaceproperties.html#cfn-workspaces-workspace-workspaceproperties-computetypename
            """
            return self._values.get('compute_type_name')

        @property
        def root_volume_size_gib(self) -> typing.Optional[jsii.Number]:
            """``CfnWorkspace.WorkspacePropertiesProperty.RootVolumeSizeGib``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-workspaces-workspace-workspaceproperties.html#cfn-workspaces-workspace-workspaceproperties-rootvolumesizegib
            """
            return self._values.get('root_volume_size_gib')

        @property
        def running_mode(self) -> typing.Optional[str]:
            """``CfnWorkspace.WorkspacePropertiesProperty.RunningMode``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-workspaces-workspace-workspaceproperties.html#cfn-workspaces-workspace-workspaceproperties-runningmode
            """
            return self._values.get('running_mode')

        @property
        def running_mode_auto_stop_timeout_in_minutes(self) -> typing.Optional[jsii.Number]:
            """``CfnWorkspace.WorkspacePropertiesProperty.RunningModeAutoStopTimeoutInMinutes``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-workspaces-workspace-workspaceproperties.html#cfn-workspaces-workspace-workspaceproperties-runningmodeautostoptimeoutinminutes
            """
            return self._values.get('running_mode_auto_stop_timeout_in_minutes')

        @property
        def user_volume_size_gib(self) -> typing.Optional[jsii.Number]:
            """``CfnWorkspace.WorkspacePropertiesProperty.UserVolumeSizeGib``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-workspaces-workspace-workspaceproperties.html#cfn-workspaces-workspace-workspaceproperties-uservolumesizegib
            """
            return self._values.get('user_volume_size_gib')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'WorkspacePropertiesProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



@jsii.data_type(jsii_type="@aws-cdk/aws-workspaces.CfnWorkspaceProps", jsii_struct_bases=[], name_mapping={'bundle_id': 'bundleId', 'directory_id': 'directoryId', 'user_name': 'userName', 'root_volume_encryption_enabled': 'rootVolumeEncryptionEnabled', 'tags': 'tags', 'user_volume_encryption_enabled': 'userVolumeEncryptionEnabled', 'volume_encryption_key': 'volumeEncryptionKey', 'workspace_properties': 'workspaceProperties'})
class CfnWorkspaceProps():
    def __init__(self, *, bundle_id: str, directory_id: str, user_name: str, root_volume_encryption_enabled: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None, user_volume_encryption_enabled: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, volume_encryption_key: typing.Optional[str]=None, workspace_properties: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnWorkspace.WorkspacePropertiesProperty"]]]=None):
        """Properties for defining a ``AWS::WorkSpaces::Workspace``.

        :param bundle_id: ``AWS::WorkSpaces::Workspace.BundleId``.
        :param directory_id: ``AWS::WorkSpaces::Workspace.DirectoryId``.
        :param user_name: ``AWS::WorkSpaces::Workspace.UserName``.
        :param root_volume_encryption_enabled: ``AWS::WorkSpaces::Workspace.RootVolumeEncryptionEnabled``.
        :param tags: ``AWS::WorkSpaces::Workspace.Tags``.
        :param user_volume_encryption_enabled: ``AWS::WorkSpaces::Workspace.UserVolumeEncryptionEnabled``.
        :param volume_encryption_key: ``AWS::WorkSpaces::Workspace.VolumeEncryptionKey``.
        :param workspace_properties: ``AWS::WorkSpaces::Workspace.WorkspaceProperties``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-workspaces-workspace.html
        """
        self._values = {
            'bundle_id': bundle_id,
            'directory_id': directory_id,
            'user_name': user_name,
        }
        if root_volume_encryption_enabled is not None: self._values["root_volume_encryption_enabled"] = root_volume_encryption_enabled
        if tags is not None: self._values["tags"] = tags
        if user_volume_encryption_enabled is not None: self._values["user_volume_encryption_enabled"] = user_volume_encryption_enabled
        if volume_encryption_key is not None: self._values["volume_encryption_key"] = volume_encryption_key
        if workspace_properties is not None: self._values["workspace_properties"] = workspace_properties

    @property
    def bundle_id(self) -> str:
        """``AWS::WorkSpaces::Workspace.BundleId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-workspaces-workspace.html#cfn-workspaces-workspace-bundleid
        """
        return self._values.get('bundle_id')

    @property
    def directory_id(self) -> str:
        """``AWS::WorkSpaces::Workspace.DirectoryId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-workspaces-workspace.html#cfn-workspaces-workspace-directoryid
        """
        return self._values.get('directory_id')

    @property
    def user_name(self) -> str:
        """``AWS::WorkSpaces::Workspace.UserName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-workspaces-workspace.html#cfn-workspaces-workspace-username
        """
        return self._values.get('user_name')

    @property
    def root_volume_encryption_enabled(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::WorkSpaces::Workspace.RootVolumeEncryptionEnabled``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-workspaces-workspace.html#cfn-workspaces-workspace-rootvolumeencryptionenabled
        """
        return self._values.get('root_volume_encryption_enabled')

    @property
    def tags(self) -> typing.Optional[typing.List[aws_cdk.core.CfnTag]]:
        """``AWS::WorkSpaces::Workspace.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-workspaces-workspace.html#cfn-workspaces-workspace-tags
        """
        return self._values.get('tags')

    @property
    def user_volume_encryption_enabled(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::WorkSpaces::Workspace.UserVolumeEncryptionEnabled``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-workspaces-workspace.html#cfn-workspaces-workspace-uservolumeencryptionenabled
        """
        return self._values.get('user_volume_encryption_enabled')

    @property
    def volume_encryption_key(self) -> typing.Optional[str]:
        """``AWS::WorkSpaces::Workspace.VolumeEncryptionKey``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-workspaces-workspace.html#cfn-workspaces-workspace-volumeencryptionkey
        """
        return self._values.get('volume_encryption_key')

    @property
    def workspace_properties(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnWorkspace.WorkspacePropertiesProperty"]]]:
        """``AWS::WorkSpaces::Workspace.WorkspaceProperties``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-workspaces-workspace.html#cfn-workspaces-workspace-workspaceproperties
        """
        return self._values.get('workspace_properties')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnWorkspaceProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


__all__ = ["CfnWorkspace", "CfnWorkspaceProps", "__jsii_assembly__"]

publication.publish()
