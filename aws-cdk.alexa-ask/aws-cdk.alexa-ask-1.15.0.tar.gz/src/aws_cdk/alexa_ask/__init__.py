import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.core
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/alexa-ask", "1.15.0", __name__, "alexa-ask@1.15.0.jsii.tgz")
class CfnSkill(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/alexa-ask.CfnSkill"):
    """A CloudFormation ``Alexa::ASK::Skill``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ask-skill.html
    cloudformationResource:
    :cloudformationResource:: Alexa::ASK::Skill
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, authentication_configuration: typing.Union["AuthenticationConfigurationProperty", aws_cdk.core.IResolvable], skill_package: typing.Union[aws_cdk.core.IResolvable, "SkillPackageProperty"], vendor_id: str) -> None:
        """Create a new ``Alexa::ASK::Skill``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param authentication_configuration: ``Alexa::ASK::Skill.AuthenticationConfiguration``.
        :param skill_package: ``Alexa::ASK::Skill.SkillPackage``.
        :param vendor_id: ``Alexa::ASK::Skill.VendorId``.
        """
        props = CfnSkillProps(authentication_configuration=authentication_configuration, skill_package=skill_package, vendor_id=vendor_id)

        jsii.create(CfnSkill, self, [scope, id, props])

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
    @jsii.member(jsii_name="authenticationConfiguration")
    def authentication_configuration(self) -> typing.Union["AuthenticationConfigurationProperty", aws_cdk.core.IResolvable]:
        """``Alexa::ASK::Skill.AuthenticationConfiguration``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ask-skill.html#cfn-ask-skill-authenticationconfiguration
        """
        return jsii.get(self, "authenticationConfiguration")

    @authentication_configuration.setter
    def authentication_configuration(self, value: typing.Union["AuthenticationConfigurationProperty", aws_cdk.core.IResolvable]):
        return jsii.set(self, "authenticationConfiguration", value)

    @property
    @jsii.member(jsii_name="skillPackage")
    def skill_package(self) -> typing.Union[aws_cdk.core.IResolvable, "SkillPackageProperty"]:
        """``Alexa::ASK::Skill.SkillPackage``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ask-skill.html#cfn-ask-skill-skillpackage
        """
        return jsii.get(self, "skillPackage")

    @skill_package.setter
    def skill_package(self, value: typing.Union[aws_cdk.core.IResolvable, "SkillPackageProperty"]):
        return jsii.set(self, "skillPackage", value)

    @property
    @jsii.member(jsii_name="vendorId")
    def vendor_id(self) -> str:
        """``Alexa::ASK::Skill.VendorId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ask-skill.html#cfn-ask-skill-vendorid
        """
        return jsii.get(self, "vendorId")

    @vendor_id.setter
    def vendor_id(self, value: str):
        return jsii.set(self, "vendorId", value)

    @jsii.data_type(jsii_type="@aws-cdk/alexa-ask.CfnSkill.AuthenticationConfigurationProperty", jsii_struct_bases=[], name_mapping={'client_id': 'clientId', 'client_secret': 'clientSecret', 'refresh_token': 'refreshToken'})
    class AuthenticationConfigurationProperty():
        def __init__(self, *, client_id: str, client_secret: str, refresh_token: str):
            """
            :param client_id: ``CfnSkill.AuthenticationConfigurationProperty.ClientId``.
            :param client_secret: ``CfnSkill.AuthenticationConfigurationProperty.ClientSecret``.
            :param refresh_token: ``CfnSkill.AuthenticationConfigurationProperty.RefreshToken``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ask-skill-authenticationconfiguration.html
            """
            self._values = {
                'client_id': client_id,
                'client_secret': client_secret,
                'refresh_token': refresh_token,
            }

        @property
        def client_id(self) -> str:
            """``CfnSkill.AuthenticationConfigurationProperty.ClientId``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ask-skill-authenticationconfiguration.html#cfn-ask-skill-authenticationconfiguration-clientid
            """
            return self._values.get('client_id')

        @property
        def client_secret(self) -> str:
            """``CfnSkill.AuthenticationConfigurationProperty.ClientSecret``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ask-skill-authenticationconfiguration.html#cfn-ask-skill-authenticationconfiguration-clientsecret
            """
            return self._values.get('client_secret')

        @property
        def refresh_token(self) -> str:
            """``CfnSkill.AuthenticationConfigurationProperty.RefreshToken``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ask-skill-authenticationconfiguration.html#cfn-ask-skill-authenticationconfiguration-refreshtoken
            """
            return self._values.get('refresh_token')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'AuthenticationConfigurationProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/alexa-ask.CfnSkill.OverridesProperty", jsii_struct_bases=[], name_mapping={'manifest': 'manifest'})
    class OverridesProperty():
        def __init__(self, *, manifest: typing.Any=None):
            """
            :param manifest: ``CfnSkill.OverridesProperty.Manifest``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ask-skill-overrides.html
            """
            self._values = {
            }
            if manifest is not None: self._values["manifest"] = manifest

        @property
        def manifest(self) -> typing.Any:
            """``CfnSkill.OverridesProperty.Manifest``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ask-skill-overrides.html#cfn-ask-skill-overrides-manifest
            """
            return self._values.get('manifest')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'OverridesProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/alexa-ask.CfnSkill.SkillPackageProperty", jsii_struct_bases=[], name_mapping={'s3_bucket': 's3Bucket', 's3_key': 's3Key', 'overrides': 'overrides', 's3_bucket_role': 's3BucketRole', 's3_object_version': 's3ObjectVersion'})
    class SkillPackageProperty():
        def __init__(self, *, s3_bucket: str, s3_key: str, overrides: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnSkill.OverridesProperty"]]]=None, s3_bucket_role: typing.Optional[str]=None, s3_object_version: typing.Optional[str]=None):
            """
            :param s3_bucket: ``CfnSkill.SkillPackageProperty.S3Bucket``.
            :param s3_key: ``CfnSkill.SkillPackageProperty.S3Key``.
            :param overrides: ``CfnSkill.SkillPackageProperty.Overrides``.
            :param s3_bucket_role: ``CfnSkill.SkillPackageProperty.S3BucketRole``.
            :param s3_object_version: ``CfnSkill.SkillPackageProperty.S3ObjectVersion``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ask-skill-skillpackage.html
            """
            self._values = {
                's3_bucket': s3_bucket,
                's3_key': s3_key,
            }
            if overrides is not None: self._values["overrides"] = overrides
            if s3_bucket_role is not None: self._values["s3_bucket_role"] = s3_bucket_role
            if s3_object_version is not None: self._values["s3_object_version"] = s3_object_version

        @property
        def s3_bucket(self) -> str:
            """``CfnSkill.SkillPackageProperty.S3Bucket``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ask-skill-skillpackage.html#cfn-ask-skill-skillpackage-s3bucket
            """
            return self._values.get('s3_bucket')

        @property
        def s3_key(self) -> str:
            """``CfnSkill.SkillPackageProperty.S3Key``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ask-skill-skillpackage.html#cfn-ask-skill-skillpackage-s3key
            """
            return self._values.get('s3_key')

        @property
        def overrides(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnSkill.OverridesProperty"]]]:
            """``CfnSkill.SkillPackageProperty.Overrides``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ask-skill-skillpackage.html#cfn-ask-skill-skillpackage-overrides
            """
            return self._values.get('overrides')

        @property
        def s3_bucket_role(self) -> typing.Optional[str]:
            """``CfnSkill.SkillPackageProperty.S3BucketRole``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ask-skill-skillpackage.html#cfn-ask-skill-skillpackage-s3bucketrole
            """
            return self._values.get('s3_bucket_role')

        @property
        def s3_object_version(self) -> typing.Optional[str]:
            """``CfnSkill.SkillPackageProperty.S3ObjectVersion``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ask-skill-skillpackage.html#cfn-ask-skill-skillpackage-s3objectversion
            """
            return self._values.get('s3_object_version')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'SkillPackageProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



@jsii.data_type(jsii_type="@aws-cdk/alexa-ask.CfnSkillProps", jsii_struct_bases=[], name_mapping={'authentication_configuration': 'authenticationConfiguration', 'skill_package': 'skillPackage', 'vendor_id': 'vendorId'})
class CfnSkillProps():
    def __init__(self, *, authentication_configuration: typing.Union["CfnSkill.AuthenticationConfigurationProperty", aws_cdk.core.IResolvable], skill_package: typing.Union[aws_cdk.core.IResolvable, "CfnSkill.SkillPackageProperty"], vendor_id: str):
        """Properties for defining a ``Alexa::ASK::Skill``.

        :param authentication_configuration: ``Alexa::ASK::Skill.AuthenticationConfiguration``.
        :param skill_package: ``Alexa::ASK::Skill.SkillPackage``.
        :param vendor_id: ``Alexa::ASK::Skill.VendorId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ask-skill.html
        """
        self._values = {
            'authentication_configuration': authentication_configuration,
            'skill_package': skill_package,
            'vendor_id': vendor_id,
        }

    @property
    def authentication_configuration(self) -> typing.Union["CfnSkill.AuthenticationConfigurationProperty", aws_cdk.core.IResolvable]:
        """``Alexa::ASK::Skill.AuthenticationConfiguration``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ask-skill.html#cfn-ask-skill-authenticationconfiguration
        """
        return self._values.get('authentication_configuration')

    @property
    def skill_package(self) -> typing.Union[aws_cdk.core.IResolvable, "CfnSkill.SkillPackageProperty"]:
        """``Alexa::ASK::Skill.SkillPackage``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ask-skill.html#cfn-ask-skill-skillpackage
        """
        return self._values.get('skill_package')

    @property
    def vendor_id(self) -> str:
        """``Alexa::ASK::Skill.VendorId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ask-skill.html#cfn-ask-skill-vendorid
        """
        return self._values.get('vendor_id')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnSkillProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


__all__ = ["CfnSkill", "CfnSkillProps", "__jsii_assembly__"]

publication.publish()
