import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.core
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-opsworkscm", "1.15.0", __name__, "aws-opsworkscm@1.15.0.jsii.tgz")
class CfnServer(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-opsworkscm.CfnServer"):
    """A CloudFormation ``AWS::OpsWorksCM::Server``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-opsworkscm-server.html
    cloudformationResource:
    :cloudformationResource:: AWS::OpsWorksCM::Server
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, instance_profile_arn: str, instance_type: str, service_role_arn: str, associate_public_ip_address: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, backup_id: typing.Optional[str]=None, backup_retention_count: typing.Optional[jsii.Number]=None, disable_automated_backup: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, engine: typing.Optional[str]=None, engine_attributes: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "EngineAttributeProperty"]]]]]=None, engine_model: typing.Optional[str]=None, engine_version: typing.Optional[str]=None, key_pair: typing.Optional[str]=None, preferred_backup_window: typing.Optional[str]=None, preferred_maintenance_window: typing.Optional[str]=None, security_group_ids: typing.Optional[typing.List[str]]=None, server_name: typing.Optional[str]=None, subnet_ids: typing.Optional[typing.List[str]]=None) -> None:
        """Create a new ``AWS::OpsWorksCM::Server``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param instance_profile_arn: ``AWS::OpsWorksCM::Server.InstanceProfileArn``.
        :param instance_type: ``AWS::OpsWorksCM::Server.InstanceType``.
        :param service_role_arn: ``AWS::OpsWorksCM::Server.ServiceRoleArn``.
        :param associate_public_ip_address: ``AWS::OpsWorksCM::Server.AssociatePublicIpAddress``.
        :param backup_id: ``AWS::OpsWorksCM::Server.BackupId``.
        :param backup_retention_count: ``AWS::OpsWorksCM::Server.BackupRetentionCount``.
        :param disable_automated_backup: ``AWS::OpsWorksCM::Server.DisableAutomatedBackup``.
        :param engine: ``AWS::OpsWorksCM::Server.Engine``.
        :param engine_attributes: ``AWS::OpsWorksCM::Server.EngineAttributes``.
        :param engine_model: ``AWS::OpsWorksCM::Server.EngineModel``.
        :param engine_version: ``AWS::OpsWorksCM::Server.EngineVersion``.
        :param key_pair: ``AWS::OpsWorksCM::Server.KeyPair``.
        :param preferred_backup_window: ``AWS::OpsWorksCM::Server.PreferredBackupWindow``.
        :param preferred_maintenance_window: ``AWS::OpsWorksCM::Server.PreferredMaintenanceWindow``.
        :param security_group_ids: ``AWS::OpsWorksCM::Server.SecurityGroupIds``.
        :param server_name: ``AWS::OpsWorksCM::Server.ServerName``.
        :param subnet_ids: ``AWS::OpsWorksCM::Server.SubnetIds``.
        """
        props = CfnServerProps(instance_profile_arn=instance_profile_arn, instance_type=instance_type, service_role_arn=service_role_arn, associate_public_ip_address=associate_public_ip_address, backup_id=backup_id, backup_retention_count=backup_retention_count, disable_automated_backup=disable_automated_backup, engine=engine, engine_attributes=engine_attributes, engine_model=engine_model, engine_version=engine_version, key_pair=key_pair, preferred_backup_window=preferred_backup_window, preferred_maintenance_window=preferred_maintenance_window, security_group_ids=security_group_ids, server_name=server_name, subnet_ids=subnet_ids)

        jsii.create(CfnServer, self, [scope, id, props])

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
    @jsii.member(jsii_name="attrEndpoint")
    def attr_endpoint(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: Endpoint
        """
        return jsii.get(self, "attrEndpoint")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="instanceProfileArn")
    def instance_profile_arn(self) -> str:
        """``AWS::OpsWorksCM::Server.InstanceProfileArn``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-opsworkscm-server.html#cfn-opsworkscm-server-instanceprofilearn
        """
        return jsii.get(self, "instanceProfileArn")

    @instance_profile_arn.setter
    def instance_profile_arn(self, value: str):
        return jsii.set(self, "instanceProfileArn", value)

    @property
    @jsii.member(jsii_name="instanceType")
    def instance_type(self) -> str:
        """``AWS::OpsWorksCM::Server.InstanceType``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-opsworkscm-server.html#cfn-opsworkscm-server-instancetype
        """
        return jsii.get(self, "instanceType")

    @instance_type.setter
    def instance_type(self, value: str):
        return jsii.set(self, "instanceType", value)

    @property
    @jsii.member(jsii_name="serviceRoleArn")
    def service_role_arn(self) -> str:
        """``AWS::OpsWorksCM::Server.ServiceRoleArn``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-opsworkscm-server.html#cfn-opsworkscm-server-servicerolearn
        """
        return jsii.get(self, "serviceRoleArn")

    @service_role_arn.setter
    def service_role_arn(self, value: str):
        return jsii.set(self, "serviceRoleArn", value)

    @property
    @jsii.member(jsii_name="associatePublicIpAddress")
    def associate_public_ip_address(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::OpsWorksCM::Server.AssociatePublicIpAddress``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-opsworkscm-server.html#cfn-opsworkscm-server-associatepublicipaddress
        """
        return jsii.get(self, "associatePublicIpAddress")

    @associate_public_ip_address.setter
    def associate_public_ip_address(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "associatePublicIpAddress", value)

    @property
    @jsii.member(jsii_name="backupId")
    def backup_id(self) -> typing.Optional[str]:
        """``AWS::OpsWorksCM::Server.BackupId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-opsworkscm-server.html#cfn-opsworkscm-server-backupid
        """
        return jsii.get(self, "backupId")

    @backup_id.setter
    def backup_id(self, value: typing.Optional[str]):
        return jsii.set(self, "backupId", value)

    @property
    @jsii.member(jsii_name="backupRetentionCount")
    def backup_retention_count(self) -> typing.Optional[jsii.Number]:
        """``AWS::OpsWorksCM::Server.BackupRetentionCount``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-opsworkscm-server.html#cfn-opsworkscm-server-backupretentioncount
        """
        return jsii.get(self, "backupRetentionCount")

    @backup_retention_count.setter
    def backup_retention_count(self, value: typing.Optional[jsii.Number]):
        return jsii.set(self, "backupRetentionCount", value)

    @property
    @jsii.member(jsii_name="disableAutomatedBackup")
    def disable_automated_backup(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::OpsWorksCM::Server.DisableAutomatedBackup``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-opsworkscm-server.html#cfn-opsworkscm-server-disableautomatedbackup
        """
        return jsii.get(self, "disableAutomatedBackup")

    @disable_automated_backup.setter
    def disable_automated_backup(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "disableAutomatedBackup", value)

    @property
    @jsii.member(jsii_name="engine")
    def engine(self) -> typing.Optional[str]:
        """``AWS::OpsWorksCM::Server.Engine``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-opsworkscm-server.html#cfn-opsworkscm-server-engine
        """
        return jsii.get(self, "engine")

    @engine.setter
    def engine(self, value: typing.Optional[str]):
        return jsii.set(self, "engine", value)

    @property
    @jsii.member(jsii_name="engineAttributes")
    def engine_attributes(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "EngineAttributeProperty"]]]]]:
        """``AWS::OpsWorksCM::Server.EngineAttributes``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-opsworkscm-server.html#cfn-opsworkscm-server-engineattributes
        """
        return jsii.get(self, "engineAttributes")

    @engine_attributes.setter
    def engine_attributes(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "EngineAttributeProperty"]]]]]):
        return jsii.set(self, "engineAttributes", value)

    @property
    @jsii.member(jsii_name="engineModel")
    def engine_model(self) -> typing.Optional[str]:
        """``AWS::OpsWorksCM::Server.EngineModel``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-opsworkscm-server.html#cfn-opsworkscm-server-enginemodel
        """
        return jsii.get(self, "engineModel")

    @engine_model.setter
    def engine_model(self, value: typing.Optional[str]):
        return jsii.set(self, "engineModel", value)

    @property
    @jsii.member(jsii_name="engineVersion")
    def engine_version(self) -> typing.Optional[str]:
        """``AWS::OpsWorksCM::Server.EngineVersion``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-opsworkscm-server.html#cfn-opsworkscm-server-engineversion
        """
        return jsii.get(self, "engineVersion")

    @engine_version.setter
    def engine_version(self, value: typing.Optional[str]):
        return jsii.set(self, "engineVersion", value)

    @property
    @jsii.member(jsii_name="keyPair")
    def key_pair(self) -> typing.Optional[str]:
        """``AWS::OpsWorksCM::Server.KeyPair``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-opsworkscm-server.html#cfn-opsworkscm-server-keypair
        """
        return jsii.get(self, "keyPair")

    @key_pair.setter
    def key_pair(self, value: typing.Optional[str]):
        return jsii.set(self, "keyPair", value)

    @property
    @jsii.member(jsii_name="preferredBackupWindow")
    def preferred_backup_window(self) -> typing.Optional[str]:
        """``AWS::OpsWorksCM::Server.PreferredBackupWindow``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-opsworkscm-server.html#cfn-opsworkscm-server-preferredbackupwindow
        """
        return jsii.get(self, "preferredBackupWindow")

    @preferred_backup_window.setter
    def preferred_backup_window(self, value: typing.Optional[str]):
        return jsii.set(self, "preferredBackupWindow", value)

    @property
    @jsii.member(jsii_name="preferredMaintenanceWindow")
    def preferred_maintenance_window(self) -> typing.Optional[str]:
        """``AWS::OpsWorksCM::Server.PreferredMaintenanceWindow``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-opsworkscm-server.html#cfn-opsworkscm-server-preferredmaintenancewindow
        """
        return jsii.get(self, "preferredMaintenanceWindow")

    @preferred_maintenance_window.setter
    def preferred_maintenance_window(self, value: typing.Optional[str]):
        return jsii.set(self, "preferredMaintenanceWindow", value)

    @property
    @jsii.member(jsii_name="securityGroupIds")
    def security_group_ids(self) -> typing.Optional[typing.List[str]]:
        """``AWS::OpsWorksCM::Server.SecurityGroupIds``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-opsworkscm-server.html#cfn-opsworkscm-server-securitygroupids
        """
        return jsii.get(self, "securityGroupIds")

    @security_group_ids.setter
    def security_group_ids(self, value: typing.Optional[typing.List[str]]):
        return jsii.set(self, "securityGroupIds", value)

    @property
    @jsii.member(jsii_name="serverName")
    def server_name(self) -> typing.Optional[str]:
        """``AWS::OpsWorksCM::Server.ServerName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-opsworkscm-server.html#cfn-opsworkscm-server-servername
        """
        return jsii.get(self, "serverName")

    @server_name.setter
    def server_name(self, value: typing.Optional[str]):
        return jsii.set(self, "serverName", value)

    @property
    @jsii.member(jsii_name="subnetIds")
    def subnet_ids(self) -> typing.Optional[typing.List[str]]:
        """``AWS::OpsWorksCM::Server.SubnetIds``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-opsworkscm-server.html#cfn-opsworkscm-server-subnetids
        """
        return jsii.get(self, "subnetIds")

    @subnet_ids.setter
    def subnet_ids(self, value: typing.Optional[typing.List[str]]):
        return jsii.set(self, "subnetIds", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-opsworkscm.CfnServer.EngineAttributeProperty", jsii_struct_bases=[], name_mapping={'name': 'name', 'value': 'value'})
    class EngineAttributeProperty():
        def __init__(self, *, name: typing.Optional[str]=None, value: typing.Optional[str]=None):
            """
            :param name: ``CfnServer.EngineAttributeProperty.Name``.
            :param value: ``CfnServer.EngineAttributeProperty.Value``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-opsworkscm-server-engineattribute.html
            """
            self._values = {
            }
            if name is not None: self._values["name"] = name
            if value is not None: self._values["value"] = value

        @property
        def name(self) -> typing.Optional[str]:
            """``CfnServer.EngineAttributeProperty.Name``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-opsworkscm-server-engineattribute.html#cfn-opsworkscm-server-engineattribute-name
            """
            return self._values.get('name')

        @property
        def value(self) -> typing.Optional[str]:
            """``CfnServer.EngineAttributeProperty.Value``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-opsworkscm-server-engineattribute.html#cfn-opsworkscm-server-engineattribute-value
            """
            return self._values.get('value')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'EngineAttributeProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



@jsii.data_type(jsii_type="@aws-cdk/aws-opsworkscm.CfnServerProps", jsii_struct_bases=[], name_mapping={'instance_profile_arn': 'instanceProfileArn', 'instance_type': 'instanceType', 'service_role_arn': 'serviceRoleArn', 'associate_public_ip_address': 'associatePublicIpAddress', 'backup_id': 'backupId', 'backup_retention_count': 'backupRetentionCount', 'disable_automated_backup': 'disableAutomatedBackup', 'engine': 'engine', 'engine_attributes': 'engineAttributes', 'engine_model': 'engineModel', 'engine_version': 'engineVersion', 'key_pair': 'keyPair', 'preferred_backup_window': 'preferredBackupWindow', 'preferred_maintenance_window': 'preferredMaintenanceWindow', 'security_group_ids': 'securityGroupIds', 'server_name': 'serverName', 'subnet_ids': 'subnetIds'})
class CfnServerProps():
    def __init__(self, *, instance_profile_arn: str, instance_type: str, service_role_arn: str, associate_public_ip_address: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, backup_id: typing.Optional[str]=None, backup_retention_count: typing.Optional[jsii.Number]=None, disable_automated_backup: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, engine: typing.Optional[str]=None, engine_attributes: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnServer.EngineAttributeProperty"]]]]]=None, engine_model: typing.Optional[str]=None, engine_version: typing.Optional[str]=None, key_pair: typing.Optional[str]=None, preferred_backup_window: typing.Optional[str]=None, preferred_maintenance_window: typing.Optional[str]=None, security_group_ids: typing.Optional[typing.List[str]]=None, server_name: typing.Optional[str]=None, subnet_ids: typing.Optional[typing.List[str]]=None):
        """Properties for defining a ``AWS::OpsWorksCM::Server``.

        :param instance_profile_arn: ``AWS::OpsWorksCM::Server.InstanceProfileArn``.
        :param instance_type: ``AWS::OpsWorksCM::Server.InstanceType``.
        :param service_role_arn: ``AWS::OpsWorksCM::Server.ServiceRoleArn``.
        :param associate_public_ip_address: ``AWS::OpsWorksCM::Server.AssociatePublicIpAddress``.
        :param backup_id: ``AWS::OpsWorksCM::Server.BackupId``.
        :param backup_retention_count: ``AWS::OpsWorksCM::Server.BackupRetentionCount``.
        :param disable_automated_backup: ``AWS::OpsWorksCM::Server.DisableAutomatedBackup``.
        :param engine: ``AWS::OpsWorksCM::Server.Engine``.
        :param engine_attributes: ``AWS::OpsWorksCM::Server.EngineAttributes``.
        :param engine_model: ``AWS::OpsWorksCM::Server.EngineModel``.
        :param engine_version: ``AWS::OpsWorksCM::Server.EngineVersion``.
        :param key_pair: ``AWS::OpsWorksCM::Server.KeyPair``.
        :param preferred_backup_window: ``AWS::OpsWorksCM::Server.PreferredBackupWindow``.
        :param preferred_maintenance_window: ``AWS::OpsWorksCM::Server.PreferredMaintenanceWindow``.
        :param security_group_ids: ``AWS::OpsWorksCM::Server.SecurityGroupIds``.
        :param server_name: ``AWS::OpsWorksCM::Server.ServerName``.
        :param subnet_ids: ``AWS::OpsWorksCM::Server.SubnetIds``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-opsworkscm-server.html
        """
        self._values = {
            'instance_profile_arn': instance_profile_arn,
            'instance_type': instance_type,
            'service_role_arn': service_role_arn,
        }
        if associate_public_ip_address is not None: self._values["associate_public_ip_address"] = associate_public_ip_address
        if backup_id is not None: self._values["backup_id"] = backup_id
        if backup_retention_count is not None: self._values["backup_retention_count"] = backup_retention_count
        if disable_automated_backup is not None: self._values["disable_automated_backup"] = disable_automated_backup
        if engine is not None: self._values["engine"] = engine
        if engine_attributes is not None: self._values["engine_attributes"] = engine_attributes
        if engine_model is not None: self._values["engine_model"] = engine_model
        if engine_version is not None: self._values["engine_version"] = engine_version
        if key_pair is not None: self._values["key_pair"] = key_pair
        if preferred_backup_window is not None: self._values["preferred_backup_window"] = preferred_backup_window
        if preferred_maintenance_window is not None: self._values["preferred_maintenance_window"] = preferred_maintenance_window
        if security_group_ids is not None: self._values["security_group_ids"] = security_group_ids
        if server_name is not None: self._values["server_name"] = server_name
        if subnet_ids is not None: self._values["subnet_ids"] = subnet_ids

    @property
    def instance_profile_arn(self) -> str:
        """``AWS::OpsWorksCM::Server.InstanceProfileArn``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-opsworkscm-server.html#cfn-opsworkscm-server-instanceprofilearn
        """
        return self._values.get('instance_profile_arn')

    @property
    def instance_type(self) -> str:
        """``AWS::OpsWorksCM::Server.InstanceType``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-opsworkscm-server.html#cfn-opsworkscm-server-instancetype
        """
        return self._values.get('instance_type')

    @property
    def service_role_arn(self) -> str:
        """``AWS::OpsWorksCM::Server.ServiceRoleArn``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-opsworkscm-server.html#cfn-opsworkscm-server-servicerolearn
        """
        return self._values.get('service_role_arn')

    @property
    def associate_public_ip_address(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::OpsWorksCM::Server.AssociatePublicIpAddress``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-opsworkscm-server.html#cfn-opsworkscm-server-associatepublicipaddress
        """
        return self._values.get('associate_public_ip_address')

    @property
    def backup_id(self) -> typing.Optional[str]:
        """``AWS::OpsWorksCM::Server.BackupId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-opsworkscm-server.html#cfn-opsworkscm-server-backupid
        """
        return self._values.get('backup_id')

    @property
    def backup_retention_count(self) -> typing.Optional[jsii.Number]:
        """``AWS::OpsWorksCM::Server.BackupRetentionCount``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-opsworkscm-server.html#cfn-opsworkscm-server-backupretentioncount
        """
        return self._values.get('backup_retention_count')

    @property
    def disable_automated_backup(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::OpsWorksCM::Server.DisableAutomatedBackup``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-opsworkscm-server.html#cfn-opsworkscm-server-disableautomatedbackup
        """
        return self._values.get('disable_automated_backup')

    @property
    def engine(self) -> typing.Optional[str]:
        """``AWS::OpsWorksCM::Server.Engine``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-opsworkscm-server.html#cfn-opsworkscm-server-engine
        """
        return self._values.get('engine')

    @property
    def engine_attributes(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnServer.EngineAttributeProperty"]]]]]:
        """``AWS::OpsWorksCM::Server.EngineAttributes``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-opsworkscm-server.html#cfn-opsworkscm-server-engineattributes
        """
        return self._values.get('engine_attributes')

    @property
    def engine_model(self) -> typing.Optional[str]:
        """``AWS::OpsWorksCM::Server.EngineModel``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-opsworkscm-server.html#cfn-opsworkscm-server-enginemodel
        """
        return self._values.get('engine_model')

    @property
    def engine_version(self) -> typing.Optional[str]:
        """``AWS::OpsWorksCM::Server.EngineVersion``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-opsworkscm-server.html#cfn-opsworkscm-server-engineversion
        """
        return self._values.get('engine_version')

    @property
    def key_pair(self) -> typing.Optional[str]:
        """``AWS::OpsWorksCM::Server.KeyPair``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-opsworkscm-server.html#cfn-opsworkscm-server-keypair
        """
        return self._values.get('key_pair')

    @property
    def preferred_backup_window(self) -> typing.Optional[str]:
        """``AWS::OpsWorksCM::Server.PreferredBackupWindow``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-opsworkscm-server.html#cfn-opsworkscm-server-preferredbackupwindow
        """
        return self._values.get('preferred_backup_window')

    @property
    def preferred_maintenance_window(self) -> typing.Optional[str]:
        """``AWS::OpsWorksCM::Server.PreferredMaintenanceWindow``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-opsworkscm-server.html#cfn-opsworkscm-server-preferredmaintenancewindow
        """
        return self._values.get('preferred_maintenance_window')

    @property
    def security_group_ids(self) -> typing.Optional[typing.List[str]]:
        """``AWS::OpsWorksCM::Server.SecurityGroupIds``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-opsworkscm-server.html#cfn-opsworkscm-server-securitygroupids
        """
        return self._values.get('security_group_ids')

    @property
    def server_name(self) -> typing.Optional[str]:
        """``AWS::OpsWorksCM::Server.ServerName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-opsworkscm-server.html#cfn-opsworkscm-server-servername
        """
        return self._values.get('server_name')

    @property
    def subnet_ids(self) -> typing.Optional[typing.List[str]]:
        """``AWS::OpsWorksCM::Server.SubnetIds``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-opsworkscm-server.html#cfn-opsworkscm-server-subnetids
        """
        return self._values.get('subnet_ids')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnServerProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


__all__ = ["CfnServer", "CfnServerProps", "__jsii_assembly__"]

publication.publish()
