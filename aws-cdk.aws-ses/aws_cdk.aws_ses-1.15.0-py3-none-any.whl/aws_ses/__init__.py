import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.aws_iam
import aws_cdk.aws_lambda
import aws_cdk.core
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-ses", "1.15.0", __name__, "aws-ses@1.15.0.jsii.tgz")
class CfnConfigurationSet(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ses.CfnConfigurationSet"):
    """A CloudFormation ``AWS::SES::ConfigurationSet``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ses-configurationset.html
    cloudformationResource:
    :cloudformationResource:: AWS::SES::ConfigurationSet
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, name: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::SES::ConfigurationSet``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param name: ``AWS::SES::ConfigurationSet.Name``.
        """
        props = CfnConfigurationSetProps(name=name)

        jsii.create(CfnConfigurationSet, self, [scope, id, props])

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
        """``AWS::SES::ConfigurationSet.Name``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ses-configurationset.html#cfn-ses-configurationset-name
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: typing.Optional[str]):
        return jsii.set(self, "name", value)


class CfnConfigurationSetEventDestination(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ses.CfnConfigurationSetEventDestination"):
    """A CloudFormation ``AWS::SES::ConfigurationSetEventDestination``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ses-configurationseteventdestination.html
    cloudformationResource:
    :cloudformationResource:: AWS::SES::ConfigurationSetEventDestination
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, configuration_set_name: str, event_destination: typing.Union[aws_cdk.core.IResolvable, "EventDestinationProperty"]) -> None:
        """Create a new ``AWS::SES::ConfigurationSetEventDestination``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param configuration_set_name: ``AWS::SES::ConfigurationSetEventDestination.ConfigurationSetName``.
        :param event_destination: ``AWS::SES::ConfigurationSetEventDestination.EventDestination``.
        """
        props = CfnConfigurationSetEventDestinationProps(configuration_set_name=configuration_set_name, event_destination=event_destination)

        jsii.create(CfnConfigurationSetEventDestination, self, [scope, id, props])

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
    @jsii.member(jsii_name="configurationSetName")
    def configuration_set_name(self) -> str:
        """``AWS::SES::ConfigurationSetEventDestination.ConfigurationSetName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ses-configurationseteventdestination.html#cfn-ses-configurationseteventdestination-configurationsetname
        """
        return jsii.get(self, "configurationSetName")

    @configuration_set_name.setter
    def configuration_set_name(self, value: str):
        return jsii.set(self, "configurationSetName", value)

    @property
    @jsii.member(jsii_name="eventDestination")
    def event_destination(self) -> typing.Union[aws_cdk.core.IResolvable, "EventDestinationProperty"]:
        """``AWS::SES::ConfigurationSetEventDestination.EventDestination``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ses-configurationseteventdestination.html#cfn-ses-configurationseteventdestination-eventdestination
        """
        return jsii.get(self, "eventDestination")

    @event_destination.setter
    def event_destination(self, value: typing.Union[aws_cdk.core.IResolvable, "EventDestinationProperty"]):
        return jsii.set(self, "eventDestination", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-ses.CfnConfigurationSetEventDestination.CloudWatchDestinationProperty", jsii_struct_bases=[], name_mapping={'dimension_configurations': 'dimensionConfigurations'})
    class CloudWatchDestinationProperty():
        def __init__(self, *, dimension_configurations: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnConfigurationSetEventDestination.DimensionConfigurationProperty"]]]]]=None):
            """
            :param dimension_configurations: ``CfnConfigurationSetEventDestination.CloudWatchDestinationProperty.DimensionConfigurations``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-configurationseteventdestination-cloudwatchdestination.html
            """
            self._values = {
            }
            if dimension_configurations is not None: self._values["dimension_configurations"] = dimension_configurations

        @property
        def dimension_configurations(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnConfigurationSetEventDestination.DimensionConfigurationProperty"]]]]]:
            """``CfnConfigurationSetEventDestination.CloudWatchDestinationProperty.DimensionConfigurations``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-configurationseteventdestination-cloudwatchdestination.html#cfn-ses-configurationseteventdestination-cloudwatchdestination-dimensionconfigurations
            """
            return self._values.get('dimension_configurations')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'CloudWatchDestinationProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-ses.CfnConfigurationSetEventDestination.DimensionConfigurationProperty", jsii_struct_bases=[], name_mapping={'default_dimension_value': 'defaultDimensionValue', 'dimension_name': 'dimensionName', 'dimension_value_source': 'dimensionValueSource'})
    class DimensionConfigurationProperty():
        def __init__(self, *, default_dimension_value: str, dimension_name: str, dimension_value_source: str):
            """
            :param default_dimension_value: ``CfnConfigurationSetEventDestination.DimensionConfigurationProperty.DefaultDimensionValue``.
            :param dimension_name: ``CfnConfigurationSetEventDestination.DimensionConfigurationProperty.DimensionName``.
            :param dimension_value_source: ``CfnConfigurationSetEventDestination.DimensionConfigurationProperty.DimensionValueSource``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-configurationseteventdestination-dimensionconfiguration.html
            """
            self._values = {
                'default_dimension_value': default_dimension_value,
                'dimension_name': dimension_name,
                'dimension_value_source': dimension_value_source,
            }

        @property
        def default_dimension_value(self) -> str:
            """``CfnConfigurationSetEventDestination.DimensionConfigurationProperty.DefaultDimensionValue``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-configurationseteventdestination-dimensionconfiguration.html#cfn-ses-configurationseteventdestination-dimensionconfiguration-defaultdimensionvalue
            """
            return self._values.get('default_dimension_value')

        @property
        def dimension_name(self) -> str:
            """``CfnConfigurationSetEventDestination.DimensionConfigurationProperty.DimensionName``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-configurationseteventdestination-dimensionconfiguration.html#cfn-ses-configurationseteventdestination-dimensionconfiguration-dimensionname
            """
            return self._values.get('dimension_name')

        @property
        def dimension_value_source(self) -> str:
            """``CfnConfigurationSetEventDestination.DimensionConfigurationProperty.DimensionValueSource``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-configurationseteventdestination-dimensionconfiguration.html#cfn-ses-configurationseteventdestination-dimensionconfiguration-dimensionvaluesource
            """
            return self._values.get('dimension_value_source')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'DimensionConfigurationProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-ses.CfnConfigurationSetEventDestination.EventDestinationProperty", jsii_struct_bases=[], name_mapping={'matching_event_types': 'matchingEventTypes', 'cloud_watch_destination': 'cloudWatchDestination', 'enabled': 'enabled', 'kinesis_firehose_destination': 'kinesisFirehoseDestination', 'name': 'name'})
    class EventDestinationProperty():
        def __init__(self, *, matching_event_types: typing.List[str], cloud_watch_destination: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnConfigurationSetEventDestination.CloudWatchDestinationProperty"]]]=None, enabled: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, kinesis_firehose_destination: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnConfigurationSetEventDestination.KinesisFirehoseDestinationProperty"]]]=None, name: typing.Optional[str]=None):
            """
            :param matching_event_types: ``CfnConfigurationSetEventDestination.EventDestinationProperty.MatchingEventTypes``.
            :param cloud_watch_destination: ``CfnConfigurationSetEventDestination.EventDestinationProperty.CloudWatchDestination``.
            :param enabled: ``CfnConfigurationSetEventDestination.EventDestinationProperty.Enabled``.
            :param kinesis_firehose_destination: ``CfnConfigurationSetEventDestination.EventDestinationProperty.KinesisFirehoseDestination``.
            :param name: ``CfnConfigurationSetEventDestination.EventDestinationProperty.Name``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-configurationseteventdestination-eventdestination.html
            """
            self._values = {
                'matching_event_types': matching_event_types,
            }
            if cloud_watch_destination is not None: self._values["cloud_watch_destination"] = cloud_watch_destination
            if enabled is not None: self._values["enabled"] = enabled
            if kinesis_firehose_destination is not None: self._values["kinesis_firehose_destination"] = kinesis_firehose_destination
            if name is not None: self._values["name"] = name

        @property
        def matching_event_types(self) -> typing.List[str]:
            """``CfnConfigurationSetEventDestination.EventDestinationProperty.MatchingEventTypes``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-configurationseteventdestination-eventdestination.html#cfn-ses-configurationseteventdestination-eventdestination-matchingeventtypes
            """
            return self._values.get('matching_event_types')

        @property
        def cloud_watch_destination(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnConfigurationSetEventDestination.CloudWatchDestinationProperty"]]]:
            """``CfnConfigurationSetEventDestination.EventDestinationProperty.CloudWatchDestination``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-configurationseteventdestination-eventdestination.html#cfn-ses-configurationseteventdestination-eventdestination-cloudwatchdestination
            """
            return self._values.get('cloud_watch_destination')

        @property
        def enabled(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
            """``CfnConfigurationSetEventDestination.EventDestinationProperty.Enabled``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-configurationseteventdestination-eventdestination.html#cfn-ses-configurationseteventdestination-eventdestination-enabled
            """
            return self._values.get('enabled')

        @property
        def kinesis_firehose_destination(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnConfigurationSetEventDestination.KinesisFirehoseDestinationProperty"]]]:
            """``CfnConfigurationSetEventDestination.EventDestinationProperty.KinesisFirehoseDestination``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-configurationseteventdestination-eventdestination.html#cfn-ses-configurationseteventdestination-eventdestination-kinesisfirehosedestination
            """
            return self._values.get('kinesis_firehose_destination')

        @property
        def name(self) -> typing.Optional[str]:
            """``CfnConfigurationSetEventDestination.EventDestinationProperty.Name``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-configurationseteventdestination-eventdestination.html#cfn-ses-configurationseteventdestination-eventdestination-name
            """
            return self._values.get('name')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'EventDestinationProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-ses.CfnConfigurationSetEventDestination.KinesisFirehoseDestinationProperty", jsii_struct_bases=[], name_mapping={'delivery_stream_arn': 'deliveryStreamArn', 'iam_role_arn': 'iamRoleArn'})
    class KinesisFirehoseDestinationProperty():
        def __init__(self, *, delivery_stream_arn: str, iam_role_arn: str):
            """
            :param delivery_stream_arn: ``CfnConfigurationSetEventDestination.KinesisFirehoseDestinationProperty.DeliveryStreamARN``.
            :param iam_role_arn: ``CfnConfigurationSetEventDestination.KinesisFirehoseDestinationProperty.IAMRoleARN``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-configurationseteventdestination-kinesisfirehosedestination.html
            """
            self._values = {
                'delivery_stream_arn': delivery_stream_arn,
                'iam_role_arn': iam_role_arn,
            }

        @property
        def delivery_stream_arn(self) -> str:
            """``CfnConfigurationSetEventDestination.KinesisFirehoseDestinationProperty.DeliveryStreamARN``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-configurationseteventdestination-kinesisfirehosedestination.html#cfn-ses-configurationseteventdestination-kinesisfirehosedestination-deliverystreamarn
            """
            return self._values.get('delivery_stream_arn')

        @property
        def iam_role_arn(self) -> str:
            """``CfnConfigurationSetEventDestination.KinesisFirehoseDestinationProperty.IAMRoleARN``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-configurationseteventdestination-kinesisfirehosedestination.html#cfn-ses-configurationseteventdestination-kinesisfirehosedestination-iamrolearn
            """
            return self._values.get('iam_role_arn')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'KinesisFirehoseDestinationProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



@jsii.data_type(jsii_type="@aws-cdk/aws-ses.CfnConfigurationSetEventDestinationProps", jsii_struct_bases=[], name_mapping={'configuration_set_name': 'configurationSetName', 'event_destination': 'eventDestination'})
class CfnConfigurationSetEventDestinationProps():
    def __init__(self, *, configuration_set_name: str, event_destination: typing.Union[aws_cdk.core.IResolvable, "CfnConfigurationSetEventDestination.EventDestinationProperty"]):
        """Properties for defining a ``AWS::SES::ConfigurationSetEventDestination``.

        :param configuration_set_name: ``AWS::SES::ConfigurationSetEventDestination.ConfigurationSetName``.
        :param event_destination: ``AWS::SES::ConfigurationSetEventDestination.EventDestination``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ses-configurationseteventdestination.html
        """
        self._values = {
            'configuration_set_name': configuration_set_name,
            'event_destination': event_destination,
        }

    @property
    def configuration_set_name(self) -> str:
        """``AWS::SES::ConfigurationSetEventDestination.ConfigurationSetName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ses-configurationseteventdestination.html#cfn-ses-configurationseteventdestination-configurationsetname
        """
        return self._values.get('configuration_set_name')

    @property
    def event_destination(self) -> typing.Union[aws_cdk.core.IResolvable, "CfnConfigurationSetEventDestination.EventDestinationProperty"]:
        """``AWS::SES::ConfigurationSetEventDestination.EventDestination``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ses-configurationseteventdestination.html#cfn-ses-configurationseteventdestination-eventdestination
        """
        return self._values.get('event_destination')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnConfigurationSetEventDestinationProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


@jsii.data_type(jsii_type="@aws-cdk/aws-ses.CfnConfigurationSetProps", jsii_struct_bases=[], name_mapping={'name': 'name'})
class CfnConfigurationSetProps():
    def __init__(self, *, name: typing.Optional[str]=None):
        """Properties for defining a ``AWS::SES::ConfigurationSet``.

        :param name: ``AWS::SES::ConfigurationSet.Name``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ses-configurationset.html
        """
        self._values = {
        }
        if name is not None: self._values["name"] = name

    @property
    def name(self) -> typing.Optional[str]:
        """``AWS::SES::ConfigurationSet.Name``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ses-configurationset.html#cfn-ses-configurationset-name
        """
        return self._values.get('name')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnConfigurationSetProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnReceiptFilter(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ses.CfnReceiptFilter"):
    """A CloudFormation ``AWS::SES::ReceiptFilter``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ses-receiptfilter.html
    cloudformationResource:
    :cloudformationResource:: AWS::SES::ReceiptFilter
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, filter: typing.Union["FilterProperty", aws_cdk.core.IResolvable]) -> None:
        """Create a new ``AWS::SES::ReceiptFilter``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param filter: ``AWS::SES::ReceiptFilter.Filter``.
        """
        props = CfnReceiptFilterProps(filter=filter)

        jsii.create(CfnReceiptFilter, self, [scope, id, props])

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
    @jsii.member(jsii_name="filter")
    def filter(self) -> typing.Union["FilterProperty", aws_cdk.core.IResolvable]:
        """``AWS::SES::ReceiptFilter.Filter``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ses-receiptfilter.html#cfn-ses-receiptfilter-filter
        """
        return jsii.get(self, "filter")

    @filter.setter
    def filter(self, value: typing.Union["FilterProperty", aws_cdk.core.IResolvable]):
        return jsii.set(self, "filter", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-ses.CfnReceiptFilter.FilterProperty", jsii_struct_bases=[], name_mapping={'ip_filter': 'ipFilter', 'name': 'name'})
    class FilterProperty():
        def __init__(self, *, ip_filter: typing.Union[aws_cdk.core.IResolvable, "CfnReceiptFilter.IpFilterProperty"], name: typing.Optional[str]=None):
            """
            :param ip_filter: ``CfnReceiptFilter.FilterProperty.IpFilter``.
            :param name: ``CfnReceiptFilter.FilterProperty.Name``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-receiptfilter-filter.html
            """
            self._values = {
                'ip_filter': ip_filter,
            }
            if name is not None: self._values["name"] = name

        @property
        def ip_filter(self) -> typing.Union[aws_cdk.core.IResolvable, "CfnReceiptFilter.IpFilterProperty"]:
            """``CfnReceiptFilter.FilterProperty.IpFilter``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-receiptfilter-filter.html#cfn-ses-receiptfilter-filter-ipfilter
            """
            return self._values.get('ip_filter')

        @property
        def name(self) -> typing.Optional[str]:
            """``CfnReceiptFilter.FilterProperty.Name``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-receiptfilter-filter.html#cfn-ses-receiptfilter-filter-name
            """
            return self._values.get('name')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'FilterProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-ses.CfnReceiptFilter.IpFilterProperty", jsii_struct_bases=[], name_mapping={'cidr': 'cidr', 'policy': 'policy'})
    class IpFilterProperty():
        def __init__(self, *, cidr: str, policy: str):
            """
            :param cidr: ``CfnReceiptFilter.IpFilterProperty.Cidr``.
            :param policy: ``CfnReceiptFilter.IpFilterProperty.Policy``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-receiptfilter-ipfilter.html
            """
            self._values = {
                'cidr': cidr,
                'policy': policy,
            }

        @property
        def cidr(self) -> str:
            """``CfnReceiptFilter.IpFilterProperty.Cidr``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-receiptfilter-ipfilter.html#cfn-ses-receiptfilter-ipfilter-cidr
            """
            return self._values.get('cidr')

        @property
        def policy(self) -> str:
            """``CfnReceiptFilter.IpFilterProperty.Policy``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-receiptfilter-ipfilter.html#cfn-ses-receiptfilter-ipfilter-policy
            """
            return self._values.get('policy')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'IpFilterProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



@jsii.data_type(jsii_type="@aws-cdk/aws-ses.CfnReceiptFilterProps", jsii_struct_bases=[], name_mapping={'filter': 'filter'})
class CfnReceiptFilterProps():
    def __init__(self, *, filter: typing.Union["CfnReceiptFilter.FilterProperty", aws_cdk.core.IResolvable]):
        """Properties for defining a ``AWS::SES::ReceiptFilter``.

        :param filter: ``AWS::SES::ReceiptFilter.Filter``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ses-receiptfilter.html
        """
        self._values = {
            'filter': filter,
        }

    @property
    def filter(self) -> typing.Union["CfnReceiptFilter.FilterProperty", aws_cdk.core.IResolvable]:
        """``AWS::SES::ReceiptFilter.Filter``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ses-receiptfilter.html#cfn-ses-receiptfilter-filter
        """
        return self._values.get('filter')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnReceiptFilterProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnReceiptRule(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ses.CfnReceiptRule"):
    """A CloudFormation ``AWS::SES::ReceiptRule``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ses-receiptrule.html
    cloudformationResource:
    :cloudformationResource:: AWS::SES::ReceiptRule
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, rule: typing.Union[aws_cdk.core.IResolvable, "RuleProperty"], rule_set_name: str, after: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::SES::ReceiptRule``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param rule: ``AWS::SES::ReceiptRule.Rule``.
        :param rule_set_name: ``AWS::SES::ReceiptRule.RuleSetName``.
        :param after: ``AWS::SES::ReceiptRule.After``.
        """
        props = CfnReceiptRuleProps(rule=rule, rule_set_name=rule_set_name, after=after)

        jsii.create(CfnReceiptRule, self, [scope, id, props])

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
    @jsii.member(jsii_name="rule")
    def rule(self) -> typing.Union[aws_cdk.core.IResolvable, "RuleProperty"]:
        """``AWS::SES::ReceiptRule.Rule``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ses-receiptrule.html#cfn-ses-receiptrule-rule
        """
        return jsii.get(self, "rule")

    @rule.setter
    def rule(self, value: typing.Union[aws_cdk.core.IResolvable, "RuleProperty"]):
        return jsii.set(self, "rule", value)

    @property
    @jsii.member(jsii_name="ruleSetName")
    def rule_set_name(self) -> str:
        """``AWS::SES::ReceiptRule.RuleSetName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ses-receiptrule.html#cfn-ses-receiptrule-rulesetname
        """
        return jsii.get(self, "ruleSetName")

    @rule_set_name.setter
    def rule_set_name(self, value: str):
        return jsii.set(self, "ruleSetName", value)

    @property
    @jsii.member(jsii_name="after")
    def after(self) -> typing.Optional[str]:
        """``AWS::SES::ReceiptRule.After``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ses-receiptrule.html#cfn-ses-receiptrule-after
        """
        return jsii.get(self, "after")

    @after.setter
    def after(self, value: typing.Optional[str]):
        return jsii.set(self, "after", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-ses.CfnReceiptRule.ActionProperty", jsii_struct_bases=[], name_mapping={'add_header_action': 'addHeaderAction', 'bounce_action': 'bounceAction', 'lambda_action': 'lambdaAction', 's3_action': 's3Action', 'sns_action': 'snsAction', 'stop_action': 'stopAction', 'workmail_action': 'workmailAction'})
    class ActionProperty():
        def __init__(self, *, add_header_action: typing.Optional[typing.Union[typing.Optional["CfnReceiptRule.AddHeaderActionProperty"], typing.Optional[aws_cdk.core.IResolvable]]]=None, bounce_action: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnReceiptRule.BounceActionProperty"]]]=None, lambda_action: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnReceiptRule.LambdaActionProperty"]]]=None, s3_action: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnReceiptRule.S3ActionProperty"]]]=None, sns_action: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnReceiptRule.SNSActionProperty"]]]=None, stop_action: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnReceiptRule.StopActionProperty"]]]=None, workmail_action: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnReceiptRule.WorkmailActionProperty"]]]=None):
            """
            :param add_header_action: ``CfnReceiptRule.ActionProperty.AddHeaderAction``.
            :param bounce_action: ``CfnReceiptRule.ActionProperty.BounceAction``.
            :param lambda_action: ``CfnReceiptRule.ActionProperty.LambdaAction``.
            :param s3_action: ``CfnReceiptRule.ActionProperty.S3Action``.
            :param sns_action: ``CfnReceiptRule.ActionProperty.SNSAction``.
            :param stop_action: ``CfnReceiptRule.ActionProperty.StopAction``.
            :param workmail_action: ``CfnReceiptRule.ActionProperty.WorkmailAction``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-receiptrule-action.html
            """
            self._values = {
            }
            if add_header_action is not None: self._values["add_header_action"] = add_header_action
            if bounce_action is not None: self._values["bounce_action"] = bounce_action
            if lambda_action is not None: self._values["lambda_action"] = lambda_action
            if s3_action is not None: self._values["s3_action"] = s3_action
            if sns_action is not None: self._values["sns_action"] = sns_action
            if stop_action is not None: self._values["stop_action"] = stop_action
            if workmail_action is not None: self._values["workmail_action"] = workmail_action

        @property
        def add_header_action(self) -> typing.Optional[typing.Union[typing.Optional["CfnReceiptRule.AddHeaderActionProperty"], typing.Optional[aws_cdk.core.IResolvable]]]:
            """``CfnReceiptRule.ActionProperty.AddHeaderAction``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-receiptrule-action.html#cfn-ses-receiptrule-action-addheaderaction
            """
            return self._values.get('add_header_action')

        @property
        def bounce_action(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnReceiptRule.BounceActionProperty"]]]:
            """``CfnReceiptRule.ActionProperty.BounceAction``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-receiptrule-action.html#cfn-ses-receiptrule-action-bounceaction
            """
            return self._values.get('bounce_action')

        @property
        def lambda_action(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnReceiptRule.LambdaActionProperty"]]]:
            """``CfnReceiptRule.ActionProperty.LambdaAction``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-receiptrule-action.html#cfn-ses-receiptrule-action-lambdaaction
            """
            return self._values.get('lambda_action')

        @property
        def s3_action(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnReceiptRule.S3ActionProperty"]]]:
            """``CfnReceiptRule.ActionProperty.S3Action``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-receiptrule-action.html#cfn-ses-receiptrule-action-s3action
            """
            return self._values.get('s3_action')

        @property
        def sns_action(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnReceiptRule.SNSActionProperty"]]]:
            """``CfnReceiptRule.ActionProperty.SNSAction``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-receiptrule-action.html#cfn-ses-receiptrule-action-snsaction
            """
            return self._values.get('sns_action')

        @property
        def stop_action(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnReceiptRule.StopActionProperty"]]]:
            """``CfnReceiptRule.ActionProperty.StopAction``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-receiptrule-action.html#cfn-ses-receiptrule-action-stopaction
            """
            return self._values.get('stop_action')

        @property
        def workmail_action(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnReceiptRule.WorkmailActionProperty"]]]:
            """``CfnReceiptRule.ActionProperty.WorkmailAction``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-receiptrule-action.html#cfn-ses-receiptrule-action-workmailaction
            """
            return self._values.get('workmail_action')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'ActionProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-ses.CfnReceiptRule.AddHeaderActionProperty", jsii_struct_bases=[], name_mapping={'header_name': 'headerName', 'header_value': 'headerValue'})
    class AddHeaderActionProperty():
        def __init__(self, *, header_name: str, header_value: str):
            """
            :param header_name: ``CfnReceiptRule.AddHeaderActionProperty.HeaderName``.
            :param header_value: ``CfnReceiptRule.AddHeaderActionProperty.HeaderValue``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-receiptrule-addheaderaction.html
            """
            self._values = {
                'header_name': header_name,
                'header_value': header_value,
            }

        @property
        def header_name(self) -> str:
            """``CfnReceiptRule.AddHeaderActionProperty.HeaderName``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-receiptrule-addheaderaction.html#cfn-ses-receiptrule-addheaderaction-headername
            """
            return self._values.get('header_name')

        @property
        def header_value(self) -> str:
            """``CfnReceiptRule.AddHeaderActionProperty.HeaderValue``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-receiptrule-addheaderaction.html#cfn-ses-receiptrule-addheaderaction-headervalue
            """
            return self._values.get('header_value')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'AddHeaderActionProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-ses.CfnReceiptRule.BounceActionProperty", jsii_struct_bases=[], name_mapping={'message': 'message', 'sender': 'sender', 'smtp_reply_code': 'smtpReplyCode', 'status_code': 'statusCode', 'topic_arn': 'topicArn'})
    class BounceActionProperty():
        def __init__(self, *, message: str, sender: str, smtp_reply_code: str, status_code: typing.Optional[str]=None, topic_arn: typing.Optional[str]=None):
            """
            :param message: ``CfnReceiptRule.BounceActionProperty.Message``.
            :param sender: ``CfnReceiptRule.BounceActionProperty.Sender``.
            :param smtp_reply_code: ``CfnReceiptRule.BounceActionProperty.SmtpReplyCode``.
            :param status_code: ``CfnReceiptRule.BounceActionProperty.StatusCode``.
            :param topic_arn: ``CfnReceiptRule.BounceActionProperty.TopicArn``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-receiptrule-bounceaction.html
            """
            self._values = {
                'message': message,
                'sender': sender,
                'smtp_reply_code': smtp_reply_code,
            }
            if status_code is not None: self._values["status_code"] = status_code
            if topic_arn is not None: self._values["topic_arn"] = topic_arn

        @property
        def message(self) -> str:
            """``CfnReceiptRule.BounceActionProperty.Message``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-receiptrule-bounceaction.html#cfn-ses-receiptrule-bounceaction-message
            """
            return self._values.get('message')

        @property
        def sender(self) -> str:
            """``CfnReceiptRule.BounceActionProperty.Sender``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-receiptrule-bounceaction.html#cfn-ses-receiptrule-bounceaction-sender
            """
            return self._values.get('sender')

        @property
        def smtp_reply_code(self) -> str:
            """``CfnReceiptRule.BounceActionProperty.SmtpReplyCode``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-receiptrule-bounceaction.html#cfn-ses-receiptrule-bounceaction-smtpreplycode
            """
            return self._values.get('smtp_reply_code')

        @property
        def status_code(self) -> typing.Optional[str]:
            """``CfnReceiptRule.BounceActionProperty.StatusCode``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-receiptrule-bounceaction.html#cfn-ses-receiptrule-bounceaction-statuscode
            """
            return self._values.get('status_code')

        @property
        def topic_arn(self) -> typing.Optional[str]:
            """``CfnReceiptRule.BounceActionProperty.TopicArn``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-receiptrule-bounceaction.html#cfn-ses-receiptrule-bounceaction-topicarn
            """
            return self._values.get('topic_arn')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'BounceActionProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-ses.CfnReceiptRule.LambdaActionProperty", jsii_struct_bases=[], name_mapping={'function_arn': 'functionArn', 'invocation_type': 'invocationType', 'topic_arn': 'topicArn'})
    class LambdaActionProperty():
        def __init__(self, *, function_arn: str, invocation_type: typing.Optional[str]=None, topic_arn: typing.Optional[str]=None):
            """
            :param function_arn: ``CfnReceiptRule.LambdaActionProperty.FunctionArn``.
            :param invocation_type: ``CfnReceiptRule.LambdaActionProperty.InvocationType``.
            :param topic_arn: ``CfnReceiptRule.LambdaActionProperty.TopicArn``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-receiptrule-lambdaaction.html
            """
            self._values = {
                'function_arn': function_arn,
            }
            if invocation_type is not None: self._values["invocation_type"] = invocation_type
            if topic_arn is not None: self._values["topic_arn"] = topic_arn

        @property
        def function_arn(self) -> str:
            """``CfnReceiptRule.LambdaActionProperty.FunctionArn``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-receiptrule-lambdaaction.html#cfn-ses-receiptrule-lambdaaction-functionarn
            """
            return self._values.get('function_arn')

        @property
        def invocation_type(self) -> typing.Optional[str]:
            """``CfnReceiptRule.LambdaActionProperty.InvocationType``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-receiptrule-lambdaaction.html#cfn-ses-receiptrule-lambdaaction-invocationtype
            """
            return self._values.get('invocation_type')

        @property
        def topic_arn(self) -> typing.Optional[str]:
            """``CfnReceiptRule.LambdaActionProperty.TopicArn``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-receiptrule-lambdaaction.html#cfn-ses-receiptrule-lambdaaction-topicarn
            """
            return self._values.get('topic_arn')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'LambdaActionProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-ses.CfnReceiptRule.RuleProperty", jsii_struct_bases=[], name_mapping={'actions': 'actions', 'enabled': 'enabled', 'name': 'name', 'recipients': 'recipients', 'scan_enabled': 'scanEnabled', 'tls_policy': 'tlsPolicy'})
    class RuleProperty():
        def __init__(self, *, actions: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnReceiptRule.ActionProperty"]]]]]=None, enabled: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, name: typing.Optional[str]=None, recipients: typing.Optional[typing.List[str]]=None, scan_enabled: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, tls_policy: typing.Optional[str]=None):
            """
            :param actions: ``CfnReceiptRule.RuleProperty.Actions``.
            :param enabled: ``CfnReceiptRule.RuleProperty.Enabled``.
            :param name: ``CfnReceiptRule.RuleProperty.Name``.
            :param recipients: ``CfnReceiptRule.RuleProperty.Recipients``.
            :param scan_enabled: ``CfnReceiptRule.RuleProperty.ScanEnabled``.
            :param tls_policy: ``CfnReceiptRule.RuleProperty.TlsPolicy``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-receiptrule-rule.html
            """
            self._values = {
            }
            if actions is not None: self._values["actions"] = actions
            if enabled is not None: self._values["enabled"] = enabled
            if name is not None: self._values["name"] = name
            if recipients is not None: self._values["recipients"] = recipients
            if scan_enabled is not None: self._values["scan_enabled"] = scan_enabled
            if tls_policy is not None: self._values["tls_policy"] = tls_policy

        @property
        def actions(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnReceiptRule.ActionProperty"]]]]]:
            """``CfnReceiptRule.RuleProperty.Actions``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-receiptrule-rule.html#cfn-ses-receiptrule-rule-actions
            """
            return self._values.get('actions')

        @property
        def enabled(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
            """``CfnReceiptRule.RuleProperty.Enabled``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-receiptrule-rule.html#cfn-ses-receiptrule-rule-enabled
            """
            return self._values.get('enabled')

        @property
        def name(self) -> typing.Optional[str]:
            """``CfnReceiptRule.RuleProperty.Name``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-receiptrule-rule.html#cfn-ses-receiptrule-rule-name
            """
            return self._values.get('name')

        @property
        def recipients(self) -> typing.Optional[typing.List[str]]:
            """``CfnReceiptRule.RuleProperty.Recipients``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-receiptrule-rule.html#cfn-ses-receiptrule-rule-recipients
            """
            return self._values.get('recipients')

        @property
        def scan_enabled(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
            """``CfnReceiptRule.RuleProperty.ScanEnabled``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-receiptrule-rule.html#cfn-ses-receiptrule-rule-scanenabled
            """
            return self._values.get('scan_enabled')

        @property
        def tls_policy(self) -> typing.Optional[str]:
            """``CfnReceiptRule.RuleProperty.TlsPolicy``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-receiptrule-rule.html#cfn-ses-receiptrule-rule-tlspolicy
            """
            return self._values.get('tls_policy')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'RuleProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-ses.CfnReceiptRule.S3ActionProperty", jsii_struct_bases=[], name_mapping={'bucket_name': 'bucketName', 'kms_key_arn': 'kmsKeyArn', 'object_key_prefix': 'objectKeyPrefix', 'topic_arn': 'topicArn'})
    class S3ActionProperty():
        def __init__(self, *, bucket_name: str, kms_key_arn: typing.Optional[str]=None, object_key_prefix: typing.Optional[str]=None, topic_arn: typing.Optional[str]=None):
            """
            :param bucket_name: ``CfnReceiptRule.S3ActionProperty.BucketName``.
            :param kms_key_arn: ``CfnReceiptRule.S3ActionProperty.KmsKeyArn``.
            :param object_key_prefix: ``CfnReceiptRule.S3ActionProperty.ObjectKeyPrefix``.
            :param topic_arn: ``CfnReceiptRule.S3ActionProperty.TopicArn``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-receiptrule-s3action.html
            """
            self._values = {
                'bucket_name': bucket_name,
            }
            if kms_key_arn is not None: self._values["kms_key_arn"] = kms_key_arn
            if object_key_prefix is not None: self._values["object_key_prefix"] = object_key_prefix
            if topic_arn is not None: self._values["topic_arn"] = topic_arn

        @property
        def bucket_name(self) -> str:
            """``CfnReceiptRule.S3ActionProperty.BucketName``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-receiptrule-s3action.html#cfn-ses-receiptrule-s3action-bucketname
            """
            return self._values.get('bucket_name')

        @property
        def kms_key_arn(self) -> typing.Optional[str]:
            """``CfnReceiptRule.S3ActionProperty.KmsKeyArn``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-receiptrule-s3action.html#cfn-ses-receiptrule-s3action-kmskeyarn
            """
            return self._values.get('kms_key_arn')

        @property
        def object_key_prefix(self) -> typing.Optional[str]:
            """``CfnReceiptRule.S3ActionProperty.ObjectKeyPrefix``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-receiptrule-s3action.html#cfn-ses-receiptrule-s3action-objectkeyprefix
            """
            return self._values.get('object_key_prefix')

        @property
        def topic_arn(self) -> typing.Optional[str]:
            """``CfnReceiptRule.S3ActionProperty.TopicArn``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-receiptrule-s3action.html#cfn-ses-receiptrule-s3action-topicarn
            """
            return self._values.get('topic_arn')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'S3ActionProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-ses.CfnReceiptRule.SNSActionProperty", jsii_struct_bases=[], name_mapping={'encoding': 'encoding', 'topic_arn': 'topicArn'})
    class SNSActionProperty():
        def __init__(self, *, encoding: typing.Optional[str]=None, topic_arn: typing.Optional[str]=None):
            """
            :param encoding: ``CfnReceiptRule.SNSActionProperty.Encoding``.
            :param topic_arn: ``CfnReceiptRule.SNSActionProperty.TopicArn``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-receiptrule-snsaction.html
            """
            self._values = {
            }
            if encoding is not None: self._values["encoding"] = encoding
            if topic_arn is not None: self._values["topic_arn"] = topic_arn

        @property
        def encoding(self) -> typing.Optional[str]:
            """``CfnReceiptRule.SNSActionProperty.Encoding``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-receiptrule-snsaction.html#cfn-ses-receiptrule-snsaction-encoding
            """
            return self._values.get('encoding')

        @property
        def topic_arn(self) -> typing.Optional[str]:
            """``CfnReceiptRule.SNSActionProperty.TopicArn``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-receiptrule-snsaction.html#cfn-ses-receiptrule-snsaction-topicarn
            """
            return self._values.get('topic_arn')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'SNSActionProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-ses.CfnReceiptRule.StopActionProperty", jsii_struct_bases=[], name_mapping={'scope': 'scope', 'topic_arn': 'topicArn'})
    class StopActionProperty():
        def __init__(self, *, scope: str, topic_arn: typing.Optional[str]=None):
            """
            :param scope: ``CfnReceiptRule.StopActionProperty.Scope``.
            :param topic_arn: ``CfnReceiptRule.StopActionProperty.TopicArn``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-receiptrule-stopaction.html
            """
            self._values = {
                'scope': scope,
            }
            if topic_arn is not None: self._values["topic_arn"] = topic_arn

        @property
        def scope(self) -> str:
            """``CfnReceiptRule.StopActionProperty.Scope``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-receiptrule-stopaction.html#cfn-ses-receiptrule-stopaction-scope
            """
            return self._values.get('scope')

        @property
        def topic_arn(self) -> typing.Optional[str]:
            """``CfnReceiptRule.StopActionProperty.TopicArn``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-receiptrule-stopaction.html#cfn-ses-receiptrule-stopaction-topicarn
            """
            return self._values.get('topic_arn')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'StopActionProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-ses.CfnReceiptRule.WorkmailActionProperty", jsii_struct_bases=[], name_mapping={'organization_arn': 'organizationArn', 'topic_arn': 'topicArn'})
    class WorkmailActionProperty():
        def __init__(self, *, organization_arn: str, topic_arn: typing.Optional[str]=None):
            """
            :param organization_arn: ``CfnReceiptRule.WorkmailActionProperty.OrganizationArn``.
            :param topic_arn: ``CfnReceiptRule.WorkmailActionProperty.TopicArn``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-receiptrule-workmailaction.html
            """
            self._values = {
                'organization_arn': organization_arn,
            }
            if topic_arn is not None: self._values["topic_arn"] = topic_arn

        @property
        def organization_arn(self) -> str:
            """``CfnReceiptRule.WorkmailActionProperty.OrganizationArn``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-receiptrule-workmailaction.html#cfn-ses-receiptrule-workmailaction-organizationarn
            """
            return self._values.get('organization_arn')

        @property
        def topic_arn(self) -> typing.Optional[str]:
            """``CfnReceiptRule.WorkmailActionProperty.TopicArn``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-receiptrule-workmailaction.html#cfn-ses-receiptrule-workmailaction-topicarn
            """
            return self._values.get('topic_arn')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'WorkmailActionProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



@jsii.data_type(jsii_type="@aws-cdk/aws-ses.CfnReceiptRuleProps", jsii_struct_bases=[], name_mapping={'rule': 'rule', 'rule_set_name': 'ruleSetName', 'after': 'after'})
class CfnReceiptRuleProps():
    def __init__(self, *, rule: typing.Union[aws_cdk.core.IResolvable, "CfnReceiptRule.RuleProperty"], rule_set_name: str, after: typing.Optional[str]=None):
        """Properties for defining a ``AWS::SES::ReceiptRule``.

        :param rule: ``AWS::SES::ReceiptRule.Rule``.
        :param rule_set_name: ``AWS::SES::ReceiptRule.RuleSetName``.
        :param after: ``AWS::SES::ReceiptRule.After``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ses-receiptrule.html
        """
        self._values = {
            'rule': rule,
            'rule_set_name': rule_set_name,
        }
        if after is not None: self._values["after"] = after

    @property
    def rule(self) -> typing.Union[aws_cdk.core.IResolvable, "CfnReceiptRule.RuleProperty"]:
        """``AWS::SES::ReceiptRule.Rule``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ses-receiptrule.html#cfn-ses-receiptrule-rule
        """
        return self._values.get('rule')

    @property
    def rule_set_name(self) -> str:
        """``AWS::SES::ReceiptRule.RuleSetName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ses-receiptrule.html#cfn-ses-receiptrule-rulesetname
        """
        return self._values.get('rule_set_name')

    @property
    def after(self) -> typing.Optional[str]:
        """``AWS::SES::ReceiptRule.After``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ses-receiptrule.html#cfn-ses-receiptrule-after
        """
        return self._values.get('after')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnReceiptRuleProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnReceiptRuleSet(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ses.CfnReceiptRuleSet"):
    """A CloudFormation ``AWS::SES::ReceiptRuleSet``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ses-receiptruleset.html
    cloudformationResource:
    :cloudformationResource:: AWS::SES::ReceiptRuleSet
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, rule_set_name: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::SES::ReceiptRuleSet``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param rule_set_name: ``AWS::SES::ReceiptRuleSet.RuleSetName``.
        """
        props = CfnReceiptRuleSetProps(rule_set_name=rule_set_name)

        jsii.create(CfnReceiptRuleSet, self, [scope, id, props])

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
    @jsii.member(jsii_name="ruleSetName")
    def rule_set_name(self) -> typing.Optional[str]:
        """``AWS::SES::ReceiptRuleSet.RuleSetName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ses-receiptruleset.html#cfn-ses-receiptruleset-rulesetname
        """
        return jsii.get(self, "ruleSetName")

    @rule_set_name.setter
    def rule_set_name(self, value: typing.Optional[str]):
        return jsii.set(self, "ruleSetName", value)


@jsii.data_type(jsii_type="@aws-cdk/aws-ses.CfnReceiptRuleSetProps", jsii_struct_bases=[], name_mapping={'rule_set_name': 'ruleSetName'})
class CfnReceiptRuleSetProps():
    def __init__(self, *, rule_set_name: typing.Optional[str]=None):
        """Properties for defining a ``AWS::SES::ReceiptRuleSet``.

        :param rule_set_name: ``AWS::SES::ReceiptRuleSet.RuleSetName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ses-receiptruleset.html
        """
        self._values = {
        }
        if rule_set_name is not None: self._values["rule_set_name"] = rule_set_name

    @property
    def rule_set_name(self) -> typing.Optional[str]:
        """``AWS::SES::ReceiptRuleSet.RuleSetName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ses-receiptruleset.html#cfn-ses-receiptruleset-rulesetname
        """
        return self._values.get('rule_set_name')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnReceiptRuleSetProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnTemplate(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ses.CfnTemplate"):
    """A CloudFormation ``AWS::SES::Template``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ses-template.html
    cloudformationResource:
    :cloudformationResource:: AWS::SES::Template
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, template: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["TemplateProperty"]]]=None) -> None:
        """Create a new ``AWS::SES::Template``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param template: ``AWS::SES::Template.Template``.
        """
        props = CfnTemplateProps(template=template)

        jsii.create(CfnTemplate, self, [scope, id, props])

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
    @jsii.member(jsii_name="template")
    def template(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["TemplateProperty"]]]:
        """``AWS::SES::Template.Template``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ses-template.html#cfn-ses-template-template
        """
        return jsii.get(self, "template")

    @template.setter
    def template(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["TemplateProperty"]]]):
        return jsii.set(self, "template", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-ses.CfnTemplate.TemplateProperty", jsii_struct_bases=[], name_mapping={'html_part': 'htmlPart', 'subject_part': 'subjectPart', 'template_name': 'templateName', 'text_part': 'textPart'})
    class TemplateProperty():
        def __init__(self, *, html_part: typing.Optional[str]=None, subject_part: typing.Optional[str]=None, template_name: typing.Optional[str]=None, text_part: typing.Optional[str]=None):
            """
            :param html_part: ``CfnTemplate.TemplateProperty.HtmlPart``.
            :param subject_part: ``CfnTemplate.TemplateProperty.SubjectPart``.
            :param template_name: ``CfnTemplate.TemplateProperty.TemplateName``.
            :param text_part: ``CfnTemplate.TemplateProperty.TextPart``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-template-template.html
            """
            self._values = {
            }
            if html_part is not None: self._values["html_part"] = html_part
            if subject_part is not None: self._values["subject_part"] = subject_part
            if template_name is not None: self._values["template_name"] = template_name
            if text_part is not None: self._values["text_part"] = text_part

        @property
        def html_part(self) -> typing.Optional[str]:
            """``CfnTemplate.TemplateProperty.HtmlPart``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-template-template.html#cfn-ses-template-template-htmlpart
            """
            return self._values.get('html_part')

        @property
        def subject_part(self) -> typing.Optional[str]:
            """``CfnTemplate.TemplateProperty.SubjectPart``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-template-template.html#cfn-ses-template-template-subjectpart
            """
            return self._values.get('subject_part')

        @property
        def template_name(self) -> typing.Optional[str]:
            """``CfnTemplate.TemplateProperty.TemplateName``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-template-template.html#cfn-ses-template-template-templatename
            """
            return self._values.get('template_name')

        @property
        def text_part(self) -> typing.Optional[str]:
            """``CfnTemplate.TemplateProperty.TextPart``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-template-template.html#cfn-ses-template-template-textpart
            """
            return self._values.get('text_part')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'TemplateProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



@jsii.data_type(jsii_type="@aws-cdk/aws-ses.CfnTemplateProps", jsii_struct_bases=[], name_mapping={'template': 'template'})
class CfnTemplateProps():
    def __init__(self, *, template: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnTemplate.TemplateProperty"]]]=None):
        """Properties for defining a ``AWS::SES::Template``.

        :param template: ``AWS::SES::Template.Template``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ses-template.html
        """
        self._values = {
        }
        if template is not None: self._values["template"] = template

    @property
    def template(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnTemplate.TemplateProperty"]]]:
        """``AWS::SES::Template.Template``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ses-template.html#cfn-ses-template-template
        """
        return self._values.get('template')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnTemplateProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class DropSpamReceiptRule(aws_cdk.core.Construct, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ses.DropSpamReceiptRule"):
    """A rule added at the top of the rule set to drop spam/virus.

    see
    :see: https://docs.aws.amazon.com/ses/latest/DeveloperGuide/receiving-email-action-lambda-example-functions.html
    stability
    :stability: experimental
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, rule_set: "IReceiptRuleSet", actions: typing.Optional[typing.List["IReceiptRuleAction"]]=None, after: typing.Optional["IReceiptRule"]=None, enabled: typing.Optional[bool]=None, receipt_rule_name: typing.Optional[str]=None, recipients: typing.Optional[typing.List[str]]=None, scan_enabled: typing.Optional[bool]=None, tls_policy: typing.Optional["TlsPolicy"]=None) -> None:
        """
        :param scope: -
        :param id: -
        :param props: -
        :param rule_set: The name of the rule set that the receipt rule will be added to.
        :param actions: An ordered list of actions to perform on messages that match at least one of the recipient email addresses or domains specified in the receipt rule. Default: - No actions.
        :param after: An existing rule after which the new rule will be placed. Default: - The new rule is inserted at the beginning of the rule list.
        :param enabled: Whether the rule is active. Default: true
        :param receipt_rule_name: The name for the rule. Default: - A CloudFormation generated name.
        :param recipients: The recipient domains and email addresses that the receipt rule applies to. Default: - Match all recipients under all verified domains.
        :param scan_enabled: Whether to scan for spam and viruses. Default: false
        :param tls_policy: Whether Amazon SES should require that incoming email is delivered over a connection encrypted with Transport Layer Security (TLS). Default: - Optional which will not check for TLS.

        stability
        :stability: experimental
        """
        props = DropSpamReceiptRuleProps(rule_set=rule_set, actions=actions, after=after, enabled=enabled, receipt_rule_name=receipt_rule_name, recipients=recipients, scan_enabled=scan_enabled, tls_policy=tls_policy)

        jsii.create(DropSpamReceiptRule, self, [scope, id, props])

    @property
    @jsii.member(jsii_name="rule")
    def rule(self) -> "ReceiptRule":
        """
        stability
        :stability: experimental
        """
        return jsii.get(self, "rule")


@jsii.interface(jsii_type="@aws-cdk/aws-ses.IReceiptRule")
class IReceiptRule(aws_cdk.core.IResource, jsii.compat.Protocol):
    """A receipt rule.

    stability
    :stability: experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IReceiptRuleProxy

    @property
    @jsii.member(jsii_name="receiptRuleName")
    def receipt_rule_name(self) -> str:
        """The name of the receipt rule.

        stability
        :stability: experimental
        attribute:
        :attribute:: true
        """
        ...


class _IReceiptRuleProxy(jsii.proxy_for(aws_cdk.core.IResource)):
    """A receipt rule.

    stability
    :stability: experimental
    """
    __jsii_type__ = "@aws-cdk/aws-ses.IReceiptRule"
    @property
    @jsii.member(jsii_name="receiptRuleName")
    def receipt_rule_name(self) -> str:
        """The name of the receipt rule.

        stability
        :stability: experimental
        attribute:
        :attribute:: true
        """
        return jsii.get(self, "receiptRuleName")


@jsii.interface(jsii_type="@aws-cdk/aws-ses.IReceiptRuleAction")
class IReceiptRuleAction(jsii.compat.Protocol):
    """An abstract action for a receipt rule.

    stability
    :stability: experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IReceiptRuleActionProxy

    @jsii.member(jsii_name="bind")
    def bind(self, receipt_rule: "IReceiptRule") -> "ReceiptRuleActionConfig":
        """Returns the receipt rule action specification.

        :param receipt_rule: -

        stability
        :stability: experimental
        """
        ...


class _IReceiptRuleActionProxy():
    """An abstract action for a receipt rule.

    stability
    :stability: experimental
    """
    __jsii_type__ = "@aws-cdk/aws-ses.IReceiptRuleAction"
    @jsii.member(jsii_name="bind")
    def bind(self, receipt_rule: "IReceiptRule") -> "ReceiptRuleActionConfig":
        """Returns the receipt rule action specification.

        :param receipt_rule: -

        stability
        :stability: experimental
        """
        return jsii.invoke(self, "bind", [receipt_rule])


@jsii.interface(jsii_type="@aws-cdk/aws-ses.IReceiptRuleSet")
class IReceiptRuleSet(aws_cdk.core.IResource, jsii.compat.Protocol):
    """A receipt rule set.

    stability
    :stability: experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IReceiptRuleSetProxy

    @property
    @jsii.member(jsii_name="receiptRuleSetName")
    def receipt_rule_set_name(self) -> str:
        """The receipt rule set name.

        stability
        :stability: experimental
        attribute:
        :attribute:: true
        """
        ...

    @jsii.member(jsii_name="addRule")
    def add_rule(self, id: str, *, actions: typing.Optional[typing.List["IReceiptRuleAction"]]=None, after: typing.Optional["IReceiptRule"]=None, enabled: typing.Optional[bool]=None, receipt_rule_name: typing.Optional[str]=None, recipients: typing.Optional[typing.List[str]]=None, scan_enabled: typing.Optional[bool]=None, tls_policy: typing.Optional["TlsPolicy"]=None) -> "ReceiptRule":
        """Adds a new receipt rule in this rule set.

        The new rule is added after
        the last added rule unless ``after`` is specified.

        :param id: -
        :param options: -
        :param actions: An ordered list of actions to perform on messages that match at least one of the recipient email addresses or domains specified in the receipt rule. Default: - No actions.
        :param after: An existing rule after which the new rule will be placed. Default: - The new rule is inserted at the beginning of the rule list.
        :param enabled: Whether the rule is active. Default: true
        :param receipt_rule_name: The name for the rule. Default: - A CloudFormation generated name.
        :param recipients: The recipient domains and email addresses that the receipt rule applies to. Default: - Match all recipients under all verified domains.
        :param scan_enabled: Whether to scan for spam and viruses. Default: false
        :param tls_policy: Whether Amazon SES should require that incoming email is delivered over a connection encrypted with Transport Layer Security (TLS). Default: - Optional which will not check for TLS.

        stability
        :stability: experimental
        """
        ...


class _IReceiptRuleSetProxy(jsii.proxy_for(aws_cdk.core.IResource)):
    """A receipt rule set.

    stability
    :stability: experimental
    """
    __jsii_type__ = "@aws-cdk/aws-ses.IReceiptRuleSet"
    @property
    @jsii.member(jsii_name="receiptRuleSetName")
    def receipt_rule_set_name(self) -> str:
        """The receipt rule set name.

        stability
        :stability: experimental
        attribute:
        :attribute:: true
        """
        return jsii.get(self, "receiptRuleSetName")

    @jsii.member(jsii_name="addRule")
    def add_rule(self, id: str, *, actions: typing.Optional[typing.List["IReceiptRuleAction"]]=None, after: typing.Optional["IReceiptRule"]=None, enabled: typing.Optional[bool]=None, receipt_rule_name: typing.Optional[str]=None, recipients: typing.Optional[typing.List[str]]=None, scan_enabled: typing.Optional[bool]=None, tls_policy: typing.Optional["TlsPolicy"]=None) -> "ReceiptRule":
        """Adds a new receipt rule in this rule set.

        The new rule is added after
        the last added rule unless ``after`` is specified.

        :param id: -
        :param options: -
        :param actions: An ordered list of actions to perform on messages that match at least one of the recipient email addresses or domains specified in the receipt rule. Default: - No actions.
        :param after: An existing rule after which the new rule will be placed. Default: - The new rule is inserted at the beginning of the rule list.
        :param enabled: Whether the rule is active. Default: true
        :param receipt_rule_name: The name for the rule. Default: - A CloudFormation generated name.
        :param recipients: The recipient domains and email addresses that the receipt rule applies to. Default: - Match all recipients under all verified domains.
        :param scan_enabled: Whether to scan for spam and viruses. Default: false
        :param tls_policy: Whether Amazon SES should require that incoming email is delivered over a connection encrypted with Transport Layer Security (TLS). Default: - Optional which will not check for TLS.

        stability
        :stability: experimental
        """
        options = ReceiptRuleOptions(actions=actions, after=after, enabled=enabled, receipt_rule_name=receipt_rule_name, recipients=recipients, scan_enabled=scan_enabled, tls_policy=tls_policy)

        return jsii.invoke(self, "addRule", [id, options])


class ReceiptFilter(aws_cdk.core.Resource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ses.ReceiptFilter"):
    """A receipt filter.

    When instantiated without props, it creates a
    block all receipt filter.

    stability
    :stability: experimental
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, ip: typing.Optional[str]=None, policy: typing.Optional["ReceiptFilterPolicy"]=None, receipt_filter_name: typing.Optional[str]=None) -> None:
        """
        :param scope: -
        :param id: -
        :param props: -
        :param ip: The ip address or range to filter. Default: 0.0.0.0/0
        :param policy: The policy for the filter. Default: Block
        :param receipt_filter_name: The name for the receipt filter. Default: a CloudFormation generated name

        stability
        :stability: experimental
        """
        props = ReceiptFilterProps(ip=ip, policy=policy, receipt_filter_name=receipt_filter_name)

        jsii.create(ReceiptFilter, self, [scope, id, props])


@jsii.enum(jsii_type="@aws-cdk/aws-ses.ReceiptFilterPolicy")
class ReceiptFilterPolicy(enum.Enum):
    """The policy for the receipt filter.

    stability
    :stability: experimental
    """
    ALLOW = "ALLOW"
    """Allow the ip address or range.

    stability
    :stability: experimental
    """
    BLOCK = "BLOCK"
    """Block the ip address or range.

    stability
    :stability: experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ses.ReceiptFilterProps", jsii_struct_bases=[], name_mapping={'ip': 'ip', 'policy': 'policy', 'receipt_filter_name': 'receiptFilterName'})
class ReceiptFilterProps():
    def __init__(self, *, ip: typing.Optional[str]=None, policy: typing.Optional["ReceiptFilterPolicy"]=None, receipt_filter_name: typing.Optional[str]=None):
        """Construction properties for a ReceiptFilter.

        :param ip: The ip address or range to filter. Default: 0.0.0.0/0
        :param policy: The policy for the filter. Default: Block
        :param receipt_filter_name: The name for the receipt filter. Default: a CloudFormation generated name

        stability
        :stability: experimental
        """
        self._values = {
        }
        if ip is not None: self._values["ip"] = ip
        if policy is not None: self._values["policy"] = policy
        if receipt_filter_name is not None: self._values["receipt_filter_name"] = receipt_filter_name

    @property
    def ip(self) -> typing.Optional[str]:
        """The ip address or range to filter.

        default
        :default: 0.0.0.0/0

        stability
        :stability: experimental
        """
        return self._values.get('ip')

    @property
    def policy(self) -> typing.Optional["ReceiptFilterPolicy"]:
        """The policy for the filter.

        default
        :default: Block

        stability
        :stability: experimental
        """
        return self._values.get('policy')

    @property
    def receipt_filter_name(self) -> typing.Optional[str]:
        """The name for the receipt filter.

        default
        :default: a CloudFormation generated name

        stability
        :stability: experimental
        """
        return self._values.get('receipt_filter_name')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'ReceiptFilterProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


@jsii.implements(IReceiptRule)
class ReceiptRule(aws_cdk.core.Resource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ses.ReceiptRule"):
    """A new receipt rule.

    stability
    :stability: experimental
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, rule_set: "IReceiptRuleSet", actions: typing.Optional[typing.List["IReceiptRuleAction"]]=None, after: typing.Optional["IReceiptRule"]=None, enabled: typing.Optional[bool]=None, receipt_rule_name: typing.Optional[str]=None, recipients: typing.Optional[typing.List[str]]=None, scan_enabled: typing.Optional[bool]=None, tls_policy: typing.Optional["TlsPolicy"]=None) -> None:
        """
        :param scope: -
        :param id: -
        :param props: -
        :param rule_set: The name of the rule set that the receipt rule will be added to.
        :param actions: An ordered list of actions to perform on messages that match at least one of the recipient email addresses or domains specified in the receipt rule. Default: - No actions.
        :param after: An existing rule after which the new rule will be placed. Default: - The new rule is inserted at the beginning of the rule list.
        :param enabled: Whether the rule is active. Default: true
        :param receipt_rule_name: The name for the rule. Default: - A CloudFormation generated name.
        :param recipients: The recipient domains and email addresses that the receipt rule applies to. Default: - Match all recipients under all verified domains.
        :param scan_enabled: Whether to scan for spam and viruses. Default: false
        :param tls_policy: Whether Amazon SES should require that incoming email is delivered over a connection encrypted with Transport Layer Security (TLS). Default: - Optional which will not check for TLS.

        stability
        :stability: experimental
        """
        props = ReceiptRuleProps(rule_set=rule_set, actions=actions, after=after, enabled=enabled, receipt_rule_name=receipt_rule_name, recipients=recipients, scan_enabled=scan_enabled, tls_policy=tls_policy)

        jsii.create(ReceiptRule, self, [scope, id, props])

    @jsii.member(jsii_name="fromReceiptRuleName")
    @classmethod
    def from_receipt_rule_name(cls, scope: aws_cdk.core.Construct, id: str, receipt_rule_name: str) -> "IReceiptRule":
        """
        :param scope: -
        :param id: -
        :param receipt_rule_name: -

        stability
        :stability: experimental
        """
        return jsii.sinvoke(cls, "fromReceiptRuleName", [scope, id, receipt_rule_name])

    @jsii.member(jsii_name="addAction")
    def add_action(self, action: "IReceiptRuleAction") -> None:
        """Adds an action to this receipt rule.

        :param action: -

        stability
        :stability: experimental
        """
        return jsii.invoke(self, "addAction", [action])

    @property
    @jsii.member(jsii_name="receiptRuleName")
    def receipt_rule_name(self) -> str:
        """The name of the receipt rule.

        stability
        :stability: experimental
        """
        return jsii.get(self, "receiptRuleName")


@jsii.data_type(jsii_type="@aws-cdk/aws-ses.ReceiptRuleActionConfig", jsii_struct_bases=[], name_mapping={'add_header_action': 'addHeaderAction', 'bounce_action': 'bounceAction', 'lambda_action': 'lambdaAction', 's3_action': 's3Action', 'sns_action': 'snsAction', 'stop_action': 'stopAction', 'workmail_action': 'workmailAction'})
class ReceiptRuleActionConfig():
    def __init__(self, *, add_header_action: typing.Optional["CfnReceiptRule.AddHeaderActionProperty"]=None, bounce_action: typing.Optional["CfnReceiptRule.BounceActionProperty"]=None, lambda_action: typing.Optional["CfnReceiptRule.LambdaActionProperty"]=None, s3_action: typing.Optional["CfnReceiptRule.S3ActionProperty"]=None, sns_action: typing.Optional["CfnReceiptRule.SNSActionProperty"]=None, stop_action: typing.Optional["CfnReceiptRule.StopActionProperty"]=None, workmail_action: typing.Optional["CfnReceiptRule.WorkmailActionProperty"]=None):
        """Properties for a receipt rule action.

        :param add_header_action: Adds a header to the received email.
        :param bounce_action: Rejects the received email by returning a bounce response to the sender and, optionally, publishes a notification to Amazon SNS.
        :param lambda_action: Calls an AWS Lambda function, and optionally, publishes a notification to Amazon SNS.
        :param s3_action: Saves the received message to an Amazon S3 bucket and, optionally, publishes a notification to Amazon SNS.
        :param sns_action: Publishes the email content within a notification to Amazon SNS.
        :param stop_action: Terminates the evaluation of the receipt rule set and optionally publishes a notification to Amazon SNS.
        :param workmail_action: Calls Amazon WorkMail and, optionally, publishes a notification to Amazon SNS.

        stability
        :stability: experimental
        """
        self._values = {
        }
        if add_header_action is not None: self._values["add_header_action"] = add_header_action
        if bounce_action is not None: self._values["bounce_action"] = bounce_action
        if lambda_action is not None: self._values["lambda_action"] = lambda_action
        if s3_action is not None: self._values["s3_action"] = s3_action
        if sns_action is not None: self._values["sns_action"] = sns_action
        if stop_action is not None: self._values["stop_action"] = stop_action
        if workmail_action is not None: self._values["workmail_action"] = workmail_action

    @property
    def add_header_action(self) -> typing.Optional["CfnReceiptRule.AddHeaderActionProperty"]:
        """Adds a header to the received email.

        stability
        :stability: experimental
        """
        return self._values.get('add_header_action')

    @property
    def bounce_action(self) -> typing.Optional["CfnReceiptRule.BounceActionProperty"]:
        """Rejects the received email by returning a bounce response to the sender and, optionally, publishes a notification to Amazon SNS.

        stability
        :stability: experimental
        """
        return self._values.get('bounce_action')

    @property
    def lambda_action(self) -> typing.Optional["CfnReceiptRule.LambdaActionProperty"]:
        """Calls an AWS Lambda function, and optionally, publishes a notification to Amazon SNS.

        stability
        :stability: experimental
        """
        return self._values.get('lambda_action')

    @property
    def s3_action(self) -> typing.Optional["CfnReceiptRule.S3ActionProperty"]:
        """Saves the received message to an Amazon S3 bucket and, optionally, publishes a notification to Amazon SNS.

        stability
        :stability: experimental
        """
        return self._values.get('s3_action')

    @property
    def sns_action(self) -> typing.Optional["CfnReceiptRule.SNSActionProperty"]:
        """Publishes the email content within a notification to Amazon SNS.

        stability
        :stability: experimental
        """
        return self._values.get('sns_action')

    @property
    def stop_action(self) -> typing.Optional["CfnReceiptRule.StopActionProperty"]:
        """Terminates the evaluation of the receipt rule set and optionally publishes a notification to Amazon SNS.

        stability
        :stability: experimental
        """
        return self._values.get('stop_action')

    @property
    def workmail_action(self) -> typing.Optional["CfnReceiptRule.WorkmailActionProperty"]:
        """Calls Amazon WorkMail and, optionally, publishes a notification to Amazon SNS.

        stability
        :stability: experimental
        """
        return self._values.get('workmail_action')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'ReceiptRuleActionConfig(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


@jsii.data_type(jsii_type="@aws-cdk/aws-ses.ReceiptRuleOptions", jsii_struct_bases=[], name_mapping={'actions': 'actions', 'after': 'after', 'enabled': 'enabled', 'receipt_rule_name': 'receiptRuleName', 'recipients': 'recipients', 'scan_enabled': 'scanEnabled', 'tls_policy': 'tlsPolicy'})
class ReceiptRuleOptions():
    def __init__(self, *, actions: typing.Optional[typing.List["IReceiptRuleAction"]]=None, after: typing.Optional["IReceiptRule"]=None, enabled: typing.Optional[bool]=None, receipt_rule_name: typing.Optional[str]=None, recipients: typing.Optional[typing.List[str]]=None, scan_enabled: typing.Optional[bool]=None, tls_policy: typing.Optional["TlsPolicy"]=None):
        """Options to add a receipt rule to a receipt rule set.

        :param actions: An ordered list of actions to perform on messages that match at least one of the recipient email addresses or domains specified in the receipt rule. Default: - No actions.
        :param after: An existing rule after which the new rule will be placed. Default: - The new rule is inserted at the beginning of the rule list.
        :param enabled: Whether the rule is active. Default: true
        :param receipt_rule_name: The name for the rule. Default: - A CloudFormation generated name.
        :param recipients: The recipient domains and email addresses that the receipt rule applies to. Default: - Match all recipients under all verified domains.
        :param scan_enabled: Whether to scan for spam and viruses. Default: false
        :param tls_policy: Whether Amazon SES should require that incoming email is delivered over a connection encrypted with Transport Layer Security (TLS). Default: - Optional which will not check for TLS.

        stability
        :stability: experimental
        """
        self._values = {
        }
        if actions is not None: self._values["actions"] = actions
        if after is not None: self._values["after"] = after
        if enabled is not None: self._values["enabled"] = enabled
        if receipt_rule_name is not None: self._values["receipt_rule_name"] = receipt_rule_name
        if recipients is not None: self._values["recipients"] = recipients
        if scan_enabled is not None: self._values["scan_enabled"] = scan_enabled
        if tls_policy is not None: self._values["tls_policy"] = tls_policy

    @property
    def actions(self) -> typing.Optional[typing.List["IReceiptRuleAction"]]:
        """An ordered list of actions to perform on messages that match at least one of the recipient email addresses or domains specified in the receipt rule.

        default
        :default: - No actions.

        stability
        :stability: experimental
        """
        return self._values.get('actions')

    @property
    def after(self) -> typing.Optional["IReceiptRule"]:
        """An existing rule after which the new rule will be placed.

        default
        :default: - The new rule is inserted at the beginning of the rule list.

        stability
        :stability: experimental
        """
        return self._values.get('after')

    @property
    def enabled(self) -> typing.Optional[bool]:
        """Whether the rule is active.

        default
        :default: true

        stability
        :stability: experimental
        """
        return self._values.get('enabled')

    @property
    def receipt_rule_name(self) -> typing.Optional[str]:
        """The name for the rule.

        default
        :default: - A CloudFormation generated name.

        stability
        :stability: experimental
        """
        return self._values.get('receipt_rule_name')

    @property
    def recipients(self) -> typing.Optional[typing.List[str]]:
        """The recipient domains and email addresses that the receipt rule applies to.

        default
        :default: - Match all recipients under all verified domains.

        stability
        :stability: experimental
        """
        return self._values.get('recipients')

    @property
    def scan_enabled(self) -> typing.Optional[bool]:
        """Whether to scan for spam and viruses.

        default
        :default: false

        stability
        :stability: experimental
        """
        return self._values.get('scan_enabled')

    @property
    def tls_policy(self) -> typing.Optional["TlsPolicy"]:
        """Whether Amazon SES should require that incoming email is delivered over a connection encrypted with Transport Layer Security (TLS).

        default
        :default: - Optional which will not check for TLS.

        stability
        :stability: experimental
        """
        return self._values.get('tls_policy')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'ReceiptRuleOptions(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


@jsii.data_type(jsii_type="@aws-cdk/aws-ses.ReceiptRuleProps", jsii_struct_bases=[ReceiptRuleOptions], name_mapping={'actions': 'actions', 'after': 'after', 'enabled': 'enabled', 'receipt_rule_name': 'receiptRuleName', 'recipients': 'recipients', 'scan_enabled': 'scanEnabled', 'tls_policy': 'tlsPolicy', 'rule_set': 'ruleSet'})
class ReceiptRuleProps(ReceiptRuleOptions):
    def __init__(self, *, actions: typing.Optional[typing.List["IReceiptRuleAction"]]=None, after: typing.Optional["IReceiptRule"]=None, enabled: typing.Optional[bool]=None, receipt_rule_name: typing.Optional[str]=None, recipients: typing.Optional[typing.List[str]]=None, scan_enabled: typing.Optional[bool]=None, tls_policy: typing.Optional["TlsPolicy"]=None, rule_set: "IReceiptRuleSet"):
        """Construction properties for a ReceiptRule.

        :param actions: An ordered list of actions to perform on messages that match at least one of the recipient email addresses or domains specified in the receipt rule. Default: - No actions.
        :param after: An existing rule after which the new rule will be placed. Default: - The new rule is inserted at the beginning of the rule list.
        :param enabled: Whether the rule is active. Default: true
        :param receipt_rule_name: The name for the rule. Default: - A CloudFormation generated name.
        :param recipients: The recipient domains and email addresses that the receipt rule applies to. Default: - Match all recipients under all verified domains.
        :param scan_enabled: Whether to scan for spam and viruses. Default: false
        :param tls_policy: Whether Amazon SES should require that incoming email is delivered over a connection encrypted with Transport Layer Security (TLS). Default: - Optional which will not check for TLS.
        :param rule_set: The name of the rule set that the receipt rule will be added to.

        stability
        :stability: experimental
        """
        self._values = {
            'rule_set': rule_set,
        }
        if actions is not None: self._values["actions"] = actions
        if after is not None: self._values["after"] = after
        if enabled is not None: self._values["enabled"] = enabled
        if receipt_rule_name is not None: self._values["receipt_rule_name"] = receipt_rule_name
        if recipients is not None: self._values["recipients"] = recipients
        if scan_enabled is not None: self._values["scan_enabled"] = scan_enabled
        if tls_policy is not None: self._values["tls_policy"] = tls_policy

    @property
    def actions(self) -> typing.Optional[typing.List["IReceiptRuleAction"]]:
        """An ordered list of actions to perform on messages that match at least one of the recipient email addresses or domains specified in the receipt rule.

        default
        :default: - No actions.

        stability
        :stability: experimental
        """
        return self._values.get('actions')

    @property
    def after(self) -> typing.Optional["IReceiptRule"]:
        """An existing rule after which the new rule will be placed.

        default
        :default: - The new rule is inserted at the beginning of the rule list.

        stability
        :stability: experimental
        """
        return self._values.get('after')

    @property
    def enabled(self) -> typing.Optional[bool]:
        """Whether the rule is active.

        default
        :default: true

        stability
        :stability: experimental
        """
        return self._values.get('enabled')

    @property
    def receipt_rule_name(self) -> typing.Optional[str]:
        """The name for the rule.

        default
        :default: - A CloudFormation generated name.

        stability
        :stability: experimental
        """
        return self._values.get('receipt_rule_name')

    @property
    def recipients(self) -> typing.Optional[typing.List[str]]:
        """The recipient domains and email addresses that the receipt rule applies to.

        default
        :default: - Match all recipients under all verified domains.

        stability
        :stability: experimental
        """
        return self._values.get('recipients')

    @property
    def scan_enabled(self) -> typing.Optional[bool]:
        """Whether to scan for spam and viruses.

        default
        :default: false

        stability
        :stability: experimental
        """
        return self._values.get('scan_enabled')

    @property
    def tls_policy(self) -> typing.Optional["TlsPolicy"]:
        """Whether Amazon SES should require that incoming email is delivered over a connection encrypted with Transport Layer Security (TLS).

        default
        :default: - Optional which will not check for TLS.

        stability
        :stability: experimental
        """
        return self._values.get('tls_policy')

    @property
    def rule_set(self) -> "IReceiptRuleSet":
        """The name of the rule set that the receipt rule will be added to.

        stability
        :stability: experimental
        """
        return self._values.get('rule_set')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'ReceiptRuleProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


@jsii.data_type(jsii_type="@aws-cdk/aws-ses.DropSpamReceiptRuleProps", jsii_struct_bases=[ReceiptRuleProps], name_mapping={'actions': 'actions', 'after': 'after', 'enabled': 'enabled', 'receipt_rule_name': 'receiptRuleName', 'recipients': 'recipients', 'scan_enabled': 'scanEnabled', 'tls_policy': 'tlsPolicy', 'rule_set': 'ruleSet'})
class DropSpamReceiptRuleProps(ReceiptRuleProps):
    def __init__(self, *, actions: typing.Optional[typing.List["IReceiptRuleAction"]]=None, after: typing.Optional["IReceiptRule"]=None, enabled: typing.Optional[bool]=None, receipt_rule_name: typing.Optional[str]=None, recipients: typing.Optional[typing.List[str]]=None, scan_enabled: typing.Optional[bool]=None, tls_policy: typing.Optional["TlsPolicy"]=None, rule_set: "IReceiptRuleSet"):
        """
        :param actions: An ordered list of actions to perform on messages that match at least one of the recipient email addresses or domains specified in the receipt rule. Default: - No actions.
        :param after: An existing rule after which the new rule will be placed. Default: - The new rule is inserted at the beginning of the rule list.
        :param enabled: Whether the rule is active. Default: true
        :param receipt_rule_name: The name for the rule. Default: - A CloudFormation generated name.
        :param recipients: The recipient domains and email addresses that the receipt rule applies to. Default: - Match all recipients under all verified domains.
        :param scan_enabled: Whether to scan for spam and viruses. Default: false
        :param tls_policy: Whether Amazon SES should require that incoming email is delivered over a connection encrypted with Transport Layer Security (TLS). Default: - Optional which will not check for TLS.
        :param rule_set: The name of the rule set that the receipt rule will be added to.

        stability
        :stability: experimental
        """
        self._values = {
            'rule_set': rule_set,
        }
        if actions is not None: self._values["actions"] = actions
        if after is not None: self._values["after"] = after
        if enabled is not None: self._values["enabled"] = enabled
        if receipt_rule_name is not None: self._values["receipt_rule_name"] = receipt_rule_name
        if recipients is not None: self._values["recipients"] = recipients
        if scan_enabled is not None: self._values["scan_enabled"] = scan_enabled
        if tls_policy is not None: self._values["tls_policy"] = tls_policy

    @property
    def actions(self) -> typing.Optional[typing.List["IReceiptRuleAction"]]:
        """An ordered list of actions to perform on messages that match at least one of the recipient email addresses or domains specified in the receipt rule.

        default
        :default: - No actions.

        stability
        :stability: experimental
        """
        return self._values.get('actions')

    @property
    def after(self) -> typing.Optional["IReceiptRule"]:
        """An existing rule after which the new rule will be placed.

        default
        :default: - The new rule is inserted at the beginning of the rule list.

        stability
        :stability: experimental
        """
        return self._values.get('after')

    @property
    def enabled(self) -> typing.Optional[bool]:
        """Whether the rule is active.

        default
        :default: true

        stability
        :stability: experimental
        """
        return self._values.get('enabled')

    @property
    def receipt_rule_name(self) -> typing.Optional[str]:
        """The name for the rule.

        default
        :default: - A CloudFormation generated name.

        stability
        :stability: experimental
        """
        return self._values.get('receipt_rule_name')

    @property
    def recipients(self) -> typing.Optional[typing.List[str]]:
        """The recipient domains and email addresses that the receipt rule applies to.

        default
        :default: - Match all recipients under all verified domains.

        stability
        :stability: experimental
        """
        return self._values.get('recipients')

    @property
    def scan_enabled(self) -> typing.Optional[bool]:
        """Whether to scan for spam and viruses.

        default
        :default: false

        stability
        :stability: experimental
        """
        return self._values.get('scan_enabled')

    @property
    def tls_policy(self) -> typing.Optional["TlsPolicy"]:
        """Whether Amazon SES should require that incoming email is delivered over a connection encrypted with Transport Layer Security (TLS).

        default
        :default: - Optional which will not check for TLS.

        stability
        :stability: experimental
        """
        return self._values.get('tls_policy')

    @property
    def rule_set(self) -> "IReceiptRuleSet":
        """The name of the rule set that the receipt rule will be added to.

        stability
        :stability: experimental
        """
        return self._values.get('rule_set')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'DropSpamReceiptRuleProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


@jsii.implements(IReceiptRuleSet)
class ReceiptRuleSet(aws_cdk.core.Resource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ses.ReceiptRuleSet"):
    """A new receipt rule set.

    stability
    :stability: experimental
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, drop_spam: typing.Optional[bool]=None, receipt_rule_set_name: typing.Optional[str]=None, rules: typing.Optional[typing.List["ReceiptRuleOptions"]]=None) -> None:
        """
        :param scope: -
        :param id: -
        :param props: -
        :param drop_spam: Whether to add a first rule to stop processing messages that have at least one spam indicator. Default: false
        :param receipt_rule_set_name: The name for the receipt rule set. Default: - A CloudFormation generated name.
        :param rules: The list of rules to add to this rule set. Rules are added in the same order as they appear in the list. Default: - No rules are added to the rule set.

        stability
        :stability: experimental
        """
        props = ReceiptRuleSetProps(drop_spam=drop_spam, receipt_rule_set_name=receipt_rule_set_name, rules=rules)

        jsii.create(ReceiptRuleSet, self, [scope, id, props])

    @jsii.member(jsii_name="fromReceiptRuleSetName")
    @classmethod
    def from_receipt_rule_set_name(cls, scope: aws_cdk.core.Construct, id: str, receipt_rule_set_name: str) -> "IReceiptRuleSet":
        """Import an exported receipt rule set.

        :param scope: -
        :param id: -
        :param receipt_rule_set_name: -

        stability
        :stability: experimental
        """
        return jsii.sinvoke(cls, "fromReceiptRuleSetName", [scope, id, receipt_rule_set_name])

    @jsii.member(jsii_name="addDropSpamRule")
    def _add_drop_spam_rule(self) -> None:
        """Adds a drop spam rule.

        stability
        :stability: experimental
        """
        return jsii.invoke(self, "addDropSpamRule", [])

    @jsii.member(jsii_name="addRule")
    def add_rule(self, id: str, *, actions: typing.Optional[typing.List["IReceiptRuleAction"]]=None, after: typing.Optional["IReceiptRule"]=None, enabled: typing.Optional[bool]=None, receipt_rule_name: typing.Optional[str]=None, recipients: typing.Optional[typing.List[str]]=None, scan_enabled: typing.Optional[bool]=None, tls_policy: typing.Optional["TlsPolicy"]=None) -> "ReceiptRule":
        """Adds a new receipt rule in this rule set.

        The new rule is added after
        the last added rule unless ``after`` is specified.

        :param id: -
        :param options: -
        :param actions: An ordered list of actions to perform on messages that match at least one of the recipient email addresses or domains specified in the receipt rule. Default: - No actions.
        :param after: An existing rule after which the new rule will be placed. Default: - The new rule is inserted at the beginning of the rule list.
        :param enabled: Whether the rule is active. Default: true
        :param receipt_rule_name: The name for the rule. Default: - A CloudFormation generated name.
        :param recipients: The recipient domains and email addresses that the receipt rule applies to. Default: - Match all recipients under all verified domains.
        :param scan_enabled: Whether to scan for spam and viruses. Default: false
        :param tls_policy: Whether Amazon SES should require that incoming email is delivered over a connection encrypted with Transport Layer Security (TLS). Default: - Optional which will not check for TLS.

        stability
        :stability: experimental
        """
        options = ReceiptRuleOptions(actions=actions, after=after, enabled=enabled, receipt_rule_name=receipt_rule_name, recipients=recipients, scan_enabled=scan_enabled, tls_policy=tls_policy)

        return jsii.invoke(self, "addRule", [id, options])

    @property
    @jsii.member(jsii_name="receiptRuleSetName")
    def receipt_rule_set_name(self) -> str:
        """The receipt rule set name.

        stability
        :stability: experimental
        """
        return jsii.get(self, "receiptRuleSetName")


@jsii.data_type(jsii_type="@aws-cdk/aws-ses.ReceiptRuleSetProps", jsii_struct_bases=[], name_mapping={'drop_spam': 'dropSpam', 'receipt_rule_set_name': 'receiptRuleSetName', 'rules': 'rules'})
class ReceiptRuleSetProps():
    def __init__(self, *, drop_spam: typing.Optional[bool]=None, receipt_rule_set_name: typing.Optional[str]=None, rules: typing.Optional[typing.List["ReceiptRuleOptions"]]=None):
        """Construction properties for a ReceiptRuleSet.

        :param drop_spam: Whether to add a first rule to stop processing messages that have at least one spam indicator. Default: false
        :param receipt_rule_set_name: The name for the receipt rule set. Default: - A CloudFormation generated name.
        :param rules: The list of rules to add to this rule set. Rules are added in the same order as they appear in the list. Default: - No rules are added to the rule set.

        stability
        :stability: experimental
        """
        self._values = {
        }
        if drop_spam is not None: self._values["drop_spam"] = drop_spam
        if receipt_rule_set_name is not None: self._values["receipt_rule_set_name"] = receipt_rule_set_name
        if rules is not None: self._values["rules"] = rules

    @property
    def drop_spam(self) -> typing.Optional[bool]:
        """Whether to add a first rule to stop processing messages that have at least one spam indicator.

        default
        :default: false

        stability
        :stability: experimental
        """
        return self._values.get('drop_spam')

    @property
    def receipt_rule_set_name(self) -> typing.Optional[str]:
        """The name for the receipt rule set.

        default
        :default: - A CloudFormation generated name.

        stability
        :stability: experimental
        """
        return self._values.get('receipt_rule_set_name')

    @property
    def rules(self) -> typing.Optional[typing.List["ReceiptRuleOptions"]]:
        """The list of rules to add to this rule set.

        Rules are added in the same
        order as they appear in the list.

        default
        :default: - No rules are added to the rule set.

        stability
        :stability: experimental
        """
        return self._values.get('rules')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'ReceiptRuleSetProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


@jsii.enum(jsii_type="@aws-cdk/aws-ses.TlsPolicy")
class TlsPolicy(enum.Enum):
    """The type of TLS policy for a receipt rule.

    stability
    :stability: experimental
    """
    OPTIONAL = "OPTIONAL"
    """Do not check for TLS.

    stability
    :stability: experimental
    """
    REQUIRE = "REQUIRE"
    """Bounce emails that are not received over TLS.

    stability
    :stability: experimental
    """

class WhiteListReceiptFilter(aws_cdk.core.Construct, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ses.WhiteListReceiptFilter"):
    """A white list receipt filter.

    stability
    :stability: experimental
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, ips: typing.List[str]) -> None:
        """
        :param scope: -
        :param id: -
        :param props: -
        :param ips: A list of ip addresses or ranges to white list.

        stability
        :stability: experimental
        """
        props = WhiteListReceiptFilterProps(ips=ips)

        jsii.create(WhiteListReceiptFilter, self, [scope, id, props])


@jsii.data_type(jsii_type="@aws-cdk/aws-ses.WhiteListReceiptFilterProps", jsii_struct_bases=[], name_mapping={'ips': 'ips'})
class WhiteListReceiptFilterProps():
    def __init__(self, *, ips: typing.List[str]):
        """Construction properties for a WhiteListReceiptFilter.

        :param ips: A list of ip addresses or ranges to white list.

        stability
        :stability: experimental
        """
        self._values = {
            'ips': ips,
        }

    @property
    def ips(self) -> typing.List[str]:
        """A list of ip addresses or ranges to white list.

        stability
        :stability: experimental
        """
        return self._values.get('ips')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'WhiteListReceiptFilterProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


__all__ = ["CfnConfigurationSet", "CfnConfigurationSetEventDestination", "CfnConfigurationSetEventDestinationProps", "CfnConfigurationSetProps", "CfnReceiptFilter", "CfnReceiptFilterProps", "CfnReceiptRule", "CfnReceiptRuleProps", "CfnReceiptRuleSet", "CfnReceiptRuleSetProps", "CfnTemplate", "CfnTemplateProps", "DropSpamReceiptRule", "DropSpamReceiptRuleProps", "IReceiptRule", "IReceiptRuleAction", "IReceiptRuleSet", "ReceiptFilter", "ReceiptFilterPolicy", "ReceiptFilterProps", "ReceiptRule", "ReceiptRuleActionConfig", "ReceiptRuleOptions", "ReceiptRuleProps", "ReceiptRuleSet", "ReceiptRuleSetProps", "TlsPolicy", "WhiteListReceiptFilter", "WhiteListReceiptFilterProps", "__jsii_assembly__"]

publication.publish()
