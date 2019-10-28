import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.core
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-iotevents", "1.15.0", __name__, "aws-iotevents@1.15.0.jsii.tgz")
class CfnDetectorModel(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-iotevents.CfnDetectorModel"):
    """A CloudFormation ``AWS::IoTEvents::DetectorModel``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotevents-detectormodel.html
    cloudformationResource:
    :cloudformationResource:: AWS::IoTEvents::DetectorModel
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, detector_model_definition: typing.Optional[typing.Union[typing.Optional["DetectorModelDefinitionProperty"], typing.Optional[aws_cdk.core.IResolvable]]]=None, detector_model_description: typing.Optional[str]=None, detector_model_name: typing.Optional[str]=None, key: typing.Optional[str]=None, role_arn: typing.Optional[str]=None, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None) -> None:
        """Create a new ``AWS::IoTEvents::DetectorModel``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param detector_model_definition: ``AWS::IoTEvents::DetectorModel.DetectorModelDefinition``.
        :param detector_model_description: ``AWS::IoTEvents::DetectorModel.DetectorModelDescription``.
        :param detector_model_name: ``AWS::IoTEvents::DetectorModel.DetectorModelName``.
        :param key: ``AWS::IoTEvents::DetectorModel.Key``.
        :param role_arn: ``AWS::IoTEvents::DetectorModel.RoleArn``.
        :param tags: ``AWS::IoTEvents::DetectorModel.Tags``.
        """
        props = CfnDetectorModelProps(detector_model_definition=detector_model_definition, detector_model_description=detector_model_description, detector_model_name=detector_model_name, key=key, role_arn=role_arn, tags=tags)

        jsii.create(CfnDetectorModel, self, [scope, id, props])

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
        """``AWS::IoTEvents::DetectorModel.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotevents-detectormodel.html#cfn-iotevents-detectormodel-tags
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="detectorModelDefinition")
    def detector_model_definition(self) -> typing.Optional[typing.Union[typing.Optional["DetectorModelDefinitionProperty"], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::IoTEvents::DetectorModel.DetectorModelDefinition``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotevents-detectormodel.html#cfn-iotevents-detectormodel-detectormodeldefinition
        """
        return jsii.get(self, "detectorModelDefinition")

    @detector_model_definition.setter
    def detector_model_definition(self, value: typing.Optional[typing.Union[typing.Optional["DetectorModelDefinitionProperty"], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "detectorModelDefinition", value)

    @property
    @jsii.member(jsii_name="detectorModelDescription")
    def detector_model_description(self) -> typing.Optional[str]:
        """``AWS::IoTEvents::DetectorModel.DetectorModelDescription``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotevents-detectormodel.html#cfn-iotevents-detectormodel-detectormodeldescription
        """
        return jsii.get(self, "detectorModelDescription")

    @detector_model_description.setter
    def detector_model_description(self, value: typing.Optional[str]):
        return jsii.set(self, "detectorModelDescription", value)

    @property
    @jsii.member(jsii_name="detectorModelName")
    def detector_model_name(self) -> typing.Optional[str]:
        """``AWS::IoTEvents::DetectorModel.DetectorModelName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotevents-detectormodel.html#cfn-iotevents-detectormodel-detectormodelname
        """
        return jsii.get(self, "detectorModelName")

    @detector_model_name.setter
    def detector_model_name(self, value: typing.Optional[str]):
        return jsii.set(self, "detectorModelName", value)

    @property
    @jsii.member(jsii_name="key")
    def key(self) -> typing.Optional[str]:
        """``AWS::IoTEvents::DetectorModel.Key``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotevents-detectormodel.html#cfn-iotevents-detectormodel-key
        """
        return jsii.get(self, "key")

    @key.setter
    def key(self, value: typing.Optional[str]):
        return jsii.set(self, "key", value)

    @property
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> typing.Optional[str]:
        """``AWS::IoTEvents::DetectorModel.RoleArn``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotevents-detectormodel.html#cfn-iotevents-detectormodel-rolearn
        """
        return jsii.get(self, "roleArn")

    @role_arn.setter
    def role_arn(self, value: typing.Optional[str]):
        return jsii.set(self, "roleArn", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-iotevents.CfnDetectorModel.ActionProperty", jsii_struct_bases=[], name_mapping={'clear_timer': 'clearTimer', 'firehose': 'firehose', 'iot_events': 'iotEvents', 'iot_topic_publish': 'iotTopicPublish', 'lambda_': 'lambda', 'reset_timer': 'resetTimer', 'set_timer': 'setTimer', 'set_variable': 'setVariable', 'sns': 'sns', 'sqs': 'sqs'})
    class ActionProperty():
        def __init__(self, *, clear_timer: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnDetectorModel.ClearTimerProperty"]]]=None, firehose: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnDetectorModel.FirehoseProperty"]]]=None, iot_events: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnDetectorModel.IotEventsProperty"]]]=None, iot_topic_publish: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnDetectorModel.IotTopicPublishProperty"]]]=None, lambda_: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnDetectorModel.LambdaProperty"]]]=None, reset_timer: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnDetectorModel.ResetTimerProperty"]]]=None, set_timer: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnDetectorModel.SetTimerProperty"]]]=None, set_variable: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnDetectorModel.SetVariableProperty"]]]=None, sns: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnDetectorModel.SnsProperty"]]]=None, sqs: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnDetectorModel.SqsProperty"]]]=None):
            """
            :param clear_timer: ``CfnDetectorModel.ActionProperty.ClearTimer``.
            :param firehose: ``CfnDetectorModel.ActionProperty.Firehose``.
            :param iot_events: ``CfnDetectorModel.ActionProperty.IotEvents``.
            :param iot_topic_publish: ``CfnDetectorModel.ActionProperty.IotTopicPublish``.
            :param lambda_: ``CfnDetectorModel.ActionProperty.Lambda``.
            :param reset_timer: ``CfnDetectorModel.ActionProperty.ResetTimer``.
            :param set_timer: ``CfnDetectorModel.ActionProperty.SetTimer``.
            :param set_variable: ``CfnDetectorModel.ActionProperty.SetVariable``.
            :param sns: ``CfnDetectorModel.ActionProperty.Sns``.
            :param sqs: ``CfnDetectorModel.ActionProperty.Sqs``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-action.html
            """
            self._values = {
            }
            if clear_timer is not None: self._values["clear_timer"] = clear_timer
            if firehose is not None: self._values["firehose"] = firehose
            if iot_events is not None: self._values["iot_events"] = iot_events
            if iot_topic_publish is not None: self._values["iot_topic_publish"] = iot_topic_publish
            if lambda_ is not None: self._values["lambda_"] = lambda_
            if reset_timer is not None: self._values["reset_timer"] = reset_timer
            if set_timer is not None: self._values["set_timer"] = set_timer
            if set_variable is not None: self._values["set_variable"] = set_variable
            if sns is not None: self._values["sns"] = sns
            if sqs is not None: self._values["sqs"] = sqs

        @property
        def clear_timer(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnDetectorModel.ClearTimerProperty"]]]:
            """``CfnDetectorModel.ActionProperty.ClearTimer``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-action.html#cfn-iotevents-detectormodel-action-cleartimer
            """
            return self._values.get('clear_timer')

        @property
        def firehose(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnDetectorModel.FirehoseProperty"]]]:
            """``CfnDetectorModel.ActionProperty.Firehose``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-action.html#cfn-iotevents-detectormodel-action-firehose
            """
            return self._values.get('firehose')

        @property
        def iot_events(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnDetectorModel.IotEventsProperty"]]]:
            """``CfnDetectorModel.ActionProperty.IotEvents``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-action.html#cfn-iotevents-detectormodel-action-iotevents
            """
            return self._values.get('iot_events')

        @property
        def iot_topic_publish(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnDetectorModel.IotTopicPublishProperty"]]]:
            """``CfnDetectorModel.ActionProperty.IotTopicPublish``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-action.html#cfn-iotevents-detectormodel-action-iottopicpublish
            """
            return self._values.get('iot_topic_publish')

        @property
        def lambda_(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnDetectorModel.LambdaProperty"]]]:
            """``CfnDetectorModel.ActionProperty.Lambda``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-action.html#cfn-iotevents-detectormodel-action-lambda
            """
            return self._values.get('lambda_')

        @property
        def reset_timer(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnDetectorModel.ResetTimerProperty"]]]:
            """``CfnDetectorModel.ActionProperty.ResetTimer``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-action.html#cfn-iotevents-detectormodel-action-resettimer
            """
            return self._values.get('reset_timer')

        @property
        def set_timer(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnDetectorModel.SetTimerProperty"]]]:
            """``CfnDetectorModel.ActionProperty.SetTimer``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-action.html#cfn-iotevents-detectormodel-action-settimer
            """
            return self._values.get('set_timer')

        @property
        def set_variable(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnDetectorModel.SetVariableProperty"]]]:
            """``CfnDetectorModel.ActionProperty.SetVariable``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-action.html#cfn-iotevents-detectormodel-action-setvariable
            """
            return self._values.get('set_variable')

        @property
        def sns(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnDetectorModel.SnsProperty"]]]:
            """``CfnDetectorModel.ActionProperty.Sns``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-action.html#cfn-iotevents-detectormodel-action-sns
            """
            return self._values.get('sns')

        @property
        def sqs(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnDetectorModel.SqsProperty"]]]:
            """``CfnDetectorModel.ActionProperty.Sqs``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-action.html#cfn-iotevents-detectormodel-action-sqs
            """
            return self._values.get('sqs')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'ActionProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-iotevents.CfnDetectorModel.ClearTimerProperty", jsii_struct_bases=[], name_mapping={'timer_name': 'timerName'})
    class ClearTimerProperty():
        def __init__(self, *, timer_name: typing.Optional[str]=None):
            """
            :param timer_name: ``CfnDetectorModel.ClearTimerProperty.TimerName``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-cleartimer.html
            """
            self._values = {
            }
            if timer_name is not None: self._values["timer_name"] = timer_name

        @property
        def timer_name(self) -> typing.Optional[str]:
            """``CfnDetectorModel.ClearTimerProperty.TimerName``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-cleartimer.html#cfn-iotevents-detectormodel-cleartimer-timername
            """
            return self._values.get('timer_name')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'ClearTimerProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-iotevents.CfnDetectorModel.DetectorModelDefinitionProperty", jsii_struct_bases=[], name_mapping={'initial_state_name': 'initialStateName', 'states': 'states'})
    class DetectorModelDefinitionProperty():
        def __init__(self, *, initial_state_name: typing.Optional[str]=None, states: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnDetectorModel.StateProperty"]]]]]=None):
            """
            :param initial_state_name: ``CfnDetectorModel.DetectorModelDefinitionProperty.InitialStateName``.
            :param states: ``CfnDetectorModel.DetectorModelDefinitionProperty.States``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-detectormodeldefinition.html
            """
            self._values = {
            }
            if initial_state_name is not None: self._values["initial_state_name"] = initial_state_name
            if states is not None: self._values["states"] = states

        @property
        def initial_state_name(self) -> typing.Optional[str]:
            """``CfnDetectorModel.DetectorModelDefinitionProperty.InitialStateName``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-detectormodeldefinition.html#cfn-iotevents-detectormodel-detectormodeldefinition-initialstatename
            """
            return self._values.get('initial_state_name')

        @property
        def states(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnDetectorModel.StateProperty"]]]]]:
            """``CfnDetectorModel.DetectorModelDefinitionProperty.States``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-detectormodeldefinition.html#cfn-iotevents-detectormodel-detectormodeldefinition-states
            """
            return self._values.get('states')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'DetectorModelDefinitionProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-iotevents.CfnDetectorModel.EventProperty", jsii_struct_bases=[], name_mapping={'actions': 'actions', 'condition': 'condition', 'event_name': 'eventName'})
    class EventProperty():
        def __init__(self, *, actions: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnDetectorModel.ActionProperty"]]]]]=None, condition: typing.Optional[str]=None, event_name: typing.Optional[str]=None):
            """
            :param actions: ``CfnDetectorModel.EventProperty.Actions``.
            :param condition: ``CfnDetectorModel.EventProperty.Condition``.
            :param event_name: ``CfnDetectorModel.EventProperty.EventName``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-event.html
            """
            self._values = {
            }
            if actions is not None: self._values["actions"] = actions
            if condition is not None: self._values["condition"] = condition
            if event_name is not None: self._values["event_name"] = event_name

        @property
        def actions(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnDetectorModel.ActionProperty"]]]]]:
            """``CfnDetectorModel.EventProperty.Actions``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-event.html#cfn-iotevents-detectormodel-event-actions
            """
            return self._values.get('actions')

        @property
        def condition(self) -> typing.Optional[str]:
            """``CfnDetectorModel.EventProperty.Condition``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-event.html#cfn-iotevents-detectormodel-event-condition
            """
            return self._values.get('condition')

        @property
        def event_name(self) -> typing.Optional[str]:
            """``CfnDetectorModel.EventProperty.EventName``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-event.html#cfn-iotevents-detectormodel-event-eventname
            """
            return self._values.get('event_name')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'EventProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-iotevents.CfnDetectorModel.FirehoseProperty", jsii_struct_bases=[], name_mapping={'delivery_stream_name': 'deliveryStreamName', 'separator': 'separator'})
    class FirehoseProperty():
        def __init__(self, *, delivery_stream_name: typing.Optional[str]=None, separator: typing.Optional[str]=None):
            """
            :param delivery_stream_name: ``CfnDetectorModel.FirehoseProperty.DeliveryStreamName``.
            :param separator: ``CfnDetectorModel.FirehoseProperty.Separator``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-firehose.html
            """
            self._values = {
            }
            if delivery_stream_name is not None: self._values["delivery_stream_name"] = delivery_stream_name
            if separator is not None: self._values["separator"] = separator

        @property
        def delivery_stream_name(self) -> typing.Optional[str]:
            """``CfnDetectorModel.FirehoseProperty.DeliveryStreamName``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-firehose.html#cfn-iotevents-detectormodel-firehose-deliverystreamname
            """
            return self._values.get('delivery_stream_name')

        @property
        def separator(self) -> typing.Optional[str]:
            """``CfnDetectorModel.FirehoseProperty.Separator``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-firehose.html#cfn-iotevents-detectormodel-firehose-separator
            """
            return self._values.get('separator')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'FirehoseProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-iotevents.CfnDetectorModel.IotEventsProperty", jsii_struct_bases=[], name_mapping={'input_name': 'inputName'})
    class IotEventsProperty():
        def __init__(self, *, input_name: typing.Optional[str]=None):
            """
            :param input_name: ``CfnDetectorModel.IotEventsProperty.InputName``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-iotevents.html
            """
            self._values = {
            }
            if input_name is not None: self._values["input_name"] = input_name

        @property
        def input_name(self) -> typing.Optional[str]:
            """``CfnDetectorModel.IotEventsProperty.InputName``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-iotevents.html#cfn-iotevents-detectormodel-iotevents-inputname
            """
            return self._values.get('input_name')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'IotEventsProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-iotevents.CfnDetectorModel.IotTopicPublishProperty", jsii_struct_bases=[], name_mapping={'mqtt_topic': 'mqttTopic'})
    class IotTopicPublishProperty():
        def __init__(self, *, mqtt_topic: typing.Optional[str]=None):
            """
            :param mqtt_topic: ``CfnDetectorModel.IotTopicPublishProperty.MqttTopic``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-iottopicpublish.html
            """
            self._values = {
            }
            if mqtt_topic is not None: self._values["mqtt_topic"] = mqtt_topic

        @property
        def mqtt_topic(self) -> typing.Optional[str]:
            """``CfnDetectorModel.IotTopicPublishProperty.MqttTopic``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-iottopicpublish.html#cfn-iotevents-detectormodel-iottopicpublish-mqtttopic
            """
            return self._values.get('mqtt_topic')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'IotTopicPublishProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-iotevents.CfnDetectorModel.LambdaProperty", jsii_struct_bases=[], name_mapping={'function_arn': 'functionArn'})
    class LambdaProperty():
        def __init__(self, *, function_arn: typing.Optional[str]=None):
            """
            :param function_arn: ``CfnDetectorModel.LambdaProperty.FunctionArn``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-lambda.html
            """
            self._values = {
            }
            if function_arn is not None: self._values["function_arn"] = function_arn

        @property
        def function_arn(self) -> typing.Optional[str]:
            """``CfnDetectorModel.LambdaProperty.FunctionArn``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-lambda.html#cfn-iotevents-detectormodel-lambda-functionarn
            """
            return self._values.get('function_arn')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'LambdaProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-iotevents.CfnDetectorModel.OnEnterProperty", jsii_struct_bases=[], name_mapping={'events': 'events'})
    class OnEnterProperty():
        def __init__(self, *, events: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnDetectorModel.EventProperty"]]]]]=None):
            """
            :param events: ``CfnDetectorModel.OnEnterProperty.Events``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-onenter.html
            """
            self._values = {
            }
            if events is not None: self._values["events"] = events

        @property
        def events(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnDetectorModel.EventProperty"]]]]]:
            """``CfnDetectorModel.OnEnterProperty.Events``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-onenter.html#cfn-iotevents-detectormodel-onenter-events
            """
            return self._values.get('events')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'OnEnterProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-iotevents.CfnDetectorModel.OnExitProperty", jsii_struct_bases=[], name_mapping={'events': 'events'})
    class OnExitProperty():
        def __init__(self, *, events: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnDetectorModel.EventProperty"]]]]]=None):
            """
            :param events: ``CfnDetectorModel.OnExitProperty.Events``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-onexit.html
            """
            self._values = {
            }
            if events is not None: self._values["events"] = events

        @property
        def events(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnDetectorModel.EventProperty"]]]]]:
            """``CfnDetectorModel.OnExitProperty.Events``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-onexit.html#cfn-iotevents-detectormodel-onexit-events
            """
            return self._values.get('events')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'OnExitProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-iotevents.CfnDetectorModel.OnInputProperty", jsii_struct_bases=[], name_mapping={'events': 'events', 'transition_events': 'transitionEvents'})
    class OnInputProperty():
        def __init__(self, *, events: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnDetectorModel.EventProperty"]]]]]=None, transition_events: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnDetectorModel.TransitionEventProperty"]]]]]=None):
            """
            :param events: ``CfnDetectorModel.OnInputProperty.Events``.
            :param transition_events: ``CfnDetectorModel.OnInputProperty.TransitionEvents``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-oninput.html
            """
            self._values = {
            }
            if events is not None: self._values["events"] = events
            if transition_events is not None: self._values["transition_events"] = transition_events

        @property
        def events(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnDetectorModel.EventProperty"]]]]]:
            """``CfnDetectorModel.OnInputProperty.Events``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-oninput.html#cfn-iotevents-detectormodel-oninput-events
            """
            return self._values.get('events')

        @property
        def transition_events(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnDetectorModel.TransitionEventProperty"]]]]]:
            """``CfnDetectorModel.OnInputProperty.TransitionEvents``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-oninput.html#cfn-iotevents-detectormodel-oninput-transitionevents
            """
            return self._values.get('transition_events')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'OnInputProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-iotevents.CfnDetectorModel.ResetTimerProperty", jsii_struct_bases=[], name_mapping={'timer_name': 'timerName'})
    class ResetTimerProperty():
        def __init__(self, *, timer_name: typing.Optional[str]=None):
            """
            :param timer_name: ``CfnDetectorModel.ResetTimerProperty.TimerName``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-resettimer.html
            """
            self._values = {
            }
            if timer_name is not None: self._values["timer_name"] = timer_name

        @property
        def timer_name(self) -> typing.Optional[str]:
            """``CfnDetectorModel.ResetTimerProperty.TimerName``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-resettimer.html#cfn-iotevents-detectormodel-resettimer-timername
            """
            return self._values.get('timer_name')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'ResetTimerProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-iotevents.CfnDetectorModel.SetTimerProperty", jsii_struct_bases=[], name_mapping={'seconds': 'seconds', 'timer_name': 'timerName'})
    class SetTimerProperty():
        def __init__(self, *, seconds: typing.Optional[jsii.Number]=None, timer_name: typing.Optional[str]=None):
            """
            :param seconds: ``CfnDetectorModel.SetTimerProperty.Seconds``.
            :param timer_name: ``CfnDetectorModel.SetTimerProperty.TimerName``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-settimer.html
            """
            self._values = {
            }
            if seconds is not None: self._values["seconds"] = seconds
            if timer_name is not None: self._values["timer_name"] = timer_name

        @property
        def seconds(self) -> typing.Optional[jsii.Number]:
            """``CfnDetectorModel.SetTimerProperty.Seconds``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-settimer.html#cfn-iotevents-detectormodel-settimer-seconds
            """
            return self._values.get('seconds')

        @property
        def timer_name(self) -> typing.Optional[str]:
            """``CfnDetectorModel.SetTimerProperty.TimerName``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-settimer.html#cfn-iotevents-detectormodel-settimer-timername
            """
            return self._values.get('timer_name')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'SetTimerProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-iotevents.CfnDetectorModel.SetVariableProperty", jsii_struct_bases=[], name_mapping={'value': 'value', 'variable_name': 'variableName'})
    class SetVariableProperty():
        def __init__(self, *, value: typing.Optional[str]=None, variable_name: typing.Optional[str]=None):
            """
            :param value: ``CfnDetectorModel.SetVariableProperty.Value``.
            :param variable_name: ``CfnDetectorModel.SetVariableProperty.VariableName``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-setvariable.html
            """
            self._values = {
            }
            if value is not None: self._values["value"] = value
            if variable_name is not None: self._values["variable_name"] = variable_name

        @property
        def value(self) -> typing.Optional[str]:
            """``CfnDetectorModel.SetVariableProperty.Value``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-setvariable.html#cfn-iotevents-detectormodel-setvariable-value
            """
            return self._values.get('value')

        @property
        def variable_name(self) -> typing.Optional[str]:
            """``CfnDetectorModel.SetVariableProperty.VariableName``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-setvariable.html#cfn-iotevents-detectormodel-setvariable-variablename
            """
            return self._values.get('variable_name')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'SetVariableProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-iotevents.CfnDetectorModel.SnsProperty", jsii_struct_bases=[], name_mapping={'target_arn': 'targetArn'})
    class SnsProperty():
        def __init__(self, *, target_arn: typing.Optional[str]=None):
            """
            :param target_arn: ``CfnDetectorModel.SnsProperty.TargetArn``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-sns.html
            """
            self._values = {
            }
            if target_arn is not None: self._values["target_arn"] = target_arn

        @property
        def target_arn(self) -> typing.Optional[str]:
            """``CfnDetectorModel.SnsProperty.TargetArn``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-sns.html#cfn-iotevents-detectormodel-sns-targetarn
            """
            return self._values.get('target_arn')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'SnsProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-iotevents.CfnDetectorModel.SqsProperty", jsii_struct_bases=[], name_mapping={'queue_url': 'queueUrl', 'use_base64': 'useBase64'})
    class SqsProperty():
        def __init__(self, *, queue_url: typing.Optional[str]=None, use_base64: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None):
            """
            :param queue_url: ``CfnDetectorModel.SqsProperty.QueueUrl``.
            :param use_base64: ``CfnDetectorModel.SqsProperty.UseBase64``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-sqs.html
            """
            self._values = {
            }
            if queue_url is not None: self._values["queue_url"] = queue_url
            if use_base64 is not None: self._values["use_base64"] = use_base64

        @property
        def queue_url(self) -> typing.Optional[str]:
            """``CfnDetectorModel.SqsProperty.QueueUrl``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-sqs.html#cfn-iotevents-detectormodel-sqs-queueurl
            """
            return self._values.get('queue_url')

        @property
        def use_base64(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
            """``CfnDetectorModel.SqsProperty.UseBase64``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-sqs.html#cfn-iotevents-detectormodel-sqs-usebase64
            """
            return self._values.get('use_base64')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'SqsProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-iotevents.CfnDetectorModel.StateProperty", jsii_struct_bases=[], name_mapping={'on_enter': 'onEnter', 'on_exit': 'onExit', 'on_input': 'onInput', 'state_name': 'stateName'})
    class StateProperty():
        def __init__(self, *, on_enter: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnDetectorModel.OnEnterProperty"]]]=None, on_exit: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnDetectorModel.OnExitProperty"]]]=None, on_input: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnDetectorModel.OnInputProperty"]]]=None, state_name: typing.Optional[str]=None):
            """
            :param on_enter: ``CfnDetectorModel.StateProperty.OnEnter``.
            :param on_exit: ``CfnDetectorModel.StateProperty.OnExit``.
            :param on_input: ``CfnDetectorModel.StateProperty.OnInput``.
            :param state_name: ``CfnDetectorModel.StateProperty.StateName``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-state.html
            """
            self._values = {
            }
            if on_enter is not None: self._values["on_enter"] = on_enter
            if on_exit is not None: self._values["on_exit"] = on_exit
            if on_input is not None: self._values["on_input"] = on_input
            if state_name is not None: self._values["state_name"] = state_name

        @property
        def on_enter(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnDetectorModel.OnEnterProperty"]]]:
            """``CfnDetectorModel.StateProperty.OnEnter``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-state.html#cfn-iotevents-detectormodel-state-onenter
            """
            return self._values.get('on_enter')

        @property
        def on_exit(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnDetectorModel.OnExitProperty"]]]:
            """``CfnDetectorModel.StateProperty.OnExit``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-state.html#cfn-iotevents-detectormodel-state-onexit
            """
            return self._values.get('on_exit')

        @property
        def on_input(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnDetectorModel.OnInputProperty"]]]:
            """``CfnDetectorModel.StateProperty.OnInput``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-state.html#cfn-iotevents-detectormodel-state-oninput
            """
            return self._values.get('on_input')

        @property
        def state_name(self) -> typing.Optional[str]:
            """``CfnDetectorModel.StateProperty.StateName``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-state.html#cfn-iotevents-detectormodel-state-statename
            """
            return self._values.get('state_name')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'StateProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-iotevents.CfnDetectorModel.TransitionEventProperty", jsii_struct_bases=[], name_mapping={'actions': 'actions', 'condition': 'condition', 'event_name': 'eventName', 'next_state': 'nextState'})
    class TransitionEventProperty():
        def __init__(self, *, actions: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnDetectorModel.ActionProperty"]]]]]=None, condition: typing.Optional[str]=None, event_name: typing.Optional[str]=None, next_state: typing.Optional[str]=None):
            """
            :param actions: ``CfnDetectorModel.TransitionEventProperty.Actions``.
            :param condition: ``CfnDetectorModel.TransitionEventProperty.Condition``.
            :param event_name: ``CfnDetectorModel.TransitionEventProperty.EventName``.
            :param next_state: ``CfnDetectorModel.TransitionEventProperty.NextState``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-transitionevent.html
            """
            self._values = {
            }
            if actions is not None: self._values["actions"] = actions
            if condition is not None: self._values["condition"] = condition
            if event_name is not None: self._values["event_name"] = event_name
            if next_state is not None: self._values["next_state"] = next_state

        @property
        def actions(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnDetectorModel.ActionProperty"]]]]]:
            """``CfnDetectorModel.TransitionEventProperty.Actions``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-transitionevent.html#cfn-iotevents-detectormodel-transitionevent-actions
            """
            return self._values.get('actions')

        @property
        def condition(self) -> typing.Optional[str]:
            """``CfnDetectorModel.TransitionEventProperty.Condition``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-transitionevent.html#cfn-iotevents-detectormodel-transitionevent-condition
            """
            return self._values.get('condition')

        @property
        def event_name(self) -> typing.Optional[str]:
            """``CfnDetectorModel.TransitionEventProperty.EventName``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-transitionevent.html#cfn-iotevents-detectormodel-transitionevent-eventname
            """
            return self._values.get('event_name')

        @property
        def next_state(self) -> typing.Optional[str]:
            """``CfnDetectorModel.TransitionEventProperty.NextState``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-transitionevent.html#cfn-iotevents-detectormodel-transitionevent-nextstate
            """
            return self._values.get('next_state')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'TransitionEventProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



@jsii.data_type(jsii_type="@aws-cdk/aws-iotevents.CfnDetectorModelProps", jsii_struct_bases=[], name_mapping={'detector_model_definition': 'detectorModelDefinition', 'detector_model_description': 'detectorModelDescription', 'detector_model_name': 'detectorModelName', 'key': 'key', 'role_arn': 'roleArn', 'tags': 'tags'})
class CfnDetectorModelProps():
    def __init__(self, *, detector_model_definition: typing.Optional[typing.Union[typing.Optional["CfnDetectorModel.DetectorModelDefinitionProperty"], typing.Optional[aws_cdk.core.IResolvable]]]=None, detector_model_description: typing.Optional[str]=None, detector_model_name: typing.Optional[str]=None, key: typing.Optional[str]=None, role_arn: typing.Optional[str]=None, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None):
        """Properties for defining a ``AWS::IoTEvents::DetectorModel``.

        :param detector_model_definition: ``AWS::IoTEvents::DetectorModel.DetectorModelDefinition``.
        :param detector_model_description: ``AWS::IoTEvents::DetectorModel.DetectorModelDescription``.
        :param detector_model_name: ``AWS::IoTEvents::DetectorModel.DetectorModelName``.
        :param key: ``AWS::IoTEvents::DetectorModel.Key``.
        :param role_arn: ``AWS::IoTEvents::DetectorModel.RoleArn``.
        :param tags: ``AWS::IoTEvents::DetectorModel.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotevents-detectormodel.html
        """
        self._values = {
        }
        if detector_model_definition is not None: self._values["detector_model_definition"] = detector_model_definition
        if detector_model_description is not None: self._values["detector_model_description"] = detector_model_description
        if detector_model_name is not None: self._values["detector_model_name"] = detector_model_name
        if key is not None: self._values["key"] = key
        if role_arn is not None: self._values["role_arn"] = role_arn
        if tags is not None: self._values["tags"] = tags

    @property
    def detector_model_definition(self) -> typing.Optional[typing.Union[typing.Optional["CfnDetectorModel.DetectorModelDefinitionProperty"], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::IoTEvents::DetectorModel.DetectorModelDefinition``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotevents-detectormodel.html#cfn-iotevents-detectormodel-detectormodeldefinition
        """
        return self._values.get('detector_model_definition')

    @property
    def detector_model_description(self) -> typing.Optional[str]:
        """``AWS::IoTEvents::DetectorModel.DetectorModelDescription``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotevents-detectormodel.html#cfn-iotevents-detectormodel-detectormodeldescription
        """
        return self._values.get('detector_model_description')

    @property
    def detector_model_name(self) -> typing.Optional[str]:
        """``AWS::IoTEvents::DetectorModel.DetectorModelName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotevents-detectormodel.html#cfn-iotevents-detectormodel-detectormodelname
        """
        return self._values.get('detector_model_name')

    @property
    def key(self) -> typing.Optional[str]:
        """``AWS::IoTEvents::DetectorModel.Key``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotevents-detectormodel.html#cfn-iotevents-detectormodel-key
        """
        return self._values.get('key')

    @property
    def role_arn(self) -> typing.Optional[str]:
        """``AWS::IoTEvents::DetectorModel.RoleArn``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotevents-detectormodel.html#cfn-iotevents-detectormodel-rolearn
        """
        return self._values.get('role_arn')

    @property
    def tags(self) -> typing.Optional[typing.List[aws_cdk.core.CfnTag]]:
        """``AWS::IoTEvents::DetectorModel.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotevents-detectormodel.html#cfn-iotevents-detectormodel-tags
        """
        return self._values.get('tags')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnDetectorModelProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnInput(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-iotevents.CfnInput"):
    """A CloudFormation ``AWS::IoTEvents::Input``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotevents-input.html
    cloudformationResource:
    :cloudformationResource:: AWS::IoTEvents::Input
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, input_definition: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["InputDefinitionProperty"]]]=None, input_description: typing.Optional[str]=None, input_name: typing.Optional[str]=None, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None) -> None:
        """Create a new ``AWS::IoTEvents::Input``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param input_definition: ``AWS::IoTEvents::Input.InputDefinition``.
        :param input_description: ``AWS::IoTEvents::Input.InputDescription``.
        :param input_name: ``AWS::IoTEvents::Input.InputName``.
        :param tags: ``AWS::IoTEvents::Input.Tags``.
        """
        props = CfnInputProps(input_definition=input_definition, input_description=input_description, input_name=input_name, tags=tags)

        jsii.create(CfnInput, self, [scope, id, props])

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
        """``AWS::IoTEvents::Input.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotevents-input.html#cfn-iotevents-input-tags
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="inputDefinition")
    def input_definition(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["InputDefinitionProperty"]]]:
        """``AWS::IoTEvents::Input.InputDefinition``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotevents-input.html#cfn-iotevents-input-inputdefinition
        """
        return jsii.get(self, "inputDefinition")

    @input_definition.setter
    def input_definition(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["InputDefinitionProperty"]]]):
        return jsii.set(self, "inputDefinition", value)

    @property
    @jsii.member(jsii_name="inputDescription")
    def input_description(self) -> typing.Optional[str]:
        """``AWS::IoTEvents::Input.InputDescription``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotevents-input.html#cfn-iotevents-input-inputdescription
        """
        return jsii.get(self, "inputDescription")

    @input_description.setter
    def input_description(self, value: typing.Optional[str]):
        return jsii.set(self, "inputDescription", value)

    @property
    @jsii.member(jsii_name="inputName")
    def input_name(self) -> typing.Optional[str]:
        """``AWS::IoTEvents::Input.InputName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotevents-input.html#cfn-iotevents-input-inputname
        """
        return jsii.get(self, "inputName")

    @input_name.setter
    def input_name(self, value: typing.Optional[str]):
        return jsii.set(self, "inputName", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-iotevents.CfnInput.AttributeProperty", jsii_struct_bases=[], name_mapping={'json_path': 'jsonPath'})
    class AttributeProperty():
        def __init__(self, *, json_path: typing.Optional[str]=None):
            """
            :param json_path: ``CfnInput.AttributeProperty.JsonPath``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-input-attribute.html
            """
            self._values = {
            }
            if json_path is not None: self._values["json_path"] = json_path

        @property
        def json_path(self) -> typing.Optional[str]:
            """``CfnInput.AttributeProperty.JsonPath``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-input-attribute.html#cfn-iotevents-input-attribute-jsonpath
            """
            return self._values.get('json_path')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'AttributeProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-iotevents.CfnInput.InputDefinitionProperty", jsii_struct_bases=[], name_mapping={'attributes': 'attributes'})
    class InputDefinitionProperty():
        def __init__(self, *, attributes: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnInput.AttributeProperty"]]]]]=None):
            """
            :param attributes: ``CfnInput.InputDefinitionProperty.Attributes``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-input-inputdefinition.html
            """
            self._values = {
            }
            if attributes is not None: self._values["attributes"] = attributes

        @property
        def attributes(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnInput.AttributeProperty"]]]]]:
            """``CfnInput.InputDefinitionProperty.Attributes``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-input-inputdefinition.html#cfn-iotevents-input-inputdefinition-attributes
            """
            return self._values.get('attributes')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'InputDefinitionProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



@jsii.data_type(jsii_type="@aws-cdk/aws-iotevents.CfnInputProps", jsii_struct_bases=[], name_mapping={'input_definition': 'inputDefinition', 'input_description': 'inputDescription', 'input_name': 'inputName', 'tags': 'tags'})
class CfnInputProps():
    def __init__(self, *, input_definition: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnInput.InputDefinitionProperty"]]]=None, input_description: typing.Optional[str]=None, input_name: typing.Optional[str]=None, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None):
        """Properties for defining a ``AWS::IoTEvents::Input``.

        :param input_definition: ``AWS::IoTEvents::Input.InputDefinition``.
        :param input_description: ``AWS::IoTEvents::Input.InputDescription``.
        :param input_name: ``AWS::IoTEvents::Input.InputName``.
        :param tags: ``AWS::IoTEvents::Input.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotevents-input.html
        """
        self._values = {
        }
        if input_definition is not None: self._values["input_definition"] = input_definition
        if input_description is not None: self._values["input_description"] = input_description
        if input_name is not None: self._values["input_name"] = input_name
        if tags is not None: self._values["tags"] = tags

    @property
    def input_definition(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnInput.InputDefinitionProperty"]]]:
        """``AWS::IoTEvents::Input.InputDefinition``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotevents-input.html#cfn-iotevents-input-inputdefinition
        """
        return self._values.get('input_definition')

    @property
    def input_description(self) -> typing.Optional[str]:
        """``AWS::IoTEvents::Input.InputDescription``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotevents-input.html#cfn-iotevents-input-inputdescription
        """
        return self._values.get('input_description')

    @property
    def input_name(self) -> typing.Optional[str]:
        """``AWS::IoTEvents::Input.InputName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotevents-input.html#cfn-iotevents-input-inputname
        """
        return self._values.get('input_name')

    @property
    def tags(self) -> typing.Optional[typing.List[aws_cdk.core.CfnTag]]:
        """``AWS::IoTEvents::Input.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotevents-input.html#cfn-iotevents-input-tags
        """
        return self._values.get('tags')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnInputProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


__all__ = ["CfnDetectorModel", "CfnDetectorModelProps", "CfnInput", "CfnInputProps", "__jsii_assembly__"]

publication.publish()
