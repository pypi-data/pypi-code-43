import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.core
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-backup", "1.15.0", __name__, "aws-backup@1.15.0.jsii.tgz")
class CfnBackupPlan(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-backup.CfnBackupPlan"):
    """A CloudFormation ``AWS::Backup::BackupPlan``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-backup-backupplan.html
    cloudformationResource:
    :cloudformationResource:: AWS::Backup::BackupPlan
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, backup_plan: typing.Union["BackupPlanResourceTypeProperty", aws_cdk.core.IResolvable], backup_plan_tags: typing.Any=None) -> None:
        """Create a new ``AWS::Backup::BackupPlan``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param backup_plan: ``AWS::Backup::BackupPlan.BackupPlan``.
        :param backup_plan_tags: ``AWS::Backup::BackupPlan.BackupPlanTags``.
        """
        props = CfnBackupPlanProps(backup_plan=backup_plan, backup_plan_tags=backup_plan_tags)

        jsii.create(CfnBackupPlan, self, [scope, id, props])

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
    @jsii.member(jsii_name="attrBackupPlanArn")
    def attr_backup_plan_arn(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: BackupPlanArn
        """
        return jsii.get(self, "attrBackupPlanArn")

    @property
    @jsii.member(jsii_name="attrBackupPlanId")
    def attr_backup_plan_id(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: BackupPlanId
        """
        return jsii.get(self, "attrBackupPlanId")

    @property
    @jsii.member(jsii_name="attrVersionId")
    def attr_version_id(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: VersionId
        """
        return jsii.get(self, "attrVersionId")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="backupPlan")
    def backup_plan(self) -> typing.Union["BackupPlanResourceTypeProperty", aws_cdk.core.IResolvable]:
        """``AWS::Backup::BackupPlan.BackupPlan``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-backup-backupplan.html#cfn-backup-backupplan-backupplan
        """
        return jsii.get(self, "backupPlan")

    @backup_plan.setter
    def backup_plan(self, value: typing.Union["BackupPlanResourceTypeProperty", aws_cdk.core.IResolvable]):
        return jsii.set(self, "backupPlan", value)

    @property
    @jsii.member(jsii_name="backupPlanTags")
    def backup_plan_tags(self) -> typing.Any:
        """``AWS::Backup::BackupPlan.BackupPlanTags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-backup-backupplan.html#cfn-backup-backupplan-backupplantags
        """
        return jsii.get(self, "backupPlanTags")

    @backup_plan_tags.setter
    def backup_plan_tags(self, value: typing.Any):
        return jsii.set(self, "backupPlanTags", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-backup.CfnBackupPlan.BackupPlanResourceTypeProperty", jsii_struct_bases=[], name_mapping={'backup_plan_name': 'backupPlanName', 'backup_plan_rule': 'backupPlanRule'})
    class BackupPlanResourceTypeProperty():
        def __init__(self, *, backup_plan_name: str, backup_plan_rule: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnBackupPlan.BackupRuleResourceTypeProperty"]]]):
            """
            :param backup_plan_name: ``CfnBackupPlan.BackupPlanResourceTypeProperty.BackupPlanName``.
            :param backup_plan_rule: ``CfnBackupPlan.BackupPlanResourceTypeProperty.BackupPlanRule``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-backup-backupplan-backupplanresourcetype.html
            """
            self._values = {
                'backup_plan_name': backup_plan_name,
                'backup_plan_rule': backup_plan_rule,
            }

        @property
        def backup_plan_name(self) -> str:
            """``CfnBackupPlan.BackupPlanResourceTypeProperty.BackupPlanName``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-backup-backupplan-backupplanresourcetype.html#cfn-backup-backupplan-backupplanresourcetype-backupplanname
            """
            return self._values.get('backup_plan_name')

        @property
        def backup_plan_rule(self) -> typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnBackupPlan.BackupRuleResourceTypeProperty"]]]:
            """``CfnBackupPlan.BackupPlanResourceTypeProperty.BackupPlanRule``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-backup-backupplan-backupplanresourcetype.html#cfn-backup-backupplan-backupplanresourcetype-backupplanrule
            """
            return self._values.get('backup_plan_rule')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'BackupPlanResourceTypeProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-backup.CfnBackupPlan.BackupRuleResourceTypeProperty", jsii_struct_bases=[], name_mapping={'rule_name': 'ruleName', 'target_backup_vault': 'targetBackupVault', 'completion_window_minutes': 'completionWindowMinutes', 'lifecycle': 'lifecycle', 'recovery_point_tags': 'recoveryPointTags', 'schedule_expression': 'scheduleExpression', 'start_window_minutes': 'startWindowMinutes'})
    class BackupRuleResourceTypeProperty():
        def __init__(self, *, rule_name: str, target_backup_vault: str, completion_window_minutes: typing.Optional[jsii.Number]=None, lifecycle: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnBackupPlan.LifecycleResourceTypeProperty"]]]=None, recovery_point_tags: typing.Any=None, schedule_expression: typing.Optional[str]=None, start_window_minutes: typing.Optional[jsii.Number]=None):
            """
            :param rule_name: ``CfnBackupPlan.BackupRuleResourceTypeProperty.RuleName``.
            :param target_backup_vault: ``CfnBackupPlan.BackupRuleResourceTypeProperty.TargetBackupVault``.
            :param completion_window_minutes: ``CfnBackupPlan.BackupRuleResourceTypeProperty.CompletionWindowMinutes``.
            :param lifecycle: ``CfnBackupPlan.BackupRuleResourceTypeProperty.Lifecycle``.
            :param recovery_point_tags: ``CfnBackupPlan.BackupRuleResourceTypeProperty.RecoveryPointTags``.
            :param schedule_expression: ``CfnBackupPlan.BackupRuleResourceTypeProperty.ScheduleExpression``.
            :param start_window_minutes: ``CfnBackupPlan.BackupRuleResourceTypeProperty.StartWindowMinutes``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-backup-backupplan-backupruleresourcetype.html
            """
            self._values = {
                'rule_name': rule_name,
                'target_backup_vault': target_backup_vault,
            }
            if completion_window_minutes is not None: self._values["completion_window_minutes"] = completion_window_minutes
            if lifecycle is not None: self._values["lifecycle"] = lifecycle
            if recovery_point_tags is not None: self._values["recovery_point_tags"] = recovery_point_tags
            if schedule_expression is not None: self._values["schedule_expression"] = schedule_expression
            if start_window_minutes is not None: self._values["start_window_minutes"] = start_window_minutes

        @property
        def rule_name(self) -> str:
            """``CfnBackupPlan.BackupRuleResourceTypeProperty.RuleName``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-backup-backupplan-backupruleresourcetype.html#cfn-backup-backupplan-backupruleresourcetype-rulename
            """
            return self._values.get('rule_name')

        @property
        def target_backup_vault(self) -> str:
            """``CfnBackupPlan.BackupRuleResourceTypeProperty.TargetBackupVault``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-backup-backupplan-backupruleresourcetype.html#cfn-backup-backupplan-backupruleresourcetype-targetbackupvault
            """
            return self._values.get('target_backup_vault')

        @property
        def completion_window_minutes(self) -> typing.Optional[jsii.Number]:
            """``CfnBackupPlan.BackupRuleResourceTypeProperty.CompletionWindowMinutes``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-backup-backupplan-backupruleresourcetype.html#cfn-backup-backupplan-backupruleresourcetype-completionwindowminutes
            """
            return self._values.get('completion_window_minutes')

        @property
        def lifecycle(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnBackupPlan.LifecycleResourceTypeProperty"]]]:
            """``CfnBackupPlan.BackupRuleResourceTypeProperty.Lifecycle``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-backup-backupplan-backupruleresourcetype.html#cfn-backup-backupplan-backupruleresourcetype-lifecycle
            """
            return self._values.get('lifecycle')

        @property
        def recovery_point_tags(self) -> typing.Any:
            """``CfnBackupPlan.BackupRuleResourceTypeProperty.RecoveryPointTags``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-backup-backupplan-backupruleresourcetype.html#cfn-backup-backupplan-backupruleresourcetype-recoverypointtags
            """
            return self._values.get('recovery_point_tags')

        @property
        def schedule_expression(self) -> typing.Optional[str]:
            """``CfnBackupPlan.BackupRuleResourceTypeProperty.ScheduleExpression``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-backup-backupplan-backupruleresourcetype.html#cfn-backup-backupplan-backupruleresourcetype-scheduleexpression
            """
            return self._values.get('schedule_expression')

        @property
        def start_window_minutes(self) -> typing.Optional[jsii.Number]:
            """``CfnBackupPlan.BackupRuleResourceTypeProperty.StartWindowMinutes``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-backup-backupplan-backupruleresourcetype.html#cfn-backup-backupplan-backupruleresourcetype-startwindowminutes
            """
            return self._values.get('start_window_minutes')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'BackupRuleResourceTypeProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-backup.CfnBackupPlan.LifecycleResourceTypeProperty", jsii_struct_bases=[], name_mapping={'delete_after_days': 'deleteAfterDays', 'move_to_cold_storage_after_days': 'moveToColdStorageAfterDays'})
    class LifecycleResourceTypeProperty():
        def __init__(self, *, delete_after_days: typing.Optional[jsii.Number]=None, move_to_cold_storage_after_days: typing.Optional[jsii.Number]=None):
            """
            :param delete_after_days: ``CfnBackupPlan.LifecycleResourceTypeProperty.DeleteAfterDays``.
            :param move_to_cold_storage_after_days: ``CfnBackupPlan.LifecycleResourceTypeProperty.MoveToColdStorageAfterDays``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-backup-backupplan-lifecycleresourcetype.html
            """
            self._values = {
            }
            if delete_after_days is not None: self._values["delete_after_days"] = delete_after_days
            if move_to_cold_storage_after_days is not None: self._values["move_to_cold_storage_after_days"] = move_to_cold_storage_after_days

        @property
        def delete_after_days(self) -> typing.Optional[jsii.Number]:
            """``CfnBackupPlan.LifecycleResourceTypeProperty.DeleteAfterDays``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-backup-backupplan-lifecycleresourcetype.html#cfn-backup-backupplan-lifecycleresourcetype-deleteafterdays
            """
            return self._values.get('delete_after_days')

        @property
        def move_to_cold_storage_after_days(self) -> typing.Optional[jsii.Number]:
            """``CfnBackupPlan.LifecycleResourceTypeProperty.MoveToColdStorageAfterDays``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-backup-backupplan-lifecycleresourcetype.html#cfn-backup-backupplan-lifecycleresourcetype-movetocoldstorageafterdays
            """
            return self._values.get('move_to_cold_storage_after_days')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'LifecycleResourceTypeProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



@jsii.data_type(jsii_type="@aws-cdk/aws-backup.CfnBackupPlanProps", jsii_struct_bases=[], name_mapping={'backup_plan': 'backupPlan', 'backup_plan_tags': 'backupPlanTags'})
class CfnBackupPlanProps():
    def __init__(self, *, backup_plan: typing.Union["CfnBackupPlan.BackupPlanResourceTypeProperty", aws_cdk.core.IResolvable], backup_plan_tags: typing.Any=None):
        """Properties for defining a ``AWS::Backup::BackupPlan``.

        :param backup_plan: ``AWS::Backup::BackupPlan.BackupPlan``.
        :param backup_plan_tags: ``AWS::Backup::BackupPlan.BackupPlanTags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-backup-backupplan.html
        """
        self._values = {
            'backup_plan': backup_plan,
        }
        if backup_plan_tags is not None: self._values["backup_plan_tags"] = backup_plan_tags

    @property
    def backup_plan(self) -> typing.Union["CfnBackupPlan.BackupPlanResourceTypeProperty", aws_cdk.core.IResolvable]:
        """``AWS::Backup::BackupPlan.BackupPlan``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-backup-backupplan.html#cfn-backup-backupplan-backupplan
        """
        return self._values.get('backup_plan')

    @property
    def backup_plan_tags(self) -> typing.Any:
        """``AWS::Backup::BackupPlan.BackupPlanTags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-backup-backupplan.html#cfn-backup-backupplan-backupplantags
        """
        return self._values.get('backup_plan_tags')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnBackupPlanProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnBackupSelection(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-backup.CfnBackupSelection"):
    """A CloudFormation ``AWS::Backup::BackupSelection``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-backup-backupselection.html
    cloudformationResource:
    :cloudformationResource:: AWS::Backup::BackupSelection
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, backup_plan_id: str, backup_selection: typing.Union[aws_cdk.core.IResolvable, "BackupSelectionResourceTypeProperty"]) -> None:
        """Create a new ``AWS::Backup::BackupSelection``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param backup_plan_id: ``AWS::Backup::BackupSelection.BackupPlanId``.
        :param backup_selection: ``AWS::Backup::BackupSelection.BackupSelection``.
        """
        props = CfnBackupSelectionProps(backup_plan_id=backup_plan_id, backup_selection=backup_selection)

        jsii.create(CfnBackupSelection, self, [scope, id, props])

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
    @jsii.member(jsii_name="attrBackupPlanId")
    def attr_backup_plan_id(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: BackupPlanId
        """
        return jsii.get(self, "attrBackupPlanId")

    @property
    @jsii.member(jsii_name="attrSelectionId")
    def attr_selection_id(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: SelectionId
        """
        return jsii.get(self, "attrSelectionId")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="backupPlanId")
    def backup_plan_id(self) -> str:
        """``AWS::Backup::BackupSelection.BackupPlanId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-backup-backupselection.html#cfn-backup-backupselection-backupplanid
        """
        return jsii.get(self, "backupPlanId")

    @backup_plan_id.setter
    def backup_plan_id(self, value: str):
        return jsii.set(self, "backupPlanId", value)

    @property
    @jsii.member(jsii_name="backupSelection")
    def backup_selection(self) -> typing.Union[aws_cdk.core.IResolvable, "BackupSelectionResourceTypeProperty"]:
        """``AWS::Backup::BackupSelection.BackupSelection``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-backup-backupselection.html#cfn-backup-backupselection-backupselection
        """
        return jsii.get(self, "backupSelection")

    @backup_selection.setter
    def backup_selection(self, value: typing.Union[aws_cdk.core.IResolvable, "BackupSelectionResourceTypeProperty"]):
        return jsii.set(self, "backupSelection", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-backup.CfnBackupSelection.BackupSelectionResourceTypeProperty", jsii_struct_bases=[], name_mapping={'iam_role_arn': 'iamRoleArn', 'selection_name': 'selectionName', 'list_of_tags': 'listOfTags', 'resources': 'resources'})
    class BackupSelectionResourceTypeProperty():
        def __init__(self, *, iam_role_arn: str, selection_name: str, list_of_tags: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnBackupSelection.ConditionResourceTypeProperty"]]]]]=None, resources: typing.Optional[typing.List[str]]=None):
            """
            :param iam_role_arn: ``CfnBackupSelection.BackupSelectionResourceTypeProperty.IamRoleArn``.
            :param selection_name: ``CfnBackupSelection.BackupSelectionResourceTypeProperty.SelectionName``.
            :param list_of_tags: ``CfnBackupSelection.BackupSelectionResourceTypeProperty.ListOfTags``.
            :param resources: ``CfnBackupSelection.BackupSelectionResourceTypeProperty.Resources``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-backup-backupselection-backupselectionresourcetype.html
            """
            self._values = {
                'iam_role_arn': iam_role_arn,
                'selection_name': selection_name,
            }
            if list_of_tags is not None: self._values["list_of_tags"] = list_of_tags
            if resources is not None: self._values["resources"] = resources

        @property
        def iam_role_arn(self) -> str:
            """``CfnBackupSelection.BackupSelectionResourceTypeProperty.IamRoleArn``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-backup-backupselection-backupselectionresourcetype.html#cfn-backup-backupselection-backupselectionresourcetype-iamrolearn
            """
            return self._values.get('iam_role_arn')

        @property
        def selection_name(self) -> str:
            """``CfnBackupSelection.BackupSelectionResourceTypeProperty.SelectionName``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-backup-backupselection-backupselectionresourcetype.html#cfn-backup-backupselection-backupselectionresourcetype-selectionname
            """
            return self._values.get('selection_name')

        @property
        def list_of_tags(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnBackupSelection.ConditionResourceTypeProperty"]]]]]:
            """``CfnBackupSelection.BackupSelectionResourceTypeProperty.ListOfTags``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-backup-backupselection-backupselectionresourcetype.html#cfn-backup-backupselection-backupselectionresourcetype-listoftags
            """
            return self._values.get('list_of_tags')

        @property
        def resources(self) -> typing.Optional[typing.List[str]]:
            """``CfnBackupSelection.BackupSelectionResourceTypeProperty.Resources``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-backup-backupselection-backupselectionresourcetype.html#cfn-backup-backupselection-backupselectionresourcetype-resources
            """
            return self._values.get('resources')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'BackupSelectionResourceTypeProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-backup.CfnBackupSelection.ConditionResourceTypeProperty", jsii_struct_bases=[], name_mapping={'condition_key': 'conditionKey', 'condition_type': 'conditionType', 'condition_value': 'conditionValue'})
    class ConditionResourceTypeProperty():
        def __init__(self, *, condition_key: str, condition_type: str, condition_value: str):
            """
            :param condition_key: ``CfnBackupSelection.ConditionResourceTypeProperty.ConditionKey``.
            :param condition_type: ``CfnBackupSelection.ConditionResourceTypeProperty.ConditionType``.
            :param condition_value: ``CfnBackupSelection.ConditionResourceTypeProperty.ConditionValue``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-backup-backupselection-conditionresourcetype.html
            """
            self._values = {
                'condition_key': condition_key,
                'condition_type': condition_type,
                'condition_value': condition_value,
            }

        @property
        def condition_key(self) -> str:
            """``CfnBackupSelection.ConditionResourceTypeProperty.ConditionKey``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-backup-backupselection-conditionresourcetype.html#cfn-backup-backupselection-conditionresourcetype-conditionkey
            """
            return self._values.get('condition_key')

        @property
        def condition_type(self) -> str:
            """``CfnBackupSelection.ConditionResourceTypeProperty.ConditionType``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-backup-backupselection-conditionresourcetype.html#cfn-backup-backupselection-conditionresourcetype-conditiontype
            """
            return self._values.get('condition_type')

        @property
        def condition_value(self) -> str:
            """``CfnBackupSelection.ConditionResourceTypeProperty.ConditionValue``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-backup-backupselection-conditionresourcetype.html#cfn-backup-backupselection-conditionresourcetype-conditionvalue
            """
            return self._values.get('condition_value')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'ConditionResourceTypeProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



@jsii.data_type(jsii_type="@aws-cdk/aws-backup.CfnBackupSelectionProps", jsii_struct_bases=[], name_mapping={'backup_plan_id': 'backupPlanId', 'backup_selection': 'backupSelection'})
class CfnBackupSelectionProps():
    def __init__(self, *, backup_plan_id: str, backup_selection: typing.Union[aws_cdk.core.IResolvable, "CfnBackupSelection.BackupSelectionResourceTypeProperty"]):
        """Properties for defining a ``AWS::Backup::BackupSelection``.

        :param backup_plan_id: ``AWS::Backup::BackupSelection.BackupPlanId``.
        :param backup_selection: ``AWS::Backup::BackupSelection.BackupSelection``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-backup-backupselection.html
        """
        self._values = {
            'backup_plan_id': backup_plan_id,
            'backup_selection': backup_selection,
        }

    @property
    def backup_plan_id(self) -> str:
        """``AWS::Backup::BackupSelection.BackupPlanId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-backup-backupselection.html#cfn-backup-backupselection-backupplanid
        """
        return self._values.get('backup_plan_id')

    @property
    def backup_selection(self) -> typing.Union[aws_cdk.core.IResolvable, "CfnBackupSelection.BackupSelectionResourceTypeProperty"]:
        """``AWS::Backup::BackupSelection.BackupSelection``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-backup-backupselection.html#cfn-backup-backupselection-backupselection
        """
        return self._values.get('backup_selection')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnBackupSelectionProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnBackupVault(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-backup.CfnBackupVault"):
    """A CloudFormation ``AWS::Backup::BackupVault``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-backup-backupvault.html
    cloudformationResource:
    :cloudformationResource:: AWS::Backup::BackupVault
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, backup_vault_name: str, access_policy: typing.Any=None, backup_vault_tags: typing.Any=None, encryption_key_arn: typing.Optional[str]=None, notifications: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["NotificationObjectTypeProperty"]]]=None) -> None:
        """Create a new ``AWS::Backup::BackupVault``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param backup_vault_name: ``AWS::Backup::BackupVault.BackupVaultName``.
        :param access_policy: ``AWS::Backup::BackupVault.AccessPolicy``.
        :param backup_vault_tags: ``AWS::Backup::BackupVault.BackupVaultTags``.
        :param encryption_key_arn: ``AWS::Backup::BackupVault.EncryptionKeyArn``.
        :param notifications: ``AWS::Backup::BackupVault.Notifications``.
        """
        props = CfnBackupVaultProps(backup_vault_name=backup_vault_name, access_policy=access_policy, backup_vault_tags=backup_vault_tags, encryption_key_arn=encryption_key_arn, notifications=notifications)

        jsii.create(CfnBackupVault, self, [scope, id, props])

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
    @jsii.member(jsii_name="attrBackupVaultArn")
    def attr_backup_vault_arn(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: BackupVaultArn
        """
        return jsii.get(self, "attrBackupVaultArn")

    @property
    @jsii.member(jsii_name="attrBackupVaultName")
    def attr_backup_vault_name(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: BackupVaultName
        """
        return jsii.get(self, "attrBackupVaultName")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="accessPolicy")
    def access_policy(self) -> typing.Any:
        """``AWS::Backup::BackupVault.AccessPolicy``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-backup-backupvault.html#cfn-backup-backupvault-accesspolicy
        """
        return jsii.get(self, "accessPolicy")

    @access_policy.setter
    def access_policy(self, value: typing.Any):
        return jsii.set(self, "accessPolicy", value)

    @property
    @jsii.member(jsii_name="backupVaultName")
    def backup_vault_name(self) -> str:
        """``AWS::Backup::BackupVault.BackupVaultName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-backup-backupvault.html#cfn-backup-backupvault-backupvaultname
        """
        return jsii.get(self, "backupVaultName")

    @backup_vault_name.setter
    def backup_vault_name(self, value: str):
        return jsii.set(self, "backupVaultName", value)

    @property
    @jsii.member(jsii_name="backupVaultTags")
    def backup_vault_tags(self) -> typing.Any:
        """``AWS::Backup::BackupVault.BackupVaultTags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-backup-backupvault.html#cfn-backup-backupvault-backupvaulttags
        """
        return jsii.get(self, "backupVaultTags")

    @backup_vault_tags.setter
    def backup_vault_tags(self, value: typing.Any):
        return jsii.set(self, "backupVaultTags", value)

    @property
    @jsii.member(jsii_name="encryptionKeyArn")
    def encryption_key_arn(self) -> typing.Optional[str]:
        """``AWS::Backup::BackupVault.EncryptionKeyArn``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-backup-backupvault.html#cfn-backup-backupvault-encryptionkeyarn
        """
        return jsii.get(self, "encryptionKeyArn")

    @encryption_key_arn.setter
    def encryption_key_arn(self, value: typing.Optional[str]):
        return jsii.set(self, "encryptionKeyArn", value)

    @property
    @jsii.member(jsii_name="notifications")
    def notifications(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["NotificationObjectTypeProperty"]]]:
        """``AWS::Backup::BackupVault.Notifications``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-backup-backupvault.html#cfn-backup-backupvault-notifications
        """
        return jsii.get(self, "notifications")

    @notifications.setter
    def notifications(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["NotificationObjectTypeProperty"]]]):
        return jsii.set(self, "notifications", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-backup.CfnBackupVault.NotificationObjectTypeProperty", jsii_struct_bases=[], name_mapping={'backup_vault_events': 'backupVaultEvents', 'sns_topic_arn': 'snsTopicArn'})
    class NotificationObjectTypeProperty():
        def __init__(self, *, backup_vault_events: typing.List[str], sns_topic_arn: str):
            """
            :param backup_vault_events: ``CfnBackupVault.NotificationObjectTypeProperty.BackupVaultEvents``.
            :param sns_topic_arn: ``CfnBackupVault.NotificationObjectTypeProperty.SNSTopicArn``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-backup-backupvault-notificationobjecttype.html
            """
            self._values = {
                'backup_vault_events': backup_vault_events,
                'sns_topic_arn': sns_topic_arn,
            }

        @property
        def backup_vault_events(self) -> typing.List[str]:
            """``CfnBackupVault.NotificationObjectTypeProperty.BackupVaultEvents``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-backup-backupvault-notificationobjecttype.html#cfn-backup-backupvault-notificationobjecttype-backupvaultevents
            """
            return self._values.get('backup_vault_events')

        @property
        def sns_topic_arn(self) -> str:
            """``CfnBackupVault.NotificationObjectTypeProperty.SNSTopicArn``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-backup-backupvault-notificationobjecttype.html#cfn-backup-backupvault-notificationobjecttype-snstopicarn
            """
            return self._values.get('sns_topic_arn')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'NotificationObjectTypeProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



@jsii.data_type(jsii_type="@aws-cdk/aws-backup.CfnBackupVaultProps", jsii_struct_bases=[], name_mapping={'backup_vault_name': 'backupVaultName', 'access_policy': 'accessPolicy', 'backup_vault_tags': 'backupVaultTags', 'encryption_key_arn': 'encryptionKeyArn', 'notifications': 'notifications'})
class CfnBackupVaultProps():
    def __init__(self, *, backup_vault_name: str, access_policy: typing.Any=None, backup_vault_tags: typing.Any=None, encryption_key_arn: typing.Optional[str]=None, notifications: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnBackupVault.NotificationObjectTypeProperty"]]]=None):
        """Properties for defining a ``AWS::Backup::BackupVault``.

        :param backup_vault_name: ``AWS::Backup::BackupVault.BackupVaultName``.
        :param access_policy: ``AWS::Backup::BackupVault.AccessPolicy``.
        :param backup_vault_tags: ``AWS::Backup::BackupVault.BackupVaultTags``.
        :param encryption_key_arn: ``AWS::Backup::BackupVault.EncryptionKeyArn``.
        :param notifications: ``AWS::Backup::BackupVault.Notifications``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-backup-backupvault.html
        """
        self._values = {
            'backup_vault_name': backup_vault_name,
        }
        if access_policy is not None: self._values["access_policy"] = access_policy
        if backup_vault_tags is not None: self._values["backup_vault_tags"] = backup_vault_tags
        if encryption_key_arn is not None: self._values["encryption_key_arn"] = encryption_key_arn
        if notifications is not None: self._values["notifications"] = notifications

    @property
    def backup_vault_name(self) -> str:
        """``AWS::Backup::BackupVault.BackupVaultName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-backup-backupvault.html#cfn-backup-backupvault-backupvaultname
        """
        return self._values.get('backup_vault_name')

    @property
    def access_policy(self) -> typing.Any:
        """``AWS::Backup::BackupVault.AccessPolicy``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-backup-backupvault.html#cfn-backup-backupvault-accesspolicy
        """
        return self._values.get('access_policy')

    @property
    def backup_vault_tags(self) -> typing.Any:
        """``AWS::Backup::BackupVault.BackupVaultTags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-backup-backupvault.html#cfn-backup-backupvault-backupvaulttags
        """
        return self._values.get('backup_vault_tags')

    @property
    def encryption_key_arn(self) -> typing.Optional[str]:
        """``AWS::Backup::BackupVault.EncryptionKeyArn``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-backup-backupvault.html#cfn-backup-backupvault-encryptionkeyarn
        """
        return self._values.get('encryption_key_arn')

    @property
    def notifications(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnBackupVault.NotificationObjectTypeProperty"]]]:
        """``AWS::Backup::BackupVault.Notifications``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-backup-backupvault.html#cfn-backup-backupvault-notifications
        """
        return self._values.get('notifications')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnBackupVaultProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


__all__ = ["CfnBackupPlan", "CfnBackupPlanProps", "CfnBackupSelection", "CfnBackupSelectionProps", "CfnBackupVault", "CfnBackupVaultProps", "__jsii_assembly__"]

publication.publish()
