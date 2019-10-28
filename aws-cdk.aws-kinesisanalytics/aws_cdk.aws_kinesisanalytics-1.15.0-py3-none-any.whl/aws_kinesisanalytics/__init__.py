import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.core
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-kinesisanalytics", "1.15.0", __name__, "aws-kinesisanalytics@1.15.0.jsii.tgz")
class CfnApplication(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-kinesisanalytics.CfnApplication"):
    """A CloudFormation ``AWS::KinesisAnalytics::Application``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisanalytics-application.html
    cloudformationResource:
    :cloudformationResource:: AWS::KinesisAnalytics::Application
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, inputs: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union["InputProperty", aws_cdk.core.IResolvable]]], application_code: typing.Optional[str]=None, application_description: typing.Optional[str]=None, application_name: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::KinesisAnalytics::Application``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param inputs: ``AWS::KinesisAnalytics::Application.Inputs``.
        :param application_code: ``AWS::KinesisAnalytics::Application.ApplicationCode``.
        :param application_description: ``AWS::KinesisAnalytics::Application.ApplicationDescription``.
        :param application_name: ``AWS::KinesisAnalytics::Application.ApplicationName``.
        """
        props = CfnApplicationProps(inputs=inputs, application_code=application_code, application_description=application_description, application_name=application_name)

        jsii.create(CfnApplication, self, [scope, id, props])

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
    @jsii.member(jsii_name="inputs")
    def inputs(self) -> typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union["InputProperty", aws_cdk.core.IResolvable]]]:
        """``AWS::KinesisAnalytics::Application.Inputs``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisanalytics-application.html#cfn-kinesisanalytics-application-inputs
        """
        return jsii.get(self, "inputs")

    @inputs.setter
    def inputs(self, value: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union["InputProperty", aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "inputs", value)

    @property
    @jsii.member(jsii_name="applicationCode")
    def application_code(self) -> typing.Optional[str]:
        """``AWS::KinesisAnalytics::Application.ApplicationCode``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisanalytics-application.html#cfn-kinesisanalytics-application-applicationcode
        """
        return jsii.get(self, "applicationCode")

    @application_code.setter
    def application_code(self, value: typing.Optional[str]):
        return jsii.set(self, "applicationCode", value)

    @property
    @jsii.member(jsii_name="applicationDescription")
    def application_description(self) -> typing.Optional[str]:
        """``AWS::KinesisAnalytics::Application.ApplicationDescription``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisanalytics-application.html#cfn-kinesisanalytics-application-applicationdescription
        """
        return jsii.get(self, "applicationDescription")

    @application_description.setter
    def application_description(self, value: typing.Optional[str]):
        return jsii.set(self, "applicationDescription", value)

    @property
    @jsii.member(jsii_name="applicationName")
    def application_name(self) -> typing.Optional[str]:
        """``AWS::KinesisAnalytics::Application.ApplicationName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisanalytics-application.html#cfn-kinesisanalytics-application-applicationname
        """
        return jsii.get(self, "applicationName")

    @application_name.setter
    def application_name(self, value: typing.Optional[str]):
        return jsii.set(self, "applicationName", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisanalytics.CfnApplication.CSVMappingParametersProperty", jsii_struct_bases=[], name_mapping={'record_column_delimiter': 'recordColumnDelimiter', 'record_row_delimiter': 'recordRowDelimiter'})
    class CSVMappingParametersProperty():
        def __init__(self, *, record_column_delimiter: str, record_row_delimiter: str):
            """
            :param record_column_delimiter: ``CfnApplication.CSVMappingParametersProperty.RecordColumnDelimiter``.
            :param record_row_delimiter: ``CfnApplication.CSVMappingParametersProperty.RecordRowDelimiter``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalytics-application-csvmappingparameters.html
            """
            self._values = {
                'record_column_delimiter': record_column_delimiter,
                'record_row_delimiter': record_row_delimiter,
            }

        @property
        def record_column_delimiter(self) -> str:
            """``CfnApplication.CSVMappingParametersProperty.RecordColumnDelimiter``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalytics-application-csvmappingparameters.html#cfn-kinesisanalytics-application-csvmappingparameters-recordcolumndelimiter
            """
            return self._values.get('record_column_delimiter')

        @property
        def record_row_delimiter(self) -> str:
            """``CfnApplication.CSVMappingParametersProperty.RecordRowDelimiter``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalytics-application-csvmappingparameters.html#cfn-kinesisanalytics-application-csvmappingparameters-recordrowdelimiter
            """
            return self._values.get('record_row_delimiter')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'CSVMappingParametersProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisanalytics.CfnApplication.InputLambdaProcessorProperty", jsii_struct_bases=[], name_mapping={'resource_arn': 'resourceArn', 'role_arn': 'roleArn'})
    class InputLambdaProcessorProperty():
        def __init__(self, *, resource_arn: str, role_arn: str):
            """
            :param resource_arn: ``CfnApplication.InputLambdaProcessorProperty.ResourceARN``.
            :param role_arn: ``CfnApplication.InputLambdaProcessorProperty.RoleARN``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalytics-application-inputlambdaprocessor.html
            """
            self._values = {
                'resource_arn': resource_arn,
                'role_arn': role_arn,
            }

        @property
        def resource_arn(self) -> str:
            """``CfnApplication.InputLambdaProcessorProperty.ResourceARN``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalytics-application-inputlambdaprocessor.html#cfn-kinesisanalytics-application-inputlambdaprocessor-resourcearn
            """
            return self._values.get('resource_arn')

        @property
        def role_arn(self) -> str:
            """``CfnApplication.InputLambdaProcessorProperty.RoleARN``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalytics-application-inputlambdaprocessor.html#cfn-kinesisanalytics-application-inputlambdaprocessor-rolearn
            """
            return self._values.get('role_arn')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'InputLambdaProcessorProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisanalytics.CfnApplication.InputParallelismProperty", jsii_struct_bases=[], name_mapping={'count': 'count'})
    class InputParallelismProperty():
        def __init__(self, *, count: typing.Optional[jsii.Number]=None):
            """
            :param count: ``CfnApplication.InputParallelismProperty.Count``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalytics-application-inputparallelism.html
            """
            self._values = {
            }
            if count is not None: self._values["count"] = count

        @property
        def count(self) -> typing.Optional[jsii.Number]:
            """``CfnApplication.InputParallelismProperty.Count``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalytics-application-inputparallelism.html#cfn-kinesisanalytics-application-inputparallelism-count
            """
            return self._values.get('count')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'InputParallelismProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisanalytics.CfnApplication.InputProcessingConfigurationProperty", jsii_struct_bases=[], name_mapping={'input_lambda_processor': 'inputLambdaProcessor'})
    class InputProcessingConfigurationProperty():
        def __init__(self, *, input_lambda_processor: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnApplication.InputLambdaProcessorProperty"]]]=None):
            """
            :param input_lambda_processor: ``CfnApplication.InputProcessingConfigurationProperty.InputLambdaProcessor``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalytics-application-inputprocessingconfiguration.html
            """
            self._values = {
            }
            if input_lambda_processor is not None: self._values["input_lambda_processor"] = input_lambda_processor

        @property
        def input_lambda_processor(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnApplication.InputLambdaProcessorProperty"]]]:
            """``CfnApplication.InputProcessingConfigurationProperty.InputLambdaProcessor``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalytics-application-inputprocessingconfiguration.html#cfn-kinesisanalytics-application-inputprocessingconfiguration-inputlambdaprocessor
            """
            return self._values.get('input_lambda_processor')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'InputProcessingConfigurationProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisanalytics.CfnApplication.InputProperty", jsii_struct_bases=[], name_mapping={'input_schema': 'inputSchema', 'name_prefix': 'namePrefix', 'input_parallelism': 'inputParallelism', 'input_processing_configuration': 'inputProcessingConfiguration', 'kinesis_firehose_input': 'kinesisFirehoseInput', 'kinesis_streams_input': 'kinesisStreamsInput'})
    class InputProperty():
        def __init__(self, *, input_schema: typing.Union[aws_cdk.core.IResolvable, "CfnApplication.InputSchemaProperty"], name_prefix: str, input_parallelism: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnApplication.InputParallelismProperty"]]]=None, input_processing_configuration: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnApplication.InputProcessingConfigurationProperty"]]]=None, kinesis_firehose_input: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnApplication.KinesisFirehoseInputProperty"]]]=None, kinesis_streams_input: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnApplication.KinesisStreamsInputProperty"]]]=None):
            """
            :param input_schema: ``CfnApplication.InputProperty.InputSchema``.
            :param name_prefix: ``CfnApplication.InputProperty.NamePrefix``.
            :param input_parallelism: ``CfnApplication.InputProperty.InputParallelism``.
            :param input_processing_configuration: ``CfnApplication.InputProperty.InputProcessingConfiguration``.
            :param kinesis_firehose_input: ``CfnApplication.InputProperty.KinesisFirehoseInput``.
            :param kinesis_streams_input: ``CfnApplication.InputProperty.KinesisStreamsInput``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalytics-application-input.html
            """
            self._values = {
                'input_schema': input_schema,
                'name_prefix': name_prefix,
            }
            if input_parallelism is not None: self._values["input_parallelism"] = input_parallelism
            if input_processing_configuration is not None: self._values["input_processing_configuration"] = input_processing_configuration
            if kinesis_firehose_input is not None: self._values["kinesis_firehose_input"] = kinesis_firehose_input
            if kinesis_streams_input is not None: self._values["kinesis_streams_input"] = kinesis_streams_input

        @property
        def input_schema(self) -> typing.Union[aws_cdk.core.IResolvable, "CfnApplication.InputSchemaProperty"]:
            """``CfnApplication.InputProperty.InputSchema``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalytics-application-input.html#cfn-kinesisanalytics-application-input-inputschema
            """
            return self._values.get('input_schema')

        @property
        def name_prefix(self) -> str:
            """``CfnApplication.InputProperty.NamePrefix``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalytics-application-input.html#cfn-kinesisanalytics-application-input-nameprefix
            """
            return self._values.get('name_prefix')

        @property
        def input_parallelism(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnApplication.InputParallelismProperty"]]]:
            """``CfnApplication.InputProperty.InputParallelism``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalytics-application-input.html#cfn-kinesisanalytics-application-input-inputparallelism
            """
            return self._values.get('input_parallelism')

        @property
        def input_processing_configuration(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnApplication.InputProcessingConfigurationProperty"]]]:
            """``CfnApplication.InputProperty.InputProcessingConfiguration``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalytics-application-input.html#cfn-kinesisanalytics-application-input-inputprocessingconfiguration
            """
            return self._values.get('input_processing_configuration')

        @property
        def kinesis_firehose_input(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnApplication.KinesisFirehoseInputProperty"]]]:
            """``CfnApplication.InputProperty.KinesisFirehoseInput``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalytics-application-input.html#cfn-kinesisanalytics-application-input-kinesisfirehoseinput
            """
            return self._values.get('kinesis_firehose_input')

        @property
        def kinesis_streams_input(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnApplication.KinesisStreamsInputProperty"]]]:
            """``CfnApplication.InputProperty.KinesisStreamsInput``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalytics-application-input.html#cfn-kinesisanalytics-application-input-kinesisstreamsinput
            """
            return self._values.get('kinesis_streams_input')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'InputProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisanalytics.CfnApplication.InputSchemaProperty", jsii_struct_bases=[], name_mapping={'record_columns': 'recordColumns', 'record_format': 'recordFormat', 'record_encoding': 'recordEncoding'})
    class InputSchemaProperty():
        def __init__(self, *, record_columns: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnApplication.RecordColumnProperty"]]], record_format: typing.Union[aws_cdk.core.IResolvable, "CfnApplication.RecordFormatProperty"], record_encoding: typing.Optional[str]=None):
            """
            :param record_columns: ``CfnApplication.InputSchemaProperty.RecordColumns``.
            :param record_format: ``CfnApplication.InputSchemaProperty.RecordFormat``.
            :param record_encoding: ``CfnApplication.InputSchemaProperty.RecordEncoding``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalytics-application-inputschema.html
            """
            self._values = {
                'record_columns': record_columns,
                'record_format': record_format,
            }
            if record_encoding is not None: self._values["record_encoding"] = record_encoding

        @property
        def record_columns(self) -> typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnApplication.RecordColumnProperty"]]]:
            """``CfnApplication.InputSchemaProperty.RecordColumns``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalytics-application-inputschema.html#cfn-kinesisanalytics-application-inputschema-recordcolumns
            """
            return self._values.get('record_columns')

        @property
        def record_format(self) -> typing.Union[aws_cdk.core.IResolvable, "CfnApplication.RecordFormatProperty"]:
            """``CfnApplication.InputSchemaProperty.RecordFormat``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalytics-application-inputschema.html#cfn-kinesisanalytics-application-inputschema-recordformat
            """
            return self._values.get('record_format')

        @property
        def record_encoding(self) -> typing.Optional[str]:
            """``CfnApplication.InputSchemaProperty.RecordEncoding``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalytics-application-inputschema.html#cfn-kinesisanalytics-application-inputschema-recordencoding
            """
            return self._values.get('record_encoding')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'InputSchemaProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisanalytics.CfnApplication.JSONMappingParametersProperty", jsii_struct_bases=[], name_mapping={'record_row_path': 'recordRowPath'})
    class JSONMappingParametersProperty():
        def __init__(self, *, record_row_path: str):
            """
            :param record_row_path: ``CfnApplication.JSONMappingParametersProperty.RecordRowPath``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalytics-application-jsonmappingparameters.html
            """
            self._values = {
                'record_row_path': record_row_path,
            }

        @property
        def record_row_path(self) -> str:
            """``CfnApplication.JSONMappingParametersProperty.RecordRowPath``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalytics-application-jsonmappingparameters.html#cfn-kinesisanalytics-application-jsonmappingparameters-recordrowpath
            """
            return self._values.get('record_row_path')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'JSONMappingParametersProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisanalytics.CfnApplication.KinesisFirehoseInputProperty", jsii_struct_bases=[], name_mapping={'resource_arn': 'resourceArn', 'role_arn': 'roleArn'})
    class KinesisFirehoseInputProperty():
        def __init__(self, *, resource_arn: str, role_arn: str):
            """
            :param resource_arn: ``CfnApplication.KinesisFirehoseInputProperty.ResourceARN``.
            :param role_arn: ``CfnApplication.KinesisFirehoseInputProperty.RoleARN``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalytics-application-kinesisfirehoseinput.html
            """
            self._values = {
                'resource_arn': resource_arn,
                'role_arn': role_arn,
            }

        @property
        def resource_arn(self) -> str:
            """``CfnApplication.KinesisFirehoseInputProperty.ResourceARN``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalytics-application-kinesisfirehoseinput.html#cfn-kinesisanalytics-application-kinesisfirehoseinput-resourcearn
            """
            return self._values.get('resource_arn')

        @property
        def role_arn(self) -> str:
            """``CfnApplication.KinesisFirehoseInputProperty.RoleARN``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalytics-application-kinesisfirehoseinput.html#cfn-kinesisanalytics-application-kinesisfirehoseinput-rolearn
            """
            return self._values.get('role_arn')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'KinesisFirehoseInputProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisanalytics.CfnApplication.KinesisStreamsInputProperty", jsii_struct_bases=[], name_mapping={'resource_arn': 'resourceArn', 'role_arn': 'roleArn'})
    class KinesisStreamsInputProperty():
        def __init__(self, *, resource_arn: str, role_arn: str):
            """
            :param resource_arn: ``CfnApplication.KinesisStreamsInputProperty.ResourceARN``.
            :param role_arn: ``CfnApplication.KinesisStreamsInputProperty.RoleARN``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalytics-application-kinesisstreamsinput.html
            """
            self._values = {
                'resource_arn': resource_arn,
                'role_arn': role_arn,
            }

        @property
        def resource_arn(self) -> str:
            """``CfnApplication.KinesisStreamsInputProperty.ResourceARN``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalytics-application-kinesisstreamsinput.html#cfn-kinesisanalytics-application-kinesisstreamsinput-resourcearn
            """
            return self._values.get('resource_arn')

        @property
        def role_arn(self) -> str:
            """``CfnApplication.KinesisStreamsInputProperty.RoleARN``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalytics-application-kinesisstreamsinput.html#cfn-kinesisanalytics-application-kinesisstreamsinput-rolearn
            """
            return self._values.get('role_arn')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'KinesisStreamsInputProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisanalytics.CfnApplication.MappingParametersProperty", jsii_struct_bases=[], name_mapping={'csv_mapping_parameters': 'csvMappingParameters', 'json_mapping_parameters': 'jsonMappingParameters'})
    class MappingParametersProperty():
        def __init__(self, *, csv_mapping_parameters: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnApplication.CSVMappingParametersProperty"]]]=None, json_mapping_parameters: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnApplication.JSONMappingParametersProperty"]]]=None):
            """
            :param csv_mapping_parameters: ``CfnApplication.MappingParametersProperty.CSVMappingParameters``.
            :param json_mapping_parameters: ``CfnApplication.MappingParametersProperty.JSONMappingParameters``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalytics-application-mappingparameters.html
            """
            self._values = {
            }
            if csv_mapping_parameters is not None: self._values["csv_mapping_parameters"] = csv_mapping_parameters
            if json_mapping_parameters is not None: self._values["json_mapping_parameters"] = json_mapping_parameters

        @property
        def csv_mapping_parameters(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnApplication.CSVMappingParametersProperty"]]]:
            """``CfnApplication.MappingParametersProperty.CSVMappingParameters``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalytics-application-mappingparameters.html#cfn-kinesisanalytics-application-mappingparameters-csvmappingparameters
            """
            return self._values.get('csv_mapping_parameters')

        @property
        def json_mapping_parameters(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnApplication.JSONMappingParametersProperty"]]]:
            """``CfnApplication.MappingParametersProperty.JSONMappingParameters``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalytics-application-mappingparameters.html#cfn-kinesisanalytics-application-mappingparameters-jsonmappingparameters
            """
            return self._values.get('json_mapping_parameters')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'MappingParametersProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisanalytics.CfnApplication.RecordColumnProperty", jsii_struct_bases=[], name_mapping={'name': 'name', 'sql_type': 'sqlType', 'mapping': 'mapping'})
    class RecordColumnProperty():
        def __init__(self, *, name: str, sql_type: str, mapping: typing.Optional[str]=None):
            """
            :param name: ``CfnApplication.RecordColumnProperty.Name``.
            :param sql_type: ``CfnApplication.RecordColumnProperty.SqlType``.
            :param mapping: ``CfnApplication.RecordColumnProperty.Mapping``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalytics-application-recordcolumn.html
            """
            self._values = {
                'name': name,
                'sql_type': sql_type,
            }
            if mapping is not None: self._values["mapping"] = mapping

        @property
        def name(self) -> str:
            """``CfnApplication.RecordColumnProperty.Name``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalytics-application-recordcolumn.html#cfn-kinesisanalytics-application-recordcolumn-name
            """
            return self._values.get('name')

        @property
        def sql_type(self) -> str:
            """``CfnApplication.RecordColumnProperty.SqlType``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalytics-application-recordcolumn.html#cfn-kinesisanalytics-application-recordcolumn-sqltype
            """
            return self._values.get('sql_type')

        @property
        def mapping(self) -> typing.Optional[str]:
            """``CfnApplication.RecordColumnProperty.Mapping``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalytics-application-recordcolumn.html#cfn-kinesisanalytics-application-recordcolumn-mapping
            """
            return self._values.get('mapping')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'RecordColumnProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisanalytics.CfnApplication.RecordFormatProperty", jsii_struct_bases=[], name_mapping={'record_format_type': 'recordFormatType', 'mapping_parameters': 'mappingParameters'})
    class RecordFormatProperty():
        def __init__(self, *, record_format_type: str, mapping_parameters: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnApplication.MappingParametersProperty"]]]=None):
            """
            :param record_format_type: ``CfnApplication.RecordFormatProperty.RecordFormatType``.
            :param mapping_parameters: ``CfnApplication.RecordFormatProperty.MappingParameters``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalytics-application-recordformat.html
            """
            self._values = {
                'record_format_type': record_format_type,
            }
            if mapping_parameters is not None: self._values["mapping_parameters"] = mapping_parameters

        @property
        def record_format_type(self) -> str:
            """``CfnApplication.RecordFormatProperty.RecordFormatType``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalytics-application-recordformat.html#cfn-kinesisanalytics-application-recordformat-recordformattype
            """
            return self._values.get('record_format_type')

        @property
        def mapping_parameters(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnApplication.MappingParametersProperty"]]]:
            """``CfnApplication.RecordFormatProperty.MappingParameters``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalytics-application-recordformat.html#cfn-kinesisanalytics-application-recordformat-mappingparameters
            """
            return self._values.get('mapping_parameters')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'RecordFormatProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



class CfnApplicationCloudWatchLoggingOptionV2(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-kinesisanalytics.CfnApplicationCloudWatchLoggingOptionV2"):
    """A CloudFormation ``AWS::KinesisAnalyticsV2::ApplicationCloudWatchLoggingOption``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisanalyticsv2-applicationcloudwatchloggingoption.html
    cloudformationResource:
    :cloudformationResource:: AWS::KinesisAnalyticsV2::ApplicationCloudWatchLoggingOption
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, application_name: str, cloud_watch_logging_option: typing.Union[aws_cdk.core.IResolvable, "CloudWatchLoggingOptionProperty"]) -> None:
        """Create a new ``AWS::KinesisAnalyticsV2::ApplicationCloudWatchLoggingOption``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param application_name: ``AWS::KinesisAnalyticsV2::ApplicationCloudWatchLoggingOption.ApplicationName``.
        :param cloud_watch_logging_option: ``AWS::KinesisAnalyticsV2::ApplicationCloudWatchLoggingOption.CloudWatchLoggingOption``.
        """
        props = CfnApplicationCloudWatchLoggingOptionV2Props(application_name=application_name, cloud_watch_logging_option=cloud_watch_logging_option)

        jsii.create(CfnApplicationCloudWatchLoggingOptionV2, self, [scope, id, props])

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
    @jsii.member(jsii_name="applicationName")
    def application_name(self) -> str:
        """``AWS::KinesisAnalyticsV2::ApplicationCloudWatchLoggingOption.ApplicationName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisanalyticsv2-applicationcloudwatchloggingoption.html#cfn-kinesisanalyticsv2-applicationcloudwatchloggingoption-applicationname
        """
        return jsii.get(self, "applicationName")

    @application_name.setter
    def application_name(self, value: str):
        return jsii.set(self, "applicationName", value)

    @property
    @jsii.member(jsii_name="cloudWatchLoggingOption")
    def cloud_watch_logging_option(self) -> typing.Union[aws_cdk.core.IResolvable, "CloudWatchLoggingOptionProperty"]:
        """``AWS::KinesisAnalyticsV2::ApplicationCloudWatchLoggingOption.CloudWatchLoggingOption``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisanalyticsv2-applicationcloudwatchloggingoption.html#cfn-kinesisanalyticsv2-applicationcloudwatchloggingoption-cloudwatchloggingoption
        """
        return jsii.get(self, "cloudWatchLoggingOption")

    @cloud_watch_logging_option.setter
    def cloud_watch_logging_option(self, value: typing.Union[aws_cdk.core.IResolvable, "CloudWatchLoggingOptionProperty"]):
        return jsii.set(self, "cloudWatchLoggingOption", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisanalytics.CfnApplicationCloudWatchLoggingOptionV2.CloudWatchLoggingOptionProperty", jsii_struct_bases=[], name_mapping={'log_stream_arn': 'logStreamArn'})
    class CloudWatchLoggingOptionProperty():
        def __init__(self, *, log_stream_arn: str):
            """
            :param log_stream_arn: ``CfnApplicationCloudWatchLoggingOptionV2.CloudWatchLoggingOptionProperty.LogStreamARN``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-applicationcloudwatchloggingoption-cloudwatchloggingoption.html
            """
            self._values = {
                'log_stream_arn': log_stream_arn,
            }

        @property
        def log_stream_arn(self) -> str:
            """``CfnApplicationCloudWatchLoggingOptionV2.CloudWatchLoggingOptionProperty.LogStreamARN``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-applicationcloudwatchloggingoption-cloudwatchloggingoption.html#cfn-kinesisanalyticsv2-applicationcloudwatchloggingoption-cloudwatchloggingoption-logstreamarn
            """
            return self._values.get('log_stream_arn')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'CloudWatchLoggingOptionProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



@jsii.data_type(jsii_type="@aws-cdk/aws-kinesisanalytics.CfnApplicationCloudWatchLoggingOptionV2Props", jsii_struct_bases=[], name_mapping={'application_name': 'applicationName', 'cloud_watch_logging_option': 'cloudWatchLoggingOption'})
class CfnApplicationCloudWatchLoggingOptionV2Props():
    def __init__(self, *, application_name: str, cloud_watch_logging_option: typing.Union[aws_cdk.core.IResolvable, "CfnApplicationCloudWatchLoggingOptionV2.CloudWatchLoggingOptionProperty"]):
        """Properties for defining a ``AWS::KinesisAnalyticsV2::ApplicationCloudWatchLoggingOption``.

        :param application_name: ``AWS::KinesisAnalyticsV2::ApplicationCloudWatchLoggingOption.ApplicationName``.
        :param cloud_watch_logging_option: ``AWS::KinesisAnalyticsV2::ApplicationCloudWatchLoggingOption.CloudWatchLoggingOption``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisanalyticsv2-applicationcloudwatchloggingoption.html
        """
        self._values = {
            'application_name': application_name,
            'cloud_watch_logging_option': cloud_watch_logging_option,
        }

    @property
    def application_name(self) -> str:
        """``AWS::KinesisAnalyticsV2::ApplicationCloudWatchLoggingOption.ApplicationName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisanalyticsv2-applicationcloudwatchloggingoption.html#cfn-kinesisanalyticsv2-applicationcloudwatchloggingoption-applicationname
        """
        return self._values.get('application_name')

    @property
    def cloud_watch_logging_option(self) -> typing.Union[aws_cdk.core.IResolvable, "CfnApplicationCloudWatchLoggingOptionV2.CloudWatchLoggingOptionProperty"]:
        """``AWS::KinesisAnalyticsV2::ApplicationCloudWatchLoggingOption.CloudWatchLoggingOption``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisanalyticsv2-applicationcloudwatchloggingoption.html#cfn-kinesisanalyticsv2-applicationcloudwatchloggingoption-cloudwatchloggingoption
        """
        return self._values.get('cloud_watch_logging_option')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnApplicationCloudWatchLoggingOptionV2Props(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnApplicationOutput(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-kinesisanalytics.CfnApplicationOutput"):
    """A CloudFormation ``AWS::KinesisAnalytics::ApplicationOutput``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisanalytics-applicationoutput.html
    cloudformationResource:
    :cloudformationResource:: AWS::KinesisAnalytics::ApplicationOutput
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, application_name: str, output: typing.Union[aws_cdk.core.IResolvable, "OutputProperty"]) -> None:
        """Create a new ``AWS::KinesisAnalytics::ApplicationOutput``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param application_name: ``AWS::KinesisAnalytics::ApplicationOutput.ApplicationName``.
        :param output: ``AWS::KinesisAnalytics::ApplicationOutput.Output``.
        """
        props = CfnApplicationOutputProps(application_name=application_name, output=output)

        jsii.create(CfnApplicationOutput, self, [scope, id, props])

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
    @jsii.member(jsii_name="applicationName")
    def application_name(self) -> str:
        """``AWS::KinesisAnalytics::ApplicationOutput.ApplicationName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisanalytics-applicationoutput.html#cfn-kinesisanalytics-applicationoutput-applicationname
        """
        return jsii.get(self, "applicationName")

    @application_name.setter
    def application_name(self, value: str):
        return jsii.set(self, "applicationName", value)

    @property
    @jsii.member(jsii_name="output")
    def output(self) -> typing.Union[aws_cdk.core.IResolvable, "OutputProperty"]:
        """``AWS::KinesisAnalytics::ApplicationOutput.Output``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisanalytics-applicationoutput.html#cfn-kinesisanalytics-applicationoutput-output
        """
        return jsii.get(self, "output")

    @output.setter
    def output(self, value: typing.Union[aws_cdk.core.IResolvable, "OutputProperty"]):
        return jsii.set(self, "output", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisanalytics.CfnApplicationOutput.DestinationSchemaProperty", jsii_struct_bases=[], name_mapping={'record_format_type': 'recordFormatType'})
    class DestinationSchemaProperty():
        def __init__(self, *, record_format_type: typing.Optional[str]=None):
            """
            :param record_format_type: ``CfnApplicationOutput.DestinationSchemaProperty.RecordFormatType``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalytics-applicationoutput-destinationschema.html
            """
            self._values = {
            }
            if record_format_type is not None: self._values["record_format_type"] = record_format_type

        @property
        def record_format_type(self) -> typing.Optional[str]:
            """``CfnApplicationOutput.DestinationSchemaProperty.RecordFormatType``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalytics-applicationoutput-destinationschema.html#cfn-kinesisanalytics-applicationoutput-destinationschema-recordformattype
            """
            return self._values.get('record_format_type')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'DestinationSchemaProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisanalytics.CfnApplicationOutput.KinesisFirehoseOutputProperty", jsii_struct_bases=[], name_mapping={'resource_arn': 'resourceArn', 'role_arn': 'roleArn'})
    class KinesisFirehoseOutputProperty():
        def __init__(self, *, resource_arn: str, role_arn: str):
            """
            :param resource_arn: ``CfnApplicationOutput.KinesisFirehoseOutputProperty.ResourceARN``.
            :param role_arn: ``CfnApplicationOutput.KinesisFirehoseOutputProperty.RoleARN``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalytics-applicationoutput-kinesisfirehoseoutput.html
            """
            self._values = {
                'resource_arn': resource_arn,
                'role_arn': role_arn,
            }

        @property
        def resource_arn(self) -> str:
            """``CfnApplicationOutput.KinesisFirehoseOutputProperty.ResourceARN``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalytics-applicationoutput-kinesisfirehoseoutput.html#cfn-kinesisanalytics-applicationoutput-kinesisfirehoseoutput-resourcearn
            """
            return self._values.get('resource_arn')

        @property
        def role_arn(self) -> str:
            """``CfnApplicationOutput.KinesisFirehoseOutputProperty.RoleARN``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalytics-applicationoutput-kinesisfirehoseoutput.html#cfn-kinesisanalytics-applicationoutput-kinesisfirehoseoutput-rolearn
            """
            return self._values.get('role_arn')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'KinesisFirehoseOutputProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisanalytics.CfnApplicationOutput.KinesisStreamsOutputProperty", jsii_struct_bases=[], name_mapping={'resource_arn': 'resourceArn', 'role_arn': 'roleArn'})
    class KinesisStreamsOutputProperty():
        def __init__(self, *, resource_arn: str, role_arn: str):
            """
            :param resource_arn: ``CfnApplicationOutput.KinesisStreamsOutputProperty.ResourceARN``.
            :param role_arn: ``CfnApplicationOutput.KinesisStreamsOutputProperty.RoleARN``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalytics-applicationoutput-kinesisstreamsoutput.html
            """
            self._values = {
                'resource_arn': resource_arn,
                'role_arn': role_arn,
            }

        @property
        def resource_arn(self) -> str:
            """``CfnApplicationOutput.KinesisStreamsOutputProperty.ResourceARN``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalytics-applicationoutput-kinesisstreamsoutput.html#cfn-kinesisanalytics-applicationoutput-kinesisstreamsoutput-resourcearn
            """
            return self._values.get('resource_arn')

        @property
        def role_arn(self) -> str:
            """``CfnApplicationOutput.KinesisStreamsOutputProperty.RoleARN``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalytics-applicationoutput-kinesisstreamsoutput.html#cfn-kinesisanalytics-applicationoutput-kinesisstreamsoutput-rolearn
            """
            return self._values.get('role_arn')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'KinesisStreamsOutputProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisanalytics.CfnApplicationOutput.LambdaOutputProperty", jsii_struct_bases=[], name_mapping={'resource_arn': 'resourceArn', 'role_arn': 'roleArn'})
    class LambdaOutputProperty():
        def __init__(self, *, resource_arn: str, role_arn: str):
            """
            :param resource_arn: ``CfnApplicationOutput.LambdaOutputProperty.ResourceARN``.
            :param role_arn: ``CfnApplicationOutput.LambdaOutputProperty.RoleARN``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalytics-applicationoutput-lambdaoutput.html
            """
            self._values = {
                'resource_arn': resource_arn,
                'role_arn': role_arn,
            }

        @property
        def resource_arn(self) -> str:
            """``CfnApplicationOutput.LambdaOutputProperty.ResourceARN``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalytics-applicationoutput-lambdaoutput.html#cfn-kinesisanalytics-applicationoutput-lambdaoutput-resourcearn
            """
            return self._values.get('resource_arn')

        @property
        def role_arn(self) -> str:
            """``CfnApplicationOutput.LambdaOutputProperty.RoleARN``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalytics-applicationoutput-lambdaoutput.html#cfn-kinesisanalytics-applicationoutput-lambdaoutput-rolearn
            """
            return self._values.get('role_arn')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'LambdaOutputProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisanalytics.CfnApplicationOutput.OutputProperty", jsii_struct_bases=[], name_mapping={'destination_schema': 'destinationSchema', 'kinesis_firehose_output': 'kinesisFirehoseOutput', 'kinesis_streams_output': 'kinesisStreamsOutput', 'lambda_output': 'lambdaOutput', 'name': 'name'})
    class OutputProperty():
        def __init__(self, *, destination_schema: typing.Union[aws_cdk.core.IResolvable, "CfnApplicationOutput.DestinationSchemaProperty"], kinesis_firehose_output: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnApplicationOutput.KinesisFirehoseOutputProperty"]]]=None, kinesis_streams_output: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnApplicationOutput.KinesisStreamsOutputProperty"]]]=None, lambda_output: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnApplicationOutput.LambdaOutputProperty"]]]=None, name: typing.Optional[str]=None):
            """
            :param destination_schema: ``CfnApplicationOutput.OutputProperty.DestinationSchema``.
            :param kinesis_firehose_output: ``CfnApplicationOutput.OutputProperty.KinesisFirehoseOutput``.
            :param kinesis_streams_output: ``CfnApplicationOutput.OutputProperty.KinesisStreamsOutput``.
            :param lambda_output: ``CfnApplicationOutput.OutputProperty.LambdaOutput``.
            :param name: ``CfnApplicationOutput.OutputProperty.Name``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalytics-applicationoutput-output.html
            """
            self._values = {
                'destination_schema': destination_schema,
            }
            if kinesis_firehose_output is not None: self._values["kinesis_firehose_output"] = kinesis_firehose_output
            if kinesis_streams_output is not None: self._values["kinesis_streams_output"] = kinesis_streams_output
            if lambda_output is not None: self._values["lambda_output"] = lambda_output
            if name is not None: self._values["name"] = name

        @property
        def destination_schema(self) -> typing.Union[aws_cdk.core.IResolvable, "CfnApplicationOutput.DestinationSchemaProperty"]:
            """``CfnApplicationOutput.OutputProperty.DestinationSchema``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalytics-applicationoutput-output.html#cfn-kinesisanalytics-applicationoutput-output-destinationschema
            """
            return self._values.get('destination_schema')

        @property
        def kinesis_firehose_output(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnApplicationOutput.KinesisFirehoseOutputProperty"]]]:
            """``CfnApplicationOutput.OutputProperty.KinesisFirehoseOutput``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalytics-applicationoutput-output.html#cfn-kinesisanalytics-applicationoutput-output-kinesisfirehoseoutput
            """
            return self._values.get('kinesis_firehose_output')

        @property
        def kinesis_streams_output(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnApplicationOutput.KinesisStreamsOutputProperty"]]]:
            """``CfnApplicationOutput.OutputProperty.KinesisStreamsOutput``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalytics-applicationoutput-output.html#cfn-kinesisanalytics-applicationoutput-output-kinesisstreamsoutput
            """
            return self._values.get('kinesis_streams_output')

        @property
        def lambda_output(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnApplicationOutput.LambdaOutputProperty"]]]:
            """``CfnApplicationOutput.OutputProperty.LambdaOutput``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalytics-applicationoutput-output.html#cfn-kinesisanalytics-applicationoutput-output-lambdaoutput
            """
            return self._values.get('lambda_output')

        @property
        def name(self) -> typing.Optional[str]:
            """``CfnApplicationOutput.OutputProperty.Name``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalytics-applicationoutput-output.html#cfn-kinesisanalytics-applicationoutput-output-name
            """
            return self._values.get('name')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'OutputProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



@jsii.data_type(jsii_type="@aws-cdk/aws-kinesisanalytics.CfnApplicationOutputProps", jsii_struct_bases=[], name_mapping={'application_name': 'applicationName', 'output': 'output'})
class CfnApplicationOutputProps():
    def __init__(self, *, application_name: str, output: typing.Union[aws_cdk.core.IResolvable, "CfnApplicationOutput.OutputProperty"]):
        """Properties for defining a ``AWS::KinesisAnalytics::ApplicationOutput``.

        :param application_name: ``AWS::KinesisAnalytics::ApplicationOutput.ApplicationName``.
        :param output: ``AWS::KinesisAnalytics::ApplicationOutput.Output``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisanalytics-applicationoutput.html
        """
        self._values = {
            'application_name': application_name,
            'output': output,
        }

    @property
    def application_name(self) -> str:
        """``AWS::KinesisAnalytics::ApplicationOutput.ApplicationName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisanalytics-applicationoutput.html#cfn-kinesisanalytics-applicationoutput-applicationname
        """
        return self._values.get('application_name')

    @property
    def output(self) -> typing.Union[aws_cdk.core.IResolvable, "CfnApplicationOutput.OutputProperty"]:
        """``AWS::KinesisAnalytics::ApplicationOutput.Output``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisanalytics-applicationoutput.html#cfn-kinesisanalytics-applicationoutput-output
        """
        return self._values.get('output')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnApplicationOutputProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnApplicationOutputV2(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-kinesisanalytics.CfnApplicationOutputV2"):
    """A CloudFormation ``AWS::KinesisAnalyticsV2::ApplicationOutput``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisanalyticsv2-applicationoutput.html
    cloudformationResource:
    :cloudformationResource:: AWS::KinesisAnalyticsV2::ApplicationOutput
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, application_name: str, output: typing.Union[aws_cdk.core.IResolvable, "OutputProperty"]) -> None:
        """Create a new ``AWS::KinesisAnalyticsV2::ApplicationOutput``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param application_name: ``AWS::KinesisAnalyticsV2::ApplicationOutput.ApplicationName``.
        :param output: ``AWS::KinesisAnalyticsV2::ApplicationOutput.Output``.
        """
        props = CfnApplicationOutputV2Props(application_name=application_name, output=output)

        jsii.create(CfnApplicationOutputV2, self, [scope, id, props])

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
    @jsii.member(jsii_name="applicationName")
    def application_name(self) -> str:
        """``AWS::KinesisAnalyticsV2::ApplicationOutput.ApplicationName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisanalyticsv2-applicationoutput.html#cfn-kinesisanalyticsv2-applicationoutput-applicationname
        """
        return jsii.get(self, "applicationName")

    @application_name.setter
    def application_name(self, value: str):
        return jsii.set(self, "applicationName", value)

    @property
    @jsii.member(jsii_name="output")
    def output(self) -> typing.Union[aws_cdk.core.IResolvable, "OutputProperty"]:
        """``AWS::KinesisAnalyticsV2::ApplicationOutput.Output``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisanalyticsv2-applicationoutput.html#cfn-kinesisanalyticsv2-applicationoutput-output
        """
        return jsii.get(self, "output")

    @output.setter
    def output(self, value: typing.Union[aws_cdk.core.IResolvable, "OutputProperty"]):
        return jsii.set(self, "output", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisanalytics.CfnApplicationOutputV2.DestinationSchemaProperty", jsii_struct_bases=[], name_mapping={'record_format_type': 'recordFormatType'})
    class DestinationSchemaProperty():
        def __init__(self, *, record_format_type: typing.Optional[str]=None):
            """
            :param record_format_type: ``CfnApplicationOutputV2.DestinationSchemaProperty.RecordFormatType``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-applicationoutput-destinationschema.html
            """
            self._values = {
            }
            if record_format_type is not None: self._values["record_format_type"] = record_format_type

        @property
        def record_format_type(self) -> typing.Optional[str]:
            """``CfnApplicationOutputV2.DestinationSchemaProperty.RecordFormatType``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-applicationoutput-destinationschema.html#cfn-kinesisanalyticsv2-applicationoutput-destinationschema-recordformattype
            """
            return self._values.get('record_format_type')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'DestinationSchemaProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisanalytics.CfnApplicationOutputV2.KinesisFirehoseOutputProperty", jsii_struct_bases=[], name_mapping={'resource_arn': 'resourceArn'})
    class KinesisFirehoseOutputProperty():
        def __init__(self, *, resource_arn: str):
            """
            :param resource_arn: ``CfnApplicationOutputV2.KinesisFirehoseOutputProperty.ResourceARN``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-applicationoutput-kinesisfirehoseoutput.html
            """
            self._values = {
                'resource_arn': resource_arn,
            }

        @property
        def resource_arn(self) -> str:
            """``CfnApplicationOutputV2.KinesisFirehoseOutputProperty.ResourceARN``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-applicationoutput-kinesisfirehoseoutput.html#cfn-kinesisanalyticsv2-applicationoutput-kinesisfirehoseoutput-resourcearn
            """
            return self._values.get('resource_arn')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'KinesisFirehoseOutputProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisanalytics.CfnApplicationOutputV2.KinesisStreamsOutputProperty", jsii_struct_bases=[], name_mapping={'resource_arn': 'resourceArn'})
    class KinesisStreamsOutputProperty():
        def __init__(self, *, resource_arn: str):
            """
            :param resource_arn: ``CfnApplicationOutputV2.KinesisStreamsOutputProperty.ResourceARN``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-applicationoutput-kinesisstreamsoutput.html
            """
            self._values = {
                'resource_arn': resource_arn,
            }

        @property
        def resource_arn(self) -> str:
            """``CfnApplicationOutputV2.KinesisStreamsOutputProperty.ResourceARN``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-applicationoutput-kinesisstreamsoutput.html#cfn-kinesisanalyticsv2-applicationoutput-kinesisstreamsoutput-resourcearn
            """
            return self._values.get('resource_arn')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'KinesisStreamsOutputProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisanalytics.CfnApplicationOutputV2.LambdaOutputProperty", jsii_struct_bases=[], name_mapping={'resource_arn': 'resourceArn'})
    class LambdaOutputProperty():
        def __init__(self, *, resource_arn: str):
            """
            :param resource_arn: ``CfnApplicationOutputV2.LambdaOutputProperty.ResourceARN``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-applicationoutput-lambdaoutput.html
            """
            self._values = {
                'resource_arn': resource_arn,
            }

        @property
        def resource_arn(self) -> str:
            """``CfnApplicationOutputV2.LambdaOutputProperty.ResourceARN``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-applicationoutput-lambdaoutput.html#cfn-kinesisanalyticsv2-applicationoutput-lambdaoutput-resourcearn
            """
            return self._values.get('resource_arn')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'LambdaOutputProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisanalytics.CfnApplicationOutputV2.OutputProperty", jsii_struct_bases=[], name_mapping={'destination_schema': 'destinationSchema', 'kinesis_firehose_output': 'kinesisFirehoseOutput', 'kinesis_streams_output': 'kinesisStreamsOutput', 'lambda_output': 'lambdaOutput', 'name': 'name'})
    class OutputProperty():
        def __init__(self, *, destination_schema: typing.Union[aws_cdk.core.IResolvable, "CfnApplicationOutputV2.DestinationSchemaProperty"], kinesis_firehose_output: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnApplicationOutputV2.KinesisFirehoseOutputProperty"]]]=None, kinesis_streams_output: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnApplicationOutputV2.KinesisStreamsOutputProperty"]]]=None, lambda_output: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnApplicationOutputV2.LambdaOutputProperty"]]]=None, name: typing.Optional[str]=None):
            """
            :param destination_schema: ``CfnApplicationOutputV2.OutputProperty.DestinationSchema``.
            :param kinesis_firehose_output: ``CfnApplicationOutputV2.OutputProperty.KinesisFirehoseOutput``.
            :param kinesis_streams_output: ``CfnApplicationOutputV2.OutputProperty.KinesisStreamsOutput``.
            :param lambda_output: ``CfnApplicationOutputV2.OutputProperty.LambdaOutput``.
            :param name: ``CfnApplicationOutputV2.OutputProperty.Name``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-applicationoutput-output.html
            """
            self._values = {
                'destination_schema': destination_schema,
            }
            if kinesis_firehose_output is not None: self._values["kinesis_firehose_output"] = kinesis_firehose_output
            if kinesis_streams_output is not None: self._values["kinesis_streams_output"] = kinesis_streams_output
            if lambda_output is not None: self._values["lambda_output"] = lambda_output
            if name is not None: self._values["name"] = name

        @property
        def destination_schema(self) -> typing.Union[aws_cdk.core.IResolvable, "CfnApplicationOutputV2.DestinationSchemaProperty"]:
            """``CfnApplicationOutputV2.OutputProperty.DestinationSchema``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-applicationoutput-output.html#cfn-kinesisanalyticsv2-applicationoutput-output-destinationschema
            """
            return self._values.get('destination_schema')

        @property
        def kinesis_firehose_output(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnApplicationOutputV2.KinesisFirehoseOutputProperty"]]]:
            """``CfnApplicationOutputV2.OutputProperty.KinesisFirehoseOutput``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-applicationoutput-output.html#cfn-kinesisanalyticsv2-applicationoutput-output-kinesisfirehoseoutput
            """
            return self._values.get('kinesis_firehose_output')

        @property
        def kinesis_streams_output(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnApplicationOutputV2.KinesisStreamsOutputProperty"]]]:
            """``CfnApplicationOutputV2.OutputProperty.KinesisStreamsOutput``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-applicationoutput-output.html#cfn-kinesisanalyticsv2-applicationoutput-output-kinesisstreamsoutput
            """
            return self._values.get('kinesis_streams_output')

        @property
        def lambda_output(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnApplicationOutputV2.LambdaOutputProperty"]]]:
            """``CfnApplicationOutputV2.OutputProperty.LambdaOutput``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-applicationoutput-output.html#cfn-kinesisanalyticsv2-applicationoutput-output-lambdaoutput
            """
            return self._values.get('lambda_output')

        @property
        def name(self) -> typing.Optional[str]:
            """``CfnApplicationOutputV2.OutputProperty.Name``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-applicationoutput-output.html#cfn-kinesisanalyticsv2-applicationoutput-output-name
            """
            return self._values.get('name')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'OutputProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



@jsii.data_type(jsii_type="@aws-cdk/aws-kinesisanalytics.CfnApplicationOutputV2Props", jsii_struct_bases=[], name_mapping={'application_name': 'applicationName', 'output': 'output'})
class CfnApplicationOutputV2Props():
    def __init__(self, *, application_name: str, output: typing.Union[aws_cdk.core.IResolvable, "CfnApplicationOutputV2.OutputProperty"]):
        """Properties for defining a ``AWS::KinesisAnalyticsV2::ApplicationOutput``.

        :param application_name: ``AWS::KinesisAnalyticsV2::ApplicationOutput.ApplicationName``.
        :param output: ``AWS::KinesisAnalyticsV2::ApplicationOutput.Output``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisanalyticsv2-applicationoutput.html
        """
        self._values = {
            'application_name': application_name,
            'output': output,
        }

    @property
    def application_name(self) -> str:
        """``AWS::KinesisAnalyticsV2::ApplicationOutput.ApplicationName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisanalyticsv2-applicationoutput.html#cfn-kinesisanalyticsv2-applicationoutput-applicationname
        """
        return self._values.get('application_name')

    @property
    def output(self) -> typing.Union[aws_cdk.core.IResolvable, "CfnApplicationOutputV2.OutputProperty"]:
        """``AWS::KinesisAnalyticsV2::ApplicationOutput.Output``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisanalyticsv2-applicationoutput.html#cfn-kinesisanalyticsv2-applicationoutput-output
        """
        return self._values.get('output')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnApplicationOutputV2Props(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


@jsii.data_type(jsii_type="@aws-cdk/aws-kinesisanalytics.CfnApplicationProps", jsii_struct_bases=[], name_mapping={'inputs': 'inputs', 'application_code': 'applicationCode', 'application_description': 'applicationDescription', 'application_name': 'applicationName'})
class CfnApplicationProps():
    def __init__(self, *, inputs: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union["CfnApplication.InputProperty", aws_cdk.core.IResolvable]]], application_code: typing.Optional[str]=None, application_description: typing.Optional[str]=None, application_name: typing.Optional[str]=None):
        """Properties for defining a ``AWS::KinesisAnalytics::Application``.

        :param inputs: ``AWS::KinesisAnalytics::Application.Inputs``.
        :param application_code: ``AWS::KinesisAnalytics::Application.ApplicationCode``.
        :param application_description: ``AWS::KinesisAnalytics::Application.ApplicationDescription``.
        :param application_name: ``AWS::KinesisAnalytics::Application.ApplicationName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisanalytics-application.html
        """
        self._values = {
            'inputs': inputs,
        }
        if application_code is not None: self._values["application_code"] = application_code
        if application_description is not None: self._values["application_description"] = application_description
        if application_name is not None: self._values["application_name"] = application_name

    @property
    def inputs(self) -> typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union["CfnApplication.InputProperty", aws_cdk.core.IResolvable]]]:
        """``AWS::KinesisAnalytics::Application.Inputs``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisanalytics-application.html#cfn-kinesisanalytics-application-inputs
        """
        return self._values.get('inputs')

    @property
    def application_code(self) -> typing.Optional[str]:
        """``AWS::KinesisAnalytics::Application.ApplicationCode``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisanalytics-application.html#cfn-kinesisanalytics-application-applicationcode
        """
        return self._values.get('application_code')

    @property
    def application_description(self) -> typing.Optional[str]:
        """``AWS::KinesisAnalytics::Application.ApplicationDescription``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisanalytics-application.html#cfn-kinesisanalytics-application-applicationdescription
        """
        return self._values.get('application_description')

    @property
    def application_name(self) -> typing.Optional[str]:
        """``AWS::KinesisAnalytics::Application.ApplicationName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisanalytics-application.html#cfn-kinesisanalytics-application-applicationname
        """
        return self._values.get('application_name')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnApplicationProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnApplicationReferenceDataSource(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-kinesisanalytics.CfnApplicationReferenceDataSource"):
    """A CloudFormation ``AWS::KinesisAnalytics::ApplicationReferenceDataSource``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisanalytics-applicationreferencedatasource.html
    cloudformationResource:
    :cloudformationResource:: AWS::KinesisAnalytics::ApplicationReferenceDataSource
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, application_name: str, reference_data_source: typing.Union[aws_cdk.core.IResolvable, "ReferenceDataSourceProperty"]) -> None:
        """Create a new ``AWS::KinesisAnalytics::ApplicationReferenceDataSource``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param application_name: ``AWS::KinesisAnalytics::ApplicationReferenceDataSource.ApplicationName``.
        :param reference_data_source: ``AWS::KinesisAnalytics::ApplicationReferenceDataSource.ReferenceDataSource``.
        """
        props = CfnApplicationReferenceDataSourceProps(application_name=application_name, reference_data_source=reference_data_source)

        jsii.create(CfnApplicationReferenceDataSource, self, [scope, id, props])

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
    @jsii.member(jsii_name="applicationName")
    def application_name(self) -> str:
        """``AWS::KinesisAnalytics::ApplicationReferenceDataSource.ApplicationName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisanalytics-applicationreferencedatasource.html#cfn-kinesisanalytics-applicationreferencedatasource-applicationname
        """
        return jsii.get(self, "applicationName")

    @application_name.setter
    def application_name(self, value: str):
        return jsii.set(self, "applicationName", value)

    @property
    @jsii.member(jsii_name="referenceDataSource")
    def reference_data_source(self) -> typing.Union[aws_cdk.core.IResolvable, "ReferenceDataSourceProperty"]:
        """``AWS::KinesisAnalytics::ApplicationReferenceDataSource.ReferenceDataSource``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisanalytics-applicationreferencedatasource.html#cfn-kinesisanalytics-applicationreferencedatasource-referencedatasource
        """
        return jsii.get(self, "referenceDataSource")

    @reference_data_source.setter
    def reference_data_source(self, value: typing.Union[aws_cdk.core.IResolvable, "ReferenceDataSourceProperty"]):
        return jsii.set(self, "referenceDataSource", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisanalytics.CfnApplicationReferenceDataSource.CSVMappingParametersProperty", jsii_struct_bases=[], name_mapping={'record_column_delimiter': 'recordColumnDelimiter', 'record_row_delimiter': 'recordRowDelimiter'})
    class CSVMappingParametersProperty():
        def __init__(self, *, record_column_delimiter: str, record_row_delimiter: str):
            """
            :param record_column_delimiter: ``CfnApplicationReferenceDataSource.CSVMappingParametersProperty.RecordColumnDelimiter``.
            :param record_row_delimiter: ``CfnApplicationReferenceDataSource.CSVMappingParametersProperty.RecordRowDelimiter``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalytics-applicationreferencedatasource-csvmappingparameters.html
            """
            self._values = {
                'record_column_delimiter': record_column_delimiter,
                'record_row_delimiter': record_row_delimiter,
            }

        @property
        def record_column_delimiter(self) -> str:
            """``CfnApplicationReferenceDataSource.CSVMappingParametersProperty.RecordColumnDelimiter``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalytics-applicationreferencedatasource-csvmappingparameters.html#cfn-kinesisanalytics-applicationreferencedatasource-csvmappingparameters-recordcolumndelimiter
            """
            return self._values.get('record_column_delimiter')

        @property
        def record_row_delimiter(self) -> str:
            """``CfnApplicationReferenceDataSource.CSVMappingParametersProperty.RecordRowDelimiter``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalytics-applicationreferencedatasource-csvmappingparameters.html#cfn-kinesisanalytics-applicationreferencedatasource-csvmappingparameters-recordrowdelimiter
            """
            return self._values.get('record_row_delimiter')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'CSVMappingParametersProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisanalytics.CfnApplicationReferenceDataSource.JSONMappingParametersProperty", jsii_struct_bases=[], name_mapping={'record_row_path': 'recordRowPath'})
    class JSONMappingParametersProperty():
        def __init__(self, *, record_row_path: str):
            """
            :param record_row_path: ``CfnApplicationReferenceDataSource.JSONMappingParametersProperty.RecordRowPath``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalytics-applicationreferencedatasource-jsonmappingparameters.html
            """
            self._values = {
                'record_row_path': record_row_path,
            }

        @property
        def record_row_path(self) -> str:
            """``CfnApplicationReferenceDataSource.JSONMappingParametersProperty.RecordRowPath``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalytics-applicationreferencedatasource-jsonmappingparameters.html#cfn-kinesisanalytics-applicationreferencedatasource-jsonmappingparameters-recordrowpath
            """
            return self._values.get('record_row_path')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'JSONMappingParametersProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisanalytics.CfnApplicationReferenceDataSource.MappingParametersProperty", jsii_struct_bases=[], name_mapping={'csv_mapping_parameters': 'csvMappingParameters', 'json_mapping_parameters': 'jsonMappingParameters'})
    class MappingParametersProperty():
        def __init__(self, *, csv_mapping_parameters: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnApplicationReferenceDataSource.CSVMappingParametersProperty"]]]=None, json_mapping_parameters: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnApplicationReferenceDataSource.JSONMappingParametersProperty"]]]=None):
            """
            :param csv_mapping_parameters: ``CfnApplicationReferenceDataSource.MappingParametersProperty.CSVMappingParameters``.
            :param json_mapping_parameters: ``CfnApplicationReferenceDataSource.MappingParametersProperty.JSONMappingParameters``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalytics-applicationreferencedatasource-mappingparameters.html
            """
            self._values = {
            }
            if csv_mapping_parameters is not None: self._values["csv_mapping_parameters"] = csv_mapping_parameters
            if json_mapping_parameters is not None: self._values["json_mapping_parameters"] = json_mapping_parameters

        @property
        def csv_mapping_parameters(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnApplicationReferenceDataSource.CSVMappingParametersProperty"]]]:
            """``CfnApplicationReferenceDataSource.MappingParametersProperty.CSVMappingParameters``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalytics-applicationreferencedatasource-mappingparameters.html#cfn-kinesisanalytics-applicationreferencedatasource-mappingparameters-csvmappingparameters
            """
            return self._values.get('csv_mapping_parameters')

        @property
        def json_mapping_parameters(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnApplicationReferenceDataSource.JSONMappingParametersProperty"]]]:
            """``CfnApplicationReferenceDataSource.MappingParametersProperty.JSONMappingParameters``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalytics-applicationreferencedatasource-mappingparameters.html#cfn-kinesisanalytics-applicationreferencedatasource-mappingparameters-jsonmappingparameters
            """
            return self._values.get('json_mapping_parameters')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'MappingParametersProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisanalytics.CfnApplicationReferenceDataSource.RecordColumnProperty", jsii_struct_bases=[], name_mapping={'name': 'name', 'sql_type': 'sqlType', 'mapping': 'mapping'})
    class RecordColumnProperty():
        def __init__(self, *, name: str, sql_type: str, mapping: typing.Optional[str]=None):
            """
            :param name: ``CfnApplicationReferenceDataSource.RecordColumnProperty.Name``.
            :param sql_type: ``CfnApplicationReferenceDataSource.RecordColumnProperty.SqlType``.
            :param mapping: ``CfnApplicationReferenceDataSource.RecordColumnProperty.Mapping``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalytics-applicationreferencedatasource-recordcolumn.html
            """
            self._values = {
                'name': name,
                'sql_type': sql_type,
            }
            if mapping is not None: self._values["mapping"] = mapping

        @property
        def name(self) -> str:
            """``CfnApplicationReferenceDataSource.RecordColumnProperty.Name``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalytics-applicationreferencedatasource-recordcolumn.html#cfn-kinesisanalytics-applicationreferencedatasource-recordcolumn-name
            """
            return self._values.get('name')

        @property
        def sql_type(self) -> str:
            """``CfnApplicationReferenceDataSource.RecordColumnProperty.SqlType``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalytics-applicationreferencedatasource-recordcolumn.html#cfn-kinesisanalytics-applicationreferencedatasource-recordcolumn-sqltype
            """
            return self._values.get('sql_type')

        @property
        def mapping(self) -> typing.Optional[str]:
            """``CfnApplicationReferenceDataSource.RecordColumnProperty.Mapping``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalytics-applicationreferencedatasource-recordcolumn.html#cfn-kinesisanalytics-applicationreferencedatasource-recordcolumn-mapping
            """
            return self._values.get('mapping')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'RecordColumnProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisanalytics.CfnApplicationReferenceDataSource.RecordFormatProperty", jsii_struct_bases=[], name_mapping={'record_format_type': 'recordFormatType', 'mapping_parameters': 'mappingParameters'})
    class RecordFormatProperty():
        def __init__(self, *, record_format_type: str, mapping_parameters: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnApplicationReferenceDataSource.MappingParametersProperty"]]]=None):
            """
            :param record_format_type: ``CfnApplicationReferenceDataSource.RecordFormatProperty.RecordFormatType``.
            :param mapping_parameters: ``CfnApplicationReferenceDataSource.RecordFormatProperty.MappingParameters``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalytics-applicationreferencedatasource-recordformat.html
            """
            self._values = {
                'record_format_type': record_format_type,
            }
            if mapping_parameters is not None: self._values["mapping_parameters"] = mapping_parameters

        @property
        def record_format_type(self) -> str:
            """``CfnApplicationReferenceDataSource.RecordFormatProperty.RecordFormatType``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalytics-applicationreferencedatasource-recordformat.html#cfn-kinesisanalytics-applicationreferencedatasource-recordformat-recordformattype
            """
            return self._values.get('record_format_type')

        @property
        def mapping_parameters(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnApplicationReferenceDataSource.MappingParametersProperty"]]]:
            """``CfnApplicationReferenceDataSource.RecordFormatProperty.MappingParameters``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalytics-applicationreferencedatasource-recordformat.html#cfn-kinesisanalytics-applicationreferencedatasource-recordformat-mappingparameters
            """
            return self._values.get('mapping_parameters')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'RecordFormatProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisanalytics.CfnApplicationReferenceDataSource.ReferenceDataSourceProperty", jsii_struct_bases=[], name_mapping={'reference_schema': 'referenceSchema', 's3_reference_data_source': 's3ReferenceDataSource', 'table_name': 'tableName'})
    class ReferenceDataSourceProperty():
        def __init__(self, *, reference_schema: typing.Union[aws_cdk.core.IResolvable, "CfnApplicationReferenceDataSource.ReferenceSchemaProperty"], s3_reference_data_source: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnApplicationReferenceDataSource.S3ReferenceDataSourceProperty"]]]=None, table_name: typing.Optional[str]=None):
            """
            :param reference_schema: ``CfnApplicationReferenceDataSource.ReferenceDataSourceProperty.ReferenceSchema``.
            :param s3_reference_data_source: ``CfnApplicationReferenceDataSource.ReferenceDataSourceProperty.S3ReferenceDataSource``.
            :param table_name: ``CfnApplicationReferenceDataSource.ReferenceDataSourceProperty.TableName``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalytics-applicationreferencedatasource-referencedatasource.html
            """
            self._values = {
                'reference_schema': reference_schema,
            }
            if s3_reference_data_source is not None: self._values["s3_reference_data_source"] = s3_reference_data_source
            if table_name is not None: self._values["table_name"] = table_name

        @property
        def reference_schema(self) -> typing.Union[aws_cdk.core.IResolvable, "CfnApplicationReferenceDataSource.ReferenceSchemaProperty"]:
            """``CfnApplicationReferenceDataSource.ReferenceDataSourceProperty.ReferenceSchema``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalytics-applicationreferencedatasource-referencedatasource.html#cfn-kinesisanalytics-applicationreferencedatasource-referencedatasource-referenceschema
            """
            return self._values.get('reference_schema')

        @property
        def s3_reference_data_source(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnApplicationReferenceDataSource.S3ReferenceDataSourceProperty"]]]:
            """``CfnApplicationReferenceDataSource.ReferenceDataSourceProperty.S3ReferenceDataSource``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalytics-applicationreferencedatasource-referencedatasource.html#cfn-kinesisanalytics-applicationreferencedatasource-referencedatasource-s3referencedatasource
            """
            return self._values.get('s3_reference_data_source')

        @property
        def table_name(self) -> typing.Optional[str]:
            """``CfnApplicationReferenceDataSource.ReferenceDataSourceProperty.TableName``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalytics-applicationreferencedatasource-referencedatasource.html#cfn-kinesisanalytics-applicationreferencedatasource-referencedatasource-tablename
            """
            return self._values.get('table_name')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'ReferenceDataSourceProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisanalytics.CfnApplicationReferenceDataSource.ReferenceSchemaProperty", jsii_struct_bases=[], name_mapping={'record_columns': 'recordColumns', 'record_format': 'recordFormat', 'record_encoding': 'recordEncoding'})
    class ReferenceSchemaProperty():
        def __init__(self, *, record_columns: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnApplicationReferenceDataSource.RecordColumnProperty"]]], record_format: typing.Union[aws_cdk.core.IResolvable, "CfnApplicationReferenceDataSource.RecordFormatProperty"], record_encoding: typing.Optional[str]=None):
            """
            :param record_columns: ``CfnApplicationReferenceDataSource.ReferenceSchemaProperty.RecordColumns``.
            :param record_format: ``CfnApplicationReferenceDataSource.ReferenceSchemaProperty.RecordFormat``.
            :param record_encoding: ``CfnApplicationReferenceDataSource.ReferenceSchemaProperty.RecordEncoding``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalytics-applicationreferencedatasource-referenceschema.html
            """
            self._values = {
                'record_columns': record_columns,
                'record_format': record_format,
            }
            if record_encoding is not None: self._values["record_encoding"] = record_encoding

        @property
        def record_columns(self) -> typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnApplicationReferenceDataSource.RecordColumnProperty"]]]:
            """``CfnApplicationReferenceDataSource.ReferenceSchemaProperty.RecordColumns``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalytics-applicationreferencedatasource-referenceschema.html#cfn-kinesisanalytics-applicationreferencedatasource-referenceschema-recordcolumns
            """
            return self._values.get('record_columns')

        @property
        def record_format(self) -> typing.Union[aws_cdk.core.IResolvable, "CfnApplicationReferenceDataSource.RecordFormatProperty"]:
            """``CfnApplicationReferenceDataSource.ReferenceSchemaProperty.RecordFormat``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalytics-applicationreferencedatasource-referenceschema.html#cfn-kinesisanalytics-applicationreferencedatasource-referenceschema-recordformat
            """
            return self._values.get('record_format')

        @property
        def record_encoding(self) -> typing.Optional[str]:
            """``CfnApplicationReferenceDataSource.ReferenceSchemaProperty.RecordEncoding``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalytics-applicationreferencedatasource-referenceschema.html#cfn-kinesisanalytics-applicationreferencedatasource-referenceschema-recordencoding
            """
            return self._values.get('record_encoding')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'ReferenceSchemaProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisanalytics.CfnApplicationReferenceDataSource.S3ReferenceDataSourceProperty", jsii_struct_bases=[], name_mapping={'bucket_arn': 'bucketArn', 'file_key': 'fileKey', 'reference_role_arn': 'referenceRoleArn'})
    class S3ReferenceDataSourceProperty():
        def __init__(self, *, bucket_arn: str, file_key: str, reference_role_arn: str):
            """
            :param bucket_arn: ``CfnApplicationReferenceDataSource.S3ReferenceDataSourceProperty.BucketARN``.
            :param file_key: ``CfnApplicationReferenceDataSource.S3ReferenceDataSourceProperty.FileKey``.
            :param reference_role_arn: ``CfnApplicationReferenceDataSource.S3ReferenceDataSourceProperty.ReferenceRoleARN``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalytics-applicationreferencedatasource-s3referencedatasource.html
            """
            self._values = {
                'bucket_arn': bucket_arn,
                'file_key': file_key,
                'reference_role_arn': reference_role_arn,
            }

        @property
        def bucket_arn(self) -> str:
            """``CfnApplicationReferenceDataSource.S3ReferenceDataSourceProperty.BucketARN``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalytics-applicationreferencedatasource-s3referencedatasource.html#cfn-kinesisanalytics-applicationreferencedatasource-s3referencedatasource-bucketarn
            """
            return self._values.get('bucket_arn')

        @property
        def file_key(self) -> str:
            """``CfnApplicationReferenceDataSource.S3ReferenceDataSourceProperty.FileKey``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalytics-applicationreferencedatasource-s3referencedatasource.html#cfn-kinesisanalytics-applicationreferencedatasource-s3referencedatasource-filekey
            """
            return self._values.get('file_key')

        @property
        def reference_role_arn(self) -> str:
            """``CfnApplicationReferenceDataSource.S3ReferenceDataSourceProperty.ReferenceRoleARN``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalytics-applicationreferencedatasource-s3referencedatasource.html#cfn-kinesisanalytics-applicationreferencedatasource-s3referencedatasource-referencerolearn
            """
            return self._values.get('reference_role_arn')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'S3ReferenceDataSourceProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



@jsii.data_type(jsii_type="@aws-cdk/aws-kinesisanalytics.CfnApplicationReferenceDataSourceProps", jsii_struct_bases=[], name_mapping={'application_name': 'applicationName', 'reference_data_source': 'referenceDataSource'})
class CfnApplicationReferenceDataSourceProps():
    def __init__(self, *, application_name: str, reference_data_source: typing.Union[aws_cdk.core.IResolvable, "CfnApplicationReferenceDataSource.ReferenceDataSourceProperty"]):
        """Properties for defining a ``AWS::KinesisAnalytics::ApplicationReferenceDataSource``.

        :param application_name: ``AWS::KinesisAnalytics::ApplicationReferenceDataSource.ApplicationName``.
        :param reference_data_source: ``AWS::KinesisAnalytics::ApplicationReferenceDataSource.ReferenceDataSource``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisanalytics-applicationreferencedatasource.html
        """
        self._values = {
            'application_name': application_name,
            'reference_data_source': reference_data_source,
        }

    @property
    def application_name(self) -> str:
        """``AWS::KinesisAnalytics::ApplicationReferenceDataSource.ApplicationName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisanalytics-applicationreferencedatasource.html#cfn-kinesisanalytics-applicationreferencedatasource-applicationname
        """
        return self._values.get('application_name')

    @property
    def reference_data_source(self) -> typing.Union[aws_cdk.core.IResolvable, "CfnApplicationReferenceDataSource.ReferenceDataSourceProperty"]:
        """``AWS::KinesisAnalytics::ApplicationReferenceDataSource.ReferenceDataSource``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisanalytics-applicationreferencedatasource.html#cfn-kinesisanalytics-applicationreferencedatasource-referencedatasource
        """
        return self._values.get('reference_data_source')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnApplicationReferenceDataSourceProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnApplicationReferenceDataSourceV2(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-kinesisanalytics.CfnApplicationReferenceDataSourceV2"):
    """A CloudFormation ``AWS::KinesisAnalyticsV2::ApplicationReferenceDataSource``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisanalyticsv2-applicationreferencedatasource.html
    cloudformationResource:
    :cloudformationResource:: AWS::KinesisAnalyticsV2::ApplicationReferenceDataSource
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, application_name: str, reference_data_source: typing.Union[aws_cdk.core.IResolvable, "ReferenceDataSourceProperty"]) -> None:
        """Create a new ``AWS::KinesisAnalyticsV2::ApplicationReferenceDataSource``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param application_name: ``AWS::KinesisAnalyticsV2::ApplicationReferenceDataSource.ApplicationName``.
        :param reference_data_source: ``AWS::KinesisAnalyticsV2::ApplicationReferenceDataSource.ReferenceDataSource``.
        """
        props = CfnApplicationReferenceDataSourceV2Props(application_name=application_name, reference_data_source=reference_data_source)

        jsii.create(CfnApplicationReferenceDataSourceV2, self, [scope, id, props])

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
    @jsii.member(jsii_name="applicationName")
    def application_name(self) -> str:
        """``AWS::KinesisAnalyticsV2::ApplicationReferenceDataSource.ApplicationName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisanalyticsv2-applicationreferencedatasource.html#cfn-kinesisanalyticsv2-applicationreferencedatasource-applicationname
        """
        return jsii.get(self, "applicationName")

    @application_name.setter
    def application_name(self, value: str):
        return jsii.set(self, "applicationName", value)

    @property
    @jsii.member(jsii_name="referenceDataSource")
    def reference_data_source(self) -> typing.Union[aws_cdk.core.IResolvable, "ReferenceDataSourceProperty"]:
        """``AWS::KinesisAnalyticsV2::ApplicationReferenceDataSource.ReferenceDataSource``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisanalyticsv2-applicationreferencedatasource.html#cfn-kinesisanalyticsv2-applicationreferencedatasource-referencedatasource
        """
        return jsii.get(self, "referenceDataSource")

    @reference_data_source.setter
    def reference_data_source(self, value: typing.Union[aws_cdk.core.IResolvable, "ReferenceDataSourceProperty"]):
        return jsii.set(self, "referenceDataSource", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisanalytics.CfnApplicationReferenceDataSourceV2.CSVMappingParametersProperty", jsii_struct_bases=[], name_mapping={'record_column_delimiter': 'recordColumnDelimiter', 'record_row_delimiter': 'recordRowDelimiter'})
    class CSVMappingParametersProperty():
        def __init__(self, *, record_column_delimiter: str, record_row_delimiter: str):
            """
            :param record_column_delimiter: ``CfnApplicationReferenceDataSourceV2.CSVMappingParametersProperty.RecordColumnDelimiter``.
            :param record_row_delimiter: ``CfnApplicationReferenceDataSourceV2.CSVMappingParametersProperty.RecordRowDelimiter``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-applicationreferencedatasource-csvmappingparameters.html
            """
            self._values = {
                'record_column_delimiter': record_column_delimiter,
                'record_row_delimiter': record_row_delimiter,
            }

        @property
        def record_column_delimiter(self) -> str:
            """``CfnApplicationReferenceDataSourceV2.CSVMappingParametersProperty.RecordColumnDelimiter``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-applicationreferencedatasource-csvmappingparameters.html#cfn-kinesisanalyticsv2-applicationreferencedatasource-csvmappingparameters-recordcolumndelimiter
            """
            return self._values.get('record_column_delimiter')

        @property
        def record_row_delimiter(self) -> str:
            """``CfnApplicationReferenceDataSourceV2.CSVMappingParametersProperty.RecordRowDelimiter``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-applicationreferencedatasource-csvmappingparameters.html#cfn-kinesisanalyticsv2-applicationreferencedatasource-csvmappingparameters-recordrowdelimiter
            """
            return self._values.get('record_row_delimiter')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'CSVMappingParametersProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisanalytics.CfnApplicationReferenceDataSourceV2.JSONMappingParametersProperty", jsii_struct_bases=[], name_mapping={'record_row_path': 'recordRowPath'})
    class JSONMappingParametersProperty():
        def __init__(self, *, record_row_path: str):
            """
            :param record_row_path: ``CfnApplicationReferenceDataSourceV2.JSONMappingParametersProperty.RecordRowPath``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-applicationreferencedatasource-jsonmappingparameters.html
            """
            self._values = {
                'record_row_path': record_row_path,
            }

        @property
        def record_row_path(self) -> str:
            """``CfnApplicationReferenceDataSourceV2.JSONMappingParametersProperty.RecordRowPath``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-applicationreferencedatasource-jsonmappingparameters.html#cfn-kinesisanalyticsv2-applicationreferencedatasource-jsonmappingparameters-recordrowpath
            """
            return self._values.get('record_row_path')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'JSONMappingParametersProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisanalytics.CfnApplicationReferenceDataSourceV2.MappingParametersProperty", jsii_struct_bases=[], name_mapping={'csv_mapping_parameters': 'csvMappingParameters', 'json_mapping_parameters': 'jsonMappingParameters'})
    class MappingParametersProperty():
        def __init__(self, *, csv_mapping_parameters: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnApplicationReferenceDataSourceV2.CSVMappingParametersProperty"]]]=None, json_mapping_parameters: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnApplicationReferenceDataSourceV2.JSONMappingParametersProperty"]]]=None):
            """
            :param csv_mapping_parameters: ``CfnApplicationReferenceDataSourceV2.MappingParametersProperty.CSVMappingParameters``.
            :param json_mapping_parameters: ``CfnApplicationReferenceDataSourceV2.MappingParametersProperty.JSONMappingParameters``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-applicationreferencedatasource-mappingparameters.html
            """
            self._values = {
            }
            if csv_mapping_parameters is not None: self._values["csv_mapping_parameters"] = csv_mapping_parameters
            if json_mapping_parameters is not None: self._values["json_mapping_parameters"] = json_mapping_parameters

        @property
        def csv_mapping_parameters(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnApplicationReferenceDataSourceV2.CSVMappingParametersProperty"]]]:
            """``CfnApplicationReferenceDataSourceV2.MappingParametersProperty.CSVMappingParameters``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-applicationreferencedatasource-mappingparameters.html#cfn-kinesisanalyticsv2-applicationreferencedatasource-mappingparameters-csvmappingparameters
            """
            return self._values.get('csv_mapping_parameters')

        @property
        def json_mapping_parameters(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnApplicationReferenceDataSourceV2.JSONMappingParametersProperty"]]]:
            """``CfnApplicationReferenceDataSourceV2.MappingParametersProperty.JSONMappingParameters``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-applicationreferencedatasource-mappingparameters.html#cfn-kinesisanalyticsv2-applicationreferencedatasource-mappingparameters-jsonmappingparameters
            """
            return self._values.get('json_mapping_parameters')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'MappingParametersProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisanalytics.CfnApplicationReferenceDataSourceV2.RecordColumnProperty", jsii_struct_bases=[], name_mapping={'name': 'name', 'sql_type': 'sqlType', 'mapping': 'mapping'})
    class RecordColumnProperty():
        def __init__(self, *, name: str, sql_type: str, mapping: typing.Optional[str]=None):
            """
            :param name: ``CfnApplicationReferenceDataSourceV2.RecordColumnProperty.Name``.
            :param sql_type: ``CfnApplicationReferenceDataSourceV2.RecordColumnProperty.SqlType``.
            :param mapping: ``CfnApplicationReferenceDataSourceV2.RecordColumnProperty.Mapping``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-applicationreferencedatasource-recordcolumn.html
            """
            self._values = {
                'name': name,
                'sql_type': sql_type,
            }
            if mapping is not None: self._values["mapping"] = mapping

        @property
        def name(self) -> str:
            """``CfnApplicationReferenceDataSourceV2.RecordColumnProperty.Name``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-applicationreferencedatasource-recordcolumn.html#cfn-kinesisanalyticsv2-applicationreferencedatasource-recordcolumn-name
            """
            return self._values.get('name')

        @property
        def sql_type(self) -> str:
            """``CfnApplicationReferenceDataSourceV2.RecordColumnProperty.SqlType``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-applicationreferencedatasource-recordcolumn.html#cfn-kinesisanalyticsv2-applicationreferencedatasource-recordcolumn-sqltype
            """
            return self._values.get('sql_type')

        @property
        def mapping(self) -> typing.Optional[str]:
            """``CfnApplicationReferenceDataSourceV2.RecordColumnProperty.Mapping``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-applicationreferencedatasource-recordcolumn.html#cfn-kinesisanalyticsv2-applicationreferencedatasource-recordcolumn-mapping
            """
            return self._values.get('mapping')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'RecordColumnProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisanalytics.CfnApplicationReferenceDataSourceV2.RecordFormatProperty", jsii_struct_bases=[], name_mapping={'record_format_type': 'recordFormatType', 'mapping_parameters': 'mappingParameters'})
    class RecordFormatProperty():
        def __init__(self, *, record_format_type: str, mapping_parameters: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnApplicationReferenceDataSourceV2.MappingParametersProperty"]]]=None):
            """
            :param record_format_type: ``CfnApplicationReferenceDataSourceV2.RecordFormatProperty.RecordFormatType``.
            :param mapping_parameters: ``CfnApplicationReferenceDataSourceV2.RecordFormatProperty.MappingParameters``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-applicationreferencedatasource-recordformat.html
            """
            self._values = {
                'record_format_type': record_format_type,
            }
            if mapping_parameters is not None: self._values["mapping_parameters"] = mapping_parameters

        @property
        def record_format_type(self) -> str:
            """``CfnApplicationReferenceDataSourceV2.RecordFormatProperty.RecordFormatType``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-applicationreferencedatasource-recordformat.html#cfn-kinesisanalyticsv2-applicationreferencedatasource-recordformat-recordformattype
            """
            return self._values.get('record_format_type')

        @property
        def mapping_parameters(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnApplicationReferenceDataSourceV2.MappingParametersProperty"]]]:
            """``CfnApplicationReferenceDataSourceV2.RecordFormatProperty.MappingParameters``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-applicationreferencedatasource-recordformat.html#cfn-kinesisanalyticsv2-applicationreferencedatasource-recordformat-mappingparameters
            """
            return self._values.get('mapping_parameters')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'RecordFormatProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisanalytics.CfnApplicationReferenceDataSourceV2.ReferenceDataSourceProperty", jsii_struct_bases=[], name_mapping={'reference_schema': 'referenceSchema', 's3_reference_data_source': 's3ReferenceDataSource', 'table_name': 'tableName'})
    class ReferenceDataSourceProperty():
        def __init__(self, *, reference_schema: typing.Union[aws_cdk.core.IResolvable, "CfnApplicationReferenceDataSourceV2.ReferenceSchemaProperty"], s3_reference_data_source: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnApplicationReferenceDataSourceV2.S3ReferenceDataSourceProperty"]]]=None, table_name: typing.Optional[str]=None):
            """
            :param reference_schema: ``CfnApplicationReferenceDataSourceV2.ReferenceDataSourceProperty.ReferenceSchema``.
            :param s3_reference_data_source: ``CfnApplicationReferenceDataSourceV2.ReferenceDataSourceProperty.S3ReferenceDataSource``.
            :param table_name: ``CfnApplicationReferenceDataSourceV2.ReferenceDataSourceProperty.TableName``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-applicationreferencedatasource-referencedatasource.html
            """
            self._values = {
                'reference_schema': reference_schema,
            }
            if s3_reference_data_source is not None: self._values["s3_reference_data_source"] = s3_reference_data_source
            if table_name is not None: self._values["table_name"] = table_name

        @property
        def reference_schema(self) -> typing.Union[aws_cdk.core.IResolvable, "CfnApplicationReferenceDataSourceV2.ReferenceSchemaProperty"]:
            """``CfnApplicationReferenceDataSourceV2.ReferenceDataSourceProperty.ReferenceSchema``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-applicationreferencedatasource-referencedatasource.html#cfn-kinesisanalyticsv2-applicationreferencedatasource-referencedatasource-referenceschema
            """
            return self._values.get('reference_schema')

        @property
        def s3_reference_data_source(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnApplicationReferenceDataSourceV2.S3ReferenceDataSourceProperty"]]]:
            """``CfnApplicationReferenceDataSourceV2.ReferenceDataSourceProperty.S3ReferenceDataSource``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-applicationreferencedatasource-referencedatasource.html#cfn-kinesisanalyticsv2-applicationreferencedatasource-referencedatasource-s3referencedatasource
            """
            return self._values.get('s3_reference_data_source')

        @property
        def table_name(self) -> typing.Optional[str]:
            """``CfnApplicationReferenceDataSourceV2.ReferenceDataSourceProperty.TableName``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-applicationreferencedatasource-referencedatasource.html#cfn-kinesisanalyticsv2-applicationreferencedatasource-referencedatasource-tablename
            """
            return self._values.get('table_name')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'ReferenceDataSourceProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisanalytics.CfnApplicationReferenceDataSourceV2.ReferenceSchemaProperty", jsii_struct_bases=[], name_mapping={'record_columns': 'recordColumns', 'record_format': 'recordFormat', 'record_encoding': 'recordEncoding'})
    class ReferenceSchemaProperty():
        def __init__(self, *, record_columns: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnApplicationReferenceDataSourceV2.RecordColumnProperty"]]], record_format: typing.Union[aws_cdk.core.IResolvable, "CfnApplicationReferenceDataSourceV2.RecordFormatProperty"], record_encoding: typing.Optional[str]=None):
            """
            :param record_columns: ``CfnApplicationReferenceDataSourceV2.ReferenceSchemaProperty.RecordColumns``.
            :param record_format: ``CfnApplicationReferenceDataSourceV2.ReferenceSchemaProperty.RecordFormat``.
            :param record_encoding: ``CfnApplicationReferenceDataSourceV2.ReferenceSchemaProperty.RecordEncoding``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-applicationreferencedatasource-referenceschema.html
            """
            self._values = {
                'record_columns': record_columns,
                'record_format': record_format,
            }
            if record_encoding is not None: self._values["record_encoding"] = record_encoding

        @property
        def record_columns(self) -> typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnApplicationReferenceDataSourceV2.RecordColumnProperty"]]]:
            """``CfnApplicationReferenceDataSourceV2.ReferenceSchemaProperty.RecordColumns``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-applicationreferencedatasource-referenceschema.html#cfn-kinesisanalyticsv2-applicationreferencedatasource-referenceschema-recordcolumns
            """
            return self._values.get('record_columns')

        @property
        def record_format(self) -> typing.Union[aws_cdk.core.IResolvable, "CfnApplicationReferenceDataSourceV2.RecordFormatProperty"]:
            """``CfnApplicationReferenceDataSourceV2.ReferenceSchemaProperty.RecordFormat``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-applicationreferencedatasource-referenceschema.html#cfn-kinesisanalyticsv2-applicationreferencedatasource-referenceschema-recordformat
            """
            return self._values.get('record_format')

        @property
        def record_encoding(self) -> typing.Optional[str]:
            """``CfnApplicationReferenceDataSourceV2.ReferenceSchemaProperty.RecordEncoding``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-applicationreferencedatasource-referenceschema.html#cfn-kinesisanalyticsv2-applicationreferencedatasource-referenceschema-recordencoding
            """
            return self._values.get('record_encoding')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'ReferenceSchemaProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisanalytics.CfnApplicationReferenceDataSourceV2.S3ReferenceDataSourceProperty", jsii_struct_bases=[], name_mapping={'bucket_arn': 'bucketArn', 'file_key': 'fileKey'})
    class S3ReferenceDataSourceProperty():
        def __init__(self, *, bucket_arn: str, file_key: str):
            """
            :param bucket_arn: ``CfnApplicationReferenceDataSourceV2.S3ReferenceDataSourceProperty.BucketARN``.
            :param file_key: ``CfnApplicationReferenceDataSourceV2.S3ReferenceDataSourceProperty.FileKey``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-applicationreferencedatasource-s3referencedatasource.html
            """
            self._values = {
                'bucket_arn': bucket_arn,
                'file_key': file_key,
            }

        @property
        def bucket_arn(self) -> str:
            """``CfnApplicationReferenceDataSourceV2.S3ReferenceDataSourceProperty.BucketARN``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-applicationreferencedatasource-s3referencedatasource.html#cfn-kinesisanalyticsv2-applicationreferencedatasource-s3referencedatasource-bucketarn
            """
            return self._values.get('bucket_arn')

        @property
        def file_key(self) -> str:
            """``CfnApplicationReferenceDataSourceV2.S3ReferenceDataSourceProperty.FileKey``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-applicationreferencedatasource-s3referencedatasource.html#cfn-kinesisanalyticsv2-applicationreferencedatasource-s3referencedatasource-filekey
            """
            return self._values.get('file_key')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'S3ReferenceDataSourceProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



@jsii.data_type(jsii_type="@aws-cdk/aws-kinesisanalytics.CfnApplicationReferenceDataSourceV2Props", jsii_struct_bases=[], name_mapping={'application_name': 'applicationName', 'reference_data_source': 'referenceDataSource'})
class CfnApplicationReferenceDataSourceV2Props():
    def __init__(self, *, application_name: str, reference_data_source: typing.Union[aws_cdk.core.IResolvable, "CfnApplicationReferenceDataSourceV2.ReferenceDataSourceProperty"]):
        """Properties for defining a ``AWS::KinesisAnalyticsV2::ApplicationReferenceDataSource``.

        :param application_name: ``AWS::KinesisAnalyticsV2::ApplicationReferenceDataSource.ApplicationName``.
        :param reference_data_source: ``AWS::KinesisAnalyticsV2::ApplicationReferenceDataSource.ReferenceDataSource``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisanalyticsv2-applicationreferencedatasource.html
        """
        self._values = {
            'application_name': application_name,
            'reference_data_source': reference_data_source,
        }

    @property
    def application_name(self) -> str:
        """``AWS::KinesisAnalyticsV2::ApplicationReferenceDataSource.ApplicationName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisanalyticsv2-applicationreferencedatasource.html#cfn-kinesisanalyticsv2-applicationreferencedatasource-applicationname
        """
        return self._values.get('application_name')

    @property
    def reference_data_source(self) -> typing.Union[aws_cdk.core.IResolvable, "CfnApplicationReferenceDataSourceV2.ReferenceDataSourceProperty"]:
        """``AWS::KinesisAnalyticsV2::ApplicationReferenceDataSource.ReferenceDataSource``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisanalyticsv2-applicationreferencedatasource.html#cfn-kinesisanalyticsv2-applicationreferencedatasource-referencedatasource
        """
        return self._values.get('reference_data_source')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnApplicationReferenceDataSourceV2Props(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnApplicationV2(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-kinesisanalytics.CfnApplicationV2"):
    """A CloudFormation ``AWS::KinesisAnalyticsV2::Application``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisanalyticsv2-application.html
    cloudformationResource:
    :cloudformationResource:: AWS::KinesisAnalyticsV2::Application
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, runtime_environment: str, service_execution_role: str, application_configuration: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["ApplicationConfigurationProperty"]]]=None, application_description: typing.Optional[str]=None, application_name: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::KinesisAnalyticsV2::Application``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param runtime_environment: ``AWS::KinesisAnalyticsV2::Application.RuntimeEnvironment``.
        :param service_execution_role: ``AWS::KinesisAnalyticsV2::Application.ServiceExecutionRole``.
        :param application_configuration: ``AWS::KinesisAnalyticsV2::Application.ApplicationConfiguration``.
        :param application_description: ``AWS::KinesisAnalyticsV2::Application.ApplicationDescription``.
        :param application_name: ``AWS::KinesisAnalyticsV2::Application.ApplicationName``.
        """
        props = CfnApplicationV2Props(runtime_environment=runtime_environment, service_execution_role=service_execution_role, application_configuration=application_configuration, application_description=application_description, application_name=application_name)

        jsii.create(CfnApplicationV2, self, [scope, id, props])

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
    @jsii.member(jsii_name="runtimeEnvironment")
    def runtime_environment(self) -> str:
        """``AWS::KinesisAnalyticsV2::Application.RuntimeEnvironment``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisanalyticsv2-application.html#cfn-kinesisanalyticsv2-application-runtimeenvironment
        """
        return jsii.get(self, "runtimeEnvironment")

    @runtime_environment.setter
    def runtime_environment(self, value: str):
        return jsii.set(self, "runtimeEnvironment", value)

    @property
    @jsii.member(jsii_name="serviceExecutionRole")
    def service_execution_role(self) -> str:
        """``AWS::KinesisAnalyticsV2::Application.ServiceExecutionRole``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisanalyticsv2-application.html#cfn-kinesisanalyticsv2-application-serviceexecutionrole
        """
        return jsii.get(self, "serviceExecutionRole")

    @service_execution_role.setter
    def service_execution_role(self, value: str):
        return jsii.set(self, "serviceExecutionRole", value)

    @property
    @jsii.member(jsii_name="applicationConfiguration")
    def application_configuration(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["ApplicationConfigurationProperty"]]]:
        """``AWS::KinesisAnalyticsV2::Application.ApplicationConfiguration``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisanalyticsv2-application.html#cfn-kinesisanalyticsv2-application-applicationconfiguration
        """
        return jsii.get(self, "applicationConfiguration")

    @application_configuration.setter
    def application_configuration(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["ApplicationConfigurationProperty"]]]):
        return jsii.set(self, "applicationConfiguration", value)

    @property
    @jsii.member(jsii_name="applicationDescription")
    def application_description(self) -> typing.Optional[str]:
        """``AWS::KinesisAnalyticsV2::Application.ApplicationDescription``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisanalyticsv2-application.html#cfn-kinesisanalyticsv2-application-applicationdescription
        """
        return jsii.get(self, "applicationDescription")

    @application_description.setter
    def application_description(self, value: typing.Optional[str]):
        return jsii.set(self, "applicationDescription", value)

    @property
    @jsii.member(jsii_name="applicationName")
    def application_name(self) -> typing.Optional[str]:
        """``AWS::KinesisAnalyticsV2::Application.ApplicationName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisanalyticsv2-application.html#cfn-kinesisanalyticsv2-application-applicationname
        """
        return jsii.get(self, "applicationName")

    @application_name.setter
    def application_name(self, value: typing.Optional[str]):
        return jsii.set(self, "applicationName", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisanalytics.CfnApplicationV2.ApplicationCodeConfigurationProperty", jsii_struct_bases=[], name_mapping={'code_content': 'codeContent', 'code_content_type': 'codeContentType'})
    class ApplicationCodeConfigurationProperty():
        def __init__(self, *, code_content: typing.Union[aws_cdk.core.IResolvable, "CfnApplicationV2.CodeContentProperty"], code_content_type: str):
            """
            :param code_content: ``CfnApplicationV2.ApplicationCodeConfigurationProperty.CodeContent``.
            :param code_content_type: ``CfnApplicationV2.ApplicationCodeConfigurationProperty.CodeContentType``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-application-applicationcodeconfiguration.html
            """
            self._values = {
                'code_content': code_content,
                'code_content_type': code_content_type,
            }

        @property
        def code_content(self) -> typing.Union[aws_cdk.core.IResolvable, "CfnApplicationV2.CodeContentProperty"]:
            """``CfnApplicationV2.ApplicationCodeConfigurationProperty.CodeContent``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-application-applicationcodeconfiguration.html#cfn-kinesisanalyticsv2-application-applicationcodeconfiguration-codecontent
            """
            return self._values.get('code_content')

        @property
        def code_content_type(self) -> str:
            """``CfnApplicationV2.ApplicationCodeConfigurationProperty.CodeContentType``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-application-applicationcodeconfiguration.html#cfn-kinesisanalyticsv2-application-applicationcodeconfiguration-codecontenttype
            """
            return self._values.get('code_content_type')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'ApplicationCodeConfigurationProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisanalytics.CfnApplicationV2.ApplicationConfigurationProperty", jsii_struct_bases=[], name_mapping={'application_code_configuration': 'applicationCodeConfiguration', 'application_snapshot_configuration': 'applicationSnapshotConfiguration', 'environment_properties': 'environmentProperties', 'flink_application_configuration': 'flinkApplicationConfiguration', 'sql_application_configuration': 'sqlApplicationConfiguration'})
    class ApplicationConfigurationProperty():
        def __init__(self, *, application_code_configuration: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnApplicationV2.ApplicationCodeConfigurationProperty"]]]=None, application_snapshot_configuration: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnApplicationV2.ApplicationSnapshotConfigurationProperty"]]]=None, environment_properties: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnApplicationV2.EnvironmentPropertiesProperty"]]]=None, flink_application_configuration: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnApplicationV2.FlinkApplicationConfigurationProperty"]]]=None, sql_application_configuration: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnApplicationV2.SqlApplicationConfigurationProperty"]]]=None):
            """
            :param application_code_configuration: ``CfnApplicationV2.ApplicationConfigurationProperty.ApplicationCodeConfiguration``.
            :param application_snapshot_configuration: ``CfnApplicationV2.ApplicationConfigurationProperty.ApplicationSnapshotConfiguration``.
            :param environment_properties: ``CfnApplicationV2.ApplicationConfigurationProperty.EnvironmentProperties``.
            :param flink_application_configuration: ``CfnApplicationV2.ApplicationConfigurationProperty.FlinkApplicationConfiguration``.
            :param sql_application_configuration: ``CfnApplicationV2.ApplicationConfigurationProperty.SqlApplicationConfiguration``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-application-applicationconfiguration.html
            """
            self._values = {
            }
            if application_code_configuration is not None: self._values["application_code_configuration"] = application_code_configuration
            if application_snapshot_configuration is not None: self._values["application_snapshot_configuration"] = application_snapshot_configuration
            if environment_properties is not None: self._values["environment_properties"] = environment_properties
            if flink_application_configuration is not None: self._values["flink_application_configuration"] = flink_application_configuration
            if sql_application_configuration is not None: self._values["sql_application_configuration"] = sql_application_configuration

        @property
        def application_code_configuration(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnApplicationV2.ApplicationCodeConfigurationProperty"]]]:
            """``CfnApplicationV2.ApplicationConfigurationProperty.ApplicationCodeConfiguration``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-application-applicationconfiguration.html#cfn-kinesisanalyticsv2-application-applicationconfiguration-applicationcodeconfiguration
            """
            return self._values.get('application_code_configuration')

        @property
        def application_snapshot_configuration(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnApplicationV2.ApplicationSnapshotConfigurationProperty"]]]:
            """``CfnApplicationV2.ApplicationConfigurationProperty.ApplicationSnapshotConfiguration``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-application-applicationconfiguration.html#cfn-kinesisanalyticsv2-application-applicationconfiguration-applicationsnapshotconfiguration
            """
            return self._values.get('application_snapshot_configuration')

        @property
        def environment_properties(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnApplicationV2.EnvironmentPropertiesProperty"]]]:
            """``CfnApplicationV2.ApplicationConfigurationProperty.EnvironmentProperties``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-application-applicationconfiguration.html#cfn-kinesisanalyticsv2-application-applicationconfiguration-environmentproperties
            """
            return self._values.get('environment_properties')

        @property
        def flink_application_configuration(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnApplicationV2.FlinkApplicationConfigurationProperty"]]]:
            """``CfnApplicationV2.ApplicationConfigurationProperty.FlinkApplicationConfiguration``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-application-applicationconfiguration.html#cfn-kinesisanalyticsv2-application-applicationconfiguration-flinkapplicationconfiguration
            """
            return self._values.get('flink_application_configuration')

        @property
        def sql_application_configuration(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnApplicationV2.SqlApplicationConfigurationProperty"]]]:
            """``CfnApplicationV2.ApplicationConfigurationProperty.SqlApplicationConfiguration``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-application-applicationconfiguration.html#cfn-kinesisanalyticsv2-application-applicationconfiguration-sqlapplicationconfiguration
            """
            return self._values.get('sql_application_configuration')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'ApplicationConfigurationProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisanalytics.CfnApplicationV2.ApplicationSnapshotConfigurationProperty", jsii_struct_bases=[], name_mapping={'snapshots_enabled': 'snapshotsEnabled'})
    class ApplicationSnapshotConfigurationProperty():
        def __init__(self, *, snapshots_enabled: typing.Union[bool, aws_cdk.core.IResolvable]):
            """
            :param snapshots_enabled: ``CfnApplicationV2.ApplicationSnapshotConfigurationProperty.SnapshotsEnabled``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-application-applicationsnapshotconfiguration.html
            """
            self._values = {
                'snapshots_enabled': snapshots_enabled,
            }

        @property
        def snapshots_enabled(self) -> typing.Union[bool, aws_cdk.core.IResolvable]:
            """``CfnApplicationV2.ApplicationSnapshotConfigurationProperty.SnapshotsEnabled``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-application-applicationsnapshotconfiguration.html#cfn-kinesisanalyticsv2-application-applicationsnapshotconfiguration-snapshotsenabled
            """
            return self._values.get('snapshots_enabled')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'ApplicationSnapshotConfigurationProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisanalytics.CfnApplicationV2.CSVMappingParametersProperty", jsii_struct_bases=[], name_mapping={'record_column_delimiter': 'recordColumnDelimiter', 'record_row_delimiter': 'recordRowDelimiter'})
    class CSVMappingParametersProperty():
        def __init__(self, *, record_column_delimiter: str, record_row_delimiter: str):
            """
            :param record_column_delimiter: ``CfnApplicationV2.CSVMappingParametersProperty.RecordColumnDelimiter``.
            :param record_row_delimiter: ``CfnApplicationV2.CSVMappingParametersProperty.RecordRowDelimiter``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-application-csvmappingparameters.html
            """
            self._values = {
                'record_column_delimiter': record_column_delimiter,
                'record_row_delimiter': record_row_delimiter,
            }

        @property
        def record_column_delimiter(self) -> str:
            """``CfnApplicationV2.CSVMappingParametersProperty.RecordColumnDelimiter``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-application-csvmappingparameters.html#cfn-kinesisanalyticsv2-application-csvmappingparameters-recordcolumndelimiter
            """
            return self._values.get('record_column_delimiter')

        @property
        def record_row_delimiter(self) -> str:
            """``CfnApplicationV2.CSVMappingParametersProperty.RecordRowDelimiter``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-application-csvmappingparameters.html#cfn-kinesisanalyticsv2-application-csvmappingparameters-recordrowdelimiter
            """
            return self._values.get('record_row_delimiter')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'CSVMappingParametersProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisanalytics.CfnApplicationV2.CheckpointConfigurationProperty", jsii_struct_bases=[], name_mapping={'configuration_type': 'configurationType', 'checkpointing_enabled': 'checkpointingEnabled', 'checkpoint_interval': 'checkpointInterval', 'min_pause_between_checkpoints': 'minPauseBetweenCheckpoints'})
    class CheckpointConfigurationProperty():
        def __init__(self, *, configuration_type: str, checkpointing_enabled: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, checkpoint_interval: typing.Optional[jsii.Number]=None, min_pause_between_checkpoints: typing.Optional[jsii.Number]=None):
            """
            :param configuration_type: ``CfnApplicationV2.CheckpointConfigurationProperty.ConfigurationType``.
            :param checkpointing_enabled: ``CfnApplicationV2.CheckpointConfigurationProperty.CheckpointingEnabled``.
            :param checkpoint_interval: ``CfnApplicationV2.CheckpointConfigurationProperty.CheckpointInterval``.
            :param min_pause_between_checkpoints: ``CfnApplicationV2.CheckpointConfigurationProperty.MinPauseBetweenCheckpoints``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-application-checkpointconfiguration.html
            """
            self._values = {
                'configuration_type': configuration_type,
            }
            if checkpointing_enabled is not None: self._values["checkpointing_enabled"] = checkpointing_enabled
            if checkpoint_interval is not None: self._values["checkpoint_interval"] = checkpoint_interval
            if min_pause_between_checkpoints is not None: self._values["min_pause_between_checkpoints"] = min_pause_between_checkpoints

        @property
        def configuration_type(self) -> str:
            """``CfnApplicationV2.CheckpointConfigurationProperty.ConfigurationType``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-application-checkpointconfiguration.html#cfn-kinesisanalyticsv2-application-checkpointconfiguration-configurationtype
            """
            return self._values.get('configuration_type')

        @property
        def checkpointing_enabled(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
            """``CfnApplicationV2.CheckpointConfigurationProperty.CheckpointingEnabled``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-application-checkpointconfiguration.html#cfn-kinesisanalyticsv2-application-checkpointconfiguration-checkpointingenabled
            """
            return self._values.get('checkpointing_enabled')

        @property
        def checkpoint_interval(self) -> typing.Optional[jsii.Number]:
            """``CfnApplicationV2.CheckpointConfigurationProperty.CheckpointInterval``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-application-checkpointconfiguration.html#cfn-kinesisanalyticsv2-application-checkpointconfiguration-checkpointinterval
            """
            return self._values.get('checkpoint_interval')

        @property
        def min_pause_between_checkpoints(self) -> typing.Optional[jsii.Number]:
            """``CfnApplicationV2.CheckpointConfigurationProperty.MinPauseBetweenCheckpoints``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-application-checkpointconfiguration.html#cfn-kinesisanalyticsv2-application-checkpointconfiguration-minpausebetweencheckpoints
            """
            return self._values.get('min_pause_between_checkpoints')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'CheckpointConfigurationProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisanalytics.CfnApplicationV2.CodeContentProperty", jsii_struct_bases=[], name_mapping={'s3_content_location': 's3ContentLocation', 'text_content': 'textContent', 'zip_file_content': 'zipFileContent'})
    class CodeContentProperty():
        def __init__(self, *, s3_content_location: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnApplicationV2.S3ContentLocationProperty"]]]=None, text_content: typing.Optional[str]=None, zip_file_content: typing.Optional[str]=None):
            """
            :param s3_content_location: ``CfnApplicationV2.CodeContentProperty.S3ContentLocation``.
            :param text_content: ``CfnApplicationV2.CodeContentProperty.TextContent``.
            :param zip_file_content: ``CfnApplicationV2.CodeContentProperty.ZipFileContent``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-application-codecontent.html
            """
            self._values = {
            }
            if s3_content_location is not None: self._values["s3_content_location"] = s3_content_location
            if text_content is not None: self._values["text_content"] = text_content
            if zip_file_content is not None: self._values["zip_file_content"] = zip_file_content

        @property
        def s3_content_location(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnApplicationV2.S3ContentLocationProperty"]]]:
            """``CfnApplicationV2.CodeContentProperty.S3ContentLocation``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-application-codecontent.html#cfn-kinesisanalyticsv2-application-codecontent-s3contentlocation
            """
            return self._values.get('s3_content_location')

        @property
        def text_content(self) -> typing.Optional[str]:
            """``CfnApplicationV2.CodeContentProperty.TextContent``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-application-codecontent.html#cfn-kinesisanalyticsv2-application-codecontent-textcontent
            """
            return self._values.get('text_content')

        @property
        def zip_file_content(self) -> typing.Optional[str]:
            """``CfnApplicationV2.CodeContentProperty.ZipFileContent``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-application-codecontent.html#cfn-kinesisanalyticsv2-application-codecontent-zipfilecontent
            """
            return self._values.get('zip_file_content')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'CodeContentProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisanalytics.CfnApplicationV2.EnvironmentPropertiesProperty", jsii_struct_bases=[], name_mapping={'property_groups': 'propertyGroups'})
    class EnvironmentPropertiesProperty():
        def __init__(self, *, property_groups: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnApplicationV2.PropertyGroupProperty"]]]]]=None):
            """
            :param property_groups: ``CfnApplicationV2.EnvironmentPropertiesProperty.PropertyGroups``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-application-environmentproperties.html
            """
            self._values = {
            }
            if property_groups is not None: self._values["property_groups"] = property_groups

        @property
        def property_groups(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnApplicationV2.PropertyGroupProperty"]]]]]:
            """``CfnApplicationV2.EnvironmentPropertiesProperty.PropertyGroups``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-application-environmentproperties.html#cfn-kinesisanalyticsv2-application-environmentproperties-propertygroups
            """
            return self._values.get('property_groups')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'EnvironmentPropertiesProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisanalytics.CfnApplicationV2.FlinkApplicationConfigurationProperty", jsii_struct_bases=[], name_mapping={'checkpoint_configuration': 'checkpointConfiguration', 'monitoring_configuration': 'monitoringConfiguration', 'parallelism_configuration': 'parallelismConfiguration'})
    class FlinkApplicationConfigurationProperty():
        def __init__(self, *, checkpoint_configuration: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnApplicationV2.CheckpointConfigurationProperty"]]]=None, monitoring_configuration: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnApplicationV2.MonitoringConfigurationProperty"]]]=None, parallelism_configuration: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnApplicationV2.ParallelismConfigurationProperty"]]]=None):
            """
            :param checkpoint_configuration: ``CfnApplicationV2.FlinkApplicationConfigurationProperty.CheckpointConfiguration``.
            :param monitoring_configuration: ``CfnApplicationV2.FlinkApplicationConfigurationProperty.MonitoringConfiguration``.
            :param parallelism_configuration: ``CfnApplicationV2.FlinkApplicationConfigurationProperty.ParallelismConfiguration``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-application-flinkapplicationconfiguration.html
            """
            self._values = {
            }
            if checkpoint_configuration is not None: self._values["checkpoint_configuration"] = checkpoint_configuration
            if monitoring_configuration is not None: self._values["monitoring_configuration"] = monitoring_configuration
            if parallelism_configuration is not None: self._values["parallelism_configuration"] = parallelism_configuration

        @property
        def checkpoint_configuration(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnApplicationV2.CheckpointConfigurationProperty"]]]:
            """``CfnApplicationV2.FlinkApplicationConfigurationProperty.CheckpointConfiguration``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-application-flinkapplicationconfiguration.html#cfn-kinesisanalyticsv2-application-flinkapplicationconfiguration-checkpointconfiguration
            """
            return self._values.get('checkpoint_configuration')

        @property
        def monitoring_configuration(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnApplicationV2.MonitoringConfigurationProperty"]]]:
            """``CfnApplicationV2.FlinkApplicationConfigurationProperty.MonitoringConfiguration``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-application-flinkapplicationconfiguration.html#cfn-kinesisanalyticsv2-application-flinkapplicationconfiguration-monitoringconfiguration
            """
            return self._values.get('monitoring_configuration')

        @property
        def parallelism_configuration(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnApplicationV2.ParallelismConfigurationProperty"]]]:
            """``CfnApplicationV2.FlinkApplicationConfigurationProperty.ParallelismConfiguration``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-application-flinkapplicationconfiguration.html#cfn-kinesisanalyticsv2-application-flinkapplicationconfiguration-parallelismconfiguration
            """
            return self._values.get('parallelism_configuration')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'FlinkApplicationConfigurationProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisanalytics.CfnApplicationV2.InputLambdaProcessorProperty", jsii_struct_bases=[], name_mapping={'resource_arn': 'resourceArn'})
    class InputLambdaProcessorProperty():
        def __init__(self, *, resource_arn: str):
            """
            :param resource_arn: ``CfnApplicationV2.InputLambdaProcessorProperty.ResourceARN``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-application-inputlambdaprocessor.html
            """
            self._values = {
                'resource_arn': resource_arn,
            }

        @property
        def resource_arn(self) -> str:
            """``CfnApplicationV2.InputLambdaProcessorProperty.ResourceARN``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-application-inputlambdaprocessor.html#cfn-kinesisanalyticsv2-application-inputlambdaprocessor-resourcearn
            """
            return self._values.get('resource_arn')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'InputLambdaProcessorProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisanalytics.CfnApplicationV2.InputParallelismProperty", jsii_struct_bases=[], name_mapping={'count': 'count'})
    class InputParallelismProperty():
        def __init__(self, *, count: typing.Optional[jsii.Number]=None):
            """
            :param count: ``CfnApplicationV2.InputParallelismProperty.Count``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-application-inputparallelism.html
            """
            self._values = {
            }
            if count is not None: self._values["count"] = count

        @property
        def count(self) -> typing.Optional[jsii.Number]:
            """``CfnApplicationV2.InputParallelismProperty.Count``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-application-inputparallelism.html#cfn-kinesisanalyticsv2-application-inputparallelism-count
            """
            return self._values.get('count')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'InputParallelismProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisanalytics.CfnApplicationV2.InputProcessingConfigurationProperty", jsii_struct_bases=[], name_mapping={'input_lambda_processor': 'inputLambdaProcessor'})
    class InputProcessingConfigurationProperty():
        def __init__(self, *, input_lambda_processor: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnApplicationV2.InputLambdaProcessorProperty"]]]=None):
            """
            :param input_lambda_processor: ``CfnApplicationV2.InputProcessingConfigurationProperty.InputLambdaProcessor``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-application-inputprocessingconfiguration.html
            """
            self._values = {
            }
            if input_lambda_processor is not None: self._values["input_lambda_processor"] = input_lambda_processor

        @property
        def input_lambda_processor(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnApplicationV2.InputLambdaProcessorProperty"]]]:
            """``CfnApplicationV2.InputProcessingConfigurationProperty.InputLambdaProcessor``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-application-inputprocessingconfiguration.html#cfn-kinesisanalyticsv2-application-inputprocessingconfiguration-inputlambdaprocessor
            """
            return self._values.get('input_lambda_processor')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'InputProcessingConfigurationProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisanalytics.CfnApplicationV2.InputProperty", jsii_struct_bases=[], name_mapping={'input_schema': 'inputSchema', 'name_prefix': 'namePrefix', 'input_parallelism': 'inputParallelism', 'input_processing_configuration': 'inputProcessingConfiguration', 'kinesis_firehose_input': 'kinesisFirehoseInput', 'kinesis_streams_input': 'kinesisStreamsInput'})
    class InputProperty():
        def __init__(self, *, input_schema: typing.Union[aws_cdk.core.IResolvable, "CfnApplicationV2.InputSchemaProperty"], name_prefix: str, input_parallelism: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnApplicationV2.InputParallelismProperty"]]]=None, input_processing_configuration: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnApplicationV2.InputProcessingConfigurationProperty"]]]=None, kinesis_firehose_input: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnApplicationV2.KinesisFirehoseInputProperty"]]]=None, kinesis_streams_input: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnApplicationV2.KinesisStreamsInputProperty"]]]=None):
            """
            :param input_schema: ``CfnApplicationV2.InputProperty.InputSchema``.
            :param name_prefix: ``CfnApplicationV2.InputProperty.NamePrefix``.
            :param input_parallelism: ``CfnApplicationV2.InputProperty.InputParallelism``.
            :param input_processing_configuration: ``CfnApplicationV2.InputProperty.InputProcessingConfiguration``.
            :param kinesis_firehose_input: ``CfnApplicationV2.InputProperty.KinesisFirehoseInput``.
            :param kinesis_streams_input: ``CfnApplicationV2.InputProperty.KinesisStreamsInput``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-application-input.html
            """
            self._values = {
                'input_schema': input_schema,
                'name_prefix': name_prefix,
            }
            if input_parallelism is not None: self._values["input_parallelism"] = input_parallelism
            if input_processing_configuration is not None: self._values["input_processing_configuration"] = input_processing_configuration
            if kinesis_firehose_input is not None: self._values["kinesis_firehose_input"] = kinesis_firehose_input
            if kinesis_streams_input is not None: self._values["kinesis_streams_input"] = kinesis_streams_input

        @property
        def input_schema(self) -> typing.Union[aws_cdk.core.IResolvable, "CfnApplicationV2.InputSchemaProperty"]:
            """``CfnApplicationV2.InputProperty.InputSchema``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-application-input.html#cfn-kinesisanalyticsv2-application-input-inputschema
            """
            return self._values.get('input_schema')

        @property
        def name_prefix(self) -> str:
            """``CfnApplicationV2.InputProperty.NamePrefix``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-application-input.html#cfn-kinesisanalyticsv2-application-input-nameprefix
            """
            return self._values.get('name_prefix')

        @property
        def input_parallelism(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnApplicationV2.InputParallelismProperty"]]]:
            """``CfnApplicationV2.InputProperty.InputParallelism``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-application-input.html#cfn-kinesisanalyticsv2-application-input-inputparallelism
            """
            return self._values.get('input_parallelism')

        @property
        def input_processing_configuration(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnApplicationV2.InputProcessingConfigurationProperty"]]]:
            """``CfnApplicationV2.InputProperty.InputProcessingConfiguration``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-application-input.html#cfn-kinesisanalyticsv2-application-input-inputprocessingconfiguration
            """
            return self._values.get('input_processing_configuration')

        @property
        def kinesis_firehose_input(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnApplicationV2.KinesisFirehoseInputProperty"]]]:
            """``CfnApplicationV2.InputProperty.KinesisFirehoseInput``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-application-input.html#cfn-kinesisanalyticsv2-application-input-kinesisfirehoseinput
            """
            return self._values.get('kinesis_firehose_input')

        @property
        def kinesis_streams_input(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnApplicationV2.KinesisStreamsInputProperty"]]]:
            """``CfnApplicationV2.InputProperty.KinesisStreamsInput``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-application-input.html#cfn-kinesisanalyticsv2-application-input-kinesisstreamsinput
            """
            return self._values.get('kinesis_streams_input')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'InputProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisanalytics.CfnApplicationV2.InputSchemaProperty", jsii_struct_bases=[], name_mapping={'record_columns': 'recordColumns', 'record_format': 'recordFormat', 'record_encoding': 'recordEncoding'})
    class InputSchemaProperty():
        def __init__(self, *, record_columns: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnApplicationV2.RecordColumnProperty"]]], record_format: typing.Union[aws_cdk.core.IResolvable, "CfnApplicationV2.RecordFormatProperty"], record_encoding: typing.Optional[str]=None):
            """
            :param record_columns: ``CfnApplicationV2.InputSchemaProperty.RecordColumns``.
            :param record_format: ``CfnApplicationV2.InputSchemaProperty.RecordFormat``.
            :param record_encoding: ``CfnApplicationV2.InputSchemaProperty.RecordEncoding``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-application-inputschema.html
            """
            self._values = {
                'record_columns': record_columns,
                'record_format': record_format,
            }
            if record_encoding is not None: self._values["record_encoding"] = record_encoding

        @property
        def record_columns(self) -> typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnApplicationV2.RecordColumnProperty"]]]:
            """``CfnApplicationV2.InputSchemaProperty.RecordColumns``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-application-inputschema.html#cfn-kinesisanalyticsv2-application-inputschema-recordcolumns
            """
            return self._values.get('record_columns')

        @property
        def record_format(self) -> typing.Union[aws_cdk.core.IResolvable, "CfnApplicationV2.RecordFormatProperty"]:
            """``CfnApplicationV2.InputSchemaProperty.RecordFormat``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-application-inputschema.html#cfn-kinesisanalyticsv2-application-inputschema-recordformat
            """
            return self._values.get('record_format')

        @property
        def record_encoding(self) -> typing.Optional[str]:
            """``CfnApplicationV2.InputSchemaProperty.RecordEncoding``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-application-inputschema.html#cfn-kinesisanalyticsv2-application-inputschema-recordencoding
            """
            return self._values.get('record_encoding')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'InputSchemaProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisanalytics.CfnApplicationV2.JSONMappingParametersProperty", jsii_struct_bases=[], name_mapping={'record_row_path': 'recordRowPath'})
    class JSONMappingParametersProperty():
        def __init__(self, *, record_row_path: str):
            """
            :param record_row_path: ``CfnApplicationV2.JSONMappingParametersProperty.RecordRowPath``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-application-jsonmappingparameters.html
            """
            self._values = {
                'record_row_path': record_row_path,
            }

        @property
        def record_row_path(self) -> str:
            """``CfnApplicationV2.JSONMappingParametersProperty.RecordRowPath``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-application-jsonmappingparameters.html#cfn-kinesisanalyticsv2-application-jsonmappingparameters-recordrowpath
            """
            return self._values.get('record_row_path')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'JSONMappingParametersProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisanalytics.CfnApplicationV2.KinesisFirehoseInputProperty", jsii_struct_bases=[], name_mapping={'resource_arn': 'resourceArn'})
    class KinesisFirehoseInputProperty():
        def __init__(self, *, resource_arn: str):
            """
            :param resource_arn: ``CfnApplicationV2.KinesisFirehoseInputProperty.ResourceARN``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-application-kinesisfirehoseinput.html
            """
            self._values = {
                'resource_arn': resource_arn,
            }

        @property
        def resource_arn(self) -> str:
            """``CfnApplicationV2.KinesisFirehoseInputProperty.ResourceARN``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-application-kinesisfirehoseinput.html#cfn-kinesisanalyticsv2-application-kinesisfirehoseinput-resourcearn
            """
            return self._values.get('resource_arn')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'KinesisFirehoseInputProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisanalytics.CfnApplicationV2.KinesisStreamsInputProperty", jsii_struct_bases=[], name_mapping={'resource_arn': 'resourceArn'})
    class KinesisStreamsInputProperty():
        def __init__(self, *, resource_arn: str):
            """
            :param resource_arn: ``CfnApplicationV2.KinesisStreamsInputProperty.ResourceARN``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-application-kinesisstreamsinput.html
            """
            self._values = {
                'resource_arn': resource_arn,
            }

        @property
        def resource_arn(self) -> str:
            """``CfnApplicationV2.KinesisStreamsInputProperty.ResourceARN``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-application-kinesisstreamsinput.html#cfn-kinesisanalyticsv2-application-kinesisstreamsinput-resourcearn
            """
            return self._values.get('resource_arn')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'KinesisStreamsInputProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisanalytics.CfnApplicationV2.MappingParametersProperty", jsii_struct_bases=[], name_mapping={'csv_mapping_parameters': 'csvMappingParameters', 'json_mapping_parameters': 'jsonMappingParameters'})
    class MappingParametersProperty():
        def __init__(self, *, csv_mapping_parameters: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnApplicationV2.CSVMappingParametersProperty"]]]=None, json_mapping_parameters: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnApplicationV2.JSONMappingParametersProperty"]]]=None):
            """
            :param csv_mapping_parameters: ``CfnApplicationV2.MappingParametersProperty.CSVMappingParameters``.
            :param json_mapping_parameters: ``CfnApplicationV2.MappingParametersProperty.JSONMappingParameters``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-application-mappingparameters.html
            """
            self._values = {
            }
            if csv_mapping_parameters is not None: self._values["csv_mapping_parameters"] = csv_mapping_parameters
            if json_mapping_parameters is not None: self._values["json_mapping_parameters"] = json_mapping_parameters

        @property
        def csv_mapping_parameters(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnApplicationV2.CSVMappingParametersProperty"]]]:
            """``CfnApplicationV2.MappingParametersProperty.CSVMappingParameters``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-application-mappingparameters.html#cfn-kinesisanalyticsv2-application-mappingparameters-csvmappingparameters
            """
            return self._values.get('csv_mapping_parameters')

        @property
        def json_mapping_parameters(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnApplicationV2.JSONMappingParametersProperty"]]]:
            """``CfnApplicationV2.MappingParametersProperty.JSONMappingParameters``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-application-mappingparameters.html#cfn-kinesisanalyticsv2-application-mappingparameters-jsonmappingparameters
            """
            return self._values.get('json_mapping_parameters')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'MappingParametersProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisanalytics.CfnApplicationV2.MonitoringConfigurationProperty", jsii_struct_bases=[], name_mapping={'configuration_type': 'configurationType', 'log_level': 'logLevel', 'metrics_level': 'metricsLevel'})
    class MonitoringConfigurationProperty():
        def __init__(self, *, configuration_type: str, log_level: typing.Optional[str]=None, metrics_level: typing.Optional[str]=None):
            """
            :param configuration_type: ``CfnApplicationV2.MonitoringConfigurationProperty.ConfigurationType``.
            :param log_level: ``CfnApplicationV2.MonitoringConfigurationProperty.LogLevel``.
            :param metrics_level: ``CfnApplicationV2.MonitoringConfigurationProperty.MetricsLevel``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-application-monitoringconfiguration.html
            """
            self._values = {
                'configuration_type': configuration_type,
            }
            if log_level is not None: self._values["log_level"] = log_level
            if metrics_level is not None: self._values["metrics_level"] = metrics_level

        @property
        def configuration_type(self) -> str:
            """``CfnApplicationV2.MonitoringConfigurationProperty.ConfigurationType``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-application-monitoringconfiguration.html#cfn-kinesisanalyticsv2-application-monitoringconfiguration-configurationtype
            """
            return self._values.get('configuration_type')

        @property
        def log_level(self) -> typing.Optional[str]:
            """``CfnApplicationV2.MonitoringConfigurationProperty.LogLevel``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-application-monitoringconfiguration.html#cfn-kinesisanalyticsv2-application-monitoringconfiguration-loglevel
            """
            return self._values.get('log_level')

        @property
        def metrics_level(self) -> typing.Optional[str]:
            """``CfnApplicationV2.MonitoringConfigurationProperty.MetricsLevel``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-application-monitoringconfiguration.html#cfn-kinesisanalyticsv2-application-monitoringconfiguration-metricslevel
            """
            return self._values.get('metrics_level')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'MonitoringConfigurationProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisanalytics.CfnApplicationV2.ParallelismConfigurationProperty", jsii_struct_bases=[], name_mapping={'configuration_type': 'configurationType', 'auto_scaling_enabled': 'autoScalingEnabled', 'parallelism': 'parallelism', 'parallelism_per_kpu': 'parallelismPerKpu'})
    class ParallelismConfigurationProperty():
        def __init__(self, *, configuration_type: str, auto_scaling_enabled: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, parallelism: typing.Optional[jsii.Number]=None, parallelism_per_kpu: typing.Optional[jsii.Number]=None):
            """
            :param configuration_type: ``CfnApplicationV2.ParallelismConfigurationProperty.ConfigurationType``.
            :param auto_scaling_enabled: ``CfnApplicationV2.ParallelismConfigurationProperty.AutoScalingEnabled``.
            :param parallelism: ``CfnApplicationV2.ParallelismConfigurationProperty.Parallelism``.
            :param parallelism_per_kpu: ``CfnApplicationV2.ParallelismConfigurationProperty.ParallelismPerKPU``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-application-parallelismconfiguration.html
            """
            self._values = {
                'configuration_type': configuration_type,
            }
            if auto_scaling_enabled is not None: self._values["auto_scaling_enabled"] = auto_scaling_enabled
            if parallelism is not None: self._values["parallelism"] = parallelism
            if parallelism_per_kpu is not None: self._values["parallelism_per_kpu"] = parallelism_per_kpu

        @property
        def configuration_type(self) -> str:
            """``CfnApplicationV2.ParallelismConfigurationProperty.ConfigurationType``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-application-parallelismconfiguration.html#cfn-kinesisanalyticsv2-application-parallelismconfiguration-configurationtype
            """
            return self._values.get('configuration_type')

        @property
        def auto_scaling_enabled(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
            """``CfnApplicationV2.ParallelismConfigurationProperty.AutoScalingEnabled``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-application-parallelismconfiguration.html#cfn-kinesisanalyticsv2-application-parallelismconfiguration-autoscalingenabled
            """
            return self._values.get('auto_scaling_enabled')

        @property
        def parallelism(self) -> typing.Optional[jsii.Number]:
            """``CfnApplicationV2.ParallelismConfigurationProperty.Parallelism``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-application-parallelismconfiguration.html#cfn-kinesisanalyticsv2-application-parallelismconfiguration-parallelism
            """
            return self._values.get('parallelism')

        @property
        def parallelism_per_kpu(self) -> typing.Optional[jsii.Number]:
            """``CfnApplicationV2.ParallelismConfigurationProperty.ParallelismPerKPU``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-application-parallelismconfiguration.html#cfn-kinesisanalyticsv2-application-parallelismconfiguration-parallelismperkpu
            """
            return self._values.get('parallelism_per_kpu')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'ParallelismConfigurationProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisanalytics.CfnApplicationV2.PropertyGroupProperty", jsii_struct_bases=[], name_mapping={'property_group_id': 'propertyGroupId', 'property_map': 'propertyMap'})
    class PropertyGroupProperty():
        def __init__(self, *, property_group_id: typing.Optional[str]=None, property_map: typing.Any=None):
            """
            :param property_group_id: ``CfnApplicationV2.PropertyGroupProperty.PropertyGroupId``.
            :param property_map: ``CfnApplicationV2.PropertyGroupProperty.PropertyMap``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-application-propertygroup.html
            """
            self._values = {
            }
            if property_group_id is not None: self._values["property_group_id"] = property_group_id
            if property_map is not None: self._values["property_map"] = property_map

        @property
        def property_group_id(self) -> typing.Optional[str]:
            """``CfnApplicationV2.PropertyGroupProperty.PropertyGroupId``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-application-propertygroup.html#cfn-kinesisanalyticsv2-application-propertygroup-propertygroupid
            """
            return self._values.get('property_group_id')

        @property
        def property_map(self) -> typing.Any:
            """``CfnApplicationV2.PropertyGroupProperty.PropertyMap``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-application-propertygroup.html#cfn-kinesisanalyticsv2-application-propertygroup-propertymap
            """
            return self._values.get('property_map')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'PropertyGroupProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisanalytics.CfnApplicationV2.RecordColumnProperty", jsii_struct_bases=[], name_mapping={'name': 'name', 'sql_type': 'sqlType', 'mapping': 'mapping'})
    class RecordColumnProperty():
        def __init__(self, *, name: str, sql_type: str, mapping: typing.Optional[str]=None):
            """
            :param name: ``CfnApplicationV2.RecordColumnProperty.Name``.
            :param sql_type: ``CfnApplicationV2.RecordColumnProperty.SqlType``.
            :param mapping: ``CfnApplicationV2.RecordColumnProperty.Mapping``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-application-recordcolumn.html
            """
            self._values = {
                'name': name,
                'sql_type': sql_type,
            }
            if mapping is not None: self._values["mapping"] = mapping

        @property
        def name(self) -> str:
            """``CfnApplicationV2.RecordColumnProperty.Name``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-application-recordcolumn.html#cfn-kinesisanalyticsv2-application-recordcolumn-name
            """
            return self._values.get('name')

        @property
        def sql_type(self) -> str:
            """``CfnApplicationV2.RecordColumnProperty.SqlType``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-application-recordcolumn.html#cfn-kinesisanalyticsv2-application-recordcolumn-sqltype
            """
            return self._values.get('sql_type')

        @property
        def mapping(self) -> typing.Optional[str]:
            """``CfnApplicationV2.RecordColumnProperty.Mapping``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-application-recordcolumn.html#cfn-kinesisanalyticsv2-application-recordcolumn-mapping
            """
            return self._values.get('mapping')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'RecordColumnProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisanalytics.CfnApplicationV2.RecordFormatProperty", jsii_struct_bases=[], name_mapping={'record_format_type': 'recordFormatType', 'mapping_parameters': 'mappingParameters'})
    class RecordFormatProperty():
        def __init__(self, *, record_format_type: str, mapping_parameters: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnApplicationV2.MappingParametersProperty"]]]=None):
            """
            :param record_format_type: ``CfnApplicationV2.RecordFormatProperty.RecordFormatType``.
            :param mapping_parameters: ``CfnApplicationV2.RecordFormatProperty.MappingParameters``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-application-recordformat.html
            """
            self._values = {
                'record_format_type': record_format_type,
            }
            if mapping_parameters is not None: self._values["mapping_parameters"] = mapping_parameters

        @property
        def record_format_type(self) -> str:
            """``CfnApplicationV2.RecordFormatProperty.RecordFormatType``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-application-recordformat.html#cfn-kinesisanalyticsv2-application-recordformat-recordformattype
            """
            return self._values.get('record_format_type')

        @property
        def mapping_parameters(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnApplicationV2.MappingParametersProperty"]]]:
            """``CfnApplicationV2.RecordFormatProperty.MappingParameters``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-application-recordformat.html#cfn-kinesisanalyticsv2-application-recordformat-mappingparameters
            """
            return self._values.get('mapping_parameters')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'RecordFormatProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisanalytics.CfnApplicationV2.S3ContentLocationProperty", jsii_struct_bases=[], name_mapping={'bucket_arn': 'bucketArn', 'file_key': 'fileKey', 'object_version': 'objectVersion'})
    class S3ContentLocationProperty():
        def __init__(self, *, bucket_arn: typing.Optional[str]=None, file_key: typing.Optional[str]=None, object_version: typing.Optional[str]=None):
            """
            :param bucket_arn: ``CfnApplicationV2.S3ContentLocationProperty.BucketARN``.
            :param file_key: ``CfnApplicationV2.S3ContentLocationProperty.FileKey``.
            :param object_version: ``CfnApplicationV2.S3ContentLocationProperty.ObjectVersion``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-application-s3contentlocation.html
            """
            self._values = {
            }
            if bucket_arn is not None: self._values["bucket_arn"] = bucket_arn
            if file_key is not None: self._values["file_key"] = file_key
            if object_version is not None: self._values["object_version"] = object_version

        @property
        def bucket_arn(self) -> typing.Optional[str]:
            """``CfnApplicationV2.S3ContentLocationProperty.BucketARN``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-application-s3contentlocation.html#cfn-kinesisanalyticsv2-application-s3contentlocation-bucketarn
            """
            return self._values.get('bucket_arn')

        @property
        def file_key(self) -> typing.Optional[str]:
            """``CfnApplicationV2.S3ContentLocationProperty.FileKey``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-application-s3contentlocation.html#cfn-kinesisanalyticsv2-application-s3contentlocation-filekey
            """
            return self._values.get('file_key')

        @property
        def object_version(self) -> typing.Optional[str]:
            """``CfnApplicationV2.S3ContentLocationProperty.ObjectVersion``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-application-s3contentlocation.html#cfn-kinesisanalyticsv2-application-s3contentlocation-objectversion
            """
            return self._values.get('object_version')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'S3ContentLocationProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisanalytics.CfnApplicationV2.SqlApplicationConfigurationProperty", jsii_struct_bases=[], name_mapping={'inputs': 'inputs'})
    class SqlApplicationConfigurationProperty():
        def __init__(self, *, inputs: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnApplicationV2.InputProperty"]]]]]=None):
            """
            :param inputs: ``CfnApplicationV2.SqlApplicationConfigurationProperty.Inputs``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-application-sqlapplicationconfiguration.html
            """
            self._values = {
            }
            if inputs is not None: self._values["inputs"] = inputs

        @property
        def inputs(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnApplicationV2.InputProperty"]]]]]:
            """``CfnApplicationV2.SqlApplicationConfigurationProperty.Inputs``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisanalyticsv2-application-sqlapplicationconfiguration.html#cfn-kinesisanalyticsv2-application-sqlapplicationconfiguration-inputs
            """
            return self._values.get('inputs')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'SqlApplicationConfigurationProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



@jsii.data_type(jsii_type="@aws-cdk/aws-kinesisanalytics.CfnApplicationV2Props", jsii_struct_bases=[], name_mapping={'runtime_environment': 'runtimeEnvironment', 'service_execution_role': 'serviceExecutionRole', 'application_configuration': 'applicationConfiguration', 'application_description': 'applicationDescription', 'application_name': 'applicationName'})
class CfnApplicationV2Props():
    def __init__(self, *, runtime_environment: str, service_execution_role: str, application_configuration: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnApplicationV2.ApplicationConfigurationProperty"]]]=None, application_description: typing.Optional[str]=None, application_name: typing.Optional[str]=None):
        """Properties for defining a ``AWS::KinesisAnalyticsV2::Application``.

        :param runtime_environment: ``AWS::KinesisAnalyticsV2::Application.RuntimeEnvironment``.
        :param service_execution_role: ``AWS::KinesisAnalyticsV2::Application.ServiceExecutionRole``.
        :param application_configuration: ``AWS::KinesisAnalyticsV2::Application.ApplicationConfiguration``.
        :param application_description: ``AWS::KinesisAnalyticsV2::Application.ApplicationDescription``.
        :param application_name: ``AWS::KinesisAnalyticsV2::Application.ApplicationName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisanalyticsv2-application.html
        """
        self._values = {
            'runtime_environment': runtime_environment,
            'service_execution_role': service_execution_role,
        }
        if application_configuration is not None: self._values["application_configuration"] = application_configuration
        if application_description is not None: self._values["application_description"] = application_description
        if application_name is not None: self._values["application_name"] = application_name

    @property
    def runtime_environment(self) -> str:
        """``AWS::KinesisAnalyticsV2::Application.RuntimeEnvironment``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisanalyticsv2-application.html#cfn-kinesisanalyticsv2-application-runtimeenvironment
        """
        return self._values.get('runtime_environment')

    @property
    def service_execution_role(self) -> str:
        """``AWS::KinesisAnalyticsV2::Application.ServiceExecutionRole``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisanalyticsv2-application.html#cfn-kinesisanalyticsv2-application-serviceexecutionrole
        """
        return self._values.get('service_execution_role')

    @property
    def application_configuration(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnApplicationV2.ApplicationConfigurationProperty"]]]:
        """``AWS::KinesisAnalyticsV2::Application.ApplicationConfiguration``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisanalyticsv2-application.html#cfn-kinesisanalyticsv2-application-applicationconfiguration
        """
        return self._values.get('application_configuration')

    @property
    def application_description(self) -> typing.Optional[str]:
        """``AWS::KinesisAnalyticsV2::Application.ApplicationDescription``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisanalyticsv2-application.html#cfn-kinesisanalyticsv2-application-applicationdescription
        """
        return self._values.get('application_description')

    @property
    def application_name(self) -> typing.Optional[str]:
        """``AWS::KinesisAnalyticsV2::Application.ApplicationName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisanalyticsv2-application.html#cfn-kinesisanalyticsv2-application-applicationname
        """
        return self._values.get('application_name')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnApplicationV2Props(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


__all__ = ["CfnApplication", "CfnApplicationCloudWatchLoggingOptionV2", "CfnApplicationCloudWatchLoggingOptionV2Props", "CfnApplicationOutput", "CfnApplicationOutputProps", "CfnApplicationOutputV2", "CfnApplicationOutputV2Props", "CfnApplicationProps", "CfnApplicationReferenceDataSource", "CfnApplicationReferenceDataSourceProps", "CfnApplicationReferenceDataSourceV2", "CfnApplicationReferenceDataSourceV2Props", "CfnApplicationV2", "CfnApplicationV2Props", "__jsii_assembly__"]

publication.publish()
