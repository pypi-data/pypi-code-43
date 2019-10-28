import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.aws_iam
import aws_cdk.aws_kinesis
import aws_cdk.aws_lambda
import aws_cdk.aws_logs
import aws_cdk.core
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-logs-destinations", "1.15.0", __name__, "aws-logs-destinations@1.15.0.jsii.tgz")
@jsii.implements(aws_cdk.aws_logs.ILogSubscriptionDestination)
class KinesisDestination(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-logs-destinations.KinesisDestination"):
    """Use a Kinesis stream as the destination for a log subscription."""
    def __init__(self, stream: aws_cdk.aws_kinesis.IStream) -> None:
        """
        :param stream: -
        """
        jsii.create(KinesisDestination, self, [stream])

    @jsii.member(jsii_name="bind")
    def bind(self, scope: aws_cdk.core.Construct, _source_log_group: aws_cdk.aws_logs.ILogGroup) -> aws_cdk.aws_logs.LogSubscriptionDestinationConfig:
        """Return the properties required to send subscription events to this destination.

        If necessary, the destination can use the properties of the SubscriptionFilter
        object itself to configure its permissions to allow the subscription to write
        to it.

        The destination may reconfigure its own permissions in response to this
        function call.

        :param scope: -
        :param _source_log_group: -
        """
        return jsii.invoke(self, "bind", [scope, _source_log_group])


@jsii.implements(aws_cdk.aws_logs.ILogSubscriptionDestination)
class LambdaDestination(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-logs-destinations.LambdaDestination"):
    """Use a Lamda Function as the destination for a log subscription."""
    def __init__(self, fn: aws_cdk.aws_lambda.IFunction) -> None:
        """
        :param fn: -
        """
        jsii.create(LambdaDestination, self, [fn])

    @jsii.member(jsii_name="bind")
    def bind(self, _scope: aws_cdk.core.Construct, log_group: aws_cdk.aws_logs.ILogGroup) -> aws_cdk.aws_logs.LogSubscriptionDestinationConfig:
        """Return the properties required to send subscription events to this destination.

        If necessary, the destination can use the properties of the SubscriptionFilter
        object itself to configure its permissions to allow the subscription to write
        to it.

        The destination may reconfigure its own permissions in response to this
        function call.

        :param _scope: -
        :param log_group: -
        """
        return jsii.invoke(self, "bind", [_scope, log_group])


__all__ = ["KinesisDestination", "LambdaDestination", "__jsii_assembly__"]

publication.publish()
