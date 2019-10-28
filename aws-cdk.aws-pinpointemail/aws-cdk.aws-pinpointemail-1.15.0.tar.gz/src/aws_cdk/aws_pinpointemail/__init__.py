import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.core
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-pinpointemail", "1.15.0", __name__, "aws-pinpointemail@1.15.0.jsii.tgz")
class CfnConfigurationSet(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-pinpointemail.CfnConfigurationSet"):
    """A CloudFormation ``AWS::PinpointEmail::ConfigurationSet``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpointemail-configurationset.html
    cloudformationResource:
    :cloudformationResource:: AWS::PinpointEmail::ConfigurationSet
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, name: str, delivery_options: typing.Optional[typing.Union[typing.Optional["DeliveryOptionsProperty"], typing.Optional[aws_cdk.core.IResolvable]]]=None, reputation_options: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["ReputationOptionsProperty"]]]=None, sending_options: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["SendingOptionsProperty"]]]=None, tags: typing.Optional[typing.List["TagsProperty"]]=None, tracking_options: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["TrackingOptionsProperty"]]]=None) -> None:
        """Create a new ``AWS::PinpointEmail::ConfigurationSet``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param name: ``AWS::PinpointEmail::ConfigurationSet.Name``.
        :param delivery_options: ``AWS::PinpointEmail::ConfigurationSet.DeliveryOptions``.
        :param reputation_options: ``AWS::PinpointEmail::ConfigurationSet.ReputationOptions``.
        :param sending_options: ``AWS::PinpointEmail::ConfigurationSet.SendingOptions``.
        :param tags: ``AWS::PinpointEmail::ConfigurationSet.Tags``.
        :param tracking_options: ``AWS::PinpointEmail::ConfigurationSet.TrackingOptions``.
        """
        props = CfnConfigurationSetProps(name=name, delivery_options=delivery_options, reputation_options=reputation_options, sending_options=sending_options, tags=tags, tracking_options=tracking_options)

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
    def name(self) -> str:
        """``AWS::PinpointEmail::ConfigurationSet.Name``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpointemail-configurationset.html#cfn-pinpointemail-configurationset-name
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: str):
        return jsii.set(self, "name", value)

    @property
    @jsii.member(jsii_name="deliveryOptions")
    def delivery_options(self) -> typing.Optional[typing.Union[typing.Optional["DeliveryOptionsProperty"], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::PinpointEmail::ConfigurationSet.DeliveryOptions``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpointemail-configurationset.html#cfn-pinpointemail-configurationset-deliveryoptions
        """
        return jsii.get(self, "deliveryOptions")

    @delivery_options.setter
    def delivery_options(self, value: typing.Optional[typing.Union[typing.Optional["DeliveryOptionsProperty"], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "deliveryOptions", value)

    @property
    @jsii.member(jsii_name="reputationOptions")
    def reputation_options(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["ReputationOptionsProperty"]]]:
        """``AWS::PinpointEmail::ConfigurationSet.ReputationOptions``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpointemail-configurationset.html#cfn-pinpointemail-configurationset-reputationoptions
        """
        return jsii.get(self, "reputationOptions")

    @reputation_options.setter
    def reputation_options(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["ReputationOptionsProperty"]]]):
        return jsii.set(self, "reputationOptions", value)

    @property
    @jsii.member(jsii_name="sendingOptions")
    def sending_options(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["SendingOptionsProperty"]]]:
        """``AWS::PinpointEmail::ConfigurationSet.SendingOptions``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpointemail-configurationset.html#cfn-pinpointemail-configurationset-sendingoptions
        """
        return jsii.get(self, "sendingOptions")

    @sending_options.setter
    def sending_options(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["SendingOptionsProperty"]]]):
        return jsii.set(self, "sendingOptions", value)

    @property
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.Optional[typing.List["TagsProperty"]]:
        """``AWS::PinpointEmail::ConfigurationSet.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpointemail-configurationset.html#cfn-pinpointemail-configurationset-tags
        """
        return jsii.get(self, "tags")

    @tags.setter
    def tags(self, value: typing.Optional[typing.List["TagsProperty"]]):
        return jsii.set(self, "tags", value)

    @property
    @jsii.member(jsii_name="trackingOptions")
    def tracking_options(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["TrackingOptionsProperty"]]]:
        """``AWS::PinpointEmail::ConfigurationSet.TrackingOptions``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpointemail-configurationset.html#cfn-pinpointemail-configurationset-trackingoptions
        """
        return jsii.get(self, "trackingOptions")

    @tracking_options.setter
    def tracking_options(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["TrackingOptionsProperty"]]]):
        return jsii.set(self, "trackingOptions", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-pinpointemail.CfnConfigurationSet.DeliveryOptionsProperty", jsii_struct_bases=[], name_mapping={'sending_pool_name': 'sendingPoolName'})
    class DeliveryOptionsProperty():
        def __init__(self, *, sending_pool_name: typing.Optional[str]=None):
            """
            :param sending_pool_name: ``CfnConfigurationSet.DeliveryOptionsProperty.SendingPoolName``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpointemail-configurationset-deliveryoptions.html
            """
            self._values = {
            }
            if sending_pool_name is not None: self._values["sending_pool_name"] = sending_pool_name

        @property
        def sending_pool_name(self) -> typing.Optional[str]:
            """``CfnConfigurationSet.DeliveryOptionsProperty.SendingPoolName``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpointemail-configurationset-deliveryoptions.html#cfn-pinpointemail-configurationset-deliveryoptions-sendingpoolname
            """
            return self._values.get('sending_pool_name')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'DeliveryOptionsProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-pinpointemail.CfnConfigurationSet.ReputationOptionsProperty", jsii_struct_bases=[], name_mapping={'reputation_metrics_enabled': 'reputationMetricsEnabled'})
    class ReputationOptionsProperty():
        def __init__(self, *, reputation_metrics_enabled: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None):
            """
            :param reputation_metrics_enabled: ``CfnConfigurationSet.ReputationOptionsProperty.ReputationMetricsEnabled``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpointemail-configurationset-reputationoptions.html
            """
            self._values = {
            }
            if reputation_metrics_enabled is not None: self._values["reputation_metrics_enabled"] = reputation_metrics_enabled

        @property
        def reputation_metrics_enabled(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
            """``CfnConfigurationSet.ReputationOptionsProperty.ReputationMetricsEnabled``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpointemail-configurationset-reputationoptions.html#cfn-pinpointemail-configurationset-reputationoptions-reputationmetricsenabled
            """
            return self._values.get('reputation_metrics_enabled')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'ReputationOptionsProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-pinpointemail.CfnConfigurationSet.SendingOptionsProperty", jsii_struct_bases=[], name_mapping={'sending_enabled': 'sendingEnabled'})
    class SendingOptionsProperty():
        def __init__(self, *, sending_enabled: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None):
            """
            :param sending_enabled: ``CfnConfigurationSet.SendingOptionsProperty.SendingEnabled``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpointemail-configurationset-sendingoptions.html
            """
            self._values = {
            }
            if sending_enabled is not None: self._values["sending_enabled"] = sending_enabled

        @property
        def sending_enabled(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
            """``CfnConfigurationSet.SendingOptionsProperty.SendingEnabled``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpointemail-configurationset-sendingoptions.html#cfn-pinpointemail-configurationset-sendingoptions-sendingenabled
            """
            return self._values.get('sending_enabled')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'SendingOptionsProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-pinpointemail.CfnConfigurationSet.TagsProperty", jsii_struct_bases=[], name_mapping={'key': 'key', 'value': 'value'})
    class TagsProperty():
        def __init__(self, *, key: typing.Optional[str]=None, value: typing.Optional[str]=None):
            """
            :param key: ``CfnConfigurationSet.TagsProperty.Key``.
            :param value: ``CfnConfigurationSet.TagsProperty.Value``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpointemail-configurationset-tags.html
            """
            self._values = {
            }
            if key is not None: self._values["key"] = key
            if value is not None: self._values["value"] = value

        @property
        def key(self) -> typing.Optional[str]:
            """``CfnConfigurationSet.TagsProperty.Key``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpointemail-configurationset-tags.html#cfn-pinpointemail-configurationset-tags-key
            """
            return self._values.get('key')

        @property
        def value(self) -> typing.Optional[str]:
            """``CfnConfigurationSet.TagsProperty.Value``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpointemail-configurationset-tags.html#cfn-pinpointemail-configurationset-tags-value
            """
            return self._values.get('value')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'TagsProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-pinpointemail.CfnConfigurationSet.TrackingOptionsProperty", jsii_struct_bases=[], name_mapping={'custom_redirect_domain': 'customRedirectDomain'})
    class TrackingOptionsProperty():
        def __init__(self, *, custom_redirect_domain: typing.Optional[str]=None):
            """
            :param custom_redirect_domain: ``CfnConfigurationSet.TrackingOptionsProperty.CustomRedirectDomain``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpointemail-configurationset-trackingoptions.html
            """
            self._values = {
            }
            if custom_redirect_domain is not None: self._values["custom_redirect_domain"] = custom_redirect_domain

        @property
        def custom_redirect_domain(self) -> typing.Optional[str]:
            """``CfnConfigurationSet.TrackingOptionsProperty.CustomRedirectDomain``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpointemail-configurationset-trackingoptions.html#cfn-pinpointemail-configurationset-trackingoptions-customredirectdomain
            """
            return self._values.get('custom_redirect_domain')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'TrackingOptionsProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



class CfnConfigurationSetEventDestination(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-pinpointemail.CfnConfigurationSetEventDestination"):
    """A CloudFormation ``AWS::PinpointEmail::ConfigurationSetEventDestination``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpointemail-configurationseteventdestination.html
    cloudformationResource:
    :cloudformationResource:: AWS::PinpointEmail::ConfigurationSetEventDestination
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, configuration_set_name: str, event_destination_name: str, event_destination: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["EventDestinationProperty"]]]=None) -> None:
        """Create a new ``AWS::PinpointEmail::ConfigurationSetEventDestination``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param configuration_set_name: ``AWS::PinpointEmail::ConfigurationSetEventDestination.ConfigurationSetName``.
        :param event_destination_name: ``AWS::PinpointEmail::ConfigurationSetEventDestination.EventDestinationName``.
        :param event_destination: ``AWS::PinpointEmail::ConfigurationSetEventDestination.EventDestination``.
        """
        props = CfnConfigurationSetEventDestinationProps(configuration_set_name=configuration_set_name, event_destination_name=event_destination_name, event_destination=event_destination)

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
        """``AWS::PinpointEmail::ConfigurationSetEventDestination.ConfigurationSetName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpointemail-configurationseteventdestination.html#cfn-pinpointemail-configurationseteventdestination-configurationsetname
        """
        return jsii.get(self, "configurationSetName")

    @configuration_set_name.setter
    def configuration_set_name(self, value: str):
        return jsii.set(self, "configurationSetName", value)

    @property
    @jsii.member(jsii_name="eventDestinationName")
    def event_destination_name(self) -> str:
        """``AWS::PinpointEmail::ConfigurationSetEventDestination.EventDestinationName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpointemail-configurationseteventdestination.html#cfn-pinpointemail-configurationseteventdestination-eventdestinationname
        """
        return jsii.get(self, "eventDestinationName")

    @event_destination_name.setter
    def event_destination_name(self, value: str):
        return jsii.set(self, "eventDestinationName", value)

    @property
    @jsii.member(jsii_name="eventDestination")
    def event_destination(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["EventDestinationProperty"]]]:
        """``AWS::PinpointEmail::ConfigurationSetEventDestination.EventDestination``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpointemail-configurationseteventdestination.html#cfn-pinpointemail-configurationseteventdestination-eventdestination
        """
        return jsii.get(self, "eventDestination")

    @event_destination.setter
    def event_destination(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["EventDestinationProperty"]]]):
        return jsii.set(self, "eventDestination", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-pinpointemail.CfnConfigurationSetEventDestination.CloudWatchDestinationProperty", jsii_struct_bases=[], name_mapping={'dimension_configurations': 'dimensionConfigurations'})
    class CloudWatchDestinationProperty():
        def __init__(self, *, dimension_configurations: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnConfigurationSetEventDestination.DimensionConfigurationProperty"]]]]]=None):
            """
            :param dimension_configurations: ``CfnConfigurationSetEventDestination.CloudWatchDestinationProperty.DimensionConfigurations``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpointemail-configurationseteventdestination-cloudwatchdestination.html
            """
            self._values = {
            }
            if dimension_configurations is not None: self._values["dimension_configurations"] = dimension_configurations

        @property
        def dimension_configurations(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnConfigurationSetEventDestination.DimensionConfigurationProperty"]]]]]:
            """``CfnConfigurationSetEventDestination.CloudWatchDestinationProperty.DimensionConfigurations``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpointemail-configurationseteventdestination-cloudwatchdestination.html#cfn-pinpointemail-configurationseteventdestination-cloudwatchdestination-dimensionconfigurations
            """
            return self._values.get('dimension_configurations')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'CloudWatchDestinationProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-pinpointemail.CfnConfigurationSetEventDestination.DimensionConfigurationProperty", jsii_struct_bases=[], name_mapping={'default_dimension_value': 'defaultDimensionValue', 'dimension_name': 'dimensionName', 'dimension_value_source': 'dimensionValueSource'})
    class DimensionConfigurationProperty():
        def __init__(self, *, default_dimension_value: str, dimension_name: str, dimension_value_source: str):
            """
            :param default_dimension_value: ``CfnConfigurationSetEventDestination.DimensionConfigurationProperty.DefaultDimensionValue``.
            :param dimension_name: ``CfnConfigurationSetEventDestination.DimensionConfigurationProperty.DimensionName``.
            :param dimension_value_source: ``CfnConfigurationSetEventDestination.DimensionConfigurationProperty.DimensionValueSource``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpointemail-configurationseteventdestination-dimensionconfiguration.html
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
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpointemail-configurationseteventdestination-dimensionconfiguration.html#cfn-pinpointemail-configurationseteventdestination-dimensionconfiguration-defaultdimensionvalue
            """
            return self._values.get('default_dimension_value')

        @property
        def dimension_name(self) -> str:
            """``CfnConfigurationSetEventDestination.DimensionConfigurationProperty.DimensionName``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpointemail-configurationseteventdestination-dimensionconfiguration.html#cfn-pinpointemail-configurationseteventdestination-dimensionconfiguration-dimensionname
            """
            return self._values.get('dimension_name')

        @property
        def dimension_value_source(self) -> str:
            """``CfnConfigurationSetEventDestination.DimensionConfigurationProperty.DimensionValueSource``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpointemail-configurationseteventdestination-dimensionconfiguration.html#cfn-pinpointemail-configurationseteventdestination-dimensionconfiguration-dimensionvaluesource
            """
            return self._values.get('dimension_value_source')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'DimensionConfigurationProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-pinpointemail.CfnConfigurationSetEventDestination.EventDestinationProperty", jsii_struct_bases=[], name_mapping={'matching_event_types': 'matchingEventTypes', 'cloud_watch_destination': 'cloudWatchDestination', 'enabled': 'enabled', 'kinesis_firehose_destination': 'kinesisFirehoseDestination', 'pinpoint_destination': 'pinpointDestination', 'sns_destination': 'snsDestination'})
    class EventDestinationProperty():
        def __init__(self, *, matching_event_types: typing.List[str], cloud_watch_destination: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnConfigurationSetEventDestination.CloudWatchDestinationProperty"]]]=None, enabled: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, kinesis_firehose_destination: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnConfigurationSetEventDestination.KinesisFirehoseDestinationProperty"]]]=None, pinpoint_destination: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnConfigurationSetEventDestination.PinpointDestinationProperty"]]]=None, sns_destination: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnConfigurationSetEventDestination.SnsDestinationProperty"]]]=None):
            """
            :param matching_event_types: ``CfnConfigurationSetEventDestination.EventDestinationProperty.MatchingEventTypes``.
            :param cloud_watch_destination: ``CfnConfigurationSetEventDestination.EventDestinationProperty.CloudWatchDestination``.
            :param enabled: ``CfnConfigurationSetEventDestination.EventDestinationProperty.Enabled``.
            :param kinesis_firehose_destination: ``CfnConfigurationSetEventDestination.EventDestinationProperty.KinesisFirehoseDestination``.
            :param pinpoint_destination: ``CfnConfigurationSetEventDestination.EventDestinationProperty.PinpointDestination``.
            :param sns_destination: ``CfnConfigurationSetEventDestination.EventDestinationProperty.SnsDestination``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpointemail-configurationseteventdestination-eventdestination.html
            """
            self._values = {
                'matching_event_types': matching_event_types,
            }
            if cloud_watch_destination is not None: self._values["cloud_watch_destination"] = cloud_watch_destination
            if enabled is not None: self._values["enabled"] = enabled
            if kinesis_firehose_destination is not None: self._values["kinesis_firehose_destination"] = kinesis_firehose_destination
            if pinpoint_destination is not None: self._values["pinpoint_destination"] = pinpoint_destination
            if sns_destination is not None: self._values["sns_destination"] = sns_destination

        @property
        def matching_event_types(self) -> typing.List[str]:
            """``CfnConfigurationSetEventDestination.EventDestinationProperty.MatchingEventTypes``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpointemail-configurationseteventdestination-eventdestination.html#cfn-pinpointemail-configurationseteventdestination-eventdestination-matchingeventtypes
            """
            return self._values.get('matching_event_types')

        @property
        def cloud_watch_destination(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnConfigurationSetEventDestination.CloudWatchDestinationProperty"]]]:
            """``CfnConfigurationSetEventDestination.EventDestinationProperty.CloudWatchDestination``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpointemail-configurationseteventdestination-eventdestination.html#cfn-pinpointemail-configurationseteventdestination-eventdestination-cloudwatchdestination
            """
            return self._values.get('cloud_watch_destination')

        @property
        def enabled(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
            """``CfnConfigurationSetEventDestination.EventDestinationProperty.Enabled``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpointemail-configurationseteventdestination-eventdestination.html#cfn-pinpointemail-configurationseteventdestination-eventdestination-enabled
            """
            return self._values.get('enabled')

        @property
        def kinesis_firehose_destination(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnConfigurationSetEventDestination.KinesisFirehoseDestinationProperty"]]]:
            """``CfnConfigurationSetEventDestination.EventDestinationProperty.KinesisFirehoseDestination``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpointemail-configurationseteventdestination-eventdestination.html#cfn-pinpointemail-configurationseteventdestination-eventdestination-kinesisfirehosedestination
            """
            return self._values.get('kinesis_firehose_destination')

        @property
        def pinpoint_destination(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnConfigurationSetEventDestination.PinpointDestinationProperty"]]]:
            """``CfnConfigurationSetEventDestination.EventDestinationProperty.PinpointDestination``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpointemail-configurationseteventdestination-eventdestination.html#cfn-pinpointemail-configurationseteventdestination-eventdestination-pinpointdestination
            """
            return self._values.get('pinpoint_destination')

        @property
        def sns_destination(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnConfigurationSetEventDestination.SnsDestinationProperty"]]]:
            """``CfnConfigurationSetEventDestination.EventDestinationProperty.SnsDestination``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpointemail-configurationseteventdestination-eventdestination.html#cfn-pinpointemail-configurationseteventdestination-eventdestination-snsdestination
            """
            return self._values.get('sns_destination')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'EventDestinationProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-pinpointemail.CfnConfigurationSetEventDestination.KinesisFirehoseDestinationProperty", jsii_struct_bases=[], name_mapping={'delivery_stream_arn': 'deliveryStreamArn', 'iam_role_arn': 'iamRoleArn'})
    class KinesisFirehoseDestinationProperty():
        def __init__(self, *, delivery_stream_arn: str, iam_role_arn: str):
            """
            :param delivery_stream_arn: ``CfnConfigurationSetEventDestination.KinesisFirehoseDestinationProperty.DeliveryStreamArn``.
            :param iam_role_arn: ``CfnConfigurationSetEventDestination.KinesisFirehoseDestinationProperty.IamRoleArn``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpointemail-configurationseteventdestination-kinesisfirehosedestination.html
            """
            self._values = {
                'delivery_stream_arn': delivery_stream_arn,
                'iam_role_arn': iam_role_arn,
            }

        @property
        def delivery_stream_arn(self) -> str:
            """``CfnConfigurationSetEventDestination.KinesisFirehoseDestinationProperty.DeliveryStreamArn``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpointemail-configurationseteventdestination-kinesisfirehosedestination.html#cfn-pinpointemail-configurationseteventdestination-kinesisfirehosedestination-deliverystreamarn
            """
            return self._values.get('delivery_stream_arn')

        @property
        def iam_role_arn(self) -> str:
            """``CfnConfigurationSetEventDestination.KinesisFirehoseDestinationProperty.IamRoleArn``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpointemail-configurationseteventdestination-kinesisfirehosedestination.html#cfn-pinpointemail-configurationseteventdestination-kinesisfirehosedestination-iamrolearn
            """
            return self._values.get('iam_role_arn')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'KinesisFirehoseDestinationProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-pinpointemail.CfnConfigurationSetEventDestination.PinpointDestinationProperty", jsii_struct_bases=[], name_mapping={'application_arn': 'applicationArn'})
    class PinpointDestinationProperty():
        def __init__(self, *, application_arn: typing.Optional[str]=None):
            """
            :param application_arn: ``CfnConfigurationSetEventDestination.PinpointDestinationProperty.ApplicationArn``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpointemail-configurationseteventdestination-pinpointdestination.html
            """
            self._values = {
            }
            if application_arn is not None: self._values["application_arn"] = application_arn

        @property
        def application_arn(self) -> typing.Optional[str]:
            """``CfnConfigurationSetEventDestination.PinpointDestinationProperty.ApplicationArn``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpointemail-configurationseteventdestination-pinpointdestination.html#cfn-pinpointemail-configurationseteventdestination-pinpointdestination-applicationarn
            """
            return self._values.get('application_arn')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'PinpointDestinationProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-pinpointemail.CfnConfigurationSetEventDestination.SnsDestinationProperty", jsii_struct_bases=[], name_mapping={'topic_arn': 'topicArn'})
    class SnsDestinationProperty():
        def __init__(self, *, topic_arn: str):
            """
            :param topic_arn: ``CfnConfigurationSetEventDestination.SnsDestinationProperty.TopicArn``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpointemail-configurationseteventdestination-snsdestination.html
            """
            self._values = {
                'topic_arn': topic_arn,
            }

        @property
        def topic_arn(self) -> str:
            """``CfnConfigurationSetEventDestination.SnsDestinationProperty.TopicArn``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpointemail-configurationseteventdestination-snsdestination.html#cfn-pinpointemail-configurationseteventdestination-snsdestination-topicarn
            """
            return self._values.get('topic_arn')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'SnsDestinationProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



@jsii.data_type(jsii_type="@aws-cdk/aws-pinpointemail.CfnConfigurationSetEventDestinationProps", jsii_struct_bases=[], name_mapping={'configuration_set_name': 'configurationSetName', 'event_destination_name': 'eventDestinationName', 'event_destination': 'eventDestination'})
class CfnConfigurationSetEventDestinationProps():
    def __init__(self, *, configuration_set_name: str, event_destination_name: str, event_destination: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnConfigurationSetEventDestination.EventDestinationProperty"]]]=None):
        """Properties for defining a ``AWS::PinpointEmail::ConfigurationSetEventDestination``.

        :param configuration_set_name: ``AWS::PinpointEmail::ConfigurationSetEventDestination.ConfigurationSetName``.
        :param event_destination_name: ``AWS::PinpointEmail::ConfigurationSetEventDestination.EventDestinationName``.
        :param event_destination: ``AWS::PinpointEmail::ConfigurationSetEventDestination.EventDestination``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpointemail-configurationseteventdestination.html
        """
        self._values = {
            'configuration_set_name': configuration_set_name,
            'event_destination_name': event_destination_name,
        }
        if event_destination is not None: self._values["event_destination"] = event_destination

    @property
    def configuration_set_name(self) -> str:
        """``AWS::PinpointEmail::ConfigurationSetEventDestination.ConfigurationSetName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpointemail-configurationseteventdestination.html#cfn-pinpointemail-configurationseteventdestination-configurationsetname
        """
        return self._values.get('configuration_set_name')

    @property
    def event_destination_name(self) -> str:
        """``AWS::PinpointEmail::ConfigurationSetEventDestination.EventDestinationName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpointemail-configurationseteventdestination.html#cfn-pinpointemail-configurationseteventdestination-eventdestinationname
        """
        return self._values.get('event_destination_name')

    @property
    def event_destination(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnConfigurationSetEventDestination.EventDestinationProperty"]]]:
        """``AWS::PinpointEmail::ConfigurationSetEventDestination.EventDestination``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpointemail-configurationseteventdestination.html#cfn-pinpointemail-configurationseteventdestination-eventdestination
        """
        return self._values.get('event_destination')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnConfigurationSetEventDestinationProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


@jsii.data_type(jsii_type="@aws-cdk/aws-pinpointemail.CfnConfigurationSetProps", jsii_struct_bases=[], name_mapping={'name': 'name', 'delivery_options': 'deliveryOptions', 'reputation_options': 'reputationOptions', 'sending_options': 'sendingOptions', 'tags': 'tags', 'tracking_options': 'trackingOptions'})
class CfnConfigurationSetProps():
    def __init__(self, *, name: str, delivery_options: typing.Optional[typing.Union[typing.Optional["CfnConfigurationSet.DeliveryOptionsProperty"], typing.Optional[aws_cdk.core.IResolvable]]]=None, reputation_options: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnConfigurationSet.ReputationOptionsProperty"]]]=None, sending_options: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnConfigurationSet.SendingOptionsProperty"]]]=None, tags: typing.Optional[typing.List["CfnConfigurationSet.TagsProperty"]]=None, tracking_options: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnConfigurationSet.TrackingOptionsProperty"]]]=None):
        """Properties for defining a ``AWS::PinpointEmail::ConfigurationSet``.

        :param name: ``AWS::PinpointEmail::ConfigurationSet.Name``.
        :param delivery_options: ``AWS::PinpointEmail::ConfigurationSet.DeliveryOptions``.
        :param reputation_options: ``AWS::PinpointEmail::ConfigurationSet.ReputationOptions``.
        :param sending_options: ``AWS::PinpointEmail::ConfigurationSet.SendingOptions``.
        :param tags: ``AWS::PinpointEmail::ConfigurationSet.Tags``.
        :param tracking_options: ``AWS::PinpointEmail::ConfigurationSet.TrackingOptions``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpointemail-configurationset.html
        """
        self._values = {
            'name': name,
        }
        if delivery_options is not None: self._values["delivery_options"] = delivery_options
        if reputation_options is not None: self._values["reputation_options"] = reputation_options
        if sending_options is not None: self._values["sending_options"] = sending_options
        if tags is not None: self._values["tags"] = tags
        if tracking_options is not None: self._values["tracking_options"] = tracking_options

    @property
    def name(self) -> str:
        """``AWS::PinpointEmail::ConfigurationSet.Name``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpointemail-configurationset.html#cfn-pinpointemail-configurationset-name
        """
        return self._values.get('name')

    @property
    def delivery_options(self) -> typing.Optional[typing.Union[typing.Optional["CfnConfigurationSet.DeliveryOptionsProperty"], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::PinpointEmail::ConfigurationSet.DeliveryOptions``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpointemail-configurationset.html#cfn-pinpointemail-configurationset-deliveryoptions
        """
        return self._values.get('delivery_options')

    @property
    def reputation_options(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnConfigurationSet.ReputationOptionsProperty"]]]:
        """``AWS::PinpointEmail::ConfigurationSet.ReputationOptions``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpointemail-configurationset.html#cfn-pinpointemail-configurationset-reputationoptions
        """
        return self._values.get('reputation_options')

    @property
    def sending_options(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnConfigurationSet.SendingOptionsProperty"]]]:
        """``AWS::PinpointEmail::ConfigurationSet.SendingOptions``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpointemail-configurationset.html#cfn-pinpointemail-configurationset-sendingoptions
        """
        return self._values.get('sending_options')

    @property
    def tags(self) -> typing.Optional[typing.List["CfnConfigurationSet.TagsProperty"]]:
        """``AWS::PinpointEmail::ConfigurationSet.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpointemail-configurationset.html#cfn-pinpointemail-configurationset-tags
        """
        return self._values.get('tags')

    @property
    def tracking_options(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnConfigurationSet.TrackingOptionsProperty"]]]:
        """``AWS::PinpointEmail::ConfigurationSet.TrackingOptions``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpointemail-configurationset.html#cfn-pinpointemail-configurationset-trackingoptions
        """
        return self._values.get('tracking_options')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnConfigurationSetProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnDedicatedIpPool(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-pinpointemail.CfnDedicatedIpPool"):
    """A CloudFormation ``AWS::PinpointEmail::DedicatedIpPool``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpointemail-dedicatedippool.html
    cloudformationResource:
    :cloudformationResource:: AWS::PinpointEmail::DedicatedIpPool
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, pool_name: typing.Optional[str]=None, tags: typing.Optional[typing.List["TagsProperty"]]=None) -> None:
        """Create a new ``AWS::PinpointEmail::DedicatedIpPool``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param pool_name: ``AWS::PinpointEmail::DedicatedIpPool.PoolName``.
        :param tags: ``AWS::PinpointEmail::DedicatedIpPool.Tags``.
        """
        props = CfnDedicatedIpPoolProps(pool_name=pool_name, tags=tags)

        jsii.create(CfnDedicatedIpPool, self, [scope, id, props])

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
    @jsii.member(jsii_name="poolName")
    def pool_name(self) -> typing.Optional[str]:
        """``AWS::PinpointEmail::DedicatedIpPool.PoolName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpointemail-dedicatedippool.html#cfn-pinpointemail-dedicatedippool-poolname
        """
        return jsii.get(self, "poolName")

    @pool_name.setter
    def pool_name(self, value: typing.Optional[str]):
        return jsii.set(self, "poolName", value)

    @property
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.Optional[typing.List["TagsProperty"]]:
        """``AWS::PinpointEmail::DedicatedIpPool.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpointemail-dedicatedippool.html#cfn-pinpointemail-dedicatedippool-tags
        """
        return jsii.get(self, "tags")

    @tags.setter
    def tags(self, value: typing.Optional[typing.List["TagsProperty"]]):
        return jsii.set(self, "tags", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-pinpointemail.CfnDedicatedIpPool.TagsProperty", jsii_struct_bases=[], name_mapping={'key': 'key', 'value': 'value'})
    class TagsProperty():
        def __init__(self, *, key: typing.Optional[str]=None, value: typing.Optional[str]=None):
            """
            :param key: ``CfnDedicatedIpPool.TagsProperty.Key``.
            :param value: ``CfnDedicatedIpPool.TagsProperty.Value``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpointemail-dedicatedippool-tags.html
            """
            self._values = {
            }
            if key is not None: self._values["key"] = key
            if value is not None: self._values["value"] = value

        @property
        def key(self) -> typing.Optional[str]:
            """``CfnDedicatedIpPool.TagsProperty.Key``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpointemail-dedicatedippool-tags.html#cfn-pinpointemail-dedicatedippool-tags-key
            """
            return self._values.get('key')

        @property
        def value(self) -> typing.Optional[str]:
            """``CfnDedicatedIpPool.TagsProperty.Value``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpointemail-dedicatedippool-tags.html#cfn-pinpointemail-dedicatedippool-tags-value
            """
            return self._values.get('value')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'TagsProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



@jsii.data_type(jsii_type="@aws-cdk/aws-pinpointemail.CfnDedicatedIpPoolProps", jsii_struct_bases=[], name_mapping={'pool_name': 'poolName', 'tags': 'tags'})
class CfnDedicatedIpPoolProps():
    def __init__(self, *, pool_name: typing.Optional[str]=None, tags: typing.Optional[typing.List["CfnDedicatedIpPool.TagsProperty"]]=None):
        """Properties for defining a ``AWS::PinpointEmail::DedicatedIpPool``.

        :param pool_name: ``AWS::PinpointEmail::DedicatedIpPool.PoolName``.
        :param tags: ``AWS::PinpointEmail::DedicatedIpPool.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpointemail-dedicatedippool.html
        """
        self._values = {
        }
        if pool_name is not None: self._values["pool_name"] = pool_name
        if tags is not None: self._values["tags"] = tags

    @property
    def pool_name(self) -> typing.Optional[str]:
        """``AWS::PinpointEmail::DedicatedIpPool.PoolName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpointemail-dedicatedippool.html#cfn-pinpointemail-dedicatedippool-poolname
        """
        return self._values.get('pool_name')

    @property
    def tags(self) -> typing.Optional[typing.List["CfnDedicatedIpPool.TagsProperty"]]:
        """``AWS::PinpointEmail::DedicatedIpPool.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpointemail-dedicatedippool.html#cfn-pinpointemail-dedicatedippool-tags
        """
        return self._values.get('tags')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnDedicatedIpPoolProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnIdentity(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-pinpointemail.CfnIdentity"):
    """A CloudFormation ``AWS::PinpointEmail::Identity``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpointemail-identity.html
    cloudformationResource:
    :cloudformationResource:: AWS::PinpointEmail::Identity
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, name: str, dkim_signing_enabled: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, feedback_forwarding_enabled: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, mail_from_attributes: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["MailFromAttributesProperty"]]]=None, tags: typing.Optional[typing.List["TagsProperty"]]=None) -> None:
        """Create a new ``AWS::PinpointEmail::Identity``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param name: ``AWS::PinpointEmail::Identity.Name``.
        :param dkim_signing_enabled: ``AWS::PinpointEmail::Identity.DkimSigningEnabled``.
        :param feedback_forwarding_enabled: ``AWS::PinpointEmail::Identity.FeedbackForwardingEnabled``.
        :param mail_from_attributes: ``AWS::PinpointEmail::Identity.MailFromAttributes``.
        :param tags: ``AWS::PinpointEmail::Identity.Tags``.
        """
        props = CfnIdentityProps(name=name, dkim_signing_enabled=dkim_signing_enabled, feedback_forwarding_enabled=feedback_forwarding_enabled, mail_from_attributes=mail_from_attributes, tags=tags)

        jsii.create(CfnIdentity, self, [scope, id, props])

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
    @jsii.member(jsii_name="attrIdentityDnsRecordName1")
    def attr_identity_dns_record_name1(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: IdentityDNSRecordName1
        """
        return jsii.get(self, "attrIdentityDnsRecordName1")

    @property
    @jsii.member(jsii_name="attrIdentityDnsRecordName2")
    def attr_identity_dns_record_name2(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: IdentityDNSRecordName2
        """
        return jsii.get(self, "attrIdentityDnsRecordName2")

    @property
    @jsii.member(jsii_name="attrIdentityDnsRecordName3")
    def attr_identity_dns_record_name3(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: IdentityDNSRecordName3
        """
        return jsii.get(self, "attrIdentityDnsRecordName3")

    @property
    @jsii.member(jsii_name="attrIdentityDnsRecordValue1")
    def attr_identity_dns_record_value1(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: IdentityDNSRecordValue1
        """
        return jsii.get(self, "attrIdentityDnsRecordValue1")

    @property
    @jsii.member(jsii_name="attrIdentityDnsRecordValue2")
    def attr_identity_dns_record_value2(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: IdentityDNSRecordValue2
        """
        return jsii.get(self, "attrIdentityDnsRecordValue2")

    @property
    @jsii.member(jsii_name="attrIdentityDnsRecordValue3")
    def attr_identity_dns_record_value3(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: IdentityDNSRecordValue3
        """
        return jsii.get(self, "attrIdentityDnsRecordValue3")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> str:
        """``AWS::PinpointEmail::Identity.Name``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpointemail-identity.html#cfn-pinpointemail-identity-name
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: str):
        return jsii.set(self, "name", value)

    @property
    @jsii.member(jsii_name="dkimSigningEnabled")
    def dkim_signing_enabled(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::PinpointEmail::Identity.DkimSigningEnabled``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpointemail-identity.html#cfn-pinpointemail-identity-dkimsigningenabled
        """
        return jsii.get(self, "dkimSigningEnabled")

    @dkim_signing_enabled.setter
    def dkim_signing_enabled(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "dkimSigningEnabled", value)

    @property
    @jsii.member(jsii_name="feedbackForwardingEnabled")
    def feedback_forwarding_enabled(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::PinpointEmail::Identity.FeedbackForwardingEnabled``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpointemail-identity.html#cfn-pinpointemail-identity-feedbackforwardingenabled
        """
        return jsii.get(self, "feedbackForwardingEnabled")

    @feedback_forwarding_enabled.setter
    def feedback_forwarding_enabled(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "feedbackForwardingEnabled", value)

    @property
    @jsii.member(jsii_name="mailFromAttributes")
    def mail_from_attributes(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["MailFromAttributesProperty"]]]:
        """``AWS::PinpointEmail::Identity.MailFromAttributes``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpointemail-identity.html#cfn-pinpointemail-identity-mailfromattributes
        """
        return jsii.get(self, "mailFromAttributes")

    @mail_from_attributes.setter
    def mail_from_attributes(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["MailFromAttributesProperty"]]]):
        return jsii.set(self, "mailFromAttributes", value)

    @property
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.Optional[typing.List["TagsProperty"]]:
        """``AWS::PinpointEmail::Identity.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpointemail-identity.html#cfn-pinpointemail-identity-tags
        """
        return jsii.get(self, "tags")

    @tags.setter
    def tags(self, value: typing.Optional[typing.List["TagsProperty"]]):
        return jsii.set(self, "tags", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-pinpointemail.CfnIdentity.MailFromAttributesProperty", jsii_struct_bases=[], name_mapping={'behavior_on_mx_failure': 'behaviorOnMxFailure', 'mail_from_domain': 'mailFromDomain'})
    class MailFromAttributesProperty():
        def __init__(self, *, behavior_on_mx_failure: typing.Optional[str]=None, mail_from_domain: typing.Optional[str]=None):
            """
            :param behavior_on_mx_failure: ``CfnIdentity.MailFromAttributesProperty.BehaviorOnMxFailure``.
            :param mail_from_domain: ``CfnIdentity.MailFromAttributesProperty.MailFromDomain``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpointemail-identity-mailfromattributes.html
            """
            self._values = {
            }
            if behavior_on_mx_failure is not None: self._values["behavior_on_mx_failure"] = behavior_on_mx_failure
            if mail_from_domain is not None: self._values["mail_from_domain"] = mail_from_domain

        @property
        def behavior_on_mx_failure(self) -> typing.Optional[str]:
            """``CfnIdentity.MailFromAttributesProperty.BehaviorOnMxFailure``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpointemail-identity-mailfromattributes.html#cfn-pinpointemail-identity-mailfromattributes-behavioronmxfailure
            """
            return self._values.get('behavior_on_mx_failure')

        @property
        def mail_from_domain(self) -> typing.Optional[str]:
            """``CfnIdentity.MailFromAttributesProperty.MailFromDomain``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpointemail-identity-mailfromattributes.html#cfn-pinpointemail-identity-mailfromattributes-mailfromdomain
            """
            return self._values.get('mail_from_domain')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'MailFromAttributesProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-pinpointemail.CfnIdentity.TagsProperty", jsii_struct_bases=[], name_mapping={'key': 'key', 'value': 'value'})
    class TagsProperty():
        def __init__(self, *, key: typing.Optional[str]=None, value: typing.Optional[str]=None):
            """
            :param key: ``CfnIdentity.TagsProperty.Key``.
            :param value: ``CfnIdentity.TagsProperty.Value``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpointemail-identity-tags.html
            """
            self._values = {
            }
            if key is not None: self._values["key"] = key
            if value is not None: self._values["value"] = value

        @property
        def key(self) -> typing.Optional[str]:
            """``CfnIdentity.TagsProperty.Key``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpointemail-identity-tags.html#cfn-pinpointemail-identity-tags-key
            """
            return self._values.get('key')

        @property
        def value(self) -> typing.Optional[str]:
            """``CfnIdentity.TagsProperty.Value``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpointemail-identity-tags.html#cfn-pinpointemail-identity-tags-value
            """
            return self._values.get('value')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'TagsProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



@jsii.data_type(jsii_type="@aws-cdk/aws-pinpointemail.CfnIdentityProps", jsii_struct_bases=[], name_mapping={'name': 'name', 'dkim_signing_enabled': 'dkimSigningEnabled', 'feedback_forwarding_enabled': 'feedbackForwardingEnabled', 'mail_from_attributes': 'mailFromAttributes', 'tags': 'tags'})
class CfnIdentityProps():
    def __init__(self, *, name: str, dkim_signing_enabled: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, feedback_forwarding_enabled: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, mail_from_attributes: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnIdentity.MailFromAttributesProperty"]]]=None, tags: typing.Optional[typing.List["CfnIdentity.TagsProperty"]]=None):
        """Properties for defining a ``AWS::PinpointEmail::Identity``.

        :param name: ``AWS::PinpointEmail::Identity.Name``.
        :param dkim_signing_enabled: ``AWS::PinpointEmail::Identity.DkimSigningEnabled``.
        :param feedback_forwarding_enabled: ``AWS::PinpointEmail::Identity.FeedbackForwardingEnabled``.
        :param mail_from_attributes: ``AWS::PinpointEmail::Identity.MailFromAttributes``.
        :param tags: ``AWS::PinpointEmail::Identity.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpointemail-identity.html
        """
        self._values = {
            'name': name,
        }
        if dkim_signing_enabled is not None: self._values["dkim_signing_enabled"] = dkim_signing_enabled
        if feedback_forwarding_enabled is not None: self._values["feedback_forwarding_enabled"] = feedback_forwarding_enabled
        if mail_from_attributes is not None: self._values["mail_from_attributes"] = mail_from_attributes
        if tags is not None: self._values["tags"] = tags

    @property
    def name(self) -> str:
        """``AWS::PinpointEmail::Identity.Name``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpointemail-identity.html#cfn-pinpointemail-identity-name
        """
        return self._values.get('name')

    @property
    def dkim_signing_enabled(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::PinpointEmail::Identity.DkimSigningEnabled``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpointemail-identity.html#cfn-pinpointemail-identity-dkimsigningenabled
        """
        return self._values.get('dkim_signing_enabled')

    @property
    def feedback_forwarding_enabled(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::PinpointEmail::Identity.FeedbackForwardingEnabled``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpointemail-identity.html#cfn-pinpointemail-identity-feedbackforwardingenabled
        """
        return self._values.get('feedback_forwarding_enabled')

    @property
    def mail_from_attributes(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnIdentity.MailFromAttributesProperty"]]]:
        """``AWS::PinpointEmail::Identity.MailFromAttributes``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpointemail-identity.html#cfn-pinpointemail-identity-mailfromattributes
        """
        return self._values.get('mail_from_attributes')

    @property
    def tags(self) -> typing.Optional[typing.List["CfnIdentity.TagsProperty"]]:
        """``AWS::PinpointEmail::Identity.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpointemail-identity.html#cfn-pinpointemail-identity-tags
        """
        return self._values.get('tags')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnIdentityProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


__all__ = ["CfnConfigurationSet", "CfnConfigurationSetEventDestination", "CfnConfigurationSetEventDestinationProps", "CfnConfigurationSetProps", "CfnDedicatedIpPool", "CfnDedicatedIpPoolProps", "CfnIdentity", "CfnIdentityProps", "__jsii_assembly__"]

publication.publish()
