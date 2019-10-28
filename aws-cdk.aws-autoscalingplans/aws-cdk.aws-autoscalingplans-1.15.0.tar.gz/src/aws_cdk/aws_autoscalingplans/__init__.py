import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.core
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-autoscalingplans", "1.15.0", __name__, "aws-autoscalingplans@1.15.0.jsii.tgz")
class CfnScalingPlan(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-autoscalingplans.CfnScalingPlan"):
    """A CloudFormation ``AWS::AutoScalingPlans::ScalingPlan``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-autoscalingplans-scalingplan.html
    cloudformationResource:
    :cloudformationResource:: AWS::AutoScalingPlans::ScalingPlan
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, application_source: typing.Union["ApplicationSourceProperty", aws_cdk.core.IResolvable], scaling_instructions: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "ScalingInstructionProperty"]]]) -> None:
        """Create a new ``AWS::AutoScalingPlans::ScalingPlan``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param application_source: ``AWS::AutoScalingPlans::ScalingPlan.ApplicationSource``.
        :param scaling_instructions: ``AWS::AutoScalingPlans::ScalingPlan.ScalingInstructions``.
        """
        props = CfnScalingPlanProps(application_source=application_source, scaling_instructions=scaling_instructions)

        jsii.create(CfnScalingPlan, self, [scope, id, props])

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
    @jsii.member(jsii_name="attrScalingPlanName")
    def attr_scaling_plan_name(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: ScalingPlanName
        """
        return jsii.get(self, "attrScalingPlanName")

    @property
    @jsii.member(jsii_name="attrScalingPlanVersion")
    def attr_scaling_plan_version(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: ScalingPlanVersion
        """
        return jsii.get(self, "attrScalingPlanVersion")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="applicationSource")
    def application_source(self) -> typing.Union["ApplicationSourceProperty", aws_cdk.core.IResolvable]:
        """``AWS::AutoScalingPlans::ScalingPlan.ApplicationSource``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-autoscalingplans-scalingplan.html#cfn-autoscalingplans-scalingplan-applicationsource
        """
        return jsii.get(self, "applicationSource")

    @application_source.setter
    def application_source(self, value: typing.Union["ApplicationSourceProperty", aws_cdk.core.IResolvable]):
        return jsii.set(self, "applicationSource", value)

    @property
    @jsii.member(jsii_name="scalingInstructions")
    def scaling_instructions(self) -> typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "ScalingInstructionProperty"]]]:
        """``AWS::AutoScalingPlans::ScalingPlan.ScalingInstructions``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-autoscalingplans-scalingplan.html#cfn-autoscalingplans-scalingplan-scalinginstructions
        """
        return jsii.get(self, "scalingInstructions")

    @scaling_instructions.setter
    def scaling_instructions(self, value: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "ScalingInstructionProperty"]]]):
        return jsii.set(self, "scalingInstructions", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-autoscalingplans.CfnScalingPlan.ApplicationSourceProperty", jsii_struct_bases=[], name_mapping={'cloud_formation_stack_arn': 'cloudFormationStackArn', 'tag_filters': 'tagFilters'})
    class ApplicationSourceProperty():
        def __init__(self, *, cloud_formation_stack_arn: typing.Optional[str]=None, tag_filters: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnScalingPlan.TagFilterProperty"]]]]]=None):
            """
            :param cloud_formation_stack_arn: ``CfnScalingPlan.ApplicationSourceProperty.CloudFormationStackARN``.
            :param tag_filters: ``CfnScalingPlan.ApplicationSourceProperty.TagFilters``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-autoscalingplans-scalingplan-applicationsource.html
            """
            self._values = {
            }
            if cloud_formation_stack_arn is not None: self._values["cloud_formation_stack_arn"] = cloud_formation_stack_arn
            if tag_filters is not None: self._values["tag_filters"] = tag_filters

        @property
        def cloud_formation_stack_arn(self) -> typing.Optional[str]:
            """``CfnScalingPlan.ApplicationSourceProperty.CloudFormationStackARN``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-autoscalingplans-scalingplan-applicationsource.html#cfn-autoscalingplans-scalingplan-applicationsource-cloudformationstackarn
            """
            return self._values.get('cloud_formation_stack_arn')

        @property
        def tag_filters(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnScalingPlan.TagFilterProperty"]]]]]:
            """``CfnScalingPlan.ApplicationSourceProperty.TagFilters``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-autoscalingplans-scalingplan-applicationsource.html#cfn-autoscalingplans-scalingplan-applicationsource-tagfilters
            """
            return self._values.get('tag_filters')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'ApplicationSourceProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-autoscalingplans.CfnScalingPlan.CustomizedLoadMetricSpecificationProperty", jsii_struct_bases=[], name_mapping={'metric_name': 'metricName', 'namespace': 'namespace', 'statistic': 'statistic', 'dimensions': 'dimensions', 'unit': 'unit'})
    class CustomizedLoadMetricSpecificationProperty():
        def __init__(self, *, metric_name: str, namespace: str, statistic: str, dimensions: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnScalingPlan.MetricDimensionProperty"]]]]]=None, unit: typing.Optional[str]=None):
            """
            :param metric_name: ``CfnScalingPlan.CustomizedLoadMetricSpecificationProperty.MetricName``.
            :param namespace: ``CfnScalingPlan.CustomizedLoadMetricSpecificationProperty.Namespace``.
            :param statistic: ``CfnScalingPlan.CustomizedLoadMetricSpecificationProperty.Statistic``.
            :param dimensions: ``CfnScalingPlan.CustomizedLoadMetricSpecificationProperty.Dimensions``.
            :param unit: ``CfnScalingPlan.CustomizedLoadMetricSpecificationProperty.Unit``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-autoscalingplans-scalingplan-customizedloadmetricspecification.html
            """
            self._values = {
                'metric_name': metric_name,
                'namespace': namespace,
                'statistic': statistic,
            }
            if dimensions is not None: self._values["dimensions"] = dimensions
            if unit is not None: self._values["unit"] = unit

        @property
        def metric_name(self) -> str:
            """``CfnScalingPlan.CustomizedLoadMetricSpecificationProperty.MetricName``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-autoscalingplans-scalingplan-customizedloadmetricspecification.html#cfn-autoscalingplans-scalingplan-customizedloadmetricspecification-metricname
            """
            return self._values.get('metric_name')

        @property
        def namespace(self) -> str:
            """``CfnScalingPlan.CustomizedLoadMetricSpecificationProperty.Namespace``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-autoscalingplans-scalingplan-customizedloadmetricspecification.html#cfn-autoscalingplans-scalingplan-customizedloadmetricspecification-namespace
            """
            return self._values.get('namespace')

        @property
        def statistic(self) -> str:
            """``CfnScalingPlan.CustomizedLoadMetricSpecificationProperty.Statistic``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-autoscalingplans-scalingplan-customizedloadmetricspecification.html#cfn-autoscalingplans-scalingplan-customizedloadmetricspecification-statistic
            """
            return self._values.get('statistic')

        @property
        def dimensions(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnScalingPlan.MetricDimensionProperty"]]]]]:
            """``CfnScalingPlan.CustomizedLoadMetricSpecificationProperty.Dimensions``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-autoscalingplans-scalingplan-customizedloadmetricspecification.html#cfn-autoscalingplans-scalingplan-customizedloadmetricspecification-dimensions
            """
            return self._values.get('dimensions')

        @property
        def unit(self) -> typing.Optional[str]:
            """``CfnScalingPlan.CustomizedLoadMetricSpecificationProperty.Unit``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-autoscalingplans-scalingplan-customizedloadmetricspecification.html#cfn-autoscalingplans-scalingplan-customizedloadmetricspecification-unit
            """
            return self._values.get('unit')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'CustomizedLoadMetricSpecificationProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-autoscalingplans.CfnScalingPlan.CustomizedScalingMetricSpecificationProperty", jsii_struct_bases=[], name_mapping={'metric_name': 'metricName', 'namespace': 'namespace', 'statistic': 'statistic', 'dimensions': 'dimensions', 'unit': 'unit'})
    class CustomizedScalingMetricSpecificationProperty():
        def __init__(self, *, metric_name: str, namespace: str, statistic: str, dimensions: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnScalingPlan.MetricDimensionProperty"]]]]]=None, unit: typing.Optional[str]=None):
            """
            :param metric_name: ``CfnScalingPlan.CustomizedScalingMetricSpecificationProperty.MetricName``.
            :param namespace: ``CfnScalingPlan.CustomizedScalingMetricSpecificationProperty.Namespace``.
            :param statistic: ``CfnScalingPlan.CustomizedScalingMetricSpecificationProperty.Statistic``.
            :param dimensions: ``CfnScalingPlan.CustomizedScalingMetricSpecificationProperty.Dimensions``.
            :param unit: ``CfnScalingPlan.CustomizedScalingMetricSpecificationProperty.Unit``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-autoscalingplans-scalingplan-customizedscalingmetricspecification.html
            """
            self._values = {
                'metric_name': metric_name,
                'namespace': namespace,
                'statistic': statistic,
            }
            if dimensions is not None: self._values["dimensions"] = dimensions
            if unit is not None: self._values["unit"] = unit

        @property
        def metric_name(self) -> str:
            """``CfnScalingPlan.CustomizedScalingMetricSpecificationProperty.MetricName``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-autoscalingplans-scalingplan-customizedscalingmetricspecification.html#cfn-autoscalingplans-scalingplan-customizedscalingmetricspecification-metricname
            """
            return self._values.get('metric_name')

        @property
        def namespace(self) -> str:
            """``CfnScalingPlan.CustomizedScalingMetricSpecificationProperty.Namespace``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-autoscalingplans-scalingplan-customizedscalingmetricspecification.html#cfn-autoscalingplans-scalingplan-customizedscalingmetricspecification-namespace
            """
            return self._values.get('namespace')

        @property
        def statistic(self) -> str:
            """``CfnScalingPlan.CustomizedScalingMetricSpecificationProperty.Statistic``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-autoscalingplans-scalingplan-customizedscalingmetricspecification.html#cfn-autoscalingplans-scalingplan-customizedscalingmetricspecification-statistic
            """
            return self._values.get('statistic')

        @property
        def dimensions(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnScalingPlan.MetricDimensionProperty"]]]]]:
            """``CfnScalingPlan.CustomizedScalingMetricSpecificationProperty.Dimensions``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-autoscalingplans-scalingplan-customizedscalingmetricspecification.html#cfn-autoscalingplans-scalingplan-customizedscalingmetricspecification-dimensions
            """
            return self._values.get('dimensions')

        @property
        def unit(self) -> typing.Optional[str]:
            """``CfnScalingPlan.CustomizedScalingMetricSpecificationProperty.Unit``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-autoscalingplans-scalingplan-customizedscalingmetricspecification.html#cfn-autoscalingplans-scalingplan-customizedscalingmetricspecification-unit
            """
            return self._values.get('unit')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'CustomizedScalingMetricSpecificationProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-autoscalingplans.CfnScalingPlan.MetricDimensionProperty", jsii_struct_bases=[], name_mapping={'name': 'name', 'value': 'value'})
    class MetricDimensionProperty():
        def __init__(self, *, name: str, value: str):
            """
            :param name: ``CfnScalingPlan.MetricDimensionProperty.Name``.
            :param value: ``CfnScalingPlan.MetricDimensionProperty.Value``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-autoscalingplans-scalingplan-metricdimension.html
            """
            self._values = {
                'name': name,
                'value': value,
            }

        @property
        def name(self) -> str:
            """``CfnScalingPlan.MetricDimensionProperty.Name``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-autoscalingplans-scalingplan-metricdimension.html#cfn-autoscalingplans-scalingplan-metricdimension-name
            """
            return self._values.get('name')

        @property
        def value(self) -> str:
            """``CfnScalingPlan.MetricDimensionProperty.Value``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-autoscalingplans-scalingplan-metricdimension.html#cfn-autoscalingplans-scalingplan-metricdimension-value
            """
            return self._values.get('value')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'MetricDimensionProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-autoscalingplans.CfnScalingPlan.PredefinedLoadMetricSpecificationProperty", jsii_struct_bases=[], name_mapping={'predefined_load_metric_type': 'predefinedLoadMetricType', 'resource_label': 'resourceLabel'})
    class PredefinedLoadMetricSpecificationProperty():
        def __init__(self, *, predefined_load_metric_type: str, resource_label: typing.Optional[str]=None):
            """
            :param predefined_load_metric_type: ``CfnScalingPlan.PredefinedLoadMetricSpecificationProperty.PredefinedLoadMetricType``.
            :param resource_label: ``CfnScalingPlan.PredefinedLoadMetricSpecificationProperty.ResourceLabel``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-autoscalingplans-scalingplan-predefinedloadmetricspecification.html
            """
            self._values = {
                'predefined_load_metric_type': predefined_load_metric_type,
            }
            if resource_label is not None: self._values["resource_label"] = resource_label

        @property
        def predefined_load_metric_type(self) -> str:
            """``CfnScalingPlan.PredefinedLoadMetricSpecificationProperty.PredefinedLoadMetricType``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-autoscalingplans-scalingplan-predefinedloadmetricspecification.html#cfn-autoscalingplans-scalingplan-predefinedloadmetricspecification-predefinedloadmetrictype
            """
            return self._values.get('predefined_load_metric_type')

        @property
        def resource_label(self) -> typing.Optional[str]:
            """``CfnScalingPlan.PredefinedLoadMetricSpecificationProperty.ResourceLabel``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-autoscalingplans-scalingplan-predefinedloadmetricspecification.html#cfn-autoscalingplans-scalingplan-predefinedloadmetricspecification-resourcelabel
            """
            return self._values.get('resource_label')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'PredefinedLoadMetricSpecificationProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-autoscalingplans.CfnScalingPlan.PredefinedScalingMetricSpecificationProperty", jsii_struct_bases=[], name_mapping={'predefined_scaling_metric_type': 'predefinedScalingMetricType', 'resource_label': 'resourceLabel'})
    class PredefinedScalingMetricSpecificationProperty():
        def __init__(self, *, predefined_scaling_metric_type: str, resource_label: typing.Optional[str]=None):
            """
            :param predefined_scaling_metric_type: ``CfnScalingPlan.PredefinedScalingMetricSpecificationProperty.PredefinedScalingMetricType``.
            :param resource_label: ``CfnScalingPlan.PredefinedScalingMetricSpecificationProperty.ResourceLabel``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-autoscalingplans-scalingplan-predefinedscalingmetricspecification.html
            """
            self._values = {
                'predefined_scaling_metric_type': predefined_scaling_metric_type,
            }
            if resource_label is not None: self._values["resource_label"] = resource_label

        @property
        def predefined_scaling_metric_type(self) -> str:
            """``CfnScalingPlan.PredefinedScalingMetricSpecificationProperty.PredefinedScalingMetricType``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-autoscalingplans-scalingplan-predefinedscalingmetricspecification.html#cfn-autoscalingplans-scalingplan-predefinedscalingmetricspecification-predefinedscalingmetrictype
            """
            return self._values.get('predefined_scaling_metric_type')

        @property
        def resource_label(self) -> typing.Optional[str]:
            """``CfnScalingPlan.PredefinedScalingMetricSpecificationProperty.ResourceLabel``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-autoscalingplans-scalingplan-predefinedscalingmetricspecification.html#cfn-autoscalingplans-scalingplan-predefinedscalingmetricspecification-resourcelabel
            """
            return self._values.get('resource_label')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'PredefinedScalingMetricSpecificationProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-autoscalingplans.CfnScalingPlan.ScalingInstructionProperty", jsii_struct_bases=[], name_mapping={'max_capacity': 'maxCapacity', 'min_capacity': 'minCapacity', 'resource_id': 'resourceId', 'scalable_dimension': 'scalableDimension', 'service_namespace': 'serviceNamespace', 'target_tracking_configurations': 'targetTrackingConfigurations', 'customized_load_metric_specification': 'customizedLoadMetricSpecification', 'disable_dynamic_scaling': 'disableDynamicScaling', 'predefined_load_metric_specification': 'predefinedLoadMetricSpecification', 'predictive_scaling_max_capacity_behavior': 'predictiveScalingMaxCapacityBehavior', 'predictive_scaling_max_capacity_buffer': 'predictiveScalingMaxCapacityBuffer', 'predictive_scaling_mode': 'predictiveScalingMode', 'scaling_policy_update_behavior': 'scalingPolicyUpdateBehavior', 'scheduled_action_buffer_time': 'scheduledActionBufferTime'})
    class ScalingInstructionProperty():
        def __init__(self, *, max_capacity: jsii.Number, min_capacity: jsii.Number, resource_id: str, scalable_dimension: str, service_namespace: str, target_tracking_configurations: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnScalingPlan.TargetTrackingConfigurationProperty"]]], customized_load_metric_specification: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnScalingPlan.CustomizedLoadMetricSpecificationProperty"]]]=None, disable_dynamic_scaling: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, predefined_load_metric_specification: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnScalingPlan.PredefinedLoadMetricSpecificationProperty"]]]=None, predictive_scaling_max_capacity_behavior: typing.Optional[str]=None, predictive_scaling_max_capacity_buffer: typing.Optional[jsii.Number]=None, predictive_scaling_mode: typing.Optional[str]=None, scaling_policy_update_behavior: typing.Optional[str]=None, scheduled_action_buffer_time: typing.Optional[jsii.Number]=None):
            """
            :param max_capacity: ``CfnScalingPlan.ScalingInstructionProperty.MaxCapacity``.
            :param min_capacity: ``CfnScalingPlan.ScalingInstructionProperty.MinCapacity``.
            :param resource_id: ``CfnScalingPlan.ScalingInstructionProperty.ResourceId``.
            :param scalable_dimension: ``CfnScalingPlan.ScalingInstructionProperty.ScalableDimension``.
            :param service_namespace: ``CfnScalingPlan.ScalingInstructionProperty.ServiceNamespace``.
            :param target_tracking_configurations: ``CfnScalingPlan.ScalingInstructionProperty.TargetTrackingConfigurations``.
            :param customized_load_metric_specification: ``CfnScalingPlan.ScalingInstructionProperty.CustomizedLoadMetricSpecification``.
            :param disable_dynamic_scaling: ``CfnScalingPlan.ScalingInstructionProperty.DisableDynamicScaling``.
            :param predefined_load_metric_specification: ``CfnScalingPlan.ScalingInstructionProperty.PredefinedLoadMetricSpecification``.
            :param predictive_scaling_max_capacity_behavior: ``CfnScalingPlan.ScalingInstructionProperty.PredictiveScalingMaxCapacityBehavior``.
            :param predictive_scaling_max_capacity_buffer: ``CfnScalingPlan.ScalingInstructionProperty.PredictiveScalingMaxCapacityBuffer``.
            :param predictive_scaling_mode: ``CfnScalingPlan.ScalingInstructionProperty.PredictiveScalingMode``.
            :param scaling_policy_update_behavior: ``CfnScalingPlan.ScalingInstructionProperty.ScalingPolicyUpdateBehavior``.
            :param scheduled_action_buffer_time: ``CfnScalingPlan.ScalingInstructionProperty.ScheduledActionBufferTime``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-autoscalingplans-scalingplan-scalinginstruction.html
            """
            self._values = {
                'max_capacity': max_capacity,
                'min_capacity': min_capacity,
                'resource_id': resource_id,
                'scalable_dimension': scalable_dimension,
                'service_namespace': service_namespace,
                'target_tracking_configurations': target_tracking_configurations,
            }
            if customized_load_metric_specification is not None: self._values["customized_load_metric_specification"] = customized_load_metric_specification
            if disable_dynamic_scaling is not None: self._values["disable_dynamic_scaling"] = disable_dynamic_scaling
            if predefined_load_metric_specification is not None: self._values["predefined_load_metric_specification"] = predefined_load_metric_specification
            if predictive_scaling_max_capacity_behavior is not None: self._values["predictive_scaling_max_capacity_behavior"] = predictive_scaling_max_capacity_behavior
            if predictive_scaling_max_capacity_buffer is not None: self._values["predictive_scaling_max_capacity_buffer"] = predictive_scaling_max_capacity_buffer
            if predictive_scaling_mode is not None: self._values["predictive_scaling_mode"] = predictive_scaling_mode
            if scaling_policy_update_behavior is not None: self._values["scaling_policy_update_behavior"] = scaling_policy_update_behavior
            if scheduled_action_buffer_time is not None: self._values["scheduled_action_buffer_time"] = scheduled_action_buffer_time

        @property
        def max_capacity(self) -> jsii.Number:
            """``CfnScalingPlan.ScalingInstructionProperty.MaxCapacity``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-autoscalingplans-scalingplan-scalinginstruction.html#cfn-autoscalingplans-scalingplan-scalinginstruction-maxcapacity
            """
            return self._values.get('max_capacity')

        @property
        def min_capacity(self) -> jsii.Number:
            """``CfnScalingPlan.ScalingInstructionProperty.MinCapacity``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-autoscalingplans-scalingplan-scalinginstruction.html#cfn-autoscalingplans-scalingplan-scalinginstruction-mincapacity
            """
            return self._values.get('min_capacity')

        @property
        def resource_id(self) -> str:
            """``CfnScalingPlan.ScalingInstructionProperty.ResourceId``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-autoscalingplans-scalingplan-scalinginstruction.html#cfn-autoscalingplans-scalingplan-scalinginstruction-resourceid
            """
            return self._values.get('resource_id')

        @property
        def scalable_dimension(self) -> str:
            """``CfnScalingPlan.ScalingInstructionProperty.ScalableDimension``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-autoscalingplans-scalingplan-scalinginstruction.html#cfn-autoscalingplans-scalingplan-scalinginstruction-scalabledimension
            """
            return self._values.get('scalable_dimension')

        @property
        def service_namespace(self) -> str:
            """``CfnScalingPlan.ScalingInstructionProperty.ServiceNamespace``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-autoscalingplans-scalingplan-scalinginstruction.html#cfn-autoscalingplans-scalingplan-scalinginstruction-servicenamespace
            """
            return self._values.get('service_namespace')

        @property
        def target_tracking_configurations(self) -> typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnScalingPlan.TargetTrackingConfigurationProperty"]]]:
            """``CfnScalingPlan.ScalingInstructionProperty.TargetTrackingConfigurations``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-autoscalingplans-scalingplan-scalinginstruction.html#cfn-autoscalingplans-scalingplan-scalinginstruction-targettrackingconfigurations
            """
            return self._values.get('target_tracking_configurations')

        @property
        def customized_load_metric_specification(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnScalingPlan.CustomizedLoadMetricSpecificationProperty"]]]:
            """``CfnScalingPlan.ScalingInstructionProperty.CustomizedLoadMetricSpecification``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-autoscalingplans-scalingplan-scalinginstruction.html#cfn-autoscalingplans-scalingplan-scalinginstruction-customizedloadmetricspecification
            """
            return self._values.get('customized_load_metric_specification')

        @property
        def disable_dynamic_scaling(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
            """``CfnScalingPlan.ScalingInstructionProperty.DisableDynamicScaling``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-autoscalingplans-scalingplan-scalinginstruction.html#cfn-autoscalingplans-scalingplan-scalinginstruction-disabledynamicscaling
            """
            return self._values.get('disable_dynamic_scaling')

        @property
        def predefined_load_metric_specification(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnScalingPlan.PredefinedLoadMetricSpecificationProperty"]]]:
            """``CfnScalingPlan.ScalingInstructionProperty.PredefinedLoadMetricSpecification``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-autoscalingplans-scalingplan-scalinginstruction.html#cfn-autoscalingplans-scalingplan-scalinginstruction-predefinedloadmetricspecification
            """
            return self._values.get('predefined_load_metric_specification')

        @property
        def predictive_scaling_max_capacity_behavior(self) -> typing.Optional[str]:
            """``CfnScalingPlan.ScalingInstructionProperty.PredictiveScalingMaxCapacityBehavior``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-autoscalingplans-scalingplan-scalinginstruction.html#cfn-autoscalingplans-scalingplan-scalinginstruction-predictivescalingmaxcapacitybehavior
            """
            return self._values.get('predictive_scaling_max_capacity_behavior')

        @property
        def predictive_scaling_max_capacity_buffer(self) -> typing.Optional[jsii.Number]:
            """``CfnScalingPlan.ScalingInstructionProperty.PredictiveScalingMaxCapacityBuffer``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-autoscalingplans-scalingplan-scalinginstruction.html#cfn-autoscalingplans-scalingplan-scalinginstruction-predictivescalingmaxcapacitybuffer
            """
            return self._values.get('predictive_scaling_max_capacity_buffer')

        @property
        def predictive_scaling_mode(self) -> typing.Optional[str]:
            """``CfnScalingPlan.ScalingInstructionProperty.PredictiveScalingMode``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-autoscalingplans-scalingplan-scalinginstruction.html#cfn-autoscalingplans-scalingplan-scalinginstruction-predictivescalingmode
            """
            return self._values.get('predictive_scaling_mode')

        @property
        def scaling_policy_update_behavior(self) -> typing.Optional[str]:
            """``CfnScalingPlan.ScalingInstructionProperty.ScalingPolicyUpdateBehavior``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-autoscalingplans-scalingplan-scalinginstruction.html#cfn-autoscalingplans-scalingplan-scalinginstruction-scalingpolicyupdatebehavior
            """
            return self._values.get('scaling_policy_update_behavior')

        @property
        def scheduled_action_buffer_time(self) -> typing.Optional[jsii.Number]:
            """``CfnScalingPlan.ScalingInstructionProperty.ScheduledActionBufferTime``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-autoscalingplans-scalingplan-scalinginstruction.html#cfn-autoscalingplans-scalingplan-scalinginstruction-scheduledactionbuffertime
            """
            return self._values.get('scheduled_action_buffer_time')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'ScalingInstructionProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-autoscalingplans.CfnScalingPlan.TagFilterProperty", jsii_struct_bases=[], name_mapping={'key': 'key', 'values': 'values'})
    class TagFilterProperty():
        def __init__(self, *, key: str, values: typing.Optional[typing.List[str]]=None):
            """
            :param key: ``CfnScalingPlan.TagFilterProperty.Key``.
            :param values: ``CfnScalingPlan.TagFilterProperty.Values``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-autoscalingplans-scalingplan-tagfilter.html
            """
            self._values = {
                'key': key,
            }
            if values is not None: self._values["values"] = values

        @property
        def key(self) -> str:
            """``CfnScalingPlan.TagFilterProperty.Key``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-autoscalingplans-scalingplan-tagfilter.html#cfn-autoscalingplans-scalingplan-tagfilter-key
            """
            return self._values.get('key')

        @property
        def values(self) -> typing.Optional[typing.List[str]]:
            """``CfnScalingPlan.TagFilterProperty.Values``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-autoscalingplans-scalingplan-tagfilter.html#cfn-autoscalingplans-scalingplan-tagfilter-values
            """
            return self._values.get('values')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'TagFilterProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-autoscalingplans.CfnScalingPlan.TargetTrackingConfigurationProperty", jsii_struct_bases=[], name_mapping={'target_value': 'targetValue', 'customized_scaling_metric_specification': 'customizedScalingMetricSpecification', 'disable_scale_in': 'disableScaleIn', 'estimated_instance_warmup': 'estimatedInstanceWarmup', 'predefined_scaling_metric_specification': 'predefinedScalingMetricSpecification', 'scale_in_cooldown': 'scaleInCooldown', 'scale_out_cooldown': 'scaleOutCooldown'})
    class TargetTrackingConfigurationProperty():
        def __init__(self, *, target_value: jsii.Number, customized_scaling_metric_specification: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnScalingPlan.CustomizedScalingMetricSpecificationProperty"]]]=None, disable_scale_in: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, estimated_instance_warmup: typing.Optional[jsii.Number]=None, predefined_scaling_metric_specification: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnScalingPlan.PredefinedScalingMetricSpecificationProperty"]]]=None, scale_in_cooldown: typing.Optional[jsii.Number]=None, scale_out_cooldown: typing.Optional[jsii.Number]=None):
            """
            :param target_value: ``CfnScalingPlan.TargetTrackingConfigurationProperty.TargetValue``.
            :param customized_scaling_metric_specification: ``CfnScalingPlan.TargetTrackingConfigurationProperty.CustomizedScalingMetricSpecification``.
            :param disable_scale_in: ``CfnScalingPlan.TargetTrackingConfigurationProperty.DisableScaleIn``.
            :param estimated_instance_warmup: ``CfnScalingPlan.TargetTrackingConfigurationProperty.EstimatedInstanceWarmup``.
            :param predefined_scaling_metric_specification: ``CfnScalingPlan.TargetTrackingConfigurationProperty.PredefinedScalingMetricSpecification``.
            :param scale_in_cooldown: ``CfnScalingPlan.TargetTrackingConfigurationProperty.ScaleInCooldown``.
            :param scale_out_cooldown: ``CfnScalingPlan.TargetTrackingConfigurationProperty.ScaleOutCooldown``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-autoscalingplans-scalingplan-targettrackingconfiguration.html
            """
            self._values = {
                'target_value': target_value,
            }
            if customized_scaling_metric_specification is not None: self._values["customized_scaling_metric_specification"] = customized_scaling_metric_specification
            if disable_scale_in is not None: self._values["disable_scale_in"] = disable_scale_in
            if estimated_instance_warmup is not None: self._values["estimated_instance_warmup"] = estimated_instance_warmup
            if predefined_scaling_metric_specification is not None: self._values["predefined_scaling_metric_specification"] = predefined_scaling_metric_specification
            if scale_in_cooldown is not None: self._values["scale_in_cooldown"] = scale_in_cooldown
            if scale_out_cooldown is not None: self._values["scale_out_cooldown"] = scale_out_cooldown

        @property
        def target_value(self) -> jsii.Number:
            """``CfnScalingPlan.TargetTrackingConfigurationProperty.TargetValue``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-autoscalingplans-scalingplan-targettrackingconfiguration.html#cfn-autoscalingplans-scalingplan-targettrackingconfiguration-targetvalue
            """
            return self._values.get('target_value')

        @property
        def customized_scaling_metric_specification(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnScalingPlan.CustomizedScalingMetricSpecificationProperty"]]]:
            """``CfnScalingPlan.TargetTrackingConfigurationProperty.CustomizedScalingMetricSpecification``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-autoscalingplans-scalingplan-targettrackingconfiguration.html#cfn-autoscalingplans-scalingplan-targettrackingconfiguration-customizedscalingmetricspecification
            """
            return self._values.get('customized_scaling_metric_specification')

        @property
        def disable_scale_in(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
            """``CfnScalingPlan.TargetTrackingConfigurationProperty.DisableScaleIn``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-autoscalingplans-scalingplan-targettrackingconfiguration.html#cfn-autoscalingplans-scalingplan-targettrackingconfiguration-disablescalein
            """
            return self._values.get('disable_scale_in')

        @property
        def estimated_instance_warmup(self) -> typing.Optional[jsii.Number]:
            """``CfnScalingPlan.TargetTrackingConfigurationProperty.EstimatedInstanceWarmup``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-autoscalingplans-scalingplan-targettrackingconfiguration.html#cfn-autoscalingplans-scalingplan-targettrackingconfiguration-estimatedinstancewarmup
            """
            return self._values.get('estimated_instance_warmup')

        @property
        def predefined_scaling_metric_specification(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnScalingPlan.PredefinedScalingMetricSpecificationProperty"]]]:
            """``CfnScalingPlan.TargetTrackingConfigurationProperty.PredefinedScalingMetricSpecification``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-autoscalingplans-scalingplan-targettrackingconfiguration.html#cfn-autoscalingplans-scalingplan-targettrackingconfiguration-predefinedscalingmetricspecification
            """
            return self._values.get('predefined_scaling_metric_specification')

        @property
        def scale_in_cooldown(self) -> typing.Optional[jsii.Number]:
            """``CfnScalingPlan.TargetTrackingConfigurationProperty.ScaleInCooldown``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-autoscalingplans-scalingplan-targettrackingconfiguration.html#cfn-autoscalingplans-scalingplan-targettrackingconfiguration-scaleincooldown
            """
            return self._values.get('scale_in_cooldown')

        @property
        def scale_out_cooldown(self) -> typing.Optional[jsii.Number]:
            """``CfnScalingPlan.TargetTrackingConfigurationProperty.ScaleOutCooldown``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-autoscalingplans-scalingplan-targettrackingconfiguration.html#cfn-autoscalingplans-scalingplan-targettrackingconfiguration-scaleoutcooldown
            """
            return self._values.get('scale_out_cooldown')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'TargetTrackingConfigurationProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



@jsii.data_type(jsii_type="@aws-cdk/aws-autoscalingplans.CfnScalingPlanProps", jsii_struct_bases=[], name_mapping={'application_source': 'applicationSource', 'scaling_instructions': 'scalingInstructions'})
class CfnScalingPlanProps():
    def __init__(self, *, application_source: typing.Union["CfnScalingPlan.ApplicationSourceProperty", aws_cdk.core.IResolvable], scaling_instructions: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnScalingPlan.ScalingInstructionProperty"]]]):
        """Properties for defining a ``AWS::AutoScalingPlans::ScalingPlan``.

        :param application_source: ``AWS::AutoScalingPlans::ScalingPlan.ApplicationSource``.
        :param scaling_instructions: ``AWS::AutoScalingPlans::ScalingPlan.ScalingInstructions``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-autoscalingplans-scalingplan.html
        """
        self._values = {
            'application_source': application_source,
            'scaling_instructions': scaling_instructions,
        }

    @property
    def application_source(self) -> typing.Union["CfnScalingPlan.ApplicationSourceProperty", aws_cdk.core.IResolvable]:
        """``AWS::AutoScalingPlans::ScalingPlan.ApplicationSource``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-autoscalingplans-scalingplan.html#cfn-autoscalingplans-scalingplan-applicationsource
        """
        return self._values.get('application_source')

    @property
    def scaling_instructions(self) -> typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnScalingPlan.ScalingInstructionProperty"]]]:
        """``AWS::AutoScalingPlans::ScalingPlan.ScalingInstructions``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-autoscalingplans-scalingplan.html#cfn-autoscalingplans-scalingplan-scalinginstructions
        """
        return self._values.get('scaling_instructions')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnScalingPlanProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


__all__ = ["CfnScalingPlan", "CfnScalingPlanProps", "__jsii_assembly__"]

publication.publish()
