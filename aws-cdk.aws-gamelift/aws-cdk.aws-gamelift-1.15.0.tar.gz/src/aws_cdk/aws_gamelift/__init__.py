import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.core
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-gamelift", "1.15.0", __name__, "aws-gamelift@1.15.0.jsii.tgz")
class CfnAlias(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-gamelift.CfnAlias"):
    """A CloudFormation ``AWS::GameLift::Alias``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-gamelift-alias.html
    cloudformationResource:
    :cloudformationResource:: AWS::GameLift::Alias
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, name: str, routing_strategy: typing.Union["RoutingStrategyProperty", aws_cdk.core.IResolvable], description: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::GameLift::Alias``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param name: ``AWS::GameLift::Alias.Name``.
        :param routing_strategy: ``AWS::GameLift::Alias.RoutingStrategy``.
        :param description: ``AWS::GameLift::Alias.Description``.
        """
        props = CfnAliasProps(name=name, routing_strategy=routing_strategy, description=description)

        jsii.create(CfnAlias, self, [scope, id, props])

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
    @jsii.member(jsii_name="name")
    def name(self) -> str:
        """``AWS::GameLift::Alias.Name``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-gamelift-alias.html#cfn-gamelift-alias-name
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: str):
        return jsii.set(self, "name", value)

    @property
    @jsii.member(jsii_name="routingStrategy")
    def routing_strategy(self) -> typing.Union["RoutingStrategyProperty", aws_cdk.core.IResolvable]:
        """``AWS::GameLift::Alias.RoutingStrategy``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-gamelift-alias.html#cfn-gamelift-alias-routingstrategy
        """
        return jsii.get(self, "routingStrategy")

    @routing_strategy.setter
    def routing_strategy(self, value: typing.Union["RoutingStrategyProperty", aws_cdk.core.IResolvable]):
        return jsii.set(self, "routingStrategy", value)

    @property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[str]:
        """``AWS::GameLift::Alias.Description``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-gamelift-alias.html#cfn-gamelift-alias-description
        """
        return jsii.get(self, "description")

    @description.setter
    def description(self, value: typing.Optional[str]):
        return jsii.set(self, "description", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-gamelift.CfnAlias.RoutingStrategyProperty", jsii_struct_bases=[], name_mapping={'type': 'type', 'fleet_id': 'fleetId', 'message': 'message'})
    class RoutingStrategyProperty():
        def __init__(self, *, type: str, fleet_id: typing.Optional[str]=None, message: typing.Optional[str]=None):
            """
            :param type: ``CfnAlias.RoutingStrategyProperty.Type``.
            :param fleet_id: ``CfnAlias.RoutingStrategyProperty.FleetId``.
            :param message: ``CfnAlias.RoutingStrategyProperty.Message``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-gamelift-alias-routingstrategy.html
            """
            self._values = {
                'type': type,
            }
            if fleet_id is not None: self._values["fleet_id"] = fleet_id
            if message is not None: self._values["message"] = message

        @property
        def type(self) -> str:
            """``CfnAlias.RoutingStrategyProperty.Type``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-gamelift-alias-routingstrategy.html#cfn-gamelift-alias-routingstrategy-type
            """
            return self._values.get('type')

        @property
        def fleet_id(self) -> typing.Optional[str]:
            """``CfnAlias.RoutingStrategyProperty.FleetId``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-gamelift-alias-routingstrategy.html#cfn-gamelift-alias-routingstrategy-fleetid
            """
            return self._values.get('fleet_id')

        @property
        def message(self) -> typing.Optional[str]:
            """``CfnAlias.RoutingStrategyProperty.Message``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-gamelift-alias-routingstrategy.html#cfn-gamelift-alias-routingstrategy-message
            """
            return self._values.get('message')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'RoutingStrategyProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



@jsii.data_type(jsii_type="@aws-cdk/aws-gamelift.CfnAliasProps", jsii_struct_bases=[], name_mapping={'name': 'name', 'routing_strategy': 'routingStrategy', 'description': 'description'})
class CfnAliasProps():
    def __init__(self, *, name: str, routing_strategy: typing.Union["CfnAlias.RoutingStrategyProperty", aws_cdk.core.IResolvable], description: typing.Optional[str]=None):
        """Properties for defining a ``AWS::GameLift::Alias``.

        :param name: ``AWS::GameLift::Alias.Name``.
        :param routing_strategy: ``AWS::GameLift::Alias.RoutingStrategy``.
        :param description: ``AWS::GameLift::Alias.Description``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-gamelift-alias.html
        """
        self._values = {
            'name': name,
            'routing_strategy': routing_strategy,
        }
        if description is not None: self._values["description"] = description

    @property
    def name(self) -> str:
        """``AWS::GameLift::Alias.Name``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-gamelift-alias.html#cfn-gamelift-alias-name
        """
        return self._values.get('name')

    @property
    def routing_strategy(self) -> typing.Union["CfnAlias.RoutingStrategyProperty", aws_cdk.core.IResolvable]:
        """``AWS::GameLift::Alias.RoutingStrategy``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-gamelift-alias.html#cfn-gamelift-alias-routingstrategy
        """
        return self._values.get('routing_strategy')

    @property
    def description(self) -> typing.Optional[str]:
        """``AWS::GameLift::Alias.Description``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-gamelift-alias.html#cfn-gamelift-alias-description
        """
        return self._values.get('description')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnAliasProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnBuild(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-gamelift.CfnBuild"):
    """A CloudFormation ``AWS::GameLift::Build``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-gamelift-build.html
    cloudformationResource:
    :cloudformationResource:: AWS::GameLift::Build
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, name: typing.Optional[str]=None, storage_location: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["S3LocationProperty"]]]=None, version: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::GameLift::Build``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param name: ``AWS::GameLift::Build.Name``.
        :param storage_location: ``AWS::GameLift::Build.StorageLocation``.
        :param version: ``AWS::GameLift::Build.Version``.
        """
        props = CfnBuildProps(name=name, storage_location=storage_location, version=version)

        jsii.create(CfnBuild, self, [scope, id, props])

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
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[str]:
        """``AWS::GameLift::Build.Name``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-gamelift-build.html#cfn-gamelift-build-name
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: typing.Optional[str]):
        return jsii.set(self, "name", value)

    @property
    @jsii.member(jsii_name="storageLocation")
    def storage_location(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["S3LocationProperty"]]]:
        """``AWS::GameLift::Build.StorageLocation``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-gamelift-build.html#cfn-gamelift-build-storagelocation
        """
        return jsii.get(self, "storageLocation")

    @storage_location.setter
    def storage_location(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["S3LocationProperty"]]]):
        return jsii.set(self, "storageLocation", value)

    @property
    @jsii.member(jsii_name="version")
    def version(self) -> typing.Optional[str]:
        """``AWS::GameLift::Build.Version``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-gamelift-build.html#cfn-gamelift-build-version
        """
        return jsii.get(self, "version")

    @version.setter
    def version(self, value: typing.Optional[str]):
        return jsii.set(self, "version", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-gamelift.CfnBuild.S3LocationProperty", jsii_struct_bases=[], name_mapping={'bucket': 'bucket', 'key': 'key', 'role_arn': 'roleArn'})
    class S3LocationProperty():
        def __init__(self, *, bucket: str, key: str, role_arn: str):
            """
            :param bucket: ``CfnBuild.S3LocationProperty.Bucket``.
            :param key: ``CfnBuild.S3LocationProperty.Key``.
            :param role_arn: ``CfnBuild.S3LocationProperty.RoleArn``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-gamelift-build-storagelocation.html
            """
            self._values = {
                'bucket': bucket,
                'key': key,
                'role_arn': role_arn,
            }

        @property
        def bucket(self) -> str:
            """``CfnBuild.S3LocationProperty.Bucket``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-gamelift-build-storagelocation.html#cfn-gamelift-build-storage-bucket
            """
            return self._values.get('bucket')

        @property
        def key(self) -> str:
            """``CfnBuild.S3LocationProperty.Key``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-gamelift-build-storagelocation.html#cfn-gamelift-build-storage-key
            """
            return self._values.get('key')

        @property
        def role_arn(self) -> str:
            """``CfnBuild.S3LocationProperty.RoleArn``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-gamelift-build-storagelocation.html#cfn-gamelift-build-storage-rolearn
            """
            return self._values.get('role_arn')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'S3LocationProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



@jsii.data_type(jsii_type="@aws-cdk/aws-gamelift.CfnBuildProps", jsii_struct_bases=[], name_mapping={'name': 'name', 'storage_location': 'storageLocation', 'version': 'version'})
class CfnBuildProps():
    def __init__(self, *, name: typing.Optional[str]=None, storage_location: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnBuild.S3LocationProperty"]]]=None, version: typing.Optional[str]=None):
        """Properties for defining a ``AWS::GameLift::Build``.

        :param name: ``AWS::GameLift::Build.Name``.
        :param storage_location: ``AWS::GameLift::Build.StorageLocation``.
        :param version: ``AWS::GameLift::Build.Version``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-gamelift-build.html
        """
        self._values = {
        }
        if name is not None: self._values["name"] = name
        if storage_location is not None: self._values["storage_location"] = storage_location
        if version is not None: self._values["version"] = version

    @property
    def name(self) -> typing.Optional[str]:
        """``AWS::GameLift::Build.Name``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-gamelift-build.html#cfn-gamelift-build-name
        """
        return self._values.get('name')

    @property
    def storage_location(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnBuild.S3LocationProperty"]]]:
        """``AWS::GameLift::Build.StorageLocation``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-gamelift-build.html#cfn-gamelift-build-storagelocation
        """
        return self._values.get('storage_location')

    @property
    def version(self) -> typing.Optional[str]:
        """``AWS::GameLift::Build.Version``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-gamelift-build.html#cfn-gamelift-build-version
        """
        return self._values.get('version')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnBuildProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnFleet(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-gamelift.CfnFleet"):
    """A CloudFormation ``AWS::GameLift::Fleet``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-gamelift-fleet.html
    cloudformationResource:
    :cloudformationResource:: AWS::GameLift::Fleet
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, build_id: str, desired_ec2_instances: jsii.Number, ec2_instance_type: str, name: str, server_launch_path: str, description: typing.Optional[str]=None, ec2_inbound_permissions: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "IpPermissionProperty"]]]]]=None, log_paths: typing.Optional[typing.List[str]]=None, max_size: typing.Optional[jsii.Number]=None, min_size: typing.Optional[jsii.Number]=None, server_launch_parameters: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::GameLift::Fleet``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param build_id: ``AWS::GameLift::Fleet.BuildId``.
        :param desired_ec2_instances: ``AWS::GameLift::Fleet.DesiredEC2Instances``.
        :param ec2_instance_type: ``AWS::GameLift::Fleet.EC2InstanceType``.
        :param name: ``AWS::GameLift::Fleet.Name``.
        :param server_launch_path: ``AWS::GameLift::Fleet.ServerLaunchPath``.
        :param description: ``AWS::GameLift::Fleet.Description``.
        :param ec2_inbound_permissions: ``AWS::GameLift::Fleet.EC2InboundPermissions``.
        :param log_paths: ``AWS::GameLift::Fleet.LogPaths``.
        :param max_size: ``AWS::GameLift::Fleet.MaxSize``.
        :param min_size: ``AWS::GameLift::Fleet.MinSize``.
        :param server_launch_parameters: ``AWS::GameLift::Fleet.ServerLaunchParameters``.
        """
        props = CfnFleetProps(build_id=build_id, desired_ec2_instances=desired_ec2_instances, ec2_instance_type=ec2_instance_type, name=name, server_launch_path=server_launch_path, description=description, ec2_inbound_permissions=ec2_inbound_permissions, log_paths=log_paths, max_size=max_size, min_size=min_size, server_launch_parameters=server_launch_parameters)

        jsii.create(CfnFleet, self, [scope, id, props])

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
    @jsii.member(jsii_name="buildId")
    def build_id(self) -> str:
        """``AWS::GameLift::Fleet.BuildId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-gamelift-fleet.html#cfn-gamelift-fleet-buildid
        """
        return jsii.get(self, "buildId")

    @build_id.setter
    def build_id(self, value: str):
        return jsii.set(self, "buildId", value)

    @property
    @jsii.member(jsii_name="desiredEc2Instances")
    def desired_ec2_instances(self) -> jsii.Number:
        """``AWS::GameLift::Fleet.DesiredEC2Instances``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-gamelift-fleet.html#cfn-gamelift-fleet-desiredec2instances
        """
        return jsii.get(self, "desiredEc2Instances")

    @desired_ec2_instances.setter
    def desired_ec2_instances(self, value: jsii.Number):
        return jsii.set(self, "desiredEc2Instances", value)

    @property
    @jsii.member(jsii_name="ec2InstanceType")
    def ec2_instance_type(self) -> str:
        """``AWS::GameLift::Fleet.EC2InstanceType``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-gamelift-fleet.html#cfn-gamelift-fleet-ec2instancetype
        """
        return jsii.get(self, "ec2InstanceType")

    @ec2_instance_type.setter
    def ec2_instance_type(self, value: str):
        return jsii.set(self, "ec2InstanceType", value)

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> str:
        """``AWS::GameLift::Fleet.Name``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-gamelift-fleet.html#cfn-gamelift-fleet-name
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: str):
        return jsii.set(self, "name", value)

    @property
    @jsii.member(jsii_name="serverLaunchPath")
    def server_launch_path(self) -> str:
        """``AWS::GameLift::Fleet.ServerLaunchPath``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-gamelift-fleet.html#cfn-gamelift-fleet-serverlaunchpath
        """
        return jsii.get(self, "serverLaunchPath")

    @server_launch_path.setter
    def server_launch_path(self, value: str):
        return jsii.set(self, "serverLaunchPath", value)

    @property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[str]:
        """``AWS::GameLift::Fleet.Description``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-gamelift-fleet.html#cfn-gamelift-fleet-description
        """
        return jsii.get(self, "description")

    @description.setter
    def description(self, value: typing.Optional[str]):
        return jsii.set(self, "description", value)

    @property
    @jsii.member(jsii_name="ec2InboundPermissions")
    def ec2_inbound_permissions(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "IpPermissionProperty"]]]]]:
        """``AWS::GameLift::Fleet.EC2InboundPermissions``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-gamelift-fleet.html#cfn-gamelift-fleet-ec2inboundpermissions
        """
        return jsii.get(self, "ec2InboundPermissions")

    @ec2_inbound_permissions.setter
    def ec2_inbound_permissions(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "IpPermissionProperty"]]]]]):
        return jsii.set(self, "ec2InboundPermissions", value)

    @property
    @jsii.member(jsii_name="logPaths")
    def log_paths(self) -> typing.Optional[typing.List[str]]:
        """``AWS::GameLift::Fleet.LogPaths``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-gamelift-fleet.html#cfn-gamelift-fleet-logpaths
        """
        return jsii.get(self, "logPaths")

    @log_paths.setter
    def log_paths(self, value: typing.Optional[typing.List[str]]):
        return jsii.set(self, "logPaths", value)

    @property
    @jsii.member(jsii_name="maxSize")
    def max_size(self) -> typing.Optional[jsii.Number]:
        """``AWS::GameLift::Fleet.MaxSize``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-gamelift-fleet.html#cfn-gamelift-fleet-maxsize
        """
        return jsii.get(self, "maxSize")

    @max_size.setter
    def max_size(self, value: typing.Optional[jsii.Number]):
        return jsii.set(self, "maxSize", value)

    @property
    @jsii.member(jsii_name="minSize")
    def min_size(self) -> typing.Optional[jsii.Number]:
        """``AWS::GameLift::Fleet.MinSize``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-gamelift-fleet.html#cfn-gamelift-fleet-minsize
        """
        return jsii.get(self, "minSize")

    @min_size.setter
    def min_size(self, value: typing.Optional[jsii.Number]):
        return jsii.set(self, "minSize", value)

    @property
    @jsii.member(jsii_name="serverLaunchParameters")
    def server_launch_parameters(self) -> typing.Optional[str]:
        """``AWS::GameLift::Fleet.ServerLaunchParameters``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-gamelift-fleet.html#cfn-gamelift-fleet-serverlaunchparameters
        """
        return jsii.get(self, "serverLaunchParameters")

    @server_launch_parameters.setter
    def server_launch_parameters(self, value: typing.Optional[str]):
        return jsii.set(self, "serverLaunchParameters", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-gamelift.CfnFleet.IpPermissionProperty", jsii_struct_bases=[], name_mapping={'from_port': 'fromPort', 'ip_range': 'ipRange', 'protocol': 'protocol', 'to_port': 'toPort'})
    class IpPermissionProperty():
        def __init__(self, *, from_port: jsii.Number, ip_range: str, protocol: str, to_port: jsii.Number):
            """
            :param from_port: ``CfnFleet.IpPermissionProperty.FromPort``.
            :param ip_range: ``CfnFleet.IpPermissionProperty.IpRange``.
            :param protocol: ``CfnFleet.IpPermissionProperty.Protocol``.
            :param to_port: ``CfnFleet.IpPermissionProperty.ToPort``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-gamelift-fleet-ec2inboundpermission.html
            """
            self._values = {
                'from_port': from_port,
                'ip_range': ip_range,
                'protocol': protocol,
                'to_port': to_port,
            }

        @property
        def from_port(self) -> jsii.Number:
            """``CfnFleet.IpPermissionProperty.FromPort``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-gamelift-fleet-ec2inboundpermission.html#cfn-gamelift-fleet-ec2inboundpermissions-fromport
            """
            return self._values.get('from_port')

        @property
        def ip_range(self) -> str:
            """``CfnFleet.IpPermissionProperty.IpRange``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-gamelift-fleet-ec2inboundpermission.html#cfn-gamelift-fleet-ec2inboundpermissions-iprange
            """
            return self._values.get('ip_range')

        @property
        def protocol(self) -> str:
            """``CfnFleet.IpPermissionProperty.Protocol``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-gamelift-fleet-ec2inboundpermission.html#cfn-gamelift-fleet-ec2inboundpermissions-protocol
            """
            return self._values.get('protocol')

        @property
        def to_port(self) -> jsii.Number:
            """``CfnFleet.IpPermissionProperty.ToPort``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-gamelift-fleet-ec2inboundpermission.html#cfn-gamelift-fleet-ec2inboundpermissions-toport
            """
            return self._values.get('to_port')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'IpPermissionProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



@jsii.data_type(jsii_type="@aws-cdk/aws-gamelift.CfnFleetProps", jsii_struct_bases=[], name_mapping={'build_id': 'buildId', 'desired_ec2_instances': 'desiredEc2Instances', 'ec2_instance_type': 'ec2InstanceType', 'name': 'name', 'server_launch_path': 'serverLaunchPath', 'description': 'description', 'ec2_inbound_permissions': 'ec2InboundPermissions', 'log_paths': 'logPaths', 'max_size': 'maxSize', 'min_size': 'minSize', 'server_launch_parameters': 'serverLaunchParameters'})
class CfnFleetProps():
    def __init__(self, *, build_id: str, desired_ec2_instances: jsii.Number, ec2_instance_type: str, name: str, server_launch_path: str, description: typing.Optional[str]=None, ec2_inbound_permissions: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnFleet.IpPermissionProperty"]]]]]=None, log_paths: typing.Optional[typing.List[str]]=None, max_size: typing.Optional[jsii.Number]=None, min_size: typing.Optional[jsii.Number]=None, server_launch_parameters: typing.Optional[str]=None):
        """Properties for defining a ``AWS::GameLift::Fleet``.

        :param build_id: ``AWS::GameLift::Fleet.BuildId``.
        :param desired_ec2_instances: ``AWS::GameLift::Fleet.DesiredEC2Instances``.
        :param ec2_instance_type: ``AWS::GameLift::Fleet.EC2InstanceType``.
        :param name: ``AWS::GameLift::Fleet.Name``.
        :param server_launch_path: ``AWS::GameLift::Fleet.ServerLaunchPath``.
        :param description: ``AWS::GameLift::Fleet.Description``.
        :param ec2_inbound_permissions: ``AWS::GameLift::Fleet.EC2InboundPermissions``.
        :param log_paths: ``AWS::GameLift::Fleet.LogPaths``.
        :param max_size: ``AWS::GameLift::Fleet.MaxSize``.
        :param min_size: ``AWS::GameLift::Fleet.MinSize``.
        :param server_launch_parameters: ``AWS::GameLift::Fleet.ServerLaunchParameters``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-gamelift-fleet.html
        """
        self._values = {
            'build_id': build_id,
            'desired_ec2_instances': desired_ec2_instances,
            'ec2_instance_type': ec2_instance_type,
            'name': name,
            'server_launch_path': server_launch_path,
        }
        if description is not None: self._values["description"] = description
        if ec2_inbound_permissions is not None: self._values["ec2_inbound_permissions"] = ec2_inbound_permissions
        if log_paths is not None: self._values["log_paths"] = log_paths
        if max_size is not None: self._values["max_size"] = max_size
        if min_size is not None: self._values["min_size"] = min_size
        if server_launch_parameters is not None: self._values["server_launch_parameters"] = server_launch_parameters

    @property
    def build_id(self) -> str:
        """``AWS::GameLift::Fleet.BuildId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-gamelift-fleet.html#cfn-gamelift-fleet-buildid
        """
        return self._values.get('build_id')

    @property
    def desired_ec2_instances(self) -> jsii.Number:
        """``AWS::GameLift::Fleet.DesiredEC2Instances``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-gamelift-fleet.html#cfn-gamelift-fleet-desiredec2instances
        """
        return self._values.get('desired_ec2_instances')

    @property
    def ec2_instance_type(self) -> str:
        """``AWS::GameLift::Fleet.EC2InstanceType``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-gamelift-fleet.html#cfn-gamelift-fleet-ec2instancetype
        """
        return self._values.get('ec2_instance_type')

    @property
    def name(self) -> str:
        """``AWS::GameLift::Fleet.Name``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-gamelift-fleet.html#cfn-gamelift-fleet-name
        """
        return self._values.get('name')

    @property
    def server_launch_path(self) -> str:
        """``AWS::GameLift::Fleet.ServerLaunchPath``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-gamelift-fleet.html#cfn-gamelift-fleet-serverlaunchpath
        """
        return self._values.get('server_launch_path')

    @property
    def description(self) -> typing.Optional[str]:
        """``AWS::GameLift::Fleet.Description``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-gamelift-fleet.html#cfn-gamelift-fleet-description
        """
        return self._values.get('description')

    @property
    def ec2_inbound_permissions(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnFleet.IpPermissionProperty"]]]]]:
        """``AWS::GameLift::Fleet.EC2InboundPermissions``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-gamelift-fleet.html#cfn-gamelift-fleet-ec2inboundpermissions
        """
        return self._values.get('ec2_inbound_permissions')

    @property
    def log_paths(self) -> typing.Optional[typing.List[str]]:
        """``AWS::GameLift::Fleet.LogPaths``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-gamelift-fleet.html#cfn-gamelift-fleet-logpaths
        """
        return self._values.get('log_paths')

    @property
    def max_size(self) -> typing.Optional[jsii.Number]:
        """``AWS::GameLift::Fleet.MaxSize``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-gamelift-fleet.html#cfn-gamelift-fleet-maxsize
        """
        return self._values.get('max_size')

    @property
    def min_size(self) -> typing.Optional[jsii.Number]:
        """``AWS::GameLift::Fleet.MinSize``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-gamelift-fleet.html#cfn-gamelift-fleet-minsize
        """
        return self._values.get('min_size')

    @property
    def server_launch_parameters(self) -> typing.Optional[str]:
        """``AWS::GameLift::Fleet.ServerLaunchParameters``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-gamelift-fleet.html#cfn-gamelift-fleet-serverlaunchparameters
        """
        return self._values.get('server_launch_parameters')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnFleetProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


__all__ = ["CfnAlias", "CfnAliasProps", "CfnBuild", "CfnBuildProps", "CfnFleet", "CfnFleetProps", "__jsii_assembly__"]

publication.publish()
