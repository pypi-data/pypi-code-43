import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.core
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-fsx", "1.15.0", __name__, "aws-fsx@1.15.0.jsii.tgz")
class CfnFileSystem(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-fsx.CfnFileSystem"):
    """A CloudFormation ``AWS::FSx::FileSystem``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-fsx-filesystem.html
    cloudformationResource:
    :cloudformationResource:: AWS::FSx::FileSystem
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, file_system_type: str, subnet_ids: typing.List[str], backup_id: typing.Optional[str]=None, kms_key_id: typing.Optional[str]=None, lustre_configuration: typing.Optional[typing.Union[typing.Optional["LustreConfigurationProperty"], typing.Optional[aws_cdk.core.IResolvable]]]=None, security_group_ids: typing.Optional[typing.List[str]]=None, storage_capacity: typing.Optional[jsii.Number]=None, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None, windows_configuration: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["WindowsConfigurationProperty"]]]=None) -> None:
        """Create a new ``AWS::FSx::FileSystem``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param file_system_type: ``AWS::FSx::FileSystem.FileSystemType``.
        :param subnet_ids: ``AWS::FSx::FileSystem.SubnetIds``.
        :param backup_id: ``AWS::FSx::FileSystem.BackupId``.
        :param kms_key_id: ``AWS::FSx::FileSystem.KmsKeyId``.
        :param lustre_configuration: ``AWS::FSx::FileSystem.LustreConfiguration``.
        :param security_group_ids: ``AWS::FSx::FileSystem.SecurityGroupIds``.
        :param storage_capacity: ``AWS::FSx::FileSystem.StorageCapacity``.
        :param tags: ``AWS::FSx::FileSystem.Tags``.
        :param windows_configuration: ``AWS::FSx::FileSystem.WindowsConfiguration``.
        """
        props = CfnFileSystemProps(file_system_type=file_system_type, subnet_ids=subnet_ids, backup_id=backup_id, kms_key_id=kms_key_id, lustre_configuration=lustre_configuration, security_group_ids=security_group_ids, storage_capacity=storage_capacity, tags=tags, windows_configuration=windows_configuration)

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
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        """``AWS::FSx::FileSystem.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-fsx-filesystem.html#cfn-fsx-filesystem-tags
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="fileSystemType")
    def file_system_type(self) -> str:
        """``AWS::FSx::FileSystem.FileSystemType``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-fsx-filesystem.html#cfn-fsx-filesystem-filesystemtype
        """
        return jsii.get(self, "fileSystemType")

    @file_system_type.setter
    def file_system_type(self, value: str):
        return jsii.set(self, "fileSystemType", value)

    @property
    @jsii.member(jsii_name="subnetIds")
    def subnet_ids(self) -> typing.List[str]:
        """``AWS::FSx::FileSystem.SubnetIds``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-fsx-filesystem.html#cfn-fsx-filesystem-subnetids
        """
        return jsii.get(self, "subnetIds")

    @subnet_ids.setter
    def subnet_ids(self, value: typing.List[str]):
        return jsii.set(self, "subnetIds", value)

    @property
    @jsii.member(jsii_name="backupId")
    def backup_id(self) -> typing.Optional[str]:
        """``AWS::FSx::FileSystem.BackupId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-fsx-filesystem.html#cfn-fsx-filesystem-backupid
        """
        return jsii.get(self, "backupId")

    @backup_id.setter
    def backup_id(self, value: typing.Optional[str]):
        return jsii.set(self, "backupId", value)

    @property
    @jsii.member(jsii_name="kmsKeyId")
    def kms_key_id(self) -> typing.Optional[str]:
        """``AWS::FSx::FileSystem.KmsKeyId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-fsx-filesystem.html#cfn-fsx-filesystem-kmskeyid
        """
        return jsii.get(self, "kmsKeyId")

    @kms_key_id.setter
    def kms_key_id(self, value: typing.Optional[str]):
        return jsii.set(self, "kmsKeyId", value)

    @property
    @jsii.member(jsii_name="lustreConfiguration")
    def lustre_configuration(self) -> typing.Optional[typing.Union[typing.Optional["LustreConfigurationProperty"], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::FSx::FileSystem.LustreConfiguration``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-fsx-filesystem.html#cfn-fsx-filesystem-lustreconfiguration
        """
        return jsii.get(self, "lustreConfiguration")

    @lustre_configuration.setter
    def lustre_configuration(self, value: typing.Optional[typing.Union[typing.Optional["LustreConfigurationProperty"], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "lustreConfiguration", value)

    @property
    @jsii.member(jsii_name="securityGroupIds")
    def security_group_ids(self) -> typing.Optional[typing.List[str]]:
        """``AWS::FSx::FileSystem.SecurityGroupIds``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-fsx-filesystem.html#cfn-fsx-filesystem-securitygroupids
        """
        return jsii.get(self, "securityGroupIds")

    @security_group_ids.setter
    def security_group_ids(self, value: typing.Optional[typing.List[str]]):
        return jsii.set(self, "securityGroupIds", value)

    @property
    @jsii.member(jsii_name="storageCapacity")
    def storage_capacity(self) -> typing.Optional[jsii.Number]:
        """``AWS::FSx::FileSystem.StorageCapacity``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-fsx-filesystem.html#cfn-fsx-filesystem-storagecapacity
        """
        return jsii.get(self, "storageCapacity")

    @storage_capacity.setter
    def storage_capacity(self, value: typing.Optional[jsii.Number]):
        return jsii.set(self, "storageCapacity", value)

    @property
    @jsii.member(jsii_name="windowsConfiguration")
    def windows_configuration(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["WindowsConfigurationProperty"]]]:
        """``AWS::FSx::FileSystem.WindowsConfiguration``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-fsx-filesystem.html#cfn-fsx-filesystem-windowsconfiguration
        """
        return jsii.get(self, "windowsConfiguration")

    @windows_configuration.setter
    def windows_configuration(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["WindowsConfigurationProperty"]]]):
        return jsii.set(self, "windowsConfiguration", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-fsx.CfnFileSystem.LustreConfigurationProperty", jsii_struct_bases=[], name_mapping={'export_path': 'exportPath', 'imported_file_chunk_size': 'importedFileChunkSize', 'import_path': 'importPath', 'weekly_maintenance_start_time': 'weeklyMaintenanceStartTime'})
    class LustreConfigurationProperty():
        def __init__(self, *, export_path: typing.Optional[str]=None, imported_file_chunk_size: typing.Optional[jsii.Number]=None, import_path: typing.Optional[str]=None, weekly_maintenance_start_time: typing.Optional[str]=None):
            """
            :param export_path: ``CfnFileSystem.LustreConfigurationProperty.ExportPath``.
            :param imported_file_chunk_size: ``CfnFileSystem.LustreConfigurationProperty.ImportedFileChunkSize``.
            :param import_path: ``CfnFileSystem.LustreConfigurationProperty.ImportPath``.
            :param weekly_maintenance_start_time: ``CfnFileSystem.LustreConfigurationProperty.WeeklyMaintenanceStartTime``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-fsx-filesystem-lustreconfiguration.html
            """
            self._values = {
            }
            if export_path is not None: self._values["export_path"] = export_path
            if imported_file_chunk_size is not None: self._values["imported_file_chunk_size"] = imported_file_chunk_size
            if import_path is not None: self._values["import_path"] = import_path
            if weekly_maintenance_start_time is not None: self._values["weekly_maintenance_start_time"] = weekly_maintenance_start_time

        @property
        def export_path(self) -> typing.Optional[str]:
            """``CfnFileSystem.LustreConfigurationProperty.ExportPath``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-fsx-filesystem-lustreconfiguration.html#cfn-fsx-filesystem-lustreconfiguration-exportpath
            """
            return self._values.get('export_path')

        @property
        def imported_file_chunk_size(self) -> typing.Optional[jsii.Number]:
            """``CfnFileSystem.LustreConfigurationProperty.ImportedFileChunkSize``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-fsx-filesystem-lustreconfiguration.html#cfn-fsx-filesystem-lustreconfiguration-importedfilechunksize
            """
            return self._values.get('imported_file_chunk_size')

        @property
        def import_path(self) -> typing.Optional[str]:
            """``CfnFileSystem.LustreConfigurationProperty.ImportPath``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-fsx-filesystem-lustreconfiguration.html#cfn-fsx-filesystem-lustreconfiguration-importpath
            """
            return self._values.get('import_path')

        @property
        def weekly_maintenance_start_time(self) -> typing.Optional[str]:
            """``CfnFileSystem.LustreConfigurationProperty.WeeklyMaintenanceStartTime``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-fsx-filesystem-lustreconfiguration.html#cfn-fsx-filesystem-lustreconfiguration-weeklymaintenancestarttime
            """
            return self._values.get('weekly_maintenance_start_time')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'LustreConfigurationProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-fsx.CfnFileSystem.SelfManagedActiveDirectoryConfigurationProperty", jsii_struct_bases=[], name_mapping={'dns_ips': 'dnsIps', 'domain_name': 'domainName', 'file_system_administrators_group': 'fileSystemAdministratorsGroup', 'organizational_unit_distinguished_name': 'organizationalUnitDistinguishedName', 'password': 'password', 'user_name': 'userName'})
    class SelfManagedActiveDirectoryConfigurationProperty():
        def __init__(self, *, dns_ips: typing.Optional[typing.List[str]]=None, domain_name: typing.Optional[str]=None, file_system_administrators_group: typing.Optional[str]=None, organizational_unit_distinguished_name: typing.Optional[str]=None, password: typing.Optional[str]=None, user_name: typing.Optional[str]=None):
            """
            :param dns_ips: ``CfnFileSystem.SelfManagedActiveDirectoryConfigurationProperty.DnsIps``.
            :param domain_name: ``CfnFileSystem.SelfManagedActiveDirectoryConfigurationProperty.DomainName``.
            :param file_system_administrators_group: ``CfnFileSystem.SelfManagedActiveDirectoryConfigurationProperty.FileSystemAdministratorsGroup``.
            :param organizational_unit_distinguished_name: ``CfnFileSystem.SelfManagedActiveDirectoryConfigurationProperty.OrganizationalUnitDistinguishedName``.
            :param password: ``CfnFileSystem.SelfManagedActiveDirectoryConfigurationProperty.Password``.
            :param user_name: ``CfnFileSystem.SelfManagedActiveDirectoryConfigurationProperty.UserName``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-fsx-filesystem-windowsconfiguration-selfmanagedactivedirectoryconfiguration.html
            """
            self._values = {
            }
            if dns_ips is not None: self._values["dns_ips"] = dns_ips
            if domain_name is not None: self._values["domain_name"] = domain_name
            if file_system_administrators_group is not None: self._values["file_system_administrators_group"] = file_system_administrators_group
            if organizational_unit_distinguished_name is not None: self._values["organizational_unit_distinguished_name"] = organizational_unit_distinguished_name
            if password is not None: self._values["password"] = password
            if user_name is not None: self._values["user_name"] = user_name

        @property
        def dns_ips(self) -> typing.Optional[typing.List[str]]:
            """``CfnFileSystem.SelfManagedActiveDirectoryConfigurationProperty.DnsIps``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-fsx-filesystem-windowsconfiguration-selfmanagedactivedirectoryconfiguration.html#cfn-fsx-filesystem-windowsconfiguration-selfmanagedactivedirectoryconfiguration-dnsips
            """
            return self._values.get('dns_ips')

        @property
        def domain_name(self) -> typing.Optional[str]:
            """``CfnFileSystem.SelfManagedActiveDirectoryConfigurationProperty.DomainName``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-fsx-filesystem-windowsconfiguration-selfmanagedactivedirectoryconfiguration.html#cfn-fsx-filesystem-windowsconfiguration-selfmanagedactivedirectoryconfiguration-domainname
            """
            return self._values.get('domain_name')

        @property
        def file_system_administrators_group(self) -> typing.Optional[str]:
            """``CfnFileSystem.SelfManagedActiveDirectoryConfigurationProperty.FileSystemAdministratorsGroup``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-fsx-filesystem-windowsconfiguration-selfmanagedactivedirectoryconfiguration.html#cfn-fsx-filesystem-windowsconfiguration-selfmanagedactivedirectoryconfiguration-filesystemadministratorsgroup
            """
            return self._values.get('file_system_administrators_group')

        @property
        def organizational_unit_distinguished_name(self) -> typing.Optional[str]:
            """``CfnFileSystem.SelfManagedActiveDirectoryConfigurationProperty.OrganizationalUnitDistinguishedName``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-fsx-filesystem-windowsconfiguration-selfmanagedactivedirectoryconfiguration.html#cfn-fsx-filesystem-windowsconfiguration-selfmanagedactivedirectoryconfiguration-organizationalunitdistinguishedname
            """
            return self._values.get('organizational_unit_distinguished_name')

        @property
        def password(self) -> typing.Optional[str]:
            """``CfnFileSystem.SelfManagedActiveDirectoryConfigurationProperty.Password``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-fsx-filesystem-windowsconfiguration-selfmanagedactivedirectoryconfiguration.html#cfn-fsx-filesystem-windowsconfiguration-selfmanagedactivedirectoryconfiguration-password
            """
            return self._values.get('password')

        @property
        def user_name(self) -> typing.Optional[str]:
            """``CfnFileSystem.SelfManagedActiveDirectoryConfigurationProperty.UserName``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-fsx-filesystem-windowsconfiguration-selfmanagedactivedirectoryconfiguration.html#cfn-fsx-filesystem-windowsconfiguration-selfmanagedactivedirectoryconfiguration-username
            """
            return self._values.get('user_name')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'SelfManagedActiveDirectoryConfigurationProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-fsx.CfnFileSystem.WindowsConfigurationProperty", jsii_struct_bases=[], name_mapping={'active_directory_id': 'activeDirectoryId', 'automatic_backup_retention_days': 'automaticBackupRetentionDays', 'copy_tags_to_backups': 'copyTagsToBackups', 'daily_automatic_backup_start_time': 'dailyAutomaticBackupStartTime', 'self_managed_active_directory_configuration': 'selfManagedActiveDirectoryConfiguration', 'throughput_capacity': 'throughputCapacity', 'weekly_maintenance_start_time': 'weeklyMaintenanceStartTime'})
    class WindowsConfigurationProperty():
        def __init__(self, *, active_directory_id: typing.Optional[str]=None, automatic_backup_retention_days: typing.Optional[jsii.Number]=None, copy_tags_to_backups: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, daily_automatic_backup_start_time: typing.Optional[str]=None, self_managed_active_directory_configuration: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnFileSystem.SelfManagedActiveDirectoryConfigurationProperty"]]]=None, throughput_capacity: typing.Optional[jsii.Number]=None, weekly_maintenance_start_time: typing.Optional[str]=None):
            """
            :param active_directory_id: ``CfnFileSystem.WindowsConfigurationProperty.ActiveDirectoryId``.
            :param automatic_backup_retention_days: ``CfnFileSystem.WindowsConfigurationProperty.AutomaticBackupRetentionDays``.
            :param copy_tags_to_backups: ``CfnFileSystem.WindowsConfigurationProperty.CopyTagsToBackups``.
            :param daily_automatic_backup_start_time: ``CfnFileSystem.WindowsConfigurationProperty.DailyAutomaticBackupStartTime``.
            :param self_managed_active_directory_configuration: ``CfnFileSystem.WindowsConfigurationProperty.SelfManagedActiveDirectoryConfiguration``.
            :param throughput_capacity: ``CfnFileSystem.WindowsConfigurationProperty.ThroughputCapacity``.
            :param weekly_maintenance_start_time: ``CfnFileSystem.WindowsConfigurationProperty.WeeklyMaintenanceStartTime``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-fsx-filesystem-windowsconfiguration.html
            """
            self._values = {
            }
            if active_directory_id is not None: self._values["active_directory_id"] = active_directory_id
            if automatic_backup_retention_days is not None: self._values["automatic_backup_retention_days"] = automatic_backup_retention_days
            if copy_tags_to_backups is not None: self._values["copy_tags_to_backups"] = copy_tags_to_backups
            if daily_automatic_backup_start_time is not None: self._values["daily_automatic_backup_start_time"] = daily_automatic_backup_start_time
            if self_managed_active_directory_configuration is not None: self._values["self_managed_active_directory_configuration"] = self_managed_active_directory_configuration
            if throughput_capacity is not None: self._values["throughput_capacity"] = throughput_capacity
            if weekly_maintenance_start_time is not None: self._values["weekly_maintenance_start_time"] = weekly_maintenance_start_time

        @property
        def active_directory_id(self) -> typing.Optional[str]:
            """``CfnFileSystem.WindowsConfigurationProperty.ActiveDirectoryId``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-fsx-filesystem-windowsconfiguration.html#cfn-fsx-filesystem-windowsconfiguration-activedirectoryid
            """
            return self._values.get('active_directory_id')

        @property
        def automatic_backup_retention_days(self) -> typing.Optional[jsii.Number]:
            """``CfnFileSystem.WindowsConfigurationProperty.AutomaticBackupRetentionDays``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-fsx-filesystem-windowsconfiguration.html#cfn-fsx-filesystem-windowsconfiguration-automaticbackupretentiondays
            """
            return self._values.get('automatic_backup_retention_days')

        @property
        def copy_tags_to_backups(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
            """``CfnFileSystem.WindowsConfigurationProperty.CopyTagsToBackups``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-fsx-filesystem-windowsconfiguration.html#cfn-fsx-filesystem-windowsconfiguration-copytagstobackups
            """
            return self._values.get('copy_tags_to_backups')

        @property
        def daily_automatic_backup_start_time(self) -> typing.Optional[str]:
            """``CfnFileSystem.WindowsConfigurationProperty.DailyAutomaticBackupStartTime``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-fsx-filesystem-windowsconfiguration.html#cfn-fsx-filesystem-windowsconfiguration-dailyautomaticbackupstarttime
            """
            return self._values.get('daily_automatic_backup_start_time')

        @property
        def self_managed_active_directory_configuration(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnFileSystem.SelfManagedActiveDirectoryConfigurationProperty"]]]:
            """``CfnFileSystem.WindowsConfigurationProperty.SelfManagedActiveDirectoryConfiguration``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-fsx-filesystem-windowsconfiguration.html#cfn-fsx-filesystem-windowsconfiguration-selfmanagedactivedirectoryconfiguration
            """
            return self._values.get('self_managed_active_directory_configuration')

        @property
        def throughput_capacity(self) -> typing.Optional[jsii.Number]:
            """``CfnFileSystem.WindowsConfigurationProperty.ThroughputCapacity``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-fsx-filesystem-windowsconfiguration.html#cfn-fsx-filesystem-windowsconfiguration-throughputcapacity
            """
            return self._values.get('throughput_capacity')

        @property
        def weekly_maintenance_start_time(self) -> typing.Optional[str]:
            """``CfnFileSystem.WindowsConfigurationProperty.WeeklyMaintenanceStartTime``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-fsx-filesystem-windowsconfiguration.html#cfn-fsx-filesystem-windowsconfiguration-weeklymaintenancestarttime
            """
            return self._values.get('weekly_maintenance_start_time')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'WindowsConfigurationProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



@jsii.data_type(jsii_type="@aws-cdk/aws-fsx.CfnFileSystemProps", jsii_struct_bases=[], name_mapping={'file_system_type': 'fileSystemType', 'subnet_ids': 'subnetIds', 'backup_id': 'backupId', 'kms_key_id': 'kmsKeyId', 'lustre_configuration': 'lustreConfiguration', 'security_group_ids': 'securityGroupIds', 'storage_capacity': 'storageCapacity', 'tags': 'tags', 'windows_configuration': 'windowsConfiguration'})
class CfnFileSystemProps():
    def __init__(self, *, file_system_type: str, subnet_ids: typing.List[str], backup_id: typing.Optional[str]=None, kms_key_id: typing.Optional[str]=None, lustre_configuration: typing.Optional[typing.Union[typing.Optional["CfnFileSystem.LustreConfigurationProperty"], typing.Optional[aws_cdk.core.IResolvable]]]=None, security_group_ids: typing.Optional[typing.List[str]]=None, storage_capacity: typing.Optional[jsii.Number]=None, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None, windows_configuration: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnFileSystem.WindowsConfigurationProperty"]]]=None):
        """Properties for defining a ``AWS::FSx::FileSystem``.

        :param file_system_type: ``AWS::FSx::FileSystem.FileSystemType``.
        :param subnet_ids: ``AWS::FSx::FileSystem.SubnetIds``.
        :param backup_id: ``AWS::FSx::FileSystem.BackupId``.
        :param kms_key_id: ``AWS::FSx::FileSystem.KmsKeyId``.
        :param lustre_configuration: ``AWS::FSx::FileSystem.LustreConfiguration``.
        :param security_group_ids: ``AWS::FSx::FileSystem.SecurityGroupIds``.
        :param storage_capacity: ``AWS::FSx::FileSystem.StorageCapacity``.
        :param tags: ``AWS::FSx::FileSystem.Tags``.
        :param windows_configuration: ``AWS::FSx::FileSystem.WindowsConfiguration``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-fsx-filesystem.html
        """
        self._values = {
            'file_system_type': file_system_type,
            'subnet_ids': subnet_ids,
        }
        if backup_id is not None: self._values["backup_id"] = backup_id
        if kms_key_id is not None: self._values["kms_key_id"] = kms_key_id
        if lustre_configuration is not None: self._values["lustre_configuration"] = lustre_configuration
        if security_group_ids is not None: self._values["security_group_ids"] = security_group_ids
        if storage_capacity is not None: self._values["storage_capacity"] = storage_capacity
        if tags is not None: self._values["tags"] = tags
        if windows_configuration is not None: self._values["windows_configuration"] = windows_configuration

    @property
    def file_system_type(self) -> str:
        """``AWS::FSx::FileSystem.FileSystemType``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-fsx-filesystem.html#cfn-fsx-filesystem-filesystemtype
        """
        return self._values.get('file_system_type')

    @property
    def subnet_ids(self) -> typing.List[str]:
        """``AWS::FSx::FileSystem.SubnetIds``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-fsx-filesystem.html#cfn-fsx-filesystem-subnetids
        """
        return self._values.get('subnet_ids')

    @property
    def backup_id(self) -> typing.Optional[str]:
        """``AWS::FSx::FileSystem.BackupId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-fsx-filesystem.html#cfn-fsx-filesystem-backupid
        """
        return self._values.get('backup_id')

    @property
    def kms_key_id(self) -> typing.Optional[str]:
        """``AWS::FSx::FileSystem.KmsKeyId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-fsx-filesystem.html#cfn-fsx-filesystem-kmskeyid
        """
        return self._values.get('kms_key_id')

    @property
    def lustre_configuration(self) -> typing.Optional[typing.Union[typing.Optional["CfnFileSystem.LustreConfigurationProperty"], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::FSx::FileSystem.LustreConfiguration``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-fsx-filesystem.html#cfn-fsx-filesystem-lustreconfiguration
        """
        return self._values.get('lustre_configuration')

    @property
    def security_group_ids(self) -> typing.Optional[typing.List[str]]:
        """``AWS::FSx::FileSystem.SecurityGroupIds``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-fsx-filesystem.html#cfn-fsx-filesystem-securitygroupids
        """
        return self._values.get('security_group_ids')

    @property
    def storage_capacity(self) -> typing.Optional[jsii.Number]:
        """``AWS::FSx::FileSystem.StorageCapacity``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-fsx-filesystem.html#cfn-fsx-filesystem-storagecapacity
        """
        return self._values.get('storage_capacity')

    @property
    def tags(self) -> typing.Optional[typing.List[aws_cdk.core.CfnTag]]:
        """``AWS::FSx::FileSystem.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-fsx-filesystem.html#cfn-fsx-filesystem-tags
        """
        return self._values.get('tags')

    @property
    def windows_configuration(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnFileSystem.WindowsConfigurationProperty"]]]:
        """``AWS::FSx::FileSystem.WindowsConfiguration``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-fsx-filesystem.html#cfn-fsx-filesystem-windowsconfiguration
        """
        return self._values.get('windows_configuration')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnFileSystemProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


__all__ = ["CfnFileSystem", "CfnFileSystemProps", "__jsii_assembly__"]

publication.publish()
