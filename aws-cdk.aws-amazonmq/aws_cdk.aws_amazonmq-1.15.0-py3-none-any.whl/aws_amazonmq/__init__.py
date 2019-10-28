import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.core
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-amazonmq", "1.15.0", __name__, "aws-amazonmq@1.15.0.jsii.tgz")
class CfnBroker(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-amazonmq.CfnBroker"):
    """A CloudFormation ``AWS::AmazonMQ::Broker``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amazonmq-broker.html
    cloudformationResource:
    :cloudformationResource:: AWS::AmazonMQ::Broker
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, auto_minor_version_upgrade: typing.Union[bool, aws_cdk.core.IResolvable], broker_name: str, deployment_mode: str, engine_type: str, engine_version: str, host_instance_type: str, publicly_accessible: typing.Union[bool, aws_cdk.core.IResolvable], users: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "UserProperty"]]], configuration: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["ConfigurationIdProperty"]]]=None, encryption_options: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["EncryptionOptionsProperty"]]]=None, logs: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["LogListProperty"]]]=None, maintenance_window_start_time: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["MaintenanceWindowProperty"]]]=None, security_groups: typing.Optional[typing.List[str]]=None, subnet_ids: typing.Optional[typing.List[str]]=None, tags: typing.Optional[typing.List["TagsEntryProperty"]]=None) -> None:
        """Create a new ``AWS::AmazonMQ::Broker``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param auto_minor_version_upgrade: ``AWS::AmazonMQ::Broker.AutoMinorVersionUpgrade``.
        :param broker_name: ``AWS::AmazonMQ::Broker.BrokerName``.
        :param deployment_mode: ``AWS::AmazonMQ::Broker.DeploymentMode``.
        :param engine_type: ``AWS::AmazonMQ::Broker.EngineType``.
        :param engine_version: ``AWS::AmazonMQ::Broker.EngineVersion``.
        :param host_instance_type: ``AWS::AmazonMQ::Broker.HostInstanceType``.
        :param publicly_accessible: ``AWS::AmazonMQ::Broker.PubliclyAccessible``.
        :param users: ``AWS::AmazonMQ::Broker.Users``.
        :param configuration: ``AWS::AmazonMQ::Broker.Configuration``.
        :param encryption_options: ``AWS::AmazonMQ::Broker.EncryptionOptions``.
        :param logs: ``AWS::AmazonMQ::Broker.Logs``.
        :param maintenance_window_start_time: ``AWS::AmazonMQ::Broker.MaintenanceWindowStartTime``.
        :param security_groups: ``AWS::AmazonMQ::Broker.SecurityGroups``.
        :param subnet_ids: ``AWS::AmazonMQ::Broker.SubnetIds``.
        :param tags: ``AWS::AmazonMQ::Broker.Tags``.
        """
        props = CfnBrokerProps(auto_minor_version_upgrade=auto_minor_version_upgrade, broker_name=broker_name, deployment_mode=deployment_mode, engine_type=engine_type, engine_version=engine_version, host_instance_type=host_instance_type, publicly_accessible=publicly_accessible, users=users, configuration=configuration, encryption_options=encryption_options, logs=logs, maintenance_window_start_time=maintenance_window_start_time, security_groups=security_groups, subnet_ids=subnet_ids, tags=tags)

        jsii.create(CfnBroker, self, [scope, id, props])

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
    @jsii.member(jsii_name="attrAmqpEndpoints")
    def attr_amqp_endpoints(self) -> typing.List[str]:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: AmqpEndpoints
        """
        return jsii.get(self, "attrAmqpEndpoints")

    @property
    @jsii.member(jsii_name="attrArn")
    def attr_arn(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: Arn
        """
        return jsii.get(self, "attrArn")

    @property
    @jsii.member(jsii_name="attrConfigurationId")
    def attr_configuration_id(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: ConfigurationId
        """
        return jsii.get(self, "attrConfigurationId")

    @property
    @jsii.member(jsii_name="attrConfigurationRevision")
    def attr_configuration_revision(self) -> jsii.Number:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: ConfigurationRevision
        """
        return jsii.get(self, "attrConfigurationRevision")

    @property
    @jsii.member(jsii_name="attrIpAddresses")
    def attr_ip_addresses(self) -> typing.List[str]:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: IpAddresses
        """
        return jsii.get(self, "attrIpAddresses")

    @property
    @jsii.member(jsii_name="attrMqttEndpoints")
    def attr_mqtt_endpoints(self) -> typing.List[str]:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: MqttEndpoints
        """
        return jsii.get(self, "attrMqttEndpoints")

    @property
    @jsii.member(jsii_name="attrOpenWireEndpoints")
    def attr_open_wire_endpoints(self) -> typing.List[str]:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: OpenWireEndpoints
        """
        return jsii.get(self, "attrOpenWireEndpoints")

    @property
    @jsii.member(jsii_name="attrStompEndpoints")
    def attr_stomp_endpoints(self) -> typing.List[str]:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: StompEndpoints
        """
        return jsii.get(self, "attrStompEndpoints")

    @property
    @jsii.member(jsii_name="attrWssEndpoints")
    def attr_wss_endpoints(self) -> typing.List[str]:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: WssEndpoints
        """
        return jsii.get(self, "attrWssEndpoints")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        """``AWS::AmazonMQ::Broker.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amazonmq-broker.html#cfn-amazonmq-broker-tags
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="autoMinorVersionUpgrade")
    def auto_minor_version_upgrade(self) -> typing.Union[bool, aws_cdk.core.IResolvable]:
        """``AWS::AmazonMQ::Broker.AutoMinorVersionUpgrade``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amazonmq-broker.html#cfn-amazonmq-broker-autominorversionupgrade
        """
        return jsii.get(self, "autoMinorVersionUpgrade")

    @auto_minor_version_upgrade.setter
    def auto_minor_version_upgrade(self, value: typing.Union[bool, aws_cdk.core.IResolvable]):
        return jsii.set(self, "autoMinorVersionUpgrade", value)

    @property
    @jsii.member(jsii_name="brokerName")
    def broker_name(self) -> str:
        """``AWS::AmazonMQ::Broker.BrokerName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amazonmq-broker.html#cfn-amazonmq-broker-brokername
        """
        return jsii.get(self, "brokerName")

    @broker_name.setter
    def broker_name(self, value: str):
        return jsii.set(self, "brokerName", value)

    @property
    @jsii.member(jsii_name="deploymentMode")
    def deployment_mode(self) -> str:
        """``AWS::AmazonMQ::Broker.DeploymentMode``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amazonmq-broker.html#cfn-amazonmq-broker-deploymentmode
        """
        return jsii.get(self, "deploymentMode")

    @deployment_mode.setter
    def deployment_mode(self, value: str):
        return jsii.set(self, "deploymentMode", value)

    @property
    @jsii.member(jsii_name="engineType")
    def engine_type(self) -> str:
        """``AWS::AmazonMQ::Broker.EngineType``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amazonmq-broker.html#cfn-amazonmq-broker-enginetype
        """
        return jsii.get(self, "engineType")

    @engine_type.setter
    def engine_type(self, value: str):
        return jsii.set(self, "engineType", value)

    @property
    @jsii.member(jsii_name="engineVersion")
    def engine_version(self) -> str:
        """``AWS::AmazonMQ::Broker.EngineVersion``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amazonmq-broker.html#cfn-amazonmq-broker-engineversion
        """
        return jsii.get(self, "engineVersion")

    @engine_version.setter
    def engine_version(self, value: str):
        return jsii.set(self, "engineVersion", value)

    @property
    @jsii.member(jsii_name="hostInstanceType")
    def host_instance_type(self) -> str:
        """``AWS::AmazonMQ::Broker.HostInstanceType``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amazonmq-broker.html#cfn-amazonmq-broker-hostinstancetype
        """
        return jsii.get(self, "hostInstanceType")

    @host_instance_type.setter
    def host_instance_type(self, value: str):
        return jsii.set(self, "hostInstanceType", value)

    @property
    @jsii.member(jsii_name="publiclyAccessible")
    def publicly_accessible(self) -> typing.Union[bool, aws_cdk.core.IResolvable]:
        """``AWS::AmazonMQ::Broker.PubliclyAccessible``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amazonmq-broker.html#cfn-amazonmq-broker-publiclyaccessible
        """
        return jsii.get(self, "publiclyAccessible")

    @publicly_accessible.setter
    def publicly_accessible(self, value: typing.Union[bool, aws_cdk.core.IResolvable]):
        return jsii.set(self, "publiclyAccessible", value)

    @property
    @jsii.member(jsii_name="users")
    def users(self) -> typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "UserProperty"]]]:
        """``AWS::AmazonMQ::Broker.Users``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amazonmq-broker.html#cfn-amazonmq-broker-users
        """
        return jsii.get(self, "users")

    @users.setter
    def users(self, value: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "UserProperty"]]]):
        return jsii.set(self, "users", value)

    @property
    @jsii.member(jsii_name="configuration")
    def configuration(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["ConfigurationIdProperty"]]]:
        """``AWS::AmazonMQ::Broker.Configuration``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amazonmq-broker.html#cfn-amazonmq-broker-configuration
        """
        return jsii.get(self, "configuration")

    @configuration.setter
    def configuration(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["ConfigurationIdProperty"]]]):
        return jsii.set(self, "configuration", value)

    @property
    @jsii.member(jsii_name="encryptionOptions")
    def encryption_options(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["EncryptionOptionsProperty"]]]:
        """``AWS::AmazonMQ::Broker.EncryptionOptions``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amazonmq-broker.html#cfn-amazonmq-broker-encryptionoptions
        """
        return jsii.get(self, "encryptionOptions")

    @encryption_options.setter
    def encryption_options(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["EncryptionOptionsProperty"]]]):
        return jsii.set(self, "encryptionOptions", value)

    @property
    @jsii.member(jsii_name="logs")
    def logs(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["LogListProperty"]]]:
        """``AWS::AmazonMQ::Broker.Logs``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amazonmq-broker.html#cfn-amazonmq-broker-logs
        """
        return jsii.get(self, "logs")

    @logs.setter
    def logs(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["LogListProperty"]]]):
        return jsii.set(self, "logs", value)

    @property
    @jsii.member(jsii_name="maintenanceWindowStartTime")
    def maintenance_window_start_time(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["MaintenanceWindowProperty"]]]:
        """``AWS::AmazonMQ::Broker.MaintenanceWindowStartTime``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amazonmq-broker.html#cfn-amazonmq-broker-maintenancewindowstarttime
        """
        return jsii.get(self, "maintenanceWindowStartTime")

    @maintenance_window_start_time.setter
    def maintenance_window_start_time(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["MaintenanceWindowProperty"]]]):
        return jsii.set(self, "maintenanceWindowStartTime", value)

    @property
    @jsii.member(jsii_name="securityGroups")
    def security_groups(self) -> typing.Optional[typing.List[str]]:
        """``AWS::AmazonMQ::Broker.SecurityGroups``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amazonmq-broker.html#cfn-amazonmq-broker-securitygroups
        """
        return jsii.get(self, "securityGroups")

    @security_groups.setter
    def security_groups(self, value: typing.Optional[typing.List[str]]):
        return jsii.set(self, "securityGroups", value)

    @property
    @jsii.member(jsii_name="subnetIds")
    def subnet_ids(self) -> typing.Optional[typing.List[str]]:
        """``AWS::AmazonMQ::Broker.SubnetIds``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amazonmq-broker.html#cfn-amazonmq-broker-subnetids
        """
        return jsii.get(self, "subnetIds")

    @subnet_ids.setter
    def subnet_ids(self, value: typing.Optional[typing.List[str]]):
        return jsii.set(self, "subnetIds", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-amazonmq.CfnBroker.ConfigurationIdProperty", jsii_struct_bases=[], name_mapping={'id': 'id', 'revision': 'revision'})
    class ConfigurationIdProperty():
        def __init__(self, *, id: str, revision: jsii.Number):
            """
            :param id: ``CfnBroker.ConfigurationIdProperty.Id``.
            :param revision: ``CfnBroker.ConfigurationIdProperty.Revision``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-amazonmq-broker-configurationid.html
            """
            self._values = {
                'id': id,
                'revision': revision,
            }

        @property
        def id(self) -> str:
            """``CfnBroker.ConfigurationIdProperty.Id``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-amazonmq-broker-configurationid.html#cfn-amazonmq-broker-configurationid-id
            """
            return self._values.get('id')

        @property
        def revision(self) -> jsii.Number:
            """``CfnBroker.ConfigurationIdProperty.Revision``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-amazonmq-broker-configurationid.html#cfn-amazonmq-broker-configurationid-revision
            """
            return self._values.get('revision')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'ConfigurationIdProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-amazonmq.CfnBroker.EncryptionOptionsProperty", jsii_struct_bases=[], name_mapping={'use_aws_owned_key': 'useAwsOwnedKey', 'kms_key_id': 'kmsKeyId'})
    class EncryptionOptionsProperty():
        def __init__(self, *, use_aws_owned_key: typing.Union[bool, aws_cdk.core.IResolvable], kms_key_id: typing.Optional[str]=None):
            """
            :param use_aws_owned_key: ``CfnBroker.EncryptionOptionsProperty.UseAwsOwnedKey``.
            :param kms_key_id: ``CfnBroker.EncryptionOptionsProperty.KmsKeyId``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-amazonmq-broker-encryptionoptions.html
            """
            self._values = {
                'use_aws_owned_key': use_aws_owned_key,
            }
            if kms_key_id is not None: self._values["kms_key_id"] = kms_key_id

        @property
        def use_aws_owned_key(self) -> typing.Union[bool, aws_cdk.core.IResolvable]:
            """``CfnBroker.EncryptionOptionsProperty.UseAwsOwnedKey``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-amazonmq-broker-encryptionoptions.html#cfn-amazonmq-broker-encryptionoptions-useawsownedkey
            """
            return self._values.get('use_aws_owned_key')

        @property
        def kms_key_id(self) -> typing.Optional[str]:
            """``CfnBroker.EncryptionOptionsProperty.KmsKeyId``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-amazonmq-broker-encryptionoptions.html#cfn-amazonmq-broker-encryptionoptions-kmskeyid
            """
            return self._values.get('kms_key_id')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'EncryptionOptionsProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-amazonmq.CfnBroker.LogListProperty", jsii_struct_bases=[], name_mapping={'audit': 'audit', 'general': 'general'})
    class LogListProperty():
        def __init__(self, *, audit: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, general: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None):
            """
            :param audit: ``CfnBroker.LogListProperty.Audit``.
            :param general: ``CfnBroker.LogListProperty.General``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-amazonmq-broker-loglist.html
            """
            self._values = {
            }
            if audit is not None: self._values["audit"] = audit
            if general is not None: self._values["general"] = general

        @property
        def audit(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
            """``CfnBroker.LogListProperty.Audit``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-amazonmq-broker-loglist.html#cfn-amazonmq-broker-loglist-audit
            """
            return self._values.get('audit')

        @property
        def general(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
            """``CfnBroker.LogListProperty.General``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-amazonmq-broker-loglist.html#cfn-amazonmq-broker-loglist-general
            """
            return self._values.get('general')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'LogListProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-amazonmq.CfnBroker.MaintenanceWindowProperty", jsii_struct_bases=[], name_mapping={'day_of_week': 'dayOfWeek', 'time_of_day': 'timeOfDay', 'time_zone': 'timeZone'})
    class MaintenanceWindowProperty():
        def __init__(self, *, day_of_week: str, time_of_day: str, time_zone: str):
            """
            :param day_of_week: ``CfnBroker.MaintenanceWindowProperty.DayOfWeek``.
            :param time_of_day: ``CfnBroker.MaintenanceWindowProperty.TimeOfDay``.
            :param time_zone: ``CfnBroker.MaintenanceWindowProperty.TimeZone``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-amazonmq-broker-maintenancewindow.html
            """
            self._values = {
                'day_of_week': day_of_week,
                'time_of_day': time_of_day,
                'time_zone': time_zone,
            }

        @property
        def day_of_week(self) -> str:
            """``CfnBroker.MaintenanceWindowProperty.DayOfWeek``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-amazonmq-broker-maintenancewindow.html#cfn-amazonmq-broker-maintenancewindow-dayofweek
            """
            return self._values.get('day_of_week')

        @property
        def time_of_day(self) -> str:
            """``CfnBroker.MaintenanceWindowProperty.TimeOfDay``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-amazonmq-broker-maintenancewindow.html#cfn-amazonmq-broker-maintenancewindow-timeofday
            """
            return self._values.get('time_of_day')

        @property
        def time_zone(self) -> str:
            """``CfnBroker.MaintenanceWindowProperty.TimeZone``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-amazonmq-broker-maintenancewindow.html#cfn-amazonmq-broker-maintenancewindow-timezone
            """
            return self._values.get('time_zone')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'MaintenanceWindowProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-amazonmq.CfnBroker.TagsEntryProperty", jsii_struct_bases=[], name_mapping={'key': 'key', 'value': 'value'})
    class TagsEntryProperty():
        def __init__(self, *, key: str, value: str):
            """
            :param key: ``CfnBroker.TagsEntryProperty.Key``.
            :param value: ``CfnBroker.TagsEntryProperty.Value``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-amazonmq-broker-tagsentry.html
            """
            self._values = {
                'key': key,
                'value': value,
            }

        @property
        def key(self) -> str:
            """``CfnBroker.TagsEntryProperty.Key``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-amazonmq-broker-tagsentry.html#cfn-amazonmq-broker-tagsentry-key
            """
            return self._values.get('key')

        @property
        def value(self) -> str:
            """``CfnBroker.TagsEntryProperty.Value``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-amazonmq-broker-tagsentry.html#cfn-amazonmq-broker-tagsentry-value
            """
            return self._values.get('value')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'TagsEntryProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-amazonmq.CfnBroker.UserProperty", jsii_struct_bases=[], name_mapping={'password': 'password', 'username': 'username', 'console_access': 'consoleAccess', 'groups': 'groups'})
    class UserProperty():
        def __init__(self, *, password: str, username: str, console_access: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, groups: typing.Optional[typing.List[str]]=None):
            """
            :param password: ``CfnBroker.UserProperty.Password``.
            :param username: ``CfnBroker.UserProperty.Username``.
            :param console_access: ``CfnBroker.UserProperty.ConsoleAccess``.
            :param groups: ``CfnBroker.UserProperty.Groups``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-amazonmq-broker-user.html
            """
            self._values = {
                'password': password,
                'username': username,
            }
            if console_access is not None: self._values["console_access"] = console_access
            if groups is not None: self._values["groups"] = groups

        @property
        def password(self) -> str:
            """``CfnBroker.UserProperty.Password``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-amazonmq-broker-user.html#cfn-amazonmq-broker-user-password
            """
            return self._values.get('password')

        @property
        def username(self) -> str:
            """``CfnBroker.UserProperty.Username``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-amazonmq-broker-user.html#cfn-amazonmq-broker-user-username
            """
            return self._values.get('username')

        @property
        def console_access(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
            """``CfnBroker.UserProperty.ConsoleAccess``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-amazonmq-broker-user.html#cfn-amazonmq-broker-user-consoleaccess
            """
            return self._values.get('console_access')

        @property
        def groups(self) -> typing.Optional[typing.List[str]]:
            """``CfnBroker.UserProperty.Groups``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-amazonmq-broker-user.html#cfn-amazonmq-broker-user-groups
            """
            return self._values.get('groups')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'UserProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



@jsii.data_type(jsii_type="@aws-cdk/aws-amazonmq.CfnBrokerProps", jsii_struct_bases=[], name_mapping={'auto_minor_version_upgrade': 'autoMinorVersionUpgrade', 'broker_name': 'brokerName', 'deployment_mode': 'deploymentMode', 'engine_type': 'engineType', 'engine_version': 'engineVersion', 'host_instance_type': 'hostInstanceType', 'publicly_accessible': 'publiclyAccessible', 'users': 'users', 'configuration': 'configuration', 'encryption_options': 'encryptionOptions', 'logs': 'logs', 'maintenance_window_start_time': 'maintenanceWindowStartTime', 'security_groups': 'securityGroups', 'subnet_ids': 'subnetIds', 'tags': 'tags'})
class CfnBrokerProps():
    def __init__(self, *, auto_minor_version_upgrade: typing.Union[bool, aws_cdk.core.IResolvable], broker_name: str, deployment_mode: str, engine_type: str, engine_version: str, host_instance_type: str, publicly_accessible: typing.Union[bool, aws_cdk.core.IResolvable], users: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnBroker.UserProperty"]]], configuration: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnBroker.ConfigurationIdProperty"]]]=None, encryption_options: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnBroker.EncryptionOptionsProperty"]]]=None, logs: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnBroker.LogListProperty"]]]=None, maintenance_window_start_time: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnBroker.MaintenanceWindowProperty"]]]=None, security_groups: typing.Optional[typing.List[str]]=None, subnet_ids: typing.Optional[typing.List[str]]=None, tags: typing.Optional[typing.List["CfnBroker.TagsEntryProperty"]]=None):
        """Properties for defining a ``AWS::AmazonMQ::Broker``.

        :param auto_minor_version_upgrade: ``AWS::AmazonMQ::Broker.AutoMinorVersionUpgrade``.
        :param broker_name: ``AWS::AmazonMQ::Broker.BrokerName``.
        :param deployment_mode: ``AWS::AmazonMQ::Broker.DeploymentMode``.
        :param engine_type: ``AWS::AmazonMQ::Broker.EngineType``.
        :param engine_version: ``AWS::AmazonMQ::Broker.EngineVersion``.
        :param host_instance_type: ``AWS::AmazonMQ::Broker.HostInstanceType``.
        :param publicly_accessible: ``AWS::AmazonMQ::Broker.PubliclyAccessible``.
        :param users: ``AWS::AmazonMQ::Broker.Users``.
        :param configuration: ``AWS::AmazonMQ::Broker.Configuration``.
        :param encryption_options: ``AWS::AmazonMQ::Broker.EncryptionOptions``.
        :param logs: ``AWS::AmazonMQ::Broker.Logs``.
        :param maintenance_window_start_time: ``AWS::AmazonMQ::Broker.MaintenanceWindowStartTime``.
        :param security_groups: ``AWS::AmazonMQ::Broker.SecurityGroups``.
        :param subnet_ids: ``AWS::AmazonMQ::Broker.SubnetIds``.
        :param tags: ``AWS::AmazonMQ::Broker.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amazonmq-broker.html
        """
        self._values = {
            'auto_minor_version_upgrade': auto_minor_version_upgrade,
            'broker_name': broker_name,
            'deployment_mode': deployment_mode,
            'engine_type': engine_type,
            'engine_version': engine_version,
            'host_instance_type': host_instance_type,
            'publicly_accessible': publicly_accessible,
            'users': users,
        }
        if configuration is not None: self._values["configuration"] = configuration
        if encryption_options is not None: self._values["encryption_options"] = encryption_options
        if logs is not None: self._values["logs"] = logs
        if maintenance_window_start_time is not None: self._values["maintenance_window_start_time"] = maintenance_window_start_time
        if security_groups is not None: self._values["security_groups"] = security_groups
        if subnet_ids is not None: self._values["subnet_ids"] = subnet_ids
        if tags is not None: self._values["tags"] = tags

    @property
    def auto_minor_version_upgrade(self) -> typing.Union[bool, aws_cdk.core.IResolvable]:
        """``AWS::AmazonMQ::Broker.AutoMinorVersionUpgrade``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amazonmq-broker.html#cfn-amazonmq-broker-autominorversionupgrade
        """
        return self._values.get('auto_minor_version_upgrade')

    @property
    def broker_name(self) -> str:
        """``AWS::AmazonMQ::Broker.BrokerName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amazonmq-broker.html#cfn-amazonmq-broker-brokername
        """
        return self._values.get('broker_name')

    @property
    def deployment_mode(self) -> str:
        """``AWS::AmazonMQ::Broker.DeploymentMode``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amazonmq-broker.html#cfn-amazonmq-broker-deploymentmode
        """
        return self._values.get('deployment_mode')

    @property
    def engine_type(self) -> str:
        """``AWS::AmazonMQ::Broker.EngineType``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amazonmq-broker.html#cfn-amazonmq-broker-enginetype
        """
        return self._values.get('engine_type')

    @property
    def engine_version(self) -> str:
        """``AWS::AmazonMQ::Broker.EngineVersion``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amazonmq-broker.html#cfn-amazonmq-broker-engineversion
        """
        return self._values.get('engine_version')

    @property
    def host_instance_type(self) -> str:
        """``AWS::AmazonMQ::Broker.HostInstanceType``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amazonmq-broker.html#cfn-amazonmq-broker-hostinstancetype
        """
        return self._values.get('host_instance_type')

    @property
    def publicly_accessible(self) -> typing.Union[bool, aws_cdk.core.IResolvable]:
        """``AWS::AmazonMQ::Broker.PubliclyAccessible``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amazonmq-broker.html#cfn-amazonmq-broker-publiclyaccessible
        """
        return self._values.get('publicly_accessible')

    @property
    def users(self) -> typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnBroker.UserProperty"]]]:
        """``AWS::AmazonMQ::Broker.Users``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amazonmq-broker.html#cfn-amazonmq-broker-users
        """
        return self._values.get('users')

    @property
    def configuration(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnBroker.ConfigurationIdProperty"]]]:
        """``AWS::AmazonMQ::Broker.Configuration``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amazonmq-broker.html#cfn-amazonmq-broker-configuration
        """
        return self._values.get('configuration')

    @property
    def encryption_options(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnBroker.EncryptionOptionsProperty"]]]:
        """``AWS::AmazonMQ::Broker.EncryptionOptions``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amazonmq-broker.html#cfn-amazonmq-broker-encryptionoptions
        """
        return self._values.get('encryption_options')

    @property
    def logs(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnBroker.LogListProperty"]]]:
        """``AWS::AmazonMQ::Broker.Logs``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amazonmq-broker.html#cfn-amazonmq-broker-logs
        """
        return self._values.get('logs')

    @property
    def maintenance_window_start_time(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnBroker.MaintenanceWindowProperty"]]]:
        """``AWS::AmazonMQ::Broker.MaintenanceWindowStartTime``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amazonmq-broker.html#cfn-amazonmq-broker-maintenancewindowstarttime
        """
        return self._values.get('maintenance_window_start_time')

    @property
    def security_groups(self) -> typing.Optional[typing.List[str]]:
        """``AWS::AmazonMQ::Broker.SecurityGroups``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amazonmq-broker.html#cfn-amazonmq-broker-securitygroups
        """
        return self._values.get('security_groups')

    @property
    def subnet_ids(self) -> typing.Optional[typing.List[str]]:
        """``AWS::AmazonMQ::Broker.SubnetIds``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amazonmq-broker.html#cfn-amazonmq-broker-subnetids
        """
        return self._values.get('subnet_ids')

    @property
    def tags(self) -> typing.Optional[typing.List["CfnBroker.TagsEntryProperty"]]:
        """``AWS::AmazonMQ::Broker.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amazonmq-broker.html#cfn-amazonmq-broker-tags
        """
        return self._values.get('tags')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnBrokerProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnConfiguration(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-amazonmq.CfnConfiguration"):
    """A CloudFormation ``AWS::AmazonMQ::Configuration``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amazonmq-configuration.html
    cloudformationResource:
    :cloudformationResource:: AWS::AmazonMQ::Configuration
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, data: str, engine_type: str, engine_version: str, name: str, description: typing.Optional[str]=None, tags: typing.Optional[typing.List["TagsEntryProperty"]]=None) -> None:
        """Create a new ``AWS::AmazonMQ::Configuration``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param data: ``AWS::AmazonMQ::Configuration.Data``.
        :param engine_type: ``AWS::AmazonMQ::Configuration.EngineType``.
        :param engine_version: ``AWS::AmazonMQ::Configuration.EngineVersion``.
        :param name: ``AWS::AmazonMQ::Configuration.Name``.
        :param description: ``AWS::AmazonMQ::Configuration.Description``.
        :param tags: ``AWS::AmazonMQ::Configuration.Tags``.
        """
        props = CfnConfigurationProps(data=data, engine_type=engine_type, engine_version=engine_version, name=name, description=description, tags=tags)

        jsii.create(CfnConfiguration, self, [scope, id, props])

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
    @jsii.member(jsii_name="attrRevision")
    def attr_revision(self) -> jsii.Number:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: Revision
        """
        return jsii.get(self, "attrRevision")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        """``AWS::AmazonMQ::Configuration.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amazonmq-configuration.html#cfn-amazonmq-configuration-tags
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="data")
    def data(self) -> str:
        """``AWS::AmazonMQ::Configuration.Data``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amazonmq-configuration.html#cfn-amazonmq-configuration-data
        """
        return jsii.get(self, "data")

    @data.setter
    def data(self, value: str):
        return jsii.set(self, "data", value)

    @property
    @jsii.member(jsii_name="engineType")
    def engine_type(self) -> str:
        """``AWS::AmazonMQ::Configuration.EngineType``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amazonmq-configuration.html#cfn-amazonmq-configuration-enginetype
        """
        return jsii.get(self, "engineType")

    @engine_type.setter
    def engine_type(self, value: str):
        return jsii.set(self, "engineType", value)

    @property
    @jsii.member(jsii_name="engineVersion")
    def engine_version(self) -> str:
        """``AWS::AmazonMQ::Configuration.EngineVersion``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amazonmq-configuration.html#cfn-amazonmq-configuration-engineversion
        """
        return jsii.get(self, "engineVersion")

    @engine_version.setter
    def engine_version(self, value: str):
        return jsii.set(self, "engineVersion", value)

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> str:
        """``AWS::AmazonMQ::Configuration.Name``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amazonmq-configuration.html#cfn-amazonmq-configuration-name
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: str):
        return jsii.set(self, "name", value)

    @property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[str]:
        """``AWS::AmazonMQ::Configuration.Description``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amazonmq-configuration.html#cfn-amazonmq-configuration-description
        """
        return jsii.get(self, "description")

    @description.setter
    def description(self, value: typing.Optional[str]):
        return jsii.set(self, "description", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-amazonmq.CfnConfiguration.TagsEntryProperty", jsii_struct_bases=[], name_mapping={'key': 'key', 'value': 'value'})
    class TagsEntryProperty():
        def __init__(self, *, key: str, value: str):
            """
            :param key: ``CfnConfiguration.TagsEntryProperty.Key``.
            :param value: ``CfnConfiguration.TagsEntryProperty.Value``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-amazonmq-configuration-tagsentry.html
            """
            self._values = {
                'key': key,
                'value': value,
            }

        @property
        def key(self) -> str:
            """``CfnConfiguration.TagsEntryProperty.Key``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-amazonmq-configuration-tagsentry.html#cfn-amazonmq-configuration-tagsentry-key
            """
            return self._values.get('key')

        @property
        def value(self) -> str:
            """``CfnConfiguration.TagsEntryProperty.Value``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-amazonmq-configuration-tagsentry.html#cfn-amazonmq-configuration-tagsentry-value
            """
            return self._values.get('value')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'TagsEntryProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



class CfnConfigurationAssociation(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-amazonmq.CfnConfigurationAssociation"):
    """A CloudFormation ``AWS::AmazonMQ::ConfigurationAssociation``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amazonmq-configurationassociation.html
    cloudformationResource:
    :cloudformationResource:: AWS::AmazonMQ::ConfigurationAssociation
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, broker: str, configuration: typing.Union[aws_cdk.core.IResolvable, "ConfigurationIdProperty"]) -> None:
        """Create a new ``AWS::AmazonMQ::ConfigurationAssociation``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param broker: ``AWS::AmazonMQ::ConfigurationAssociation.Broker``.
        :param configuration: ``AWS::AmazonMQ::ConfigurationAssociation.Configuration``.
        """
        props = CfnConfigurationAssociationProps(broker=broker, configuration=configuration)

        jsii.create(CfnConfigurationAssociation, self, [scope, id, props])

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
    @jsii.member(jsii_name="broker")
    def broker(self) -> str:
        """``AWS::AmazonMQ::ConfigurationAssociation.Broker``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amazonmq-configurationassociation.html#cfn-amazonmq-configurationassociation-broker
        """
        return jsii.get(self, "broker")

    @broker.setter
    def broker(self, value: str):
        return jsii.set(self, "broker", value)

    @property
    @jsii.member(jsii_name="configuration")
    def configuration(self) -> typing.Union[aws_cdk.core.IResolvable, "ConfigurationIdProperty"]:
        """``AWS::AmazonMQ::ConfigurationAssociation.Configuration``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amazonmq-configurationassociation.html#cfn-amazonmq-configurationassociation-configuration
        """
        return jsii.get(self, "configuration")

    @configuration.setter
    def configuration(self, value: typing.Union[aws_cdk.core.IResolvable, "ConfigurationIdProperty"]):
        return jsii.set(self, "configuration", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-amazonmq.CfnConfigurationAssociation.ConfigurationIdProperty", jsii_struct_bases=[], name_mapping={'id': 'id', 'revision': 'revision'})
    class ConfigurationIdProperty():
        def __init__(self, *, id: str, revision: jsii.Number):
            """
            :param id: ``CfnConfigurationAssociation.ConfigurationIdProperty.Id``.
            :param revision: ``CfnConfigurationAssociation.ConfigurationIdProperty.Revision``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-amazonmq-configurationassociation-configurationid.html
            """
            self._values = {
                'id': id,
                'revision': revision,
            }

        @property
        def id(self) -> str:
            """``CfnConfigurationAssociation.ConfigurationIdProperty.Id``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-amazonmq-configurationassociation-configurationid.html#cfn-amazonmq-configurationassociation-configurationid-id
            """
            return self._values.get('id')

        @property
        def revision(self) -> jsii.Number:
            """``CfnConfigurationAssociation.ConfigurationIdProperty.Revision``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-amazonmq-configurationassociation-configurationid.html#cfn-amazonmq-configurationassociation-configurationid-revision
            """
            return self._values.get('revision')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'ConfigurationIdProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



@jsii.data_type(jsii_type="@aws-cdk/aws-amazonmq.CfnConfigurationAssociationProps", jsii_struct_bases=[], name_mapping={'broker': 'broker', 'configuration': 'configuration'})
class CfnConfigurationAssociationProps():
    def __init__(self, *, broker: str, configuration: typing.Union[aws_cdk.core.IResolvable, "CfnConfigurationAssociation.ConfigurationIdProperty"]):
        """Properties for defining a ``AWS::AmazonMQ::ConfigurationAssociation``.

        :param broker: ``AWS::AmazonMQ::ConfigurationAssociation.Broker``.
        :param configuration: ``AWS::AmazonMQ::ConfigurationAssociation.Configuration``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amazonmq-configurationassociation.html
        """
        self._values = {
            'broker': broker,
            'configuration': configuration,
        }

    @property
    def broker(self) -> str:
        """``AWS::AmazonMQ::ConfigurationAssociation.Broker``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amazonmq-configurationassociation.html#cfn-amazonmq-configurationassociation-broker
        """
        return self._values.get('broker')

    @property
    def configuration(self) -> typing.Union[aws_cdk.core.IResolvable, "CfnConfigurationAssociation.ConfigurationIdProperty"]:
        """``AWS::AmazonMQ::ConfigurationAssociation.Configuration``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amazonmq-configurationassociation.html#cfn-amazonmq-configurationassociation-configuration
        """
        return self._values.get('configuration')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnConfigurationAssociationProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


@jsii.data_type(jsii_type="@aws-cdk/aws-amazonmq.CfnConfigurationProps", jsii_struct_bases=[], name_mapping={'data': 'data', 'engine_type': 'engineType', 'engine_version': 'engineVersion', 'name': 'name', 'description': 'description', 'tags': 'tags'})
class CfnConfigurationProps():
    def __init__(self, *, data: str, engine_type: str, engine_version: str, name: str, description: typing.Optional[str]=None, tags: typing.Optional[typing.List["CfnConfiguration.TagsEntryProperty"]]=None):
        """Properties for defining a ``AWS::AmazonMQ::Configuration``.

        :param data: ``AWS::AmazonMQ::Configuration.Data``.
        :param engine_type: ``AWS::AmazonMQ::Configuration.EngineType``.
        :param engine_version: ``AWS::AmazonMQ::Configuration.EngineVersion``.
        :param name: ``AWS::AmazonMQ::Configuration.Name``.
        :param description: ``AWS::AmazonMQ::Configuration.Description``.
        :param tags: ``AWS::AmazonMQ::Configuration.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amazonmq-configuration.html
        """
        self._values = {
            'data': data,
            'engine_type': engine_type,
            'engine_version': engine_version,
            'name': name,
        }
        if description is not None: self._values["description"] = description
        if tags is not None: self._values["tags"] = tags

    @property
    def data(self) -> str:
        """``AWS::AmazonMQ::Configuration.Data``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amazonmq-configuration.html#cfn-amazonmq-configuration-data
        """
        return self._values.get('data')

    @property
    def engine_type(self) -> str:
        """``AWS::AmazonMQ::Configuration.EngineType``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amazonmq-configuration.html#cfn-amazonmq-configuration-enginetype
        """
        return self._values.get('engine_type')

    @property
    def engine_version(self) -> str:
        """``AWS::AmazonMQ::Configuration.EngineVersion``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amazonmq-configuration.html#cfn-amazonmq-configuration-engineversion
        """
        return self._values.get('engine_version')

    @property
    def name(self) -> str:
        """``AWS::AmazonMQ::Configuration.Name``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amazonmq-configuration.html#cfn-amazonmq-configuration-name
        """
        return self._values.get('name')

    @property
    def description(self) -> typing.Optional[str]:
        """``AWS::AmazonMQ::Configuration.Description``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amazonmq-configuration.html#cfn-amazonmq-configuration-description
        """
        return self._values.get('description')

    @property
    def tags(self) -> typing.Optional[typing.List["CfnConfiguration.TagsEntryProperty"]]:
        """``AWS::AmazonMQ::Configuration.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amazonmq-configuration.html#cfn-amazonmq-configuration-tags
        """
        return self._values.get('tags')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnConfigurationProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


__all__ = ["CfnBroker", "CfnBrokerProps", "CfnConfiguration", "CfnConfigurationAssociation", "CfnConfigurationAssociationProps", "CfnConfigurationProps", "__jsii_assembly__"]

publication.publish()
