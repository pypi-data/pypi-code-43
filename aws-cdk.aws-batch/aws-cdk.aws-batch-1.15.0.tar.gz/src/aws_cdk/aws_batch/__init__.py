import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.core
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-batch", "1.15.0", __name__, "aws-batch@1.15.0.jsii.tgz")
class CfnComputeEnvironment(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-batch.CfnComputeEnvironment"):
    """A CloudFormation ``AWS::Batch::ComputeEnvironment``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-computeenvironment.html
    cloudformationResource:
    :cloudformationResource:: AWS::Batch::ComputeEnvironment
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, service_role: str, type: str, compute_environment_name: typing.Optional[str]=None, compute_resources: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["ComputeResourcesProperty"]]]=None, state: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::Batch::ComputeEnvironment``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param service_role: ``AWS::Batch::ComputeEnvironment.ServiceRole``.
        :param type: ``AWS::Batch::ComputeEnvironment.Type``.
        :param compute_environment_name: ``AWS::Batch::ComputeEnvironment.ComputeEnvironmentName``.
        :param compute_resources: ``AWS::Batch::ComputeEnvironment.ComputeResources``.
        :param state: ``AWS::Batch::ComputeEnvironment.State``.
        """
        props = CfnComputeEnvironmentProps(service_role=service_role, type=type, compute_environment_name=compute_environment_name, compute_resources=compute_resources, state=state)

        jsii.create(CfnComputeEnvironment, self, [scope, id, props])

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
    @jsii.member(jsii_name="serviceRole")
    def service_role(self) -> str:
        """``AWS::Batch::ComputeEnvironment.ServiceRole``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-computeenvironment.html#cfn-batch-computeenvironment-servicerole
        """
        return jsii.get(self, "serviceRole")

    @service_role.setter
    def service_role(self, value: str):
        return jsii.set(self, "serviceRole", value)

    @property
    @jsii.member(jsii_name="type")
    def type(self) -> str:
        """``AWS::Batch::ComputeEnvironment.Type``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-computeenvironment.html#cfn-batch-computeenvironment-type
        """
        return jsii.get(self, "type")

    @type.setter
    def type(self, value: str):
        return jsii.set(self, "type", value)

    @property
    @jsii.member(jsii_name="computeEnvironmentName")
    def compute_environment_name(self) -> typing.Optional[str]:
        """``AWS::Batch::ComputeEnvironment.ComputeEnvironmentName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-computeenvironment.html#cfn-batch-computeenvironment-computeenvironmentname
        """
        return jsii.get(self, "computeEnvironmentName")

    @compute_environment_name.setter
    def compute_environment_name(self, value: typing.Optional[str]):
        return jsii.set(self, "computeEnvironmentName", value)

    @property
    @jsii.member(jsii_name="computeResources")
    def compute_resources(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["ComputeResourcesProperty"]]]:
        """``AWS::Batch::ComputeEnvironment.ComputeResources``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-computeenvironment.html#cfn-batch-computeenvironment-computeresources
        """
        return jsii.get(self, "computeResources")

    @compute_resources.setter
    def compute_resources(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["ComputeResourcesProperty"]]]):
        return jsii.set(self, "computeResources", value)

    @property
    @jsii.member(jsii_name="state")
    def state(self) -> typing.Optional[str]:
        """``AWS::Batch::ComputeEnvironment.State``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-computeenvironment.html#cfn-batch-computeenvironment-state
        """
        return jsii.get(self, "state")

    @state.setter
    def state(self, value: typing.Optional[str]):
        return jsii.set(self, "state", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-batch.CfnComputeEnvironment.ComputeResourcesProperty", jsii_struct_bases=[], name_mapping={'instance_role': 'instanceRole', 'instance_types': 'instanceTypes', 'maxv_cpus': 'maxvCpus', 'minv_cpus': 'minvCpus', 'subnets': 'subnets', 'type': 'type', 'allocation_strategy': 'allocationStrategy', 'bid_percentage': 'bidPercentage', 'desiredv_cpus': 'desiredvCpus', 'ec2_key_pair': 'ec2KeyPair', 'image_id': 'imageId', 'launch_template': 'launchTemplate', 'placement_group': 'placementGroup', 'security_group_ids': 'securityGroupIds', 'spot_iam_fleet_role': 'spotIamFleetRole', 'tags': 'tags'})
    class ComputeResourcesProperty():
        def __init__(self, *, instance_role: str, instance_types: typing.List[str], maxv_cpus: jsii.Number, minv_cpus: jsii.Number, subnets: typing.List[str], type: str, allocation_strategy: typing.Optional[str]=None, bid_percentage: typing.Optional[jsii.Number]=None, desiredv_cpus: typing.Optional[jsii.Number]=None, ec2_key_pair: typing.Optional[str]=None, image_id: typing.Optional[str]=None, launch_template: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnComputeEnvironment.LaunchTemplateSpecificationProperty"]]]=None, placement_group: typing.Optional[str]=None, security_group_ids: typing.Optional[typing.List[str]]=None, spot_iam_fleet_role: typing.Optional[str]=None, tags: typing.Any=None):
            """
            :param instance_role: ``CfnComputeEnvironment.ComputeResourcesProperty.InstanceRole``.
            :param instance_types: ``CfnComputeEnvironment.ComputeResourcesProperty.InstanceTypes``.
            :param maxv_cpus: ``CfnComputeEnvironment.ComputeResourcesProperty.MaxvCpus``.
            :param minv_cpus: ``CfnComputeEnvironment.ComputeResourcesProperty.MinvCpus``.
            :param subnets: ``CfnComputeEnvironment.ComputeResourcesProperty.Subnets``.
            :param type: ``CfnComputeEnvironment.ComputeResourcesProperty.Type``.
            :param allocation_strategy: ``CfnComputeEnvironment.ComputeResourcesProperty.AllocationStrategy``.
            :param bid_percentage: ``CfnComputeEnvironment.ComputeResourcesProperty.BidPercentage``.
            :param desiredv_cpus: ``CfnComputeEnvironment.ComputeResourcesProperty.DesiredvCpus``.
            :param ec2_key_pair: ``CfnComputeEnvironment.ComputeResourcesProperty.Ec2KeyPair``.
            :param image_id: ``CfnComputeEnvironment.ComputeResourcesProperty.ImageId``.
            :param launch_template: ``CfnComputeEnvironment.ComputeResourcesProperty.LaunchTemplate``.
            :param placement_group: ``CfnComputeEnvironment.ComputeResourcesProperty.PlacementGroup``.
            :param security_group_ids: ``CfnComputeEnvironment.ComputeResourcesProperty.SecurityGroupIds``.
            :param spot_iam_fleet_role: ``CfnComputeEnvironment.ComputeResourcesProperty.SpotIamFleetRole``.
            :param tags: ``CfnComputeEnvironment.ComputeResourcesProperty.Tags``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html
            """
            self._values = {
                'instance_role': instance_role,
                'instance_types': instance_types,
                'maxv_cpus': maxv_cpus,
                'minv_cpus': minv_cpus,
                'subnets': subnets,
                'type': type,
            }
            if allocation_strategy is not None: self._values["allocation_strategy"] = allocation_strategy
            if bid_percentage is not None: self._values["bid_percentage"] = bid_percentage
            if desiredv_cpus is not None: self._values["desiredv_cpus"] = desiredv_cpus
            if ec2_key_pair is not None: self._values["ec2_key_pair"] = ec2_key_pair
            if image_id is not None: self._values["image_id"] = image_id
            if launch_template is not None: self._values["launch_template"] = launch_template
            if placement_group is not None: self._values["placement_group"] = placement_group
            if security_group_ids is not None: self._values["security_group_ids"] = security_group_ids
            if spot_iam_fleet_role is not None: self._values["spot_iam_fleet_role"] = spot_iam_fleet_role
            if tags is not None: self._values["tags"] = tags

        @property
        def instance_role(self) -> str:
            """``CfnComputeEnvironment.ComputeResourcesProperty.InstanceRole``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-instancerole
            """
            return self._values.get('instance_role')

        @property
        def instance_types(self) -> typing.List[str]:
            """``CfnComputeEnvironment.ComputeResourcesProperty.InstanceTypes``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-instancetypes
            """
            return self._values.get('instance_types')

        @property
        def maxv_cpus(self) -> jsii.Number:
            """``CfnComputeEnvironment.ComputeResourcesProperty.MaxvCpus``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-maxvcpus
            """
            return self._values.get('maxv_cpus')

        @property
        def minv_cpus(self) -> jsii.Number:
            """``CfnComputeEnvironment.ComputeResourcesProperty.MinvCpus``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-minvcpus
            """
            return self._values.get('minv_cpus')

        @property
        def subnets(self) -> typing.List[str]:
            """``CfnComputeEnvironment.ComputeResourcesProperty.Subnets``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-subnets
            """
            return self._values.get('subnets')

        @property
        def type(self) -> str:
            """``CfnComputeEnvironment.ComputeResourcesProperty.Type``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-type
            """
            return self._values.get('type')

        @property
        def allocation_strategy(self) -> typing.Optional[str]:
            """``CfnComputeEnvironment.ComputeResourcesProperty.AllocationStrategy``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-allocationstrategy
            """
            return self._values.get('allocation_strategy')

        @property
        def bid_percentage(self) -> typing.Optional[jsii.Number]:
            """``CfnComputeEnvironment.ComputeResourcesProperty.BidPercentage``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-bidpercentage
            """
            return self._values.get('bid_percentage')

        @property
        def desiredv_cpus(self) -> typing.Optional[jsii.Number]:
            """``CfnComputeEnvironment.ComputeResourcesProperty.DesiredvCpus``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-desiredvcpus
            """
            return self._values.get('desiredv_cpus')

        @property
        def ec2_key_pair(self) -> typing.Optional[str]:
            """``CfnComputeEnvironment.ComputeResourcesProperty.Ec2KeyPair``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-ec2keypair
            """
            return self._values.get('ec2_key_pair')

        @property
        def image_id(self) -> typing.Optional[str]:
            """``CfnComputeEnvironment.ComputeResourcesProperty.ImageId``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-imageid
            """
            return self._values.get('image_id')

        @property
        def launch_template(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnComputeEnvironment.LaunchTemplateSpecificationProperty"]]]:
            """``CfnComputeEnvironment.ComputeResourcesProperty.LaunchTemplate``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-launchtemplate
            """
            return self._values.get('launch_template')

        @property
        def placement_group(self) -> typing.Optional[str]:
            """``CfnComputeEnvironment.ComputeResourcesProperty.PlacementGroup``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-placementgroup
            """
            return self._values.get('placement_group')

        @property
        def security_group_ids(self) -> typing.Optional[typing.List[str]]:
            """``CfnComputeEnvironment.ComputeResourcesProperty.SecurityGroupIds``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-securitygroupids
            """
            return self._values.get('security_group_ids')

        @property
        def spot_iam_fleet_role(self) -> typing.Optional[str]:
            """``CfnComputeEnvironment.ComputeResourcesProperty.SpotIamFleetRole``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-spotiamfleetrole
            """
            return self._values.get('spot_iam_fleet_role')

        @property
        def tags(self) -> typing.Any:
            """``CfnComputeEnvironment.ComputeResourcesProperty.Tags``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-tags
            """
            return self._values.get('tags')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'ComputeResourcesProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-batch.CfnComputeEnvironment.LaunchTemplateSpecificationProperty", jsii_struct_bases=[], name_mapping={'launch_template_id': 'launchTemplateId', 'launch_template_name': 'launchTemplateName', 'version': 'version'})
    class LaunchTemplateSpecificationProperty():
        def __init__(self, *, launch_template_id: typing.Optional[str]=None, launch_template_name: typing.Optional[str]=None, version: typing.Optional[str]=None):
            """
            :param launch_template_id: ``CfnComputeEnvironment.LaunchTemplateSpecificationProperty.LaunchTemplateId``.
            :param launch_template_name: ``CfnComputeEnvironment.LaunchTemplateSpecificationProperty.LaunchTemplateName``.
            :param version: ``CfnComputeEnvironment.LaunchTemplateSpecificationProperty.Version``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-launchtemplatespecification.html
            """
            self._values = {
            }
            if launch_template_id is not None: self._values["launch_template_id"] = launch_template_id
            if launch_template_name is not None: self._values["launch_template_name"] = launch_template_name
            if version is not None: self._values["version"] = version

        @property
        def launch_template_id(self) -> typing.Optional[str]:
            """``CfnComputeEnvironment.LaunchTemplateSpecificationProperty.LaunchTemplateId``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-launchtemplatespecification.html#cfn-batch-computeenvironment-launchtemplatespecification-launchtemplateid
            """
            return self._values.get('launch_template_id')

        @property
        def launch_template_name(self) -> typing.Optional[str]:
            """``CfnComputeEnvironment.LaunchTemplateSpecificationProperty.LaunchTemplateName``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-launchtemplatespecification.html#cfn-batch-computeenvironment-launchtemplatespecification-launchtemplatename
            """
            return self._values.get('launch_template_name')

        @property
        def version(self) -> typing.Optional[str]:
            """``CfnComputeEnvironment.LaunchTemplateSpecificationProperty.Version``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-launchtemplatespecification.html#cfn-batch-computeenvironment-launchtemplatespecification-version
            """
            return self._values.get('version')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'LaunchTemplateSpecificationProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



@jsii.data_type(jsii_type="@aws-cdk/aws-batch.CfnComputeEnvironmentProps", jsii_struct_bases=[], name_mapping={'service_role': 'serviceRole', 'type': 'type', 'compute_environment_name': 'computeEnvironmentName', 'compute_resources': 'computeResources', 'state': 'state'})
class CfnComputeEnvironmentProps():
    def __init__(self, *, service_role: str, type: str, compute_environment_name: typing.Optional[str]=None, compute_resources: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnComputeEnvironment.ComputeResourcesProperty"]]]=None, state: typing.Optional[str]=None):
        """Properties for defining a ``AWS::Batch::ComputeEnvironment``.

        :param service_role: ``AWS::Batch::ComputeEnvironment.ServiceRole``.
        :param type: ``AWS::Batch::ComputeEnvironment.Type``.
        :param compute_environment_name: ``AWS::Batch::ComputeEnvironment.ComputeEnvironmentName``.
        :param compute_resources: ``AWS::Batch::ComputeEnvironment.ComputeResources``.
        :param state: ``AWS::Batch::ComputeEnvironment.State``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-computeenvironment.html
        """
        self._values = {
            'service_role': service_role,
            'type': type,
        }
        if compute_environment_name is not None: self._values["compute_environment_name"] = compute_environment_name
        if compute_resources is not None: self._values["compute_resources"] = compute_resources
        if state is not None: self._values["state"] = state

    @property
    def service_role(self) -> str:
        """``AWS::Batch::ComputeEnvironment.ServiceRole``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-computeenvironment.html#cfn-batch-computeenvironment-servicerole
        """
        return self._values.get('service_role')

    @property
    def type(self) -> str:
        """``AWS::Batch::ComputeEnvironment.Type``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-computeenvironment.html#cfn-batch-computeenvironment-type
        """
        return self._values.get('type')

    @property
    def compute_environment_name(self) -> typing.Optional[str]:
        """``AWS::Batch::ComputeEnvironment.ComputeEnvironmentName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-computeenvironment.html#cfn-batch-computeenvironment-computeenvironmentname
        """
        return self._values.get('compute_environment_name')

    @property
    def compute_resources(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnComputeEnvironment.ComputeResourcesProperty"]]]:
        """``AWS::Batch::ComputeEnvironment.ComputeResources``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-computeenvironment.html#cfn-batch-computeenvironment-computeresources
        """
        return self._values.get('compute_resources')

    @property
    def state(self) -> typing.Optional[str]:
        """``AWS::Batch::ComputeEnvironment.State``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-computeenvironment.html#cfn-batch-computeenvironment-state
        """
        return self._values.get('state')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnComputeEnvironmentProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnJobDefinition(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-batch.CfnJobDefinition"):
    """A CloudFormation ``AWS::Batch::JobDefinition``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobdefinition.html
    cloudformationResource:
    :cloudformationResource:: AWS::Batch::JobDefinition
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, type: str, container_properties: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["ContainerPropertiesProperty"]]]=None, job_definition_name: typing.Optional[str]=None, node_properties: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["NodePropertiesProperty"]]]=None, parameters: typing.Any=None, retry_strategy: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["RetryStrategyProperty"]]]=None, timeout: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["TimeoutProperty"]]]=None) -> None:
        """Create a new ``AWS::Batch::JobDefinition``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param type: ``AWS::Batch::JobDefinition.Type``.
        :param container_properties: ``AWS::Batch::JobDefinition.ContainerProperties``.
        :param job_definition_name: ``AWS::Batch::JobDefinition.JobDefinitionName``.
        :param node_properties: ``AWS::Batch::JobDefinition.NodeProperties``.
        :param parameters: ``AWS::Batch::JobDefinition.Parameters``.
        :param retry_strategy: ``AWS::Batch::JobDefinition.RetryStrategy``.
        :param timeout: ``AWS::Batch::JobDefinition.Timeout``.
        """
        props = CfnJobDefinitionProps(type=type, container_properties=container_properties, job_definition_name=job_definition_name, node_properties=node_properties, parameters=parameters, retry_strategy=retry_strategy, timeout=timeout)

        jsii.create(CfnJobDefinition, self, [scope, id, props])

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
    @jsii.member(jsii_name="parameters")
    def parameters(self) -> typing.Any:
        """``AWS::Batch::JobDefinition.Parameters``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobdefinition.html#cfn-batch-jobdefinition-parameters
        """
        return jsii.get(self, "parameters")

    @parameters.setter
    def parameters(self, value: typing.Any):
        return jsii.set(self, "parameters", value)

    @property
    @jsii.member(jsii_name="type")
    def type(self) -> str:
        """``AWS::Batch::JobDefinition.Type``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobdefinition.html#cfn-batch-jobdefinition-type
        """
        return jsii.get(self, "type")

    @type.setter
    def type(self, value: str):
        return jsii.set(self, "type", value)

    @property
    @jsii.member(jsii_name="containerProperties")
    def container_properties(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["ContainerPropertiesProperty"]]]:
        """``AWS::Batch::JobDefinition.ContainerProperties``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobdefinition.html#cfn-batch-jobdefinition-containerproperties
        """
        return jsii.get(self, "containerProperties")

    @container_properties.setter
    def container_properties(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["ContainerPropertiesProperty"]]]):
        return jsii.set(self, "containerProperties", value)

    @property
    @jsii.member(jsii_name="jobDefinitionName")
    def job_definition_name(self) -> typing.Optional[str]:
        """``AWS::Batch::JobDefinition.JobDefinitionName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobdefinition.html#cfn-batch-jobdefinition-jobdefinitionname
        """
        return jsii.get(self, "jobDefinitionName")

    @job_definition_name.setter
    def job_definition_name(self, value: typing.Optional[str]):
        return jsii.set(self, "jobDefinitionName", value)

    @property
    @jsii.member(jsii_name="nodeProperties")
    def node_properties(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["NodePropertiesProperty"]]]:
        """``AWS::Batch::JobDefinition.NodeProperties``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobdefinition.html#cfn-batch-jobdefinition-nodeproperties
        """
        return jsii.get(self, "nodeProperties")

    @node_properties.setter
    def node_properties(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["NodePropertiesProperty"]]]):
        return jsii.set(self, "nodeProperties", value)

    @property
    @jsii.member(jsii_name="retryStrategy")
    def retry_strategy(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["RetryStrategyProperty"]]]:
        """``AWS::Batch::JobDefinition.RetryStrategy``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobdefinition.html#cfn-batch-jobdefinition-retrystrategy
        """
        return jsii.get(self, "retryStrategy")

    @retry_strategy.setter
    def retry_strategy(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["RetryStrategyProperty"]]]):
        return jsii.set(self, "retryStrategy", value)

    @property
    @jsii.member(jsii_name="timeout")
    def timeout(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["TimeoutProperty"]]]:
        """``AWS::Batch::JobDefinition.Timeout``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobdefinition.html#cfn-batch-jobdefinition-timeout
        """
        return jsii.get(self, "timeout")

    @timeout.setter
    def timeout(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["TimeoutProperty"]]]):
        return jsii.set(self, "timeout", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-batch.CfnJobDefinition.ContainerPropertiesProperty", jsii_struct_bases=[], name_mapping={'image': 'image', 'memory': 'memory', 'vcpus': 'vcpus', 'command': 'command', 'environment': 'environment', 'instance_type': 'instanceType', 'job_role_arn': 'jobRoleArn', 'linux_parameters': 'linuxParameters', 'mount_points': 'mountPoints', 'privileged': 'privileged', 'readonly_root_filesystem': 'readonlyRootFilesystem', 'resource_requirements': 'resourceRequirements', 'ulimits': 'ulimits', 'user': 'user', 'volumes': 'volumes'})
    class ContainerPropertiesProperty():
        def __init__(self, *, image: str, memory: jsii.Number, vcpus: jsii.Number, command: typing.Optional[typing.List[str]]=None, environment: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnJobDefinition.EnvironmentProperty"]]]]]=None, instance_type: typing.Optional[str]=None, job_role_arn: typing.Optional[str]=None, linux_parameters: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnJobDefinition.LinuxParametersProperty"]]]=None, mount_points: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnJobDefinition.MountPointsProperty"]]]]]=None, privileged: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, readonly_root_filesystem: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, resource_requirements: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnJobDefinition.ResourceRequirementProperty"]]]]]=None, ulimits: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnJobDefinition.UlimitProperty"]]]]]=None, user: typing.Optional[str]=None, volumes: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnJobDefinition.VolumesProperty"]]]]]=None):
            """
            :param image: ``CfnJobDefinition.ContainerPropertiesProperty.Image``.
            :param memory: ``CfnJobDefinition.ContainerPropertiesProperty.Memory``.
            :param vcpus: ``CfnJobDefinition.ContainerPropertiesProperty.Vcpus``.
            :param command: ``CfnJobDefinition.ContainerPropertiesProperty.Command``.
            :param environment: ``CfnJobDefinition.ContainerPropertiesProperty.Environment``.
            :param instance_type: ``CfnJobDefinition.ContainerPropertiesProperty.InstanceType``.
            :param job_role_arn: ``CfnJobDefinition.ContainerPropertiesProperty.JobRoleArn``.
            :param linux_parameters: ``CfnJobDefinition.ContainerPropertiesProperty.LinuxParameters``.
            :param mount_points: ``CfnJobDefinition.ContainerPropertiesProperty.MountPoints``.
            :param privileged: ``CfnJobDefinition.ContainerPropertiesProperty.Privileged``.
            :param readonly_root_filesystem: ``CfnJobDefinition.ContainerPropertiesProperty.ReadonlyRootFilesystem``.
            :param resource_requirements: ``CfnJobDefinition.ContainerPropertiesProperty.ResourceRequirements``.
            :param ulimits: ``CfnJobDefinition.ContainerPropertiesProperty.Ulimits``.
            :param user: ``CfnJobDefinition.ContainerPropertiesProperty.User``.
            :param volumes: ``CfnJobDefinition.ContainerPropertiesProperty.Volumes``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-containerproperties.html
            """
            self._values = {
                'image': image,
                'memory': memory,
                'vcpus': vcpus,
            }
            if command is not None: self._values["command"] = command
            if environment is not None: self._values["environment"] = environment
            if instance_type is not None: self._values["instance_type"] = instance_type
            if job_role_arn is not None: self._values["job_role_arn"] = job_role_arn
            if linux_parameters is not None: self._values["linux_parameters"] = linux_parameters
            if mount_points is not None: self._values["mount_points"] = mount_points
            if privileged is not None: self._values["privileged"] = privileged
            if readonly_root_filesystem is not None: self._values["readonly_root_filesystem"] = readonly_root_filesystem
            if resource_requirements is not None: self._values["resource_requirements"] = resource_requirements
            if ulimits is not None: self._values["ulimits"] = ulimits
            if user is not None: self._values["user"] = user
            if volumes is not None: self._values["volumes"] = volumes

        @property
        def image(self) -> str:
            """``CfnJobDefinition.ContainerPropertiesProperty.Image``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-containerproperties.html#cfn-batch-jobdefinition-containerproperties-image
            """
            return self._values.get('image')

        @property
        def memory(self) -> jsii.Number:
            """``CfnJobDefinition.ContainerPropertiesProperty.Memory``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-containerproperties.html#cfn-batch-jobdefinition-containerproperties-memory
            """
            return self._values.get('memory')

        @property
        def vcpus(self) -> jsii.Number:
            """``CfnJobDefinition.ContainerPropertiesProperty.Vcpus``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-containerproperties.html#cfn-batch-jobdefinition-containerproperties-vcpus
            """
            return self._values.get('vcpus')

        @property
        def command(self) -> typing.Optional[typing.List[str]]:
            """``CfnJobDefinition.ContainerPropertiesProperty.Command``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-containerproperties.html#cfn-batch-jobdefinition-containerproperties-command
            """
            return self._values.get('command')

        @property
        def environment(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnJobDefinition.EnvironmentProperty"]]]]]:
            """``CfnJobDefinition.ContainerPropertiesProperty.Environment``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-containerproperties.html#cfn-batch-jobdefinition-containerproperties-environment
            """
            return self._values.get('environment')

        @property
        def instance_type(self) -> typing.Optional[str]:
            """``CfnJobDefinition.ContainerPropertiesProperty.InstanceType``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-containerproperties.html#cfn-batch-jobdefinition-containerproperties-instancetype
            """
            return self._values.get('instance_type')

        @property
        def job_role_arn(self) -> typing.Optional[str]:
            """``CfnJobDefinition.ContainerPropertiesProperty.JobRoleArn``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-containerproperties.html#cfn-batch-jobdefinition-containerproperties-jobrolearn
            """
            return self._values.get('job_role_arn')

        @property
        def linux_parameters(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnJobDefinition.LinuxParametersProperty"]]]:
            """``CfnJobDefinition.ContainerPropertiesProperty.LinuxParameters``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-containerproperties.html#cfn-batch-jobdefinition-containerproperties-linuxparameters
            """
            return self._values.get('linux_parameters')

        @property
        def mount_points(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnJobDefinition.MountPointsProperty"]]]]]:
            """``CfnJobDefinition.ContainerPropertiesProperty.MountPoints``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-containerproperties.html#cfn-batch-jobdefinition-containerproperties-mountpoints
            """
            return self._values.get('mount_points')

        @property
        def privileged(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
            """``CfnJobDefinition.ContainerPropertiesProperty.Privileged``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-containerproperties.html#cfn-batch-jobdefinition-containerproperties-privileged
            """
            return self._values.get('privileged')

        @property
        def readonly_root_filesystem(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
            """``CfnJobDefinition.ContainerPropertiesProperty.ReadonlyRootFilesystem``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-containerproperties.html#cfn-batch-jobdefinition-containerproperties-readonlyrootfilesystem
            """
            return self._values.get('readonly_root_filesystem')

        @property
        def resource_requirements(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnJobDefinition.ResourceRequirementProperty"]]]]]:
            """``CfnJobDefinition.ContainerPropertiesProperty.ResourceRequirements``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-containerproperties.html#cfn-batch-jobdefinition-containerproperties-resourcerequirements
            """
            return self._values.get('resource_requirements')

        @property
        def ulimits(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnJobDefinition.UlimitProperty"]]]]]:
            """``CfnJobDefinition.ContainerPropertiesProperty.Ulimits``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-containerproperties.html#cfn-batch-jobdefinition-containerproperties-ulimits
            """
            return self._values.get('ulimits')

        @property
        def user(self) -> typing.Optional[str]:
            """``CfnJobDefinition.ContainerPropertiesProperty.User``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-containerproperties.html#cfn-batch-jobdefinition-containerproperties-user
            """
            return self._values.get('user')

        @property
        def volumes(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnJobDefinition.VolumesProperty"]]]]]:
            """``CfnJobDefinition.ContainerPropertiesProperty.Volumes``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-containerproperties.html#cfn-batch-jobdefinition-containerproperties-volumes
            """
            return self._values.get('volumes')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'ContainerPropertiesProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-batch.CfnJobDefinition.DeviceProperty", jsii_struct_bases=[], name_mapping={'container_path': 'containerPath', 'host_path': 'hostPath', 'permissions': 'permissions'})
    class DeviceProperty():
        def __init__(self, *, container_path: typing.Optional[str]=None, host_path: typing.Optional[str]=None, permissions: typing.Optional[typing.List[str]]=None):
            """
            :param container_path: ``CfnJobDefinition.DeviceProperty.ContainerPath``.
            :param host_path: ``CfnJobDefinition.DeviceProperty.HostPath``.
            :param permissions: ``CfnJobDefinition.DeviceProperty.Permissions``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-device.html
            """
            self._values = {
            }
            if container_path is not None: self._values["container_path"] = container_path
            if host_path is not None: self._values["host_path"] = host_path
            if permissions is not None: self._values["permissions"] = permissions

        @property
        def container_path(self) -> typing.Optional[str]:
            """``CfnJobDefinition.DeviceProperty.ContainerPath``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-device.html#cfn-batch-jobdefinition-device-containerpath
            """
            return self._values.get('container_path')

        @property
        def host_path(self) -> typing.Optional[str]:
            """``CfnJobDefinition.DeviceProperty.HostPath``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-device.html#cfn-batch-jobdefinition-device-hostpath
            """
            return self._values.get('host_path')

        @property
        def permissions(self) -> typing.Optional[typing.List[str]]:
            """``CfnJobDefinition.DeviceProperty.Permissions``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-device.html#cfn-batch-jobdefinition-device-permissions
            """
            return self._values.get('permissions')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'DeviceProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-batch.CfnJobDefinition.EnvironmentProperty", jsii_struct_bases=[], name_mapping={'name': 'name', 'value': 'value'})
    class EnvironmentProperty():
        def __init__(self, *, name: typing.Optional[str]=None, value: typing.Optional[str]=None):
            """
            :param name: ``CfnJobDefinition.EnvironmentProperty.Name``.
            :param value: ``CfnJobDefinition.EnvironmentProperty.Value``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-environment.html
            """
            self._values = {
            }
            if name is not None: self._values["name"] = name
            if value is not None: self._values["value"] = value

        @property
        def name(self) -> typing.Optional[str]:
            """``CfnJobDefinition.EnvironmentProperty.Name``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-environment.html#cfn-batch-jobdefinition-environment-name
            """
            return self._values.get('name')

        @property
        def value(self) -> typing.Optional[str]:
            """``CfnJobDefinition.EnvironmentProperty.Value``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-environment.html#cfn-batch-jobdefinition-environment-value
            """
            return self._values.get('value')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'EnvironmentProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-batch.CfnJobDefinition.LinuxParametersProperty", jsii_struct_bases=[], name_mapping={'devices': 'devices'})
    class LinuxParametersProperty():
        def __init__(self, *, devices: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnJobDefinition.DeviceProperty"]]]]]=None):
            """
            :param devices: ``CfnJobDefinition.LinuxParametersProperty.Devices``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-containerproperties-linuxparameters.html
            """
            self._values = {
            }
            if devices is not None: self._values["devices"] = devices

        @property
        def devices(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnJobDefinition.DeviceProperty"]]]]]:
            """``CfnJobDefinition.LinuxParametersProperty.Devices``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-containerproperties-linuxparameters.html#cfn-batch-jobdefinition-containerproperties-linuxparameters-devices
            """
            return self._values.get('devices')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'LinuxParametersProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-batch.CfnJobDefinition.MountPointsProperty", jsii_struct_bases=[], name_mapping={'container_path': 'containerPath', 'read_only': 'readOnly', 'source_volume': 'sourceVolume'})
    class MountPointsProperty():
        def __init__(self, *, container_path: typing.Optional[str]=None, read_only: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, source_volume: typing.Optional[str]=None):
            """
            :param container_path: ``CfnJobDefinition.MountPointsProperty.ContainerPath``.
            :param read_only: ``CfnJobDefinition.MountPointsProperty.ReadOnly``.
            :param source_volume: ``CfnJobDefinition.MountPointsProperty.SourceVolume``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-mountpoints.html
            """
            self._values = {
            }
            if container_path is not None: self._values["container_path"] = container_path
            if read_only is not None: self._values["read_only"] = read_only
            if source_volume is not None: self._values["source_volume"] = source_volume

        @property
        def container_path(self) -> typing.Optional[str]:
            """``CfnJobDefinition.MountPointsProperty.ContainerPath``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-mountpoints.html#cfn-batch-jobdefinition-mountpoints-containerpath
            """
            return self._values.get('container_path')

        @property
        def read_only(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
            """``CfnJobDefinition.MountPointsProperty.ReadOnly``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-mountpoints.html#cfn-batch-jobdefinition-mountpoints-readonly
            """
            return self._values.get('read_only')

        @property
        def source_volume(self) -> typing.Optional[str]:
            """``CfnJobDefinition.MountPointsProperty.SourceVolume``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-mountpoints.html#cfn-batch-jobdefinition-mountpoints-sourcevolume
            """
            return self._values.get('source_volume')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'MountPointsProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-batch.CfnJobDefinition.NodePropertiesProperty", jsii_struct_bases=[], name_mapping={'main_node': 'mainNode', 'node_range_properties': 'nodeRangeProperties', 'num_nodes': 'numNodes'})
    class NodePropertiesProperty():
        def __init__(self, *, main_node: jsii.Number, node_range_properties: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnJobDefinition.NodeRangePropertyProperty"]]], num_nodes: jsii.Number):
            """
            :param main_node: ``CfnJobDefinition.NodePropertiesProperty.MainNode``.
            :param node_range_properties: ``CfnJobDefinition.NodePropertiesProperty.NodeRangeProperties``.
            :param num_nodes: ``CfnJobDefinition.NodePropertiesProperty.NumNodes``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-nodeproperties.html
            """
            self._values = {
                'main_node': main_node,
                'node_range_properties': node_range_properties,
                'num_nodes': num_nodes,
            }

        @property
        def main_node(self) -> jsii.Number:
            """``CfnJobDefinition.NodePropertiesProperty.MainNode``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-nodeproperties.html#cfn-batch-jobdefinition-nodeproperties-mainnode
            """
            return self._values.get('main_node')

        @property
        def node_range_properties(self) -> typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnJobDefinition.NodeRangePropertyProperty"]]]:
            """``CfnJobDefinition.NodePropertiesProperty.NodeRangeProperties``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-nodeproperties.html#cfn-batch-jobdefinition-nodeproperties-noderangeproperties
            """
            return self._values.get('node_range_properties')

        @property
        def num_nodes(self) -> jsii.Number:
            """``CfnJobDefinition.NodePropertiesProperty.NumNodes``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-nodeproperties.html#cfn-batch-jobdefinition-nodeproperties-numnodes
            """
            return self._values.get('num_nodes')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'NodePropertiesProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-batch.CfnJobDefinition.NodeRangePropertyProperty", jsii_struct_bases=[], name_mapping={'target_nodes': 'targetNodes', 'container': 'container'})
    class NodeRangePropertyProperty():
        def __init__(self, *, target_nodes: str, container: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnJobDefinition.ContainerPropertiesProperty"]]]=None):
            """
            :param target_nodes: ``CfnJobDefinition.NodeRangePropertyProperty.TargetNodes``.
            :param container: ``CfnJobDefinition.NodeRangePropertyProperty.Container``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-noderangeproperty.html
            """
            self._values = {
                'target_nodes': target_nodes,
            }
            if container is not None: self._values["container"] = container

        @property
        def target_nodes(self) -> str:
            """``CfnJobDefinition.NodeRangePropertyProperty.TargetNodes``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-noderangeproperty.html#cfn-batch-jobdefinition-noderangeproperty-targetnodes
            """
            return self._values.get('target_nodes')

        @property
        def container(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnJobDefinition.ContainerPropertiesProperty"]]]:
            """``CfnJobDefinition.NodeRangePropertyProperty.Container``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-noderangeproperty.html#cfn-batch-jobdefinition-noderangeproperty-container
            """
            return self._values.get('container')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'NodeRangePropertyProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-batch.CfnJobDefinition.ResourceRequirementProperty", jsii_struct_bases=[], name_mapping={'type': 'type', 'value': 'value'})
    class ResourceRequirementProperty():
        def __init__(self, *, type: typing.Optional[str]=None, value: typing.Optional[str]=None):
            """
            :param type: ``CfnJobDefinition.ResourceRequirementProperty.Type``.
            :param value: ``CfnJobDefinition.ResourceRequirementProperty.Value``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-resourcerequirement.html
            """
            self._values = {
            }
            if type is not None: self._values["type"] = type
            if value is not None: self._values["value"] = value

        @property
        def type(self) -> typing.Optional[str]:
            """``CfnJobDefinition.ResourceRequirementProperty.Type``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-resourcerequirement.html#cfn-batch-jobdefinition-resourcerequirement-type
            """
            return self._values.get('type')

        @property
        def value(self) -> typing.Optional[str]:
            """``CfnJobDefinition.ResourceRequirementProperty.Value``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-resourcerequirement.html#cfn-batch-jobdefinition-resourcerequirement-value
            """
            return self._values.get('value')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'ResourceRequirementProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-batch.CfnJobDefinition.RetryStrategyProperty", jsii_struct_bases=[], name_mapping={'attempts': 'attempts'})
    class RetryStrategyProperty():
        def __init__(self, *, attempts: typing.Optional[jsii.Number]=None):
            """
            :param attempts: ``CfnJobDefinition.RetryStrategyProperty.Attempts``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-retrystrategy.html
            """
            self._values = {
            }
            if attempts is not None: self._values["attempts"] = attempts

        @property
        def attempts(self) -> typing.Optional[jsii.Number]:
            """``CfnJobDefinition.RetryStrategyProperty.Attempts``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-retrystrategy.html#cfn-batch-jobdefinition-retrystrategy-attempts
            """
            return self._values.get('attempts')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'RetryStrategyProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-batch.CfnJobDefinition.TimeoutProperty", jsii_struct_bases=[], name_mapping={'attempt_duration_seconds': 'attemptDurationSeconds'})
    class TimeoutProperty():
        def __init__(self, *, attempt_duration_seconds: typing.Optional[jsii.Number]=None):
            """
            :param attempt_duration_seconds: ``CfnJobDefinition.TimeoutProperty.AttemptDurationSeconds``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-timeout.html
            """
            self._values = {
            }
            if attempt_duration_seconds is not None: self._values["attempt_duration_seconds"] = attempt_duration_seconds

        @property
        def attempt_duration_seconds(self) -> typing.Optional[jsii.Number]:
            """``CfnJobDefinition.TimeoutProperty.AttemptDurationSeconds``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-timeout.html#cfn-batch-jobdefinition-timeout-attemptdurationseconds
            """
            return self._values.get('attempt_duration_seconds')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'TimeoutProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-batch.CfnJobDefinition.UlimitProperty", jsii_struct_bases=[], name_mapping={'hard_limit': 'hardLimit', 'name': 'name', 'soft_limit': 'softLimit'})
    class UlimitProperty():
        def __init__(self, *, hard_limit: jsii.Number, name: str, soft_limit: jsii.Number):
            """
            :param hard_limit: ``CfnJobDefinition.UlimitProperty.HardLimit``.
            :param name: ``CfnJobDefinition.UlimitProperty.Name``.
            :param soft_limit: ``CfnJobDefinition.UlimitProperty.SoftLimit``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-ulimit.html
            """
            self._values = {
                'hard_limit': hard_limit,
                'name': name,
                'soft_limit': soft_limit,
            }

        @property
        def hard_limit(self) -> jsii.Number:
            """``CfnJobDefinition.UlimitProperty.HardLimit``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-ulimit.html#cfn-batch-jobdefinition-ulimit-hardlimit
            """
            return self._values.get('hard_limit')

        @property
        def name(self) -> str:
            """``CfnJobDefinition.UlimitProperty.Name``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-ulimit.html#cfn-batch-jobdefinition-ulimit-name
            """
            return self._values.get('name')

        @property
        def soft_limit(self) -> jsii.Number:
            """``CfnJobDefinition.UlimitProperty.SoftLimit``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-ulimit.html#cfn-batch-jobdefinition-ulimit-softlimit
            """
            return self._values.get('soft_limit')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'UlimitProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-batch.CfnJobDefinition.VolumesHostProperty", jsii_struct_bases=[], name_mapping={'source_path': 'sourcePath'})
    class VolumesHostProperty():
        def __init__(self, *, source_path: typing.Optional[str]=None):
            """
            :param source_path: ``CfnJobDefinition.VolumesHostProperty.SourcePath``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-volumeshost.html
            """
            self._values = {
            }
            if source_path is not None: self._values["source_path"] = source_path

        @property
        def source_path(self) -> typing.Optional[str]:
            """``CfnJobDefinition.VolumesHostProperty.SourcePath``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-volumeshost.html#cfn-batch-jobdefinition-volumeshost-sourcepath
            """
            return self._values.get('source_path')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'VolumesHostProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-batch.CfnJobDefinition.VolumesProperty", jsii_struct_bases=[], name_mapping={'host': 'host', 'name': 'name'})
    class VolumesProperty():
        def __init__(self, *, host: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnJobDefinition.VolumesHostProperty"]]]=None, name: typing.Optional[str]=None):
            """
            :param host: ``CfnJobDefinition.VolumesProperty.Host``.
            :param name: ``CfnJobDefinition.VolumesProperty.Name``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-volumes.html
            """
            self._values = {
            }
            if host is not None: self._values["host"] = host
            if name is not None: self._values["name"] = name

        @property
        def host(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnJobDefinition.VolumesHostProperty"]]]:
            """``CfnJobDefinition.VolumesProperty.Host``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-volumes.html#cfn-batch-jobdefinition-volumes-host
            """
            return self._values.get('host')

        @property
        def name(self) -> typing.Optional[str]:
            """``CfnJobDefinition.VolumesProperty.Name``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-volumes.html#cfn-batch-jobdefinition-volumes-name
            """
            return self._values.get('name')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'VolumesProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



@jsii.data_type(jsii_type="@aws-cdk/aws-batch.CfnJobDefinitionProps", jsii_struct_bases=[], name_mapping={'type': 'type', 'container_properties': 'containerProperties', 'job_definition_name': 'jobDefinitionName', 'node_properties': 'nodeProperties', 'parameters': 'parameters', 'retry_strategy': 'retryStrategy', 'timeout': 'timeout'})
class CfnJobDefinitionProps():
    def __init__(self, *, type: str, container_properties: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnJobDefinition.ContainerPropertiesProperty"]]]=None, job_definition_name: typing.Optional[str]=None, node_properties: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnJobDefinition.NodePropertiesProperty"]]]=None, parameters: typing.Any=None, retry_strategy: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnJobDefinition.RetryStrategyProperty"]]]=None, timeout: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnJobDefinition.TimeoutProperty"]]]=None):
        """Properties for defining a ``AWS::Batch::JobDefinition``.

        :param type: ``AWS::Batch::JobDefinition.Type``.
        :param container_properties: ``AWS::Batch::JobDefinition.ContainerProperties``.
        :param job_definition_name: ``AWS::Batch::JobDefinition.JobDefinitionName``.
        :param node_properties: ``AWS::Batch::JobDefinition.NodeProperties``.
        :param parameters: ``AWS::Batch::JobDefinition.Parameters``.
        :param retry_strategy: ``AWS::Batch::JobDefinition.RetryStrategy``.
        :param timeout: ``AWS::Batch::JobDefinition.Timeout``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobdefinition.html
        """
        self._values = {
            'type': type,
        }
        if container_properties is not None: self._values["container_properties"] = container_properties
        if job_definition_name is not None: self._values["job_definition_name"] = job_definition_name
        if node_properties is not None: self._values["node_properties"] = node_properties
        if parameters is not None: self._values["parameters"] = parameters
        if retry_strategy is not None: self._values["retry_strategy"] = retry_strategy
        if timeout is not None: self._values["timeout"] = timeout

    @property
    def type(self) -> str:
        """``AWS::Batch::JobDefinition.Type``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobdefinition.html#cfn-batch-jobdefinition-type
        """
        return self._values.get('type')

    @property
    def container_properties(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnJobDefinition.ContainerPropertiesProperty"]]]:
        """``AWS::Batch::JobDefinition.ContainerProperties``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobdefinition.html#cfn-batch-jobdefinition-containerproperties
        """
        return self._values.get('container_properties')

    @property
    def job_definition_name(self) -> typing.Optional[str]:
        """``AWS::Batch::JobDefinition.JobDefinitionName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobdefinition.html#cfn-batch-jobdefinition-jobdefinitionname
        """
        return self._values.get('job_definition_name')

    @property
    def node_properties(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnJobDefinition.NodePropertiesProperty"]]]:
        """``AWS::Batch::JobDefinition.NodeProperties``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobdefinition.html#cfn-batch-jobdefinition-nodeproperties
        """
        return self._values.get('node_properties')

    @property
    def parameters(self) -> typing.Any:
        """``AWS::Batch::JobDefinition.Parameters``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobdefinition.html#cfn-batch-jobdefinition-parameters
        """
        return self._values.get('parameters')

    @property
    def retry_strategy(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnJobDefinition.RetryStrategyProperty"]]]:
        """``AWS::Batch::JobDefinition.RetryStrategy``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobdefinition.html#cfn-batch-jobdefinition-retrystrategy
        """
        return self._values.get('retry_strategy')

    @property
    def timeout(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnJobDefinition.TimeoutProperty"]]]:
        """``AWS::Batch::JobDefinition.Timeout``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobdefinition.html#cfn-batch-jobdefinition-timeout
        """
        return self._values.get('timeout')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnJobDefinitionProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnJobQueue(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-batch.CfnJobQueue"):
    """A CloudFormation ``AWS::Batch::JobQueue``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobqueue.html
    cloudformationResource:
    :cloudformationResource:: AWS::Batch::JobQueue
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, compute_environment_order: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union["ComputeEnvironmentOrderProperty", aws_cdk.core.IResolvable]]], priority: jsii.Number, job_queue_name: typing.Optional[str]=None, state: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::Batch::JobQueue``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param compute_environment_order: ``AWS::Batch::JobQueue.ComputeEnvironmentOrder``.
        :param priority: ``AWS::Batch::JobQueue.Priority``.
        :param job_queue_name: ``AWS::Batch::JobQueue.JobQueueName``.
        :param state: ``AWS::Batch::JobQueue.State``.
        """
        props = CfnJobQueueProps(compute_environment_order=compute_environment_order, priority=priority, job_queue_name=job_queue_name, state=state)

        jsii.create(CfnJobQueue, self, [scope, id, props])

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
    @jsii.member(jsii_name="computeEnvironmentOrder")
    def compute_environment_order(self) -> typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union["ComputeEnvironmentOrderProperty", aws_cdk.core.IResolvable]]]:
        """``AWS::Batch::JobQueue.ComputeEnvironmentOrder``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobqueue.html#cfn-batch-jobqueue-computeenvironmentorder
        """
        return jsii.get(self, "computeEnvironmentOrder")

    @compute_environment_order.setter
    def compute_environment_order(self, value: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union["ComputeEnvironmentOrderProperty", aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "computeEnvironmentOrder", value)

    @property
    @jsii.member(jsii_name="priority")
    def priority(self) -> jsii.Number:
        """``AWS::Batch::JobQueue.Priority``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobqueue.html#cfn-batch-jobqueue-priority
        """
        return jsii.get(self, "priority")

    @priority.setter
    def priority(self, value: jsii.Number):
        return jsii.set(self, "priority", value)

    @property
    @jsii.member(jsii_name="jobQueueName")
    def job_queue_name(self) -> typing.Optional[str]:
        """``AWS::Batch::JobQueue.JobQueueName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobqueue.html#cfn-batch-jobqueue-jobqueuename
        """
        return jsii.get(self, "jobQueueName")

    @job_queue_name.setter
    def job_queue_name(self, value: typing.Optional[str]):
        return jsii.set(self, "jobQueueName", value)

    @property
    @jsii.member(jsii_name="state")
    def state(self) -> typing.Optional[str]:
        """``AWS::Batch::JobQueue.State``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobqueue.html#cfn-batch-jobqueue-state
        """
        return jsii.get(self, "state")

    @state.setter
    def state(self, value: typing.Optional[str]):
        return jsii.set(self, "state", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-batch.CfnJobQueue.ComputeEnvironmentOrderProperty", jsii_struct_bases=[], name_mapping={'compute_environment': 'computeEnvironment', 'order': 'order'})
    class ComputeEnvironmentOrderProperty():
        def __init__(self, *, compute_environment: str, order: jsii.Number):
            """
            :param compute_environment: ``CfnJobQueue.ComputeEnvironmentOrderProperty.ComputeEnvironment``.
            :param order: ``CfnJobQueue.ComputeEnvironmentOrderProperty.Order``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobqueue-computeenvironmentorder.html
            """
            self._values = {
                'compute_environment': compute_environment,
                'order': order,
            }

        @property
        def compute_environment(self) -> str:
            """``CfnJobQueue.ComputeEnvironmentOrderProperty.ComputeEnvironment``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobqueue-computeenvironmentorder.html#cfn-batch-jobqueue-computeenvironmentorder-computeenvironment
            """
            return self._values.get('compute_environment')

        @property
        def order(self) -> jsii.Number:
            """``CfnJobQueue.ComputeEnvironmentOrderProperty.Order``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobqueue-computeenvironmentorder.html#cfn-batch-jobqueue-computeenvironmentorder-order
            """
            return self._values.get('order')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'ComputeEnvironmentOrderProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



@jsii.data_type(jsii_type="@aws-cdk/aws-batch.CfnJobQueueProps", jsii_struct_bases=[], name_mapping={'compute_environment_order': 'computeEnvironmentOrder', 'priority': 'priority', 'job_queue_name': 'jobQueueName', 'state': 'state'})
class CfnJobQueueProps():
    def __init__(self, *, compute_environment_order: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union["CfnJobQueue.ComputeEnvironmentOrderProperty", aws_cdk.core.IResolvable]]], priority: jsii.Number, job_queue_name: typing.Optional[str]=None, state: typing.Optional[str]=None):
        """Properties for defining a ``AWS::Batch::JobQueue``.

        :param compute_environment_order: ``AWS::Batch::JobQueue.ComputeEnvironmentOrder``.
        :param priority: ``AWS::Batch::JobQueue.Priority``.
        :param job_queue_name: ``AWS::Batch::JobQueue.JobQueueName``.
        :param state: ``AWS::Batch::JobQueue.State``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobqueue.html
        """
        self._values = {
            'compute_environment_order': compute_environment_order,
            'priority': priority,
        }
        if job_queue_name is not None: self._values["job_queue_name"] = job_queue_name
        if state is not None: self._values["state"] = state

    @property
    def compute_environment_order(self) -> typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union["CfnJobQueue.ComputeEnvironmentOrderProperty", aws_cdk.core.IResolvable]]]:
        """``AWS::Batch::JobQueue.ComputeEnvironmentOrder``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobqueue.html#cfn-batch-jobqueue-computeenvironmentorder
        """
        return self._values.get('compute_environment_order')

    @property
    def priority(self) -> jsii.Number:
        """``AWS::Batch::JobQueue.Priority``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobqueue.html#cfn-batch-jobqueue-priority
        """
        return self._values.get('priority')

    @property
    def job_queue_name(self) -> typing.Optional[str]:
        """``AWS::Batch::JobQueue.JobQueueName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobqueue.html#cfn-batch-jobqueue-jobqueuename
        """
        return self._values.get('job_queue_name')

    @property
    def state(self) -> typing.Optional[str]:
        """``AWS::Batch::JobQueue.State``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobqueue.html#cfn-batch-jobqueue-state
        """
        return self._values.get('state')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnJobQueueProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


__all__ = ["CfnComputeEnvironment", "CfnComputeEnvironmentProps", "CfnJobDefinition", "CfnJobDefinitionProps", "CfnJobQueue", "CfnJobQueueProps", "__jsii_assembly__"]

publication.publish()
