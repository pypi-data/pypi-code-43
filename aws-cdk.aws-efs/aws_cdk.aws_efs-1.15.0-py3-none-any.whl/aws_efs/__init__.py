import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.core
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-efs", "1.15.0", __name__, "aws-efs@1.15.0.jsii.tgz")
class CfnFileSystem(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-efs.CfnFileSystem"):
    """A CloudFormation ``AWS::EFS::FileSystem``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-filesystem.html
    cloudformationResource:
    :cloudformationResource:: AWS::EFS::FileSystem
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, encrypted: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, file_system_tags: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "ElasticFileSystemTagProperty"]]]]]=None, kms_key_id: typing.Optional[str]=None, lifecycle_policies: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "LifecyclePolicyProperty"]]]]]=None, performance_mode: typing.Optional[str]=None, provisioned_throughput_in_mibps: typing.Optional[jsii.Number]=None, throughput_mode: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::EFS::FileSystem``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param encrypted: ``AWS::EFS::FileSystem.Encrypted``.
        :param file_system_tags: ``AWS::EFS::FileSystem.FileSystemTags``.
        :param kms_key_id: ``AWS::EFS::FileSystem.KmsKeyId``.
        :param lifecycle_policies: ``AWS::EFS::FileSystem.LifecyclePolicies``.
        :param performance_mode: ``AWS::EFS::FileSystem.PerformanceMode``.
        :param provisioned_throughput_in_mibps: ``AWS::EFS::FileSystem.ProvisionedThroughputInMibps``.
        :param throughput_mode: ``AWS::EFS::FileSystem.ThroughputMode``.
        """
        props = CfnFileSystemProps(encrypted=encrypted, file_system_tags=file_system_tags, kms_key_id=kms_key_id, lifecycle_policies=lifecycle_policies, performance_mode=performance_mode, provisioned_throughput_in_mibps=provisioned_throughput_in_mibps, throughput_mode=throughput_mode)

        jsii.create(CfnFileSystem, self, [scope, id, props])

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
    @jsii.member(jsii_name="encrypted")
    def encrypted(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::EFS::FileSystem.Encrypted``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-filesystem.html#cfn-efs-filesystem-encrypted
        """
        return jsii.get(self, "encrypted")

    @encrypted.setter
    def encrypted(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "encrypted", value)

    @property
    @jsii.member(jsii_name="fileSystemTags")
    def file_system_tags(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "ElasticFileSystemTagProperty"]]]]]:
        """``AWS::EFS::FileSystem.FileSystemTags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-filesystem.html#cfn-efs-filesystem-filesystemtags
        """
        return jsii.get(self, "fileSystemTags")

    @file_system_tags.setter
    def file_system_tags(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "ElasticFileSystemTagProperty"]]]]]):
        return jsii.set(self, "fileSystemTags", value)

    @property
    @jsii.member(jsii_name="kmsKeyId")
    def kms_key_id(self) -> typing.Optional[str]:
        """``AWS::EFS::FileSystem.KmsKeyId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-filesystem.html#cfn-efs-filesystem-kmskeyid
        """
        return jsii.get(self, "kmsKeyId")

    @kms_key_id.setter
    def kms_key_id(self, value: typing.Optional[str]):
        return jsii.set(self, "kmsKeyId", value)

    @property
    @jsii.member(jsii_name="lifecyclePolicies")
    def lifecycle_policies(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "LifecyclePolicyProperty"]]]]]:
        """``AWS::EFS::FileSystem.LifecyclePolicies``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-filesystem.html#cfn-elasticfilesystem-filesystem-lifecyclepolicies
        """
        return jsii.get(self, "lifecyclePolicies")

    @lifecycle_policies.setter
    def lifecycle_policies(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "LifecyclePolicyProperty"]]]]]):
        return jsii.set(self, "lifecyclePolicies", value)

    @property
    @jsii.member(jsii_name="performanceMode")
    def performance_mode(self) -> typing.Optional[str]:
        """``AWS::EFS::FileSystem.PerformanceMode``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-filesystem.html#cfn-efs-filesystem-performancemode
        """
        return jsii.get(self, "performanceMode")

    @performance_mode.setter
    def performance_mode(self, value: typing.Optional[str]):
        return jsii.set(self, "performanceMode", value)

    @property
    @jsii.member(jsii_name="provisionedThroughputInMibps")
    def provisioned_throughput_in_mibps(self) -> typing.Optional[jsii.Number]:
        """``AWS::EFS::FileSystem.ProvisionedThroughputInMibps``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-filesystem.html#cfn-elasticfilesystem-filesystem-provisionedthroughputinmibps
        """
        return jsii.get(self, "provisionedThroughputInMibps")

    @provisioned_throughput_in_mibps.setter
    def provisioned_throughput_in_mibps(self, value: typing.Optional[jsii.Number]):
        return jsii.set(self, "provisionedThroughputInMibps", value)

    @property
    @jsii.member(jsii_name="throughputMode")
    def throughput_mode(self) -> typing.Optional[str]:
        """``AWS::EFS::FileSystem.ThroughputMode``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-filesystem.html#cfn-elasticfilesystem-filesystem-throughputmode
        """
        return jsii.get(self, "throughputMode")

    @throughput_mode.setter
    def throughput_mode(self, value: typing.Optional[str]):
        return jsii.set(self, "throughputMode", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-efs.CfnFileSystem.ElasticFileSystemTagProperty", jsii_struct_bases=[], name_mapping={'key': 'key', 'value': 'value'})
    class ElasticFileSystemTagProperty():
        def __init__(self, *, key: str, value: str):
            """
            :param key: ``CfnFileSystem.ElasticFileSystemTagProperty.Key``.
            :param value: ``CfnFileSystem.ElasticFileSystemTagProperty.Value``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-efs-filesystem-filesystemtags.html
            """
            self._values = {
                'key': key,
                'value': value,
            }

        @property
        def key(self) -> str:
            """``CfnFileSystem.ElasticFileSystemTagProperty.Key``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-efs-filesystem-filesystemtags.html#cfn-efs-filesystem-filesystemtags-key
            """
            return self._values.get('key')

        @property
        def value(self) -> str:
            """``CfnFileSystem.ElasticFileSystemTagProperty.Value``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-efs-filesystem-filesystemtags.html#cfn-efs-filesystem-filesystemtags-value
            """
            return self._values.get('value')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'ElasticFileSystemTagProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-efs.CfnFileSystem.LifecyclePolicyProperty", jsii_struct_bases=[], name_mapping={'transition_to_ia': 'transitionToIa'})
    class LifecyclePolicyProperty():
        def __init__(self, *, transition_to_ia: str):
            """
            :param transition_to_ia: ``CfnFileSystem.LifecyclePolicyProperty.TransitionToIA``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticfilesystem-filesystem-lifecyclepolicy.html
            """
            self._values = {
                'transition_to_ia': transition_to_ia,
            }

        @property
        def transition_to_ia(self) -> str:
            """``CfnFileSystem.LifecyclePolicyProperty.TransitionToIA``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticfilesystem-filesystem-lifecyclepolicy.html#cfn-elasticfilesystem-filesystem-lifecyclepolicy-transitiontoia
            """
            return self._values.get('transition_to_ia')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'LifecyclePolicyProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



@jsii.data_type(jsii_type="@aws-cdk/aws-efs.CfnFileSystemProps", jsii_struct_bases=[], name_mapping={'encrypted': 'encrypted', 'file_system_tags': 'fileSystemTags', 'kms_key_id': 'kmsKeyId', 'lifecycle_policies': 'lifecyclePolicies', 'performance_mode': 'performanceMode', 'provisioned_throughput_in_mibps': 'provisionedThroughputInMibps', 'throughput_mode': 'throughputMode'})
class CfnFileSystemProps():
    def __init__(self, *, encrypted: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, file_system_tags: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnFileSystem.ElasticFileSystemTagProperty"]]]]]=None, kms_key_id: typing.Optional[str]=None, lifecycle_policies: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnFileSystem.LifecyclePolicyProperty"]]]]]=None, performance_mode: typing.Optional[str]=None, provisioned_throughput_in_mibps: typing.Optional[jsii.Number]=None, throughput_mode: typing.Optional[str]=None):
        """Properties for defining a ``AWS::EFS::FileSystem``.

        :param encrypted: ``AWS::EFS::FileSystem.Encrypted``.
        :param file_system_tags: ``AWS::EFS::FileSystem.FileSystemTags``.
        :param kms_key_id: ``AWS::EFS::FileSystem.KmsKeyId``.
        :param lifecycle_policies: ``AWS::EFS::FileSystem.LifecyclePolicies``.
        :param performance_mode: ``AWS::EFS::FileSystem.PerformanceMode``.
        :param provisioned_throughput_in_mibps: ``AWS::EFS::FileSystem.ProvisionedThroughputInMibps``.
        :param throughput_mode: ``AWS::EFS::FileSystem.ThroughputMode``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-filesystem.html
        """
        self._values = {
        }
        if encrypted is not None: self._values["encrypted"] = encrypted
        if file_system_tags is not None: self._values["file_system_tags"] = file_system_tags
        if kms_key_id is not None: self._values["kms_key_id"] = kms_key_id
        if lifecycle_policies is not None: self._values["lifecycle_policies"] = lifecycle_policies
        if performance_mode is not None: self._values["performance_mode"] = performance_mode
        if provisioned_throughput_in_mibps is not None: self._values["provisioned_throughput_in_mibps"] = provisioned_throughput_in_mibps
        if throughput_mode is not None: self._values["throughput_mode"] = throughput_mode

    @property
    def encrypted(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::EFS::FileSystem.Encrypted``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-filesystem.html#cfn-efs-filesystem-encrypted
        """
        return self._values.get('encrypted')

    @property
    def file_system_tags(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnFileSystem.ElasticFileSystemTagProperty"]]]]]:
        """``AWS::EFS::FileSystem.FileSystemTags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-filesystem.html#cfn-efs-filesystem-filesystemtags
        """
        return self._values.get('file_system_tags')

    @property
    def kms_key_id(self) -> typing.Optional[str]:
        """``AWS::EFS::FileSystem.KmsKeyId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-filesystem.html#cfn-efs-filesystem-kmskeyid
        """
        return self._values.get('kms_key_id')

    @property
    def lifecycle_policies(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnFileSystem.LifecyclePolicyProperty"]]]]]:
        """``AWS::EFS::FileSystem.LifecyclePolicies``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-filesystem.html#cfn-elasticfilesystem-filesystem-lifecyclepolicies
        """
        return self._values.get('lifecycle_policies')

    @property
    def performance_mode(self) -> typing.Optional[str]:
        """``AWS::EFS::FileSystem.PerformanceMode``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-filesystem.html#cfn-efs-filesystem-performancemode
        """
        return self._values.get('performance_mode')

    @property
    def provisioned_throughput_in_mibps(self) -> typing.Optional[jsii.Number]:
        """``AWS::EFS::FileSystem.ProvisionedThroughputInMibps``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-filesystem.html#cfn-elasticfilesystem-filesystem-provisionedthroughputinmibps
        """
        return self._values.get('provisioned_throughput_in_mibps')

    @property
    def throughput_mode(self) -> typing.Optional[str]:
        """``AWS::EFS::FileSystem.ThroughputMode``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-filesystem.html#cfn-elasticfilesystem-filesystem-throughputmode
        """
        return self._values.get('throughput_mode')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnFileSystemProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnMountTarget(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-efs.CfnMountTarget"):
    """A CloudFormation ``AWS::EFS::MountTarget``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-mounttarget.html
    cloudformationResource:
    :cloudformationResource:: AWS::EFS::MountTarget
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, file_system_id: str, security_groups: typing.List[str], subnet_id: str, ip_address: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::EFS::MountTarget``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param file_system_id: ``AWS::EFS::MountTarget.FileSystemId``.
        :param security_groups: ``AWS::EFS::MountTarget.SecurityGroups``.
        :param subnet_id: ``AWS::EFS::MountTarget.SubnetId``.
        :param ip_address: ``AWS::EFS::MountTarget.IpAddress``.
        """
        props = CfnMountTargetProps(file_system_id=file_system_id, security_groups=security_groups, subnet_id=subnet_id, ip_address=ip_address)

        jsii.create(CfnMountTarget, self, [scope, id, props])

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
    @jsii.member(jsii_name="attrIpAddress")
    def attr_ip_address(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: IpAddress
        """
        return jsii.get(self, "attrIpAddress")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="fileSystemId")
    def file_system_id(self) -> str:
        """``AWS::EFS::MountTarget.FileSystemId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-mounttarget.html#cfn-efs-mounttarget-filesystemid
        """
        return jsii.get(self, "fileSystemId")

    @file_system_id.setter
    def file_system_id(self, value: str):
        return jsii.set(self, "fileSystemId", value)

    @property
    @jsii.member(jsii_name="securityGroups")
    def security_groups(self) -> typing.List[str]:
        """``AWS::EFS::MountTarget.SecurityGroups``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-mounttarget.html#cfn-efs-mounttarget-securitygroups
        """
        return jsii.get(self, "securityGroups")

    @security_groups.setter
    def security_groups(self, value: typing.List[str]):
        return jsii.set(self, "securityGroups", value)

    @property
    @jsii.member(jsii_name="subnetId")
    def subnet_id(self) -> str:
        """``AWS::EFS::MountTarget.SubnetId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-mounttarget.html#cfn-efs-mounttarget-subnetid
        """
        return jsii.get(self, "subnetId")

    @subnet_id.setter
    def subnet_id(self, value: str):
        return jsii.set(self, "subnetId", value)

    @property
    @jsii.member(jsii_name="ipAddress")
    def ip_address(self) -> typing.Optional[str]:
        """``AWS::EFS::MountTarget.IpAddress``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-mounttarget.html#cfn-efs-mounttarget-ipaddress
        """
        return jsii.get(self, "ipAddress")

    @ip_address.setter
    def ip_address(self, value: typing.Optional[str]):
        return jsii.set(self, "ipAddress", value)


@jsii.data_type(jsii_type="@aws-cdk/aws-efs.CfnMountTargetProps", jsii_struct_bases=[], name_mapping={'file_system_id': 'fileSystemId', 'security_groups': 'securityGroups', 'subnet_id': 'subnetId', 'ip_address': 'ipAddress'})
class CfnMountTargetProps():
    def __init__(self, *, file_system_id: str, security_groups: typing.List[str], subnet_id: str, ip_address: typing.Optional[str]=None):
        """Properties for defining a ``AWS::EFS::MountTarget``.

        :param file_system_id: ``AWS::EFS::MountTarget.FileSystemId``.
        :param security_groups: ``AWS::EFS::MountTarget.SecurityGroups``.
        :param subnet_id: ``AWS::EFS::MountTarget.SubnetId``.
        :param ip_address: ``AWS::EFS::MountTarget.IpAddress``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-mounttarget.html
        """
        self._values = {
            'file_system_id': file_system_id,
            'security_groups': security_groups,
            'subnet_id': subnet_id,
        }
        if ip_address is not None: self._values["ip_address"] = ip_address

    @property
    def file_system_id(self) -> str:
        """``AWS::EFS::MountTarget.FileSystemId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-mounttarget.html#cfn-efs-mounttarget-filesystemid
        """
        return self._values.get('file_system_id')

    @property
    def security_groups(self) -> typing.List[str]:
        """``AWS::EFS::MountTarget.SecurityGroups``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-mounttarget.html#cfn-efs-mounttarget-securitygroups
        """
        return self._values.get('security_groups')

    @property
    def subnet_id(self) -> str:
        """``AWS::EFS::MountTarget.SubnetId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-mounttarget.html#cfn-efs-mounttarget-subnetid
        """
        return self._values.get('subnet_id')

    @property
    def ip_address(self) -> typing.Optional[str]:
        """``AWS::EFS::MountTarget.IpAddress``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-mounttarget.html#cfn-efs-mounttarget-ipaddress
        """
        return self._values.get('ip_address')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnMountTargetProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


__all__ = ["CfnFileSystem", "CfnFileSystemProps", "CfnMountTarget", "CfnMountTargetProps", "__jsii_assembly__"]

publication.publish()
