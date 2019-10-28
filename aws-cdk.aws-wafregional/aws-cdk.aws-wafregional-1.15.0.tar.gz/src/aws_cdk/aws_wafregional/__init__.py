import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.core
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-wafregional", "1.15.0", __name__, "aws-wafregional@1.15.0.jsii.tgz")
class CfnByteMatchSet(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-wafregional.CfnByteMatchSet"):
    """A CloudFormation ``AWS::WAFRegional::ByteMatchSet``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-bytematchset.html
    cloudformationResource:
    :cloudformationResource:: AWS::WAFRegional::ByteMatchSet
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, name: str, byte_match_tuples: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "ByteMatchTupleProperty"]]]]]=None) -> None:
        """Create a new ``AWS::WAFRegional::ByteMatchSet``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param name: ``AWS::WAFRegional::ByteMatchSet.Name``.
        :param byte_match_tuples: ``AWS::WAFRegional::ByteMatchSet.ByteMatchTuples``.
        """
        props = CfnByteMatchSetProps(name=name, byte_match_tuples=byte_match_tuples)

        jsii.create(CfnByteMatchSet, self, [scope, id, props])

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
        """``AWS::WAFRegional::ByteMatchSet.Name``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-bytematchset.html#cfn-wafregional-bytematchset-name
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: str):
        return jsii.set(self, "name", value)

    @property
    @jsii.member(jsii_name="byteMatchTuples")
    def byte_match_tuples(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "ByteMatchTupleProperty"]]]]]:
        """``AWS::WAFRegional::ByteMatchSet.ByteMatchTuples``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-bytematchset.html#cfn-wafregional-bytematchset-bytematchtuples
        """
        return jsii.get(self, "byteMatchTuples")

    @byte_match_tuples.setter
    def byte_match_tuples(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "ByteMatchTupleProperty"]]]]]):
        return jsii.set(self, "byteMatchTuples", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-wafregional.CfnByteMatchSet.ByteMatchTupleProperty", jsii_struct_bases=[], name_mapping={'field_to_match': 'fieldToMatch', 'positional_constraint': 'positionalConstraint', 'text_transformation': 'textTransformation', 'target_string': 'targetString', 'target_string_base64': 'targetStringBase64'})
    class ByteMatchTupleProperty():
        def __init__(self, *, field_to_match: typing.Union[aws_cdk.core.IResolvable, "CfnByteMatchSet.FieldToMatchProperty"], positional_constraint: str, text_transformation: str, target_string: typing.Optional[str]=None, target_string_base64: typing.Optional[str]=None):
            """
            :param field_to_match: ``CfnByteMatchSet.ByteMatchTupleProperty.FieldToMatch``.
            :param positional_constraint: ``CfnByteMatchSet.ByteMatchTupleProperty.PositionalConstraint``.
            :param text_transformation: ``CfnByteMatchSet.ByteMatchTupleProperty.TextTransformation``.
            :param target_string: ``CfnByteMatchSet.ByteMatchTupleProperty.TargetString``.
            :param target_string_base64: ``CfnByteMatchSet.ByteMatchTupleProperty.TargetStringBase64``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-bytematchset-bytematchtuple.html
            """
            self._values = {
                'field_to_match': field_to_match,
                'positional_constraint': positional_constraint,
                'text_transformation': text_transformation,
            }
            if target_string is not None: self._values["target_string"] = target_string
            if target_string_base64 is not None: self._values["target_string_base64"] = target_string_base64

        @property
        def field_to_match(self) -> typing.Union[aws_cdk.core.IResolvable, "CfnByteMatchSet.FieldToMatchProperty"]:
            """``CfnByteMatchSet.ByteMatchTupleProperty.FieldToMatch``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-bytematchset-bytematchtuple.html#cfn-wafregional-bytematchset-bytematchtuple-fieldtomatch
            """
            return self._values.get('field_to_match')

        @property
        def positional_constraint(self) -> str:
            """``CfnByteMatchSet.ByteMatchTupleProperty.PositionalConstraint``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-bytematchset-bytematchtuple.html#cfn-wafregional-bytematchset-bytematchtuple-positionalconstraint
            """
            return self._values.get('positional_constraint')

        @property
        def text_transformation(self) -> str:
            """``CfnByteMatchSet.ByteMatchTupleProperty.TextTransformation``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-bytematchset-bytematchtuple.html#cfn-wafregional-bytematchset-bytematchtuple-texttransformation
            """
            return self._values.get('text_transformation')

        @property
        def target_string(self) -> typing.Optional[str]:
            """``CfnByteMatchSet.ByteMatchTupleProperty.TargetString``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-bytematchset-bytematchtuple.html#cfn-wafregional-bytematchset-bytematchtuple-targetstring
            """
            return self._values.get('target_string')

        @property
        def target_string_base64(self) -> typing.Optional[str]:
            """``CfnByteMatchSet.ByteMatchTupleProperty.TargetStringBase64``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-bytematchset-bytematchtuple.html#cfn-wafregional-bytematchset-bytematchtuple-targetstringbase64
            """
            return self._values.get('target_string_base64')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'ByteMatchTupleProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-wafregional.CfnByteMatchSet.FieldToMatchProperty", jsii_struct_bases=[], name_mapping={'type': 'type', 'data': 'data'})
    class FieldToMatchProperty():
        def __init__(self, *, type: str, data: typing.Optional[str]=None):
            """
            :param type: ``CfnByteMatchSet.FieldToMatchProperty.Type``.
            :param data: ``CfnByteMatchSet.FieldToMatchProperty.Data``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-bytematchset-fieldtomatch.html
            """
            self._values = {
                'type': type,
            }
            if data is not None: self._values["data"] = data

        @property
        def type(self) -> str:
            """``CfnByteMatchSet.FieldToMatchProperty.Type``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-bytematchset-fieldtomatch.html#cfn-wafregional-bytematchset-fieldtomatch-type
            """
            return self._values.get('type')

        @property
        def data(self) -> typing.Optional[str]:
            """``CfnByteMatchSet.FieldToMatchProperty.Data``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-bytematchset-fieldtomatch.html#cfn-wafregional-bytematchset-fieldtomatch-data
            """
            return self._values.get('data')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'FieldToMatchProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



@jsii.data_type(jsii_type="@aws-cdk/aws-wafregional.CfnByteMatchSetProps", jsii_struct_bases=[], name_mapping={'name': 'name', 'byte_match_tuples': 'byteMatchTuples'})
class CfnByteMatchSetProps():
    def __init__(self, *, name: str, byte_match_tuples: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnByteMatchSet.ByteMatchTupleProperty"]]]]]=None):
        """Properties for defining a ``AWS::WAFRegional::ByteMatchSet``.

        :param name: ``AWS::WAFRegional::ByteMatchSet.Name``.
        :param byte_match_tuples: ``AWS::WAFRegional::ByteMatchSet.ByteMatchTuples``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-bytematchset.html
        """
        self._values = {
            'name': name,
        }
        if byte_match_tuples is not None: self._values["byte_match_tuples"] = byte_match_tuples

    @property
    def name(self) -> str:
        """``AWS::WAFRegional::ByteMatchSet.Name``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-bytematchset.html#cfn-wafregional-bytematchset-name
        """
        return self._values.get('name')

    @property
    def byte_match_tuples(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnByteMatchSet.ByteMatchTupleProperty"]]]]]:
        """``AWS::WAFRegional::ByteMatchSet.ByteMatchTuples``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-bytematchset.html#cfn-wafregional-bytematchset-bytematchtuples
        """
        return self._values.get('byte_match_tuples')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnByteMatchSetProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnGeoMatchSet(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-wafregional.CfnGeoMatchSet"):
    """A CloudFormation ``AWS::WAFRegional::GeoMatchSet``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-geomatchset.html
    cloudformationResource:
    :cloudformationResource:: AWS::WAFRegional::GeoMatchSet
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, name: str, geo_match_constraints: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "GeoMatchConstraintProperty"]]]]]=None) -> None:
        """Create a new ``AWS::WAFRegional::GeoMatchSet``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param name: ``AWS::WAFRegional::GeoMatchSet.Name``.
        :param geo_match_constraints: ``AWS::WAFRegional::GeoMatchSet.GeoMatchConstraints``.
        """
        props = CfnGeoMatchSetProps(name=name, geo_match_constraints=geo_match_constraints)

        jsii.create(CfnGeoMatchSet, self, [scope, id, props])

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
        """``AWS::WAFRegional::GeoMatchSet.Name``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-geomatchset.html#cfn-wafregional-geomatchset-name
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: str):
        return jsii.set(self, "name", value)

    @property
    @jsii.member(jsii_name="geoMatchConstraints")
    def geo_match_constraints(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "GeoMatchConstraintProperty"]]]]]:
        """``AWS::WAFRegional::GeoMatchSet.GeoMatchConstraints``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-geomatchset.html#cfn-wafregional-geomatchset-geomatchconstraints
        """
        return jsii.get(self, "geoMatchConstraints")

    @geo_match_constraints.setter
    def geo_match_constraints(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "GeoMatchConstraintProperty"]]]]]):
        return jsii.set(self, "geoMatchConstraints", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-wafregional.CfnGeoMatchSet.GeoMatchConstraintProperty", jsii_struct_bases=[], name_mapping={'type': 'type', 'value': 'value'})
    class GeoMatchConstraintProperty():
        def __init__(self, *, type: str, value: str):
            """
            :param type: ``CfnGeoMatchSet.GeoMatchConstraintProperty.Type``.
            :param value: ``CfnGeoMatchSet.GeoMatchConstraintProperty.Value``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-geomatchset-geomatchconstraint.html
            """
            self._values = {
                'type': type,
                'value': value,
            }

        @property
        def type(self) -> str:
            """``CfnGeoMatchSet.GeoMatchConstraintProperty.Type``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-geomatchset-geomatchconstraint.html#cfn-wafregional-geomatchset-geomatchconstraint-type
            """
            return self._values.get('type')

        @property
        def value(self) -> str:
            """``CfnGeoMatchSet.GeoMatchConstraintProperty.Value``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-geomatchset-geomatchconstraint.html#cfn-wafregional-geomatchset-geomatchconstraint-value
            """
            return self._values.get('value')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'GeoMatchConstraintProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



@jsii.data_type(jsii_type="@aws-cdk/aws-wafregional.CfnGeoMatchSetProps", jsii_struct_bases=[], name_mapping={'name': 'name', 'geo_match_constraints': 'geoMatchConstraints'})
class CfnGeoMatchSetProps():
    def __init__(self, *, name: str, geo_match_constraints: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnGeoMatchSet.GeoMatchConstraintProperty"]]]]]=None):
        """Properties for defining a ``AWS::WAFRegional::GeoMatchSet``.

        :param name: ``AWS::WAFRegional::GeoMatchSet.Name``.
        :param geo_match_constraints: ``AWS::WAFRegional::GeoMatchSet.GeoMatchConstraints``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-geomatchset.html
        """
        self._values = {
            'name': name,
        }
        if geo_match_constraints is not None: self._values["geo_match_constraints"] = geo_match_constraints

    @property
    def name(self) -> str:
        """``AWS::WAFRegional::GeoMatchSet.Name``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-geomatchset.html#cfn-wafregional-geomatchset-name
        """
        return self._values.get('name')

    @property
    def geo_match_constraints(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnGeoMatchSet.GeoMatchConstraintProperty"]]]]]:
        """``AWS::WAFRegional::GeoMatchSet.GeoMatchConstraints``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-geomatchset.html#cfn-wafregional-geomatchset-geomatchconstraints
        """
        return self._values.get('geo_match_constraints')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnGeoMatchSetProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnIPSet(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-wafregional.CfnIPSet"):
    """A CloudFormation ``AWS::WAFRegional::IPSet``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-ipset.html
    cloudformationResource:
    :cloudformationResource:: AWS::WAFRegional::IPSet
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, name: str, ip_set_descriptors: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "IPSetDescriptorProperty"]]]]]=None) -> None:
        """Create a new ``AWS::WAFRegional::IPSet``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param name: ``AWS::WAFRegional::IPSet.Name``.
        :param ip_set_descriptors: ``AWS::WAFRegional::IPSet.IPSetDescriptors``.
        """
        props = CfnIPSetProps(name=name, ip_set_descriptors=ip_set_descriptors)

        jsii.create(CfnIPSet, self, [scope, id, props])

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
        """``AWS::WAFRegional::IPSet.Name``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-ipset.html#cfn-wafregional-ipset-name
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: str):
        return jsii.set(self, "name", value)

    @property
    @jsii.member(jsii_name="ipSetDescriptors")
    def ip_set_descriptors(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "IPSetDescriptorProperty"]]]]]:
        """``AWS::WAFRegional::IPSet.IPSetDescriptors``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-ipset.html#cfn-wafregional-ipset-ipsetdescriptors
        """
        return jsii.get(self, "ipSetDescriptors")

    @ip_set_descriptors.setter
    def ip_set_descriptors(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "IPSetDescriptorProperty"]]]]]):
        return jsii.set(self, "ipSetDescriptors", value)

    @jsii.interface(jsii_type="@aws-cdk/aws-wafregional.CfnIPSet.IPSetDescriptorProperty")
    class IPSetDescriptorProperty(jsii.compat.Protocol):
        """
        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-ipset-ipsetdescriptor.html
        """
        @staticmethod
        def __jsii_proxy_class__():
            return _IPSetDescriptorPropertyProxy

        @property
        @jsii.member(jsii_name="type")
        def type(self) -> str:
            """``CfnIPSet.IPSetDescriptorProperty.Type``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-ipset-ipsetdescriptor.html#cfn-wafregional-ipset-ipsetdescriptor-type
            """
            ...

        @property
        @jsii.member(jsii_name="value")
        def value(self) -> str:
            """``CfnIPSet.IPSetDescriptorProperty.Value``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-ipset-ipsetdescriptor.html#cfn-wafregional-ipset-ipsetdescriptor-value
            """
            ...


    class _IPSetDescriptorPropertyProxy():
        """
        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-ipset-ipsetdescriptor.html
        """
        __jsii_type__ = "@aws-cdk/aws-wafregional.CfnIPSet.IPSetDescriptorProperty"
        @property
        @jsii.member(jsii_name="type")
        def type(self) -> str:
            """``CfnIPSet.IPSetDescriptorProperty.Type``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-ipset-ipsetdescriptor.html#cfn-wafregional-ipset-ipsetdescriptor-type
            """
            return jsii.get(self, "type")

        @property
        @jsii.member(jsii_name="value")
        def value(self) -> str:
            """``CfnIPSet.IPSetDescriptorProperty.Value``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-ipset-ipsetdescriptor.html#cfn-wafregional-ipset-ipsetdescriptor-value
            """
            return jsii.get(self, "value")



@jsii.data_type(jsii_type="@aws-cdk/aws-wafregional.CfnIPSetProps", jsii_struct_bases=[], name_mapping={'name': 'name', 'ip_set_descriptors': 'ipSetDescriptors'})
class CfnIPSetProps():
    def __init__(self, *, name: str, ip_set_descriptors: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnIPSet.IPSetDescriptorProperty"]]]]]=None):
        """Properties for defining a ``AWS::WAFRegional::IPSet``.

        :param name: ``AWS::WAFRegional::IPSet.Name``.
        :param ip_set_descriptors: ``AWS::WAFRegional::IPSet.IPSetDescriptors``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-ipset.html
        """
        self._values = {
            'name': name,
        }
        if ip_set_descriptors is not None: self._values["ip_set_descriptors"] = ip_set_descriptors

    @property
    def name(self) -> str:
        """``AWS::WAFRegional::IPSet.Name``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-ipset.html#cfn-wafregional-ipset-name
        """
        return self._values.get('name')

    @property
    def ip_set_descriptors(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnIPSet.IPSetDescriptorProperty"]]]]]:
        """``AWS::WAFRegional::IPSet.IPSetDescriptors``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-ipset.html#cfn-wafregional-ipset-ipsetdescriptors
        """
        return self._values.get('ip_set_descriptors')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnIPSetProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnRateBasedRule(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-wafregional.CfnRateBasedRule"):
    """A CloudFormation ``AWS::WAFRegional::RateBasedRule``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-ratebasedrule.html
    cloudformationResource:
    :cloudformationResource:: AWS::WAFRegional::RateBasedRule
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, metric_name: str, name: str, rate_key: str, rate_limit: jsii.Number, match_predicates: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "PredicateProperty"]]]]]=None) -> None:
        """Create a new ``AWS::WAFRegional::RateBasedRule``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param metric_name: ``AWS::WAFRegional::RateBasedRule.MetricName``.
        :param name: ``AWS::WAFRegional::RateBasedRule.Name``.
        :param rate_key: ``AWS::WAFRegional::RateBasedRule.RateKey``.
        :param rate_limit: ``AWS::WAFRegional::RateBasedRule.RateLimit``.
        :param match_predicates: ``AWS::WAFRegional::RateBasedRule.MatchPredicates``.
        """
        props = CfnRateBasedRuleProps(metric_name=metric_name, name=name, rate_key=rate_key, rate_limit=rate_limit, match_predicates=match_predicates)

        jsii.create(CfnRateBasedRule, self, [scope, id, props])

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
    @jsii.member(jsii_name="metricName")
    def metric_name(self) -> str:
        """``AWS::WAFRegional::RateBasedRule.MetricName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-ratebasedrule.html#cfn-wafregional-ratebasedrule-metricname
        """
        return jsii.get(self, "metricName")

    @metric_name.setter
    def metric_name(self, value: str):
        return jsii.set(self, "metricName", value)

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> str:
        """``AWS::WAFRegional::RateBasedRule.Name``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-ratebasedrule.html#cfn-wafregional-ratebasedrule-name
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: str):
        return jsii.set(self, "name", value)

    @property
    @jsii.member(jsii_name="rateKey")
    def rate_key(self) -> str:
        """``AWS::WAFRegional::RateBasedRule.RateKey``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-ratebasedrule.html#cfn-wafregional-ratebasedrule-ratekey
        """
        return jsii.get(self, "rateKey")

    @rate_key.setter
    def rate_key(self, value: str):
        return jsii.set(self, "rateKey", value)

    @property
    @jsii.member(jsii_name="rateLimit")
    def rate_limit(self) -> jsii.Number:
        """``AWS::WAFRegional::RateBasedRule.RateLimit``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-ratebasedrule.html#cfn-wafregional-ratebasedrule-ratelimit
        """
        return jsii.get(self, "rateLimit")

    @rate_limit.setter
    def rate_limit(self, value: jsii.Number):
        return jsii.set(self, "rateLimit", value)

    @property
    @jsii.member(jsii_name="matchPredicates")
    def match_predicates(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "PredicateProperty"]]]]]:
        """``AWS::WAFRegional::RateBasedRule.MatchPredicates``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-ratebasedrule.html#cfn-wafregional-ratebasedrule-matchpredicates
        """
        return jsii.get(self, "matchPredicates")

    @match_predicates.setter
    def match_predicates(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "PredicateProperty"]]]]]):
        return jsii.set(self, "matchPredicates", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-wafregional.CfnRateBasedRule.PredicateProperty", jsii_struct_bases=[], name_mapping={'data_id': 'dataId', 'negated': 'negated', 'type': 'type'})
    class PredicateProperty():
        def __init__(self, *, data_id: str, negated: typing.Union[bool, aws_cdk.core.IResolvable], type: str):
            """
            :param data_id: ``CfnRateBasedRule.PredicateProperty.DataId``.
            :param negated: ``CfnRateBasedRule.PredicateProperty.Negated``.
            :param type: ``CfnRateBasedRule.PredicateProperty.Type``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-ratebasedrule-predicate.html
            """
            self._values = {
                'data_id': data_id,
                'negated': negated,
                'type': type,
            }

        @property
        def data_id(self) -> str:
            """``CfnRateBasedRule.PredicateProperty.DataId``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-ratebasedrule-predicate.html#cfn-wafregional-ratebasedrule-predicate-dataid
            """
            return self._values.get('data_id')

        @property
        def negated(self) -> typing.Union[bool, aws_cdk.core.IResolvable]:
            """``CfnRateBasedRule.PredicateProperty.Negated``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-ratebasedrule-predicate.html#cfn-wafregional-ratebasedrule-predicate-negated
            """
            return self._values.get('negated')

        @property
        def type(self) -> str:
            """``CfnRateBasedRule.PredicateProperty.Type``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-ratebasedrule-predicate.html#cfn-wafregional-ratebasedrule-predicate-type
            """
            return self._values.get('type')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'PredicateProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



@jsii.data_type(jsii_type="@aws-cdk/aws-wafregional.CfnRateBasedRuleProps", jsii_struct_bases=[], name_mapping={'metric_name': 'metricName', 'name': 'name', 'rate_key': 'rateKey', 'rate_limit': 'rateLimit', 'match_predicates': 'matchPredicates'})
class CfnRateBasedRuleProps():
    def __init__(self, *, metric_name: str, name: str, rate_key: str, rate_limit: jsii.Number, match_predicates: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnRateBasedRule.PredicateProperty"]]]]]=None):
        """Properties for defining a ``AWS::WAFRegional::RateBasedRule``.

        :param metric_name: ``AWS::WAFRegional::RateBasedRule.MetricName``.
        :param name: ``AWS::WAFRegional::RateBasedRule.Name``.
        :param rate_key: ``AWS::WAFRegional::RateBasedRule.RateKey``.
        :param rate_limit: ``AWS::WAFRegional::RateBasedRule.RateLimit``.
        :param match_predicates: ``AWS::WAFRegional::RateBasedRule.MatchPredicates``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-ratebasedrule.html
        """
        self._values = {
            'metric_name': metric_name,
            'name': name,
            'rate_key': rate_key,
            'rate_limit': rate_limit,
        }
        if match_predicates is not None: self._values["match_predicates"] = match_predicates

    @property
    def metric_name(self) -> str:
        """``AWS::WAFRegional::RateBasedRule.MetricName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-ratebasedrule.html#cfn-wafregional-ratebasedrule-metricname
        """
        return self._values.get('metric_name')

    @property
    def name(self) -> str:
        """``AWS::WAFRegional::RateBasedRule.Name``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-ratebasedrule.html#cfn-wafregional-ratebasedrule-name
        """
        return self._values.get('name')

    @property
    def rate_key(self) -> str:
        """``AWS::WAFRegional::RateBasedRule.RateKey``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-ratebasedrule.html#cfn-wafregional-ratebasedrule-ratekey
        """
        return self._values.get('rate_key')

    @property
    def rate_limit(self) -> jsii.Number:
        """``AWS::WAFRegional::RateBasedRule.RateLimit``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-ratebasedrule.html#cfn-wafregional-ratebasedrule-ratelimit
        """
        return self._values.get('rate_limit')

    @property
    def match_predicates(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnRateBasedRule.PredicateProperty"]]]]]:
        """``AWS::WAFRegional::RateBasedRule.MatchPredicates``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-ratebasedrule.html#cfn-wafregional-ratebasedrule-matchpredicates
        """
        return self._values.get('match_predicates')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnRateBasedRuleProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnRegexPatternSet(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-wafregional.CfnRegexPatternSet"):
    """A CloudFormation ``AWS::WAFRegional::RegexPatternSet``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-regexpatternset.html
    cloudformationResource:
    :cloudformationResource:: AWS::WAFRegional::RegexPatternSet
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, name: str, regex_pattern_strings: typing.List[str]) -> None:
        """Create a new ``AWS::WAFRegional::RegexPatternSet``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param name: ``AWS::WAFRegional::RegexPatternSet.Name``.
        :param regex_pattern_strings: ``AWS::WAFRegional::RegexPatternSet.RegexPatternStrings``.
        """
        props = CfnRegexPatternSetProps(name=name, regex_pattern_strings=regex_pattern_strings)

        jsii.create(CfnRegexPatternSet, self, [scope, id, props])

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
        """``AWS::WAFRegional::RegexPatternSet.Name``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-regexpatternset.html#cfn-wafregional-regexpatternset-name
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: str):
        return jsii.set(self, "name", value)

    @property
    @jsii.member(jsii_name="regexPatternStrings")
    def regex_pattern_strings(self) -> typing.List[str]:
        """``AWS::WAFRegional::RegexPatternSet.RegexPatternStrings``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-regexpatternset.html#cfn-wafregional-regexpatternset-regexpatternstrings
        """
        return jsii.get(self, "regexPatternStrings")

    @regex_pattern_strings.setter
    def regex_pattern_strings(self, value: typing.List[str]):
        return jsii.set(self, "regexPatternStrings", value)


@jsii.data_type(jsii_type="@aws-cdk/aws-wafregional.CfnRegexPatternSetProps", jsii_struct_bases=[], name_mapping={'name': 'name', 'regex_pattern_strings': 'regexPatternStrings'})
class CfnRegexPatternSetProps():
    def __init__(self, *, name: str, regex_pattern_strings: typing.List[str]):
        """Properties for defining a ``AWS::WAFRegional::RegexPatternSet``.

        :param name: ``AWS::WAFRegional::RegexPatternSet.Name``.
        :param regex_pattern_strings: ``AWS::WAFRegional::RegexPatternSet.RegexPatternStrings``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-regexpatternset.html
        """
        self._values = {
            'name': name,
            'regex_pattern_strings': regex_pattern_strings,
        }

    @property
    def name(self) -> str:
        """``AWS::WAFRegional::RegexPatternSet.Name``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-regexpatternset.html#cfn-wafregional-regexpatternset-name
        """
        return self._values.get('name')

    @property
    def regex_pattern_strings(self) -> typing.List[str]:
        """``AWS::WAFRegional::RegexPatternSet.RegexPatternStrings``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-regexpatternset.html#cfn-wafregional-regexpatternset-regexpatternstrings
        """
        return self._values.get('regex_pattern_strings')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnRegexPatternSetProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnRule(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-wafregional.CfnRule"):
    """A CloudFormation ``AWS::WAFRegional::Rule``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-rule.html
    cloudformationResource:
    :cloudformationResource:: AWS::WAFRegional::Rule
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, metric_name: str, name: str, predicates: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "PredicateProperty"]]]]]=None) -> None:
        """Create a new ``AWS::WAFRegional::Rule``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param metric_name: ``AWS::WAFRegional::Rule.MetricName``.
        :param name: ``AWS::WAFRegional::Rule.Name``.
        :param predicates: ``AWS::WAFRegional::Rule.Predicates``.
        """
        props = CfnRuleProps(metric_name=metric_name, name=name, predicates=predicates)

        jsii.create(CfnRule, self, [scope, id, props])

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
    @jsii.member(jsii_name="metricName")
    def metric_name(self) -> str:
        """``AWS::WAFRegional::Rule.MetricName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-rule.html#cfn-wafregional-rule-metricname
        """
        return jsii.get(self, "metricName")

    @metric_name.setter
    def metric_name(self, value: str):
        return jsii.set(self, "metricName", value)

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> str:
        """``AWS::WAFRegional::Rule.Name``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-rule.html#cfn-wafregional-rule-name
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: str):
        return jsii.set(self, "name", value)

    @property
    @jsii.member(jsii_name="predicates")
    def predicates(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "PredicateProperty"]]]]]:
        """``AWS::WAFRegional::Rule.Predicates``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-rule.html#cfn-wafregional-rule-predicates
        """
        return jsii.get(self, "predicates")

    @predicates.setter
    def predicates(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "PredicateProperty"]]]]]):
        return jsii.set(self, "predicates", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-wafregional.CfnRule.PredicateProperty", jsii_struct_bases=[], name_mapping={'data_id': 'dataId', 'negated': 'negated', 'type': 'type'})
    class PredicateProperty():
        def __init__(self, *, data_id: str, negated: typing.Union[bool, aws_cdk.core.IResolvable], type: str):
            """
            :param data_id: ``CfnRule.PredicateProperty.DataId``.
            :param negated: ``CfnRule.PredicateProperty.Negated``.
            :param type: ``CfnRule.PredicateProperty.Type``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-rule-predicate.html
            """
            self._values = {
                'data_id': data_id,
                'negated': negated,
                'type': type,
            }

        @property
        def data_id(self) -> str:
            """``CfnRule.PredicateProperty.DataId``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-rule-predicate.html#cfn-wafregional-rule-predicate-dataid
            """
            return self._values.get('data_id')

        @property
        def negated(self) -> typing.Union[bool, aws_cdk.core.IResolvable]:
            """``CfnRule.PredicateProperty.Negated``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-rule-predicate.html#cfn-wafregional-rule-predicate-negated
            """
            return self._values.get('negated')

        @property
        def type(self) -> str:
            """``CfnRule.PredicateProperty.Type``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-rule-predicate.html#cfn-wafregional-rule-predicate-type
            """
            return self._values.get('type')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'PredicateProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



@jsii.data_type(jsii_type="@aws-cdk/aws-wafregional.CfnRuleProps", jsii_struct_bases=[], name_mapping={'metric_name': 'metricName', 'name': 'name', 'predicates': 'predicates'})
class CfnRuleProps():
    def __init__(self, *, metric_name: str, name: str, predicates: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnRule.PredicateProperty"]]]]]=None):
        """Properties for defining a ``AWS::WAFRegional::Rule``.

        :param metric_name: ``AWS::WAFRegional::Rule.MetricName``.
        :param name: ``AWS::WAFRegional::Rule.Name``.
        :param predicates: ``AWS::WAFRegional::Rule.Predicates``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-rule.html
        """
        self._values = {
            'metric_name': metric_name,
            'name': name,
        }
        if predicates is not None: self._values["predicates"] = predicates

    @property
    def metric_name(self) -> str:
        """``AWS::WAFRegional::Rule.MetricName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-rule.html#cfn-wafregional-rule-metricname
        """
        return self._values.get('metric_name')

    @property
    def name(self) -> str:
        """``AWS::WAFRegional::Rule.Name``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-rule.html#cfn-wafregional-rule-name
        """
        return self._values.get('name')

    @property
    def predicates(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnRule.PredicateProperty"]]]]]:
        """``AWS::WAFRegional::Rule.Predicates``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-rule.html#cfn-wafregional-rule-predicates
        """
        return self._values.get('predicates')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnRuleProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnSizeConstraintSet(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-wafregional.CfnSizeConstraintSet"):
    """A CloudFormation ``AWS::WAFRegional::SizeConstraintSet``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-sizeconstraintset.html
    cloudformationResource:
    :cloudformationResource:: AWS::WAFRegional::SizeConstraintSet
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, name: str, size_constraints: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "SizeConstraintProperty"]]]]]=None) -> None:
        """Create a new ``AWS::WAFRegional::SizeConstraintSet``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param name: ``AWS::WAFRegional::SizeConstraintSet.Name``.
        :param size_constraints: ``AWS::WAFRegional::SizeConstraintSet.SizeConstraints``.
        """
        props = CfnSizeConstraintSetProps(name=name, size_constraints=size_constraints)

        jsii.create(CfnSizeConstraintSet, self, [scope, id, props])

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
        """``AWS::WAFRegional::SizeConstraintSet.Name``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-sizeconstraintset.html#cfn-wafregional-sizeconstraintset-name
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: str):
        return jsii.set(self, "name", value)

    @property
    @jsii.member(jsii_name="sizeConstraints")
    def size_constraints(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "SizeConstraintProperty"]]]]]:
        """``AWS::WAFRegional::SizeConstraintSet.SizeConstraints``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-sizeconstraintset.html#cfn-wafregional-sizeconstraintset-sizeconstraints
        """
        return jsii.get(self, "sizeConstraints")

    @size_constraints.setter
    def size_constraints(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "SizeConstraintProperty"]]]]]):
        return jsii.set(self, "sizeConstraints", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-wafregional.CfnSizeConstraintSet.FieldToMatchProperty", jsii_struct_bases=[], name_mapping={'type': 'type', 'data': 'data'})
    class FieldToMatchProperty():
        def __init__(self, *, type: str, data: typing.Optional[str]=None):
            """
            :param type: ``CfnSizeConstraintSet.FieldToMatchProperty.Type``.
            :param data: ``CfnSizeConstraintSet.FieldToMatchProperty.Data``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-sizeconstraintset-fieldtomatch.html
            """
            self._values = {
                'type': type,
            }
            if data is not None: self._values["data"] = data

        @property
        def type(self) -> str:
            """``CfnSizeConstraintSet.FieldToMatchProperty.Type``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-sizeconstraintset-fieldtomatch.html#cfn-wafregional-sizeconstraintset-fieldtomatch-type
            """
            return self._values.get('type')

        @property
        def data(self) -> typing.Optional[str]:
            """``CfnSizeConstraintSet.FieldToMatchProperty.Data``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-sizeconstraintset-fieldtomatch.html#cfn-wafregional-sizeconstraintset-fieldtomatch-data
            """
            return self._values.get('data')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'FieldToMatchProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-wafregional.CfnSizeConstraintSet.SizeConstraintProperty", jsii_struct_bases=[], name_mapping={'comparison_operator': 'comparisonOperator', 'field_to_match': 'fieldToMatch', 'size': 'size', 'text_transformation': 'textTransformation'})
    class SizeConstraintProperty():
        def __init__(self, *, comparison_operator: str, field_to_match: typing.Union[aws_cdk.core.IResolvable, "CfnSizeConstraintSet.FieldToMatchProperty"], size: jsii.Number, text_transformation: str):
            """
            :param comparison_operator: ``CfnSizeConstraintSet.SizeConstraintProperty.ComparisonOperator``.
            :param field_to_match: ``CfnSizeConstraintSet.SizeConstraintProperty.FieldToMatch``.
            :param size: ``CfnSizeConstraintSet.SizeConstraintProperty.Size``.
            :param text_transformation: ``CfnSizeConstraintSet.SizeConstraintProperty.TextTransformation``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-sizeconstraintset-sizeconstraint.html
            """
            self._values = {
                'comparison_operator': comparison_operator,
                'field_to_match': field_to_match,
                'size': size,
                'text_transformation': text_transformation,
            }

        @property
        def comparison_operator(self) -> str:
            """``CfnSizeConstraintSet.SizeConstraintProperty.ComparisonOperator``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-sizeconstraintset-sizeconstraint.html#cfn-wafregional-sizeconstraintset-sizeconstraint-comparisonoperator
            """
            return self._values.get('comparison_operator')

        @property
        def field_to_match(self) -> typing.Union[aws_cdk.core.IResolvable, "CfnSizeConstraintSet.FieldToMatchProperty"]:
            """``CfnSizeConstraintSet.SizeConstraintProperty.FieldToMatch``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-sizeconstraintset-sizeconstraint.html#cfn-wafregional-sizeconstraintset-sizeconstraint-fieldtomatch
            """
            return self._values.get('field_to_match')

        @property
        def size(self) -> jsii.Number:
            """``CfnSizeConstraintSet.SizeConstraintProperty.Size``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-sizeconstraintset-sizeconstraint.html#cfn-wafregional-sizeconstraintset-sizeconstraint-size
            """
            return self._values.get('size')

        @property
        def text_transformation(self) -> str:
            """``CfnSizeConstraintSet.SizeConstraintProperty.TextTransformation``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-sizeconstraintset-sizeconstraint.html#cfn-wafregional-sizeconstraintset-sizeconstraint-texttransformation
            """
            return self._values.get('text_transformation')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'SizeConstraintProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



@jsii.data_type(jsii_type="@aws-cdk/aws-wafregional.CfnSizeConstraintSetProps", jsii_struct_bases=[], name_mapping={'name': 'name', 'size_constraints': 'sizeConstraints'})
class CfnSizeConstraintSetProps():
    def __init__(self, *, name: str, size_constraints: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnSizeConstraintSet.SizeConstraintProperty"]]]]]=None):
        """Properties for defining a ``AWS::WAFRegional::SizeConstraintSet``.

        :param name: ``AWS::WAFRegional::SizeConstraintSet.Name``.
        :param size_constraints: ``AWS::WAFRegional::SizeConstraintSet.SizeConstraints``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-sizeconstraintset.html
        """
        self._values = {
            'name': name,
        }
        if size_constraints is not None: self._values["size_constraints"] = size_constraints

    @property
    def name(self) -> str:
        """``AWS::WAFRegional::SizeConstraintSet.Name``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-sizeconstraintset.html#cfn-wafregional-sizeconstraintset-name
        """
        return self._values.get('name')

    @property
    def size_constraints(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnSizeConstraintSet.SizeConstraintProperty"]]]]]:
        """``AWS::WAFRegional::SizeConstraintSet.SizeConstraints``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-sizeconstraintset.html#cfn-wafregional-sizeconstraintset-sizeconstraints
        """
        return self._values.get('size_constraints')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnSizeConstraintSetProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnSqlInjectionMatchSet(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-wafregional.CfnSqlInjectionMatchSet"):
    """A CloudFormation ``AWS::WAFRegional::SqlInjectionMatchSet``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-sqlinjectionmatchset.html
    cloudformationResource:
    :cloudformationResource:: AWS::WAFRegional::SqlInjectionMatchSet
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, name: str, sql_injection_match_tuples: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "SqlInjectionMatchTupleProperty"]]]]]=None) -> None:
        """Create a new ``AWS::WAFRegional::SqlInjectionMatchSet``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param name: ``AWS::WAFRegional::SqlInjectionMatchSet.Name``.
        :param sql_injection_match_tuples: ``AWS::WAFRegional::SqlInjectionMatchSet.SqlInjectionMatchTuples``.
        """
        props = CfnSqlInjectionMatchSetProps(name=name, sql_injection_match_tuples=sql_injection_match_tuples)

        jsii.create(CfnSqlInjectionMatchSet, self, [scope, id, props])

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
        """``AWS::WAFRegional::SqlInjectionMatchSet.Name``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-sqlinjectionmatchset.html#cfn-wafregional-sqlinjectionmatchset-name
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: str):
        return jsii.set(self, "name", value)

    @property
    @jsii.member(jsii_name="sqlInjectionMatchTuples")
    def sql_injection_match_tuples(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "SqlInjectionMatchTupleProperty"]]]]]:
        """``AWS::WAFRegional::SqlInjectionMatchSet.SqlInjectionMatchTuples``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-sqlinjectionmatchset.html#cfn-wafregional-sqlinjectionmatchset-sqlinjectionmatchtuples
        """
        return jsii.get(self, "sqlInjectionMatchTuples")

    @sql_injection_match_tuples.setter
    def sql_injection_match_tuples(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "SqlInjectionMatchTupleProperty"]]]]]):
        return jsii.set(self, "sqlInjectionMatchTuples", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-wafregional.CfnSqlInjectionMatchSet.FieldToMatchProperty", jsii_struct_bases=[], name_mapping={'type': 'type', 'data': 'data'})
    class FieldToMatchProperty():
        def __init__(self, *, type: str, data: typing.Optional[str]=None):
            """
            :param type: ``CfnSqlInjectionMatchSet.FieldToMatchProperty.Type``.
            :param data: ``CfnSqlInjectionMatchSet.FieldToMatchProperty.Data``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-sqlinjectionmatchset-fieldtomatch.html
            """
            self._values = {
                'type': type,
            }
            if data is not None: self._values["data"] = data

        @property
        def type(self) -> str:
            """``CfnSqlInjectionMatchSet.FieldToMatchProperty.Type``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-sqlinjectionmatchset-fieldtomatch.html#cfn-wafregional-sqlinjectionmatchset-fieldtomatch-type
            """
            return self._values.get('type')

        @property
        def data(self) -> typing.Optional[str]:
            """``CfnSqlInjectionMatchSet.FieldToMatchProperty.Data``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-sqlinjectionmatchset-fieldtomatch.html#cfn-wafregional-sqlinjectionmatchset-fieldtomatch-data
            """
            return self._values.get('data')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'FieldToMatchProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-wafregional.CfnSqlInjectionMatchSet.SqlInjectionMatchTupleProperty", jsii_struct_bases=[], name_mapping={'field_to_match': 'fieldToMatch', 'text_transformation': 'textTransformation'})
    class SqlInjectionMatchTupleProperty():
        def __init__(self, *, field_to_match: typing.Union[aws_cdk.core.IResolvable, "CfnSqlInjectionMatchSet.FieldToMatchProperty"], text_transformation: str):
            """
            :param field_to_match: ``CfnSqlInjectionMatchSet.SqlInjectionMatchTupleProperty.FieldToMatch``.
            :param text_transformation: ``CfnSqlInjectionMatchSet.SqlInjectionMatchTupleProperty.TextTransformation``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-sqlinjectionmatchset-sqlinjectionmatchtuple.html
            """
            self._values = {
                'field_to_match': field_to_match,
                'text_transformation': text_transformation,
            }

        @property
        def field_to_match(self) -> typing.Union[aws_cdk.core.IResolvable, "CfnSqlInjectionMatchSet.FieldToMatchProperty"]:
            """``CfnSqlInjectionMatchSet.SqlInjectionMatchTupleProperty.FieldToMatch``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-sqlinjectionmatchset-sqlinjectionmatchtuple.html#cfn-wafregional-sqlinjectionmatchset-sqlinjectionmatchtuple-fieldtomatch
            """
            return self._values.get('field_to_match')

        @property
        def text_transformation(self) -> str:
            """``CfnSqlInjectionMatchSet.SqlInjectionMatchTupleProperty.TextTransformation``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-sqlinjectionmatchset-sqlinjectionmatchtuple.html#cfn-wafregional-sqlinjectionmatchset-sqlinjectionmatchtuple-texttransformation
            """
            return self._values.get('text_transformation')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'SqlInjectionMatchTupleProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



@jsii.data_type(jsii_type="@aws-cdk/aws-wafregional.CfnSqlInjectionMatchSetProps", jsii_struct_bases=[], name_mapping={'name': 'name', 'sql_injection_match_tuples': 'sqlInjectionMatchTuples'})
class CfnSqlInjectionMatchSetProps():
    def __init__(self, *, name: str, sql_injection_match_tuples: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnSqlInjectionMatchSet.SqlInjectionMatchTupleProperty"]]]]]=None):
        """Properties for defining a ``AWS::WAFRegional::SqlInjectionMatchSet``.

        :param name: ``AWS::WAFRegional::SqlInjectionMatchSet.Name``.
        :param sql_injection_match_tuples: ``AWS::WAFRegional::SqlInjectionMatchSet.SqlInjectionMatchTuples``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-sqlinjectionmatchset.html
        """
        self._values = {
            'name': name,
        }
        if sql_injection_match_tuples is not None: self._values["sql_injection_match_tuples"] = sql_injection_match_tuples

    @property
    def name(self) -> str:
        """``AWS::WAFRegional::SqlInjectionMatchSet.Name``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-sqlinjectionmatchset.html#cfn-wafregional-sqlinjectionmatchset-name
        """
        return self._values.get('name')

    @property
    def sql_injection_match_tuples(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnSqlInjectionMatchSet.SqlInjectionMatchTupleProperty"]]]]]:
        """``AWS::WAFRegional::SqlInjectionMatchSet.SqlInjectionMatchTuples``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-sqlinjectionmatchset.html#cfn-wafregional-sqlinjectionmatchset-sqlinjectionmatchtuples
        """
        return self._values.get('sql_injection_match_tuples')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnSqlInjectionMatchSetProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnWebACL(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-wafregional.CfnWebACL"):
    """A CloudFormation ``AWS::WAFRegional::WebACL``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-webacl.html
    cloudformationResource:
    :cloudformationResource:: AWS::WAFRegional::WebACL
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, default_action: typing.Union["ActionProperty", aws_cdk.core.IResolvable], metric_name: str, name: str, rules: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "RuleProperty"]]]]]=None) -> None:
        """Create a new ``AWS::WAFRegional::WebACL``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param default_action: ``AWS::WAFRegional::WebACL.DefaultAction``.
        :param metric_name: ``AWS::WAFRegional::WebACL.MetricName``.
        :param name: ``AWS::WAFRegional::WebACL.Name``.
        :param rules: ``AWS::WAFRegional::WebACL.Rules``.
        """
        props = CfnWebACLProps(default_action=default_action, metric_name=metric_name, name=name, rules=rules)

        jsii.create(CfnWebACL, self, [scope, id, props])

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
    @jsii.member(jsii_name="defaultAction")
    def default_action(self) -> typing.Union["ActionProperty", aws_cdk.core.IResolvable]:
        """``AWS::WAFRegional::WebACL.DefaultAction``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-webacl.html#cfn-wafregional-webacl-defaultaction
        """
        return jsii.get(self, "defaultAction")

    @default_action.setter
    def default_action(self, value: typing.Union["ActionProperty", aws_cdk.core.IResolvable]):
        return jsii.set(self, "defaultAction", value)

    @property
    @jsii.member(jsii_name="metricName")
    def metric_name(self) -> str:
        """``AWS::WAFRegional::WebACL.MetricName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-webacl.html#cfn-wafregional-webacl-metricname
        """
        return jsii.get(self, "metricName")

    @metric_name.setter
    def metric_name(self, value: str):
        return jsii.set(self, "metricName", value)

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> str:
        """``AWS::WAFRegional::WebACL.Name``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-webacl.html#cfn-wafregional-webacl-name
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: str):
        return jsii.set(self, "name", value)

    @property
    @jsii.member(jsii_name="rules")
    def rules(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "RuleProperty"]]]]]:
        """``AWS::WAFRegional::WebACL.Rules``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-webacl.html#cfn-wafregional-webacl-rules
        """
        return jsii.get(self, "rules")

    @rules.setter
    def rules(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "RuleProperty"]]]]]):
        return jsii.set(self, "rules", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-wafregional.CfnWebACL.ActionProperty", jsii_struct_bases=[], name_mapping={'type': 'type'})
    class ActionProperty():
        def __init__(self, *, type: str):
            """
            :param type: ``CfnWebACL.ActionProperty.Type``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-webacl-action.html
            """
            self._values = {
                'type': type,
            }

        @property
        def type(self) -> str:
            """``CfnWebACL.ActionProperty.Type``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-webacl-action.html#cfn-wafregional-webacl-action-type
            """
            return self._values.get('type')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'ActionProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-wafregional.CfnWebACL.RuleProperty", jsii_struct_bases=[], name_mapping={'action': 'action', 'priority': 'priority', 'rule_id': 'ruleId'})
    class RuleProperty():
        def __init__(self, *, action: typing.Union["CfnWebACL.ActionProperty", aws_cdk.core.IResolvable], priority: jsii.Number, rule_id: str):
            """
            :param action: ``CfnWebACL.RuleProperty.Action``.
            :param priority: ``CfnWebACL.RuleProperty.Priority``.
            :param rule_id: ``CfnWebACL.RuleProperty.RuleId``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-webacl-rule.html
            """
            self._values = {
                'action': action,
                'priority': priority,
                'rule_id': rule_id,
            }

        @property
        def action(self) -> typing.Union["CfnWebACL.ActionProperty", aws_cdk.core.IResolvable]:
            """``CfnWebACL.RuleProperty.Action``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-webacl-rule.html#cfn-wafregional-webacl-rule-action
            """
            return self._values.get('action')

        @property
        def priority(self) -> jsii.Number:
            """``CfnWebACL.RuleProperty.Priority``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-webacl-rule.html#cfn-wafregional-webacl-rule-priority
            """
            return self._values.get('priority')

        @property
        def rule_id(self) -> str:
            """``CfnWebACL.RuleProperty.RuleId``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-webacl-rule.html#cfn-wafregional-webacl-rule-ruleid
            """
            return self._values.get('rule_id')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'RuleProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



class CfnWebACLAssociation(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-wafregional.CfnWebACLAssociation"):
    """A CloudFormation ``AWS::WAFRegional::WebACLAssociation``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-webaclassociation.html
    cloudformationResource:
    :cloudformationResource:: AWS::WAFRegional::WebACLAssociation
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, resource_arn: str, web_acl_id: str) -> None:
        """Create a new ``AWS::WAFRegional::WebACLAssociation``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param resource_arn: ``AWS::WAFRegional::WebACLAssociation.ResourceArn``.
        :param web_acl_id: ``AWS::WAFRegional::WebACLAssociation.WebACLId``.
        """
        props = CfnWebACLAssociationProps(resource_arn=resource_arn, web_acl_id=web_acl_id)

        jsii.create(CfnWebACLAssociation, self, [scope, id, props])

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
    @jsii.member(jsii_name="resourceArn")
    def resource_arn(self) -> str:
        """``AWS::WAFRegional::WebACLAssociation.ResourceArn``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-webaclassociation.html#cfn-wafregional-webaclassociation-resourcearn
        """
        return jsii.get(self, "resourceArn")

    @resource_arn.setter
    def resource_arn(self, value: str):
        return jsii.set(self, "resourceArn", value)

    @property
    @jsii.member(jsii_name="webAclId")
    def web_acl_id(self) -> str:
        """``AWS::WAFRegional::WebACLAssociation.WebACLId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-webaclassociation.html#cfn-wafregional-webaclassociation-webaclid
        """
        return jsii.get(self, "webAclId")

    @web_acl_id.setter
    def web_acl_id(self, value: str):
        return jsii.set(self, "webAclId", value)


@jsii.data_type(jsii_type="@aws-cdk/aws-wafregional.CfnWebACLAssociationProps", jsii_struct_bases=[], name_mapping={'resource_arn': 'resourceArn', 'web_acl_id': 'webAclId'})
class CfnWebACLAssociationProps():
    def __init__(self, *, resource_arn: str, web_acl_id: str):
        """Properties for defining a ``AWS::WAFRegional::WebACLAssociation``.

        :param resource_arn: ``AWS::WAFRegional::WebACLAssociation.ResourceArn``.
        :param web_acl_id: ``AWS::WAFRegional::WebACLAssociation.WebACLId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-webaclassociation.html
        """
        self._values = {
            'resource_arn': resource_arn,
            'web_acl_id': web_acl_id,
        }

    @property
    def resource_arn(self) -> str:
        """``AWS::WAFRegional::WebACLAssociation.ResourceArn``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-webaclassociation.html#cfn-wafregional-webaclassociation-resourcearn
        """
        return self._values.get('resource_arn')

    @property
    def web_acl_id(self) -> str:
        """``AWS::WAFRegional::WebACLAssociation.WebACLId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-webaclassociation.html#cfn-wafregional-webaclassociation-webaclid
        """
        return self._values.get('web_acl_id')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnWebACLAssociationProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


@jsii.data_type(jsii_type="@aws-cdk/aws-wafregional.CfnWebACLProps", jsii_struct_bases=[], name_mapping={'default_action': 'defaultAction', 'metric_name': 'metricName', 'name': 'name', 'rules': 'rules'})
class CfnWebACLProps():
    def __init__(self, *, default_action: typing.Union["CfnWebACL.ActionProperty", aws_cdk.core.IResolvable], metric_name: str, name: str, rules: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnWebACL.RuleProperty"]]]]]=None):
        """Properties for defining a ``AWS::WAFRegional::WebACL``.

        :param default_action: ``AWS::WAFRegional::WebACL.DefaultAction``.
        :param metric_name: ``AWS::WAFRegional::WebACL.MetricName``.
        :param name: ``AWS::WAFRegional::WebACL.Name``.
        :param rules: ``AWS::WAFRegional::WebACL.Rules``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-webacl.html
        """
        self._values = {
            'default_action': default_action,
            'metric_name': metric_name,
            'name': name,
        }
        if rules is not None: self._values["rules"] = rules

    @property
    def default_action(self) -> typing.Union["CfnWebACL.ActionProperty", aws_cdk.core.IResolvable]:
        """``AWS::WAFRegional::WebACL.DefaultAction``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-webacl.html#cfn-wafregional-webacl-defaultaction
        """
        return self._values.get('default_action')

    @property
    def metric_name(self) -> str:
        """``AWS::WAFRegional::WebACL.MetricName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-webacl.html#cfn-wafregional-webacl-metricname
        """
        return self._values.get('metric_name')

    @property
    def name(self) -> str:
        """``AWS::WAFRegional::WebACL.Name``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-webacl.html#cfn-wafregional-webacl-name
        """
        return self._values.get('name')

    @property
    def rules(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnWebACL.RuleProperty"]]]]]:
        """``AWS::WAFRegional::WebACL.Rules``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-webacl.html#cfn-wafregional-webacl-rules
        """
        return self._values.get('rules')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnWebACLProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnXssMatchSet(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-wafregional.CfnXssMatchSet"):
    """A CloudFormation ``AWS::WAFRegional::XssMatchSet``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-xssmatchset.html
    cloudformationResource:
    :cloudformationResource:: AWS::WAFRegional::XssMatchSet
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, name: str, xss_match_tuples: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "XssMatchTupleProperty"]]]]]=None) -> None:
        """Create a new ``AWS::WAFRegional::XssMatchSet``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param name: ``AWS::WAFRegional::XssMatchSet.Name``.
        :param xss_match_tuples: ``AWS::WAFRegional::XssMatchSet.XssMatchTuples``.
        """
        props = CfnXssMatchSetProps(name=name, xss_match_tuples=xss_match_tuples)

        jsii.create(CfnXssMatchSet, self, [scope, id, props])

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
        """``AWS::WAFRegional::XssMatchSet.Name``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-xssmatchset.html#cfn-wafregional-xssmatchset-name
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: str):
        return jsii.set(self, "name", value)

    @property
    @jsii.member(jsii_name="xssMatchTuples")
    def xss_match_tuples(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "XssMatchTupleProperty"]]]]]:
        """``AWS::WAFRegional::XssMatchSet.XssMatchTuples``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-xssmatchset.html#cfn-wafregional-xssmatchset-xssmatchtuples
        """
        return jsii.get(self, "xssMatchTuples")

    @xss_match_tuples.setter
    def xss_match_tuples(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "XssMatchTupleProperty"]]]]]):
        return jsii.set(self, "xssMatchTuples", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-wafregional.CfnXssMatchSet.FieldToMatchProperty", jsii_struct_bases=[], name_mapping={'type': 'type', 'data': 'data'})
    class FieldToMatchProperty():
        def __init__(self, *, type: str, data: typing.Optional[str]=None):
            """
            :param type: ``CfnXssMatchSet.FieldToMatchProperty.Type``.
            :param data: ``CfnXssMatchSet.FieldToMatchProperty.Data``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-xssmatchset-fieldtomatch.html
            """
            self._values = {
                'type': type,
            }
            if data is not None: self._values["data"] = data

        @property
        def type(self) -> str:
            """``CfnXssMatchSet.FieldToMatchProperty.Type``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-xssmatchset-fieldtomatch.html#cfn-wafregional-xssmatchset-fieldtomatch-type
            """
            return self._values.get('type')

        @property
        def data(self) -> typing.Optional[str]:
            """``CfnXssMatchSet.FieldToMatchProperty.Data``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-xssmatchset-fieldtomatch.html#cfn-wafregional-xssmatchset-fieldtomatch-data
            """
            return self._values.get('data')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'FieldToMatchProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-wafregional.CfnXssMatchSet.XssMatchTupleProperty", jsii_struct_bases=[], name_mapping={'field_to_match': 'fieldToMatch', 'text_transformation': 'textTransformation'})
    class XssMatchTupleProperty():
        def __init__(self, *, field_to_match: typing.Union[aws_cdk.core.IResolvable, "CfnXssMatchSet.FieldToMatchProperty"], text_transformation: str):
            """
            :param field_to_match: ``CfnXssMatchSet.XssMatchTupleProperty.FieldToMatch``.
            :param text_transformation: ``CfnXssMatchSet.XssMatchTupleProperty.TextTransformation``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-xssmatchset-xssmatchtuple.html
            """
            self._values = {
                'field_to_match': field_to_match,
                'text_transformation': text_transformation,
            }

        @property
        def field_to_match(self) -> typing.Union[aws_cdk.core.IResolvable, "CfnXssMatchSet.FieldToMatchProperty"]:
            """``CfnXssMatchSet.XssMatchTupleProperty.FieldToMatch``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-xssmatchset-xssmatchtuple.html#cfn-wafregional-xssmatchset-xssmatchtuple-fieldtomatch
            """
            return self._values.get('field_to_match')

        @property
        def text_transformation(self) -> str:
            """``CfnXssMatchSet.XssMatchTupleProperty.TextTransformation``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-xssmatchset-xssmatchtuple.html#cfn-wafregional-xssmatchset-xssmatchtuple-texttransformation
            """
            return self._values.get('text_transformation')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'XssMatchTupleProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



@jsii.data_type(jsii_type="@aws-cdk/aws-wafregional.CfnXssMatchSetProps", jsii_struct_bases=[], name_mapping={'name': 'name', 'xss_match_tuples': 'xssMatchTuples'})
class CfnXssMatchSetProps():
    def __init__(self, *, name: str, xss_match_tuples: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnXssMatchSet.XssMatchTupleProperty"]]]]]=None):
        """Properties for defining a ``AWS::WAFRegional::XssMatchSet``.

        :param name: ``AWS::WAFRegional::XssMatchSet.Name``.
        :param xss_match_tuples: ``AWS::WAFRegional::XssMatchSet.XssMatchTuples``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-xssmatchset.html
        """
        self._values = {
            'name': name,
        }
        if xss_match_tuples is not None: self._values["xss_match_tuples"] = xss_match_tuples

    @property
    def name(self) -> str:
        """``AWS::WAFRegional::XssMatchSet.Name``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-xssmatchset.html#cfn-wafregional-xssmatchset-name
        """
        return self._values.get('name')

    @property
    def xss_match_tuples(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnXssMatchSet.XssMatchTupleProperty"]]]]]:
        """``AWS::WAFRegional::XssMatchSet.XssMatchTuples``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-xssmatchset.html#cfn-wafregional-xssmatchset-xssmatchtuples
        """
        return self._values.get('xss_match_tuples')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnXssMatchSetProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


__all__ = ["CfnByteMatchSet", "CfnByteMatchSetProps", "CfnGeoMatchSet", "CfnGeoMatchSetProps", "CfnIPSet", "CfnIPSetProps", "CfnRateBasedRule", "CfnRateBasedRuleProps", "CfnRegexPatternSet", "CfnRegexPatternSetProps", "CfnRule", "CfnRuleProps", "CfnSizeConstraintSet", "CfnSizeConstraintSetProps", "CfnSqlInjectionMatchSet", "CfnSqlInjectionMatchSetProps", "CfnWebACL", "CfnWebACLAssociation", "CfnWebACLAssociationProps", "CfnWebACLProps", "CfnXssMatchSet", "CfnXssMatchSetProps", "__jsii_assembly__"]

publication.publish()
