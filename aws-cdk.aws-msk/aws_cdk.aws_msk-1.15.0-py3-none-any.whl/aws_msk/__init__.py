import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.core
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-msk", "1.15.0", __name__, "aws-msk@1.15.0.jsii.tgz")
class CfnCluster(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-msk.CfnCluster"):
    """A CloudFormation ``AWS::MSK::Cluster``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-msk-cluster.html
    cloudformationResource:
    :cloudformationResource:: AWS::MSK::Cluster
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, broker_node_group_info: typing.Union["BrokerNodeGroupInfoProperty", aws_cdk.core.IResolvable], cluster_name: str, kafka_version: str, number_of_broker_nodes: jsii.Number, client_authentication: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["ClientAuthenticationProperty"]]]=None, configuration_info: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["ConfigurationInfoProperty"]]]=None, encryption_info: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["EncryptionInfoProperty"]]]=None, enhanced_monitoring: typing.Optional[str]=None, tags: typing.Any=None) -> None:
        """Create a new ``AWS::MSK::Cluster``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param broker_node_group_info: ``AWS::MSK::Cluster.BrokerNodeGroupInfo``.
        :param cluster_name: ``AWS::MSK::Cluster.ClusterName``.
        :param kafka_version: ``AWS::MSK::Cluster.KafkaVersion``.
        :param number_of_broker_nodes: ``AWS::MSK::Cluster.NumberOfBrokerNodes``.
        :param client_authentication: ``AWS::MSK::Cluster.ClientAuthentication``.
        :param configuration_info: ``AWS::MSK::Cluster.ConfigurationInfo``.
        :param encryption_info: ``AWS::MSK::Cluster.EncryptionInfo``.
        :param enhanced_monitoring: ``AWS::MSK::Cluster.EnhancedMonitoring``.
        :param tags: ``AWS::MSK::Cluster.Tags``.
        """
        props = CfnClusterProps(broker_node_group_info=broker_node_group_info, cluster_name=cluster_name, kafka_version=kafka_version, number_of_broker_nodes=number_of_broker_nodes, client_authentication=client_authentication, configuration_info=configuration_info, encryption_info=encryption_info, enhanced_monitoring=enhanced_monitoring, tags=tags)

        jsii.create(CfnCluster, self, [scope, id, props])

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
        """``AWS::MSK::Cluster.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-msk-cluster.html#cfn-msk-cluster-tags
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="brokerNodeGroupInfo")
    def broker_node_group_info(self) -> typing.Union["BrokerNodeGroupInfoProperty", aws_cdk.core.IResolvable]:
        """``AWS::MSK::Cluster.BrokerNodeGroupInfo``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-msk-cluster.html#cfn-msk-cluster-brokernodegroupinfo
        """
        return jsii.get(self, "brokerNodeGroupInfo")

    @broker_node_group_info.setter
    def broker_node_group_info(self, value: typing.Union["BrokerNodeGroupInfoProperty", aws_cdk.core.IResolvable]):
        return jsii.set(self, "brokerNodeGroupInfo", value)

    @property
    @jsii.member(jsii_name="clusterName")
    def cluster_name(self) -> str:
        """``AWS::MSK::Cluster.ClusterName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-msk-cluster.html#cfn-msk-cluster-clustername
        """
        return jsii.get(self, "clusterName")

    @cluster_name.setter
    def cluster_name(self, value: str):
        return jsii.set(self, "clusterName", value)

    @property
    @jsii.member(jsii_name="kafkaVersion")
    def kafka_version(self) -> str:
        """``AWS::MSK::Cluster.KafkaVersion``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-msk-cluster.html#cfn-msk-cluster-kafkaversion
        """
        return jsii.get(self, "kafkaVersion")

    @kafka_version.setter
    def kafka_version(self, value: str):
        return jsii.set(self, "kafkaVersion", value)

    @property
    @jsii.member(jsii_name="numberOfBrokerNodes")
    def number_of_broker_nodes(self) -> jsii.Number:
        """``AWS::MSK::Cluster.NumberOfBrokerNodes``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-msk-cluster.html#cfn-msk-cluster-numberofbrokernodes
        """
        return jsii.get(self, "numberOfBrokerNodes")

    @number_of_broker_nodes.setter
    def number_of_broker_nodes(self, value: jsii.Number):
        return jsii.set(self, "numberOfBrokerNodes", value)

    @property
    @jsii.member(jsii_name="clientAuthentication")
    def client_authentication(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["ClientAuthenticationProperty"]]]:
        """``AWS::MSK::Cluster.ClientAuthentication``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-msk-cluster.html#cfn-msk-cluster-clientauthentication
        """
        return jsii.get(self, "clientAuthentication")

    @client_authentication.setter
    def client_authentication(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["ClientAuthenticationProperty"]]]):
        return jsii.set(self, "clientAuthentication", value)

    @property
    @jsii.member(jsii_name="configurationInfo")
    def configuration_info(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["ConfigurationInfoProperty"]]]:
        """``AWS::MSK::Cluster.ConfigurationInfo``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-msk-cluster.html#cfn-msk-cluster-configurationinfo
        """
        return jsii.get(self, "configurationInfo")

    @configuration_info.setter
    def configuration_info(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["ConfigurationInfoProperty"]]]):
        return jsii.set(self, "configurationInfo", value)

    @property
    @jsii.member(jsii_name="encryptionInfo")
    def encryption_info(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["EncryptionInfoProperty"]]]:
        """``AWS::MSK::Cluster.EncryptionInfo``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-msk-cluster.html#cfn-msk-cluster-encryptioninfo
        """
        return jsii.get(self, "encryptionInfo")

    @encryption_info.setter
    def encryption_info(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["EncryptionInfoProperty"]]]):
        return jsii.set(self, "encryptionInfo", value)

    @property
    @jsii.member(jsii_name="enhancedMonitoring")
    def enhanced_monitoring(self) -> typing.Optional[str]:
        """``AWS::MSK::Cluster.EnhancedMonitoring``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-msk-cluster.html#cfn-msk-cluster-enhancedmonitoring
        """
        return jsii.get(self, "enhancedMonitoring")

    @enhanced_monitoring.setter
    def enhanced_monitoring(self, value: typing.Optional[str]):
        return jsii.set(self, "enhancedMonitoring", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-msk.CfnCluster.BrokerNodeGroupInfoProperty", jsii_struct_bases=[], name_mapping={'client_subnets': 'clientSubnets', 'instance_type': 'instanceType', 'broker_az_distribution': 'brokerAzDistribution', 'security_groups': 'securityGroups', 'storage_info': 'storageInfo'})
    class BrokerNodeGroupInfoProperty():
        def __init__(self, *, client_subnets: typing.List[str], instance_type: str, broker_az_distribution: typing.Optional[str]=None, security_groups: typing.Optional[typing.List[str]]=None, storage_info: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnCluster.StorageInfoProperty"]]]=None):
            """
            :param client_subnets: ``CfnCluster.BrokerNodeGroupInfoProperty.ClientSubnets``.
            :param instance_type: ``CfnCluster.BrokerNodeGroupInfoProperty.InstanceType``.
            :param broker_az_distribution: ``CfnCluster.BrokerNodeGroupInfoProperty.BrokerAZDistribution``.
            :param security_groups: ``CfnCluster.BrokerNodeGroupInfoProperty.SecurityGroups``.
            :param storage_info: ``CfnCluster.BrokerNodeGroupInfoProperty.StorageInfo``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-msk-cluster-brokernodegroupinfo.html
            """
            self._values = {
                'client_subnets': client_subnets,
                'instance_type': instance_type,
            }
            if broker_az_distribution is not None: self._values["broker_az_distribution"] = broker_az_distribution
            if security_groups is not None: self._values["security_groups"] = security_groups
            if storage_info is not None: self._values["storage_info"] = storage_info

        @property
        def client_subnets(self) -> typing.List[str]:
            """``CfnCluster.BrokerNodeGroupInfoProperty.ClientSubnets``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-msk-cluster-brokernodegroupinfo.html#cfn-msk-cluster-brokernodegroupinfo-clientsubnets
            """
            return self._values.get('client_subnets')

        @property
        def instance_type(self) -> str:
            """``CfnCluster.BrokerNodeGroupInfoProperty.InstanceType``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-msk-cluster-brokernodegroupinfo.html#cfn-msk-cluster-brokernodegroupinfo-instancetype
            """
            return self._values.get('instance_type')

        @property
        def broker_az_distribution(self) -> typing.Optional[str]:
            """``CfnCluster.BrokerNodeGroupInfoProperty.BrokerAZDistribution``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-msk-cluster-brokernodegroupinfo.html#cfn-msk-cluster-brokernodegroupinfo-brokerazdistribution
            """
            return self._values.get('broker_az_distribution')

        @property
        def security_groups(self) -> typing.Optional[typing.List[str]]:
            """``CfnCluster.BrokerNodeGroupInfoProperty.SecurityGroups``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-msk-cluster-brokernodegroupinfo.html#cfn-msk-cluster-brokernodegroupinfo-securitygroups
            """
            return self._values.get('security_groups')

        @property
        def storage_info(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnCluster.StorageInfoProperty"]]]:
            """``CfnCluster.BrokerNodeGroupInfoProperty.StorageInfo``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-msk-cluster-brokernodegroupinfo.html#cfn-msk-cluster-brokernodegroupinfo-storageinfo
            """
            return self._values.get('storage_info')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'BrokerNodeGroupInfoProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-msk.CfnCluster.ClientAuthenticationProperty", jsii_struct_bases=[], name_mapping={'tls': 'tls'})
    class ClientAuthenticationProperty():
        def __init__(self, *, tls: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnCluster.TlsProperty"]]]=None):
            """
            :param tls: ``CfnCluster.ClientAuthenticationProperty.Tls``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-msk-cluster-clientauthentication.html
            """
            self._values = {
            }
            if tls is not None: self._values["tls"] = tls

        @property
        def tls(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnCluster.TlsProperty"]]]:
            """``CfnCluster.ClientAuthenticationProperty.Tls``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-msk-cluster-clientauthentication.html#cfn-msk-cluster-clientauthentication-tls
            """
            return self._values.get('tls')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'ClientAuthenticationProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-msk.CfnCluster.ConfigurationInfoProperty", jsii_struct_bases=[], name_mapping={'arn': 'arn', 'revision': 'revision'})
    class ConfigurationInfoProperty():
        def __init__(self, *, arn: str, revision: jsii.Number):
            """
            :param arn: ``CfnCluster.ConfigurationInfoProperty.Arn``.
            :param revision: ``CfnCluster.ConfigurationInfoProperty.Revision``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-msk-cluster-configurationinfo.html
            """
            self._values = {
                'arn': arn,
                'revision': revision,
            }

        @property
        def arn(self) -> str:
            """``CfnCluster.ConfigurationInfoProperty.Arn``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-msk-cluster-configurationinfo.html#cfn-msk-cluster-configurationinfo-arn
            """
            return self._values.get('arn')

        @property
        def revision(self) -> jsii.Number:
            """``CfnCluster.ConfigurationInfoProperty.Revision``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-msk-cluster-configurationinfo.html#cfn-msk-cluster-configurationinfo-revision
            """
            return self._values.get('revision')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'ConfigurationInfoProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-msk.CfnCluster.EBSStorageInfoProperty", jsii_struct_bases=[], name_mapping={'volume_size': 'volumeSize'})
    class EBSStorageInfoProperty():
        def __init__(self, *, volume_size: typing.Optional[jsii.Number]=None):
            """
            :param volume_size: ``CfnCluster.EBSStorageInfoProperty.VolumeSize``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-msk-cluster-ebsstorageinfo.html
            """
            self._values = {
            }
            if volume_size is not None: self._values["volume_size"] = volume_size

        @property
        def volume_size(self) -> typing.Optional[jsii.Number]:
            """``CfnCluster.EBSStorageInfoProperty.VolumeSize``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-msk-cluster-ebsstorageinfo.html#cfn-msk-cluster-ebsstorageinfo-volumesize
            """
            return self._values.get('volume_size')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'EBSStorageInfoProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-msk.CfnCluster.EncryptionAtRestProperty", jsii_struct_bases=[], name_mapping={'data_volume_kms_key_id': 'dataVolumeKmsKeyId'})
    class EncryptionAtRestProperty():
        def __init__(self, *, data_volume_kms_key_id: str):
            """
            :param data_volume_kms_key_id: ``CfnCluster.EncryptionAtRestProperty.DataVolumeKMSKeyId``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-msk-cluster-encryptionatrest.html
            """
            self._values = {
                'data_volume_kms_key_id': data_volume_kms_key_id,
            }

        @property
        def data_volume_kms_key_id(self) -> str:
            """``CfnCluster.EncryptionAtRestProperty.DataVolumeKMSKeyId``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-msk-cluster-encryptionatrest.html#cfn-msk-cluster-encryptionatrest-datavolumekmskeyid
            """
            return self._values.get('data_volume_kms_key_id')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'EncryptionAtRestProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-msk.CfnCluster.EncryptionInTransitProperty", jsii_struct_bases=[], name_mapping={'client_broker': 'clientBroker', 'in_cluster': 'inCluster'})
    class EncryptionInTransitProperty():
        def __init__(self, *, client_broker: typing.Optional[str]=None, in_cluster: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None):
            """
            :param client_broker: ``CfnCluster.EncryptionInTransitProperty.ClientBroker``.
            :param in_cluster: ``CfnCluster.EncryptionInTransitProperty.InCluster``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-msk-cluster-encryptionintransit.html
            """
            self._values = {
            }
            if client_broker is not None: self._values["client_broker"] = client_broker
            if in_cluster is not None: self._values["in_cluster"] = in_cluster

        @property
        def client_broker(self) -> typing.Optional[str]:
            """``CfnCluster.EncryptionInTransitProperty.ClientBroker``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-msk-cluster-encryptionintransit.html#cfn-msk-cluster-encryptionintransit-clientbroker
            """
            return self._values.get('client_broker')

        @property
        def in_cluster(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
            """``CfnCluster.EncryptionInTransitProperty.InCluster``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-msk-cluster-encryptionintransit.html#cfn-msk-cluster-encryptionintransit-incluster
            """
            return self._values.get('in_cluster')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'EncryptionInTransitProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-msk.CfnCluster.EncryptionInfoProperty", jsii_struct_bases=[], name_mapping={'encryption_at_rest': 'encryptionAtRest', 'encryption_in_transit': 'encryptionInTransit'})
    class EncryptionInfoProperty():
        def __init__(self, *, encryption_at_rest: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnCluster.EncryptionAtRestProperty"]]]=None, encryption_in_transit: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnCluster.EncryptionInTransitProperty"]]]=None):
            """
            :param encryption_at_rest: ``CfnCluster.EncryptionInfoProperty.EncryptionAtRest``.
            :param encryption_in_transit: ``CfnCluster.EncryptionInfoProperty.EncryptionInTransit``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-msk-cluster-encryptioninfo.html
            """
            self._values = {
            }
            if encryption_at_rest is not None: self._values["encryption_at_rest"] = encryption_at_rest
            if encryption_in_transit is not None: self._values["encryption_in_transit"] = encryption_in_transit

        @property
        def encryption_at_rest(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnCluster.EncryptionAtRestProperty"]]]:
            """``CfnCluster.EncryptionInfoProperty.EncryptionAtRest``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-msk-cluster-encryptioninfo.html#cfn-msk-cluster-encryptioninfo-encryptionatrest
            """
            return self._values.get('encryption_at_rest')

        @property
        def encryption_in_transit(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnCluster.EncryptionInTransitProperty"]]]:
            """``CfnCluster.EncryptionInfoProperty.EncryptionInTransit``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-msk-cluster-encryptioninfo.html#cfn-msk-cluster-encryptioninfo-encryptionintransit
            """
            return self._values.get('encryption_in_transit')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'EncryptionInfoProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-msk.CfnCluster.StorageInfoProperty", jsii_struct_bases=[], name_mapping={'ebs_storage_info': 'ebsStorageInfo'})
    class StorageInfoProperty():
        def __init__(self, *, ebs_storage_info: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnCluster.EBSStorageInfoProperty"]]]=None):
            """
            :param ebs_storage_info: ``CfnCluster.StorageInfoProperty.EBSStorageInfo``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-msk-cluster-storageinfo.html
            """
            self._values = {
            }
            if ebs_storage_info is not None: self._values["ebs_storage_info"] = ebs_storage_info

        @property
        def ebs_storage_info(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnCluster.EBSStorageInfoProperty"]]]:
            """``CfnCluster.StorageInfoProperty.EBSStorageInfo``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-msk-cluster-storageinfo.html#cfn-msk-cluster-storageinfo-ebsstorageinfo
            """
            return self._values.get('ebs_storage_info')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'StorageInfoProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-msk.CfnCluster.TlsProperty", jsii_struct_bases=[], name_mapping={'certificate_authority_arn_list': 'certificateAuthorityArnList'})
    class TlsProperty():
        def __init__(self, *, certificate_authority_arn_list: typing.Optional[typing.List[str]]=None):
            """
            :param certificate_authority_arn_list: ``CfnCluster.TlsProperty.CertificateAuthorityArnList``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-msk-cluster-tls.html
            """
            self._values = {
            }
            if certificate_authority_arn_list is not None: self._values["certificate_authority_arn_list"] = certificate_authority_arn_list

        @property
        def certificate_authority_arn_list(self) -> typing.Optional[typing.List[str]]:
            """``CfnCluster.TlsProperty.CertificateAuthorityArnList``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-msk-cluster-tls.html#cfn-msk-cluster-tls-certificateauthorityarnlist
            """
            return self._values.get('certificate_authority_arn_list')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'TlsProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



@jsii.data_type(jsii_type="@aws-cdk/aws-msk.CfnClusterProps", jsii_struct_bases=[], name_mapping={'broker_node_group_info': 'brokerNodeGroupInfo', 'cluster_name': 'clusterName', 'kafka_version': 'kafkaVersion', 'number_of_broker_nodes': 'numberOfBrokerNodes', 'client_authentication': 'clientAuthentication', 'configuration_info': 'configurationInfo', 'encryption_info': 'encryptionInfo', 'enhanced_monitoring': 'enhancedMonitoring', 'tags': 'tags'})
class CfnClusterProps():
    def __init__(self, *, broker_node_group_info: typing.Union["CfnCluster.BrokerNodeGroupInfoProperty", aws_cdk.core.IResolvable], cluster_name: str, kafka_version: str, number_of_broker_nodes: jsii.Number, client_authentication: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnCluster.ClientAuthenticationProperty"]]]=None, configuration_info: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnCluster.ConfigurationInfoProperty"]]]=None, encryption_info: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnCluster.EncryptionInfoProperty"]]]=None, enhanced_monitoring: typing.Optional[str]=None, tags: typing.Any=None):
        """Properties for defining a ``AWS::MSK::Cluster``.

        :param broker_node_group_info: ``AWS::MSK::Cluster.BrokerNodeGroupInfo``.
        :param cluster_name: ``AWS::MSK::Cluster.ClusterName``.
        :param kafka_version: ``AWS::MSK::Cluster.KafkaVersion``.
        :param number_of_broker_nodes: ``AWS::MSK::Cluster.NumberOfBrokerNodes``.
        :param client_authentication: ``AWS::MSK::Cluster.ClientAuthentication``.
        :param configuration_info: ``AWS::MSK::Cluster.ConfigurationInfo``.
        :param encryption_info: ``AWS::MSK::Cluster.EncryptionInfo``.
        :param enhanced_monitoring: ``AWS::MSK::Cluster.EnhancedMonitoring``.
        :param tags: ``AWS::MSK::Cluster.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-msk-cluster.html
        """
        self._values = {
            'broker_node_group_info': broker_node_group_info,
            'cluster_name': cluster_name,
            'kafka_version': kafka_version,
            'number_of_broker_nodes': number_of_broker_nodes,
        }
        if client_authentication is not None: self._values["client_authentication"] = client_authentication
        if configuration_info is not None: self._values["configuration_info"] = configuration_info
        if encryption_info is not None: self._values["encryption_info"] = encryption_info
        if enhanced_monitoring is not None: self._values["enhanced_monitoring"] = enhanced_monitoring
        if tags is not None: self._values["tags"] = tags

    @property
    def broker_node_group_info(self) -> typing.Union["CfnCluster.BrokerNodeGroupInfoProperty", aws_cdk.core.IResolvable]:
        """``AWS::MSK::Cluster.BrokerNodeGroupInfo``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-msk-cluster.html#cfn-msk-cluster-brokernodegroupinfo
        """
        return self._values.get('broker_node_group_info')

    @property
    def cluster_name(self) -> str:
        """``AWS::MSK::Cluster.ClusterName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-msk-cluster.html#cfn-msk-cluster-clustername
        """
        return self._values.get('cluster_name')

    @property
    def kafka_version(self) -> str:
        """``AWS::MSK::Cluster.KafkaVersion``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-msk-cluster.html#cfn-msk-cluster-kafkaversion
        """
        return self._values.get('kafka_version')

    @property
    def number_of_broker_nodes(self) -> jsii.Number:
        """``AWS::MSK::Cluster.NumberOfBrokerNodes``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-msk-cluster.html#cfn-msk-cluster-numberofbrokernodes
        """
        return self._values.get('number_of_broker_nodes')

    @property
    def client_authentication(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnCluster.ClientAuthenticationProperty"]]]:
        """``AWS::MSK::Cluster.ClientAuthentication``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-msk-cluster.html#cfn-msk-cluster-clientauthentication
        """
        return self._values.get('client_authentication')

    @property
    def configuration_info(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnCluster.ConfigurationInfoProperty"]]]:
        """``AWS::MSK::Cluster.ConfigurationInfo``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-msk-cluster.html#cfn-msk-cluster-configurationinfo
        """
        return self._values.get('configuration_info')

    @property
    def encryption_info(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnCluster.EncryptionInfoProperty"]]]:
        """``AWS::MSK::Cluster.EncryptionInfo``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-msk-cluster.html#cfn-msk-cluster-encryptioninfo
        """
        return self._values.get('encryption_info')

    @property
    def enhanced_monitoring(self) -> typing.Optional[str]:
        """``AWS::MSK::Cluster.EnhancedMonitoring``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-msk-cluster.html#cfn-msk-cluster-enhancedmonitoring
        """
        return self._values.get('enhanced_monitoring')

    @property
    def tags(self) -> typing.Any:
        """``AWS::MSK::Cluster.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-msk-cluster.html#cfn-msk-cluster-tags
        """
        return self._values.get('tags')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnClusterProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


__all__ = ["CfnCluster", "CfnClusterProps", "__jsii_assembly__"]

publication.publish()
