import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.core
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-iot", "1.15.0", __name__, "aws-iot@1.15.0.jsii.tgz")
class CfnCertificate(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-iot.CfnCertificate"):
    """A CloudFormation ``AWS::IoT::Certificate``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-certificate.html
    cloudformationResource:
    :cloudformationResource:: AWS::IoT::Certificate
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, certificate_signing_request: str, status: str) -> None:
        """Create a new ``AWS::IoT::Certificate``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param certificate_signing_request: ``AWS::IoT::Certificate.CertificateSigningRequest``.
        :param status: ``AWS::IoT::Certificate.Status``.
        """
        props = CfnCertificateProps(certificate_signing_request=certificate_signing_request, status=status)

        jsii.create(CfnCertificate, self, [scope, id, props])

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
    @jsii.member(jsii_name="certificateSigningRequest")
    def certificate_signing_request(self) -> str:
        """``AWS::IoT::Certificate.CertificateSigningRequest``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-certificate.html#cfn-iot-certificate-certificatesigningrequest
        """
        return jsii.get(self, "certificateSigningRequest")

    @certificate_signing_request.setter
    def certificate_signing_request(self, value: str):
        return jsii.set(self, "certificateSigningRequest", value)

    @property
    @jsii.member(jsii_name="status")
    def status(self) -> str:
        """``AWS::IoT::Certificate.Status``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-certificate.html#cfn-iot-certificate-status
        """
        return jsii.get(self, "status")

    @status.setter
    def status(self, value: str):
        return jsii.set(self, "status", value)


@jsii.data_type(jsii_type="@aws-cdk/aws-iot.CfnCertificateProps", jsii_struct_bases=[], name_mapping={'certificate_signing_request': 'certificateSigningRequest', 'status': 'status'})
class CfnCertificateProps():
    def __init__(self, *, certificate_signing_request: str, status: str):
        """Properties for defining a ``AWS::IoT::Certificate``.

        :param certificate_signing_request: ``AWS::IoT::Certificate.CertificateSigningRequest``.
        :param status: ``AWS::IoT::Certificate.Status``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-certificate.html
        """
        self._values = {
            'certificate_signing_request': certificate_signing_request,
            'status': status,
        }

    @property
    def certificate_signing_request(self) -> str:
        """``AWS::IoT::Certificate.CertificateSigningRequest``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-certificate.html#cfn-iot-certificate-certificatesigningrequest
        """
        return self._values.get('certificate_signing_request')

    @property
    def status(self) -> str:
        """``AWS::IoT::Certificate.Status``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-certificate.html#cfn-iot-certificate-status
        """
        return self._values.get('status')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnCertificateProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnPolicy(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-iot.CfnPolicy"):
    """A CloudFormation ``AWS::IoT::Policy``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-policy.html
    cloudformationResource:
    :cloudformationResource:: AWS::IoT::Policy
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, policy_document: typing.Any, policy_name: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::IoT::Policy``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param policy_document: ``AWS::IoT::Policy.PolicyDocument``.
        :param policy_name: ``AWS::IoT::Policy.PolicyName``.
        """
        props = CfnPolicyProps(policy_document=policy_document, policy_name=policy_name)

        jsii.create(CfnPolicy, self, [scope, id, props])

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
    @jsii.member(jsii_name="policyDocument")
    def policy_document(self) -> typing.Any:
        """``AWS::IoT::Policy.PolicyDocument``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-policy.html#cfn-iot-policy-policydocument
        """
        return jsii.get(self, "policyDocument")

    @policy_document.setter
    def policy_document(self, value: typing.Any):
        return jsii.set(self, "policyDocument", value)

    @property
    @jsii.member(jsii_name="policyName")
    def policy_name(self) -> typing.Optional[str]:
        """``AWS::IoT::Policy.PolicyName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-policy.html#cfn-iot-policy-policyname
        """
        return jsii.get(self, "policyName")

    @policy_name.setter
    def policy_name(self, value: typing.Optional[str]):
        return jsii.set(self, "policyName", value)


class CfnPolicyPrincipalAttachment(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-iot.CfnPolicyPrincipalAttachment"):
    """A CloudFormation ``AWS::IoT::PolicyPrincipalAttachment``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-policyprincipalattachment.html
    cloudformationResource:
    :cloudformationResource:: AWS::IoT::PolicyPrincipalAttachment
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, policy_name: str, principal: str) -> None:
        """Create a new ``AWS::IoT::PolicyPrincipalAttachment``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param policy_name: ``AWS::IoT::PolicyPrincipalAttachment.PolicyName``.
        :param principal: ``AWS::IoT::PolicyPrincipalAttachment.Principal``.
        """
        props = CfnPolicyPrincipalAttachmentProps(policy_name=policy_name, principal=principal)

        jsii.create(CfnPolicyPrincipalAttachment, self, [scope, id, props])

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
    @jsii.member(jsii_name="policyName")
    def policy_name(self) -> str:
        """``AWS::IoT::PolicyPrincipalAttachment.PolicyName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-policyprincipalattachment.html#cfn-iot-policyprincipalattachment-policyname
        """
        return jsii.get(self, "policyName")

    @policy_name.setter
    def policy_name(self, value: str):
        return jsii.set(self, "policyName", value)

    @property
    @jsii.member(jsii_name="principal")
    def principal(self) -> str:
        """``AWS::IoT::PolicyPrincipalAttachment.Principal``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-policyprincipalattachment.html#cfn-iot-policyprincipalattachment-principal
        """
        return jsii.get(self, "principal")

    @principal.setter
    def principal(self, value: str):
        return jsii.set(self, "principal", value)


@jsii.data_type(jsii_type="@aws-cdk/aws-iot.CfnPolicyPrincipalAttachmentProps", jsii_struct_bases=[], name_mapping={'policy_name': 'policyName', 'principal': 'principal'})
class CfnPolicyPrincipalAttachmentProps():
    def __init__(self, *, policy_name: str, principal: str):
        """Properties for defining a ``AWS::IoT::PolicyPrincipalAttachment``.

        :param policy_name: ``AWS::IoT::PolicyPrincipalAttachment.PolicyName``.
        :param principal: ``AWS::IoT::PolicyPrincipalAttachment.Principal``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-policyprincipalattachment.html
        """
        self._values = {
            'policy_name': policy_name,
            'principal': principal,
        }

    @property
    def policy_name(self) -> str:
        """``AWS::IoT::PolicyPrincipalAttachment.PolicyName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-policyprincipalattachment.html#cfn-iot-policyprincipalattachment-policyname
        """
        return self._values.get('policy_name')

    @property
    def principal(self) -> str:
        """``AWS::IoT::PolicyPrincipalAttachment.Principal``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-policyprincipalattachment.html#cfn-iot-policyprincipalattachment-principal
        """
        return self._values.get('principal')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnPolicyPrincipalAttachmentProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


@jsii.data_type(jsii_type="@aws-cdk/aws-iot.CfnPolicyProps", jsii_struct_bases=[], name_mapping={'policy_document': 'policyDocument', 'policy_name': 'policyName'})
class CfnPolicyProps():
    def __init__(self, *, policy_document: typing.Any, policy_name: typing.Optional[str]=None):
        """Properties for defining a ``AWS::IoT::Policy``.

        :param policy_document: ``AWS::IoT::Policy.PolicyDocument``.
        :param policy_name: ``AWS::IoT::Policy.PolicyName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-policy.html
        """
        self._values = {
            'policy_document': policy_document,
        }
        if policy_name is not None: self._values["policy_name"] = policy_name

    @property
    def policy_document(self) -> typing.Any:
        """``AWS::IoT::Policy.PolicyDocument``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-policy.html#cfn-iot-policy-policydocument
        """
        return self._values.get('policy_document')

    @property
    def policy_name(self) -> typing.Optional[str]:
        """``AWS::IoT::Policy.PolicyName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-policy.html#cfn-iot-policy-policyname
        """
        return self._values.get('policy_name')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnPolicyProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnThing(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-iot.CfnThing"):
    """A CloudFormation ``AWS::IoT::Thing``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-thing.html
    cloudformationResource:
    :cloudformationResource:: AWS::IoT::Thing
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, attribute_payload: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["AttributePayloadProperty"]]]=None, thing_name: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::IoT::Thing``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param attribute_payload: ``AWS::IoT::Thing.AttributePayload``.
        :param thing_name: ``AWS::IoT::Thing.ThingName``.
        """
        props = CfnThingProps(attribute_payload=attribute_payload, thing_name=thing_name)

        jsii.create(CfnThing, self, [scope, id, props])

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
    @jsii.member(jsii_name="attributePayload")
    def attribute_payload(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["AttributePayloadProperty"]]]:
        """``AWS::IoT::Thing.AttributePayload``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-thing.html#cfn-iot-thing-attributepayload
        """
        return jsii.get(self, "attributePayload")

    @attribute_payload.setter
    def attribute_payload(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["AttributePayloadProperty"]]]):
        return jsii.set(self, "attributePayload", value)

    @property
    @jsii.member(jsii_name="thingName")
    def thing_name(self) -> typing.Optional[str]:
        """``AWS::IoT::Thing.ThingName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-thing.html#cfn-iot-thing-thingname
        """
        return jsii.get(self, "thingName")

    @thing_name.setter
    def thing_name(self, value: typing.Optional[str]):
        return jsii.set(self, "thingName", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-iot.CfnThing.AttributePayloadProperty", jsii_struct_bases=[], name_mapping={'attributes': 'attributes'})
    class AttributePayloadProperty():
        def __init__(self, *, attributes: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.Mapping[str,str]]]]=None):
            """
            :param attributes: ``CfnThing.AttributePayloadProperty.Attributes``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-thing-attributepayload.html
            """
            self._values = {
            }
            if attributes is not None: self._values["attributes"] = attributes

        @property
        def attributes(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.Mapping[str,str]]]]:
            """``CfnThing.AttributePayloadProperty.Attributes``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-thing-attributepayload.html#cfn-iot-thing-attributepayload-attributes
            """
            return self._values.get('attributes')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'AttributePayloadProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



class CfnThingPrincipalAttachment(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-iot.CfnThingPrincipalAttachment"):
    """A CloudFormation ``AWS::IoT::ThingPrincipalAttachment``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-thingprincipalattachment.html
    cloudformationResource:
    :cloudformationResource:: AWS::IoT::ThingPrincipalAttachment
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, principal: str, thing_name: str) -> None:
        """Create a new ``AWS::IoT::ThingPrincipalAttachment``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param principal: ``AWS::IoT::ThingPrincipalAttachment.Principal``.
        :param thing_name: ``AWS::IoT::ThingPrincipalAttachment.ThingName``.
        """
        props = CfnThingPrincipalAttachmentProps(principal=principal, thing_name=thing_name)

        jsii.create(CfnThingPrincipalAttachment, self, [scope, id, props])

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
    @jsii.member(jsii_name="principal")
    def principal(self) -> str:
        """``AWS::IoT::ThingPrincipalAttachment.Principal``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-thingprincipalattachment.html#cfn-iot-thingprincipalattachment-principal
        """
        return jsii.get(self, "principal")

    @principal.setter
    def principal(self, value: str):
        return jsii.set(self, "principal", value)

    @property
    @jsii.member(jsii_name="thingName")
    def thing_name(self) -> str:
        """``AWS::IoT::ThingPrincipalAttachment.ThingName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-thingprincipalattachment.html#cfn-iot-thingprincipalattachment-thingname
        """
        return jsii.get(self, "thingName")

    @thing_name.setter
    def thing_name(self, value: str):
        return jsii.set(self, "thingName", value)


@jsii.data_type(jsii_type="@aws-cdk/aws-iot.CfnThingPrincipalAttachmentProps", jsii_struct_bases=[], name_mapping={'principal': 'principal', 'thing_name': 'thingName'})
class CfnThingPrincipalAttachmentProps():
    def __init__(self, *, principal: str, thing_name: str):
        """Properties for defining a ``AWS::IoT::ThingPrincipalAttachment``.

        :param principal: ``AWS::IoT::ThingPrincipalAttachment.Principal``.
        :param thing_name: ``AWS::IoT::ThingPrincipalAttachment.ThingName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-thingprincipalattachment.html
        """
        self._values = {
            'principal': principal,
            'thing_name': thing_name,
        }

    @property
    def principal(self) -> str:
        """``AWS::IoT::ThingPrincipalAttachment.Principal``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-thingprincipalattachment.html#cfn-iot-thingprincipalattachment-principal
        """
        return self._values.get('principal')

    @property
    def thing_name(self) -> str:
        """``AWS::IoT::ThingPrincipalAttachment.ThingName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-thingprincipalattachment.html#cfn-iot-thingprincipalattachment-thingname
        """
        return self._values.get('thing_name')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnThingPrincipalAttachmentProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


@jsii.data_type(jsii_type="@aws-cdk/aws-iot.CfnThingProps", jsii_struct_bases=[], name_mapping={'attribute_payload': 'attributePayload', 'thing_name': 'thingName'})
class CfnThingProps():
    def __init__(self, *, attribute_payload: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnThing.AttributePayloadProperty"]]]=None, thing_name: typing.Optional[str]=None):
        """Properties for defining a ``AWS::IoT::Thing``.

        :param attribute_payload: ``AWS::IoT::Thing.AttributePayload``.
        :param thing_name: ``AWS::IoT::Thing.ThingName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-thing.html
        """
        self._values = {
        }
        if attribute_payload is not None: self._values["attribute_payload"] = attribute_payload
        if thing_name is not None: self._values["thing_name"] = thing_name

    @property
    def attribute_payload(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnThing.AttributePayloadProperty"]]]:
        """``AWS::IoT::Thing.AttributePayload``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-thing.html#cfn-iot-thing-attributepayload
        """
        return self._values.get('attribute_payload')

    @property
    def thing_name(self) -> typing.Optional[str]:
        """``AWS::IoT::Thing.ThingName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-thing.html#cfn-iot-thing-thingname
        """
        return self._values.get('thing_name')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnThingProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnTopicRule(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-iot.CfnTopicRule"):
    """A CloudFormation ``AWS::IoT::TopicRule``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-topicrule.html
    cloudformationResource:
    :cloudformationResource:: AWS::IoT::TopicRule
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, topic_rule_payload: typing.Union[aws_cdk.core.IResolvable, "TopicRulePayloadProperty"], rule_name: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::IoT::TopicRule``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param topic_rule_payload: ``AWS::IoT::TopicRule.TopicRulePayload``.
        :param rule_name: ``AWS::IoT::TopicRule.RuleName``.
        """
        props = CfnTopicRuleProps(topic_rule_payload=topic_rule_payload, rule_name=rule_name)

        jsii.create(CfnTopicRule, self, [scope, id, props])

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
    @jsii.member(jsii_name="topicRulePayload")
    def topic_rule_payload(self) -> typing.Union[aws_cdk.core.IResolvable, "TopicRulePayloadProperty"]:
        """``AWS::IoT::TopicRule.TopicRulePayload``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-topicrule.html#cfn-iot-topicrule-topicrulepayload
        """
        return jsii.get(self, "topicRulePayload")

    @topic_rule_payload.setter
    def topic_rule_payload(self, value: typing.Union[aws_cdk.core.IResolvable, "TopicRulePayloadProperty"]):
        return jsii.set(self, "topicRulePayload", value)

    @property
    @jsii.member(jsii_name="ruleName")
    def rule_name(self) -> typing.Optional[str]:
        """``AWS::IoT::TopicRule.RuleName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-topicrule.html#cfn-iot-topicrule-rulename
        """
        return jsii.get(self, "ruleName")

    @rule_name.setter
    def rule_name(self, value: typing.Optional[str]):
        return jsii.set(self, "ruleName", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-iot.CfnTopicRule.ActionProperty", jsii_struct_bases=[], name_mapping={'cloudwatch_alarm': 'cloudwatchAlarm', 'cloudwatch_metric': 'cloudwatchMetric', 'dynamo_db': 'dynamoDb', 'dynamo_d_bv2': 'dynamoDBv2', 'elasticsearch': 'elasticsearch', 'firehose': 'firehose', 'iot_analytics': 'iotAnalytics', 'kinesis': 'kinesis', 'lambda_': 'lambda', 'republish': 'republish', 's3': 's3', 'sns': 'sns', 'sqs': 'sqs', 'step_functions': 'stepFunctions'})
    class ActionProperty():
        def __init__(self, *, cloudwatch_alarm: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnTopicRule.CloudwatchAlarmActionProperty"]]]=None, cloudwatch_metric: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnTopicRule.CloudwatchMetricActionProperty"]]]=None, dynamo_db: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnTopicRule.DynamoDBActionProperty"]]]=None, dynamo_d_bv2: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnTopicRule.DynamoDBv2ActionProperty"]]]=None, elasticsearch: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnTopicRule.ElasticsearchActionProperty"]]]=None, firehose: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnTopicRule.FirehoseActionProperty"]]]=None, iot_analytics: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnTopicRule.IotAnalyticsActionProperty"]]]=None, kinesis: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnTopicRule.KinesisActionProperty"]]]=None, lambda_: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnTopicRule.LambdaActionProperty"]]]=None, republish: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnTopicRule.RepublishActionProperty"]]]=None, s3: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnTopicRule.S3ActionProperty"]]]=None, sns: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnTopicRule.SnsActionProperty"]]]=None, sqs: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnTopicRule.SqsActionProperty"]]]=None, step_functions: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnTopicRule.StepFunctionsActionProperty"]]]=None):
            """
            :param cloudwatch_alarm: ``CfnTopicRule.ActionProperty.CloudwatchAlarm``.
            :param cloudwatch_metric: ``CfnTopicRule.ActionProperty.CloudwatchMetric``.
            :param dynamo_db: ``CfnTopicRule.ActionProperty.DynamoDB``.
            :param dynamo_d_bv2: ``CfnTopicRule.ActionProperty.DynamoDBv2``.
            :param elasticsearch: ``CfnTopicRule.ActionProperty.Elasticsearch``.
            :param firehose: ``CfnTopicRule.ActionProperty.Firehose``.
            :param iot_analytics: ``CfnTopicRule.ActionProperty.IotAnalytics``.
            :param kinesis: ``CfnTopicRule.ActionProperty.Kinesis``.
            :param lambda_: ``CfnTopicRule.ActionProperty.Lambda``.
            :param republish: ``CfnTopicRule.ActionProperty.Republish``.
            :param s3: ``CfnTopicRule.ActionProperty.S3``.
            :param sns: ``CfnTopicRule.ActionProperty.Sns``.
            :param sqs: ``CfnTopicRule.ActionProperty.Sqs``.
            :param step_functions: ``CfnTopicRule.ActionProperty.StepFunctions``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-action.html
            """
            self._values = {
            }
            if cloudwatch_alarm is not None: self._values["cloudwatch_alarm"] = cloudwatch_alarm
            if cloudwatch_metric is not None: self._values["cloudwatch_metric"] = cloudwatch_metric
            if dynamo_db is not None: self._values["dynamo_db"] = dynamo_db
            if dynamo_d_bv2 is not None: self._values["dynamo_d_bv2"] = dynamo_d_bv2
            if elasticsearch is not None: self._values["elasticsearch"] = elasticsearch
            if firehose is not None: self._values["firehose"] = firehose
            if iot_analytics is not None: self._values["iot_analytics"] = iot_analytics
            if kinesis is not None: self._values["kinesis"] = kinesis
            if lambda_ is not None: self._values["lambda_"] = lambda_
            if republish is not None: self._values["republish"] = republish
            if s3 is not None: self._values["s3"] = s3
            if sns is not None: self._values["sns"] = sns
            if sqs is not None: self._values["sqs"] = sqs
            if step_functions is not None: self._values["step_functions"] = step_functions

        @property
        def cloudwatch_alarm(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnTopicRule.CloudwatchAlarmActionProperty"]]]:
            """``CfnTopicRule.ActionProperty.CloudwatchAlarm``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-action.html#cfn-iot-topicrule-action-cloudwatchalarm
            """
            return self._values.get('cloudwatch_alarm')

        @property
        def cloudwatch_metric(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnTopicRule.CloudwatchMetricActionProperty"]]]:
            """``CfnTopicRule.ActionProperty.CloudwatchMetric``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-action.html#cfn-iot-topicrule-action-cloudwatchmetric
            """
            return self._values.get('cloudwatch_metric')

        @property
        def dynamo_db(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnTopicRule.DynamoDBActionProperty"]]]:
            """``CfnTopicRule.ActionProperty.DynamoDB``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-action.html#cfn-iot-topicrule-action-dynamodb
            """
            return self._values.get('dynamo_db')

        @property
        def dynamo_d_bv2(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnTopicRule.DynamoDBv2ActionProperty"]]]:
            """``CfnTopicRule.ActionProperty.DynamoDBv2``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-action.html#cfn-iot-topicrule-action-dynamodbv2
            """
            return self._values.get('dynamo_d_bv2')

        @property
        def elasticsearch(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnTopicRule.ElasticsearchActionProperty"]]]:
            """``CfnTopicRule.ActionProperty.Elasticsearch``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-action.html#cfn-iot-topicrule-action-elasticsearch
            """
            return self._values.get('elasticsearch')

        @property
        def firehose(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnTopicRule.FirehoseActionProperty"]]]:
            """``CfnTopicRule.ActionProperty.Firehose``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-action.html#cfn-iot-topicrule-action-firehose
            """
            return self._values.get('firehose')

        @property
        def iot_analytics(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnTopicRule.IotAnalyticsActionProperty"]]]:
            """``CfnTopicRule.ActionProperty.IotAnalytics``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-action.html#cfn-iot-topicrule-action-iotanalytics
            """
            return self._values.get('iot_analytics')

        @property
        def kinesis(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnTopicRule.KinesisActionProperty"]]]:
            """``CfnTopicRule.ActionProperty.Kinesis``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-action.html#cfn-iot-topicrule-action-kinesis
            """
            return self._values.get('kinesis')

        @property
        def lambda_(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnTopicRule.LambdaActionProperty"]]]:
            """``CfnTopicRule.ActionProperty.Lambda``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-action.html#cfn-iot-topicrule-action-lambda
            """
            return self._values.get('lambda_')

        @property
        def republish(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnTopicRule.RepublishActionProperty"]]]:
            """``CfnTopicRule.ActionProperty.Republish``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-action.html#cfn-iot-topicrule-action-republish
            """
            return self._values.get('republish')

        @property
        def s3(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnTopicRule.S3ActionProperty"]]]:
            """``CfnTopicRule.ActionProperty.S3``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-action.html#cfn-iot-topicrule-action-s3
            """
            return self._values.get('s3')

        @property
        def sns(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnTopicRule.SnsActionProperty"]]]:
            """``CfnTopicRule.ActionProperty.Sns``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-action.html#cfn-iot-topicrule-action-sns
            """
            return self._values.get('sns')

        @property
        def sqs(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnTopicRule.SqsActionProperty"]]]:
            """``CfnTopicRule.ActionProperty.Sqs``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-action.html#cfn-iot-topicrule-action-sqs
            """
            return self._values.get('sqs')

        @property
        def step_functions(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnTopicRule.StepFunctionsActionProperty"]]]:
            """``CfnTopicRule.ActionProperty.StepFunctions``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-action.html#cfn-iot-topicrule-action-stepfunctions
            """
            return self._values.get('step_functions')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'ActionProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-iot.CfnTopicRule.CloudwatchAlarmActionProperty", jsii_struct_bases=[], name_mapping={'alarm_name': 'alarmName', 'role_arn': 'roleArn', 'state_reason': 'stateReason', 'state_value': 'stateValue'})
    class CloudwatchAlarmActionProperty():
        def __init__(self, *, alarm_name: str, role_arn: str, state_reason: str, state_value: str):
            """
            :param alarm_name: ``CfnTopicRule.CloudwatchAlarmActionProperty.AlarmName``.
            :param role_arn: ``CfnTopicRule.CloudwatchAlarmActionProperty.RoleArn``.
            :param state_reason: ``CfnTopicRule.CloudwatchAlarmActionProperty.StateReason``.
            :param state_value: ``CfnTopicRule.CloudwatchAlarmActionProperty.StateValue``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-cloudwatchalarmaction.html
            """
            self._values = {
                'alarm_name': alarm_name,
                'role_arn': role_arn,
                'state_reason': state_reason,
                'state_value': state_value,
            }

        @property
        def alarm_name(self) -> str:
            """``CfnTopicRule.CloudwatchAlarmActionProperty.AlarmName``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-cloudwatchalarmaction.html#cfn-iot-topicrule-cloudwatchalarmaction-alarmname
            """
            return self._values.get('alarm_name')

        @property
        def role_arn(self) -> str:
            """``CfnTopicRule.CloudwatchAlarmActionProperty.RoleArn``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-cloudwatchalarmaction.html#cfn-iot-topicrule-cloudwatchalarmaction-rolearn
            """
            return self._values.get('role_arn')

        @property
        def state_reason(self) -> str:
            """``CfnTopicRule.CloudwatchAlarmActionProperty.StateReason``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-cloudwatchalarmaction.html#cfn-iot-topicrule-cloudwatchalarmaction-statereason
            """
            return self._values.get('state_reason')

        @property
        def state_value(self) -> str:
            """``CfnTopicRule.CloudwatchAlarmActionProperty.StateValue``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-cloudwatchalarmaction.html#cfn-iot-topicrule-cloudwatchalarmaction-statevalue
            """
            return self._values.get('state_value')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'CloudwatchAlarmActionProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-iot.CfnTopicRule.CloudwatchMetricActionProperty", jsii_struct_bases=[], name_mapping={'metric_name': 'metricName', 'metric_namespace': 'metricNamespace', 'metric_unit': 'metricUnit', 'metric_value': 'metricValue', 'role_arn': 'roleArn', 'metric_timestamp': 'metricTimestamp'})
    class CloudwatchMetricActionProperty():
        def __init__(self, *, metric_name: str, metric_namespace: str, metric_unit: str, metric_value: str, role_arn: str, metric_timestamp: typing.Optional[str]=None):
            """
            :param metric_name: ``CfnTopicRule.CloudwatchMetricActionProperty.MetricName``.
            :param metric_namespace: ``CfnTopicRule.CloudwatchMetricActionProperty.MetricNamespace``.
            :param metric_unit: ``CfnTopicRule.CloudwatchMetricActionProperty.MetricUnit``.
            :param metric_value: ``CfnTopicRule.CloudwatchMetricActionProperty.MetricValue``.
            :param role_arn: ``CfnTopicRule.CloudwatchMetricActionProperty.RoleArn``.
            :param metric_timestamp: ``CfnTopicRule.CloudwatchMetricActionProperty.MetricTimestamp``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-cloudwatchmetricaction.html
            """
            self._values = {
                'metric_name': metric_name,
                'metric_namespace': metric_namespace,
                'metric_unit': metric_unit,
                'metric_value': metric_value,
                'role_arn': role_arn,
            }
            if metric_timestamp is not None: self._values["metric_timestamp"] = metric_timestamp

        @property
        def metric_name(self) -> str:
            """``CfnTopicRule.CloudwatchMetricActionProperty.MetricName``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-cloudwatchmetricaction.html#cfn-iot-topicrule-cloudwatchmetricaction-metricname
            """
            return self._values.get('metric_name')

        @property
        def metric_namespace(self) -> str:
            """``CfnTopicRule.CloudwatchMetricActionProperty.MetricNamespace``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-cloudwatchmetricaction.html#cfn-iot-topicrule-cloudwatchmetricaction-metricnamespace
            """
            return self._values.get('metric_namespace')

        @property
        def metric_unit(self) -> str:
            """``CfnTopicRule.CloudwatchMetricActionProperty.MetricUnit``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-cloudwatchmetricaction.html#cfn-iot-topicrule-cloudwatchmetricaction-metricunit
            """
            return self._values.get('metric_unit')

        @property
        def metric_value(self) -> str:
            """``CfnTopicRule.CloudwatchMetricActionProperty.MetricValue``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-cloudwatchmetricaction.html#cfn-iot-topicrule-cloudwatchmetricaction-metricvalue
            """
            return self._values.get('metric_value')

        @property
        def role_arn(self) -> str:
            """``CfnTopicRule.CloudwatchMetricActionProperty.RoleArn``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-cloudwatchmetricaction.html#cfn-iot-topicrule-cloudwatchmetricaction-rolearn
            """
            return self._values.get('role_arn')

        @property
        def metric_timestamp(self) -> typing.Optional[str]:
            """``CfnTopicRule.CloudwatchMetricActionProperty.MetricTimestamp``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-cloudwatchmetricaction.html#cfn-iot-topicrule-cloudwatchmetricaction-metrictimestamp
            """
            return self._values.get('metric_timestamp')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'CloudwatchMetricActionProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-iot.CfnTopicRule.DynamoDBActionProperty", jsii_struct_bases=[], name_mapping={'hash_key_field': 'hashKeyField', 'hash_key_value': 'hashKeyValue', 'role_arn': 'roleArn', 'table_name': 'tableName', 'hash_key_type': 'hashKeyType', 'payload_field': 'payloadField', 'range_key_field': 'rangeKeyField', 'range_key_type': 'rangeKeyType', 'range_key_value': 'rangeKeyValue'})
    class DynamoDBActionProperty():
        def __init__(self, *, hash_key_field: str, hash_key_value: str, role_arn: str, table_name: str, hash_key_type: typing.Optional[str]=None, payload_field: typing.Optional[str]=None, range_key_field: typing.Optional[str]=None, range_key_type: typing.Optional[str]=None, range_key_value: typing.Optional[str]=None):
            """
            :param hash_key_field: ``CfnTopicRule.DynamoDBActionProperty.HashKeyField``.
            :param hash_key_value: ``CfnTopicRule.DynamoDBActionProperty.HashKeyValue``.
            :param role_arn: ``CfnTopicRule.DynamoDBActionProperty.RoleArn``.
            :param table_name: ``CfnTopicRule.DynamoDBActionProperty.TableName``.
            :param hash_key_type: ``CfnTopicRule.DynamoDBActionProperty.HashKeyType``.
            :param payload_field: ``CfnTopicRule.DynamoDBActionProperty.PayloadField``.
            :param range_key_field: ``CfnTopicRule.DynamoDBActionProperty.RangeKeyField``.
            :param range_key_type: ``CfnTopicRule.DynamoDBActionProperty.RangeKeyType``.
            :param range_key_value: ``CfnTopicRule.DynamoDBActionProperty.RangeKeyValue``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-dynamodbaction.html
            """
            self._values = {
                'hash_key_field': hash_key_field,
                'hash_key_value': hash_key_value,
                'role_arn': role_arn,
                'table_name': table_name,
            }
            if hash_key_type is not None: self._values["hash_key_type"] = hash_key_type
            if payload_field is not None: self._values["payload_field"] = payload_field
            if range_key_field is not None: self._values["range_key_field"] = range_key_field
            if range_key_type is not None: self._values["range_key_type"] = range_key_type
            if range_key_value is not None: self._values["range_key_value"] = range_key_value

        @property
        def hash_key_field(self) -> str:
            """``CfnTopicRule.DynamoDBActionProperty.HashKeyField``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-dynamodbaction.html#cfn-iot-topicrule-dynamodbaction-hashkeyfield
            """
            return self._values.get('hash_key_field')

        @property
        def hash_key_value(self) -> str:
            """``CfnTopicRule.DynamoDBActionProperty.HashKeyValue``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-dynamodbaction.html#cfn-iot-topicrule-dynamodbaction-hashkeyvalue
            """
            return self._values.get('hash_key_value')

        @property
        def role_arn(self) -> str:
            """``CfnTopicRule.DynamoDBActionProperty.RoleArn``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-dynamodbaction.html#cfn-iot-topicrule-dynamodbaction-rolearn
            """
            return self._values.get('role_arn')

        @property
        def table_name(self) -> str:
            """``CfnTopicRule.DynamoDBActionProperty.TableName``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-dynamodbaction.html#cfn-iot-topicrule-dynamodbaction-tablename
            """
            return self._values.get('table_name')

        @property
        def hash_key_type(self) -> typing.Optional[str]:
            """``CfnTopicRule.DynamoDBActionProperty.HashKeyType``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-dynamodbaction.html#cfn-iot-topicrule-dynamodbaction-hashkeytype
            """
            return self._values.get('hash_key_type')

        @property
        def payload_field(self) -> typing.Optional[str]:
            """``CfnTopicRule.DynamoDBActionProperty.PayloadField``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-dynamodbaction.html#cfn-iot-topicrule-dynamodbaction-payloadfield
            """
            return self._values.get('payload_field')

        @property
        def range_key_field(self) -> typing.Optional[str]:
            """``CfnTopicRule.DynamoDBActionProperty.RangeKeyField``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-dynamodbaction.html#cfn-iot-topicrule-dynamodbaction-rangekeyfield
            """
            return self._values.get('range_key_field')

        @property
        def range_key_type(self) -> typing.Optional[str]:
            """``CfnTopicRule.DynamoDBActionProperty.RangeKeyType``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-dynamodbaction.html#cfn-iot-topicrule-dynamodbaction-rangekeytype
            """
            return self._values.get('range_key_type')

        @property
        def range_key_value(self) -> typing.Optional[str]:
            """``CfnTopicRule.DynamoDBActionProperty.RangeKeyValue``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-dynamodbaction.html#cfn-iot-topicrule-dynamodbaction-rangekeyvalue
            """
            return self._values.get('range_key_value')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'DynamoDBActionProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-iot.CfnTopicRule.DynamoDBv2ActionProperty", jsii_struct_bases=[], name_mapping={'put_item': 'putItem', 'role_arn': 'roleArn'})
    class DynamoDBv2ActionProperty():
        def __init__(self, *, put_item: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnTopicRule.PutItemInputProperty"]]]=None, role_arn: typing.Optional[str]=None):
            """
            :param put_item: ``CfnTopicRule.DynamoDBv2ActionProperty.PutItem``.
            :param role_arn: ``CfnTopicRule.DynamoDBv2ActionProperty.RoleArn``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-dynamodbv2action.html
            """
            self._values = {
            }
            if put_item is not None: self._values["put_item"] = put_item
            if role_arn is not None: self._values["role_arn"] = role_arn

        @property
        def put_item(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnTopicRule.PutItemInputProperty"]]]:
            """``CfnTopicRule.DynamoDBv2ActionProperty.PutItem``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-dynamodbv2action.html#cfn-iot-topicrule-dynamodbv2action-putitem
            """
            return self._values.get('put_item')

        @property
        def role_arn(self) -> typing.Optional[str]:
            """``CfnTopicRule.DynamoDBv2ActionProperty.RoleArn``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-dynamodbv2action.html#cfn-iot-topicrule-dynamodbv2action-rolearn
            """
            return self._values.get('role_arn')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'DynamoDBv2ActionProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-iot.CfnTopicRule.ElasticsearchActionProperty", jsii_struct_bases=[], name_mapping={'endpoint': 'endpoint', 'id': 'id', 'index': 'index', 'role_arn': 'roleArn', 'type': 'type'})
    class ElasticsearchActionProperty():
        def __init__(self, *, endpoint: str, id: str, index: str, role_arn: str, type: str):
            """
            :param endpoint: ``CfnTopicRule.ElasticsearchActionProperty.Endpoint``.
            :param id: ``CfnTopicRule.ElasticsearchActionProperty.Id``.
            :param index: ``CfnTopicRule.ElasticsearchActionProperty.Index``.
            :param role_arn: ``CfnTopicRule.ElasticsearchActionProperty.RoleArn``.
            :param type: ``CfnTopicRule.ElasticsearchActionProperty.Type``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-elasticsearchaction.html
            """
            self._values = {
                'endpoint': endpoint,
                'id': id,
                'index': index,
                'role_arn': role_arn,
                'type': type,
            }

        @property
        def endpoint(self) -> str:
            """``CfnTopicRule.ElasticsearchActionProperty.Endpoint``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-elasticsearchaction.html#cfn-iot-topicrule-elasticsearchaction-endpoint
            """
            return self._values.get('endpoint')

        @property
        def id(self) -> str:
            """``CfnTopicRule.ElasticsearchActionProperty.Id``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-elasticsearchaction.html#cfn-iot-topicrule-elasticsearchaction-id
            """
            return self._values.get('id')

        @property
        def index(self) -> str:
            """``CfnTopicRule.ElasticsearchActionProperty.Index``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-elasticsearchaction.html#cfn-iot-topicrule-elasticsearchaction-index
            """
            return self._values.get('index')

        @property
        def role_arn(self) -> str:
            """``CfnTopicRule.ElasticsearchActionProperty.RoleArn``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-elasticsearchaction.html#cfn-iot-topicrule-elasticsearchaction-rolearn
            """
            return self._values.get('role_arn')

        @property
        def type(self) -> str:
            """``CfnTopicRule.ElasticsearchActionProperty.Type``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-elasticsearchaction.html#cfn-iot-topicrule-elasticsearchaction-type
            """
            return self._values.get('type')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'ElasticsearchActionProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-iot.CfnTopicRule.FirehoseActionProperty", jsii_struct_bases=[], name_mapping={'delivery_stream_name': 'deliveryStreamName', 'role_arn': 'roleArn', 'separator': 'separator'})
    class FirehoseActionProperty():
        def __init__(self, *, delivery_stream_name: str, role_arn: str, separator: typing.Optional[str]=None):
            """
            :param delivery_stream_name: ``CfnTopicRule.FirehoseActionProperty.DeliveryStreamName``.
            :param role_arn: ``CfnTopicRule.FirehoseActionProperty.RoleArn``.
            :param separator: ``CfnTopicRule.FirehoseActionProperty.Separator``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-firehoseaction.html
            """
            self._values = {
                'delivery_stream_name': delivery_stream_name,
                'role_arn': role_arn,
            }
            if separator is not None: self._values["separator"] = separator

        @property
        def delivery_stream_name(self) -> str:
            """``CfnTopicRule.FirehoseActionProperty.DeliveryStreamName``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-firehoseaction.html#cfn-iot-topicrule-firehoseaction-deliverystreamname
            """
            return self._values.get('delivery_stream_name')

        @property
        def role_arn(self) -> str:
            """``CfnTopicRule.FirehoseActionProperty.RoleArn``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-firehoseaction.html#cfn-iot-topicrule-firehoseaction-rolearn
            """
            return self._values.get('role_arn')

        @property
        def separator(self) -> typing.Optional[str]:
            """``CfnTopicRule.FirehoseActionProperty.Separator``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-firehoseaction.html#cfn-iot-topicrule-firehoseaction-separator
            """
            return self._values.get('separator')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'FirehoseActionProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-iot.CfnTopicRule.IotAnalyticsActionProperty", jsii_struct_bases=[], name_mapping={'channel_name': 'channelName', 'role_arn': 'roleArn'})
    class IotAnalyticsActionProperty():
        def __init__(self, *, channel_name: str, role_arn: str):
            """
            :param channel_name: ``CfnTopicRule.IotAnalyticsActionProperty.ChannelName``.
            :param role_arn: ``CfnTopicRule.IotAnalyticsActionProperty.RoleArn``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-iotanalyticsaction.html
            """
            self._values = {
                'channel_name': channel_name,
                'role_arn': role_arn,
            }

        @property
        def channel_name(self) -> str:
            """``CfnTopicRule.IotAnalyticsActionProperty.ChannelName``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-iotanalyticsaction.html#cfn-iot-topicrule-iotanalyticsaction-channelname
            """
            return self._values.get('channel_name')

        @property
        def role_arn(self) -> str:
            """``CfnTopicRule.IotAnalyticsActionProperty.RoleArn``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-iotanalyticsaction.html#cfn-iot-topicrule-iotanalyticsaction-rolearn
            """
            return self._values.get('role_arn')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'IotAnalyticsActionProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-iot.CfnTopicRule.KinesisActionProperty", jsii_struct_bases=[], name_mapping={'role_arn': 'roleArn', 'stream_name': 'streamName', 'partition_key': 'partitionKey'})
    class KinesisActionProperty():
        def __init__(self, *, role_arn: str, stream_name: str, partition_key: typing.Optional[str]=None):
            """
            :param role_arn: ``CfnTopicRule.KinesisActionProperty.RoleArn``.
            :param stream_name: ``CfnTopicRule.KinesisActionProperty.StreamName``.
            :param partition_key: ``CfnTopicRule.KinesisActionProperty.PartitionKey``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-kinesisaction.html
            """
            self._values = {
                'role_arn': role_arn,
                'stream_name': stream_name,
            }
            if partition_key is not None: self._values["partition_key"] = partition_key

        @property
        def role_arn(self) -> str:
            """``CfnTopicRule.KinesisActionProperty.RoleArn``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-kinesisaction.html#cfn-iot-topicrule-kinesisaction-rolearn
            """
            return self._values.get('role_arn')

        @property
        def stream_name(self) -> str:
            """``CfnTopicRule.KinesisActionProperty.StreamName``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-kinesisaction.html#cfn-iot-topicrule-kinesisaction-streamname
            """
            return self._values.get('stream_name')

        @property
        def partition_key(self) -> typing.Optional[str]:
            """``CfnTopicRule.KinesisActionProperty.PartitionKey``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-kinesisaction.html#cfn-iot-topicrule-kinesisaction-partitionkey
            """
            return self._values.get('partition_key')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'KinesisActionProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-iot.CfnTopicRule.LambdaActionProperty", jsii_struct_bases=[], name_mapping={'function_arn': 'functionArn'})
    class LambdaActionProperty():
        def __init__(self, *, function_arn: typing.Optional[str]=None):
            """
            :param function_arn: ``CfnTopicRule.LambdaActionProperty.FunctionArn``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-lambdaaction.html
            """
            self._values = {
            }
            if function_arn is not None: self._values["function_arn"] = function_arn

        @property
        def function_arn(self) -> typing.Optional[str]:
            """``CfnTopicRule.LambdaActionProperty.FunctionArn``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-lambdaaction.html#cfn-iot-topicrule-lambdaaction-functionarn
            """
            return self._values.get('function_arn')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'LambdaActionProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-iot.CfnTopicRule.PutItemInputProperty", jsii_struct_bases=[], name_mapping={'table_name': 'tableName'})
    class PutItemInputProperty():
        def __init__(self, *, table_name: str):
            """
            :param table_name: ``CfnTopicRule.PutItemInputProperty.TableName``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-putiteminput.html
            """
            self._values = {
                'table_name': table_name,
            }

        @property
        def table_name(self) -> str:
            """``CfnTopicRule.PutItemInputProperty.TableName``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-putiteminput.html#cfn-iot-topicrule-putiteminput-tablename
            """
            return self._values.get('table_name')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'PutItemInputProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-iot.CfnTopicRule.RepublishActionProperty", jsii_struct_bases=[], name_mapping={'role_arn': 'roleArn', 'topic': 'topic'})
    class RepublishActionProperty():
        def __init__(self, *, role_arn: str, topic: str):
            """
            :param role_arn: ``CfnTopicRule.RepublishActionProperty.RoleArn``.
            :param topic: ``CfnTopicRule.RepublishActionProperty.Topic``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-republishaction.html
            """
            self._values = {
                'role_arn': role_arn,
                'topic': topic,
            }

        @property
        def role_arn(self) -> str:
            """``CfnTopicRule.RepublishActionProperty.RoleArn``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-republishaction.html#cfn-iot-topicrule-republishaction-rolearn
            """
            return self._values.get('role_arn')

        @property
        def topic(self) -> str:
            """``CfnTopicRule.RepublishActionProperty.Topic``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-republishaction.html#cfn-iot-topicrule-republishaction-topic
            """
            return self._values.get('topic')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'RepublishActionProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-iot.CfnTopicRule.S3ActionProperty", jsii_struct_bases=[], name_mapping={'bucket_name': 'bucketName', 'key': 'key', 'role_arn': 'roleArn'})
    class S3ActionProperty():
        def __init__(self, *, bucket_name: str, key: str, role_arn: str):
            """
            :param bucket_name: ``CfnTopicRule.S3ActionProperty.BucketName``.
            :param key: ``CfnTopicRule.S3ActionProperty.Key``.
            :param role_arn: ``CfnTopicRule.S3ActionProperty.RoleArn``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-s3action.html
            """
            self._values = {
                'bucket_name': bucket_name,
                'key': key,
                'role_arn': role_arn,
            }

        @property
        def bucket_name(self) -> str:
            """``CfnTopicRule.S3ActionProperty.BucketName``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-s3action.html#cfn-iot-topicrule-s3action-bucketname
            """
            return self._values.get('bucket_name')

        @property
        def key(self) -> str:
            """``CfnTopicRule.S3ActionProperty.Key``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-s3action.html#cfn-iot-topicrule-s3action-key
            """
            return self._values.get('key')

        @property
        def role_arn(self) -> str:
            """``CfnTopicRule.S3ActionProperty.RoleArn``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-s3action.html#cfn-iot-topicrule-s3action-rolearn
            """
            return self._values.get('role_arn')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'S3ActionProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-iot.CfnTopicRule.SnsActionProperty", jsii_struct_bases=[], name_mapping={'role_arn': 'roleArn', 'target_arn': 'targetArn', 'message_format': 'messageFormat'})
    class SnsActionProperty():
        def __init__(self, *, role_arn: str, target_arn: str, message_format: typing.Optional[str]=None):
            """
            :param role_arn: ``CfnTopicRule.SnsActionProperty.RoleArn``.
            :param target_arn: ``CfnTopicRule.SnsActionProperty.TargetArn``.
            :param message_format: ``CfnTopicRule.SnsActionProperty.MessageFormat``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-snsaction.html
            """
            self._values = {
                'role_arn': role_arn,
                'target_arn': target_arn,
            }
            if message_format is not None: self._values["message_format"] = message_format

        @property
        def role_arn(self) -> str:
            """``CfnTopicRule.SnsActionProperty.RoleArn``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-snsaction.html#cfn-iot-topicrule-snsaction-rolearn
            """
            return self._values.get('role_arn')

        @property
        def target_arn(self) -> str:
            """``CfnTopicRule.SnsActionProperty.TargetArn``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-snsaction.html#cfn-iot-topicrule-snsaction-targetarn
            """
            return self._values.get('target_arn')

        @property
        def message_format(self) -> typing.Optional[str]:
            """``CfnTopicRule.SnsActionProperty.MessageFormat``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-snsaction.html#cfn-iot-topicrule-snsaction-messageformat
            """
            return self._values.get('message_format')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'SnsActionProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-iot.CfnTopicRule.SqsActionProperty", jsii_struct_bases=[], name_mapping={'queue_url': 'queueUrl', 'role_arn': 'roleArn', 'use_base64': 'useBase64'})
    class SqsActionProperty():
        def __init__(self, *, queue_url: str, role_arn: str, use_base64: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None):
            """
            :param queue_url: ``CfnTopicRule.SqsActionProperty.QueueUrl``.
            :param role_arn: ``CfnTopicRule.SqsActionProperty.RoleArn``.
            :param use_base64: ``CfnTopicRule.SqsActionProperty.UseBase64``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-sqsaction.html
            """
            self._values = {
                'queue_url': queue_url,
                'role_arn': role_arn,
            }
            if use_base64 is not None: self._values["use_base64"] = use_base64

        @property
        def queue_url(self) -> str:
            """``CfnTopicRule.SqsActionProperty.QueueUrl``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-sqsaction.html#cfn-iot-topicrule-sqsaction-queueurl
            """
            return self._values.get('queue_url')

        @property
        def role_arn(self) -> str:
            """``CfnTopicRule.SqsActionProperty.RoleArn``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-sqsaction.html#cfn-iot-topicrule-sqsaction-rolearn
            """
            return self._values.get('role_arn')

        @property
        def use_base64(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
            """``CfnTopicRule.SqsActionProperty.UseBase64``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-sqsaction.html#cfn-iot-topicrule-sqsaction-usebase64
            """
            return self._values.get('use_base64')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'SqsActionProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-iot.CfnTopicRule.StepFunctionsActionProperty", jsii_struct_bases=[], name_mapping={'role_arn': 'roleArn', 'state_machine_name': 'stateMachineName', 'execution_name_prefix': 'executionNamePrefix'})
    class StepFunctionsActionProperty():
        def __init__(self, *, role_arn: str, state_machine_name: str, execution_name_prefix: typing.Optional[str]=None):
            """
            :param role_arn: ``CfnTopicRule.StepFunctionsActionProperty.RoleArn``.
            :param state_machine_name: ``CfnTopicRule.StepFunctionsActionProperty.StateMachineName``.
            :param execution_name_prefix: ``CfnTopicRule.StepFunctionsActionProperty.ExecutionNamePrefix``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-stepfunctionsaction.html
            """
            self._values = {
                'role_arn': role_arn,
                'state_machine_name': state_machine_name,
            }
            if execution_name_prefix is not None: self._values["execution_name_prefix"] = execution_name_prefix

        @property
        def role_arn(self) -> str:
            """``CfnTopicRule.StepFunctionsActionProperty.RoleArn``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-stepfunctionsaction.html#cfn-iot-topicrule-stepfunctionsaction-rolearn
            """
            return self._values.get('role_arn')

        @property
        def state_machine_name(self) -> str:
            """``CfnTopicRule.StepFunctionsActionProperty.StateMachineName``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-stepfunctionsaction.html#cfn-iot-topicrule-stepfunctionsaction-statemachinename
            """
            return self._values.get('state_machine_name')

        @property
        def execution_name_prefix(self) -> typing.Optional[str]:
            """``CfnTopicRule.StepFunctionsActionProperty.ExecutionNamePrefix``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-stepfunctionsaction.html#cfn-iot-topicrule-stepfunctionsaction-executionnameprefix
            """
            return self._values.get('execution_name_prefix')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'StepFunctionsActionProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-iot.CfnTopicRule.TopicRulePayloadProperty", jsii_struct_bases=[], name_mapping={'actions': 'actions', 'rule_disabled': 'ruleDisabled', 'sql': 'sql', 'aws_iot_sql_version': 'awsIotSqlVersion', 'description': 'description', 'error_action': 'errorAction'})
    class TopicRulePayloadProperty():
        def __init__(self, *, actions: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnTopicRule.ActionProperty"]]], rule_disabled: typing.Union[bool, aws_cdk.core.IResolvable], sql: str, aws_iot_sql_version: typing.Optional[str]=None, description: typing.Optional[str]=None, error_action: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnTopicRule.ActionProperty"]]]=None):
            """
            :param actions: ``CfnTopicRule.TopicRulePayloadProperty.Actions``.
            :param rule_disabled: ``CfnTopicRule.TopicRulePayloadProperty.RuleDisabled``.
            :param sql: ``CfnTopicRule.TopicRulePayloadProperty.Sql``.
            :param aws_iot_sql_version: ``CfnTopicRule.TopicRulePayloadProperty.AwsIotSqlVersion``.
            :param description: ``CfnTopicRule.TopicRulePayloadProperty.Description``.
            :param error_action: ``CfnTopicRule.TopicRulePayloadProperty.ErrorAction``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-topicrulepayload.html
            """
            self._values = {
                'actions': actions,
                'rule_disabled': rule_disabled,
                'sql': sql,
            }
            if aws_iot_sql_version is not None: self._values["aws_iot_sql_version"] = aws_iot_sql_version
            if description is not None: self._values["description"] = description
            if error_action is not None: self._values["error_action"] = error_action

        @property
        def actions(self) -> typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnTopicRule.ActionProperty"]]]:
            """``CfnTopicRule.TopicRulePayloadProperty.Actions``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-topicrulepayload.html#cfn-iot-topicrule-topicrulepayload-actions
            """
            return self._values.get('actions')

        @property
        def rule_disabled(self) -> typing.Union[bool, aws_cdk.core.IResolvable]:
            """``CfnTopicRule.TopicRulePayloadProperty.RuleDisabled``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-topicrulepayload.html#cfn-iot-topicrule-topicrulepayload-ruledisabled
            """
            return self._values.get('rule_disabled')

        @property
        def sql(self) -> str:
            """``CfnTopicRule.TopicRulePayloadProperty.Sql``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-topicrulepayload.html#cfn-iot-topicrule-topicrulepayload-sql
            """
            return self._values.get('sql')

        @property
        def aws_iot_sql_version(self) -> typing.Optional[str]:
            """``CfnTopicRule.TopicRulePayloadProperty.AwsIotSqlVersion``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-topicrulepayload.html#cfn-iot-topicrule-topicrulepayload-awsiotsqlversion
            """
            return self._values.get('aws_iot_sql_version')

        @property
        def description(self) -> typing.Optional[str]:
            """``CfnTopicRule.TopicRulePayloadProperty.Description``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-topicrulepayload.html#cfn-iot-topicrule-topicrulepayload-description
            """
            return self._values.get('description')

        @property
        def error_action(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnTopicRule.ActionProperty"]]]:
            """``CfnTopicRule.TopicRulePayloadProperty.ErrorAction``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-topicrulepayload.html#cfn-iot-topicrule-topicrulepayload-erroraction
            """
            return self._values.get('error_action')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'TopicRulePayloadProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



@jsii.data_type(jsii_type="@aws-cdk/aws-iot.CfnTopicRuleProps", jsii_struct_bases=[], name_mapping={'topic_rule_payload': 'topicRulePayload', 'rule_name': 'ruleName'})
class CfnTopicRuleProps():
    def __init__(self, *, topic_rule_payload: typing.Union[aws_cdk.core.IResolvable, "CfnTopicRule.TopicRulePayloadProperty"], rule_name: typing.Optional[str]=None):
        """Properties for defining a ``AWS::IoT::TopicRule``.

        :param topic_rule_payload: ``AWS::IoT::TopicRule.TopicRulePayload``.
        :param rule_name: ``AWS::IoT::TopicRule.RuleName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-topicrule.html
        """
        self._values = {
            'topic_rule_payload': topic_rule_payload,
        }
        if rule_name is not None: self._values["rule_name"] = rule_name

    @property
    def topic_rule_payload(self) -> typing.Union[aws_cdk.core.IResolvable, "CfnTopicRule.TopicRulePayloadProperty"]:
        """``AWS::IoT::TopicRule.TopicRulePayload``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-topicrule.html#cfn-iot-topicrule-topicrulepayload
        """
        return self._values.get('topic_rule_payload')

    @property
    def rule_name(self) -> typing.Optional[str]:
        """``AWS::IoT::TopicRule.RuleName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-topicrule.html#cfn-iot-topicrule-rulename
        """
        return self._values.get('rule_name')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnTopicRuleProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


__all__ = ["CfnCertificate", "CfnCertificateProps", "CfnPolicy", "CfnPolicyPrincipalAttachment", "CfnPolicyPrincipalAttachmentProps", "CfnPolicyProps", "CfnThing", "CfnThingPrincipalAttachment", "CfnThingPrincipalAttachmentProps", "CfnThingProps", "CfnTopicRule", "CfnTopicRuleProps", "__jsii_assembly__"]

publication.publish()
