import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.core
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-dlm", "1.15.0", __name__, "aws-dlm@1.15.0.jsii.tgz")
class CfnLifecyclePolicy(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-dlm.CfnLifecyclePolicy"):
    """A CloudFormation ``AWS::DLM::LifecyclePolicy``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dlm-lifecyclepolicy.html
    cloudformationResource:
    :cloudformationResource:: AWS::DLM::LifecyclePolicy
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, description: typing.Optional[str]=None, execution_role_arn: typing.Optional[str]=None, policy_details: typing.Optional[typing.Union[typing.Optional["PolicyDetailsProperty"], typing.Optional[aws_cdk.core.IResolvable]]]=None, state: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::DLM::LifecyclePolicy``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param description: ``AWS::DLM::LifecyclePolicy.Description``.
        :param execution_role_arn: ``AWS::DLM::LifecyclePolicy.ExecutionRoleArn``.
        :param policy_details: ``AWS::DLM::LifecyclePolicy.PolicyDetails``.
        :param state: ``AWS::DLM::LifecyclePolicy.State``.
        """
        props = CfnLifecyclePolicyProps(description=description, execution_role_arn=execution_role_arn, policy_details=policy_details, state=state)

        jsii.create(CfnLifecyclePolicy, self, [scope, id, props])

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
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[str]:
        """``AWS::DLM::LifecyclePolicy.Description``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dlm-lifecyclepolicy.html#cfn-dlm-lifecyclepolicy-description
        """
        return jsii.get(self, "description")

    @description.setter
    def description(self, value: typing.Optional[str]):
        return jsii.set(self, "description", value)

    @property
    @jsii.member(jsii_name="executionRoleArn")
    def execution_role_arn(self) -> typing.Optional[str]:
        """``AWS::DLM::LifecyclePolicy.ExecutionRoleArn``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dlm-lifecyclepolicy.html#cfn-dlm-lifecyclepolicy-executionrolearn
        """
        return jsii.get(self, "executionRoleArn")

    @execution_role_arn.setter
    def execution_role_arn(self, value: typing.Optional[str]):
        return jsii.set(self, "executionRoleArn", value)

    @property
    @jsii.member(jsii_name="policyDetails")
    def policy_details(self) -> typing.Optional[typing.Union[typing.Optional["PolicyDetailsProperty"], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::DLM::LifecyclePolicy.PolicyDetails``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dlm-lifecyclepolicy.html#cfn-dlm-lifecyclepolicy-policydetails
        """
        return jsii.get(self, "policyDetails")

    @policy_details.setter
    def policy_details(self, value: typing.Optional[typing.Union[typing.Optional["PolicyDetailsProperty"], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "policyDetails", value)

    @property
    @jsii.member(jsii_name="state")
    def state(self) -> typing.Optional[str]:
        """``AWS::DLM::LifecyclePolicy.State``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dlm-lifecyclepolicy.html#cfn-dlm-lifecyclepolicy-state
        """
        return jsii.get(self, "state")

    @state.setter
    def state(self, value: typing.Optional[str]):
        return jsii.set(self, "state", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-dlm.CfnLifecyclePolicy.CreateRuleProperty", jsii_struct_bases=[], name_mapping={'interval': 'interval', 'interval_unit': 'intervalUnit', 'times': 'times'})
    class CreateRuleProperty():
        def __init__(self, *, interval: jsii.Number, interval_unit: str, times: typing.Optional[typing.List[str]]=None):
            """
            :param interval: ``CfnLifecyclePolicy.CreateRuleProperty.Interval``.
            :param interval_unit: ``CfnLifecyclePolicy.CreateRuleProperty.IntervalUnit``.
            :param times: ``CfnLifecyclePolicy.CreateRuleProperty.Times``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dlm-lifecyclepolicy-createrule.html
            """
            self._values = {
                'interval': interval,
                'interval_unit': interval_unit,
            }
            if times is not None: self._values["times"] = times

        @property
        def interval(self) -> jsii.Number:
            """``CfnLifecyclePolicy.CreateRuleProperty.Interval``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dlm-lifecyclepolicy-createrule.html#cfn-dlm-lifecyclepolicy-createrule-interval
            """
            return self._values.get('interval')

        @property
        def interval_unit(self) -> str:
            """``CfnLifecyclePolicy.CreateRuleProperty.IntervalUnit``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dlm-lifecyclepolicy-createrule.html#cfn-dlm-lifecyclepolicy-createrule-intervalunit
            """
            return self._values.get('interval_unit')

        @property
        def times(self) -> typing.Optional[typing.List[str]]:
            """``CfnLifecyclePolicy.CreateRuleProperty.Times``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dlm-lifecyclepolicy-createrule.html#cfn-dlm-lifecyclepolicy-createrule-times
            """
            return self._values.get('times')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'CreateRuleProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-dlm.CfnLifecyclePolicy.ParametersProperty", jsii_struct_bases=[], name_mapping={'exclude_boot_volume': 'excludeBootVolume'})
    class ParametersProperty():
        def __init__(self, *, exclude_boot_volume: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None):
            """
            :param exclude_boot_volume: ``CfnLifecyclePolicy.ParametersProperty.ExcludeBootVolume``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dlm-lifecyclepolicy-parameters.html
            """
            self._values = {
            }
            if exclude_boot_volume is not None: self._values["exclude_boot_volume"] = exclude_boot_volume

        @property
        def exclude_boot_volume(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
            """``CfnLifecyclePolicy.ParametersProperty.ExcludeBootVolume``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dlm-lifecyclepolicy-parameters.html#cfn-dlm-lifecyclepolicy-parameters-excludebootvolume
            """
            return self._values.get('exclude_boot_volume')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'ParametersProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-dlm.CfnLifecyclePolicy.PolicyDetailsProperty", jsii_struct_bases=[], name_mapping={'parameters': 'parameters', 'policy_type': 'policyType', 'resource_types': 'resourceTypes', 'schedules': 'schedules', 'target_tags': 'targetTags'})
    class PolicyDetailsProperty():
        def __init__(self, *, parameters: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnLifecyclePolicy.ParametersProperty"]]]=None, policy_type: typing.Optional[str]=None, resource_types: typing.Optional[typing.List[str]]=None, schedules: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnLifecyclePolicy.ScheduleProperty"]]]]]=None, target_tags: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, aws_cdk.core.CfnTag]]]]]=None):
            """
            :param parameters: ``CfnLifecyclePolicy.PolicyDetailsProperty.Parameters``.
            :param policy_type: ``CfnLifecyclePolicy.PolicyDetailsProperty.PolicyType``.
            :param resource_types: ``CfnLifecyclePolicy.PolicyDetailsProperty.ResourceTypes``.
            :param schedules: ``CfnLifecyclePolicy.PolicyDetailsProperty.Schedules``.
            :param target_tags: ``CfnLifecyclePolicy.PolicyDetailsProperty.TargetTags``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dlm-lifecyclepolicy-policydetails.html
            """
            self._values = {
            }
            if parameters is not None: self._values["parameters"] = parameters
            if policy_type is not None: self._values["policy_type"] = policy_type
            if resource_types is not None: self._values["resource_types"] = resource_types
            if schedules is not None: self._values["schedules"] = schedules
            if target_tags is not None: self._values["target_tags"] = target_tags

        @property
        def parameters(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnLifecyclePolicy.ParametersProperty"]]]:
            """``CfnLifecyclePolicy.PolicyDetailsProperty.Parameters``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dlm-lifecyclepolicy-policydetails.html#cfn-dlm-lifecyclepolicy-policydetails-parameters
            """
            return self._values.get('parameters')

        @property
        def policy_type(self) -> typing.Optional[str]:
            """``CfnLifecyclePolicy.PolicyDetailsProperty.PolicyType``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dlm-lifecyclepolicy-policydetails.html#cfn-dlm-lifecyclepolicy-policydetails-policytype
            """
            return self._values.get('policy_type')

        @property
        def resource_types(self) -> typing.Optional[typing.List[str]]:
            """``CfnLifecyclePolicy.PolicyDetailsProperty.ResourceTypes``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dlm-lifecyclepolicy-policydetails.html#cfn-dlm-lifecyclepolicy-policydetails-resourcetypes
            """
            return self._values.get('resource_types')

        @property
        def schedules(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnLifecyclePolicy.ScheduleProperty"]]]]]:
            """``CfnLifecyclePolicy.PolicyDetailsProperty.Schedules``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dlm-lifecyclepolicy-policydetails.html#cfn-dlm-lifecyclepolicy-policydetails-schedules
            """
            return self._values.get('schedules')

        @property
        def target_tags(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, aws_cdk.core.CfnTag]]]]]:
            """``CfnLifecyclePolicy.PolicyDetailsProperty.TargetTags``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dlm-lifecyclepolicy-policydetails.html#cfn-dlm-lifecyclepolicy-policydetails-targettags
            """
            return self._values.get('target_tags')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'PolicyDetailsProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-dlm.CfnLifecyclePolicy.RetainRuleProperty", jsii_struct_bases=[], name_mapping={'count': 'count'})
    class RetainRuleProperty():
        def __init__(self, *, count: jsii.Number):
            """
            :param count: ``CfnLifecyclePolicy.RetainRuleProperty.Count``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dlm-lifecyclepolicy-retainrule.html
            """
            self._values = {
                'count': count,
            }

        @property
        def count(self) -> jsii.Number:
            """``CfnLifecyclePolicy.RetainRuleProperty.Count``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dlm-lifecyclepolicy-retainrule.html#cfn-dlm-lifecyclepolicy-retainrule-count
            """
            return self._values.get('count')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'RetainRuleProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-dlm.CfnLifecyclePolicy.ScheduleProperty", jsii_struct_bases=[], name_mapping={'copy_tags': 'copyTags', 'create_rule': 'createRule', 'name': 'name', 'retain_rule': 'retainRule', 'tags_to_add': 'tagsToAdd', 'variable_tags': 'variableTags'})
    class ScheduleProperty():
        def __init__(self, *, copy_tags: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, create_rule: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnLifecyclePolicy.CreateRuleProperty"]]]=None, name: typing.Optional[str]=None, retain_rule: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnLifecyclePolicy.RetainRuleProperty"]]]=None, tags_to_add: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, aws_cdk.core.CfnTag]]]]]=None, variable_tags: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, aws_cdk.core.CfnTag]]]]]=None):
            """
            :param copy_tags: ``CfnLifecyclePolicy.ScheduleProperty.CopyTags``.
            :param create_rule: ``CfnLifecyclePolicy.ScheduleProperty.CreateRule``.
            :param name: ``CfnLifecyclePolicy.ScheduleProperty.Name``.
            :param retain_rule: ``CfnLifecyclePolicy.ScheduleProperty.RetainRule``.
            :param tags_to_add: ``CfnLifecyclePolicy.ScheduleProperty.TagsToAdd``.
            :param variable_tags: ``CfnLifecyclePolicy.ScheduleProperty.VariableTags``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dlm-lifecyclepolicy-schedule.html
            """
            self._values = {
            }
            if copy_tags is not None: self._values["copy_tags"] = copy_tags
            if create_rule is not None: self._values["create_rule"] = create_rule
            if name is not None: self._values["name"] = name
            if retain_rule is not None: self._values["retain_rule"] = retain_rule
            if tags_to_add is not None: self._values["tags_to_add"] = tags_to_add
            if variable_tags is not None: self._values["variable_tags"] = variable_tags

        @property
        def copy_tags(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
            """``CfnLifecyclePolicy.ScheduleProperty.CopyTags``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dlm-lifecyclepolicy-schedule.html#cfn-dlm-lifecyclepolicy-schedule-copytags
            """
            return self._values.get('copy_tags')

        @property
        def create_rule(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnLifecyclePolicy.CreateRuleProperty"]]]:
            """``CfnLifecyclePolicy.ScheduleProperty.CreateRule``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dlm-lifecyclepolicy-schedule.html#cfn-dlm-lifecyclepolicy-schedule-createrule
            """
            return self._values.get('create_rule')

        @property
        def name(self) -> typing.Optional[str]:
            """``CfnLifecyclePolicy.ScheduleProperty.Name``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dlm-lifecyclepolicy-schedule.html#cfn-dlm-lifecyclepolicy-schedule-name
            """
            return self._values.get('name')

        @property
        def retain_rule(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnLifecyclePolicy.RetainRuleProperty"]]]:
            """``CfnLifecyclePolicy.ScheduleProperty.RetainRule``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dlm-lifecyclepolicy-schedule.html#cfn-dlm-lifecyclepolicy-schedule-retainrule
            """
            return self._values.get('retain_rule')

        @property
        def tags_to_add(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, aws_cdk.core.CfnTag]]]]]:
            """``CfnLifecyclePolicy.ScheduleProperty.TagsToAdd``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dlm-lifecyclepolicy-schedule.html#cfn-dlm-lifecyclepolicy-schedule-tagstoadd
            """
            return self._values.get('tags_to_add')

        @property
        def variable_tags(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, aws_cdk.core.CfnTag]]]]]:
            """``CfnLifecyclePolicy.ScheduleProperty.VariableTags``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dlm-lifecyclepolicy-schedule.html#cfn-dlm-lifecyclepolicy-schedule-variabletags
            """
            return self._values.get('variable_tags')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'ScheduleProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



@jsii.data_type(jsii_type="@aws-cdk/aws-dlm.CfnLifecyclePolicyProps", jsii_struct_bases=[], name_mapping={'description': 'description', 'execution_role_arn': 'executionRoleArn', 'policy_details': 'policyDetails', 'state': 'state'})
class CfnLifecyclePolicyProps():
    def __init__(self, *, description: typing.Optional[str]=None, execution_role_arn: typing.Optional[str]=None, policy_details: typing.Optional[typing.Union[typing.Optional["CfnLifecyclePolicy.PolicyDetailsProperty"], typing.Optional[aws_cdk.core.IResolvable]]]=None, state: typing.Optional[str]=None):
        """Properties for defining a ``AWS::DLM::LifecyclePolicy``.

        :param description: ``AWS::DLM::LifecyclePolicy.Description``.
        :param execution_role_arn: ``AWS::DLM::LifecyclePolicy.ExecutionRoleArn``.
        :param policy_details: ``AWS::DLM::LifecyclePolicy.PolicyDetails``.
        :param state: ``AWS::DLM::LifecyclePolicy.State``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dlm-lifecyclepolicy.html
        """
        self._values = {
        }
        if description is not None: self._values["description"] = description
        if execution_role_arn is not None: self._values["execution_role_arn"] = execution_role_arn
        if policy_details is not None: self._values["policy_details"] = policy_details
        if state is not None: self._values["state"] = state

    @property
    def description(self) -> typing.Optional[str]:
        """``AWS::DLM::LifecyclePolicy.Description``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dlm-lifecyclepolicy.html#cfn-dlm-lifecyclepolicy-description
        """
        return self._values.get('description')

    @property
    def execution_role_arn(self) -> typing.Optional[str]:
        """``AWS::DLM::LifecyclePolicy.ExecutionRoleArn``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dlm-lifecyclepolicy.html#cfn-dlm-lifecyclepolicy-executionrolearn
        """
        return self._values.get('execution_role_arn')

    @property
    def policy_details(self) -> typing.Optional[typing.Union[typing.Optional["CfnLifecyclePolicy.PolicyDetailsProperty"], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::DLM::LifecyclePolicy.PolicyDetails``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dlm-lifecyclepolicy.html#cfn-dlm-lifecyclepolicy-policydetails
        """
        return self._values.get('policy_details')

    @property
    def state(self) -> typing.Optional[str]:
        """``AWS::DLM::LifecyclePolicy.State``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dlm-lifecyclepolicy.html#cfn-dlm-lifecyclepolicy-state
        """
        return self._values.get('state')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnLifecyclePolicyProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


__all__ = ["CfnLifecyclePolicy", "CfnLifecyclePolicyProps", "__jsii_assembly__"]

publication.publish()
