import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.core
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-kinesisfirehose", "1.15.0", __name__, "aws-kinesisfirehose@1.15.0.jsii.tgz")
class CfnDeliveryStream(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream"):
    """A CloudFormation ``AWS::KinesisFirehose::DeliveryStream``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisfirehose-deliverystream.html
    cloudformationResource:
    :cloudformationResource:: AWS::KinesisFirehose::DeliveryStream
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, delivery_stream_name: typing.Optional[str]=None, delivery_stream_type: typing.Optional[str]=None, elasticsearch_destination_configuration: typing.Optional[typing.Union[typing.Optional["ElasticsearchDestinationConfigurationProperty"], typing.Optional[aws_cdk.core.IResolvable]]]=None, extended_s3_destination_configuration: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["ExtendedS3DestinationConfigurationProperty"]]]=None, kinesis_stream_source_configuration: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["KinesisStreamSourceConfigurationProperty"]]]=None, redshift_destination_configuration: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["RedshiftDestinationConfigurationProperty"]]]=None, s3_destination_configuration: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["S3DestinationConfigurationProperty"]]]=None, splunk_destination_configuration: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["SplunkDestinationConfigurationProperty"]]]=None) -> None:
        """Create a new ``AWS::KinesisFirehose::DeliveryStream``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param delivery_stream_name: ``AWS::KinesisFirehose::DeliveryStream.DeliveryStreamName``.
        :param delivery_stream_type: ``AWS::KinesisFirehose::DeliveryStream.DeliveryStreamType``.
        :param elasticsearch_destination_configuration: ``AWS::KinesisFirehose::DeliveryStream.ElasticsearchDestinationConfiguration``.
        :param extended_s3_destination_configuration: ``AWS::KinesisFirehose::DeliveryStream.ExtendedS3DestinationConfiguration``.
        :param kinesis_stream_source_configuration: ``AWS::KinesisFirehose::DeliveryStream.KinesisStreamSourceConfiguration``.
        :param redshift_destination_configuration: ``AWS::KinesisFirehose::DeliveryStream.RedshiftDestinationConfiguration``.
        :param s3_destination_configuration: ``AWS::KinesisFirehose::DeliveryStream.S3DestinationConfiguration``.
        :param splunk_destination_configuration: ``AWS::KinesisFirehose::DeliveryStream.SplunkDestinationConfiguration``.
        """
        props = CfnDeliveryStreamProps(delivery_stream_name=delivery_stream_name, delivery_stream_type=delivery_stream_type, elasticsearch_destination_configuration=elasticsearch_destination_configuration, extended_s3_destination_configuration=extended_s3_destination_configuration, kinesis_stream_source_configuration=kinesis_stream_source_configuration, redshift_destination_configuration=redshift_destination_configuration, s3_destination_configuration=s3_destination_configuration, splunk_destination_configuration=splunk_destination_configuration)

        jsii.create(CfnDeliveryStream, self, [scope, id, props])

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
    @jsii.member(jsii_name="deliveryStreamName")
    def delivery_stream_name(self) -> typing.Optional[str]:
        """``AWS::KinesisFirehose::DeliveryStream.DeliveryStreamName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisfirehose-deliverystream.html#cfn-kinesisfirehose-deliverystream-deliverystreamname
        """
        return jsii.get(self, "deliveryStreamName")

    @delivery_stream_name.setter
    def delivery_stream_name(self, value: typing.Optional[str]):
        return jsii.set(self, "deliveryStreamName", value)

    @property
    @jsii.member(jsii_name="deliveryStreamType")
    def delivery_stream_type(self) -> typing.Optional[str]:
        """``AWS::KinesisFirehose::DeliveryStream.DeliveryStreamType``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisfirehose-deliverystream.html#cfn-kinesisfirehose-deliverystream-deliverystreamtype
        """
        return jsii.get(self, "deliveryStreamType")

    @delivery_stream_type.setter
    def delivery_stream_type(self, value: typing.Optional[str]):
        return jsii.set(self, "deliveryStreamType", value)

    @property
    @jsii.member(jsii_name="elasticsearchDestinationConfiguration")
    def elasticsearch_destination_configuration(self) -> typing.Optional[typing.Union[typing.Optional["ElasticsearchDestinationConfigurationProperty"], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::KinesisFirehose::DeliveryStream.ElasticsearchDestinationConfiguration``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisfirehose-deliverystream.html#cfn-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration
        """
        return jsii.get(self, "elasticsearchDestinationConfiguration")

    @elasticsearch_destination_configuration.setter
    def elasticsearch_destination_configuration(self, value: typing.Optional[typing.Union[typing.Optional["ElasticsearchDestinationConfigurationProperty"], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "elasticsearchDestinationConfiguration", value)

    @property
    @jsii.member(jsii_name="extendedS3DestinationConfiguration")
    def extended_s3_destination_configuration(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["ExtendedS3DestinationConfigurationProperty"]]]:
        """``AWS::KinesisFirehose::DeliveryStream.ExtendedS3DestinationConfiguration``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisfirehose-deliverystream.html#cfn-kinesisfirehose-deliverystream-extendeds3destinationconfiguration
        """
        return jsii.get(self, "extendedS3DestinationConfiguration")

    @extended_s3_destination_configuration.setter
    def extended_s3_destination_configuration(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["ExtendedS3DestinationConfigurationProperty"]]]):
        return jsii.set(self, "extendedS3DestinationConfiguration", value)

    @property
    @jsii.member(jsii_name="kinesisStreamSourceConfiguration")
    def kinesis_stream_source_configuration(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["KinesisStreamSourceConfigurationProperty"]]]:
        """``AWS::KinesisFirehose::DeliveryStream.KinesisStreamSourceConfiguration``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisfirehose-deliverystream.html#cfn-kinesisfirehose-deliverystream-kinesisstreamsourceconfiguration
        """
        return jsii.get(self, "kinesisStreamSourceConfiguration")

    @kinesis_stream_source_configuration.setter
    def kinesis_stream_source_configuration(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["KinesisStreamSourceConfigurationProperty"]]]):
        return jsii.set(self, "kinesisStreamSourceConfiguration", value)

    @property
    @jsii.member(jsii_name="redshiftDestinationConfiguration")
    def redshift_destination_configuration(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["RedshiftDestinationConfigurationProperty"]]]:
        """``AWS::KinesisFirehose::DeliveryStream.RedshiftDestinationConfiguration``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisfirehose-deliverystream.html#cfn-kinesisfirehose-deliverystream-redshiftdestinationconfiguration
        """
        return jsii.get(self, "redshiftDestinationConfiguration")

    @redshift_destination_configuration.setter
    def redshift_destination_configuration(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["RedshiftDestinationConfigurationProperty"]]]):
        return jsii.set(self, "redshiftDestinationConfiguration", value)

    @property
    @jsii.member(jsii_name="s3DestinationConfiguration")
    def s3_destination_configuration(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["S3DestinationConfigurationProperty"]]]:
        """``AWS::KinesisFirehose::DeliveryStream.S3DestinationConfiguration``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisfirehose-deliverystream.html#cfn-kinesisfirehose-deliverystream-s3destinationconfiguration
        """
        return jsii.get(self, "s3DestinationConfiguration")

    @s3_destination_configuration.setter
    def s3_destination_configuration(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["S3DestinationConfigurationProperty"]]]):
        return jsii.set(self, "s3DestinationConfiguration", value)

    @property
    @jsii.member(jsii_name="splunkDestinationConfiguration")
    def splunk_destination_configuration(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["SplunkDestinationConfigurationProperty"]]]:
        """``AWS::KinesisFirehose::DeliveryStream.SplunkDestinationConfiguration``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisfirehose-deliverystream.html#cfn-kinesisfirehose-deliverystream-splunkdestinationconfiguration
        """
        return jsii.get(self, "splunkDestinationConfiguration")

    @splunk_destination_configuration.setter
    def splunk_destination_configuration(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["SplunkDestinationConfigurationProperty"]]]):
        return jsii.set(self, "splunkDestinationConfiguration", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.BufferingHintsProperty", jsii_struct_bases=[], name_mapping={'interval_in_seconds': 'intervalInSeconds', 'size_in_m_bs': 'sizeInMBs'})
    class BufferingHintsProperty():
        def __init__(self, *, interval_in_seconds: jsii.Number, size_in_m_bs: jsii.Number):
            """
            :param interval_in_seconds: ``CfnDeliveryStream.BufferingHintsProperty.IntervalInSeconds``.
            :param size_in_m_bs: ``CfnDeliveryStream.BufferingHintsProperty.SizeInMBs``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-bufferinghints.html
            """
            self._values = {
                'interval_in_seconds': interval_in_seconds,
                'size_in_m_bs': size_in_m_bs,
            }

        @property
        def interval_in_seconds(self) -> jsii.Number:
            """``CfnDeliveryStream.BufferingHintsProperty.IntervalInSeconds``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-bufferinghints.html#cfn-kinesisfirehose-deliverystream-bufferinghints-intervalinseconds
            """
            return self._values.get('interval_in_seconds')

        @property
        def size_in_m_bs(self) -> jsii.Number:
            """``CfnDeliveryStream.BufferingHintsProperty.SizeInMBs``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-bufferinghints.html#cfn-kinesisfirehose-deliverystream-bufferinghints-sizeinmbs
            """
            return self._values.get('size_in_m_bs')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'BufferingHintsProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.CloudWatchLoggingOptionsProperty", jsii_struct_bases=[], name_mapping={'enabled': 'enabled', 'log_group_name': 'logGroupName', 'log_stream_name': 'logStreamName'})
    class CloudWatchLoggingOptionsProperty():
        def __init__(self, *, enabled: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, log_group_name: typing.Optional[str]=None, log_stream_name: typing.Optional[str]=None):
            """
            :param enabled: ``CfnDeliveryStream.CloudWatchLoggingOptionsProperty.Enabled``.
            :param log_group_name: ``CfnDeliveryStream.CloudWatchLoggingOptionsProperty.LogGroupName``.
            :param log_stream_name: ``CfnDeliveryStream.CloudWatchLoggingOptionsProperty.LogStreamName``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-cloudwatchloggingoptions.html
            """
            self._values = {
            }
            if enabled is not None: self._values["enabled"] = enabled
            if log_group_name is not None: self._values["log_group_name"] = log_group_name
            if log_stream_name is not None: self._values["log_stream_name"] = log_stream_name

        @property
        def enabled(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
            """``CfnDeliveryStream.CloudWatchLoggingOptionsProperty.Enabled``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-cloudwatchloggingoptions.html#cfn-kinesisfirehose-deliverystream-cloudwatchloggingoptions-enabled
            """
            return self._values.get('enabled')

        @property
        def log_group_name(self) -> typing.Optional[str]:
            """``CfnDeliveryStream.CloudWatchLoggingOptionsProperty.LogGroupName``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-cloudwatchloggingoptions.html#cfn-kinesisfirehose-deliverystream-cloudwatchloggingoptions-loggroupname
            """
            return self._values.get('log_group_name')

        @property
        def log_stream_name(self) -> typing.Optional[str]:
            """``CfnDeliveryStream.CloudWatchLoggingOptionsProperty.LogStreamName``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-cloudwatchloggingoptions.html#cfn-kinesisfirehose-deliverystream-cloudwatchloggingoptions-logstreamname
            """
            return self._values.get('log_stream_name')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'CloudWatchLoggingOptionsProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.CopyCommandProperty", jsii_struct_bases=[], name_mapping={'data_table_name': 'dataTableName', 'copy_options': 'copyOptions', 'data_table_columns': 'dataTableColumns'})
    class CopyCommandProperty():
        def __init__(self, *, data_table_name: str, copy_options: typing.Optional[str]=None, data_table_columns: typing.Optional[str]=None):
            """
            :param data_table_name: ``CfnDeliveryStream.CopyCommandProperty.DataTableName``.
            :param copy_options: ``CfnDeliveryStream.CopyCommandProperty.CopyOptions``.
            :param data_table_columns: ``CfnDeliveryStream.CopyCommandProperty.DataTableColumns``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-copycommand.html
            """
            self._values = {
                'data_table_name': data_table_name,
            }
            if copy_options is not None: self._values["copy_options"] = copy_options
            if data_table_columns is not None: self._values["data_table_columns"] = data_table_columns

        @property
        def data_table_name(self) -> str:
            """``CfnDeliveryStream.CopyCommandProperty.DataTableName``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-copycommand.html#cfn-kinesisfirehose-deliverystream-copycommand-datatablename
            """
            return self._values.get('data_table_name')

        @property
        def copy_options(self) -> typing.Optional[str]:
            """``CfnDeliveryStream.CopyCommandProperty.CopyOptions``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-copycommand.html#cfn-kinesisfirehose-deliverystream-copycommand-copyoptions
            """
            return self._values.get('copy_options')

        @property
        def data_table_columns(self) -> typing.Optional[str]:
            """``CfnDeliveryStream.CopyCommandProperty.DataTableColumns``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-copycommand.html#cfn-kinesisfirehose-deliverystream-copycommand-datatablecolumns
            """
            return self._values.get('data_table_columns')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'CopyCommandProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.DataFormatConversionConfigurationProperty", jsii_struct_bases=[], name_mapping={'enabled': 'enabled', 'input_format_configuration': 'inputFormatConfiguration', 'output_format_configuration': 'outputFormatConfiguration', 'schema_configuration': 'schemaConfiguration'})
    class DataFormatConversionConfigurationProperty():
        def __init__(self, *, enabled: typing.Union[bool, aws_cdk.core.IResolvable], input_format_configuration: typing.Union[aws_cdk.core.IResolvable, "CfnDeliveryStream.InputFormatConfigurationProperty"], output_format_configuration: typing.Union[aws_cdk.core.IResolvable, "CfnDeliveryStream.OutputFormatConfigurationProperty"], schema_configuration: typing.Union[aws_cdk.core.IResolvable, "CfnDeliveryStream.SchemaConfigurationProperty"]):
            """
            :param enabled: ``CfnDeliveryStream.DataFormatConversionConfigurationProperty.Enabled``.
            :param input_format_configuration: ``CfnDeliveryStream.DataFormatConversionConfigurationProperty.InputFormatConfiguration``.
            :param output_format_configuration: ``CfnDeliveryStream.DataFormatConversionConfigurationProperty.OutputFormatConfiguration``.
            :param schema_configuration: ``CfnDeliveryStream.DataFormatConversionConfigurationProperty.SchemaConfiguration``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-dataformatconversionconfiguration.html
            """
            self._values = {
                'enabled': enabled,
                'input_format_configuration': input_format_configuration,
                'output_format_configuration': output_format_configuration,
                'schema_configuration': schema_configuration,
            }

        @property
        def enabled(self) -> typing.Union[bool, aws_cdk.core.IResolvable]:
            """``CfnDeliveryStream.DataFormatConversionConfigurationProperty.Enabled``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-dataformatconversionconfiguration.html#cfn-kinesisfirehose-deliverystream-dataformatconversionconfiguration-enabled
            """
            return self._values.get('enabled')

        @property
        def input_format_configuration(self) -> typing.Union[aws_cdk.core.IResolvable, "CfnDeliveryStream.InputFormatConfigurationProperty"]:
            """``CfnDeliveryStream.DataFormatConversionConfigurationProperty.InputFormatConfiguration``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-dataformatconversionconfiguration.html#cfn-kinesisfirehose-deliverystream-dataformatconversionconfiguration-inputformatconfiguration
            """
            return self._values.get('input_format_configuration')

        @property
        def output_format_configuration(self) -> typing.Union[aws_cdk.core.IResolvable, "CfnDeliveryStream.OutputFormatConfigurationProperty"]:
            """``CfnDeliveryStream.DataFormatConversionConfigurationProperty.OutputFormatConfiguration``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-dataformatconversionconfiguration.html#cfn-kinesisfirehose-deliverystream-dataformatconversionconfiguration-outputformatconfiguration
            """
            return self._values.get('output_format_configuration')

        @property
        def schema_configuration(self) -> typing.Union[aws_cdk.core.IResolvable, "CfnDeliveryStream.SchemaConfigurationProperty"]:
            """``CfnDeliveryStream.DataFormatConversionConfigurationProperty.SchemaConfiguration``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-dataformatconversionconfiguration.html#cfn-kinesisfirehose-deliverystream-dataformatconversionconfiguration-schemaconfiguration
            """
            return self._values.get('schema_configuration')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'DataFormatConversionConfigurationProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.DeserializerProperty", jsii_struct_bases=[], name_mapping={'hive_json_ser_de': 'hiveJsonSerDe', 'open_x_json_ser_de': 'openXJsonSerDe'})
    class DeserializerProperty():
        def __init__(self, *, hive_json_ser_de: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnDeliveryStream.HiveJsonSerDeProperty"]]]=None, open_x_json_ser_de: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnDeliveryStream.OpenXJsonSerDeProperty"]]]=None):
            """
            :param hive_json_ser_de: ``CfnDeliveryStream.DeserializerProperty.HiveJsonSerDe``.
            :param open_x_json_ser_de: ``CfnDeliveryStream.DeserializerProperty.OpenXJsonSerDe``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-deserializer.html
            """
            self._values = {
            }
            if hive_json_ser_de is not None: self._values["hive_json_ser_de"] = hive_json_ser_de
            if open_x_json_ser_de is not None: self._values["open_x_json_ser_de"] = open_x_json_ser_de

        @property
        def hive_json_ser_de(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnDeliveryStream.HiveJsonSerDeProperty"]]]:
            """``CfnDeliveryStream.DeserializerProperty.HiveJsonSerDe``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-deserializer.html#cfn-kinesisfirehose-deliverystream-deserializer-hivejsonserde
            """
            return self._values.get('hive_json_ser_de')

        @property
        def open_x_json_ser_de(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnDeliveryStream.OpenXJsonSerDeProperty"]]]:
            """``CfnDeliveryStream.DeserializerProperty.OpenXJsonSerDe``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-deserializer.html#cfn-kinesisfirehose-deliverystream-deserializer-openxjsonserde
            """
            return self._values.get('open_x_json_ser_de')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'DeserializerProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.ElasticsearchBufferingHintsProperty", jsii_struct_bases=[], name_mapping={'interval_in_seconds': 'intervalInSeconds', 'size_in_m_bs': 'sizeInMBs'})
    class ElasticsearchBufferingHintsProperty():
        def __init__(self, *, interval_in_seconds: jsii.Number, size_in_m_bs: jsii.Number):
            """
            :param interval_in_seconds: ``CfnDeliveryStream.ElasticsearchBufferingHintsProperty.IntervalInSeconds``.
            :param size_in_m_bs: ``CfnDeliveryStream.ElasticsearchBufferingHintsProperty.SizeInMBs``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-elasticsearchbufferinghints.html
            """
            self._values = {
                'interval_in_seconds': interval_in_seconds,
                'size_in_m_bs': size_in_m_bs,
            }

        @property
        def interval_in_seconds(self) -> jsii.Number:
            """``CfnDeliveryStream.ElasticsearchBufferingHintsProperty.IntervalInSeconds``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-elasticsearchbufferinghints.html#cfn-kinesisfirehose-deliverystream-elasticsearchbufferinghints-intervalinseconds
            """
            return self._values.get('interval_in_seconds')

        @property
        def size_in_m_bs(self) -> jsii.Number:
            """``CfnDeliveryStream.ElasticsearchBufferingHintsProperty.SizeInMBs``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-elasticsearchbufferinghints.html#cfn-kinesisfirehose-deliverystream-elasticsearchbufferinghints-sizeinmbs
            """
            return self._values.get('size_in_m_bs')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'ElasticsearchBufferingHintsProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.ElasticsearchDestinationConfigurationProperty", jsii_struct_bases=[], name_mapping={'buffering_hints': 'bufferingHints', 'domain_arn': 'domainArn', 'index_name': 'indexName', 'index_rotation_period': 'indexRotationPeriod', 'retry_options': 'retryOptions', 'role_arn': 'roleArn', 's3_backup_mode': 's3BackupMode', 's3_configuration': 's3Configuration', 'type_name': 'typeName', 'cloud_watch_logging_options': 'cloudWatchLoggingOptions', 'processing_configuration': 'processingConfiguration'})
    class ElasticsearchDestinationConfigurationProperty():
        def __init__(self, *, buffering_hints: typing.Union[aws_cdk.core.IResolvable, "CfnDeliveryStream.ElasticsearchBufferingHintsProperty"], domain_arn: str, index_name: str, index_rotation_period: str, retry_options: typing.Union[aws_cdk.core.IResolvable, "CfnDeliveryStream.ElasticsearchRetryOptionsProperty"], role_arn: str, s3_backup_mode: str, s3_configuration: typing.Union[aws_cdk.core.IResolvable, "CfnDeliveryStream.S3DestinationConfigurationProperty"], type_name: str, cloud_watch_logging_options: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnDeliveryStream.CloudWatchLoggingOptionsProperty"]]]=None, processing_configuration: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnDeliveryStream.ProcessingConfigurationProperty"]]]=None):
            """
            :param buffering_hints: ``CfnDeliveryStream.ElasticsearchDestinationConfigurationProperty.BufferingHints``.
            :param domain_arn: ``CfnDeliveryStream.ElasticsearchDestinationConfigurationProperty.DomainARN``.
            :param index_name: ``CfnDeliveryStream.ElasticsearchDestinationConfigurationProperty.IndexName``.
            :param index_rotation_period: ``CfnDeliveryStream.ElasticsearchDestinationConfigurationProperty.IndexRotationPeriod``.
            :param retry_options: ``CfnDeliveryStream.ElasticsearchDestinationConfigurationProperty.RetryOptions``.
            :param role_arn: ``CfnDeliveryStream.ElasticsearchDestinationConfigurationProperty.RoleARN``.
            :param s3_backup_mode: ``CfnDeliveryStream.ElasticsearchDestinationConfigurationProperty.S3BackupMode``.
            :param s3_configuration: ``CfnDeliveryStream.ElasticsearchDestinationConfigurationProperty.S3Configuration``.
            :param type_name: ``CfnDeliveryStream.ElasticsearchDestinationConfigurationProperty.TypeName``.
            :param cloud_watch_logging_options: ``CfnDeliveryStream.ElasticsearchDestinationConfigurationProperty.CloudWatchLoggingOptions``.
            :param processing_configuration: ``CfnDeliveryStream.ElasticsearchDestinationConfigurationProperty.ProcessingConfiguration``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration.html
            """
            self._values = {
                'buffering_hints': buffering_hints,
                'domain_arn': domain_arn,
                'index_name': index_name,
                'index_rotation_period': index_rotation_period,
                'retry_options': retry_options,
                'role_arn': role_arn,
                's3_backup_mode': s3_backup_mode,
                's3_configuration': s3_configuration,
                'type_name': type_name,
            }
            if cloud_watch_logging_options is not None: self._values["cloud_watch_logging_options"] = cloud_watch_logging_options
            if processing_configuration is not None: self._values["processing_configuration"] = processing_configuration

        @property
        def buffering_hints(self) -> typing.Union[aws_cdk.core.IResolvable, "CfnDeliveryStream.ElasticsearchBufferingHintsProperty"]:
            """``CfnDeliveryStream.ElasticsearchDestinationConfigurationProperty.BufferingHints``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration-bufferinghints
            """
            return self._values.get('buffering_hints')

        @property
        def domain_arn(self) -> str:
            """``CfnDeliveryStream.ElasticsearchDestinationConfigurationProperty.DomainARN``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration-domainarn
            """
            return self._values.get('domain_arn')

        @property
        def index_name(self) -> str:
            """``CfnDeliveryStream.ElasticsearchDestinationConfigurationProperty.IndexName``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration-indexname
            """
            return self._values.get('index_name')

        @property
        def index_rotation_period(self) -> str:
            """``CfnDeliveryStream.ElasticsearchDestinationConfigurationProperty.IndexRotationPeriod``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration-indexrotationperiod
            """
            return self._values.get('index_rotation_period')

        @property
        def retry_options(self) -> typing.Union[aws_cdk.core.IResolvable, "CfnDeliveryStream.ElasticsearchRetryOptionsProperty"]:
            """``CfnDeliveryStream.ElasticsearchDestinationConfigurationProperty.RetryOptions``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration-retryoptions
            """
            return self._values.get('retry_options')

        @property
        def role_arn(self) -> str:
            """``CfnDeliveryStream.ElasticsearchDestinationConfigurationProperty.RoleARN``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration-rolearn
            """
            return self._values.get('role_arn')

        @property
        def s3_backup_mode(self) -> str:
            """``CfnDeliveryStream.ElasticsearchDestinationConfigurationProperty.S3BackupMode``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration-s3backupmode
            """
            return self._values.get('s3_backup_mode')

        @property
        def s3_configuration(self) -> typing.Union[aws_cdk.core.IResolvable, "CfnDeliveryStream.S3DestinationConfigurationProperty"]:
            """``CfnDeliveryStream.ElasticsearchDestinationConfigurationProperty.S3Configuration``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration-s3configuration
            """
            return self._values.get('s3_configuration')

        @property
        def type_name(self) -> str:
            """``CfnDeliveryStream.ElasticsearchDestinationConfigurationProperty.TypeName``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration-typename
            """
            return self._values.get('type_name')

        @property
        def cloud_watch_logging_options(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnDeliveryStream.CloudWatchLoggingOptionsProperty"]]]:
            """``CfnDeliveryStream.ElasticsearchDestinationConfigurationProperty.CloudWatchLoggingOptions``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration-cloudwatchloggingoptions
            """
            return self._values.get('cloud_watch_logging_options')

        @property
        def processing_configuration(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnDeliveryStream.ProcessingConfigurationProperty"]]]:
            """``CfnDeliveryStream.ElasticsearchDestinationConfigurationProperty.ProcessingConfiguration``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration-processingconfiguration
            """
            return self._values.get('processing_configuration')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'ElasticsearchDestinationConfigurationProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.ElasticsearchRetryOptionsProperty", jsii_struct_bases=[], name_mapping={'duration_in_seconds': 'durationInSeconds'})
    class ElasticsearchRetryOptionsProperty():
        def __init__(self, *, duration_in_seconds: jsii.Number):
            """
            :param duration_in_seconds: ``CfnDeliveryStream.ElasticsearchRetryOptionsProperty.DurationInSeconds``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-elasticsearchretryoptions.html
            """
            self._values = {
                'duration_in_seconds': duration_in_seconds,
            }

        @property
        def duration_in_seconds(self) -> jsii.Number:
            """``CfnDeliveryStream.ElasticsearchRetryOptionsProperty.DurationInSeconds``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-elasticsearchretryoptions.html#cfn-kinesisfirehose-deliverystream-elasticsearchretryoptions-durationinseconds
            """
            return self._values.get('duration_in_seconds')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'ElasticsearchRetryOptionsProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.EncryptionConfigurationProperty", jsii_struct_bases=[], name_mapping={'kms_encryption_config': 'kmsEncryptionConfig', 'no_encryption_config': 'noEncryptionConfig'})
    class EncryptionConfigurationProperty():
        def __init__(self, *, kms_encryption_config: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnDeliveryStream.KMSEncryptionConfigProperty"]]]=None, no_encryption_config: typing.Optional[str]=None):
            """
            :param kms_encryption_config: ``CfnDeliveryStream.EncryptionConfigurationProperty.KMSEncryptionConfig``.
            :param no_encryption_config: ``CfnDeliveryStream.EncryptionConfigurationProperty.NoEncryptionConfig``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-encryptionconfiguration.html
            """
            self._values = {
            }
            if kms_encryption_config is not None: self._values["kms_encryption_config"] = kms_encryption_config
            if no_encryption_config is not None: self._values["no_encryption_config"] = no_encryption_config

        @property
        def kms_encryption_config(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnDeliveryStream.KMSEncryptionConfigProperty"]]]:
            """``CfnDeliveryStream.EncryptionConfigurationProperty.KMSEncryptionConfig``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-encryptionconfiguration.html#cfn-kinesisfirehose-deliverystream-encryptionconfiguration-kmsencryptionconfig
            """
            return self._values.get('kms_encryption_config')

        @property
        def no_encryption_config(self) -> typing.Optional[str]:
            """``CfnDeliveryStream.EncryptionConfigurationProperty.NoEncryptionConfig``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-encryptionconfiguration.html#cfn-kinesisfirehose-deliverystream-encryptionconfiguration-noencryptionconfig
            """
            return self._values.get('no_encryption_config')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'EncryptionConfigurationProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.ExtendedS3DestinationConfigurationProperty", jsii_struct_bases=[], name_mapping={'bucket_arn': 'bucketArn', 'buffering_hints': 'bufferingHints', 'compression_format': 'compressionFormat', 'role_arn': 'roleArn', 'cloud_watch_logging_options': 'cloudWatchLoggingOptions', 'data_format_conversion_configuration': 'dataFormatConversionConfiguration', 'encryption_configuration': 'encryptionConfiguration', 'error_output_prefix': 'errorOutputPrefix', 'prefix': 'prefix', 'processing_configuration': 'processingConfiguration', 's3_backup_configuration': 's3BackupConfiguration', 's3_backup_mode': 's3BackupMode'})
    class ExtendedS3DestinationConfigurationProperty():
        def __init__(self, *, bucket_arn: str, buffering_hints: typing.Union[aws_cdk.core.IResolvable, "CfnDeliveryStream.BufferingHintsProperty"], compression_format: str, role_arn: str, cloud_watch_logging_options: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnDeliveryStream.CloudWatchLoggingOptionsProperty"]]]=None, data_format_conversion_configuration: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnDeliveryStream.DataFormatConversionConfigurationProperty"]]]=None, encryption_configuration: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnDeliveryStream.EncryptionConfigurationProperty"]]]=None, error_output_prefix: typing.Optional[str]=None, prefix: typing.Optional[str]=None, processing_configuration: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnDeliveryStream.ProcessingConfigurationProperty"]]]=None, s3_backup_configuration: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnDeliveryStream.S3DestinationConfigurationProperty"]]]=None, s3_backup_mode: typing.Optional[str]=None):
            """
            :param bucket_arn: ``CfnDeliveryStream.ExtendedS3DestinationConfigurationProperty.BucketARN``.
            :param buffering_hints: ``CfnDeliveryStream.ExtendedS3DestinationConfigurationProperty.BufferingHints``.
            :param compression_format: ``CfnDeliveryStream.ExtendedS3DestinationConfigurationProperty.CompressionFormat``.
            :param role_arn: ``CfnDeliveryStream.ExtendedS3DestinationConfigurationProperty.RoleARN``.
            :param cloud_watch_logging_options: ``CfnDeliveryStream.ExtendedS3DestinationConfigurationProperty.CloudWatchLoggingOptions``.
            :param data_format_conversion_configuration: ``CfnDeliveryStream.ExtendedS3DestinationConfigurationProperty.DataFormatConversionConfiguration``.
            :param encryption_configuration: ``CfnDeliveryStream.ExtendedS3DestinationConfigurationProperty.EncryptionConfiguration``.
            :param error_output_prefix: ``CfnDeliveryStream.ExtendedS3DestinationConfigurationProperty.ErrorOutputPrefix``.
            :param prefix: ``CfnDeliveryStream.ExtendedS3DestinationConfigurationProperty.Prefix``.
            :param processing_configuration: ``CfnDeliveryStream.ExtendedS3DestinationConfigurationProperty.ProcessingConfiguration``.
            :param s3_backup_configuration: ``CfnDeliveryStream.ExtendedS3DestinationConfigurationProperty.S3BackupConfiguration``.
            :param s3_backup_mode: ``CfnDeliveryStream.ExtendedS3DestinationConfigurationProperty.S3BackupMode``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-extendeds3destinationconfiguration.html
            """
            self._values = {
                'bucket_arn': bucket_arn,
                'buffering_hints': buffering_hints,
                'compression_format': compression_format,
                'role_arn': role_arn,
            }
            if cloud_watch_logging_options is not None: self._values["cloud_watch_logging_options"] = cloud_watch_logging_options
            if data_format_conversion_configuration is not None: self._values["data_format_conversion_configuration"] = data_format_conversion_configuration
            if encryption_configuration is not None: self._values["encryption_configuration"] = encryption_configuration
            if error_output_prefix is not None: self._values["error_output_prefix"] = error_output_prefix
            if prefix is not None: self._values["prefix"] = prefix
            if processing_configuration is not None: self._values["processing_configuration"] = processing_configuration
            if s3_backup_configuration is not None: self._values["s3_backup_configuration"] = s3_backup_configuration
            if s3_backup_mode is not None: self._values["s3_backup_mode"] = s3_backup_mode

        @property
        def bucket_arn(self) -> str:
            """``CfnDeliveryStream.ExtendedS3DestinationConfigurationProperty.BucketARN``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-extendeds3destinationconfiguration.html#cfn-kinesisfirehose-deliverystream-extendeds3destinationconfiguration-bucketarn
            """
            return self._values.get('bucket_arn')

        @property
        def buffering_hints(self) -> typing.Union[aws_cdk.core.IResolvable, "CfnDeliveryStream.BufferingHintsProperty"]:
            """``CfnDeliveryStream.ExtendedS3DestinationConfigurationProperty.BufferingHints``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-extendeds3destinationconfiguration.html#cfn-kinesisfirehose-deliverystream-extendeds3destinationconfiguration-bufferinghints
            """
            return self._values.get('buffering_hints')

        @property
        def compression_format(self) -> str:
            """``CfnDeliveryStream.ExtendedS3DestinationConfigurationProperty.CompressionFormat``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-extendeds3destinationconfiguration.html#cfn-kinesisfirehose-deliverystream-extendeds3destinationconfiguration-compressionformat
            """
            return self._values.get('compression_format')

        @property
        def role_arn(self) -> str:
            """``CfnDeliveryStream.ExtendedS3DestinationConfigurationProperty.RoleARN``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-extendeds3destinationconfiguration.html#cfn-kinesisfirehose-deliverystream-extendeds3destinationconfiguration-rolearn
            """
            return self._values.get('role_arn')

        @property
        def cloud_watch_logging_options(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnDeliveryStream.CloudWatchLoggingOptionsProperty"]]]:
            """``CfnDeliveryStream.ExtendedS3DestinationConfigurationProperty.CloudWatchLoggingOptions``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-extendeds3destinationconfiguration.html#cfn-kinesisfirehose-deliverystream-extendeds3destinationconfiguration-cloudwatchloggingoptions
            """
            return self._values.get('cloud_watch_logging_options')

        @property
        def data_format_conversion_configuration(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnDeliveryStream.DataFormatConversionConfigurationProperty"]]]:
            """``CfnDeliveryStream.ExtendedS3DestinationConfigurationProperty.DataFormatConversionConfiguration``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-extendeds3destinationconfiguration.html#cfn-kinesisfirehose-deliverystream-extendeds3destinationconfiguration-dataformatconversionconfiguration
            """
            return self._values.get('data_format_conversion_configuration')

        @property
        def encryption_configuration(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnDeliveryStream.EncryptionConfigurationProperty"]]]:
            """``CfnDeliveryStream.ExtendedS3DestinationConfigurationProperty.EncryptionConfiguration``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-extendeds3destinationconfiguration.html#cfn-kinesisfirehose-deliverystream-extendeds3destinationconfiguration-encryptionconfiguration
            """
            return self._values.get('encryption_configuration')

        @property
        def error_output_prefix(self) -> typing.Optional[str]:
            """``CfnDeliveryStream.ExtendedS3DestinationConfigurationProperty.ErrorOutputPrefix``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-extendeds3destinationconfiguration.html#cfn-kinesisfirehose-deliverystream-extendeds3destinationconfiguration-erroroutputprefix
            """
            return self._values.get('error_output_prefix')

        @property
        def prefix(self) -> typing.Optional[str]:
            """``CfnDeliveryStream.ExtendedS3DestinationConfigurationProperty.Prefix``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-extendeds3destinationconfiguration.html#cfn-kinesisfirehose-deliverystream-extendeds3destinationconfiguration-prefix
            """
            return self._values.get('prefix')

        @property
        def processing_configuration(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnDeliveryStream.ProcessingConfigurationProperty"]]]:
            """``CfnDeliveryStream.ExtendedS3DestinationConfigurationProperty.ProcessingConfiguration``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-extendeds3destinationconfiguration.html#cfn-kinesisfirehose-deliverystream-extendeds3destinationconfiguration-processingconfiguration
            """
            return self._values.get('processing_configuration')

        @property
        def s3_backup_configuration(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnDeliveryStream.S3DestinationConfigurationProperty"]]]:
            """``CfnDeliveryStream.ExtendedS3DestinationConfigurationProperty.S3BackupConfiguration``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-extendeds3destinationconfiguration.html#cfn-kinesisfirehose-deliverystream-extendeds3destinationconfiguration-s3backupconfiguration
            """
            return self._values.get('s3_backup_configuration')

        @property
        def s3_backup_mode(self) -> typing.Optional[str]:
            """``CfnDeliveryStream.ExtendedS3DestinationConfigurationProperty.S3BackupMode``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-extendeds3destinationconfiguration.html#cfn-kinesisfirehose-deliverystream-extendeds3destinationconfiguration-s3backupmode
            """
            return self._values.get('s3_backup_mode')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'ExtendedS3DestinationConfigurationProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.HiveJsonSerDeProperty", jsii_struct_bases=[], name_mapping={'timestamp_formats': 'timestampFormats'})
    class HiveJsonSerDeProperty():
        def __init__(self, *, timestamp_formats: typing.Optional[typing.List[str]]=None):
            """
            :param timestamp_formats: ``CfnDeliveryStream.HiveJsonSerDeProperty.TimestampFormats``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-hivejsonserde.html
            """
            self._values = {
            }
            if timestamp_formats is not None: self._values["timestamp_formats"] = timestamp_formats

        @property
        def timestamp_formats(self) -> typing.Optional[typing.List[str]]:
            """``CfnDeliveryStream.HiveJsonSerDeProperty.TimestampFormats``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-hivejsonserde.html#cfn-kinesisfirehose-deliverystream-hivejsonserde-timestampformats
            """
            return self._values.get('timestamp_formats')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'HiveJsonSerDeProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.InputFormatConfigurationProperty", jsii_struct_bases=[], name_mapping={'deserializer': 'deserializer'})
    class InputFormatConfigurationProperty():
        def __init__(self, *, deserializer: typing.Union[aws_cdk.core.IResolvable, "CfnDeliveryStream.DeserializerProperty"]):
            """
            :param deserializer: ``CfnDeliveryStream.InputFormatConfigurationProperty.Deserializer``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-inputformatconfiguration.html
            """
            self._values = {
                'deserializer': deserializer,
            }

        @property
        def deserializer(self) -> typing.Union[aws_cdk.core.IResolvable, "CfnDeliveryStream.DeserializerProperty"]:
            """``CfnDeliveryStream.InputFormatConfigurationProperty.Deserializer``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-inputformatconfiguration.html#cfn-kinesisfirehose-deliverystream-inputformatconfiguration-deserializer
            """
            return self._values.get('deserializer')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'InputFormatConfigurationProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.KMSEncryptionConfigProperty", jsii_struct_bases=[], name_mapping={'awskms_key_arn': 'awskmsKeyArn'})
    class KMSEncryptionConfigProperty():
        def __init__(self, *, awskms_key_arn: str):
            """
            :param awskms_key_arn: ``CfnDeliveryStream.KMSEncryptionConfigProperty.AWSKMSKeyARN``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-kmsencryptionconfig.html
            """
            self._values = {
                'awskms_key_arn': awskms_key_arn,
            }

        @property
        def awskms_key_arn(self) -> str:
            """``CfnDeliveryStream.KMSEncryptionConfigProperty.AWSKMSKeyARN``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-kmsencryptionconfig.html#cfn-kinesisfirehose-deliverystream-kmsencryptionconfig-awskmskeyarn
            """
            return self._values.get('awskms_key_arn')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'KMSEncryptionConfigProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.KinesisStreamSourceConfigurationProperty", jsii_struct_bases=[], name_mapping={'kinesis_stream_arn': 'kinesisStreamArn', 'role_arn': 'roleArn'})
    class KinesisStreamSourceConfigurationProperty():
        def __init__(self, *, kinesis_stream_arn: str, role_arn: str):
            """
            :param kinesis_stream_arn: ``CfnDeliveryStream.KinesisStreamSourceConfigurationProperty.KinesisStreamARN``.
            :param role_arn: ``CfnDeliveryStream.KinesisStreamSourceConfigurationProperty.RoleARN``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-kinesisstreamsourceconfiguration.html
            """
            self._values = {
                'kinesis_stream_arn': kinesis_stream_arn,
                'role_arn': role_arn,
            }

        @property
        def kinesis_stream_arn(self) -> str:
            """``CfnDeliveryStream.KinesisStreamSourceConfigurationProperty.KinesisStreamARN``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-kinesisstreamsourceconfiguration.html#cfn-kinesisfirehose-deliverystream-kinesisstreamsourceconfiguration-kinesisstreamarn
            """
            return self._values.get('kinesis_stream_arn')

        @property
        def role_arn(self) -> str:
            """``CfnDeliveryStream.KinesisStreamSourceConfigurationProperty.RoleARN``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-kinesisstreamsourceconfiguration.html#cfn-kinesisfirehose-deliverystream-kinesisstreamsourceconfiguration-rolearn
            """
            return self._values.get('role_arn')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'KinesisStreamSourceConfigurationProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.OpenXJsonSerDeProperty", jsii_struct_bases=[], name_mapping={'case_insensitive': 'caseInsensitive', 'column_to_json_key_mappings': 'columnToJsonKeyMappings', 'convert_dots_in_json_keys_to_underscores': 'convertDotsInJsonKeysToUnderscores'})
    class OpenXJsonSerDeProperty():
        def __init__(self, *, case_insensitive: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, column_to_json_key_mappings: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.Mapping[str,str]]]]=None, convert_dots_in_json_keys_to_underscores: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None):
            """
            :param case_insensitive: ``CfnDeliveryStream.OpenXJsonSerDeProperty.CaseInsensitive``.
            :param column_to_json_key_mappings: ``CfnDeliveryStream.OpenXJsonSerDeProperty.ColumnToJsonKeyMappings``.
            :param convert_dots_in_json_keys_to_underscores: ``CfnDeliveryStream.OpenXJsonSerDeProperty.ConvertDotsInJsonKeysToUnderscores``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-openxjsonserde.html
            """
            self._values = {
            }
            if case_insensitive is not None: self._values["case_insensitive"] = case_insensitive
            if column_to_json_key_mappings is not None: self._values["column_to_json_key_mappings"] = column_to_json_key_mappings
            if convert_dots_in_json_keys_to_underscores is not None: self._values["convert_dots_in_json_keys_to_underscores"] = convert_dots_in_json_keys_to_underscores

        @property
        def case_insensitive(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
            """``CfnDeliveryStream.OpenXJsonSerDeProperty.CaseInsensitive``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-openxjsonserde.html#cfn-kinesisfirehose-deliverystream-openxjsonserde-caseinsensitive
            """
            return self._values.get('case_insensitive')

        @property
        def column_to_json_key_mappings(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.Mapping[str,str]]]]:
            """``CfnDeliveryStream.OpenXJsonSerDeProperty.ColumnToJsonKeyMappings``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-openxjsonserde.html#cfn-kinesisfirehose-deliverystream-openxjsonserde-columntojsonkeymappings
            """
            return self._values.get('column_to_json_key_mappings')

        @property
        def convert_dots_in_json_keys_to_underscores(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
            """``CfnDeliveryStream.OpenXJsonSerDeProperty.ConvertDotsInJsonKeysToUnderscores``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-openxjsonserde.html#cfn-kinesisfirehose-deliverystream-openxjsonserde-convertdotsinjsonkeystounderscores
            """
            return self._values.get('convert_dots_in_json_keys_to_underscores')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'OpenXJsonSerDeProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.OrcSerDeProperty", jsii_struct_bases=[], name_mapping={'block_size_bytes': 'blockSizeBytes', 'bloom_filter_columns': 'bloomFilterColumns', 'bloom_filter_false_positive_probability': 'bloomFilterFalsePositiveProbability', 'compression': 'compression', 'dictionary_key_threshold': 'dictionaryKeyThreshold', 'enable_padding': 'enablePadding', 'format_version': 'formatVersion', 'padding_tolerance': 'paddingTolerance', 'row_index_stride': 'rowIndexStride', 'stripe_size_bytes': 'stripeSizeBytes'})
    class OrcSerDeProperty():
        def __init__(self, *, block_size_bytes: typing.Optional[jsii.Number]=None, bloom_filter_columns: typing.Optional[typing.List[str]]=None, bloom_filter_false_positive_probability: typing.Optional[jsii.Number]=None, compression: typing.Optional[str]=None, dictionary_key_threshold: typing.Optional[jsii.Number]=None, enable_padding: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, format_version: typing.Optional[str]=None, padding_tolerance: typing.Optional[jsii.Number]=None, row_index_stride: typing.Optional[jsii.Number]=None, stripe_size_bytes: typing.Optional[jsii.Number]=None):
            """
            :param block_size_bytes: ``CfnDeliveryStream.OrcSerDeProperty.BlockSizeBytes``.
            :param bloom_filter_columns: ``CfnDeliveryStream.OrcSerDeProperty.BloomFilterColumns``.
            :param bloom_filter_false_positive_probability: ``CfnDeliveryStream.OrcSerDeProperty.BloomFilterFalsePositiveProbability``.
            :param compression: ``CfnDeliveryStream.OrcSerDeProperty.Compression``.
            :param dictionary_key_threshold: ``CfnDeliveryStream.OrcSerDeProperty.DictionaryKeyThreshold``.
            :param enable_padding: ``CfnDeliveryStream.OrcSerDeProperty.EnablePadding``.
            :param format_version: ``CfnDeliveryStream.OrcSerDeProperty.FormatVersion``.
            :param padding_tolerance: ``CfnDeliveryStream.OrcSerDeProperty.PaddingTolerance``.
            :param row_index_stride: ``CfnDeliveryStream.OrcSerDeProperty.RowIndexStride``.
            :param stripe_size_bytes: ``CfnDeliveryStream.OrcSerDeProperty.StripeSizeBytes``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-orcserde.html
            """
            self._values = {
            }
            if block_size_bytes is not None: self._values["block_size_bytes"] = block_size_bytes
            if bloom_filter_columns is not None: self._values["bloom_filter_columns"] = bloom_filter_columns
            if bloom_filter_false_positive_probability is not None: self._values["bloom_filter_false_positive_probability"] = bloom_filter_false_positive_probability
            if compression is not None: self._values["compression"] = compression
            if dictionary_key_threshold is not None: self._values["dictionary_key_threshold"] = dictionary_key_threshold
            if enable_padding is not None: self._values["enable_padding"] = enable_padding
            if format_version is not None: self._values["format_version"] = format_version
            if padding_tolerance is not None: self._values["padding_tolerance"] = padding_tolerance
            if row_index_stride is not None: self._values["row_index_stride"] = row_index_stride
            if stripe_size_bytes is not None: self._values["stripe_size_bytes"] = stripe_size_bytes

        @property
        def block_size_bytes(self) -> typing.Optional[jsii.Number]:
            """``CfnDeliveryStream.OrcSerDeProperty.BlockSizeBytes``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-orcserde.html#cfn-kinesisfirehose-deliverystream-orcserde-blocksizebytes
            """
            return self._values.get('block_size_bytes')

        @property
        def bloom_filter_columns(self) -> typing.Optional[typing.List[str]]:
            """``CfnDeliveryStream.OrcSerDeProperty.BloomFilterColumns``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-orcserde.html#cfn-kinesisfirehose-deliverystream-orcserde-bloomfiltercolumns
            """
            return self._values.get('bloom_filter_columns')

        @property
        def bloom_filter_false_positive_probability(self) -> typing.Optional[jsii.Number]:
            """``CfnDeliveryStream.OrcSerDeProperty.BloomFilterFalsePositiveProbability``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-orcserde.html#cfn-kinesisfirehose-deliverystream-orcserde-bloomfilterfalsepositiveprobability
            """
            return self._values.get('bloom_filter_false_positive_probability')

        @property
        def compression(self) -> typing.Optional[str]:
            """``CfnDeliveryStream.OrcSerDeProperty.Compression``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-orcserde.html#cfn-kinesisfirehose-deliverystream-orcserde-compression
            """
            return self._values.get('compression')

        @property
        def dictionary_key_threshold(self) -> typing.Optional[jsii.Number]:
            """``CfnDeliveryStream.OrcSerDeProperty.DictionaryKeyThreshold``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-orcserde.html#cfn-kinesisfirehose-deliverystream-orcserde-dictionarykeythreshold
            """
            return self._values.get('dictionary_key_threshold')

        @property
        def enable_padding(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
            """``CfnDeliveryStream.OrcSerDeProperty.EnablePadding``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-orcserde.html#cfn-kinesisfirehose-deliverystream-orcserde-enablepadding
            """
            return self._values.get('enable_padding')

        @property
        def format_version(self) -> typing.Optional[str]:
            """``CfnDeliveryStream.OrcSerDeProperty.FormatVersion``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-orcserde.html#cfn-kinesisfirehose-deliverystream-orcserde-formatversion
            """
            return self._values.get('format_version')

        @property
        def padding_tolerance(self) -> typing.Optional[jsii.Number]:
            """``CfnDeliveryStream.OrcSerDeProperty.PaddingTolerance``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-orcserde.html#cfn-kinesisfirehose-deliverystream-orcserde-paddingtolerance
            """
            return self._values.get('padding_tolerance')

        @property
        def row_index_stride(self) -> typing.Optional[jsii.Number]:
            """``CfnDeliveryStream.OrcSerDeProperty.RowIndexStride``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-orcserde.html#cfn-kinesisfirehose-deliverystream-orcserde-rowindexstride
            """
            return self._values.get('row_index_stride')

        @property
        def stripe_size_bytes(self) -> typing.Optional[jsii.Number]:
            """``CfnDeliveryStream.OrcSerDeProperty.StripeSizeBytes``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-orcserde.html#cfn-kinesisfirehose-deliverystream-orcserde-stripesizebytes
            """
            return self._values.get('stripe_size_bytes')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'OrcSerDeProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.OutputFormatConfigurationProperty", jsii_struct_bases=[], name_mapping={'serializer': 'serializer'})
    class OutputFormatConfigurationProperty():
        def __init__(self, *, serializer: typing.Union[aws_cdk.core.IResolvable, "CfnDeliveryStream.SerializerProperty"]):
            """
            :param serializer: ``CfnDeliveryStream.OutputFormatConfigurationProperty.Serializer``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-outputformatconfiguration.html
            """
            self._values = {
                'serializer': serializer,
            }

        @property
        def serializer(self) -> typing.Union[aws_cdk.core.IResolvable, "CfnDeliveryStream.SerializerProperty"]:
            """``CfnDeliveryStream.OutputFormatConfigurationProperty.Serializer``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-outputformatconfiguration.html#cfn-kinesisfirehose-deliverystream-outputformatconfiguration-serializer
            """
            return self._values.get('serializer')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'OutputFormatConfigurationProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.ParquetSerDeProperty", jsii_struct_bases=[], name_mapping={'block_size_bytes': 'blockSizeBytes', 'compression': 'compression', 'enable_dictionary_compression': 'enableDictionaryCompression', 'max_padding_bytes': 'maxPaddingBytes', 'page_size_bytes': 'pageSizeBytes', 'writer_version': 'writerVersion'})
    class ParquetSerDeProperty():
        def __init__(self, *, block_size_bytes: typing.Optional[jsii.Number]=None, compression: typing.Optional[str]=None, enable_dictionary_compression: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, max_padding_bytes: typing.Optional[jsii.Number]=None, page_size_bytes: typing.Optional[jsii.Number]=None, writer_version: typing.Optional[str]=None):
            """
            :param block_size_bytes: ``CfnDeliveryStream.ParquetSerDeProperty.BlockSizeBytes``.
            :param compression: ``CfnDeliveryStream.ParquetSerDeProperty.Compression``.
            :param enable_dictionary_compression: ``CfnDeliveryStream.ParquetSerDeProperty.EnableDictionaryCompression``.
            :param max_padding_bytes: ``CfnDeliveryStream.ParquetSerDeProperty.MaxPaddingBytes``.
            :param page_size_bytes: ``CfnDeliveryStream.ParquetSerDeProperty.PageSizeBytes``.
            :param writer_version: ``CfnDeliveryStream.ParquetSerDeProperty.WriterVersion``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-parquetserde.html
            """
            self._values = {
            }
            if block_size_bytes is not None: self._values["block_size_bytes"] = block_size_bytes
            if compression is not None: self._values["compression"] = compression
            if enable_dictionary_compression is not None: self._values["enable_dictionary_compression"] = enable_dictionary_compression
            if max_padding_bytes is not None: self._values["max_padding_bytes"] = max_padding_bytes
            if page_size_bytes is not None: self._values["page_size_bytes"] = page_size_bytes
            if writer_version is not None: self._values["writer_version"] = writer_version

        @property
        def block_size_bytes(self) -> typing.Optional[jsii.Number]:
            """``CfnDeliveryStream.ParquetSerDeProperty.BlockSizeBytes``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-parquetserde.html#cfn-kinesisfirehose-deliverystream-parquetserde-blocksizebytes
            """
            return self._values.get('block_size_bytes')

        @property
        def compression(self) -> typing.Optional[str]:
            """``CfnDeliveryStream.ParquetSerDeProperty.Compression``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-parquetserde.html#cfn-kinesisfirehose-deliverystream-parquetserde-compression
            """
            return self._values.get('compression')

        @property
        def enable_dictionary_compression(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
            """``CfnDeliveryStream.ParquetSerDeProperty.EnableDictionaryCompression``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-parquetserde.html#cfn-kinesisfirehose-deliverystream-parquetserde-enabledictionarycompression
            """
            return self._values.get('enable_dictionary_compression')

        @property
        def max_padding_bytes(self) -> typing.Optional[jsii.Number]:
            """``CfnDeliveryStream.ParquetSerDeProperty.MaxPaddingBytes``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-parquetserde.html#cfn-kinesisfirehose-deliverystream-parquetserde-maxpaddingbytes
            """
            return self._values.get('max_padding_bytes')

        @property
        def page_size_bytes(self) -> typing.Optional[jsii.Number]:
            """``CfnDeliveryStream.ParquetSerDeProperty.PageSizeBytes``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-parquetserde.html#cfn-kinesisfirehose-deliverystream-parquetserde-pagesizebytes
            """
            return self._values.get('page_size_bytes')

        @property
        def writer_version(self) -> typing.Optional[str]:
            """``CfnDeliveryStream.ParquetSerDeProperty.WriterVersion``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-parquetserde.html#cfn-kinesisfirehose-deliverystream-parquetserde-writerversion
            """
            return self._values.get('writer_version')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'ParquetSerDeProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.ProcessingConfigurationProperty", jsii_struct_bases=[], name_mapping={'enabled': 'enabled', 'processors': 'processors'})
    class ProcessingConfigurationProperty():
        def __init__(self, *, enabled: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, processors: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnDeliveryStream.ProcessorProperty"]]]]]=None):
            """
            :param enabled: ``CfnDeliveryStream.ProcessingConfigurationProperty.Enabled``.
            :param processors: ``CfnDeliveryStream.ProcessingConfigurationProperty.Processors``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-processingconfiguration.html
            """
            self._values = {
            }
            if enabled is not None: self._values["enabled"] = enabled
            if processors is not None: self._values["processors"] = processors

        @property
        def enabled(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
            """``CfnDeliveryStream.ProcessingConfigurationProperty.Enabled``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-processingconfiguration.html#cfn-kinesisfirehose-deliverystream-processingconfiguration-enabled
            """
            return self._values.get('enabled')

        @property
        def processors(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnDeliveryStream.ProcessorProperty"]]]]]:
            """``CfnDeliveryStream.ProcessingConfigurationProperty.Processors``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-processingconfiguration.html#cfn-kinesisfirehose-deliverystream-processingconfiguration-processors
            """
            return self._values.get('processors')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'ProcessingConfigurationProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.ProcessorParameterProperty", jsii_struct_bases=[], name_mapping={'parameter_name': 'parameterName', 'parameter_value': 'parameterValue'})
    class ProcessorParameterProperty():
        def __init__(self, *, parameter_name: str, parameter_value: str):
            """
            :param parameter_name: ``CfnDeliveryStream.ProcessorParameterProperty.ParameterName``.
            :param parameter_value: ``CfnDeliveryStream.ProcessorParameterProperty.ParameterValue``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-processorparameter.html
            """
            self._values = {
                'parameter_name': parameter_name,
                'parameter_value': parameter_value,
            }

        @property
        def parameter_name(self) -> str:
            """``CfnDeliveryStream.ProcessorParameterProperty.ParameterName``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-processorparameter.html#cfn-kinesisfirehose-deliverystream-processorparameter-parametername
            """
            return self._values.get('parameter_name')

        @property
        def parameter_value(self) -> str:
            """``CfnDeliveryStream.ProcessorParameterProperty.ParameterValue``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-processorparameter.html#cfn-kinesisfirehose-deliverystream-processorparameter-parametervalue
            """
            return self._values.get('parameter_value')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'ProcessorParameterProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.ProcessorProperty", jsii_struct_bases=[], name_mapping={'parameters': 'parameters', 'type': 'type'})
    class ProcessorProperty():
        def __init__(self, *, parameters: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnDeliveryStream.ProcessorParameterProperty"]]], type: str):
            """
            :param parameters: ``CfnDeliveryStream.ProcessorProperty.Parameters``.
            :param type: ``CfnDeliveryStream.ProcessorProperty.Type``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-processor.html
            """
            self._values = {
                'parameters': parameters,
                'type': type,
            }

        @property
        def parameters(self) -> typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnDeliveryStream.ProcessorParameterProperty"]]]:
            """``CfnDeliveryStream.ProcessorProperty.Parameters``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-processor.html#cfn-kinesisfirehose-deliverystream-processor-parameters
            """
            return self._values.get('parameters')

        @property
        def type(self) -> str:
            """``CfnDeliveryStream.ProcessorProperty.Type``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-processor.html#cfn-kinesisfirehose-deliverystream-processor-type
            """
            return self._values.get('type')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'ProcessorProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.RedshiftDestinationConfigurationProperty", jsii_struct_bases=[], name_mapping={'cluster_jdbcurl': 'clusterJdbcurl', 'copy_command': 'copyCommand', 'password': 'password', 'role_arn': 'roleArn', 's3_configuration': 's3Configuration', 'username': 'username', 'cloud_watch_logging_options': 'cloudWatchLoggingOptions', 'processing_configuration': 'processingConfiguration'})
    class RedshiftDestinationConfigurationProperty():
        def __init__(self, *, cluster_jdbcurl: str, copy_command: typing.Union[aws_cdk.core.IResolvable, "CfnDeliveryStream.CopyCommandProperty"], password: str, role_arn: str, s3_configuration: typing.Union[aws_cdk.core.IResolvable, "CfnDeliveryStream.S3DestinationConfigurationProperty"], username: str, cloud_watch_logging_options: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnDeliveryStream.CloudWatchLoggingOptionsProperty"]]]=None, processing_configuration: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnDeliveryStream.ProcessingConfigurationProperty"]]]=None):
            """
            :param cluster_jdbcurl: ``CfnDeliveryStream.RedshiftDestinationConfigurationProperty.ClusterJDBCURL``.
            :param copy_command: ``CfnDeliveryStream.RedshiftDestinationConfigurationProperty.CopyCommand``.
            :param password: ``CfnDeliveryStream.RedshiftDestinationConfigurationProperty.Password``.
            :param role_arn: ``CfnDeliveryStream.RedshiftDestinationConfigurationProperty.RoleARN``.
            :param s3_configuration: ``CfnDeliveryStream.RedshiftDestinationConfigurationProperty.S3Configuration``.
            :param username: ``CfnDeliveryStream.RedshiftDestinationConfigurationProperty.Username``.
            :param cloud_watch_logging_options: ``CfnDeliveryStream.RedshiftDestinationConfigurationProperty.CloudWatchLoggingOptions``.
            :param processing_configuration: ``CfnDeliveryStream.RedshiftDestinationConfigurationProperty.ProcessingConfiguration``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-redshiftdestinationconfiguration.html
            """
            self._values = {
                'cluster_jdbcurl': cluster_jdbcurl,
                'copy_command': copy_command,
                'password': password,
                'role_arn': role_arn,
                's3_configuration': s3_configuration,
                'username': username,
            }
            if cloud_watch_logging_options is not None: self._values["cloud_watch_logging_options"] = cloud_watch_logging_options
            if processing_configuration is not None: self._values["processing_configuration"] = processing_configuration

        @property
        def cluster_jdbcurl(self) -> str:
            """``CfnDeliveryStream.RedshiftDestinationConfigurationProperty.ClusterJDBCURL``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-redshiftdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-redshiftdestinationconfiguration-clusterjdbcurl
            """
            return self._values.get('cluster_jdbcurl')

        @property
        def copy_command(self) -> typing.Union[aws_cdk.core.IResolvable, "CfnDeliveryStream.CopyCommandProperty"]:
            """``CfnDeliveryStream.RedshiftDestinationConfigurationProperty.CopyCommand``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-redshiftdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-redshiftdestinationconfiguration-copycommand
            """
            return self._values.get('copy_command')

        @property
        def password(self) -> str:
            """``CfnDeliveryStream.RedshiftDestinationConfigurationProperty.Password``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-redshiftdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-redshiftdestinationconfiguration-password
            """
            return self._values.get('password')

        @property
        def role_arn(self) -> str:
            """``CfnDeliveryStream.RedshiftDestinationConfigurationProperty.RoleARN``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-redshiftdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-redshiftdestinationconfiguration-rolearn
            """
            return self._values.get('role_arn')

        @property
        def s3_configuration(self) -> typing.Union[aws_cdk.core.IResolvable, "CfnDeliveryStream.S3DestinationConfigurationProperty"]:
            """``CfnDeliveryStream.RedshiftDestinationConfigurationProperty.S3Configuration``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-redshiftdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-redshiftdestinationconfiguration-s3configuration
            """
            return self._values.get('s3_configuration')

        @property
        def username(self) -> str:
            """``CfnDeliveryStream.RedshiftDestinationConfigurationProperty.Username``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-redshiftdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-redshiftdestinationconfiguration-username
            """
            return self._values.get('username')

        @property
        def cloud_watch_logging_options(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnDeliveryStream.CloudWatchLoggingOptionsProperty"]]]:
            """``CfnDeliveryStream.RedshiftDestinationConfigurationProperty.CloudWatchLoggingOptions``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-redshiftdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-redshiftdestinationconfiguration-cloudwatchloggingoptions
            """
            return self._values.get('cloud_watch_logging_options')

        @property
        def processing_configuration(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnDeliveryStream.ProcessingConfigurationProperty"]]]:
            """``CfnDeliveryStream.RedshiftDestinationConfigurationProperty.ProcessingConfiguration``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-redshiftdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-redshiftdestinationconfiguration-processingconfiguration
            """
            return self._values.get('processing_configuration')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'RedshiftDestinationConfigurationProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.S3DestinationConfigurationProperty", jsii_struct_bases=[], name_mapping={'bucket_arn': 'bucketArn', 'buffering_hints': 'bufferingHints', 'compression_format': 'compressionFormat', 'role_arn': 'roleArn', 'cloud_watch_logging_options': 'cloudWatchLoggingOptions', 'encryption_configuration': 'encryptionConfiguration', 'error_output_prefix': 'errorOutputPrefix', 'prefix': 'prefix'})
    class S3DestinationConfigurationProperty():
        def __init__(self, *, bucket_arn: str, buffering_hints: typing.Union[aws_cdk.core.IResolvable, "CfnDeliveryStream.BufferingHintsProperty"], compression_format: str, role_arn: str, cloud_watch_logging_options: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnDeliveryStream.CloudWatchLoggingOptionsProperty"]]]=None, encryption_configuration: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnDeliveryStream.EncryptionConfigurationProperty"]]]=None, error_output_prefix: typing.Optional[str]=None, prefix: typing.Optional[str]=None):
            """
            :param bucket_arn: ``CfnDeliveryStream.S3DestinationConfigurationProperty.BucketARN``.
            :param buffering_hints: ``CfnDeliveryStream.S3DestinationConfigurationProperty.BufferingHints``.
            :param compression_format: ``CfnDeliveryStream.S3DestinationConfigurationProperty.CompressionFormat``.
            :param role_arn: ``CfnDeliveryStream.S3DestinationConfigurationProperty.RoleARN``.
            :param cloud_watch_logging_options: ``CfnDeliveryStream.S3DestinationConfigurationProperty.CloudWatchLoggingOptions``.
            :param encryption_configuration: ``CfnDeliveryStream.S3DestinationConfigurationProperty.EncryptionConfiguration``.
            :param error_output_prefix: ``CfnDeliveryStream.S3DestinationConfigurationProperty.ErrorOutputPrefix``.
            :param prefix: ``CfnDeliveryStream.S3DestinationConfigurationProperty.Prefix``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-s3destinationconfiguration.html
            """
            self._values = {
                'bucket_arn': bucket_arn,
                'buffering_hints': buffering_hints,
                'compression_format': compression_format,
                'role_arn': role_arn,
            }
            if cloud_watch_logging_options is not None: self._values["cloud_watch_logging_options"] = cloud_watch_logging_options
            if encryption_configuration is not None: self._values["encryption_configuration"] = encryption_configuration
            if error_output_prefix is not None: self._values["error_output_prefix"] = error_output_prefix
            if prefix is not None: self._values["prefix"] = prefix

        @property
        def bucket_arn(self) -> str:
            """``CfnDeliveryStream.S3DestinationConfigurationProperty.BucketARN``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-s3destinationconfiguration.html#cfn-kinesisfirehose-deliverystream-s3destinationconfiguration-bucketarn
            """
            return self._values.get('bucket_arn')

        @property
        def buffering_hints(self) -> typing.Union[aws_cdk.core.IResolvable, "CfnDeliveryStream.BufferingHintsProperty"]:
            """``CfnDeliveryStream.S3DestinationConfigurationProperty.BufferingHints``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-s3destinationconfiguration.html#cfn-kinesisfirehose-deliverystream-s3destinationconfiguration-bufferinghints
            """
            return self._values.get('buffering_hints')

        @property
        def compression_format(self) -> str:
            """``CfnDeliveryStream.S3DestinationConfigurationProperty.CompressionFormat``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-s3destinationconfiguration.html#cfn-kinesisfirehose-deliverystream-s3destinationconfiguration-compressionformat
            """
            return self._values.get('compression_format')

        @property
        def role_arn(self) -> str:
            """``CfnDeliveryStream.S3DestinationConfigurationProperty.RoleARN``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-s3destinationconfiguration.html#cfn-kinesisfirehose-deliverystream-s3destinationconfiguration-rolearn
            """
            return self._values.get('role_arn')

        @property
        def cloud_watch_logging_options(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnDeliveryStream.CloudWatchLoggingOptionsProperty"]]]:
            """``CfnDeliveryStream.S3DestinationConfigurationProperty.CloudWatchLoggingOptions``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-s3destinationconfiguration.html#cfn-kinesisfirehose-deliverystream-s3destinationconfiguration-cloudwatchloggingoptions
            """
            return self._values.get('cloud_watch_logging_options')

        @property
        def encryption_configuration(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnDeliveryStream.EncryptionConfigurationProperty"]]]:
            """``CfnDeliveryStream.S3DestinationConfigurationProperty.EncryptionConfiguration``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-s3destinationconfiguration.html#cfn-kinesisfirehose-deliverystream-s3destinationconfiguration-encryptionconfiguration
            """
            return self._values.get('encryption_configuration')

        @property
        def error_output_prefix(self) -> typing.Optional[str]:
            """``CfnDeliveryStream.S3DestinationConfigurationProperty.ErrorOutputPrefix``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-s3destinationconfiguration.html#cfn-kinesisfirehose-deliverystream-s3destinationconfiguration-erroroutputprefix
            """
            return self._values.get('error_output_prefix')

        @property
        def prefix(self) -> typing.Optional[str]:
            """``CfnDeliveryStream.S3DestinationConfigurationProperty.Prefix``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-s3destinationconfiguration.html#cfn-kinesisfirehose-deliverystream-s3destinationconfiguration-prefix
            """
            return self._values.get('prefix')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'S3DestinationConfigurationProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.SchemaConfigurationProperty", jsii_struct_bases=[], name_mapping={'catalog_id': 'catalogId', 'database_name': 'databaseName', 'region': 'region', 'role_arn': 'roleArn', 'table_name': 'tableName', 'version_id': 'versionId'})
    class SchemaConfigurationProperty():
        def __init__(self, *, catalog_id: str, database_name: str, region: str, role_arn: str, table_name: str, version_id: str):
            """
            :param catalog_id: ``CfnDeliveryStream.SchemaConfigurationProperty.CatalogId``.
            :param database_name: ``CfnDeliveryStream.SchemaConfigurationProperty.DatabaseName``.
            :param region: ``CfnDeliveryStream.SchemaConfigurationProperty.Region``.
            :param role_arn: ``CfnDeliveryStream.SchemaConfigurationProperty.RoleARN``.
            :param table_name: ``CfnDeliveryStream.SchemaConfigurationProperty.TableName``.
            :param version_id: ``CfnDeliveryStream.SchemaConfigurationProperty.VersionId``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-schemaconfiguration.html
            """
            self._values = {
                'catalog_id': catalog_id,
                'database_name': database_name,
                'region': region,
                'role_arn': role_arn,
                'table_name': table_name,
                'version_id': version_id,
            }

        @property
        def catalog_id(self) -> str:
            """``CfnDeliveryStream.SchemaConfigurationProperty.CatalogId``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-schemaconfiguration.html#cfn-kinesisfirehose-deliverystream-schemaconfiguration-catalogid
            """
            return self._values.get('catalog_id')

        @property
        def database_name(self) -> str:
            """``CfnDeliveryStream.SchemaConfigurationProperty.DatabaseName``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-schemaconfiguration.html#cfn-kinesisfirehose-deliverystream-schemaconfiguration-databasename
            """
            return self._values.get('database_name')

        @property
        def region(self) -> str:
            """``CfnDeliveryStream.SchemaConfigurationProperty.Region``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-schemaconfiguration.html#cfn-kinesisfirehose-deliverystream-schemaconfiguration-region
            """
            return self._values.get('region')

        @property
        def role_arn(self) -> str:
            """``CfnDeliveryStream.SchemaConfigurationProperty.RoleARN``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-schemaconfiguration.html#cfn-kinesisfirehose-deliverystream-schemaconfiguration-rolearn
            """
            return self._values.get('role_arn')

        @property
        def table_name(self) -> str:
            """``CfnDeliveryStream.SchemaConfigurationProperty.TableName``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-schemaconfiguration.html#cfn-kinesisfirehose-deliverystream-schemaconfiguration-tablename
            """
            return self._values.get('table_name')

        @property
        def version_id(self) -> str:
            """``CfnDeliveryStream.SchemaConfigurationProperty.VersionId``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-schemaconfiguration.html#cfn-kinesisfirehose-deliverystream-schemaconfiguration-versionid
            """
            return self._values.get('version_id')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'SchemaConfigurationProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.SerializerProperty", jsii_struct_bases=[], name_mapping={'orc_ser_de': 'orcSerDe', 'parquet_ser_de': 'parquetSerDe'})
    class SerializerProperty():
        def __init__(self, *, orc_ser_de: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnDeliveryStream.OrcSerDeProperty"]]]=None, parquet_ser_de: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnDeliveryStream.ParquetSerDeProperty"]]]=None):
            """
            :param orc_ser_de: ``CfnDeliveryStream.SerializerProperty.OrcSerDe``.
            :param parquet_ser_de: ``CfnDeliveryStream.SerializerProperty.ParquetSerDe``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-serializer.html
            """
            self._values = {
            }
            if orc_ser_de is not None: self._values["orc_ser_de"] = orc_ser_de
            if parquet_ser_de is not None: self._values["parquet_ser_de"] = parquet_ser_de

        @property
        def orc_ser_de(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnDeliveryStream.OrcSerDeProperty"]]]:
            """``CfnDeliveryStream.SerializerProperty.OrcSerDe``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-serializer.html#cfn-kinesisfirehose-deliverystream-serializer-orcserde
            """
            return self._values.get('orc_ser_de')

        @property
        def parquet_ser_de(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnDeliveryStream.ParquetSerDeProperty"]]]:
            """``CfnDeliveryStream.SerializerProperty.ParquetSerDe``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-serializer.html#cfn-kinesisfirehose-deliverystream-serializer-parquetserde
            """
            return self._values.get('parquet_ser_de')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'SerializerProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.SplunkDestinationConfigurationProperty", jsii_struct_bases=[], name_mapping={'hec_endpoint': 'hecEndpoint', 'hec_endpoint_type': 'hecEndpointType', 'hec_token': 'hecToken', 's3_configuration': 's3Configuration', 'cloud_watch_logging_options': 'cloudWatchLoggingOptions', 'hec_acknowledgment_timeout_in_seconds': 'hecAcknowledgmentTimeoutInSeconds', 'processing_configuration': 'processingConfiguration', 'retry_options': 'retryOptions', 's3_backup_mode': 's3BackupMode'})
    class SplunkDestinationConfigurationProperty():
        def __init__(self, *, hec_endpoint: str, hec_endpoint_type: str, hec_token: str, s3_configuration: typing.Union[aws_cdk.core.IResolvable, "CfnDeliveryStream.S3DestinationConfigurationProperty"], cloud_watch_logging_options: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnDeliveryStream.CloudWatchLoggingOptionsProperty"]]]=None, hec_acknowledgment_timeout_in_seconds: typing.Optional[jsii.Number]=None, processing_configuration: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnDeliveryStream.ProcessingConfigurationProperty"]]]=None, retry_options: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnDeliveryStream.SplunkRetryOptionsProperty"]]]=None, s3_backup_mode: typing.Optional[str]=None):
            """
            :param hec_endpoint: ``CfnDeliveryStream.SplunkDestinationConfigurationProperty.HECEndpoint``.
            :param hec_endpoint_type: ``CfnDeliveryStream.SplunkDestinationConfigurationProperty.HECEndpointType``.
            :param hec_token: ``CfnDeliveryStream.SplunkDestinationConfigurationProperty.HECToken``.
            :param s3_configuration: ``CfnDeliveryStream.SplunkDestinationConfigurationProperty.S3Configuration``.
            :param cloud_watch_logging_options: ``CfnDeliveryStream.SplunkDestinationConfigurationProperty.CloudWatchLoggingOptions``.
            :param hec_acknowledgment_timeout_in_seconds: ``CfnDeliveryStream.SplunkDestinationConfigurationProperty.HECAcknowledgmentTimeoutInSeconds``.
            :param processing_configuration: ``CfnDeliveryStream.SplunkDestinationConfigurationProperty.ProcessingConfiguration``.
            :param retry_options: ``CfnDeliveryStream.SplunkDestinationConfigurationProperty.RetryOptions``.
            :param s3_backup_mode: ``CfnDeliveryStream.SplunkDestinationConfigurationProperty.S3BackupMode``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-splunkdestinationconfiguration.html
            """
            self._values = {
                'hec_endpoint': hec_endpoint,
                'hec_endpoint_type': hec_endpoint_type,
                'hec_token': hec_token,
                's3_configuration': s3_configuration,
            }
            if cloud_watch_logging_options is not None: self._values["cloud_watch_logging_options"] = cloud_watch_logging_options
            if hec_acknowledgment_timeout_in_seconds is not None: self._values["hec_acknowledgment_timeout_in_seconds"] = hec_acknowledgment_timeout_in_seconds
            if processing_configuration is not None: self._values["processing_configuration"] = processing_configuration
            if retry_options is not None: self._values["retry_options"] = retry_options
            if s3_backup_mode is not None: self._values["s3_backup_mode"] = s3_backup_mode

        @property
        def hec_endpoint(self) -> str:
            """``CfnDeliveryStream.SplunkDestinationConfigurationProperty.HECEndpoint``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-splunkdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-splunkdestinationconfiguration-hecendpoint
            """
            return self._values.get('hec_endpoint')

        @property
        def hec_endpoint_type(self) -> str:
            """``CfnDeliveryStream.SplunkDestinationConfigurationProperty.HECEndpointType``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-splunkdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-splunkdestinationconfiguration-hecendpointtype
            """
            return self._values.get('hec_endpoint_type')

        @property
        def hec_token(self) -> str:
            """``CfnDeliveryStream.SplunkDestinationConfigurationProperty.HECToken``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-splunkdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-splunkdestinationconfiguration-hectoken
            """
            return self._values.get('hec_token')

        @property
        def s3_configuration(self) -> typing.Union[aws_cdk.core.IResolvable, "CfnDeliveryStream.S3DestinationConfigurationProperty"]:
            """``CfnDeliveryStream.SplunkDestinationConfigurationProperty.S3Configuration``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-splunkdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-splunkdestinationconfiguration-s3configuration
            """
            return self._values.get('s3_configuration')

        @property
        def cloud_watch_logging_options(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnDeliveryStream.CloudWatchLoggingOptionsProperty"]]]:
            """``CfnDeliveryStream.SplunkDestinationConfigurationProperty.CloudWatchLoggingOptions``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-splunkdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-splunkdestinationconfiguration-cloudwatchloggingoptions
            """
            return self._values.get('cloud_watch_logging_options')

        @property
        def hec_acknowledgment_timeout_in_seconds(self) -> typing.Optional[jsii.Number]:
            """``CfnDeliveryStream.SplunkDestinationConfigurationProperty.HECAcknowledgmentTimeoutInSeconds``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-splunkdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-splunkdestinationconfiguration-hecacknowledgmenttimeoutinseconds
            """
            return self._values.get('hec_acknowledgment_timeout_in_seconds')

        @property
        def processing_configuration(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnDeliveryStream.ProcessingConfigurationProperty"]]]:
            """``CfnDeliveryStream.SplunkDestinationConfigurationProperty.ProcessingConfiguration``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-splunkdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-splunkdestinationconfiguration-processingconfiguration
            """
            return self._values.get('processing_configuration')

        @property
        def retry_options(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnDeliveryStream.SplunkRetryOptionsProperty"]]]:
            """``CfnDeliveryStream.SplunkDestinationConfigurationProperty.RetryOptions``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-splunkdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-splunkdestinationconfiguration-retryoptions
            """
            return self._values.get('retry_options')

        @property
        def s3_backup_mode(self) -> typing.Optional[str]:
            """``CfnDeliveryStream.SplunkDestinationConfigurationProperty.S3BackupMode``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-splunkdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-splunkdestinationconfiguration-s3backupmode
            """
            return self._values.get('s3_backup_mode')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'SplunkDestinationConfigurationProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.SplunkRetryOptionsProperty", jsii_struct_bases=[], name_mapping={'duration_in_seconds': 'durationInSeconds'})
    class SplunkRetryOptionsProperty():
        def __init__(self, *, duration_in_seconds: jsii.Number):
            """
            :param duration_in_seconds: ``CfnDeliveryStream.SplunkRetryOptionsProperty.DurationInSeconds``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-splunkretryoptions.html
            """
            self._values = {
                'duration_in_seconds': duration_in_seconds,
            }

        @property
        def duration_in_seconds(self) -> jsii.Number:
            """``CfnDeliveryStream.SplunkRetryOptionsProperty.DurationInSeconds``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-splunkretryoptions.html#cfn-kinesisfirehose-deliverystream-splunkretryoptions-durationinseconds
            """
            return self._values.get('duration_in_seconds')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'SplunkRetryOptionsProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



@jsii.data_type(jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStreamProps", jsii_struct_bases=[], name_mapping={'delivery_stream_name': 'deliveryStreamName', 'delivery_stream_type': 'deliveryStreamType', 'elasticsearch_destination_configuration': 'elasticsearchDestinationConfiguration', 'extended_s3_destination_configuration': 'extendedS3DestinationConfiguration', 'kinesis_stream_source_configuration': 'kinesisStreamSourceConfiguration', 'redshift_destination_configuration': 'redshiftDestinationConfiguration', 's3_destination_configuration': 's3DestinationConfiguration', 'splunk_destination_configuration': 'splunkDestinationConfiguration'})
class CfnDeliveryStreamProps():
    def __init__(self, *, delivery_stream_name: typing.Optional[str]=None, delivery_stream_type: typing.Optional[str]=None, elasticsearch_destination_configuration: typing.Optional[typing.Union[typing.Optional["CfnDeliveryStream.ElasticsearchDestinationConfigurationProperty"], typing.Optional[aws_cdk.core.IResolvable]]]=None, extended_s3_destination_configuration: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnDeliveryStream.ExtendedS3DestinationConfigurationProperty"]]]=None, kinesis_stream_source_configuration: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnDeliveryStream.KinesisStreamSourceConfigurationProperty"]]]=None, redshift_destination_configuration: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnDeliveryStream.RedshiftDestinationConfigurationProperty"]]]=None, s3_destination_configuration: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnDeliveryStream.S3DestinationConfigurationProperty"]]]=None, splunk_destination_configuration: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnDeliveryStream.SplunkDestinationConfigurationProperty"]]]=None):
        """Properties for defining a ``AWS::KinesisFirehose::DeliveryStream``.

        :param delivery_stream_name: ``AWS::KinesisFirehose::DeliveryStream.DeliveryStreamName``.
        :param delivery_stream_type: ``AWS::KinesisFirehose::DeliveryStream.DeliveryStreamType``.
        :param elasticsearch_destination_configuration: ``AWS::KinesisFirehose::DeliveryStream.ElasticsearchDestinationConfiguration``.
        :param extended_s3_destination_configuration: ``AWS::KinesisFirehose::DeliveryStream.ExtendedS3DestinationConfiguration``.
        :param kinesis_stream_source_configuration: ``AWS::KinesisFirehose::DeliveryStream.KinesisStreamSourceConfiguration``.
        :param redshift_destination_configuration: ``AWS::KinesisFirehose::DeliveryStream.RedshiftDestinationConfiguration``.
        :param s3_destination_configuration: ``AWS::KinesisFirehose::DeliveryStream.S3DestinationConfiguration``.
        :param splunk_destination_configuration: ``AWS::KinesisFirehose::DeliveryStream.SplunkDestinationConfiguration``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisfirehose-deliverystream.html
        """
        self._values = {
        }
        if delivery_stream_name is not None: self._values["delivery_stream_name"] = delivery_stream_name
        if delivery_stream_type is not None: self._values["delivery_stream_type"] = delivery_stream_type
        if elasticsearch_destination_configuration is not None: self._values["elasticsearch_destination_configuration"] = elasticsearch_destination_configuration
        if extended_s3_destination_configuration is not None: self._values["extended_s3_destination_configuration"] = extended_s3_destination_configuration
        if kinesis_stream_source_configuration is not None: self._values["kinesis_stream_source_configuration"] = kinesis_stream_source_configuration
        if redshift_destination_configuration is not None: self._values["redshift_destination_configuration"] = redshift_destination_configuration
        if s3_destination_configuration is not None: self._values["s3_destination_configuration"] = s3_destination_configuration
        if splunk_destination_configuration is not None: self._values["splunk_destination_configuration"] = splunk_destination_configuration

    @property
    def delivery_stream_name(self) -> typing.Optional[str]:
        """``AWS::KinesisFirehose::DeliveryStream.DeliveryStreamName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisfirehose-deliverystream.html#cfn-kinesisfirehose-deliverystream-deliverystreamname
        """
        return self._values.get('delivery_stream_name')

    @property
    def delivery_stream_type(self) -> typing.Optional[str]:
        """``AWS::KinesisFirehose::DeliveryStream.DeliveryStreamType``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisfirehose-deliverystream.html#cfn-kinesisfirehose-deliverystream-deliverystreamtype
        """
        return self._values.get('delivery_stream_type')

    @property
    def elasticsearch_destination_configuration(self) -> typing.Optional[typing.Union[typing.Optional["CfnDeliveryStream.ElasticsearchDestinationConfigurationProperty"], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::KinesisFirehose::DeliveryStream.ElasticsearchDestinationConfiguration``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisfirehose-deliverystream.html#cfn-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration
        """
        return self._values.get('elasticsearch_destination_configuration')

    @property
    def extended_s3_destination_configuration(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnDeliveryStream.ExtendedS3DestinationConfigurationProperty"]]]:
        """``AWS::KinesisFirehose::DeliveryStream.ExtendedS3DestinationConfiguration``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisfirehose-deliverystream.html#cfn-kinesisfirehose-deliverystream-extendeds3destinationconfiguration
        """
        return self._values.get('extended_s3_destination_configuration')

    @property
    def kinesis_stream_source_configuration(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnDeliveryStream.KinesisStreamSourceConfigurationProperty"]]]:
        """``AWS::KinesisFirehose::DeliveryStream.KinesisStreamSourceConfiguration``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisfirehose-deliverystream.html#cfn-kinesisfirehose-deliverystream-kinesisstreamsourceconfiguration
        """
        return self._values.get('kinesis_stream_source_configuration')

    @property
    def redshift_destination_configuration(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnDeliveryStream.RedshiftDestinationConfigurationProperty"]]]:
        """``AWS::KinesisFirehose::DeliveryStream.RedshiftDestinationConfiguration``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisfirehose-deliverystream.html#cfn-kinesisfirehose-deliverystream-redshiftdestinationconfiguration
        """
        return self._values.get('redshift_destination_configuration')

    @property
    def s3_destination_configuration(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnDeliveryStream.S3DestinationConfigurationProperty"]]]:
        """``AWS::KinesisFirehose::DeliveryStream.S3DestinationConfiguration``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisfirehose-deliverystream.html#cfn-kinesisfirehose-deliverystream-s3destinationconfiguration
        """
        return self._values.get('s3_destination_configuration')

    @property
    def splunk_destination_configuration(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnDeliveryStream.SplunkDestinationConfigurationProperty"]]]:
        """``AWS::KinesisFirehose::DeliveryStream.SplunkDestinationConfiguration``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisfirehose-deliverystream.html#cfn-kinesisfirehose-deliverystream-splunkdestinationconfiguration
        """
        return self._values.get('splunk_destination_configuration')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnDeliveryStreamProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


__all__ = ["CfnDeliveryStream", "CfnDeliveryStreamProps", "__jsii_assembly__"]

publication.publish()
