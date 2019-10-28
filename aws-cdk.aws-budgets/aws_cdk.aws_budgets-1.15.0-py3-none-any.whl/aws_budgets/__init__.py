import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.core
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-budgets", "1.15.0", __name__, "aws-budgets@1.15.0.jsii.tgz")
class CfnBudget(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-budgets.CfnBudget"):
    """A CloudFormation ``AWS::Budgets::Budget``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-budgets-budget.html
    cloudformationResource:
    :cloudformationResource:: AWS::Budgets::Budget
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, budget: typing.Union["BudgetDataProperty", aws_cdk.core.IResolvable], notifications_with_subscribers: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "NotificationWithSubscribersProperty"]]]]]=None) -> None:
        """Create a new ``AWS::Budgets::Budget``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param budget: ``AWS::Budgets::Budget.Budget``.
        :param notifications_with_subscribers: ``AWS::Budgets::Budget.NotificationsWithSubscribers``.
        """
        props = CfnBudgetProps(budget=budget, notifications_with_subscribers=notifications_with_subscribers)

        jsii.create(CfnBudget, self, [scope, id, props])

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
    @jsii.member(jsii_name="budget")
    def budget(self) -> typing.Union["BudgetDataProperty", aws_cdk.core.IResolvable]:
        """``AWS::Budgets::Budget.Budget``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-budgets-budget.html#cfn-budgets-budget-budget
        """
        return jsii.get(self, "budget")

    @budget.setter
    def budget(self, value: typing.Union["BudgetDataProperty", aws_cdk.core.IResolvable]):
        return jsii.set(self, "budget", value)

    @property
    @jsii.member(jsii_name="notificationsWithSubscribers")
    def notifications_with_subscribers(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "NotificationWithSubscribersProperty"]]]]]:
        """``AWS::Budgets::Budget.NotificationsWithSubscribers``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-budgets-budget.html#cfn-budgets-budget-notificationswithsubscribers
        """
        return jsii.get(self, "notificationsWithSubscribers")

    @notifications_with_subscribers.setter
    def notifications_with_subscribers(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "NotificationWithSubscribersProperty"]]]]]):
        return jsii.set(self, "notificationsWithSubscribers", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-budgets.CfnBudget.BudgetDataProperty", jsii_struct_bases=[], name_mapping={'budget_type': 'budgetType', 'time_unit': 'timeUnit', 'budget_limit': 'budgetLimit', 'budget_name': 'budgetName', 'cost_filters': 'costFilters', 'cost_types': 'costTypes', 'planned_budget_limits': 'plannedBudgetLimits', 'time_period': 'timePeriod'})
    class BudgetDataProperty():
        def __init__(self, *, budget_type: str, time_unit: str, budget_limit: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnBudget.SpendProperty"]]]=None, budget_name: typing.Optional[str]=None, cost_filters: typing.Any=None, cost_types: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnBudget.CostTypesProperty"]]]=None, planned_budget_limits: typing.Any=None, time_period: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnBudget.TimePeriodProperty"]]]=None):
            """
            :param budget_type: ``CfnBudget.BudgetDataProperty.BudgetType``.
            :param time_unit: ``CfnBudget.BudgetDataProperty.TimeUnit``.
            :param budget_limit: ``CfnBudget.BudgetDataProperty.BudgetLimit``.
            :param budget_name: ``CfnBudget.BudgetDataProperty.BudgetName``.
            :param cost_filters: ``CfnBudget.BudgetDataProperty.CostFilters``.
            :param cost_types: ``CfnBudget.BudgetDataProperty.CostTypes``.
            :param planned_budget_limits: ``CfnBudget.BudgetDataProperty.PlannedBudgetLimits``.
            :param time_period: ``CfnBudget.BudgetDataProperty.TimePeriod``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-budgetdata.html
            """
            self._values = {
                'budget_type': budget_type,
                'time_unit': time_unit,
            }
            if budget_limit is not None: self._values["budget_limit"] = budget_limit
            if budget_name is not None: self._values["budget_name"] = budget_name
            if cost_filters is not None: self._values["cost_filters"] = cost_filters
            if cost_types is not None: self._values["cost_types"] = cost_types
            if planned_budget_limits is not None: self._values["planned_budget_limits"] = planned_budget_limits
            if time_period is not None: self._values["time_period"] = time_period

        @property
        def budget_type(self) -> str:
            """``CfnBudget.BudgetDataProperty.BudgetType``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-budgetdata.html#cfn-budgets-budget-budgetdata-budgettype
            """
            return self._values.get('budget_type')

        @property
        def time_unit(self) -> str:
            """``CfnBudget.BudgetDataProperty.TimeUnit``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-budgetdata.html#cfn-budgets-budget-budgetdata-timeunit
            """
            return self._values.get('time_unit')

        @property
        def budget_limit(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnBudget.SpendProperty"]]]:
            """``CfnBudget.BudgetDataProperty.BudgetLimit``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-budgetdata.html#cfn-budgets-budget-budgetdata-budgetlimit
            """
            return self._values.get('budget_limit')

        @property
        def budget_name(self) -> typing.Optional[str]:
            """``CfnBudget.BudgetDataProperty.BudgetName``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-budgetdata.html#cfn-budgets-budget-budgetdata-budgetname
            """
            return self._values.get('budget_name')

        @property
        def cost_filters(self) -> typing.Any:
            """``CfnBudget.BudgetDataProperty.CostFilters``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-budgetdata.html#cfn-budgets-budget-budgetdata-costfilters
            """
            return self._values.get('cost_filters')

        @property
        def cost_types(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnBudget.CostTypesProperty"]]]:
            """``CfnBudget.BudgetDataProperty.CostTypes``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-budgetdata.html#cfn-budgets-budget-budgetdata-costtypes
            """
            return self._values.get('cost_types')

        @property
        def planned_budget_limits(self) -> typing.Any:
            """``CfnBudget.BudgetDataProperty.PlannedBudgetLimits``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-budgetdata.html#cfn-budgets-budget-budgetdata-plannedbudgetlimits
            """
            return self._values.get('planned_budget_limits')

        @property
        def time_period(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnBudget.TimePeriodProperty"]]]:
            """``CfnBudget.BudgetDataProperty.TimePeriod``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-budgetdata.html#cfn-budgets-budget-budgetdata-timeperiod
            """
            return self._values.get('time_period')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'BudgetDataProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-budgets.CfnBudget.CostTypesProperty", jsii_struct_bases=[], name_mapping={'include_credit': 'includeCredit', 'include_discount': 'includeDiscount', 'include_other_subscription': 'includeOtherSubscription', 'include_recurring': 'includeRecurring', 'include_refund': 'includeRefund', 'include_subscription': 'includeSubscription', 'include_support': 'includeSupport', 'include_tax': 'includeTax', 'include_upfront': 'includeUpfront', 'use_amortized': 'useAmortized', 'use_blended': 'useBlended'})
    class CostTypesProperty():
        def __init__(self, *, include_credit: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, include_discount: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, include_other_subscription: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, include_recurring: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, include_refund: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, include_subscription: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, include_support: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, include_tax: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, include_upfront: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, use_amortized: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, use_blended: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None):
            """
            :param include_credit: ``CfnBudget.CostTypesProperty.IncludeCredit``.
            :param include_discount: ``CfnBudget.CostTypesProperty.IncludeDiscount``.
            :param include_other_subscription: ``CfnBudget.CostTypesProperty.IncludeOtherSubscription``.
            :param include_recurring: ``CfnBudget.CostTypesProperty.IncludeRecurring``.
            :param include_refund: ``CfnBudget.CostTypesProperty.IncludeRefund``.
            :param include_subscription: ``CfnBudget.CostTypesProperty.IncludeSubscription``.
            :param include_support: ``CfnBudget.CostTypesProperty.IncludeSupport``.
            :param include_tax: ``CfnBudget.CostTypesProperty.IncludeTax``.
            :param include_upfront: ``CfnBudget.CostTypesProperty.IncludeUpfront``.
            :param use_amortized: ``CfnBudget.CostTypesProperty.UseAmortized``.
            :param use_blended: ``CfnBudget.CostTypesProperty.UseBlended``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-costtypes.html
            """
            self._values = {
            }
            if include_credit is not None: self._values["include_credit"] = include_credit
            if include_discount is not None: self._values["include_discount"] = include_discount
            if include_other_subscription is not None: self._values["include_other_subscription"] = include_other_subscription
            if include_recurring is not None: self._values["include_recurring"] = include_recurring
            if include_refund is not None: self._values["include_refund"] = include_refund
            if include_subscription is not None: self._values["include_subscription"] = include_subscription
            if include_support is not None: self._values["include_support"] = include_support
            if include_tax is not None: self._values["include_tax"] = include_tax
            if include_upfront is not None: self._values["include_upfront"] = include_upfront
            if use_amortized is not None: self._values["use_amortized"] = use_amortized
            if use_blended is not None: self._values["use_blended"] = use_blended

        @property
        def include_credit(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
            """``CfnBudget.CostTypesProperty.IncludeCredit``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-costtypes.html#cfn-budgets-budget-costtypes-includecredit
            """
            return self._values.get('include_credit')

        @property
        def include_discount(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
            """``CfnBudget.CostTypesProperty.IncludeDiscount``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-costtypes.html#cfn-budgets-budget-costtypes-includediscount
            """
            return self._values.get('include_discount')

        @property
        def include_other_subscription(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
            """``CfnBudget.CostTypesProperty.IncludeOtherSubscription``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-costtypes.html#cfn-budgets-budget-costtypes-includeothersubscription
            """
            return self._values.get('include_other_subscription')

        @property
        def include_recurring(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
            """``CfnBudget.CostTypesProperty.IncludeRecurring``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-costtypes.html#cfn-budgets-budget-costtypes-includerecurring
            """
            return self._values.get('include_recurring')

        @property
        def include_refund(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
            """``CfnBudget.CostTypesProperty.IncludeRefund``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-costtypes.html#cfn-budgets-budget-costtypes-includerefund
            """
            return self._values.get('include_refund')

        @property
        def include_subscription(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
            """``CfnBudget.CostTypesProperty.IncludeSubscription``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-costtypes.html#cfn-budgets-budget-costtypes-includesubscription
            """
            return self._values.get('include_subscription')

        @property
        def include_support(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
            """``CfnBudget.CostTypesProperty.IncludeSupport``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-costtypes.html#cfn-budgets-budget-costtypes-includesupport
            """
            return self._values.get('include_support')

        @property
        def include_tax(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
            """``CfnBudget.CostTypesProperty.IncludeTax``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-costtypes.html#cfn-budgets-budget-costtypes-includetax
            """
            return self._values.get('include_tax')

        @property
        def include_upfront(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
            """``CfnBudget.CostTypesProperty.IncludeUpfront``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-costtypes.html#cfn-budgets-budget-costtypes-includeupfront
            """
            return self._values.get('include_upfront')

        @property
        def use_amortized(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
            """``CfnBudget.CostTypesProperty.UseAmortized``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-costtypes.html#cfn-budgets-budget-costtypes-useamortized
            """
            return self._values.get('use_amortized')

        @property
        def use_blended(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
            """``CfnBudget.CostTypesProperty.UseBlended``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-costtypes.html#cfn-budgets-budget-costtypes-useblended
            """
            return self._values.get('use_blended')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'CostTypesProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-budgets.CfnBudget.NotificationProperty", jsii_struct_bases=[], name_mapping={'comparison_operator': 'comparisonOperator', 'notification_type': 'notificationType', 'threshold': 'threshold', 'threshold_type': 'thresholdType'})
    class NotificationProperty():
        def __init__(self, *, comparison_operator: str, notification_type: str, threshold: jsii.Number, threshold_type: typing.Optional[str]=None):
            """
            :param comparison_operator: ``CfnBudget.NotificationProperty.ComparisonOperator``.
            :param notification_type: ``CfnBudget.NotificationProperty.NotificationType``.
            :param threshold: ``CfnBudget.NotificationProperty.Threshold``.
            :param threshold_type: ``CfnBudget.NotificationProperty.ThresholdType``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-notification.html
            """
            self._values = {
                'comparison_operator': comparison_operator,
                'notification_type': notification_type,
                'threshold': threshold,
            }
            if threshold_type is not None: self._values["threshold_type"] = threshold_type

        @property
        def comparison_operator(self) -> str:
            """``CfnBudget.NotificationProperty.ComparisonOperator``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-notification.html#cfn-budgets-budget-notification-comparisonoperator
            """
            return self._values.get('comparison_operator')

        @property
        def notification_type(self) -> str:
            """``CfnBudget.NotificationProperty.NotificationType``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-notification.html#cfn-budgets-budget-notification-notificationtype
            """
            return self._values.get('notification_type')

        @property
        def threshold(self) -> jsii.Number:
            """``CfnBudget.NotificationProperty.Threshold``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-notification.html#cfn-budgets-budget-notification-threshold
            """
            return self._values.get('threshold')

        @property
        def threshold_type(self) -> typing.Optional[str]:
            """``CfnBudget.NotificationProperty.ThresholdType``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-notification.html#cfn-budgets-budget-notification-thresholdtype
            """
            return self._values.get('threshold_type')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'NotificationProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-budgets.CfnBudget.NotificationWithSubscribersProperty", jsii_struct_bases=[], name_mapping={'notification': 'notification', 'subscribers': 'subscribers'})
    class NotificationWithSubscribersProperty():
        def __init__(self, *, notification: typing.Union[aws_cdk.core.IResolvable, "CfnBudget.NotificationProperty"], subscribers: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnBudget.SubscriberProperty"]]]):
            """
            :param notification: ``CfnBudget.NotificationWithSubscribersProperty.Notification``.
            :param subscribers: ``CfnBudget.NotificationWithSubscribersProperty.Subscribers``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-notificationwithsubscribers.html
            """
            self._values = {
                'notification': notification,
                'subscribers': subscribers,
            }

        @property
        def notification(self) -> typing.Union[aws_cdk.core.IResolvable, "CfnBudget.NotificationProperty"]:
            """``CfnBudget.NotificationWithSubscribersProperty.Notification``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-notificationwithsubscribers.html#cfn-budgets-budget-notificationwithsubscribers-notification
            """
            return self._values.get('notification')

        @property
        def subscribers(self) -> typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnBudget.SubscriberProperty"]]]:
            """``CfnBudget.NotificationWithSubscribersProperty.Subscribers``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-notificationwithsubscribers.html#cfn-budgets-budget-notificationwithsubscribers-subscribers
            """
            return self._values.get('subscribers')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'NotificationWithSubscribersProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-budgets.CfnBudget.SpendProperty", jsii_struct_bases=[], name_mapping={'amount': 'amount', 'unit': 'unit'})
    class SpendProperty():
        def __init__(self, *, amount: jsii.Number, unit: str):
            """
            :param amount: ``CfnBudget.SpendProperty.Amount``.
            :param unit: ``CfnBudget.SpendProperty.Unit``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-spend.html
            """
            self._values = {
                'amount': amount,
                'unit': unit,
            }

        @property
        def amount(self) -> jsii.Number:
            """``CfnBudget.SpendProperty.Amount``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-spend.html#cfn-budgets-budget-spend-amount
            """
            return self._values.get('amount')

        @property
        def unit(self) -> str:
            """``CfnBudget.SpendProperty.Unit``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-spend.html#cfn-budgets-budget-spend-unit
            """
            return self._values.get('unit')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'SpendProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-budgets.CfnBudget.SubscriberProperty", jsii_struct_bases=[], name_mapping={'address': 'address', 'subscription_type': 'subscriptionType'})
    class SubscriberProperty():
        def __init__(self, *, address: str, subscription_type: str):
            """
            :param address: ``CfnBudget.SubscriberProperty.Address``.
            :param subscription_type: ``CfnBudget.SubscriberProperty.SubscriptionType``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-subscriber.html
            """
            self._values = {
                'address': address,
                'subscription_type': subscription_type,
            }

        @property
        def address(self) -> str:
            """``CfnBudget.SubscriberProperty.Address``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-subscriber.html#cfn-budgets-budget-subscriber-address
            """
            return self._values.get('address')

        @property
        def subscription_type(self) -> str:
            """``CfnBudget.SubscriberProperty.SubscriptionType``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-subscriber.html#cfn-budgets-budget-subscriber-subscriptiontype
            """
            return self._values.get('subscription_type')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'SubscriberProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-budgets.CfnBudget.TimePeriodProperty", jsii_struct_bases=[], name_mapping={'end': 'end', 'start': 'start'})
    class TimePeriodProperty():
        def __init__(self, *, end: typing.Optional[str]=None, start: typing.Optional[str]=None):
            """
            :param end: ``CfnBudget.TimePeriodProperty.End``.
            :param start: ``CfnBudget.TimePeriodProperty.Start``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-timeperiod.html
            """
            self._values = {
            }
            if end is not None: self._values["end"] = end
            if start is not None: self._values["start"] = start

        @property
        def end(self) -> typing.Optional[str]:
            """``CfnBudget.TimePeriodProperty.End``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-timeperiod.html#cfn-budgets-budget-timeperiod-end
            """
            return self._values.get('end')

        @property
        def start(self) -> typing.Optional[str]:
            """``CfnBudget.TimePeriodProperty.Start``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-timeperiod.html#cfn-budgets-budget-timeperiod-start
            """
            return self._values.get('start')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'TimePeriodProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



@jsii.data_type(jsii_type="@aws-cdk/aws-budgets.CfnBudgetProps", jsii_struct_bases=[], name_mapping={'budget': 'budget', 'notifications_with_subscribers': 'notificationsWithSubscribers'})
class CfnBudgetProps():
    def __init__(self, *, budget: typing.Union["CfnBudget.BudgetDataProperty", aws_cdk.core.IResolvable], notifications_with_subscribers: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnBudget.NotificationWithSubscribersProperty"]]]]]=None):
        """Properties for defining a ``AWS::Budgets::Budget``.

        :param budget: ``AWS::Budgets::Budget.Budget``.
        :param notifications_with_subscribers: ``AWS::Budgets::Budget.NotificationsWithSubscribers``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-budgets-budget.html
        """
        self._values = {
            'budget': budget,
        }
        if notifications_with_subscribers is not None: self._values["notifications_with_subscribers"] = notifications_with_subscribers

    @property
    def budget(self) -> typing.Union["CfnBudget.BudgetDataProperty", aws_cdk.core.IResolvable]:
        """``AWS::Budgets::Budget.Budget``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-budgets-budget.html#cfn-budgets-budget-budget
        """
        return self._values.get('budget')

    @property
    def notifications_with_subscribers(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnBudget.NotificationWithSubscribersProperty"]]]]]:
        """``AWS::Budgets::Budget.NotificationsWithSubscribers``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-budgets-budget.html#cfn-budgets-budget-notificationswithsubscribers
        """
        return self._values.get('notifications_with_subscribers')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnBudgetProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


__all__ = ["CfnBudget", "CfnBudgetProps", "__jsii_assembly__"]

publication.publish()
