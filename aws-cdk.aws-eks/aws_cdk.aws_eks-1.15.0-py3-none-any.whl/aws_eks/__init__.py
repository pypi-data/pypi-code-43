import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.aws_autoscaling
import aws_cdk.aws_cloudformation
import aws_cdk.aws_ec2
import aws_cdk.aws_iam
import aws_cdk.aws_lambda
import aws_cdk.aws_ssm
import aws_cdk.core
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-eks", "1.15.0", __name__, "aws-eks@1.15.0.jsii.tgz")
@jsii.data_type(jsii_type="@aws-cdk/aws-eks.AutoScalingGroupOptions", jsii_struct_bases=[], name_mapping={'bootstrap_enabled': 'bootstrapEnabled', 'bootstrap_options': 'bootstrapOptions', 'map_role': 'mapRole'})
class AutoScalingGroupOptions():
    def __init__(self, *, bootstrap_enabled: typing.Optional[bool]=None, bootstrap_options: typing.Optional["BootstrapOptions"]=None, map_role: typing.Optional[bool]=None):
        """Options for adding an AutoScalingGroup as capacity.

        :param bootstrap_enabled: Configures the EC2 user-data script for instances in this autoscaling group to bootstrap the node (invoke ``/etc/eks/bootstrap.sh``) and associate it with the EKS cluster. If you wish to provide a custom user data script, set this to ``false`` and manually invoke ``autoscalingGroup.addUserData()``. Default: true
        :param bootstrap_options: Allows options for node bootstrapping through EC2 user data.
        :param map_role: Will automatically update the aws-auth ConfigMap to map the IAM instance role to RBAC. This cannot be explicitly set to ``true`` if the cluster has kubectl disabled. Default: - true if the cluster has kubectl enabled (which is the default).

        stability
        :stability: experimental
        """
        self._values = {
        }
        if bootstrap_enabled is not None: self._values["bootstrap_enabled"] = bootstrap_enabled
        if bootstrap_options is not None: self._values["bootstrap_options"] = bootstrap_options
        if map_role is not None: self._values["map_role"] = map_role

    @property
    def bootstrap_enabled(self) -> typing.Optional[bool]:
        """Configures the EC2 user-data script for instances in this autoscaling group to bootstrap the node (invoke ``/etc/eks/bootstrap.sh``) and associate it with the EKS cluster.

        If you wish to provide a custom user data script, set this to ``false`` and
        manually invoke ``autoscalingGroup.addUserData()``.

        default
        :default: true

        stability
        :stability: experimental
        """
        return self._values.get('bootstrap_enabled')

    @property
    def bootstrap_options(self) -> typing.Optional["BootstrapOptions"]:
        """Allows options for node bootstrapping through EC2 user data.

        stability
        :stability: experimental
        """
        return self._values.get('bootstrap_options')

    @property
    def map_role(self) -> typing.Optional[bool]:
        """Will automatically update the aws-auth ConfigMap to map the IAM instance role to RBAC.

        This cannot be explicitly set to ``true`` if the cluster has kubectl disabled.

        default
        :default: - true if the cluster has kubectl enabled (which is the default).

        stability
        :stability: experimental
        """
        return self._values.get('map_role')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'AutoScalingGroupOptions(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class AwsAuth(aws_cdk.core.Construct, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-eks.AwsAuth"):
    """Manages mapping between IAM users and roles to Kubernetes RBAC configuration.

    see
    :see: https://docs.aws.amazon.com/en_us/eks/latest/userguide/add-user-role.html
    stability
    :stability: experimental
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, cluster: "Cluster") -> None:
        """
        :param scope: -
        :param id: -
        :param props: -
        :param cluster: The EKS cluster to apply this configuration to. [disable-awslint:ref-via-interface]

        stability
        :stability: experimental
        """
        props = AwsAuthProps(cluster=cluster)

        jsii.create(AwsAuth, self, [scope, id, props])

    @jsii.member(jsii_name="addAccount")
    def add_account(self, account_id: str) -> None:
        """Additional AWS account to add to the aws-auth configmap.

        :param account_id: account number.

        stability
        :stability: experimental
        """
        return jsii.invoke(self, "addAccount", [account_id])

    @jsii.member(jsii_name="addMastersRole")
    def add_masters_role(self, role: aws_cdk.aws_iam.IRole, username: typing.Optional[str]=None) -> None:
        """Adds the specified IAM role to the ``system:masters`` RBAC group, which means that anyone that can assume it will be able to administer this Kubernetes system.

        :param role: The IAM role to add.
        :param username: Optional user (defaults to the role ARN).

        stability
        :stability: experimental
        """
        return jsii.invoke(self, "addMastersRole", [role, username])

    @jsii.member(jsii_name="addRoleMapping")
    def add_role_mapping(self, role: aws_cdk.aws_iam.IRole, *, groups: typing.List[str], username: typing.Optional[str]=None) -> None:
        """Adds a mapping between an IAM role to a Kubernetes user and groups.

        :param role: The IAM role to map.
        :param mapping: Mapping to k8s user name and groups.
        :param groups: A list of groups within Kubernetes to which the role is mapped.
        :param username: The user name within Kubernetes to map to the IAM role. Default: - By default, the user name is the ARN of the IAM role.

        stability
        :stability: experimental
        """
        mapping = Mapping(groups=groups, username=username)

        return jsii.invoke(self, "addRoleMapping", [role, mapping])

    @jsii.member(jsii_name="addUserMapping")
    def add_user_mapping(self, user: aws_cdk.aws_iam.IUser, *, groups: typing.List[str], username: typing.Optional[str]=None) -> None:
        """Adds a mapping between an IAM user to a Kubernetes user and groups.

        :param user: The IAM user to map.
        :param mapping: Mapping to k8s user name and groups.
        :param groups: A list of groups within Kubernetes to which the role is mapped.
        :param username: The user name within Kubernetes to map to the IAM role. Default: - By default, the user name is the ARN of the IAM role.

        stability
        :stability: experimental
        """
        mapping = Mapping(groups=groups, username=username)

        return jsii.invoke(self, "addUserMapping", [user, mapping])


@jsii.data_type(jsii_type="@aws-cdk/aws-eks.AwsAuthProps", jsii_struct_bases=[], name_mapping={'cluster': 'cluster'})
class AwsAuthProps():
    def __init__(self, *, cluster: "Cluster"):
        """
        :param cluster: The EKS cluster to apply this configuration to. [disable-awslint:ref-via-interface]

        stability
        :stability: experimental
        """
        self._values = {
            'cluster': cluster,
        }

    @property
    def cluster(self) -> "Cluster":
        """The EKS cluster to apply this configuration to.

        [disable-awslint:ref-via-interface]

        stability
        :stability: experimental
        """
        return self._values.get('cluster')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'AwsAuthProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


@jsii.data_type(jsii_type="@aws-cdk/aws-eks.BootstrapOptions", jsii_struct_bases=[], name_mapping={'additional_args': 'additionalArgs', 'aws_api_retry_attempts': 'awsApiRetryAttempts', 'docker_config_json': 'dockerConfigJson', 'enable_docker_bridge': 'enableDockerBridge', 'kubelet_extra_args': 'kubeletExtraArgs', 'use_max_pods': 'useMaxPods'})
class BootstrapOptions():
    def __init__(self, *, additional_args: typing.Optional[str]=None, aws_api_retry_attempts: typing.Optional[jsii.Number]=None, docker_config_json: typing.Optional[str]=None, enable_docker_bridge: typing.Optional[bool]=None, kubelet_extra_args: typing.Optional[str]=None, use_max_pods: typing.Optional[bool]=None):
        """
        :param additional_args: Additional command line arguments to pass to the ``/etc/eks/bootstrap.sh`` command. Default: - none
        :param aws_api_retry_attempts: Number of retry attempts for AWS API call (DescribeCluster). Default: 3
        :param docker_config_json: The contents of the ``/etc/docker/daemon.json`` file. Useful if you want a custom config differing from the default one in the EKS AMI. Default: - none
        :param enable_docker_bridge: Restores the docker default bridge network. Default: false
        :param kubelet_extra_args: Extra arguments to add to the kubelet. Useful for adding labels or taints. Default: - none
        :param use_max_pods: Sets ``--max-pods`` for the kubelet based on the capacity of the EC2 instance. Default: true

        stability
        :stability: experimental
        """
        self._values = {
        }
        if additional_args is not None: self._values["additional_args"] = additional_args
        if aws_api_retry_attempts is not None: self._values["aws_api_retry_attempts"] = aws_api_retry_attempts
        if docker_config_json is not None: self._values["docker_config_json"] = docker_config_json
        if enable_docker_bridge is not None: self._values["enable_docker_bridge"] = enable_docker_bridge
        if kubelet_extra_args is not None: self._values["kubelet_extra_args"] = kubelet_extra_args
        if use_max_pods is not None: self._values["use_max_pods"] = use_max_pods

    @property
    def additional_args(self) -> typing.Optional[str]:
        """Additional command line arguments to pass to the ``/etc/eks/bootstrap.sh`` command.

        default
        :default: - none

        see
        :see: https://github.com/awslabs/amazon-eks-ami/blob/master/files/bootstrap.sh
        stability
        :stability: experimental
        """
        return self._values.get('additional_args')

    @property
    def aws_api_retry_attempts(self) -> typing.Optional[jsii.Number]:
        """Number of retry attempts for AWS API call (DescribeCluster).

        default
        :default: 3

        stability
        :stability: experimental
        """
        return self._values.get('aws_api_retry_attempts')

    @property
    def docker_config_json(self) -> typing.Optional[str]:
        """The contents of the ``/etc/docker/daemon.json`` file. Useful if you want a custom config differing from the default one in the EKS AMI.

        default
        :default: - none

        stability
        :stability: experimental
        """
        return self._values.get('docker_config_json')

    @property
    def enable_docker_bridge(self) -> typing.Optional[bool]:
        """Restores the docker default bridge network.

        default
        :default: false

        stability
        :stability: experimental
        """
        return self._values.get('enable_docker_bridge')

    @property
    def kubelet_extra_args(self) -> typing.Optional[str]:
        """Extra arguments to add to the kubelet.

        Useful for adding labels or taints.

        default
        :default: - none

        stability
        :stability: experimental

        Example::
            # Example may have issues. See https://github.com/aws/jsii/issues/826
            --node - labelsfoo = bar , goo = far
        """
        return self._values.get('kubelet_extra_args')

    @property
    def use_max_pods(self) -> typing.Optional[bool]:
        """Sets ``--max-pods`` for the kubelet based on the capacity of the EC2 instance.

        default
        :default: true

        stability
        :stability: experimental
        """
        return self._values.get('use_max_pods')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'BootstrapOptions(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


@jsii.data_type(jsii_type="@aws-cdk/aws-eks.CapacityOptions", jsii_struct_bases=[aws_cdk.aws_autoscaling.CommonAutoScalingGroupProps], name_mapping={'allow_all_outbound': 'allowAllOutbound', 'associate_public_ip_address': 'associatePublicIpAddress', 'cooldown': 'cooldown', 'desired_capacity': 'desiredCapacity', 'health_check': 'healthCheck', 'ignore_unmodified_size_properties': 'ignoreUnmodifiedSizeProperties', 'key_name': 'keyName', 'max_capacity': 'maxCapacity', 'min_capacity': 'minCapacity', 'notifications_topic': 'notificationsTopic', 'replacing_update_min_successful_instances_percent': 'replacingUpdateMinSuccessfulInstancesPercent', 'resource_signal_count': 'resourceSignalCount', 'resource_signal_timeout': 'resourceSignalTimeout', 'rolling_update_configuration': 'rollingUpdateConfiguration', 'spot_price': 'spotPrice', 'update_type': 'updateType', 'vpc_subnets': 'vpcSubnets', 'instance_type': 'instanceType', 'bootstrap_enabled': 'bootstrapEnabled', 'bootstrap_options': 'bootstrapOptions', 'map_role': 'mapRole'})
class CapacityOptions(aws_cdk.aws_autoscaling.CommonAutoScalingGroupProps):
    def __init__(self, *, allow_all_outbound: typing.Optional[bool]=None, associate_public_ip_address: typing.Optional[bool]=None, cooldown: typing.Optional[aws_cdk.core.Duration]=None, desired_capacity: typing.Optional[jsii.Number]=None, health_check: typing.Optional[aws_cdk.aws_autoscaling.HealthCheck]=None, ignore_unmodified_size_properties: typing.Optional[bool]=None, key_name: typing.Optional[str]=None, max_capacity: typing.Optional[jsii.Number]=None, min_capacity: typing.Optional[jsii.Number]=None, notifications_topic: typing.Optional[aws_cdk.aws_sns.ITopic]=None, replacing_update_min_successful_instances_percent: typing.Optional[jsii.Number]=None, resource_signal_count: typing.Optional[jsii.Number]=None, resource_signal_timeout: typing.Optional[aws_cdk.core.Duration]=None, rolling_update_configuration: typing.Optional[aws_cdk.aws_autoscaling.RollingUpdateConfiguration]=None, spot_price: typing.Optional[str]=None, update_type: typing.Optional[aws_cdk.aws_autoscaling.UpdateType]=None, vpc_subnets: typing.Optional[aws_cdk.aws_ec2.SubnetSelection]=None, instance_type: aws_cdk.aws_ec2.InstanceType, bootstrap_enabled: typing.Optional[bool]=None, bootstrap_options: typing.Optional["BootstrapOptions"]=None, map_role: typing.Optional[bool]=None):
        """Options for adding worker nodes.

        :param allow_all_outbound: Whether the instances can initiate connections to anywhere by default. Default: true
        :param associate_public_ip_address: Whether instances in the Auto Scaling Group should have public IP addresses associated with them. Default: - Use subnet setting.
        :param cooldown: Default scaling cooldown for this AutoScalingGroup. Default: Duration.minutes(5)
        :param desired_capacity: Initial amount of instances in the fleet. Default: 1
        :param health_check: Configuration for health checks. Default: - HealthCheck.ec2 with no grace period
        :param ignore_unmodified_size_properties: If the ASG has scheduled actions, don't reset unchanged group sizes. Only used if the ASG has scheduled actions (which may scale your ASG up or down regardless of cdk deployments). If true, the size of the group will only be reset if it has been changed in the CDK app. If false, the sizes will always be changed back to what they were in the CDK app on deployment. Default: true
        :param key_name: Name of SSH keypair to grant access to instances. Default: - No SSH access will be possible.
        :param max_capacity: Maximum number of instances in the fleet. Default: desiredCapacity
        :param min_capacity: Minimum number of instances in the fleet. Default: 1
        :param notifications_topic: SNS topic to send notifications about fleet changes. Default: - No fleet change notifications will be sent.
        :param replacing_update_min_successful_instances_percent: Configuration for replacing updates. Only used if updateType == UpdateType.ReplacingUpdate. Specifies how many instances must signal success for the update to succeed. Default: minSuccessfulInstancesPercent
        :param resource_signal_count: How many ResourceSignal calls CloudFormation expects before the resource is considered created. Default: 1
        :param resource_signal_timeout: The length of time to wait for the resourceSignalCount. The maximum value is 43200 (12 hours). Default: Duration.minutes(5)
        :param rolling_update_configuration: Configuration for rolling updates. Only used if updateType == UpdateType.RollingUpdate. Default: - RollingUpdateConfiguration with defaults.
        :param spot_price: The maximum hourly price (in USD) to be paid for any Spot Instance launched to fulfill the request. Spot Instances are launched when the price you specify exceeds the current Spot market price. Default: none
        :param update_type: What to do when an AutoScalingGroup's instance configuration is changed. This is applied when any of the settings on the ASG are changed that affect how the instances should be created (VPC, instance type, startup scripts, etc.). It indicates how the existing instances should be replaced with new instances matching the new config. By default, nothing is done and only new instances are launched with the new config. Default: UpdateType.None
        :param vpc_subnets: Where to place instances within the VPC. Default: - All Private subnets.
        :param instance_type: Instance type of the instances to start.
        :param bootstrap_enabled: Configures the EC2 user-data script for instances in this autoscaling group to bootstrap the node (invoke ``/etc/eks/bootstrap.sh``) and associate it with the EKS cluster. If you wish to provide a custom user data script, set this to ``false`` and manually invoke ``autoscalingGroup.addUserData()``. Default: true
        :param bootstrap_options: EKS node bootstrapping options. Default: - none
        :param map_role: Will automatically update the aws-auth ConfigMap to map the IAM instance role to RBAC. This cannot be explicitly set to ``true`` if the cluster has kubectl disabled. Default: - true if the cluster has kubectl enabled (which is the default).

        stability
        :stability: experimental
        """
        self._values = {
            'instance_type': instance_type,
        }
        if allow_all_outbound is not None: self._values["allow_all_outbound"] = allow_all_outbound
        if associate_public_ip_address is not None: self._values["associate_public_ip_address"] = associate_public_ip_address
        if cooldown is not None: self._values["cooldown"] = cooldown
        if desired_capacity is not None: self._values["desired_capacity"] = desired_capacity
        if health_check is not None: self._values["health_check"] = health_check
        if ignore_unmodified_size_properties is not None: self._values["ignore_unmodified_size_properties"] = ignore_unmodified_size_properties
        if key_name is not None: self._values["key_name"] = key_name
        if max_capacity is not None: self._values["max_capacity"] = max_capacity
        if min_capacity is not None: self._values["min_capacity"] = min_capacity
        if notifications_topic is not None: self._values["notifications_topic"] = notifications_topic
        if replacing_update_min_successful_instances_percent is not None: self._values["replacing_update_min_successful_instances_percent"] = replacing_update_min_successful_instances_percent
        if resource_signal_count is not None: self._values["resource_signal_count"] = resource_signal_count
        if resource_signal_timeout is not None: self._values["resource_signal_timeout"] = resource_signal_timeout
        if rolling_update_configuration is not None: self._values["rolling_update_configuration"] = rolling_update_configuration
        if spot_price is not None: self._values["spot_price"] = spot_price
        if update_type is not None: self._values["update_type"] = update_type
        if vpc_subnets is not None: self._values["vpc_subnets"] = vpc_subnets
        if bootstrap_enabled is not None: self._values["bootstrap_enabled"] = bootstrap_enabled
        if bootstrap_options is not None: self._values["bootstrap_options"] = bootstrap_options
        if map_role is not None: self._values["map_role"] = map_role

    @property
    def allow_all_outbound(self) -> typing.Optional[bool]:
        """Whether the instances can initiate connections to anywhere by default.

        default
        :default: true
        """
        return self._values.get('allow_all_outbound')

    @property
    def associate_public_ip_address(self) -> typing.Optional[bool]:
        """Whether instances in the Auto Scaling Group should have public IP addresses associated with them.

        default
        :default: - Use subnet setting.
        """
        return self._values.get('associate_public_ip_address')

    @property
    def cooldown(self) -> typing.Optional[aws_cdk.core.Duration]:
        """Default scaling cooldown for this AutoScalingGroup.

        default
        :default: Duration.minutes(5)
        """
        return self._values.get('cooldown')

    @property
    def desired_capacity(self) -> typing.Optional[jsii.Number]:
        """Initial amount of instances in the fleet.

        default
        :default: 1
        """
        return self._values.get('desired_capacity')

    @property
    def health_check(self) -> typing.Optional[aws_cdk.aws_autoscaling.HealthCheck]:
        """Configuration for health checks.

        default
        :default: - HealthCheck.ec2 with no grace period
        """
        return self._values.get('health_check')

    @property
    def ignore_unmodified_size_properties(self) -> typing.Optional[bool]:
        """If the ASG has scheduled actions, don't reset unchanged group sizes.

        Only used if the ASG has scheduled actions (which may scale your ASG up
        or down regardless of cdk deployments). If true, the size of the group
        will only be reset if it has been changed in the CDK app. If false, the
        sizes will always be changed back to what they were in the CDK app
        on deployment.

        default
        :default: true
        """
        return self._values.get('ignore_unmodified_size_properties')

    @property
    def key_name(self) -> typing.Optional[str]:
        """Name of SSH keypair to grant access to instances.

        default
        :default: - No SSH access will be possible.
        """
        return self._values.get('key_name')

    @property
    def max_capacity(self) -> typing.Optional[jsii.Number]:
        """Maximum number of instances in the fleet.

        default
        :default: desiredCapacity
        """
        return self._values.get('max_capacity')

    @property
    def min_capacity(self) -> typing.Optional[jsii.Number]:
        """Minimum number of instances in the fleet.

        default
        :default: 1
        """
        return self._values.get('min_capacity')

    @property
    def notifications_topic(self) -> typing.Optional[aws_cdk.aws_sns.ITopic]:
        """SNS topic to send notifications about fleet changes.

        default
        :default: - No fleet change notifications will be sent.
        """
        return self._values.get('notifications_topic')

    @property
    def replacing_update_min_successful_instances_percent(self) -> typing.Optional[jsii.Number]:
        """Configuration for replacing updates.

        Only used if updateType == UpdateType.ReplacingUpdate. Specifies how
        many instances must signal success for the update to succeed.

        default
        :default: minSuccessfulInstancesPercent
        """
        return self._values.get('replacing_update_min_successful_instances_percent')

    @property
    def resource_signal_count(self) -> typing.Optional[jsii.Number]:
        """How many ResourceSignal calls CloudFormation expects before the resource is considered created.

        default
        :default: 1
        """
        return self._values.get('resource_signal_count')

    @property
    def resource_signal_timeout(self) -> typing.Optional[aws_cdk.core.Duration]:
        """The length of time to wait for the resourceSignalCount.

        The maximum value is 43200 (12 hours).

        default
        :default: Duration.minutes(5)
        """
        return self._values.get('resource_signal_timeout')

    @property
    def rolling_update_configuration(self) -> typing.Optional[aws_cdk.aws_autoscaling.RollingUpdateConfiguration]:
        """Configuration for rolling updates.

        Only used if updateType == UpdateType.RollingUpdate.

        default
        :default: - RollingUpdateConfiguration with defaults.
        """
        return self._values.get('rolling_update_configuration')

    @property
    def spot_price(self) -> typing.Optional[str]:
        """The maximum hourly price (in USD) to be paid for any Spot Instance launched to fulfill the request.

        Spot Instances are
        launched when the price you specify exceeds the current Spot market price.

        default
        :default: none
        """
        return self._values.get('spot_price')

    @property
    def update_type(self) -> typing.Optional[aws_cdk.aws_autoscaling.UpdateType]:
        """What to do when an AutoScalingGroup's instance configuration is changed.

        This is applied when any of the settings on the ASG are changed that
        affect how the instances should be created (VPC, instance type, startup
        scripts, etc.). It indicates how the existing instances should be
        replaced with new instances matching the new config. By default, nothing
        is done and only new instances are launched with the new config.

        default
        :default: UpdateType.None
        """
        return self._values.get('update_type')

    @property
    def vpc_subnets(self) -> typing.Optional[aws_cdk.aws_ec2.SubnetSelection]:
        """Where to place instances within the VPC.

        default
        :default: - All Private subnets.
        """
        return self._values.get('vpc_subnets')

    @property
    def instance_type(self) -> aws_cdk.aws_ec2.InstanceType:
        """Instance type of the instances to start.

        stability
        :stability: experimental
        """
        return self._values.get('instance_type')

    @property
    def bootstrap_enabled(self) -> typing.Optional[bool]:
        """Configures the EC2 user-data script for instances in this autoscaling group to bootstrap the node (invoke ``/etc/eks/bootstrap.sh``) and associate it with the EKS cluster.

        If you wish to provide a custom user data script, set this to ``false`` and
        manually invoke ``autoscalingGroup.addUserData()``.

        default
        :default: true

        stability
        :stability: experimental
        """
        return self._values.get('bootstrap_enabled')

    @property
    def bootstrap_options(self) -> typing.Optional["BootstrapOptions"]:
        """EKS node bootstrapping options.

        default
        :default: - none

        stability
        :stability: experimental
        """
        return self._values.get('bootstrap_options')

    @property
    def map_role(self) -> typing.Optional[bool]:
        """Will automatically update the aws-auth ConfigMap to map the IAM instance role to RBAC.

        This cannot be explicitly set to ``true`` if the cluster has kubectl disabled.

        default
        :default: - true if the cluster has kubectl enabled (which is the default).

        stability
        :stability: experimental
        """
        return self._values.get('map_role')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CapacityOptions(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnCluster(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-eks.CfnCluster"):
    """A CloudFormation ``AWS::EKS::Cluster``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-eks-cluster.html
    cloudformationResource:
    :cloudformationResource:: AWS::EKS::Cluster
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, resources_vpc_config: typing.Union["ResourcesVpcConfigProperty", aws_cdk.core.IResolvable], role_arn: str, name: typing.Optional[str]=None, version: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::EKS::Cluster``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param resources_vpc_config: ``AWS::EKS::Cluster.ResourcesVpcConfig``.
        :param role_arn: ``AWS::EKS::Cluster.RoleArn``.
        :param name: ``AWS::EKS::Cluster.Name``.
        :param version: ``AWS::EKS::Cluster.Version``.
        """
        props = CfnClusterProps(resources_vpc_config=resources_vpc_config, role_arn=role_arn, name=name, version=version)

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
    @jsii.member(jsii_name="attrArn")
    def attr_arn(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: Arn
        """
        return jsii.get(self, "attrArn")

    @property
    @jsii.member(jsii_name="attrCertificateAuthorityData")
    def attr_certificate_authority_data(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: CertificateAuthorityData
        """
        return jsii.get(self, "attrCertificateAuthorityData")

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
    @jsii.member(jsii_name="resourcesVpcConfig")
    def resources_vpc_config(self) -> typing.Union["ResourcesVpcConfigProperty", aws_cdk.core.IResolvable]:
        """``AWS::EKS::Cluster.ResourcesVpcConfig``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-eks-cluster.html#cfn-eks-cluster-resourcesvpcconfig
        """
        return jsii.get(self, "resourcesVpcConfig")

    @resources_vpc_config.setter
    def resources_vpc_config(self, value: typing.Union["ResourcesVpcConfigProperty", aws_cdk.core.IResolvable]):
        return jsii.set(self, "resourcesVpcConfig", value)

    @property
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> str:
        """``AWS::EKS::Cluster.RoleArn``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-eks-cluster.html#cfn-eks-cluster-rolearn
        """
        return jsii.get(self, "roleArn")

    @role_arn.setter
    def role_arn(self, value: str):
        return jsii.set(self, "roleArn", value)

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[str]:
        """``AWS::EKS::Cluster.Name``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-eks-cluster.html#cfn-eks-cluster-name
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: typing.Optional[str]):
        return jsii.set(self, "name", value)

    @property
    @jsii.member(jsii_name="version")
    def version(self) -> typing.Optional[str]:
        """``AWS::EKS::Cluster.Version``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-eks-cluster.html#cfn-eks-cluster-version
        """
        return jsii.get(self, "version")

    @version.setter
    def version(self, value: typing.Optional[str]):
        return jsii.set(self, "version", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-eks.CfnCluster.ResourcesVpcConfigProperty", jsii_struct_bases=[], name_mapping={'subnet_ids': 'subnetIds', 'security_group_ids': 'securityGroupIds'})
    class ResourcesVpcConfigProperty():
        def __init__(self, *, subnet_ids: typing.List[str], security_group_ids: typing.Optional[typing.List[str]]=None):
            """
            :param subnet_ids: ``CfnCluster.ResourcesVpcConfigProperty.SubnetIds``.
            :param security_group_ids: ``CfnCluster.ResourcesVpcConfigProperty.SecurityGroupIds``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-eks-cluster-resourcesvpcconfig.html
            """
            self._values = {
                'subnet_ids': subnet_ids,
            }
            if security_group_ids is not None: self._values["security_group_ids"] = security_group_ids

        @property
        def subnet_ids(self) -> typing.List[str]:
            """``CfnCluster.ResourcesVpcConfigProperty.SubnetIds``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-eks-cluster-resourcesvpcconfig.html#cfn-eks-cluster-resourcesvpcconfig-subnetids
            """
            return self._values.get('subnet_ids')

        @property
        def security_group_ids(self) -> typing.Optional[typing.List[str]]:
            """``CfnCluster.ResourcesVpcConfigProperty.SecurityGroupIds``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-eks-cluster-resourcesvpcconfig.html#cfn-eks-cluster-resourcesvpcconfig-securitygroupids
            """
            return self._values.get('security_group_ids')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'ResourcesVpcConfigProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



@jsii.data_type(jsii_type="@aws-cdk/aws-eks.CfnClusterProps", jsii_struct_bases=[], name_mapping={'resources_vpc_config': 'resourcesVpcConfig', 'role_arn': 'roleArn', 'name': 'name', 'version': 'version'})
class CfnClusterProps():
    def __init__(self, *, resources_vpc_config: typing.Union["CfnCluster.ResourcesVpcConfigProperty", aws_cdk.core.IResolvable], role_arn: str, name: typing.Optional[str]=None, version: typing.Optional[str]=None):
        """Properties for defining a ``AWS::EKS::Cluster``.

        :param resources_vpc_config: ``AWS::EKS::Cluster.ResourcesVpcConfig``.
        :param role_arn: ``AWS::EKS::Cluster.RoleArn``.
        :param name: ``AWS::EKS::Cluster.Name``.
        :param version: ``AWS::EKS::Cluster.Version``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-eks-cluster.html
        """
        self._values = {
            'resources_vpc_config': resources_vpc_config,
            'role_arn': role_arn,
        }
        if name is not None: self._values["name"] = name
        if version is not None: self._values["version"] = version

    @property
    def resources_vpc_config(self) -> typing.Union["CfnCluster.ResourcesVpcConfigProperty", aws_cdk.core.IResolvable]:
        """``AWS::EKS::Cluster.ResourcesVpcConfig``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-eks-cluster.html#cfn-eks-cluster-resourcesvpcconfig
        """
        return self._values.get('resources_vpc_config')

    @property
    def role_arn(self) -> str:
        """``AWS::EKS::Cluster.RoleArn``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-eks-cluster.html#cfn-eks-cluster-rolearn
        """
        return self._values.get('role_arn')

    @property
    def name(self) -> typing.Optional[str]:
        """``AWS::EKS::Cluster.Name``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-eks-cluster.html#cfn-eks-cluster-name
        """
        return self._values.get('name')

    @property
    def version(self) -> typing.Optional[str]:
        """``AWS::EKS::Cluster.Version``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-eks-cluster.html#cfn-eks-cluster-version
        """
        return self._values.get('version')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnClusterProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


@jsii.data_type(jsii_type="@aws-cdk/aws-eks.ClusterAttributes", jsii_struct_bases=[], name_mapping={'cluster_arn': 'clusterArn', 'cluster_certificate_authority_data': 'clusterCertificateAuthorityData', 'cluster_endpoint': 'clusterEndpoint', 'cluster_name': 'clusterName', 'security_groups': 'securityGroups', 'vpc': 'vpc'})
class ClusterAttributes():
    def __init__(self, *, cluster_arn: str, cluster_certificate_authority_data: str, cluster_endpoint: str, cluster_name: str, security_groups: typing.List[aws_cdk.aws_ec2.ISecurityGroup], vpc: aws_cdk.aws_ec2.IVpc):
        """
        :param cluster_arn: The unique ARN assigned to the service by AWS in the form of arn:aws:eks:.
        :param cluster_certificate_authority_data: The certificate-authority-data for your cluster.
        :param cluster_endpoint: The API Server endpoint URL.
        :param cluster_name: The physical name of the Cluster.
        :param security_groups: The security groups associated with this cluster.
        :param vpc: The VPC in which this Cluster was created.

        stability
        :stability: experimental
        """
        self._values = {
            'cluster_arn': cluster_arn,
            'cluster_certificate_authority_data': cluster_certificate_authority_data,
            'cluster_endpoint': cluster_endpoint,
            'cluster_name': cluster_name,
            'security_groups': security_groups,
            'vpc': vpc,
        }

    @property
    def cluster_arn(self) -> str:
        """The unique ARN assigned to the service by AWS in the form of arn:aws:eks:.

        stability
        :stability: experimental
        """
        return self._values.get('cluster_arn')

    @property
    def cluster_certificate_authority_data(self) -> str:
        """The certificate-authority-data for your cluster.

        stability
        :stability: experimental
        """
        return self._values.get('cluster_certificate_authority_data')

    @property
    def cluster_endpoint(self) -> str:
        """The API Server endpoint URL.

        stability
        :stability: experimental
        """
        return self._values.get('cluster_endpoint')

    @property
    def cluster_name(self) -> str:
        """The physical name of the Cluster.

        stability
        :stability: experimental
        """
        return self._values.get('cluster_name')

    @property
    def security_groups(self) -> typing.List[aws_cdk.aws_ec2.ISecurityGroup]:
        """The security groups associated with this cluster.

        stability
        :stability: experimental
        """
        return self._values.get('security_groups')

    @property
    def vpc(self) -> aws_cdk.aws_ec2.IVpc:
        """The VPC in which this Cluster was created.

        stability
        :stability: experimental
        """
        return self._values.get('vpc')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'ClusterAttributes(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


@jsii.data_type(jsii_type="@aws-cdk/aws-eks.ClusterProps", jsii_struct_bases=[], name_mapping={'cluster_name': 'clusterName', 'default_capacity': 'defaultCapacity', 'default_capacity_instance': 'defaultCapacityInstance', 'kubectl_enabled': 'kubectlEnabled', 'masters_role': 'mastersRole', 'output_cluster_name': 'outputClusterName', 'output_config_command': 'outputConfigCommand', 'output_masters_role_arn': 'outputMastersRoleArn', 'role': 'role', 'security_group': 'securityGroup', 'version': 'version', 'vpc': 'vpc', 'vpc_subnets': 'vpcSubnets'})
class ClusterProps():
    def __init__(self, *, cluster_name: typing.Optional[str]=None, default_capacity: typing.Optional[jsii.Number]=None, default_capacity_instance: typing.Optional[aws_cdk.aws_ec2.InstanceType]=None, kubectl_enabled: typing.Optional[bool]=None, masters_role: typing.Optional[aws_cdk.aws_iam.IRole]=None, output_cluster_name: typing.Optional[bool]=None, output_config_command: typing.Optional[bool]=None, output_masters_role_arn: typing.Optional[bool]=None, role: typing.Optional[aws_cdk.aws_iam.IRole]=None, security_group: typing.Optional[aws_cdk.aws_ec2.ISecurityGroup]=None, version: typing.Optional[str]=None, vpc: typing.Optional[aws_cdk.aws_ec2.IVpc]=None, vpc_subnets: typing.Optional[typing.List[aws_cdk.aws_ec2.SubnetSelection]]=None):
        """Properties to instantiate the Cluster.

        :param cluster_name: Name for the cluster. Default: - Automatically generated name
        :param default_capacity: Number of instances to allocate as an initial capacity for this cluster. Instance type can be configured through ``defaultCapacityInstanceType``, which defaults to ``m5.large``. Use ``cluster.addCapacity`` to add additional customized capacity. Set this to ``0`` is you wish to avoid the initial capacity allocation. Default: 2
        :param default_capacity_instance: The instance type to use for the default capacity. This will only be taken into account if ``defaultCapacity`` is > 0. Default: m5.large
        :param kubectl_enabled: Allows defining ``kubectrl``-related resources on this cluster. If this is disabled, it will not be possible to use the following capabilities: - ``addResource`` - ``addRoleMapping`` - ``addUserMapping`` - ``addMastersRole`` and ``props.mastersRole`` If this is disabled, the cluster can only be managed by issuing ``kubectl`` commands from a session that uses the IAM role/user that created the account. *NOTE*: changing this value will destoy the cluster. This is because a managable cluster must be created using an AWS CloudFormation custom resource which executes with an IAM role owned by the CDK app. Default: true The cluster can be managed by the AWS CDK application.
        :param masters_role: An IAM role that will be added to the ``system:masters`` Kubernetes RBAC group. Default: - By default, it will only possible to update this Kubernetes system by adding resources to this cluster via ``addResource`` or by defining ``KubernetesResource`` resources in your AWS CDK app. Use this if you wish to grant cluster administration privileges to another role.
        :param output_cluster_name: Determines whether a CloudFormation output with the name of the cluster will be synthesized. Default: false
        :param output_config_command: Determines whether a CloudFormation output with the ``aws eks update-kubeconfig`` command will be synthesized. This command will include the cluster name and, if applicable, the ARN of the masters IAM role. Default: true
        :param output_masters_role_arn: Determines whether a CloudFormation output with the ARN of the "masters" IAM role will be synthesized (if ``mastersRole`` is specified). Default: false
        :param role: Role that provides permissions for the Kubernetes control plane to make calls to AWS API operations on your behalf. Default: - A role is automatically created for you
        :param security_group: Security Group to use for Control Plane ENIs. Default: - A security group is automatically created
        :param version: The Kubernetes version to run in the cluster. Default: - If not supplied, will use Amazon default version
        :param vpc: The VPC in which to create the Cluster. Default: - a VPC with default configuration will be created and can be accessed through ``cluster.vpc``.
        :param vpc_subnets: Where to place EKS Control Plane ENIs. If you want to create public load balancers, this must include public subnets. For example, to only select private subnets, supply the following:: vpcSubnets: [ { subnetType: ec2.SubnetType.Private } ] Default: - All public and private subnets

        stability
        :stability: experimental
        """
        self._values = {
        }
        if cluster_name is not None: self._values["cluster_name"] = cluster_name
        if default_capacity is not None: self._values["default_capacity"] = default_capacity
        if default_capacity_instance is not None: self._values["default_capacity_instance"] = default_capacity_instance
        if kubectl_enabled is not None: self._values["kubectl_enabled"] = kubectl_enabled
        if masters_role is not None: self._values["masters_role"] = masters_role
        if output_cluster_name is not None: self._values["output_cluster_name"] = output_cluster_name
        if output_config_command is not None: self._values["output_config_command"] = output_config_command
        if output_masters_role_arn is not None: self._values["output_masters_role_arn"] = output_masters_role_arn
        if role is not None: self._values["role"] = role
        if security_group is not None: self._values["security_group"] = security_group
        if version is not None: self._values["version"] = version
        if vpc is not None: self._values["vpc"] = vpc
        if vpc_subnets is not None: self._values["vpc_subnets"] = vpc_subnets

    @property
    def cluster_name(self) -> typing.Optional[str]:
        """Name for the cluster.

        default
        :default: - Automatically generated name

        stability
        :stability: experimental
        """
        return self._values.get('cluster_name')

    @property
    def default_capacity(self) -> typing.Optional[jsii.Number]:
        """Number of instances to allocate as an initial capacity for this cluster. Instance type can be configured through ``defaultCapacityInstanceType``, which defaults to ``m5.large``.

        Use ``cluster.addCapacity`` to add additional customized capacity. Set this
        to ``0`` is you wish to avoid the initial capacity allocation.

        default
        :default: 2

        stability
        :stability: experimental
        """
        return self._values.get('default_capacity')

    @property
    def default_capacity_instance(self) -> typing.Optional[aws_cdk.aws_ec2.InstanceType]:
        """The instance type to use for the default capacity.

        This will only be taken
        into account if ``defaultCapacity`` is > 0.

        default
        :default: m5.large

        stability
        :stability: experimental
        """
        return self._values.get('default_capacity_instance')

    @property
    def kubectl_enabled(self) -> typing.Optional[bool]:
        """Allows defining ``kubectrl``-related resources on this cluster.

        If this is disabled, it will not be possible to use the following
        capabilities:

        - ``addResource``
        - ``addRoleMapping``
        - ``addUserMapping``
        - ``addMastersRole`` and ``props.mastersRole``

        If this is disabled, the cluster can only be managed by issuing ``kubectl``
        commands from a session that uses the IAM role/user that created the
        account.

        *NOTE*: changing this value will destoy the cluster. This is because a
        managable cluster must be created using an AWS CloudFormation custom
        resource which executes with an IAM role owned by the CDK app.

        default
        :default: true The cluster can be managed by the AWS CDK application.

        stability
        :stability: experimental
        """
        return self._values.get('kubectl_enabled')

    @property
    def masters_role(self) -> typing.Optional[aws_cdk.aws_iam.IRole]:
        """An IAM role that will be added to the ``system:masters`` Kubernetes RBAC group.

        default
        :default:

        - By default, it will only possible to update this Kubernetes
          system by adding resources to this cluster via ``addResource`` or
          by defining ``KubernetesResource`` resources in your AWS CDK app.
          Use this if you wish to grant cluster administration privileges
          to another role.

        see
        :see: https://kubernetes.io/docs/reference/access-authn-authz/rbac/#default-roles-and-role-bindings
        stability
        :stability: experimental
        """
        return self._values.get('masters_role')

    @property
    def output_cluster_name(self) -> typing.Optional[bool]:
        """Determines whether a CloudFormation output with the name of the cluster will be synthesized.

        default
        :default: false

        stability
        :stability: experimental
        """
        return self._values.get('output_cluster_name')

    @property
    def output_config_command(self) -> typing.Optional[bool]:
        """Determines whether a CloudFormation output with the ``aws eks update-kubeconfig`` command will be synthesized.

        This command will include
        the cluster name and, if applicable, the ARN of the masters IAM role.

        default
        :default: true

        stability
        :stability: experimental
        """
        return self._values.get('output_config_command')

    @property
    def output_masters_role_arn(self) -> typing.Optional[bool]:
        """Determines whether a CloudFormation output with the ARN of the "masters" IAM role will be synthesized (if ``mastersRole`` is specified).

        default
        :default: false

        stability
        :stability: experimental
        """
        return self._values.get('output_masters_role_arn')

    @property
    def role(self) -> typing.Optional[aws_cdk.aws_iam.IRole]:
        """Role that provides permissions for the Kubernetes control plane to make calls to AWS API operations on your behalf.

        default
        :default: - A role is automatically created for you

        stability
        :stability: experimental
        """
        return self._values.get('role')

    @property
    def security_group(self) -> typing.Optional[aws_cdk.aws_ec2.ISecurityGroup]:
        """Security Group to use for Control Plane ENIs.

        default
        :default: - A security group is automatically created

        stability
        :stability: experimental
        """
        return self._values.get('security_group')

    @property
    def version(self) -> typing.Optional[str]:
        """The Kubernetes version to run in the cluster.

        default
        :default: - If not supplied, will use Amazon default version

        stability
        :stability: experimental
        """
        return self._values.get('version')

    @property
    def vpc(self) -> typing.Optional[aws_cdk.aws_ec2.IVpc]:
        """The VPC in which to create the Cluster.

        default
        :default: - a VPC with default configuration will be created and can be accessed through ``cluster.vpc``.

        stability
        :stability: experimental
        """
        return self._values.get('vpc')

    @property
    def vpc_subnets(self) -> typing.Optional[typing.List[aws_cdk.aws_ec2.SubnetSelection]]:
        """Where to place EKS Control Plane ENIs.

        If you want to create public load balancers, this must include public subnets.

        For example, to only select private subnets, supply the following::

           # Example may have issues. See https://github.com/aws/jsii/issues/826
           vpcSubnets: [
              { subnetType: ec2.SubnetType.Private }
           ]

        default
        :default: - All public and private subnets

        stability
        :stability: experimental
        """
        return self._values.get('vpc_subnets')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'ClusterProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


@jsii.implements(aws_cdk.aws_ec2.IMachineImage)
class EksOptimizedImage(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-eks.EksOptimizedImage"):
    """Construct an Amazon Linux 2 image from the latest EKS Optimized AMI published in SSM.

    stability
    :stability: experimental
    """
    def __init__(self, *, kubernetes_version: typing.Optional[str]=None, node_type: typing.Optional["NodeType"]=None) -> None:
        """Constructs a new instance of the EcsOptimizedAmi class.

        :param props: -
        :param kubernetes_version: The Kubernetes version to use. Default: - The latest version
        :param node_type: What instance type to retrieve the image for (standard or GPU-optimized). Default: NodeType.STANDARD

        stability
        :stability: experimental
        """
        props = EksOptimizedImageProps(kubernetes_version=kubernetes_version, node_type=node_type)

        jsii.create(EksOptimizedImage, self, [props])

    @jsii.member(jsii_name="getImage")
    def get_image(self, scope: aws_cdk.core.Construct) -> aws_cdk.aws_ec2.MachineImageConfig:
        """Return the correct image.

        :param scope: -

        stability
        :stability: experimental
        """
        return jsii.invoke(self, "getImage", [scope])


@jsii.data_type(jsii_type="@aws-cdk/aws-eks.EksOptimizedImageProps", jsii_struct_bases=[], name_mapping={'kubernetes_version': 'kubernetesVersion', 'node_type': 'nodeType'})
class EksOptimizedImageProps():
    def __init__(self, *, kubernetes_version: typing.Optional[str]=None, node_type: typing.Optional["NodeType"]=None):
        """Properties for EksOptimizedImage.

        :param kubernetes_version: The Kubernetes version to use. Default: - The latest version
        :param node_type: What instance type to retrieve the image for (standard or GPU-optimized). Default: NodeType.STANDARD

        stability
        :stability: experimental
        """
        self._values = {
        }
        if kubernetes_version is not None: self._values["kubernetes_version"] = kubernetes_version
        if node_type is not None: self._values["node_type"] = node_type

    @property
    def kubernetes_version(self) -> typing.Optional[str]:
        """The Kubernetes version to use.

        default
        :default: - The latest version

        stability
        :stability: experimental
        """
        return self._values.get('kubernetes_version')

    @property
    def node_type(self) -> typing.Optional["NodeType"]:
        """What instance type to retrieve the image for (standard or GPU-optimized).

        default
        :default: NodeType.STANDARD

        stability
        :stability: experimental
        """
        return self._values.get('node_type')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'EksOptimizedImageProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


@jsii.interface(jsii_type="@aws-cdk/aws-eks.ICluster")
class ICluster(aws_cdk.core.IResource, aws_cdk.aws_ec2.IConnectable, jsii.compat.Protocol):
    """An EKS cluster.

    stability
    :stability: experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IClusterProxy

    @property
    @jsii.member(jsii_name="clusterArn")
    def cluster_arn(self) -> str:
        """The unique ARN assigned to the service by AWS in the form of arn:aws:eks:.

        stability
        :stability: experimental
        attribute:
        :attribute:: true
        """
        ...

    @property
    @jsii.member(jsii_name="clusterCertificateAuthorityData")
    def cluster_certificate_authority_data(self) -> str:
        """The certificate-authority-data for your cluster.

        stability
        :stability: experimental
        attribute:
        :attribute:: true
        """
        ...

    @property
    @jsii.member(jsii_name="clusterEndpoint")
    def cluster_endpoint(self) -> str:
        """The API Server endpoint URL.

        stability
        :stability: experimental
        attribute:
        :attribute:: true
        """
        ...

    @property
    @jsii.member(jsii_name="clusterName")
    def cluster_name(self) -> str:
        """The physical name of the Cluster.

        stability
        :stability: experimental
        attribute:
        :attribute:: true
        """
        ...

    @property
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> aws_cdk.aws_ec2.IVpc:
        """The VPC in which this Cluster was created.

        stability
        :stability: experimental
        """
        ...


class _IClusterProxy(jsii.proxy_for(aws_cdk.core.IResource), jsii.proxy_for(aws_cdk.aws_ec2.IConnectable)):
    """An EKS cluster.

    stability
    :stability: experimental
    """
    __jsii_type__ = "@aws-cdk/aws-eks.ICluster"
    @property
    @jsii.member(jsii_name="clusterArn")
    def cluster_arn(self) -> str:
        """The unique ARN assigned to the service by AWS in the form of arn:aws:eks:.

        stability
        :stability: experimental
        attribute:
        :attribute:: true
        """
        return jsii.get(self, "clusterArn")

    @property
    @jsii.member(jsii_name="clusterCertificateAuthorityData")
    def cluster_certificate_authority_data(self) -> str:
        """The certificate-authority-data for your cluster.

        stability
        :stability: experimental
        attribute:
        :attribute:: true
        """
        return jsii.get(self, "clusterCertificateAuthorityData")

    @property
    @jsii.member(jsii_name="clusterEndpoint")
    def cluster_endpoint(self) -> str:
        """The API Server endpoint URL.

        stability
        :stability: experimental
        attribute:
        :attribute:: true
        """
        return jsii.get(self, "clusterEndpoint")

    @property
    @jsii.member(jsii_name="clusterName")
    def cluster_name(self) -> str:
        """The physical name of the Cluster.

        stability
        :stability: experimental
        attribute:
        :attribute:: true
        """
        return jsii.get(self, "clusterName")

    @property
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> aws_cdk.aws_ec2.IVpc:
        """The VPC in which this Cluster was created.

        stability
        :stability: experimental
        """
        return jsii.get(self, "vpc")


@jsii.implements(ICluster)
class Cluster(aws_cdk.core.Resource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-eks.Cluster"):
    """A Cluster represents a managed Kubernetes Service (EKS).

    This is a fully managed cluster of API Servers (control-plane)
    The user is still required to create the worker nodes.

    stability
    :stability: experimental
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, cluster_name: typing.Optional[str]=None, default_capacity: typing.Optional[jsii.Number]=None, default_capacity_instance: typing.Optional[aws_cdk.aws_ec2.InstanceType]=None, kubectl_enabled: typing.Optional[bool]=None, masters_role: typing.Optional[aws_cdk.aws_iam.IRole]=None, output_cluster_name: typing.Optional[bool]=None, output_config_command: typing.Optional[bool]=None, output_masters_role_arn: typing.Optional[bool]=None, role: typing.Optional[aws_cdk.aws_iam.IRole]=None, security_group: typing.Optional[aws_cdk.aws_ec2.ISecurityGroup]=None, version: typing.Optional[str]=None, vpc: typing.Optional[aws_cdk.aws_ec2.IVpc]=None, vpc_subnets: typing.Optional[typing.List[aws_cdk.aws_ec2.SubnetSelection]]=None) -> None:
        """Initiates an EKS Cluster with the supplied arguments.

        :param scope: a Construct, most likely a cdk.Stack created.
        :param id: -
        :param props: properties in the IClusterProps interface.
        :param cluster_name: Name for the cluster. Default: - Automatically generated name
        :param default_capacity: Number of instances to allocate as an initial capacity for this cluster. Instance type can be configured through ``defaultCapacityInstanceType``, which defaults to ``m5.large``. Use ``cluster.addCapacity`` to add additional customized capacity. Set this to ``0`` is you wish to avoid the initial capacity allocation. Default: 2
        :param default_capacity_instance: The instance type to use for the default capacity. This will only be taken into account if ``defaultCapacity`` is > 0. Default: m5.large
        :param kubectl_enabled: Allows defining ``kubectrl``-related resources on this cluster. If this is disabled, it will not be possible to use the following capabilities: - ``addResource`` - ``addRoleMapping`` - ``addUserMapping`` - ``addMastersRole`` and ``props.mastersRole`` If this is disabled, the cluster can only be managed by issuing ``kubectl`` commands from a session that uses the IAM role/user that created the account. *NOTE*: changing this value will destoy the cluster. This is because a managable cluster must be created using an AWS CloudFormation custom resource which executes with an IAM role owned by the CDK app. Default: true The cluster can be managed by the AWS CDK application.
        :param masters_role: An IAM role that will be added to the ``system:masters`` Kubernetes RBAC group. Default: - By default, it will only possible to update this Kubernetes system by adding resources to this cluster via ``addResource`` or by defining ``KubernetesResource`` resources in your AWS CDK app. Use this if you wish to grant cluster administration privileges to another role.
        :param output_cluster_name: Determines whether a CloudFormation output with the name of the cluster will be synthesized. Default: false
        :param output_config_command: Determines whether a CloudFormation output with the ``aws eks update-kubeconfig`` command will be synthesized. This command will include the cluster name and, if applicable, the ARN of the masters IAM role. Default: true
        :param output_masters_role_arn: Determines whether a CloudFormation output with the ARN of the "masters" IAM role will be synthesized (if ``mastersRole`` is specified). Default: false
        :param role: Role that provides permissions for the Kubernetes control plane to make calls to AWS API operations on your behalf. Default: - A role is automatically created for you
        :param security_group: Security Group to use for Control Plane ENIs. Default: - A security group is automatically created
        :param version: The Kubernetes version to run in the cluster. Default: - If not supplied, will use Amazon default version
        :param vpc: The VPC in which to create the Cluster. Default: - a VPC with default configuration will be created and can be accessed through ``cluster.vpc``.
        :param vpc_subnets: Where to place EKS Control Plane ENIs. If you want to create public load balancers, this must include public subnets. For example, to only select private subnets, supply the following:: vpcSubnets: [ { subnetType: ec2.SubnetType.Private } ] Default: - All public and private subnets

        stability
        :stability: experimental
        """
        props = ClusterProps(cluster_name=cluster_name, default_capacity=default_capacity, default_capacity_instance=default_capacity_instance, kubectl_enabled=kubectl_enabled, masters_role=masters_role, output_cluster_name=output_cluster_name, output_config_command=output_config_command, output_masters_role_arn=output_masters_role_arn, role=role, security_group=security_group, version=version, vpc=vpc, vpc_subnets=vpc_subnets)

        jsii.create(Cluster, self, [scope, id, props])

    @jsii.member(jsii_name="fromClusterAttributes")
    @classmethod
    def from_cluster_attributes(cls, scope: aws_cdk.core.Construct, id: str, *, cluster_arn: str, cluster_certificate_authority_data: str, cluster_endpoint: str, cluster_name: str, security_groups: typing.List[aws_cdk.aws_ec2.ISecurityGroup], vpc: aws_cdk.aws_ec2.IVpc) -> "ICluster":
        """Import an existing cluster.

        :param scope: the construct scope, in most cases 'this'.
        :param id: the id or name to import as.
        :param attrs: the cluster properties to use for importing information.
        :param cluster_arn: The unique ARN assigned to the service by AWS in the form of arn:aws:eks:.
        :param cluster_certificate_authority_data: The certificate-authority-data for your cluster.
        :param cluster_endpoint: The API Server endpoint URL.
        :param cluster_name: The physical name of the Cluster.
        :param security_groups: The security groups associated with this cluster.
        :param vpc: The VPC in which this Cluster was created.

        stability
        :stability: experimental
        """
        attrs = ClusterAttributes(cluster_arn=cluster_arn, cluster_certificate_authority_data=cluster_certificate_authority_data, cluster_endpoint=cluster_endpoint, cluster_name=cluster_name, security_groups=security_groups, vpc=vpc)

        return jsii.sinvoke(cls, "fromClusterAttributes", [scope, id, attrs])

    @jsii.member(jsii_name="addAutoScalingGroup")
    def add_auto_scaling_group(self, auto_scaling_group: aws_cdk.aws_autoscaling.AutoScalingGroup, *, bootstrap_enabled: typing.Optional[bool]=None, bootstrap_options: typing.Optional["BootstrapOptions"]=None, map_role: typing.Optional[bool]=None) -> None:
        """Add compute capacity to this EKS cluster in the form of an AutoScalingGroup.

        The AutoScalingGroup must be running an EKS-optimized AMI containing the
        /etc/eks/bootstrap.sh script. This method will configure Security Groups,
        add the right policies to the instance role, apply the right tags, and add
        the required user data to the instance's launch configuration.

        Spot instances will be labeled ``lifecycle=Ec2Spot`` and tainted with ``PreferNoSchedule``.
        If kubectl is enabled, the
        `spot interrupt handler <https://github.com/awslabs/ec2-spot-labs/tree/master/ec2-spot-eks-solution/spot-termination-handler>`_
        daemon will be installed on all spot instances to handle
        `EC2 Spot Instance Termination Notices <https://aws.amazon.com/blogs/aws/new-ec2-spot-instance-termination-notices/>`_.

        Prefer to use ``addCapacity`` if possible.

        :param auto_scaling_group: [disable-awslint:ref-via-interface].
        :param options: options for adding auto scaling groups, like customizing the bootstrap script.
        :param bootstrap_enabled: Configures the EC2 user-data script for instances in this autoscaling group to bootstrap the node (invoke ``/etc/eks/bootstrap.sh``) and associate it with the EKS cluster. If you wish to provide a custom user data script, set this to ``false`` and manually invoke ``autoscalingGroup.addUserData()``. Default: true
        :param bootstrap_options: Allows options for node bootstrapping through EC2 user data.
        :param map_role: Will automatically update the aws-auth ConfigMap to map the IAM instance role to RBAC. This cannot be explicitly set to ``true`` if the cluster has kubectl disabled. Default: - true if the cluster has kubectl enabled (which is the default).

        see
        :see: https://docs.aws.amazon.com/eks/latest/userguide/launch-workers.html
        stability
        :stability: experimental
        """
        options = AutoScalingGroupOptions(bootstrap_enabled=bootstrap_enabled, bootstrap_options=bootstrap_options, map_role=map_role)

        return jsii.invoke(self, "addAutoScalingGroup", [auto_scaling_group, options])

    @jsii.member(jsii_name="addCapacity")
    def add_capacity(self, id: str, *, instance_type: aws_cdk.aws_ec2.InstanceType, bootstrap_enabled: typing.Optional[bool]=None, bootstrap_options: typing.Optional["BootstrapOptions"]=None, map_role: typing.Optional[bool]=None, allow_all_outbound: typing.Optional[bool]=None, associate_public_ip_address: typing.Optional[bool]=None, cooldown: typing.Optional[aws_cdk.core.Duration]=None, desired_capacity: typing.Optional[jsii.Number]=None, health_check: typing.Optional[aws_cdk.aws_autoscaling.HealthCheck]=None, ignore_unmodified_size_properties: typing.Optional[bool]=None, key_name: typing.Optional[str]=None, max_capacity: typing.Optional[jsii.Number]=None, min_capacity: typing.Optional[jsii.Number]=None, notifications_topic: typing.Optional[aws_cdk.aws_sns.ITopic]=None, replacing_update_min_successful_instances_percent: typing.Optional[jsii.Number]=None, resource_signal_count: typing.Optional[jsii.Number]=None, resource_signal_timeout: typing.Optional[aws_cdk.core.Duration]=None, rolling_update_configuration: typing.Optional[aws_cdk.aws_autoscaling.RollingUpdateConfiguration]=None, spot_price: typing.Optional[str]=None, update_type: typing.Optional[aws_cdk.aws_autoscaling.UpdateType]=None, vpc_subnets: typing.Optional[aws_cdk.aws_ec2.SubnetSelection]=None) -> aws_cdk.aws_autoscaling.AutoScalingGroup:
        """Add nodes to this EKS cluster.

        The nodes will automatically be configured with the right VPC and AMI
        for the instance type and Kubernetes version.

        Spot instances will be labeled ``lifecycle=Ec2Spot`` and tainted with ``PreferNoSchedule``.
        If kubectl is enabled, the
        `spot interrupt handler <https://github.com/awslabs/ec2-spot-labs/tree/master/ec2-spot-eks-solution/spot-termination-handler>`_
        daemon will be installed on all spot instances to handle
        `EC2 Spot Instance Termination Notices <https://aws.amazon.com/blogs/aws/new-ec2-spot-instance-termination-notices/>`_.

        :param id: -
        :param options: -
        :param instance_type: Instance type of the instances to start.
        :param bootstrap_enabled: Configures the EC2 user-data script for instances in this autoscaling group to bootstrap the node (invoke ``/etc/eks/bootstrap.sh``) and associate it with the EKS cluster. If you wish to provide a custom user data script, set this to ``false`` and manually invoke ``autoscalingGroup.addUserData()``. Default: true
        :param bootstrap_options: EKS node bootstrapping options. Default: - none
        :param map_role: Will automatically update the aws-auth ConfigMap to map the IAM instance role to RBAC. This cannot be explicitly set to ``true`` if the cluster has kubectl disabled. Default: - true if the cluster has kubectl enabled (which is the default).
        :param allow_all_outbound: Whether the instances can initiate connections to anywhere by default. Default: true
        :param associate_public_ip_address: Whether instances in the Auto Scaling Group should have public IP addresses associated with them. Default: - Use subnet setting.
        :param cooldown: Default scaling cooldown for this AutoScalingGroup. Default: Duration.minutes(5)
        :param desired_capacity: Initial amount of instances in the fleet. Default: 1
        :param health_check: Configuration for health checks. Default: - HealthCheck.ec2 with no grace period
        :param ignore_unmodified_size_properties: If the ASG has scheduled actions, don't reset unchanged group sizes. Only used if the ASG has scheduled actions (which may scale your ASG up or down regardless of cdk deployments). If true, the size of the group will only be reset if it has been changed in the CDK app. If false, the sizes will always be changed back to what they were in the CDK app on deployment. Default: true
        :param key_name: Name of SSH keypair to grant access to instances. Default: - No SSH access will be possible.
        :param max_capacity: Maximum number of instances in the fleet. Default: desiredCapacity
        :param min_capacity: Minimum number of instances in the fleet. Default: 1
        :param notifications_topic: SNS topic to send notifications about fleet changes. Default: - No fleet change notifications will be sent.
        :param replacing_update_min_successful_instances_percent: Configuration for replacing updates. Only used if updateType == UpdateType.ReplacingUpdate. Specifies how many instances must signal success for the update to succeed. Default: minSuccessfulInstancesPercent
        :param resource_signal_count: How many ResourceSignal calls CloudFormation expects before the resource is considered created. Default: 1
        :param resource_signal_timeout: The length of time to wait for the resourceSignalCount. The maximum value is 43200 (12 hours). Default: Duration.minutes(5)
        :param rolling_update_configuration: Configuration for rolling updates. Only used if updateType == UpdateType.RollingUpdate. Default: - RollingUpdateConfiguration with defaults.
        :param spot_price: The maximum hourly price (in USD) to be paid for any Spot Instance launched to fulfill the request. Spot Instances are launched when the price you specify exceeds the current Spot market price. Default: none
        :param update_type: What to do when an AutoScalingGroup's instance configuration is changed. This is applied when any of the settings on the ASG are changed that affect how the instances should be created (VPC, instance type, startup scripts, etc.). It indicates how the existing instances should be replaced with new instances matching the new config. By default, nothing is done and only new instances are launched with the new config. Default: UpdateType.None
        :param vpc_subnets: Where to place instances within the VPC. Default: - All Private subnets.

        stability
        :stability: experimental
        """
        options = CapacityOptions(instance_type=instance_type, bootstrap_enabled=bootstrap_enabled, bootstrap_options=bootstrap_options, map_role=map_role, allow_all_outbound=allow_all_outbound, associate_public_ip_address=associate_public_ip_address, cooldown=cooldown, desired_capacity=desired_capacity, health_check=health_check, ignore_unmodified_size_properties=ignore_unmodified_size_properties, key_name=key_name, max_capacity=max_capacity, min_capacity=min_capacity, notifications_topic=notifications_topic, replacing_update_min_successful_instances_percent=replacing_update_min_successful_instances_percent, resource_signal_count=resource_signal_count, resource_signal_timeout=resource_signal_timeout, rolling_update_configuration=rolling_update_configuration, spot_price=spot_price, update_type=update_type, vpc_subnets=vpc_subnets)

        return jsii.invoke(self, "addCapacity", [id, options])

    @jsii.member(jsii_name="addResource")
    def add_resource(self, id: str, *manifest: typing.Any) -> "KubernetesResource":
        """Defines a Kubernetes resource in this cluster.

        The manifest will be applied/deleted using kubectl as needed.

        :param id: logical id of this manifest.
        :param manifest: a list of Kubernetes resource specifications.

        return
        :return: a ``KubernetesResource`` object.

        stability
        :stability: experimental
        throws:
        :throws:: If ``kubectlEnabled`` is ``false``
        """
        return jsii.invoke(self, "addResource", [id, *manifest])

    @property
    @jsii.member(jsii_name="awsAuth")
    def aws_auth(self) -> "AwsAuth":
        """Lazily creates the AwsAuth resource, which manages AWS authentication mapping.

        stability
        :stability: experimental
        """
        return jsii.get(self, "awsAuth")

    @property
    @jsii.member(jsii_name="clusterArn")
    def cluster_arn(self) -> str:
        """The AWS generated ARN for the Cluster resource.

        stability
        :stability: experimental

        Example::
            # Example may have issues. See https://github.com/aws/jsii/issues/826
            arn:aws:eks:us-west-2666666666666cluster / prod
        """
        return jsii.get(self, "clusterArn")

    @property
    @jsii.member(jsii_name="clusterCertificateAuthorityData")
    def cluster_certificate_authority_data(self) -> str:
        """The certificate-authority-data for your cluster.

        stability
        :stability: experimental
        """
        return jsii.get(self, "clusterCertificateAuthorityData")

    @property
    @jsii.member(jsii_name="clusterEndpoint")
    def cluster_endpoint(self) -> str:
        """The endpoint URL for the Cluster.

        This is the URL inside the kubeconfig file to use with kubectl

        stability
        :stability: experimental

        Example::
            # Example may have issues. See https://github.com/aws/jsii/issues/826
            https:
        """
        return jsii.get(self, "clusterEndpoint")

    @property
    @jsii.member(jsii_name="clusterName")
    def cluster_name(self) -> str:
        """The Name of the created EKS Cluster.

        stability
        :stability: experimental
        """
        return jsii.get(self, "clusterName")

    @property
    @jsii.member(jsii_name="connections")
    def connections(self) -> aws_cdk.aws_ec2.Connections:
        """Manages connection rules (Security Group Rules) for the cluster.

        stability
        :stability: experimental
        memberof:
        :memberof:: Cluster
        type:
        :type:: {ec2.Connections}
        """
        return jsii.get(self, "connections")

    @property
    @jsii.member(jsii_name="kubectlEnabled")
    def kubectl_enabled(self) -> bool:
        """Indicates if ``kubectl`` related operations can be performed on this cluster.

        stability
        :stability: experimental
        """
        return jsii.get(self, "kubectlEnabled")

    @property
    @jsii.member(jsii_name="role")
    def role(self) -> aws_cdk.aws_iam.IRole:
        """IAM role assumed by the EKS Control Plane.

        stability
        :stability: experimental
        """
        return jsii.get(self, "role")

    @property
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> aws_cdk.aws_ec2.IVpc:
        """The VPC in which this Cluster was created.

        stability
        :stability: experimental
        """
        return jsii.get(self, "vpc")

    @property
    @jsii.member(jsii_name="defaultCapacity")
    def default_capacity(self) -> typing.Optional[aws_cdk.aws_autoscaling.AutoScalingGroup]:
        """The auto scaling group that hosts the default capacity for this cluster. This will be ``undefined`` if the default capacity is set to 0.

        stability
        :stability: experimental
        """
        return jsii.get(self, "defaultCapacity")


class KubernetesResource(aws_cdk.core.Construct, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-eks.KubernetesResource"):
    """Represents a resource within the Kubernetes system.

    Alternatively, you can use ``cluster.addResource(resource[, resource, ...])``
    to define resources on this cluster.

    Applies/deletes the resources using ``kubectl`` in sync with the resource.

    stability
    :stability: experimental
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, cluster: "Cluster", manifest: typing.List[typing.Any]) -> None:
        """
        :param scope: -
        :param id: -
        :param props: -
        :param cluster: The EKS cluster to apply this configuration to. [disable-awslint:ref-via-interface]
        :param manifest: The resource manifest. Consists of any number of child resources. When the resource is created/updated, this manifest will be applied to the cluster through ``kubectl apply`` and when the resource or the stack is deleted, the manifest will be deleted through ``kubectl delete``.

        stability
        :stability: experimental
        """
        props = KubernetesResourceProps(cluster=cluster, manifest=manifest)

        jsii.create(KubernetesResource, self, [scope, id, props])

    @classproperty
    @jsii.member(jsii_name="RESOURCE_TYPE")
    def RESOURCE_TYPE(cls) -> str:
        """The CloudFormation reosurce type.

        stability
        :stability: experimental
        """
        return jsii.sget(cls, "RESOURCE_TYPE")


@jsii.data_type(jsii_type="@aws-cdk/aws-eks.KubernetesResourceProps", jsii_struct_bases=[], name_mapping={'cluster': 'cluster', 'manifest': 'manifest'})
class KubernetesResourceProps():
    def __init__(self, *, cluster: "Cluster", manifest: typing.List[typing.Any]):
        """
        :param cluster: The EKS cluster to apply this configuration to. [disable-awslint:ref-via-interface]
        :param manifest: The resource manifest. Consists of any number of child resources. When the resource is created/updated, this manifest will be applied to the cluster through ``kubectl apply`` and when the resource or the stack is deleted, the manifest will be deleted through ``kubectl delete``.

        stability
        :stability: experimental
        """
        self._values = {
            'cluster': cluster,
            'manifest': manifest,
        }

    @property
    def cluster(self) -> "Cluster":
        """The EKS cluster to apply this configuration to.

        [disable-awslint:ref-via-interface]

        stability
        :stability: experimental
        """
        return self._values.get('cluster')

    @property
    def manifest(self) -> typing.List[typing.Any]:
        """The resource manifest.

        Consists of any number of child resources.

        When the resource is created/updated, this manifest will be applied to the
        cluster through ``kubectl apply`` and when the resource or the stack is
        deleted, the manifest will be deleted through ``kubectl delete``.

        stability
        :stability: experimental

        Example::
            # Example may have issues. See https://github.com/aws/jsii/issues/826
            apiVersion: 'v1',
                  kind"Pod" , metadataname: 'mypod'spec: {
                    containers: [ { name: 'hello', image: 'paulbouwer/hello-kubernetes:1.5', ports: [ { containerPort: 8080 } ] } ]
                  }
        """
        return self._values.get('manifest')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'KubernetesResourceProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


@jsii.data_type(jsii_type="@aws-cdk/aws-eks.Mapping", jsii_struct_bases=[], name_mapping={'groups': 'groups', 'username': 'username'})
class Mapping():
    def __init__(self, *, groups: typing.List[str], username: typing.Optional[str]=None):
        """
        :param groups: A list of groups within Kubernetes to which the role is mapped.
        :param username: The user name within Kubernetes to map to the IAM role. Default: - By default, the user name is the ARN of the IAM role.

        stability
        :stability: experimental
        """
        self._values = {
            'groups': groups,
        }
        if username is not None: self._values["username"] = username

    @property
    def groups(self) -> typing.List[str]:
        """A list of groups within Kubernetes to which the role is mapped.

        see
        :see: https://kubernetes.io/docs/reference/access-authn-authz/rbac/#default-roles-and-role-bindings
        stability
        :stability: experimental
        """
        return self._values.get('groups')

    @property
    def username(self) -> typing.Optional[str]:
        """The user name within Kubernetes to map to the IAM role.

        default
        :default: - By default, the user name is the ARN of the IAM role.

        stability
        :stability: experimental
        """
        return self._values.get('username')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'Mapping(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


@jsii.enum(jsii_type="@aws-cdk/aws-eks.NodeType")
class NodeType(enum.Enum):
    """Whether the worker nodes should support GPU or just standard instances.

    stability
    :stability: experimental
    """
    STANDARD = "STANDARD"
    """Standard instances.

    stability
    :stability: experimental
    """
    GPU = "GPU"
    """GPU instances.

    stability
    :stability: experimental
    """

__all__ = ["AutoScalingGroupOptions", "AwsAuth", "AwsAuthProps", "BootstrapOptions", "CapacityOptions", "CfnCluster", "CfnClusterProps", "Cluster", "ClusterAttributes", "ClusterProps", "EksOptimizedImage", "EksOptimizedImageProps", "ICluster", "KubernetesResource", "KubernetesResourceProps", "Mapping", "NodeType", "__jsii_assembly__"]

publication.publish()
