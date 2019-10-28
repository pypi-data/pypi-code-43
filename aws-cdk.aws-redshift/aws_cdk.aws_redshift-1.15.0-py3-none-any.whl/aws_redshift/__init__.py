import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.core
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-redshift", "1.15.0", __name__, "aws-redshift@1.15.0.jsii.tgz")
class CfnCluster(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-redshift.CfnCluster"):
    """A CloudFormation ``AWS::Redshift::Cluster``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html
    cloudformationResource:
    :cloudformationResource:: AWS::Redshift::Cluster
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, cluster_type: str, db_name: str, master_username: str, master_user_password: str, node_type: str, allow_version_upgrade: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, automated_snapshot_retention_period: typing.Optional[jsii.Number]=None, availability_zone: typing.Optional[str]=None, cluster_identifier: typing.Optional[str]=None, cluster_parameter_group_name: typing.Optional[str]=None, cluster_security_groups: typing.Optional[typing.List[str]]=None, cluster_subnet_group_name: typing.Optional[str]=None, cluster_version: typing.Optional[str]=None, elastic_ip: typing.Optional[str]=None, encrypted: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, hsm_client_certificate_identifier: typing.Optional[str]=None, hsm_configuration_identifier: typing.Optional[str]=None, iam_roles: typing.Optional[typing.List[str]]=None, kms_key_id: typing.Optional[str]=None, logging_properties: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["LoggingPropertiesProperty"]]]=None, number_of_nodes: typing.Optional[jsii.Number]=None, owner_account: typing.Optional[str]=None, port: typing.Optional[jsii.Number]=None, preferred_maintenance_window: typing.Optional[str]=None, publicly_accessible: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, snapshot_cluster_identifier: typing.Optional[str]=None, snapshot_identifier: typing.Optional[str]=None, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None, vpc_security_group_ids: typing.Optional[typing.List[str]]=None) -> None:
        """Create a new ``AWS::Redshift::Cluster``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param cluster_type: ``AWS::Redshift::Cluster.ClusterType``.
        :param db_name: ``AWS::Redshift::Cluster.DBName``.
        :param master_username: ``AWS::Redshift::Cluster.MasterUsername``.
        :param master_user_password: ``AWS::Redshift::Cluster.MasterUserPassword``.
        :param node_type: ``AWS::Redshift::Cluster.NodeType``.
        :param allow_version_upgrade: ``AWS::Redshift::Cluster.AllowVersionUpgrade``.
        :param automated_snapshot_retention_period: ``AWS::Redshift::Cluster.AutomatedSnapshotRetentionPeriod``.
        :param availability_zone: ``AWS::Redshift::Cluster.AvailabilityZone``.
        :param cluster_identifier: ``AWS::Redshift::Cluster.ClusterIdentifier``.
        :param cluster_parameter_group_name: ``AWS::Redshift::Cluster.ClusterParameterGroupName``.
        :param cluster_security_groups: ``AWS::Redshift::Cluster.ClusterSecurityGroups``.
        :param cluster_subnet_group_name: ``AWS::Redshift::Cluster.ClusterSubnetGroupName``.
        :param cluster_version: ``AWS::Redshift::Cluster.ClusterVersion``.
        :param elastic_ip: ``AWS::Redshift::Cluster.ElasticIp``.
        :param encrypted: ``AWS::Redshift::Cluster.Encrypted``.
        :param hsm_client_certificate_identifier: ``AWS::Redshift::Cluster.HsmClientCertificateIdentifier``.
        :param hsm_configuration_identifier: ``AWS::Redshift::Cluster.HsmConfigurationIdentifier``.
        :param iam_roles: ``AWS::Redshift::Cluster.IamRoles``.
        :param kms_key_id: ``AWS::Redshift::Cluster.KmsKeyId``.
        :param logging_properties: ``AWS::Redshift::Cluster.LoggingProperties``.
        :param number_of_nodes: ``AWS::Redshift::Cluster.NumberOfNodes``.
        :param owner_account: ``AWS::Redshift::Cluster.OwnerAccount``.
        :param port: ``AWS::Redshift::Cluster.Port``.
        :param preferred_maintenance_window: ``AWS::Redshift::Cluster.PreferredMaintenanceWindow``.
        :param publicly_accessible: ``AWS::Redshift::Cluster.PubliclyAccessible``.
        :param snapshot_cluster_identifier: ``AWS::Redshift::Cluster.SnapshotClusterIdentifier``.
        :param snapshot_identifier: ``AWS::Redshift::Cluster.SnapshotIdentifier``.
        :param tags: ``AWS::Redshift::Cluster.Tags``.
        :param vpc_security_group_ids: ``AWS::Redshift::Cluster.VpcSecurityGroupIds``.
        """
        props = CfnClusterProps(cluster_type=cluster_type, db_name=db_name, master_username=master_username, master_user_password=master_user_password, node_type=node_type, allow_version_upgrade=allow_version_upgrade, automated_snapshot_retention_period=automated_snapshot_retention_period, availability_zone=availability_zone, cluster_identifier=cluster_identifier, cluster_parameter_group_name=cluster_parameter_group_name, cluster_security_groups=cluster_security_groups, cluster_subnet_group_name=cluster_subnet_group_name, cluster_version=cluster_version, elastic_ip=elastic_ip, encrypted=encrypted, hsm_client_certificate_identifier=hsm_client_certificate_identifier, hsm_configuration_identifier=hsm_configuration_identifier, iam_roles=iam_roles, kms_key_id=kms_key_id, logging_properties=logging_properties, number_of_nodes=number_of_nodes, owner_account=owner_account, port=port, preferred_maintenance_window=preferred_maintenance_window, publicly_accessible=publicly_accessible, snapshot_cluster_identifier=snapshot_cluster_identifier, snapshot_identifier=snapshot_identifier, tags=tags, vpc_security_group_ids=vpc_security_group_ids)

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
    @jsii.member(jsii_name="attrEndpointAddress")
    def attr_endpoint_address(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: Endpoint.Address
        """
        return jsii.get(self, "attrEndpointAddress")

    @property
    @jsii.member(jsii_name="attrEndpointPort")
    def attr_endpoint_port(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: Endpoint.Port
        """
        return jsii.get(self, "attrEndpointPort")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        """``AWS::Redshift::Cluster.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-tags
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="clusterType")
    def cluster_type(self) -> str:
        """``AWS::Redshift::Cluster.ClusterType``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-clustertype
        """
        return jsii.get(self, "clusterType")

    @cluster_type.setter
    def cluster_type(self, value: str):
        return jsii.set(self, "clusterType", value)

    @property
    @jsii.member(jsii_name="dbName")
    def db_name(self) -> str:
        """``AWS::Redshift::Cluster.DBName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-dbname
        """
        return jsii.get(self, "dbName")

    @db_name.setter
    def db_name(self, value: str):
        return jsii.set(self, "dbName", value)

    @property
    @jsii.member(jsii_name="masterUsername")
    def master_username(self) -> str:
        """``AWS::Redshift::Cluster.MasterUsername``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-masterusername
        """
        return jsii.get(self, "masterUsername")

    @master_username.setter
    def master_username(self, value: str):
        return jsii.set(self, "masterUsername", value)

    @property
    @jsii.member(jsii_name="masterUserPassword")
    def master_user_password(self) -> str:
        """``AWS::Redshift::Cluster.MasterUserPassword``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-masteruserpassword
        """
        return jsii.get(self, "masterUserPassword")

    @master_user_password.setter
    def master_user_password(self, value: str):
        return jsii.set(self, "masterUserPassword", value)

    @property
    @jsii.member(jsii_name="nodeType")
    def node_type(self) -> str:
        """``AWS::Redshift::Cluster.NodeType``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-nodetype
        """
        return jsii.get(self, "nodeType")

    @node_type.setter
    def node_type(self, value: str):
        return jsii.set(self, "nodeType", value)

    @property
    @jsii.member(jsii_name="allowVersionUpgrade")
    def allow_version_upgrade(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::Redshift::Cluster.AllowVersionUpgrade``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-allowversionupgrade
        """
        return jsii.get(self, "allowVersionUpgrade")

    @allow_version_upgrade.setter
    def allow_version_upgrade(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "allowVersionUpgrade", value)

    @property
    @jsii.member(jsii_name="automatedSnapshotRetentionPeriod")
    def automated_snapshot_retention_period(self) -> typing.Optional[jsii.Number]:
        """``AWS::Redshift::Cluster.AutomatedSnapshotRetentionPeriod``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-automatedsnapshotretentionperiod
        """
        return jsii.get(self, "automatedSnapshotRetentionPeriod")

    @automated_snapshot_retention_period.setter
    def automated_snapshot_retention_period(self, value: typing.Optional[jsii.Number]):
        return jsii.set(self, "automatedSnapshotRetentionPeriod", value)

    @property
    @jsii.member(jsii_name="availabilityZone")
    def availability_zone(self) -> typing.Optional[str]:
        """``AWS::Redshift::Cluster.AvailabilityZone``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-availabilityzone
        """
        return jsii.get(self, "availabilityZone")

    @availability_zone.setter
    def availability_zone(self, value: typing.Optional[str]):
        return jsii.set(self, "availabilityZone", value)

    @property
    @jsii.member(jsii_name="clusterIdentifier")
    def cluster_identifier(self) -> typing.Optional[str]:
        """``AWS::Redshift::Cluster.ClusterIdentifier``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-clusteridentifier
        """
        return jsii.get(self, "clusterIdentifier")

    @cluster_identifier.setter
    def cluster_identifier(self, value: typing.Optional[str]):
        return jsii.set(self, "clusterIdentifier", value)

    @property
    @jsii.member(jsii_name="clusterParameterGroupName")
    def cluster_parameter_group_name(self) -> typing.Optional[str]:
        """``AWS::Redshift::Cluster.ClusterParameterGroupName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-clusterparametergroupname
        """
        return jsii.get(self, "clusterParameterGroupName")

    @cluster_parameter_group_name.setter
    def cluster_parameter_group_name(self, value: typing.Optional[str]):
        return jsii.set(self, "clusterParameterGroupName", value)

    @property
    @jsii.member(jsii_name="clusterSecurityGroups")
    def cluster_security_groups(self) -> typing.Optional[typing.List[str]]:
        """``AWS::Redshift::Cluster.ClusterSecurityGroups``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-clustersecuritygroups
        """
        return jsii.get(self, "clusterSecurityGroups")

    @cluster_security_groups.setter
    def cluster_security_groups(self, value: typing.Optional[typing.List[str]]):
        return jsii.set(self, "clusterSecurityGroups", value)

    @property
    @jsii.member(jsii_name="clusterSubnetGroupName")
    def cluster_subnet_group_name(self) -> typing.Optional[str]:
        """``AWS::Redshift::Cluster.ClusterSubnetGroupName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-clustersubnetgroupname
        """
        return jsii.get(self, "clusterSubnetGroupName")

    @cluster_subnet_group_name.setter
    def cluster_subnet_group_name(self, value: typing.Optional[str]):
        return jsii.set(self, "clusterSubnetGroupName", value)

    @property
    @jsii.member(jsii_name="clusterVersion")
    def cluster_version(self) -> typing.Optional[str]:
        """``AWS::Redshift::Cluster.ClusterVersion``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-clusterversion
        """
        return jsii.get(self, "clusterVersion")

    @cluster_version.setter
    def cluster_version(self, value: typing.Optional[str]):
        return jsii.set(self, "clusterVersion", value)

    @property
    @jsii.member(jsii_name="elasticIp")
    def elastic_ip(self) -> typing.Optional[str]:
        """``AWS::Redshift::Cluster.ElasticIp``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-elasticip
        """
        return jsii.get(self, "elasticIp")

    @elastic_ip.setter
    def elastic_ip(self, value: typing.Optional[str]):
        return jsii.set(self, "elasticIp", value)

    @property
    @jsii.member(jsii_name="encrypted")
    def encrypted(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::Redshift::Cluster.Encrypted``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-encrypted
        """
        return jsii.get(self, "encrypted")

    @encrypted.setter
    def encrypted(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "encrypted", value)

    @property
    @jsii.member(jsii_name="hsmClientCertificateIdentifier")
    def hsm_client_certificate_identifier(self) -> typing.Optional[str]:
        """``AWS::Redshift::Cluster.HsmClientCertificateIdentifier``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-hsmclientcertidentifier
        """
        return jsii.get(self, "hsmClientCertificateIdentifier")

    @hsm_client_certificate_identifier.setter
    def hsm_client_certificate_identifier(self, value: typing.Optional[str]):
        return jsii.set(self, "hsmClientCertificateIdentifier", value)

    @property
    @jsii.member(jsii_name="hsmConfigurationIdentifier")
    def hsm_configuration_identifier(self) -> typing.Optional[str]:
        """``AWS::Redshift::Cluster.HsmConfigurationIdentifier``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-HsmConfigurationIdentifier
        """
        return jsii.get(self, "hsmConfigurationIdentifier")

    @hsm_configuration_identifier.setter
    def hsm_configuration_identifier(self, value: typing.Optional[str]):
        return jsii.set(self, "hsmConfigurationIdentifier", value)

    @property
    @jsii.member(jsii_name="iamRoles")
    def iam_roles(self) -> typing.Optional[typing.List[str]]:
        """``AWS::Redshift::Cluster.IamRoles``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-iamroles
        """
        return jsii.get(self, "iamRoles")

    @iam_roles.setter
    def iam_roles(self, value: typing.Optional[typing.List[str]]):
        return jsii.set(self, "iamRoles", value)

    @property
    @jsii.member(jsii_name="kmsKeyId")
    def kms_key_id(self) -> typing.Optional[str]:
        """``AWS::Redshift::Cluster.KmsKeyId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-kmskeyid
        """
        return jsii.get(self, "kmsKeyId")

    @kms_key_id.setter
    def kms_key_id(self, value: typing.Optional[str]):
        return jsii.set(self, "kmsKeyId", value)

    @property
    @jsii.member(jsii_name="loggingProperties")
    def logging_properties(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["LoggingPropertiesProperty"]]]:
        """``AWS::Redshift::Cluster.LoggingProperties``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-loggingproperties
        """
        return jsii.get(self, "loggingProperties")

    @logging_properties.setter
    def logging_properties(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["LoggingPropertiesProperty"]]]):
        return jsii.set(self, "loggingProperties", value)

    @property
    @jsii.member(jsii_name="numberOfNodes")
    def number_of_nodes(self) -> typing.Optional[jsii.Number]:
        """``AWS::Redshift::Cluster.NumberOfNodes``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-nodetype
        """
        return jsii.get(self, "numberOfNodes")

    @number_of_nodes.setter
    def number_of_nodes(self, value: typing.Optional[jsii.Number]):
        return jsii.set(self, "numberOfNodes", value)

    @property
    @jsii.member(jsii_name="ownerAccount")
    def owner_account(self) -> typing.Optional[str]:
        """``AWS::Redshift::Cluster.OwnerAccount``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-owneraccount
        """
        return jsii.get(self, "ownerAccount")

    @owner_account.setter
    def owner_account(self, value: typing.Optional[str]):
        return jsii.set(self, "ownerAccount", value)

    @property
    @jsii.member(jsii_name="port")
    def port(self) -> typing.Optional[jsii.Number]:
        """``AWS::Redshift::Cluster.Port``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-port
        """
        return jsii.get(self, "port")

    @port.setter
    def port(self, value: typing.Optional[jsii.Number]):
        return jsii.set(self, "port", value)

    @property
    @jsii.member(jsii_name="preferredMaintenanceWindow")
    def preferred_maintenance_window(self) -> typing.Optional[str]:
        """``AWS::Redshift::Cluster.PreferredMaintenanceWindow``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-preferredmaintenancewindow
        """
        return jsii.get(self, "preferredMaintenanceWindow")

    @preferred_maintenance_window.setter
    def preferred_maintenance_window(self, value: typing.Optional[str]):
        return jsii.set(self, "preferredMaintenanceWindow", value)

    @property
    @jsii.member(jsii_name="publiclyAccessible")
    def publicly_accessible(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::Redshift::Cluster.PubliclyAccessible``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-publiclyaccessible
        """
        return jsii.get(self, "publiclyAccessible")

    @publicly_accessible.setter
    def publicly_accessible(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "publiclyAccessible", value)

    @property
    @jsii.member(jsii_name="snapshotClusterIdentifier")
    def snapshot_cluster_identifier(self) -> typing.Optional[str]:
        """``AWS::Redshift::Cluster.SnapshotClusterIdentifier``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-snapshotclusteridentifier
        """
        return jsii.get(self, "snapshotClusterIdentifier")

    @snapshot_cluster_identifier.setter
    def snapshot_cluster_identifier(self, value: typing.Optional[str]):
        return jsii.set(self, "snapshotClusterIdentifier", value)

    @property
    @jsii.member(jsii_name="snapshotIdentifier")
    def snapshot_identifier(self) -> typing.Optional[str]:
        """``AWS::Redshift::Cluster.SnapshotIdentifier``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-snapshotidentifier
        """
        return jsii.get(self, "snapshotIdentifier")

    @snapshot_identifier.setter
    def snapshot_identifier(self, value: typing.Optional[str]):
        return jsii.set(self, "snapshotIdentifier", value)

    @property
    @jsii.member(jsii_name="vpcSecurityGroupIds")
    def vpc_security_group_ids(self) -> typing.Optional[typing.List[str]]:
        """``AWS::Redshift::Cluster.VpcSecurityGroupIds``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-vpcsecuritygroupids
        """
        return jsii.get(self, "vpcSecurityGroupIds")

    @vpc_security_group_ids.setter
    def vpc_security_group_ids(self, value: typing.Optional[typing.List[str]]):
        return jsii.set(self, "vpcSecurityGroupIds", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-redshift.CfnCluster.LoggingPropertiesProperty", jsii_struct_bases=[], name_mapping={'bucket_name': 'bucketName', 's3_key_prefix': 's3KeyPrefix'})
    class LoggingPropertiesProperty():
        def __init__(self, *, bucket_name: str, s3_key_prefix: typing.Optional[str]=None):
            """
            :param bucket_name: ``CfnCluster.LoggingPropertiesProperty.BucketName``.
            :param s3_key_prefix: ``CfnCluster.LoggingPropertiesProperty.S3KeyPrefix``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-redshift-cluster-loggingproperties.html
            """
            self._values = {
                'bucket_name': bucket_name,
            }
            if s3_key_prefix is not None: self._values["s3_key_prefix"] = s3_key_prefix

        @property
        def bucket_name(self) -> str:
            """``CfnCluster.LoggingPropertiesProperty.BucketName``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-redshift-cluster-loggingproperties.html#cfn-redshift-cluster-loggingproperties-bucketname
            """
            return self._values.get('bucket_name')

        @property
        def s3_key_prefix(self) -> typing.Optional[str]:
            """``CfnCluster.LoggingPropertiesProperty.S3KeyPrefix``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-redshift-cluster-loggingproperties.html#cfn-redshift-cluster-loggingproperties-s3keyprefix
            """
            return self._values.get('s3_key_prefix')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'LoggingPropertiesProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



class CfnClusterParameterGroup(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-redshift.CfnClusterParameterGroup"):
    """A CloudFormation ``AWS::Redshift::ClusterParameterGroup``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clusterparametergroup.html
    cloudformationResource:
    :cloudformationResource:: AWS::Redshift::ClusterParameterGroup
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, description: str, parameter_group_family: str, parameters: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union["ParameterProperty", aws_cdk.core.IResolvable]]]]]=None, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None) -> None:
        """Create a new ``AWS::Redshift::ClusterParameterGroup``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param description: ``AWS::Redshift::ClusterParameterGroup.Description``.
        :param parameter_group_family: ``AWS::Redshift::ClusterParameterGroup.ParameterGroupFamily``.
        :param parameters: ``AWS::Redshift::ClusterParameterGroup.Parameters``.
        :param tags: ``AWS::Redshift::ClusterParameterGroup.Tags``.
        """
        props = CfnClusterParameterGroupProps(description=description, parameter_group_family=parameter_group_family, parameters=parameters, tags=tags)

        jsii.create(CfnClusterParameterGroup, self, [scope, id, props])

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
        """``AWS::Redshift::ClusterParameterGroup.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clusterparametergroup.html#cfn-redshift-clusterparametergroup-tags
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="description")
    def description(self) -> str:
        """``AWS::Redshift::ClusterParameterGroup.Description``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clusterparametergroup.html#cfn-redshift-clusterparametergroup-description
        """
        return jsii.get(self, "description")

    @description.setter
    def description(self, value: str):
        return jsii.set(self, "description", value)

    @property
    @jsii.member(jsii_name="parameterGroupFamily")
    def parameter_group_family(self) -> str:
        """``AWS::Redshift::ClusterParameterGroup.ParameterGroupFamily``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clusterparametergroup.html#cfn-redshift-clusterparametergroup-parametergroupfamily
        """
        return jsii.get(self, "parameterGroupFamily")

    @parameter_group_family.setter
    def parameter_group_family(self, value: str):
        return jsii.set(self, "parameterGroupFamily", value)

    @property
    @jsii.member(jsii_name="parameters")
    def parameters(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union["ParameterProperty", aws_cdk.core.IResolvable]]]]]:
        """``AWS::Redshift::ClusterParameterGroup.Parameters``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clusterparametergroup.html#cfn-redshift-clusterparametergroup-parameters
        """
        return jsii.get(self, "parameters")

    @parameters.setter
    def parameters(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union["ParameterProperty", aws_cdk.core.IResolvable]]]]]):
        return jsii.set(self, "parameters", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-redshift.CfnClusterParameterGroup.ParameterProperty", jsii_struct_bases=[], name_mapping={'parameter_name': 'parameterName', 'parameter_value': 'parameterValue'})
    class ParameterProperty():
        def __init__(self, *, parameter_name: str, parameter_value: str):
            """
            :param parameter_name: ``CfnClusterParameterGroup.ParameterProperty.ParameterName``.
            :param parameter_value: ``CfnClusterParameterGroup.ParameterProperty.ParameterValue``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-property-redshift-clusterparametergroup-parameter.html
            """
            self._values = {
                'parameter_name': parameter_name,
                'parameter_value': parameter_value,
            }

        @property
        def parameter_name(self) -> str:
            """``CfnClusterParameterGroup.ParameterProperty.ParameterName``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-property-redshift-clusterparametergroup-parameter.html#cfn-redshift-clusterparametergroup-parameter-parametername
            """
            return self._values.get('parameter_name')

        @property
        def parameter_value(self) -> str:
            """``CfnClusterParameterGroup.ParameterProperty.ParameterValue``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-property-redshift-clusterparametergroup-parameter.html#cfn-redshift-clusterparametergroup-parameter-parametervalue
            """
            return self._values.get('parameter_value')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'ParameterProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



@jsii.data_type(jsii_type="@aws-cdk/aws-redshift.CfnClusterParameterGroupProps", jsii_struct_bases=[], name_mapping={'description': 'description', 'parameter_group_family': 'parameterGroupFamily', 'parameters': 'parameters', 'tags': 'tags'})
class CfnClusterParameterGroupProps():
    def __init__(self, *, description: str, parameter_group_family: str, parameters: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union["CfnClusterParameterGroup.ParameterProperty", aws_cdk.core.IResolvable]]]]]=None, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None):
        """Properties for defining a ``AWS::Redshift::ClusterParameterGroup``.

        :param description: ``AWS::Redshift::ClusterParameterGroup.Description``.
        :param parameter_group_family: ``AWS::Redshift::ClusterParameterGroup.ParameterGroupFamily``.
        :param parameters: ``AWS::Redshift::ClusterParameterGroup.Parameters``.
        :param tags: ``AWS::Redshift::ClusterParameterGroup.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clusterparametergroup.html
        """
        self._values = {
            'description': description,
            'parameter_group_family': parameter_group_family,
        }
        if parameters is not None: self._values["parameters"] = parameters
        if tags is not None: self._values["tags"] = tags

    @property
    def description(self) -> str:
        """``AWS::Redshift::ClusterParameterGroup.Description``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clusterparametergroup.html#cfn-redshift-clusterparametergroup-description
        """
        return self._values.get('description')

    @property
    def parameter_group_family(self) -> str:
        """``AWS::Redshift::ClusterParameterGroup.ParameterGroupFamily``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clusterparametergroup.html#cfn-redshift-clusterparametergroup-parametergroupfamily
        """
        return self._values.get('parameter_group_family')

    @property
    def parameters(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union["CfnClusterParameterGroup.ParameterProperty", aws_cdk.core.IResolvable]]]]]:
        """``AWS::Redshift::ClusterParameterGroup.Parameters``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clusterparametergroup.html#cfn-redshift-clusterparametergroup-parameters
        """
        return self._values.get('parameters')

    @property
    def tags(self) -> typing.Optional[typing.List[aws_cdk.core.CfnTag]]:
        """``AWS::Redshift::ClusterParameterGroup.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clusterparametergroup.html#cfn-redshift-clusterparametergroup-tags
        """
        return self._values.get('tags')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnClusterParameterGroupProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


@jsii.data_type(jsii_type="@aws-cdk/aws-redshift.CfnClusterProps", jsii_struct_bases=[], name_mapping={'cluster_type': 'clusterType', 'db_name': 'dbName', 'master_username': 'masterUsername', 'master_user_password': 'masterUserPassword', 'node_type': 'nodeType', 'allow_version_upgrade': 'allowVersionUpgrade', 'automated_snapshot_retention_period': 'automatedSnapshotRetentionPeriod', 'availability_zone': 'availabilityZone', 'cluster_identifier': 'clusterIdentifier', 'cluster_parameter_group_name': 'clusterParameterGroupName', 'cluster_security_groups': 'clusterSecurityGroups', 'cluster_subnet_group_name': 'clusterSubnetGroupName', 'cluster_version': 'clusterVersion', 'elastic_ip': 'elasticIp', 'encrypted': 'encrypted', 'hsm_client_certificate_identifier': 'hsmClientCertificateIdentifier', 'hsm_configuration_identifier': 'hsmConfigurationIdentifier', 'iam_roles': 'iamRoles', 'kms_key_id': 'kmsKeyId', 'logging_properties': 'loggingProperties', 'number_of_nodes': 'numberOfNodes', 'owner_account': 'ownerAccount', 'port': 'port', 'preferred_maintenance_window': 'preferredMaintenanceWindow', 'publicly_accessible': 'publiclyAccessible', 'snapshot_cluster_identifier': 'snapshotClusterIdentifier', 'snapshot_identifier': 'snapshotIdentifier', 'tags': 'tags', 'vpc_security_group_ids': 'vpcSecurityGroupIds'})
class CfnClusterProps():
    def __init__(self, *, cluster_type: str, db_name: str, master_username: str, master_user_password: str, node_type: str, allow_version_upgrade: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, automated_snapshot_retention_period: typing.Optional[jsii.Number]=None, availability_zone: typing.Optional[str]=None, cluster_identifier: typing.Optional[str]=None, cluster_parameter_group_name: typing.Optional[str]=None, cluster_security_groups: typing.Optional[typing.List[str]]=None, cluster_subnet_group_name: typing.Optional[str]=None, cluster_version: typing.Optional[str]=None, elastic_ip: typing.Optional[str]=None, encrypted: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, hsm_client_certificate_identifier: typing.Optional[str]=None, hsm_configuration_identifier: typing.Optional[str]=None, iam_roles: typing.Optional[typing.List[str]]=None, kms_key_id: typing.Optional[str]=None, logging_properties: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnCluster.LoggingPropertiesProperty"]]]=None, number_of_nodes: typing.Optional[jsii.Number]=None, owner_account: typing.Optional[str]=None, port: typing.Optional[jsii.Number]=None, preferred_maintenance_window: typing.Optional[str]=None, publicly_accessible: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, snapshot_cluster_identifier: typing.Optional[str]=None, snapshot_identifier: typing.Optional[str]=None, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None, vpc_security_group_ids: typing.Optional[typing.List[str]]=None):
        """Properties for defining a ``AWS::Redshift::Cluster``.

        :param cluster_type: ``AWS::Redshift::Cluster.ClusterType``.
        :param db_name: ``AWS::Redshift::Cluster.DBName``.
        :param master_username: ``AWS::Redshift::Cluster.MasterUsername``.
        :param master_user_password: ``AWS::Redshift::Cluster.MasterUserPassword``.
        :param node_type: ``AWS::Redshift::Cluster.NodeType``.
        :param allow_version_upgrade: ``AWS::Redshift::Cluster.AllowVersionUpgrade``.
        :param automated_snapshot_retention_period: ``AWS::Redshift::Cluster.AutomatedSnapshotRetentionPeriod``.
        :param availability_zone: ``AWS::Redshift::Cluster.AvailabilityZone``.
        :param cluster_identifier: ``AWS::Redshift::Cluster.ClusterIdentifier``.
        :param cluster_parameter_group_name: ``AWS::Redshift::Cluster.ClusterParameterGroupName``.
        :param cluster_security_groups: ``AWS::Redshift::Cluster.ClusterSecurityGroups``.
        :param cluster_subnet_group_name: ``AWS::Redshift::Cluster.ClusterSubnetGroupName``.
        :param cluster_version: ``AWS::Redshift::Cluster.ClusterVersion``.
        :param elastic_ip: ``AWS::Redshift::Cluster.ElasticIp``.
        :param encrypted: ``AWS::Redshift::Cluster.Encrypted``.
        :param hsm_client_certificate_identifier: ``AWS::Redshift::Cluster.HsmClientCertificateIdentifier``.
        :param hsm_configuration_identifier: ``AWS::Redshift::Cluster.HsmConfigurationIdentifier``.
        :param iam_roles: ``AWS::Redshift::Cluster.IamRoles``.
        :param kms_key_id: ``AWS::Redshift::Cluster.KmsKeyId``.
        :param logging_properties: ``AWS::Redshift::Cluster.LoggingProperties``.
        :param number_of_nodes: ``AWS::Redshift::Cluster.NumberOfNodes``.
        :param owner_account: ``AWS::Redshift::Cluster.OwnerAccount``.
        :param port: ``AWS::Redshift::Cluster.Port``.
        :param preferred_maintenance_window: ``AWS::Redshift::Cluster.PreferredMaintenanceWindow``.
        :param publicly_accessible: ``AWS::Redshift::Cluster.PubliclyAccessible``.
        :param snapshot_cluster_identifier: ``AWS::Redshift::Cluster.SnapshotClusterIdentifier``.
        :param snapshot_identifier: ``AWS::Redshift::Cluster.SnapshotIdentifier``.
        :param tags: ``AWS::Redshift::Cluster.Tags``.
        :param vpc_security_group_ids: ``AWS::Redshift::Cluster.VpcSecurityGroupIds``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html
        """
        self._values = {
            'cluster_type': cluster_type,
            'db_name': db_name,
            'master_username': master_username,
            'master_user_password': master_user_password,
            'node_type': node_type,
        }
        if allow_version_upgrade is not None: self._values["allow_version_upgrade"] = allow_version_upgrade
        if automated_snapshot_retention_period is not None: self._values["automated_snapshot_retention_period"] = automated_snapshot_retention_period
        if availability_zone is not None: self._values["availability_zone"] = availability_zone
        if cluster_identifier is not None: self._values["cluster_identifier"] = cluster_identifier
        if cluster_parameter_group_name is not None: self._values["cluster_parameter_group_name"] = cluster_parameter_group_name
        if cluster_security_groups is not None: self._values["cluster_security_groups"] = cluster_security_groups
        if cluster_subnet_group_name is not None: self._values["cluster_subnet_group_name"] = cluster_subnet_group_name
        if cluster_version is not None: self._values["cluster_version"] = cluster_version
        if elastic_ip is not None: self._values["elastic_ip"] = elastic_ip
        if encrypted is not None: self._values["encrypted"] = encrypted
        if hsm_client_certificate_identifier is not None: self._values["hsm_client_certificate_identifier"] = hsm_client_certificate_identifier
        if hsm_configuration_identifier is not None: self._values["hsm_configuration_identifier"] = hsm_configuration_identifier
        if iam_roles is not None: self._values["iam_roles"] = iam_roles
        if kms_key_id is not None: self._values["kms_key_id"] = kms_key_id
        if logging_properties is not None: self._values["logging_properties"] = logging_properties
        if number_of_nodes is not None: self._values["number_of_nodes"] = number_of_nodes
        if owner_account is not None: self._values["owner_account"] = owner_account
        if port is not None: self._values["port"] = port
        if preferred_maintenance_window is not None: self._values["preferred_maintenance_window"] = preferred_maintenance_window
        if publicly_accessible is not None: self._values["publicly_accessible"] = publicly_accessible
        if snapshot_cluster_identifier is not None: self._values["snapshot_cluster_identifier"] = snapshot_cluster_identifier
        if snapshot_identifier is not None: self._values["snapshot_identifier"] = snapshot_identifier
        if tags is not None: self._values["tags"] = tags
        if vpc_security_group_ids is not None: self._values["vpc_security_group_ids"] = vpc_security_group_ids

    @property
    def cluster_type(self) -> str:
        """``AWS::Redshift::Cluster.ClusterType``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-clustertype
        """
        return self._values.get('cluster_type')

    @property
    def db_name(self) -> str:
        """``AWS::Redshift::Cluster.DBName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-dbname
        """
        return self._values.get('db_name')

    @property
    def master_username(self) -> str:
        """``AWS::Redshift::Cluster.MasterUsername``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-masterusername
        """
        return self._values.get('master_username')

    @property
    def master_user_password(self) -> str:
        """``AWS::Redshift::Cluster.MasterUserPassword``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-masteruserpassword
        """
        return self._values.get('master_user_password')

    @property
    def node_type(self) -> str:
        """``AWS::Redshift::Cluster.NodeType``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-nodetype
        """
        return self._values.get('node_type')

    @property
    def allow_version_upgrade(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::Redshift::Cluster.AllowVersionUpgrade``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-allowversionupgrade
        """
        return self._values.get('allow_version_upgrade')

    @property
    def automated_snapshot_retention_period(self) -> typing.Optional[jsii.Number]:
        """``AWS::Redshift::Cluster.AutomatedSnapshotRetentionPeriod``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-automatedsnapshotretentionperiod
        """
        return self._values.get('automated_snapshot_retention_period')

    @property
    def availability_zone(self) -> typing.Optional[str]:
        """``AWS::Redshift::Cluster.AvailabilityZone``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-availabilityzone
        """
        return self._values.get('availability_zone')

    @property
    def cluster_identifier(self) -> typing.Optional[str]:
        """``AWS::Redshift::Cluster.ClusterIdentifier``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-clusteridentifier
        """
        return self._values.get('cluster_identifier')

    @property
    def cluster_parameter_group_name(self) -> typing.Optional[str]:
        """``AWS::Redshift::Cluster.ClusterParameterGroupName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-clusterparametergroupname
        """
        return self._values.get('cluster_parameter_group_name')

    @property
    def cluster_security_groups(self) -> typing.Optional[typing.List[str]]:
        """``AWS::Redshift::Cluster.ClusterSecurityGroups``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-clustersecuritygroups
        """
        return self._values.get('cluster_security_groups')

    @property
    def cluster_subnet_group_name(self) -> typing.Optional[str]:
        """``AWS::Redshift::Cluster.ClusterSubnetGroupName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-clustersubnetgroupname
        """
        return self._values.get('cluster_subnet_group_name')

    @property
    def cluster_version(self) -> typing.Optional[str]:
        """``AWS::Redshift::Cluster.ClusterVersion``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-clusterversion
        """
        return self._values.get('cluster_version')

    @property
    def elastic_ip(self) -> typing.Optional[str]:
        """``AWS::Redshift::Cluster.ElasticIp``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-elasticip
        """
        return self._values.get('elastic_ip')

    @property
    def encrypted(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::Redshift::Cluster.Encrypted``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-encrypted
        """
        return self._values.get('encrypted')

    @property
    def hsm_client_certificate_identifier(self) -> typing.Optional[str]:
        """``AWS::Redshift::Cluster.HsmClientCertificateIdentifier``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-hsmclientcertidentifier
        """
        return self._values.get('hsm_client_certificate_identifier')

    @property
    def hsm_configuration_identifier(self) -> typing.Optional[str]:
        """``AWS::Redshift::Cluster.HsmConfigurationIdentifier``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-HsmConfigurationIdentifier
        """
        return self._values.get('hsm_configuration_identifier')

    @property
    def iam_roles(self) -> typing.Optional[typing.List[str]]:
        """``AWS::Redshift::Cluster.IamRoles``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-iamroles
        """
        return self._values.get('iam_roles')

    @property
    def kms_key_id(self) -> typing.Optional[str]:
        """``AWS::Redshift::Cluster.KmsKeyId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-kmskeyid
        """
        return self._values.get('kms_key_id')

    @property
    def logging_properties(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnCluster.LoggingPropertiesProperty"]]]:
        """``AWS::Redshift::Cluster.LoggingProperties``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-loggingproperties
        """
        return self._values.get('logging_properties')

    @property
    def number_of_nodes(self) -> typing.Optional[jsii.Number]:
        """``AWS::Redshift::Cluster.NumberOfNodes``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-nodetype
        """
        return self._values.get('number_of_nodes')

    @property
    def owner_account(self) -> typing.Optional[str]:
        """``AWS::Redshift::Cluster.OwnerAccount``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-owneraccount
        """
        return self._values.get('owner_account')

    @property
    def port(self) -> typing.Optional[jsii.Number]:
        """``AWS::Redshift::Cluster.Port``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-port
        """
        return self._values.get('port')

    @property
    def preferred_maintenance_window(self) -> typing.Optional[str]:
        """``AWS::Redshift::Cluster.PreferredMaintenanceWindow``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-preferredmaintenancewindow
        """
        return self._values.get('preferred_maintenance_window')

    @property
    def publicly_accessible(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::Redshift::Cluster.PubliclyAccessible``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-publiclyaccessible
        """
        return self._values.get('publicly_accessible')

    @property
    def snapshot_cluster_identifier(self) -> typing.Optional[str]:
        """``AWS::Redshift::Cluster.SnapshotClusterIdentifier``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-snapshotclusteridentifier
        """
        return self._values.get('snapshot_cluster_identifier')

    @property
    def snapshot_identifier(self) -> typing.Optional[str]:
        """``AWS::Redshift::Cluster.SnapshotIdentifier``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-snapshotidentifier
        """
        return self._values.get('snapshot_identifier')

    @property
    def tags(self) -> typing.Optional[typing.List[aws_cdk.core.CfnTag]]:
        """``AWS::Redshift::Cluster.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-tags
        """
        return self._values.get('tags')

    @property
    def vpc_security_group_ids(self) -> typing.Optional[typing.List[str]]:
        """``AWS::Redshift::Cluster.VpcSecurityGroupIds``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-vpcsecuritygroupids
        """
        return self._values.get('vpc_security_group_ids')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnClusterProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnClusterSecurityGroup(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-redshift.CfnClusterSecurityGroup"):
    """A CloudFormation ``AWS::Redshift::ClusterSecurityGroup``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clustersecuritygroup.html
    cloudformationResource:
    :cloudformationResource:: AWS::Redshift::ClusterSecurityGroup
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, description: str, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None) -> None:
        """Create a new ``AWS::Redshift::ClusterSecurityGroup``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param description: ``AWS::Redshift::ClusterSecurityGroup.Description``.
        :param tags: ``AWS::Redshift::ClusterSecurityGroup.Tags``.
        """
        props = CfnClusterSecurityGroupProps(description=description, tags=tags)

        jsii.create(CfnClusterSecurityGroup, self, [scope, id, props])

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
        """``AWS::Redshift::ClusterSecurityGroup.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clustersecuritygroup.html#cfn-redshift-clustersecuritygroup-tags
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="description")
    def description(self) -> str:
        """``AWS::Redshift::ClusterSecurityGroup.Description``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clustersecuritygroup.html#cfn-redshift-clustersecuritygroup-description
        """
        return jsii.get(self, "description")

    @description.setter
    def description(self, value: str):
        return jsii.set(self, "description", value)


class CfnClusterSecurityGroupIngress(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-redshift.CfnClusterSecurityGroupIngress"):
    """A CloudFormation ``AWS::Redshift::ClusterSecurityGroupIngress``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clustersecuritygroupingress.html
    cloudformationResource:
    :cloudformationResource:: AWS::Redshift::ClusterSecurityGroupIngress
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, cluster_security_group_name: str, cidrip: typing.Optional[str]=None, ec2_security_group_name: typing.Optional[str]=None, ec2_security_group_owner_id: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::Redshift::ClusterSecurityGroupIngress``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param cluster_security_group_name: ``AWS::Redshift::ClusterSecurityGroupIngress.ClusterSecurityGroupName``.
        :param cidrip: ``AWS::Redshift::ClusterSecurityGroupIngress.CIDRIP``.
        :param ec2_security_group_name: ``AWS::Redshift::ClusterSecurityGroupIngress.EC2SecurityGroupName``.
        :param ec2_security_group_owner_id: ``AWS::Redshift::ClusterSecurityGroupIngress.EC2SecurityGroupOwnerId``.
        """
        props = CfnClusterSecurityGroupIngressProps(cluster_security_group_name=cluster_security_group_name, cidrip=cidrip, ec2_security_group_name=ec2_security_group_name, ec2_security_group_owner_id=ec2_security_group_owner_id)

        jsii.create(CfnClusterSecurityGroupIngress, self, [scope, id, props])

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
    @jsii.member(jsii_name="clusterSecurityGroupName")
    def cluster_security_group_name(self) -> str:
        """``AWS::Redshift::ClusterSecurityGroupIngress.ClusterSecurityGroupName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clustersecuritygroupingress.html#cfn-redshift-clustersecuritygroupingress-clustersecuritygroupname
        """
        return jsii.get(self, "clusterSecurityGroupName")

    @cluster_security_group_name.setter
    def cluster_security_group_name(self, value: str):
        return jsii.set(self, "clusterSecurityGroupName", value)

    @property
    @jsii.member(jsii_name="cidrip")
    def cidrip(self) -> typing.Optional[str]:
        """``AWS::Redshift::ClusterSecurityGroupIngress.CIDRIP``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clustersecuritygroupingress.html#cfn-redshift-clustersecuritygroupingress-cidrip
        """
        return jsii.get(self, "cidrip")

    @cidrip.setter
    def cidrip(self, value: typing.Optional[str]):
        return jsii.set(self, "cidrip", value)

    @property
    @jsii.member(jsii_name="ec2SecurityGroupName")
    def ec2_security_group_name(self) -> typing.Optional[str]:
        """``AWS::Redshift::ClusterSecurityGroupIngress.EC2SecurityGroupName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clustersecuritygroupingress.html#cfn-redshift-clustersecuritygroupingress-ec2securitygroupname
        """
        return jsii.get(self, "ec2SecurityGroupName")

    @ec2_security_group_name.setter
    def ec2_security_group_name(self, value: typing.Optional[str]):
        return jsii.set(self, "ec2SecurityGroupName", value)

    @property
    @jsii.member(jsii_name="ec2SecurityGroupOwnerId")
    def ec2_security_group_owner_id(self) -> typing.Optional[str]:
        """``AWS::Redshift::ClusterSecurityGroupIngress.EC2SecurityGroupOwnerId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clustersecuritygroupingress.html#cfn-redshift-clustersecuritygroupingress-ec2securitygroupownerid
        """
        return jsii.get(self, "ec2SecurityGroupOwnerId")

    @ec2_security_group_owner_id.setter
    def ec2_security_group_owner_id(self, value: typing.Optional[str]):
        return jsii.set(self, "ec2SecurityGroupOwnerId", value)


@jsii.data_type(jsii_type="@aws-cdk/aws-redshift.CfnClusterSecurityGroupIngressProps", jsii_struct_bases=[], name_mapping={'cluster_security_group_name': 'clusterSecurityGroupName', 'cidrip': 'cidrip', 'ec2_security_group_name': 'ec2SecurityGroupName', 'ec2_security_group_owner_id': 'ec2SecurityGroupOwnerId'})
class CfnClusterSecurityGroupIngressProps():
    def __init__(self, *, cluster_security_group_name: str, cidrip: typing.Optional[str]=None, ec2_security_group_name: typing.Optional[str]=None, ec2_security_group_owner_id: typing.Optional[str]=None):
        """Properties for defining a ``AWS::Redshift::ClusterSecurityGroupIngress``.

        :param cluster_security_group_name: ``AWS::Redshift::ClusterSecurityGroupIngress.ClusterSecurityGroupName``.
        :param cidrip: ``AWS::Redshift::ClusterSecurityGroupIngress.CIDRIP``.
        :param ec2_security_group_name: ``AWS::Redshift::ClusterSecurityGroupIngress.EC2SecurityGroupName``.
        :param ec2_security_group_owner_id: ``AWS::Redshift::ClusterSecurityGroupIngress.EC2SecurityGroupOwnerId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clustersecuritygroupingress.html
        """
        self._values = {
            'cluster_security_group_name': cluster_security_group_name,
        }
        if cidrip is not None: self._values["cidrip"] = cidrip
        if ec2_security_group_name is not None: self._values["ec2_security_group_name"] = ec2_security_group_name
        if ec2_security_group_owner_id is not None: self._values["ec2_security_group_owner_id"] = ec2_security_group_owner_id

    @property
    def cluster_security_group_name(self) -> str:
        """``AWS::Redshift::ClusterSecurityGroupIngress.ClusterSecurityGroupName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clustersecuritygroupingress.html#cfn-redshift-clustersecuritygroupingress-clustersecuritygroupname
        """
        return self._values.get('cluster_security_group_name')

    @property
    def cidrip(self) -> typing.Optional[str]:
        """``AWS::Redshift::ClusterSecurityGroupIngress.CIDRIP``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clustersecuritygroupingress.html#cfn-redshift-clustersecuritygroupingress-cidrip
        """
        return self._values.get('cidrip')

    @property
    def ec2_security_group_name(self) -> typing.Optional[str]:
        """``AWS::Redshift::ClusterSecurityGroupIngress.EC2SecurityGroupName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clustersecuritygroupingress.html#cfn-redshift-clustersecuritygroupingress-ec2securitygroupname
        """
        return self._values.get('ec2_security_group_name')

    @property
    def ec2_security_group_owner_id(self) -> typing.Optional[str]:
        """``AWS::Redshift::ClusterSecurityGroupIngress.EC2SecurityGroupOwnerId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clustersecuritygroupingress.html#cfn-redshift-clustersecuritygroupingress-ec2securitygroupownerid
        """
        return self._values.get('ec2_security_group_owner_id')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnClusterSecurityGroupIngressProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


@jsii.data_type(jsii_type="@aws-cdk/aws-redshift.CfnClusterSecurityGroupProps", jsii_struct_bases=[], name_mapping={'description': 'description', 'tags': 'tags'})
class CfnClusterSecurityGroupProps():
    def __init__(self, *, description: str, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None):
        """Properties for defining a ``AWS::Redshift::ClusterSecurityGroup``.

        :param description: ``AWS::Redshift::ClusterSecurityGroup.Description``.
        :param tags: ``AWS::Redshift::ClusterSecurityGroup.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clustersecuritygroup.html
        """
        self._values = {
            'description': description,
        }
        if tags is not None: self._values["tags"] = tags

    @property
    def description(self) -> str:
        """``AWS::Redshift::ClusterSecurityGroup.Description``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clustersecuritygroup.html#cfn-redshift-clustersecuritygroup-description
        """
        return self._values.get('description')

    @property
    def tags(self) -> typing.Optional[typing.List[aws_cdk.core.CfnTag]]:
        """``AWS::Redshift::ClusterSecurityGroup.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clustersecuritygroup.html#cfn-redshift-clustersecuritygroup-tags
        """
        return self._values.get('tags')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnClusterSecurityGroupProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnClusterSubnetGroup(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-redshift.CfnClusterSubnetGroup"):
    """A CloudFormation ``AWS::Redshift::ClusterSubnetGroup``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clustersubnetgroup.html
    cloudformationResource:
    :cloudformationResource:: AWS::Redshift::ClusterSubnetGroup
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, description: str, subnet_ids: typing.List[str], tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None) -> None:
        """Create a new ``AWS::Redshift::ClusterSubnetGroup``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param description: ``AWS::Redshift::ClusterSubnetGroup.Description``.
        :param subnet_ids: ``AWS::Redshift::ClusterSubnetGroup.SubnetIds``.
        :param tags: ``AWS::Redshift::ClusterSubnetGroup.Tags``.
        """
        props = CfnClusterSubnetGroupProps(description=description, subnet_ids=subnet_ids, tags=tags)

        jsii.create(CfnClusterSubnetGroup, self, [scope, id, props])

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
        """``AWS::Redshift::ClusterSubnetGroup.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clustersubnetgroup.html#cfn-redshift-clustersubnetgroup-tags
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="description")
    def description(self) -> str:
        """``AWS::Redshift::ClusterSubnetGroup.Description``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clustersubnetgroup.html#cfn-redshift-clustersubnetgroup-description
        """
        return jsii.get(self, "description")

    @description.setter
    def description(self, value: str):
        return jsii.set(self, "description", value)

    @property
    @jsii.member(jsii_name="subnetIds")
    def subnet_ids(self) -> typing.List[str]:
        """``AWS::Redshift::ClusterSubnetGroup.SubnetIds``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clustersubnetgroup.html#cfn-redshift-clustersubnetgroup-subnetids
        """
        return jsii.get(self, "subnetIds")

    @subnet_ids.setter
    def subnet_ids(self, value: typing.List[str]):
        return jsii.set(self, "subnetIds", value)


@jsii.data_type(jsii_type="@aws-cdk/aws-redshift.CfnClusterSubnetGroupProps", jsii_struct_bases=[], name_mapping={'description': 'description', 'subnet_ids': 'subnetIds', 'tags': 'tags'})
class CfnClusterSubnetGroupProps():
    def __init__(self, *, description: str, subnet_ids: typing.List[str], tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None):
        """Properties for defining a ``AWS::Redshift::ClusterSubnetGroup``.

        :param description: ``AWS::Redshift::ClusterSubnetGroup.Description``.
        :param subnet_ids: ``AWS::Redshift::ClusterSubnetGroup.SubnetIds``.
        :param tags: ``AWS::Redshift::ClusterSubnetGroup.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clustersubnetgroup.html
        """
        self._values = {
            'description': description,
            'subnet_ids': subnet_ids,
        }
        if tags is not None: self._values["tags"] = tags

    @property
    def description(self) -> str:
        """``AWS::Redshift::ClusterSubnetGroup.Description``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clustersubnetgroup.html#cfn-redshift-clustersubnetgroup-description
        """
        return self._values.get('description')

    @property
    def subnet_ids(self) -> typing.List[str]:
        """``AWS::Redshift::ClusterSubnetGroup.SubnetIds``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clustersubnetgroup.html#cfn-redshift-clustersubnetgroup-subnetids
        """
        return self._values.get('subnet_ids')

    @property
    def tags(self) -> typing.Optional[typing.List[aws_cdk.core.CfnTag]]:
        """``AWS::Redshift::ClusterSubnetGroup.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clustersubnetgroup.html#cfn-redshift-clustersubnetgroup-tags
        """
        return self._values.get('tags')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnClusterSubnetGroupProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


__all__ = ["CfnCluster", "CfnClusterParameterGroup", "CfnClusterParameterGroupProps", "CfnClusterProps", "CfnClusterSecurityGroup", "CfnClusterSecurityGroupIngress", "CfnClusterSecurityGroupIngressProps", "CfnClusterSecurityGroupProps", "CfnClusterSubnetGroup", "CfnClusterSubnetGroupProps", "__jsii_assembly__"]

publication.publish()
