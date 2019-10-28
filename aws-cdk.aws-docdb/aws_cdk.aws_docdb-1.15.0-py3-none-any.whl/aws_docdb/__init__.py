import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.core
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-docdb", "1.15.0", __name__, "aws-docdb@1.15.0.jsii.tgz")
class CfnDBCluster(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-docdb.CfnDBCluster"):
    """A CloudFormation ``AWS::DocDB::DBCluster``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html
    cloudformationResource:
    :cloudformationResource:: AWS::DocDB::DBCluster
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, availability_zones: typing.Optional[typing.List[str]]=None, backup_retention_period: typing.Optional[jsii.Number]=None, db_cluster_identifier: typing.Optional[str]=None, db_cluster_parameter_group_name: typing.Optional[str]=None, db_subnet_group_name: typing.Optional[str]=None, enable_cloudwatch_logs_exports: typing.Optional[typing.List[str]]=None, engine_version: typing.Optional[str]=None, kms_key_id: typing.Optional[str]=None, master_username: typing.Optional[str]=None, master_user_password: typing.Optional[str]=None, port: typing.Optional[jsii.Number]=None, preferred_backup_window: typing.Optional[str]=None, preferred_maintenance_window: typing.Optional[str]=None, snapshot_identifier: typing.Optional[str]=None, storage_encrypted: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None, vpc_security_group_ids: typing.Optional[typing.List[str]]=None) -> None:
        """Create a new ``AWS::DocDB::DBCluster``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param availability_zones: ``AWS::DocDB::DBCluster.AvailabilityZones``.
        :param backup_retention_period: ``AWS::DocDB::DBCluster.BackupRetentionPeriod``.
        :param db_cluster_identifier: ``AWS::DocDB::DBCluster.DBClusterIdentifier``.
        :param db_cluster_parameter_group_name: ``AWS::DocDB::DBCluster.DBClusterParameterGroupName``.
        :param db_subnet_group_name: ``AWS::DocDB::DBCluster.DBSubnetGroupName``.
        :param enable_cloudwatch_logs_exports: ``AWS::DocDB::DBCluster.EnableCloudwatchLogsExports``.
        :param engine_version: ``AWS::DocDB::DBCluster.EngineVersion``.
        :param kms_key_id: ``AWS::DocDB::DBCluster.KmsKeyId``.
        :param master_username: ``AWS::DocDB::DBCluster.MasterUsername``.
        :param master_user_password: ``AWS::DocDB::DBCluster.MasterUserPassword``.
        :param port: ``AWS::DocDB::DBCluster.Port``.
        :param preferred_backup_window: ``AWS::DocDB::DBCluster.PreferredBackupWindow``.
        :param preferred_maintenance_window: ``AWS::DocDB::DBCluster.PreferredMaintenanceWindow``.
        :param snapshot_identifier: ``AWS::DocDB::DBCluster.SnapshotIdentifier``.
        :param storage_encrypted: ``AWS::DocDB::DBCluster.StorageEncrypted``.
        :param tags: ``AWS::DocDB::DBCluster.Tags``.
        :param vpc_security_group_ids: ``AWS::DocDB::DBCluster.VpcSecurityGroupIds``.
        """
        props = CfnDBClusterProps(availability_zones=availability_zones, backup_retention_period=backup_retention_period, db_cluster_identifier=db_cluster_identifier, db_cluster_parameter_group_name=db_cluster_parameter_group_name, db_subnet_group_name=db_subnet_group_name, enable_cloudwatch_logs_exports=enable_cloudwatch_logs_exports, engine_version=engine_version, kms_key_id=kms_key_id, master_username=master_username, master_user_password=master_user_password, port=port, preferred_backup_window=preferred_backup_window, preferred_maintenance_window=preferred_maintenance_window, snapshot_identifier=snapshot_identifier, storage_encrypted=storage_encrypted, tags=tags, vpc_security_group_ids=vpc_security_group_ids)

        jsii.create(CfnDBCluster, self, [scope, id, props])

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
    @jsii.member(jsii_name="attrClusterResourceId")
    def attr_cluster_resource_id(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: ClusterResourceId
        """
        return jsii.get(self, "attrClusterResourceId")

    @property
    @jsii.member(jsii_name="attrEndpoint")
    def attr_endpoint(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: Endpoint
        """
        return jsii.get(self, "attrEndpoint")

    @property
    @jsii.member(jsii_name="attrPort")
    def attr_port(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: Port
        """
        return jsii.get(self, "attrPort")

    @property
    @jsii.member(jsii_name="attrReadEndpoint")
    def attr_read_endpoint(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: ReadEndpoint
        """
        return jsii.get(self, "attrReadEndpoint")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        """``AWS::DocDB::DBCluster.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-tags
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="availabilityZones")
    def availability_zones(self) -> typing.Optional[typing.List[str]]:
        """``AWS::DocDB::DBCluster.AvailabilityZones``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-availabilityzones
        """
        return jsii.get(self, "availabilityZones")

    @availability_zones.setter
    def availability_zones(self, value: typing.Optional[typing.List[str]]):
        return jsii.set(self, "availabilityZones", value)

    @property
    @jsii.member(jsii_name="backupRetentionPeriod")
    def backup_retention_period(self) -> typing.Optional[jsii.Number]:
        """``AWS::DocDB::DBCluster.BackupRetentionPeriod``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-backupretentionperiod
        """
        return jsii.get(self, "backupRetentionPeriod")

    @backup_retention_period.setter
    def backup_retention_period(self, value: typing.Optional[jsii.Number]):
        return jsii.set(self, "backupRetentionPeriod", value)

    @property
    @jsii.member(jsii_name="dbClusterIdentifier")
    def db_cluster_identifier(self) -> typing.Optional[str]:
        """``AWS::DocDB::DBCluster.DBClusterIdentifier``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-dbclusteridentifier
        """
        return jsii.get(self, "dbClusterIdentifier")

    @db_cluster_identifier.setter
    def db_cluster_identifier(self, value: typing.Optional[str]):
        return jsii.set(self, "dbClusterIdentifier", value)

    @property
    @jsii.member(jsii_name="dbClusterParameterGroupName")
    def db_cluster_parameter_group_name(self) -> typing.Optional[str]:
        """``AWS::DocDB::DBCluster.DBClusterParameterGroupName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-dbclusterparametergroupname
        """
        return jsii.get(self, "dbClusterParameterGroupName")

    @db_cluster_parameter_group_name.setter
    def db_cluster_parameter_group_name(self, value: typing.Optional[str]):
        return jsii.set(self, "dbClusterParameterGroupName", value)

    @property
    @jsii.member(jsii_name="dbSubnetGroupName")
    def db_subnet_group_name(self) -> typing.Optional[str]:
        """``AWS::DocDB::DBCluster.DBSubnetGroupName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-dbsubnetgroupname
        """
        return jsii.get(self, "dbSubnetGroupName")

    @db_subnet_group_name.setter
    def db_subnet_group_name(self, value: typing.Optional[str]):
        return jsii.set(self, "dbSubnetGroupName", value)

    @property
    @jsii.member(jsii_name="enableCloudwatchLogsExports")
    def enable_cloudwatch_logs_exports(self) -> typing.Optional[typing.List[str]]:
        """``AWS::DocDB::DBCluster.EnableCloudwatchLogsExports``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-enablecloudwatchlogsexports
        """
        return jsii.get(self, "enableCloudwatchLogsExports")

    @enable_cloudwatch_logs_exports.setter
    def enable_cloudwatch_logs_exports(self, value: typing.Optional[typing.List[str]]):
        return jsii.set(self, "enableCloudwatchLogsExports", value)

    @property
    @jsii.member(jsii_name="engineVersion")
    def engine_version(self) -> typing.Optional[str]:
        """``AWS::DocDB::DBCluster.EngineVersion``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-engineversion
        """
        return jsii.get(self, "engineVersion")

    @engine_version.setter
    def engine_version(self, value: typing.Optional[str]):
        return jsii.set(self, "engineVersion", value)

    @property
    @jsii.member(jsii_name="kmsKeyId")
    def kms_key_id(self) -> typing.Optional[str]:
        """``AWS::DocDB::DBCluster.KmsKeyId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-kmskeyid
        """
        return jsii.get(self, "kmsKeyId")

    @kms_key_id.setter
    def kms_key_id(self, value: typing.Optional[str]):
        return jsii.set(self, "kmsKeyId", value)

    @property
    @jsii.member(jsii_name="masterUsername")
    def master_username(self) -> typing.Optional[str]:
        """``AWS::DocDB::DBCluster.MasterUsername``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-masterusername
        """
        return jsii.get(self, "masterUsername")

    @master_username.setter
    def master_username(self, value: typing.Optional[str]):
        return jsii.set(self, "masterUsername", value)

    @property
    @jsii.member(jsii_name="masterUserPassword")
    def master_user_password(self) -> typing.Optional[str]:
        """``AWS::DocDB::DBCluster.MasterUserPassword``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-masteruserpassword
        """
        return jsii.get(self, "masterUserPassword")

    @master_user_password.setter
    def master_user_password(self, value: typing.Optional[str]):
        return jsii.set(self, "masterUserPassword", value)

    @property
    @jsii.member(jsii_name="port")
    def port(self) -> typing.Optional[jsii.Number]:
        """``AWS::DocDB::DBCluster.Port``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-port
        """
        return jsii.get(self, "port")

    @port.setter
    def port(self, value: typing.Optional[jsii.Number]):
        return jsii.set(self, "port", value)

    @property
    @jsii.member(jsii_name="preferredBackupWindow")
    def preferred_backup_window(self) -> typing.Optional[str]:
        """``AWS::DocDB::DBCluster.PreferredBackupWindow``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-preferredbackupwindow
        """
        return jsii.get(self, "preferredBackupWindow")

    @preferred_backup_window.setter
    def preferred_backup_window(self, value: typing.Optional[str]):
        return jsii.set(self, "preferredBackupWindow", value)

    @property
    @jsii.member(jsii_name="preferredMaintenanceWindow")
    def preferred_maintenance_window(self) -> typing.Optional[str]:
        """``AWS::DocDB::DBCluster.PreferredMaintenanceWindow``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-preferredmaintenancewindow
        """
        return jsii.get(self, "preferredMaintenanceWindow")

    @preferred_maintenance_window.setter
    def preferred_maintenance_window(self, value: typing.Optional[str]):
        return jsii.set(self, "preferredMaintenanceWindow", value)

    @property
    @jsii.member(jsii_name="snapshotIdentifier")
    def snapshot_identifier(self) -> typing.Optional[str]:
        """``AWS::DocDB::DBCluster.SnapshotIdentifier``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-snapshotidentifier
        """
        return jsii.get(self, "snapshotIdentifier")

    @snapshot_identifier.setter
    def snapshot_identifier(self, value: typing.Optional[str]):
        return jsii.set(self, "snapshotIdentifier", value)

    @property
    @jsii.member(jsii_name="storageEncrypted")
    def storage_encrypted(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::DocDB::DBCluster.StorageEncrypted``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-storageencrypted
        """
        return jsii.get(self, "storageEncrypted")

    @storage_encrypted.setter
    def storage_encrypted(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "storageEncrypted", value)

    @property
    @jsii.member(jsii_name="vpcSecurityGroupIds")
    def vpc_security_group_ids(self) -> typing.Optional[typing.List[str]]:
        """``AWS::DocDB::DBCluster.VpcSecurityGroupIds``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-vpcsecuritygroupids
        """
        return jsii.get(self, "vpcSecurityGroupIds")

    @vpc_security_group_ids.setter
    def vpc_security_group_ids(self, value: typing.Optional[typing.List[str]]):
        return jsii.set(self, "vpcSecurityGroupIds", value)


class CfnDBClusterParameterGroup(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-docdb.CfnDBClusterParameterGroup"):
    """A CloudFormation ``AWS::DocDB::DBClusterParameterGroup``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbclusterparametergroup.html
    cloudformationResource:
    :cloudformationResource:: AWS::DocDB::DBClusterParameterGroup
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, description: str, family: str, parameters: typing.Any, name: typing.Optional[str]=None, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None) -> None:
        """Create a new ``AWS::DocDB::DBClusterParameterGroup``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param description: ``AWS::DocDB::DBClusterParameterGroup.Description``.
        :param family: ``AWS::DocDB::DBClusterParameterGroup.Family``.
        :param parameters: ``AWS::DocDB::DBClusterParameterGroup.Parameters``.
        :param name: ``AWS::DocDB::DBClusterParameterGroup.Name``.
        :param tags: ``AWS::DocDB::DBClusterParameterGroup.Tags``.
        """
        props = CfnDBClusterParameterGroupProps(description=description, family=family, parameters=parameters, name=name, tags=tags)

        jsii.create(CfnDBClusterParameterGroup, self, [scope, id, props])

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
        """``AWS::DocDB::DBClusterParameterGroup.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbclusterparametergroup.html#cfn-docdb-dbclusterparametergroup-tags
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="description")
    def description(self) -> str:
        """``AWS::DocDB::DBClusterParameterGroup.Description``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbclusterparametergroup.html#cfn-docdb-dbclusterparametergroup-description
        """
        return jsii.get(self, "description")

    @description.setter
    def description(self, value: str):
        return jsii.set(self, "description", value)

    @property
    @jsii.member(jsii_name="family")
    def family(self) -> str:
        """``AWS::DocDB::DBClusterParameterGroup.Family``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbclusterparametergroup.html#cfn-docdb-dbclusterparametergroup-family
        """
        return jsii.get(self, "family")

    @family.setter
    def family(self, value: str):
        return jsii.set(self, "family", value)

    @property
    @jsii.member(jsii_name="parameters")
    def parameters(self) -> typing.Any:
        """``AWS::DocDB::DBClusterParameterGroup.Parameters``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbclusterparametergroup.html#cfn-docdb-dbclusterparametergroup-parameters
        """
        return jsii.get(self, "parameters")

    @parameters.setter
    def parameters(self, value: typing.Any):
        return jsii.set(self, "parameters", value)

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[str]:
        """``AWS::DocDB::DBClusterParameterGroup.Name``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbclusterparametergroup.html#cfn-docdb-dbclusterparametergroup-name
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: typing.Optional[str]):
        return jsii.set(self, "name", value)


@jsii.data_type(jsii_type="@aws-cdk/aws-docdb.CfnDBClusterParameterGroupProps", jsii_struct_bases=[], name_mapping={'description': 'description', 'family': 'family', 'parameters': 'parameters', 'name': 'name', 'tags': 'tags'})
class CfnDBClusterParameterGroupProps():
    def __init__(self, *, description: str, family: str, parameters: typing.Any, name: typing.Optional[str]=None, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None):
        """Properties for defining a ``AWS::DocDB::DBClusterParameterGroup``.

        :param description: ``AWS::DocDB::DBClusterParameterGroup.Description``.
        :param family: ``AWS::DocDB::DBClusterParameterGroup.Family``.
        :param parameters: ``AWS::DocDB::DBClusterParameterGroup.Parameters``.
        :param name: ``AWS::DocDB::DBClusterParameterGroup.Name``.
        :param tags: ``AWS::DocDB::DBClusterParameterGroup.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbclusterparametergroup.html
        """
        self._values = {
            'description': description,
            'family': family,
            'parameters': parameters,
        }
        if name is not None: self._values["name"] = name
        if tags is not None: self._values["tags"] = tags

    @property
    def description(self) -> str:
        """``AWS::DocDB::DBClusterParameterGroup.Description``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbclusterparametergroup.html#cfn-docdb-dbclusterparametergroup-description
        """
        return self._values.get('description')

    @property
    def family(self) -> str:
        """``AWS::DocDB::DBClusterParameterGroup.Family``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbclusterparametergroup.html#cfn-docdb-dbclusterparametergroup-family
        """
        return self._values.get('family')

    @property
    def parameters(self) -> typing.Any:
        """``AWS::DocDB::DBClusterParameterGroup.Parameters``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbclusterparametergroup.html#cfn-docdb-dbclusterparametergroup-parameters
        """
        return self._values.get('parameters')

    @property
    def name(self) -> typing.Optional[str]:
        """``AWS::DocDB::DBClusterParameterGroup.Name``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbclusterparametergroup.html#cfn-docdb-dbclusterparametergroup-name
        """
        return self._values.get('name')

    @property
    def tags(self) -> typing.Optional[typing.List[aws_cdk.core.CfnTag]]:
        """``AWS::DocDB::DBClusterParameterGroup.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbclusterparametergroup.html#cfn-docdb-dbclusterparametergroup-tags
        """
        return self._values.get('tags')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnDBClusterParameterGroupProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


@jsii.data_type(jsii_type="@aws-cdk/aws-docdb.CfnDBClusterProps", jsii_struct_bases=[], name_mapping={'availability_zones': 'availabilityZones', 'backup_retention_period': 'backupRetentionPeriod', 'db_cluster_identifier': 'dbClusterIdentifier', 'db_cluster_parameter_group_name': 'dbClusterParameterGroupName', 'db_subnet_group_name': 'dbSubnetGroupName', 'enable_cloudwatch_logs_exports': 'enableCloudwatchLogsExports', 'engine_version': 'engineVersion', 'kms_key_id': 'kmsKeyId', 'master_username': 'masterUsername', 'master_user_password': 'masterUserPassword', 'port': 'port', 'preferred_backup_window': 'preferredBackupWindow', 'preferred_maintenance_window': 'preferredMaintenanceWindow', 'snapshot_identifier': 'snapshotIdentifier', 'storage_encrypted': 'storageEncrypted', 'tags': 'tags', 'vpc_security_group_ids': 'vpcSecurityGroupIds'})
class CfnDBClusterProps():
    def __init__(self, *, availability_zones: typing.Optional[typing.List[str]]=None, backup_retention_period: typing.Optional[jsii.Number]=None, db_cluster_identifier: typing.Optional[str]=None, db_cluster_parameter_group_name: typing.Optional[str]=None, db_subnet_group_name: typing.Optional[str]=None, enable_cloudwatch_logs_exports: typing.Optional[typing.List[str]]=None, engine_version: typing.Optional[str]=None, kms_key_id: typing.Optional[str]=None, master_username: typing.Optional[str]=None, master_user_password: typing.Optional[str]=None, port: typing.Optional[jsii.Number]=None, preferred_backup_window: typing.Optional[str]=None, preferred_maintenance_window: typing.Optional[str]=None, snapshot_identifier: typing.Optional[str]=None, storage_encrypted: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None, vpc_security_group_ids: typing.Optional[typing.List[str]]=None):
        """Properties for defining a ``AWS::DocDB::DBCluster``.

        :param availability_zones: ``AWS::DocDB::DBCluster.AvailabilityZones``.
        :param backup_retention_period: ``AWS::DocDB::DBCluster.BackupRetentionPeriod``.
        :param db_cluster_identifier: ``AWS::DocDB::DBCluster.DBClusterIdentifier``.
        :param db_cluster_parameter_group_name: ``AWS::DocDB::DBCluster.DBClusterParameterGroupName``.
        :param db_subnet_group_name: ``AWS::DocDB::DBCluster.DBSubnetGroupName``.
        :param enable_cloudwatch_logs_exports: ``AWS::DocDB::DBCluster.EnableCloudwatchLogsExports``.
        :param engine_version: ``AWS::DocDB::DBCluster.EngineVersion``.
        :param kms_key_id: ``AWS::DocDB::DBCluster.KmsKeyId``.
        :param master_username: ``AWS::DocDB::DBCluster.MasterUsername``.
        :param master_user_password: ``AWS::DocDB::DBCluster.MasterUserPassword``.
        :param port: ``AWS::DocDB::DBCluster.Port``.
        :param preferred_backup_window: ``AWS::DocDB::DBCluster.PreferredBackupWindow``.
        :param preferred_maintenance_window: ``AWS::DocDB::DBCluster.PreferredMaintenanceWindow``.
        :param snapshot_identifier: ``AWS::DocDB::DBCluster.SnapshotIdentifier``.
        :param storage_encrypted: ``AWS::DocDB::DBCluster.StorageEncrypted``.
        :param tags: ``AWS::DocDB::DBCluster.Tags``.
        :param vpc_security_group_ids: ``AWS::DocDB::DBCluster.VpcSecurityGroupIds``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html
        """
        self._values = {
        }
        if availability_zones is not None: self._values["availability_zones"] = availability_zones
        if backup_retention_period is not None: self._values["backup_retention_period"] = backup_retention_period
        if db_cluster_identifier is not None: self._values["db_cluster_identifier"] = db_cluster_identifier
        if db_cluster_parameter_group_name is not None: self._values["db_cluster_parameter_group_name"] = db_cluster_parameter_group_name
        if db_subnet_group_name is not None: self._values["db_subnet_group_name"] = db_subnet_group_name
        if enable_cloudwatch_logs_exports is not None: self._values["enable_cloudwatch_logs_exports"] = enable_cloudwatch_logs_exports
        if engine_version is not None: self._values["engine_version"] = engine_version
        if kms_key_id is not None: self._values["kms_key_id"] = kms_key_id
        if master_username is not None: self._values["master_username"] = master_username
        if master_user_password is not None: self._values["master_user_password"] = master_user_password
        if port is not None: self._values["port"] = port
        if preferred_backup_window is not None: self._values["preferred_backup_window"] = preferred_backup_window
        if preferred_maintenance_window is not None: self._values["preferred_maintenance_window"] = preferred_maintenance_window
        if snapshot_identifier is not None: self._values["snapshot_identifier"] = snapshot_identifier
        if storage_encrypted is not None: self._values["storage_encrypted"] = storage_encrypted
        if tags is not None: self._values["tags"] = tags
        if vpc_security_group_ids is not None: self._values["vpc_security_group_ids"] = vpc_security_group_ids

    @property
    def availability_zones(self) -> typing.Optional[typing.List[str]]:
        """``AWS::DocDB::DBCluster.AvailabilityZones``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-availabilityzones
        """
        return self._values.get('availability_zones')

    @property
    def backup_retention_period(self) -> typing.Optional[jsii.Number]:
        """``AWS::DocDB::DBCluster.BackupRetentionPeriod``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-backupretentionperiod
        """
        return self._values.get('backup_retention_period')

    @property
    def db_cluster_identifier(self) -> typing.Optional[str]:
        """``AWS::DocDB::DBCluster.DBClusterIdentifier``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-dbclusteridentifier
        """
        return self._values.get('db_cluster_identifier')

    @property
    def db_cluster_parameter_group_name(self) -> typing.Optional[str]:
        """``AWS::DocDB::DBCluster.DBClusterParameterGroupName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-dbclusterparametergroupname
        """
        return self._values.get('db_cluster_parameter_group_name')

    @property
    def db_subnet_group_name(self) -> typing.Optional[str]:
        """``AWS::DocDB::DBCluster.DBSubnetGroupName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-dbsubnetgroupname
        """
        return self._values.get('db_subnet_group_name')

    @property
    def enable_cloudwatch_logs_exports(self) -> typing.Optional[typing.List[str]]:
        """``AWS::DocDB::DBCluster.EnableCloudwatchLogsExports``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-enablecloudwatchlogsexports
        """
        return self._values.get('enable_cloudwatch_logs_exports')

    @property
    def engine_version(self) -> typing.Optional[str]:
        """``AWS::DocDB::DBCluster.EngineVersion``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-engineversion
        """
        return self._values.get('engine_version')

    @property
    def kms_key_id(self) -> typing.Optional[str]:
        """``AWS::DocDB::DBCluster.KmsKeyId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-kmskeyid
        """
        return self._values.get('kms_key_id')

    @property
    def master_username(self) -> typing.Optional[str]:
        """``AWS::DocDB::DBCluster.MasterUsername``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-masterusername
        """
        return self._values.get('master_username')

    @property
    def master_user_password(self) -> typing.Optional[str]:
        """``AWS::DocDB::DBCluster.MasterUserPassword``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-masteruserpassword
        """
        return self._values.get('master_user_password')

    @property
    def port(self) -> typing.Optional[jsii.Number]:
        """``AWS::DocDB::DBCluster.Port``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-port
        """
        return self._values.get('port')

    @property
    def preferred_backup_window(self) -> typing.Optional[str]:
        """``AWS::DocDB::DBCluster.PreferredBackupWindow``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-preferredbackupwindow
        """
        return self._values.get('preferred_backup_window')

    @property
    def preferred_maintenance_window(self) -> typing.Optional[str]:
        """``AWS::DocDB::DBCluster.PreferredMaintenanceWindow``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-preferredmaintenancewindow
        """
        return self._values.get('preferred_maintenance_window')

    @property
    def snapshot_identifier(self) -> typing.Optional[str]:
        """``AWS::DocDB::DBCluster.SnapshotIdentifier``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-snapshotidentifier
        """
        return self._values.get('snapshot_identifier')

    @property
    def storage_encrypted(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::DocDB::DBCluster.StorageEncrypted``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-storageencrypted
        """
        return self._values.get('storage_encrypted')

    @property
    def tags(self) -> typing.Optional[typing.List[aws_cdk.core.CfnTag]]:
        """``AWS::DocDB::DBCluster.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-tags
        """
        return self._values.get('tags')

    @property
    def vpc_security_group_ids(self) -> typing.Optional[typing.List[str]]:
        """``AWS::DocDB::DBCluster.VpcSecurityGroupIds``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-vpcsecuritygroupids
        """
        return self._values.get('vpc_security_group_ids')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnDBClusterProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnDBInstance(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-docdb.CfnDBInstance"):
    """A CloudFormation ``AWS::DocDB::DBInstance``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbinstance.html
    cloudformationResource:
    :cloudformationResource:: AWS::DocDB::DBInstance
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, db_cluster_identifier: str, db_instance_class: str, auto_minor_version_upgrade: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, availability_zone: typing.Optional[str]=None, db_instance_identifier: typing.Optional[str]=None, preferred_maintenance_window: typing.Optional[str]=None, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None) -> None:
        """Create a new ``AWS::DocDB::DBInstance``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param db_cluster_identifier: ``AWS::DocDB::DBInstance.DBClusterIdentifier``.
        :param db_instance_class: ``AWS::DocDB::DBInstance.DBInstanceClass``.
        :param auto_minor_version_upgrade: ``AWS::DocDB::DBInstance.AutoMinorVersionUpgrade``.
        :param availability_zone: ``AWS::DocDB::DBInstance.AvailabilityZone``.
        :param db_instance_identifier: ``AWS::DocDB::DBInstance.DBInstanceIdentifier``.
        :param preferred_maintenance_window: ``AWS::DocDB::DBInstance.PreferredMaintenanceWindow``.
        :param tags: ``AWS::DocDB::DBInstance.Tags``.
        """
        props = CfnDBInstanceProps(db_cluster_identifier=db_cluster_identifier, db_instance_class=db_instance_class, auto_minor_version_upgrade=auto_minor_version_upgrade, availability_zone=availability_zone, db_instance_identifier=db_instance_identifier, preferred_maintenance_window=preferred_maintenance_window, tags=tags)

        jsii.create(CfnDBInstance, self, [scope, id, props])

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
    @jsii.member(jsii_name="attrEndpoint")
    def attr_endpoint(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: Endpoint
        """
        return jsii.get(self, "attrEndpoint")

    @property
    @jsii.member(jsii_name="attrPort")
    def attr_port(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: Port
        """
        return jsii.get(self, "attrPort")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        """``AWS::DocDB::DBInstance.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbinstance.html#cfn-docdb-dbinstance-tags
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="dbClusterIdentifier")
    def db_cluster_identifier(self) -> str:
        """``AWS::DocDB::DBInstance.DBClusterIdentifier``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbinstance.html#cfn-docdb-dbinstance-dbclusteridentifier
        """
        return jsii.get(self, "dbClusterIdentifier")

    @db_cluster_identifier.setter
    def db_cluster_identifier(self, value: str):
        return jsii.set(self, "dbClusterIdentifier", value)

    @property
    @jsii.member(jsii_name="dbInstanceClass")
    def db_instance_class(self) -> str:
        """``AWS::DocDB::DBInstance.DBInstanceClass``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbinstance.html#cfn-docdb-dbinstance-dbinstanceclass
        """
        return jsii.get(self, "dbInstanceClass")

    @db_instance_class.setter
    def db_instance_class(self, value: str):
        return jsii.set(self, "dbInstanceClass", value)

    @property
    @jsii.member(jsii_name="autoMinorVersionUpgrade")
    def auto_minor_version_upgrade(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::DocDB::DBInstance.AutoMinorVersionUpgrade``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbinstance.html#cfn-docdb-dbinstance-autominorversionupgrade
        """
        return jsii.get(self, "autoMinorVersionUpgrade")

    @auto_minor_version_upgrade.setter
    def auto_minor_version_upgrade(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "autoMinorVersionUpgrade", value)

    @property
    @jsii.member(jsii_name="availabilityZone")
    def availability_zone(self) -> typing.Optional[str]:
        """``AWS::DocDB::DBInstance.AvailabilityZone``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbinstance.html#cfn-docdb-dbinstance-availabilityzone
        """
        return jsii.get(self, "availabilityZone")

    @availability_zone.setter
    def availability_zone(self, value: typing.Optional[str]):
        return jsii.set(self, "availabilityZone", value)

    @property
    @jsii.member(jsii_name="dbInstanceIdentifier")
    def db_instance_identifier(self) -> typing.Optional[str]:
        """``AWS::DocDB::DBInstance.DBInstanceIdentifier``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbinstance.html#cfn-docdb-dbinstance-dbinstanceidentifier
        """
        return jsii.get(self, "dbInstanceIdentifier")

    @db_instance_identifier.setter
    def db_instance_identifier(self, value: typing.Optional[str]):
        return jsii.set(self, "dbInstanceIdentifier", value)

    @property
    @jsii.member(jsii_name="preferredMaintenanceWindow")
    def preferred_maintenance_window(self) -> typing.Optional[str]:
        """``AWS::DocDB::DBInstance.PreferredMaintenanceWindow``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbinstance.html#cfn-docdb-dbinstance-preferredmaintenancewindow
        """
        return jsii.get(self, "preferredMaintenanceWindow")

    @preferred_maintenance_window.setter
    def preferred_maintenance_window(self, value: typing.Optional[str]):
        return jsii.set(self, "preferredMaintenanceWindow", value)


@jsii.data_type(jsii_type="@aws-cdk/aws-docdb.CfnDBInstanceProps", jsii_struct_bases=[], name_mapping={'db_cluster_identifier': 'dbClusterIdentifier', 'db_instance_class': 'dbInstanceClass', 'auto_minor_version_upgrade': 'autoMinorVersionUpgrade', 'availability_zone': 'availabilityZone', 'db_instance_identifier': 'dbInstanceIdentifier', 'preferred_maintenance_window': 'preferredMaintenanceWindow', 'tags': 'tags'})
class CfnDBInstanceProps():
    def __init__(self, *, db_cluster_identifier: str, db_instance_class: str, auto_minor_version_upgrade: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, availability_zone: typing.Optional[str]=None, db_instance_identifier: typing.Optional[str]=None, preferred_maintenance_window: typing.Optional[str]=None, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None):
        """Properties for defining a ``AWS::DocDB::DBInstance``.

        :param db_cluster_identifier: ``AWS::DocDB::DBInstance.DBClusterIdentifier``.
        :param db_instance_class: ``AWS::DocDB::DBInstance.DBInstanceClass``.
        :param auto_minor_version_upgrade: ``AWS::DocDB::DBInstance.AutoMinorVersionUpgrade``.
        :param availability_zone: ``AWS::DocDB::DBInstance.AvailabilityZone``.
        :param db_instance_identifier: ``AWS::DocDB::DBInstance.DBInstanceIdentifier``.
        :param preferred_maintenance_window: ``AWS::DocDB::DBInstance.PreferredMaintenanceWindow``.
        :param tags: ``AWS::DocDB::DBInstance.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbinstance.html
        """
        self._values = {
            'db_cluster_identifier': db_cluster_identifier,
            'db_instance_class': db_instance_class,
        }
        if auto_minor_version_upgrade is not None: self._values["auto_minor_version_upgrade"] = auto_minor_version_upgrade
        if availability_zone is not None: self._values["availability_zone"] = availability_zone
        if db_instance_identifier is not None: self._values["db_instance_identifier"] = db_instance_identifier
        if preferred_maintenance_window is not None: self._values["preferred_maintenance_window"] = preferred_maintenance_window
        if tags is not None: self._values["tags"] = tags

    @property
    def db_cluster_identifier(self) -> str:
        """``AWS::DocDB::DBInstance.DBClusterIdentifier``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbinstance.html#cfn-docdb-dbinstance-dbclusteridentifier
        """
        return self._values.get('db_cluster_identifier')

    @property
    def db_instance_class(self) -> str:
        """``AWS::DocDB::DBInstance.DBInstanceClass``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbinstance.html#cfn-docdb-dbinstance-dbinstanceclass
        """
        return self._values.get('db_instance_class')

    @property
    def auto_minor_version_upgrade(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::DocDB::DBInstance.AutoMinorVersionUpgrade``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbinstance.html#cfn-docdb-dbinstance-autominorversionupgrade
        """
        return self._values.get('auto_minor_version_upgrade')

    @property
    def availability_zone(self) -> typing.Optional[str]:
        """``AWS::DocDB::DBInstance.AvailabilityZone``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbinstance.html#cfn-docdb-dbinstance-availabilityzone
        """
        return self._values.get('availability_zone')

    @property
    def db_instance_identifier(self) -> typing.Optional[str]:
        """``AWS::DocDB::DBInstance.DBInstanceIdentifier``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbinstance.html#cfn-docdb-dbinstance-dbinstanceidentifier
        """
        return self._values.get('db_instance_identifier')

    @property
    def preferred_maintenance_window(self) -> typing.Optional[str]:
        """``AWS::DocDB::DBInstance.PreferredMaintenanceWindow``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbinstance.html#cfn-docdb-dbinstance-preferredmaintenancewindow
        """
        return self._values.get('preferred_maintenance_window')

    @property
    def tags(self) -> typing.Optional[typing.List[aws_cdk.core.CfnTag]]:
        """``AWS::DocDB::DBInstance.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbinstance.html#cfn-docdb-dbinstance-tags
        """
        return self._values.get('tags')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnDBInstanceProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnDBSubnetGroup(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-docdb.CfnDBSubnetGroup"):
    """A CloudFormation ``AWS::DocDB::DBSubnetGroup``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbsubnetgroup.html
    cloudformationResource:
    :cloudformationResource:: AWS::DocDB::DBSubnetGroup
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, db_subnet_group_description: str, subnet_ids: typing.List[str], db_subnet_group_name: typing.Optional[str]=None, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None) -> None:
        """Create a new ``AWS::DocDB::DBSubnetGroup``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param db_subnet_group_description: ``AWS::DocDB::DBSubnetGroup.DBSubnetGroupDescription``.
        :param subnet_ids: ``AWS::DocDB::DBSubnetGroup.SubnetIds``.
        :param db_subnet_group_name: ``AWS::DocDB::DBSubnetGroup.DBSubnetGroupName``.
        :param tags: ``AWS::DocDB::DBSubnetGroup.Tags``.
        """
        props = CfnDBSubnetGroupProps(db_subnet_group_description=db_subnet_group_description, subnet_ids=subnet_ids, db_subnet_group_name=db_subnet_group_name, tags=tags)

        jsii.create(CfnDBSubnetGroup, self, [scope, id, props])

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
        """``AWS::DocDB::DBSubnetGroup.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbsubnetgroup.html#cfn-docdb-dbsubnetgroup-tags
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="dbSubnetGroupDescription")
    def db_subnet_group_description(self) -> str:
        """``AWS::DocDB::DBSubnetGroup.DBSubnetGroupDescription``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbsubnetgroup.html#cfn-docdb-dbsubnetgroup-dbsubnetgroupdescription
        """
        return jsii.get(self, "dbSubnetGroupDescription")

    @db_subnet_group_description.setter
    def db_subnet_group_description(self, value: str):
        return jsii.set(self, "dbSubnetGroupDescription", value)

    @property
    @jsii.member(jsii_name="subnetIds")
    def subnet_ids(self) -> typing.List[str]:
        """``AWS::DocDB::DBSubnetGroup.SubnetIds``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbsubnetgroup.html#cfn-docdb-dbsubnetgroup-subnetids
        """
        return jsii.get(self, "subnetIds")

    @subnet_ids.setter
    def subnet_ids(self, value: typing.List[str]):
        return jsii.set(self, "subnetIds", value)

    @property
    @jsii.member(jsii_name="dbSubnetGroupName")
    def db_subnet_group_name(self) -> typing.Optional[str]:
        """``AWS::DocDB::DBSubnetGroup.DBSubnetGroupName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbsubnetgroup.html#cfn-docdb-dbsubnetgroup-dbsubnetgroupname
        """
        return jsii.get(self, "dbSubnetGroupName")

    @db_subnet_group_name.setter
    def db_subnet_group_name(self, value: typing.Optional[str]):
        return jsii.set(self, "dbSubnetGroupName", value)


@jsii.data_type(jsii_type="@aws-cdk/aws-docdb.CfnDBSubnetGroupProps", jsii_struct_bases=[], name_mapping={'db_subnet_group_description': 'dbSubnetGroupDescription', 'subnet_ids': 'subnetIds', 'db_subnet_group_name': 'dbSubnetGroupName', 'tags': 'tags'})
class CfnDBSubnetGroupProps():
    def __init__(self, *, db_subnet_group_description: str, subnet_ids: typing.List[str], db_subnet_group_name: typing.Optional[str]=None, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None):
        """Properties for defining a ``AWS::DocDB::DBSubnetGroup``.

        :param db_subnet_group_description: ``AWS::DocDB::DBSubnetGroup.DBSubnetGroupDescription``.
        :param subnet_ids: ``AWS::DocDB::DBSubnetGroup.SubnetIds``.
        :param db_subnet_group_name: ``AWS::DocDB::DBSubnetGroup.DBSubnetGroupName``.
        :param tags: ``AWS::DocDB::DBSubnetGroup.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbsubnetgroup.html
        """
        self._values = {
            'db_subnet_group_description': db_subnet_group_description,
            'subnet_ids': subnet_ids,
        }
        if db_subnet_group_name is not None: self._values["db_subnet_group_name"] = db_subnet_group_name
        if tags is not None: self._values["tags"] = tags

    @property
    def db_subnet_group_description(self) -> str:
        """``AWS::DocDB::DBSubnetGroup.DBSubnetGroupDescription``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbsubnetgroup.html#cfn-docdb-dbsubnetgroup-dbsubnetgroupdescription
        """
        return self._values.get('db_subnet_group_description')

    @property
    def subnet_ids(self) -> typing.List[str]:
        """``AWS::DocDB::DBSubnetGroup.SubnetIds``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbsubnetgroup.html#cfn-docdb-dbsubnetgroup-subnetids
        """
        return self._values.get('subnet_ids')

    @property
    def db_subnet_group_name(self) -> typing.Optional[str]:
        """``AWS::DocDB::DBSubnetGroup.DBSubnetGroupName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbsubnetgroup.html#cfn-docdb-dbsubnetgroup-dbsubnetgroupname
        """
        return self._values.get('db_subnet_group_name')

    @property
    def tags(self) -> typing.Optional[typing.List[aws_cdk.core.CfnTag]]:
        """``AWS::DocDB::DBSubnetGroup.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbsubnetgroup.html#cfn-docdb-dbsubnetgroup-tags
        """
        return self._values.get('tags')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnDBSubnetGroupProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


__all__ = ["CfnDBCluster", "CfnDBClusterParameterGroup", "CfnDBClusterParameterGroupProps", "CfnDBClusterProps", "CfnDBInstance", "CfnDBInstanceProps", "CfnDBSubnetGroup", "CfnDBSubnetGroupProps", "__jsii_assembly__"]

publication.publish()
