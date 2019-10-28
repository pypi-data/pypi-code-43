import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.core
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-pinpoint", "1.15.0", __name__, "aws-pinpoint@1.15.0.jsii.tgz")
class CfnADMChannel(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-pinpoint.CfnADMChannel"):
    """A CloudFormation ``AWS::Pinpoint::ADMChannel``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-admchannel.html
    cloudformationResource:
    :cloudformationResource:: AWS::Pinpoint::ADMChannel
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, application_id: str, client_id: str, client_secret: str, enabled: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None) -> None:
        """Create a new ``AWS::Pinpoint::ADMChannel``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param application_id: ``AWS::Pinpoint::ADMChannel.ApplicationId``.
        :param client_id: ``AWS::Pinpoint::ADMChannel.ClientId``.
        :param client_secret: ``AWS::Pinpoint::ADMChannel.ClientSecret``.
        :param enabled: ``AWS::Pinpoint::ADMChannel.Enabled``.
        """
        props = CfnADMChannelProps(application_id=application_id, client_id=client_id, client_secret=client_secret, enabled=enabled)

        jsii.create(CfnADMChannel, self, [scope, id, props])

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
    @jsii.member(jsii_name="applicationId")
    def application_id(self) -> str:
        """``AWS::Pinpoint::ADMChannel.ApplicationId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-admchannel.html#cfn-pinpoint-admchannel-applicationid
        """
        return jsii.get(self, "applicationId")

    @application_id.setter
    def application_id(self, value: str):
        return jsii.set(self, "applicationId", value)

    @property
    @jsii.member(jsii_name="clientId")
    def client_id(self) -> str:
        """``AWS::Pinpoint::ADMChannel.ClientId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-admchannel.html#cfn-pinpoint-admchannel-clientid
        """
        return jsii.get(self, "clientId")

    @client_id.setter
    def client_id(self, value: str):
        return jsii.set(self, "clientId", value)

    @property
    @jsii.member(jsii_name="clientSecret")
    def client_secret(self) -> str:
        """``AWS::Pinpoint::ADMChannel.ClientSecret``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-admchannel.html#cfn-pinpoint-admchannel-clientsecret
        """
        return jsii.get(self, "clientSecret")

    @client_secret.setter
    def client_secret(self, value: str):
        return jsii.set(self, "clientSecret", value)

    @property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::Pinpoint::ADMChannel.Enabled``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-admchannel.html#cfn-pinpoint-admchannel-enabled
        """
        return jsii.get(self, "enabled")

    @enabled.setter
    def enabled(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "enabled", value)


@jsii.data_type(jsii_type="@aws-cdk/aws-pinpoint.CfnADMChannelProps", jsii_struct_bases=[], name_mapping={'application_id': 'applicationId', 'client_id': 'clientId', 'client_secret': 'clientSecret', 'enabled': 'enabled'})
class CfnADMChannelProps():
    def __init__(self, *, application_id: str, client_id: str, client_secret: str, enabled: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None):
        """Properties for defining a ``AWS::Pinpoint::ADMChannel``.

        :param application_id: ``AWS::Pinpoint::ADMChannel.ApplicationId``.
        :param client_id: ``AWS::Pinpoint::ADMChannel.ClientId``.
        :param client_secret: ``AWS::Pinpoint::ADMChannel.ClientSecret``.
        :param enabled: ``AWS::Pinpoint::ADMChannel.Enabled``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-admchannel.html
        """
        self._values = {
            'application_id': application_id,
            'client_id': client_id,
            'client_secret': client_secret,
        }
        if enabled is not None: self._values["enabled"] = enabled

    @property
    def application_id(self) -> str:
        """``AWS::Pinpoint::ADMChannel.ApplicationId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-admchannel.html#cfn-pinpoint-admchannel-applicationid
        """
        return self._values.get('application_id')

    @property
    def client_id(self) -> str:
        """``AWS::Pinpoint::ADMChannel.ClientId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-admchannel.html#cfn-pinpoint-admchannel-clientid
        """
        return self._values.get('client_id')

    @property
    def client_secret(self) -> str:
        """``AWS::Pinpoint::ADMChannel.ClientSecret``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-admchannel.html#cfn-pinpoint-admchannel-clientsecret
        """
        return self._values.get('client_secret')

    @property
    def enabled(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::Pinpoint::ADMChannel.Enabled``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-admchannel.html#cfn-pinpoint-admchannel-enabled
        """
        return self._values.get('enabled')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnADMChannelProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnAPNSChannel(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-pinpoint.CfnAPNSChannel"):
    """A CloudFormation ``AWS::Pinpoint::APNSChannel``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnschannel.html
    cloudformationResource:
    :cloudformationResource:: AWS::Pinpoint::APNSChannel
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, application_id: str, bundle_id: typing.Optional[str]=None, certificate: typing.Optional[str]=None, default_authentication_method: typing.Optional[str]=None, enabled: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, private_key: typing.Optional[str]=None, team_id: typing.Optional[str]=None, token_key: typing.Optional[str]=None, token_key_id: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::Pinpoint::APNSChannel``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param application_id: ``AWS::Pinpoint::APNSChannel.ApplicationId``.
        :param bundle_id: ``AWS::Pinpoint::APNSChannel.BundleId``.
        :param certificate: ``AWS::Pinpoint::APNSChannel.Certificate``.
        :param default_authentication_method: ``AWS::Pinpoint::APNSChannel.DefaultAuthenticationMethod``.
        :param enabled: ``AWS::Pinpoint::APNSChannel.Enabled``.
        :param private_key: ``AWS::Pinpoint::APNSChannel.PrivateKey``.
        :param team_id: ``AWS::Pinpoint::APNSChannel.TeamId``.
        :param token_key: ``AWS::Pinpoint::APNSChannel.TokenKey``.
        :param token_key_id: ``AWS::Pinpoint::APNSChannel.TokenKeyId``.
        """
        props = CfnAPNSChannelProps(application_id=application_id, bundle_id=bundle_id, certificate=certificate, default_authentication_method=default_authentication_method, enabled=enabled, private_key=private_key, team_id=team_id, token_key=token_key, token_key_id=token_key_id)

        jsii.create(CfnAPNSChannel, self, [scope, id, props])

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
    @jsii.member(jsii_name="applicationId")
    def application_id(self) -> str:
        """``AWS::Pinpoint::APNSChannel.ApplicationId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnschannel.html#cfn-pinpoint-apnschannel-applicationid
        """
        return jsii.get(self, "applicationId")

    @application_id.setter
    def application_id(self, value: str):
        return jsii.set(self, "applicationId", value)

    @property
    @jsii.member(jsii_name="bundleId")
    def bundle_id(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::APNSChannel.BundleId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnschannel.html#cfn-pinpoint-apnschannel-bundleid
        """
        return jsii.get(self, "bundleId")

    @bundle_id.setter
    def bundle_id(self, value: typing.Optional[str]):
        return jsii.set(self, "bundleId", value)

    @property
    @jsii.member(jsii_name="certificate")
    def certificate(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::APNSChannel.Certificate``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnschannel.html#cfn-pinpoint-apnschannel-certificate
        """
        return jsii.get(self, "certificate")

    @certificate.setter
    def certificate(self, value: typing.Optional[str]):
        return jsii.set(self, "certificate", value)

    @property
    @jsii.member(jsii_name="defaultAuthenticationMethod")
    def default_authentication_method(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::APNSChannel.DefaultAuthenticationMethod``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnschannel.html#cfn-pinpoint-apnschannel-defaultauthenticationmethod
        """
        return jsii.get(self, "defaultAuthenticationMethod")

    @default_authentication_method.setter
    def default_authentication_method(self, value: typing.Optional[str]):
        return jsii.set(self, "defaultAuthenticationMethod", value)

    @property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::Pinpoint::APNSChannel.Enabled``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnschannel.html#cfn-pinpoint-apnschannel-enabled
        """
        return jsii.get(self, "enabled")

    @enabled.setter
    def enabled(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "enabled", value)

    @property
    @jsii.member(jsii_name="privateKey")
    def private_key(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::APNSChannel.PrivateKey``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnschannel.html#cfn-pinpoint-apnschannel-privatekey
        """
        return jsii.get(self, "privateKey")

    @private_key.setter
    def private_key(self, value: typing.Optional[str]):
        return jsii.set(self, "privateKey", value)

    @property
    @jsii.member(jsii_name="teamId")
    def team_id(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::APNSChannel.TeamId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnschannel.html#cfn-pinpoint-apnschannel-teamid
        """
        return jsii.get(self, "teamId")

    @team_id.setter
    def team_id(self, value: typing.Optional[str]):
        return jsii.set(self, "teamId", value)

    @property
    @jsii.member(jsii_name="tokenKey")
    def token_key(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::APNSChannel.TokenKey``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnschannel.html#cfn-pinpoint-apnschannel-tokenkey
        """
        return jsii.get(self, "tokenKey")

    @token_key.setter
    def token_key(self, value: typing.Optional[str]):
        return jsii.set(self, "tokenKey", value)

    @property
    @jsii.member(jsii_name="tokenKeyId")
    def token_key_id(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::APNSChannel.TokenKeyId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnschannel.html#cfn-pinpoint-apnschannel-tokenkeyid
        """
        return jsii.get(self, "tokenKeyId")

    @token_key_id.setter
    def token_key_id(self, value: typing.Optional[str]):
        return jsii.set(self, "tokenKeyId", value)


@jsii.data_type(jsii_type="@aws-cdk/aws-pinpoint.CfnAPNSChannelProps", jsii_struct_bases=[], name_mapping={'application_id': 'applicationId', 'bundle_id': 'bundleId', 'certificate': 'certificate', 'default_authentication_method': 'defaultAuthenticationMethod', 'enabled': 'enabled', 'private_key': 'privateKey', 'team_id': 'teamId', 'token_key': 'tokenKey', 'token_key_id': 'tokenKeyId'})
class CfnAPNSChannelProps():
    def __init__(self, *, application_id: str, bundle_id: typing.Optional[str]=None, certificate: typing.Optional[str]=None, default_authentication_method: typing.Optional[str]=None, enabled: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, private_key: typing.Optional[str]=None, team_id: typing.Optional[str]=None, token_key: typing.Optional[str]=None, token_key_id: typing.Optional[str]=None):
        """Properties for defining a ``AWS::Pinpoint::APNSChannel``.

        :param application_id: ``AWS::Pinpoint::APNSChannel.ApplicationId``.
        :param bundle_id: ``AWS::Pinpoint::APNSChannel.BundleId``.
        :param certificate: ``AWS::Pinpoint::APNSChannel.Certificate``.
        :param default_authentication_method: ``AWS::Pinpoint::APNSChannel.DefaultAuthenticationMethod``.
        :param enabled: ``AWS::Pinpoint::APNSChannel.Enabled``.
        :param private_key: ``AWS::Pinpoint::APNSChannel.PrivateKey``.
        :param team_id: ``AWS::Pinpoint::APNSChannel.TeamId``.
        :param token_key: ``AWS::Pinpoint::APNSChannel.TokenKey``.
        :param token_key_id: ``AWS::Pinpoint::APNSChannel.TokenKeyId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnschannel.html
        """
        self._values = {
            'application_id': application_id,
        }
        if bundle_id is not None: self._values["bundle_id"] = bundle_id
        if certificate is not None: self._values["certificate"] = certificate
        if default_authentication_method is not None: self._values["default_authentication_method"] = default_authentication_method
        if enabled is not None: self._values["enabled"] = enabled
        if private_key is not None: self._values["private_key"] = private_key
        if team_id is not None: self._values["team_id"] = team_id
        if token_key is not None: self._values["token_key"] = token_key
        if token_key_id is not None: self._values["token_key_id"] = token_key_id

    @property
    def application_id(self) -> str:
        """``AWS::Pinpoint::APNSChannel.ApplicationId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnschannel.html#cfn-pinpoint-apnschannel-applicationid
        """
        return self._values.get('application_id')

    @property
    def bundle_id(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::APNSChannel.BundleId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnschannel.html#cfn-pinpoint-apnschannel-bundleid
        """
        return self._values.get('bundle_id')

    @property
    def certificate(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::APNSChannel.Certificate``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnschannel.html#cfn-pinpoint-apnschannel-certificate
        """
        return self._values.get('certificate')

    @property
    def default_authentication_method(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::APNSChannel.DefaultAuthenticationMethod``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnschannel.html#cfn-pinpoint-apnschannel-defaultauthenticationmethod
        """
        return self._values.get('default_authentication_method')

    @property
    def enabled(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::Pinpoint::APNSChannel.Enabled``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnschannel.html#cfn-pinpoint-apnschannel-enabled
        """
        return self._values.get('enabled')

    @property
    def private_key(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::APNSChannel.PrivateKey``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnschannel.html#cfn-pinpoint-apnschannel-privatekey
        """
        return self._values.get('private_key')

    @property
    def team_id(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::APNSChannel.TeamId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnschannel.html#cfn-pinpoint-apnschannel-teamid
        """
        return self._values.get('team_id')

    @property
    def token_key(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::APNSChannel.TokenKey``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnschannel.html#cfn-pinpoint-apnschannel-tokenkey
        """
        return self._values.get('token_key')

    @property
    def token_key_id(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::APNSChannel.TokenKeyId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnschannel.html#cfn-pinpoint-apnschannel-tokenkeyid
        """
        return self._values.get('token_key_id')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnAPNSChannelProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnAPNSSandboxChannel(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-pinpoint.CfnAPNSSandboxChannel"):
    """A CloudFormation ``AWS::Pinpoint::APNSSandboxChannel``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnssandboxchannel.html
    cloudformationResource:
    :cloudformationResource:: AWS::Pinpoint::APNSSandboxChannel
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, application_id: str, bundle_id: typing.Optional[str]=None, certificate: typing.Optional[str]=None, default_authentication_method: typing.Optional[str]=None, enabled: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, private_key: typing.Optional[str]=None, team_id: typing.Optional[str]=None, token_key: typing.Optional[str]=None, token_key_id: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::Pinpoint::APNSSandboxChannel``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param application_id: ``AWS::Pinpoint::APNSSandboxChannel.ApplicationId``.
        :param bundle_id: ``AWS::Pinpoint::APNSSandboxChannel.BundleId``.
        :param certificate: ``AWS::Pinpoint::APNSSandboxChannel.Certificate``.
        :param default_authentication_method: ``AWS::Pinpoint::APNSSandboxChannel.DefaultAuthenticationMethod``.
        :param enabled: ``AWS::Pinpoint::APNSSandboxChannel.Enabled``.
        :param private_key: ``AWS::Pinpoint::APNSSandboxChannel.PrivateKey``.
        :param team_id: ``AWS::Pinpoint::APNSSandboxChannel.TeamId``.
        :param token_key: ``AWS::Pinpoint::APNSSandboxChannel.TokenKey``.
        :param token_key_id: ``AWS::Pinpoint::APNSSandboxChannel.TokenKeyId``.
        """
        props = CfnAPNSSandboxChannelProps(application_id=application_id, bundle_id=bundle_id, certificate=certificate, default_authentication_method=default_authentication_method, enabled=enabled, private_key=private_key, team_id=team_id, token_key=token_key, token_key_id=token_key_id)

        jsii.create(CfnAPNSSandboxChannel, self, [scope, id, props])

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
    @jsii.member(jsii_name="applicationId")
    def application_id(self) -> str:
        """``AWS::Pinpoint::APNSSandboxChannel.ApplicationId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnssandboxchannel.html#cfn-pinpoint-apnssandboxchannel-applicationid
        """
        return jsii.get(self, "applicationId")

    @application_id.setter
    def application_id(self, value: str):
        return jsii.set(self, "applicationId", value)

    @property
    @jsii.member(jsii_name="bundleId")
    def bundle_id(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::APNSSandboxChannel.BundleId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnssandboxchannel.html#cfn-pinpoint-apnssandboxchannel-bundleid
        """
        return jsii.get(self, "bundleId")

    @bundle_id.setter
    def bundle_id(self, value: typing.Optional[str]):
        return jsii.set(self, "bundleId", value)

    @property
    @jsii.member(jsii_name="certificate")
    def certificate(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::APNSSandboxChannel.Certificate``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnssandboxchannel.html#cfn-pinpoint-apnssandboxchannel-certificate
        """
        return jsii.get(self, "certificate")

    @certificate.setter
    def certificate(self, value: typing.Optional[str]):
        return jsii.set(self, "certificate", value)

    @property
    @jsii.member(jsii_name="defaultAuthenticationMethod")
    def default_authentication_method(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::APNSSandboxChannel.DefaultAuthenticationMethod``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnssandboxchannel.html#cfn-pinpoint-apnssandboxchannel-defaultauthenticationmethod
        """
        return jsii.get(self, "defaultAuthenticationMethod")

    @default_authentication_method.setter
    def default_authentication_method(self, value: typing.Optional[str]):
        return jsii.set(self, "defaultAuthenticationMethod", value)

    @property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::Pinpoint::APNSSandboxChannel.Enabled``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnssandboxchannel.html#cfn-pinpoint-apnssandboxchannel-enabled
        """
        return jsii.get(self, "enabled")

    @enabled.setter
    def enabled(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "enabled", value)

    @property
    @jsii.member(jsii_name="privateKey")
    def private_key(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::APNSSandboxChannel.PrivateKey``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnssandboxchannel.html#cfn-pinpoint-apnssandboxchannel-privatekey
        """
        return jsii.get(self, "privateKey")

    @private_key.setter
    def private_key(self, value: typing.Optional[str]):
        return jsii.set(self, "privateKey", value)

    @property
    @jsii.member(jsii_name="teamId")
    def team_id(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::APNSSandboxChannel.TeamId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnssandboxchannel.html#cfn-pinpoint-apnssandboxchannel-teamid
        """
        return jsii.get(self, "teamId")

    @team_id.setter
    def team_id(self, value: typing.Optional[str]):
        return jsii.set(self, "teamId", value)

    @property
    @jsii.member(jsii_name="tokenKey")
    def token_key(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::APNSSandboxChannel.TokenKey``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnssandboxchannel.html#cfn-pinpoint-apnssandboxchannel-tokenkey
        """
        return jsii.get(self, "tokenKey")

    @token_key.setter
    def token_key(self, value: typing.Optional[str]):
        return jsii.set(self, "tokenKey", value)

    @property
    @jsii.member(jsii_name="tokenKeyId")
    def token_key_id(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::APNSSandboxChannel.TokenKeyId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnssandboxchannel.html#cfn-pinpoint-apnssandboxchannel-tokenkeyid
        """
        return jsii.get(self, "tokenKeyId")

    @token_key_id.setter
    def token_key_id(self, value: typing.Optional[str]):
        return jsii.set(self, "tokenKeyId", value)


@jsii.data_type(jsii_type="@aws-cdk/aws-pinpoint.CfnAPNSSandboxChannelProps", jsii_struct_bases=[], name_mapping={'application_id': 'applicationId', 'bundle_id': 'bundleId', 'certificate': 'certificate', 'default_authentication_method': 'defaultAuthenticationMethod', 'enabled': 'enabled', 'private_key': 'privateKey', 'team_id': 'teamId', 'token_key': 'tokenKey', 'token_key_id': 'tokenKeyId'})
class CfnAPNSSandboxChannelProps():
    def __init__(self, *, application_id: str, bundle_id: typing.Optional[str]=None, certificate: typing.Optional[str]=None, default_authentication_method: typing.Optional[str]=None, enabled: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, private_key: typing.Optional[str]=None, team_id: typing.Optional[str]=None, token_key: typing.Optional[str]=None, token_key_id: typing.Optional[str]=None):
        """Properties for defining a ``AWS::Pinpoint::APNSSandboxChannel``.

        :param application_id: ``AWS::Pinpoint::APNSSandboxChannel.ApplicationId``.
        :param bundle_id: ``AWS::Pinpoint::APNSSandboxChannel.BundleId``.
        :param certificate: ``AWS::Pinpoint::APNSSandboxChannel.Certificate``.
        :param default_authentication_method: ``AWS::Pinpoint::APNSSandboxChannel.DefaultAuthenticationMethod``.
        :param enabled: ``AWS::Pinpoint::APNSSandboxChannel.Enabled``.
        :param private_key: ``AWS::Pinpoint::APNSSandboxChannel.PrivateKey``.
        :param team_id: ``AWS::Pinpoint::APNSSandboxChannel.TeamId``.
        :param token_key: ``AWS::Pinpoint::APNSSandboxChannel.TokenKey``.
        :param token_key_id: ``AWS::Pinpoint::APNSSandboxChannel.TokenKeyId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnssandboxchannel.html
        """
        self._values = {
            'application_id': application_id,
        }
        if bundle_id is not None: self._values["bundle_id"] = bundle_id
        if certificate is not None: self._values["certificate"] = certificate
        if default_authentication_method is not None: self._values["default_authentication_method"] = default_authentication_method
        if enabled is not None: self._values["enabled"] = enabled
        if private_key is not None: self._values["private_key"] = private_key
        if team_id is not None: self._values["team_id"] = team_id
        if token_key is not None: self._values["token_key"] = token_key
        if token_key_id is not None: self._values["token_key_id"] = token_key_id

    @property
    def application_id(self) -> str:
        """``AWS::Pinpoint::APNSSandboxChannel.ApplicationId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnssandboxchannel.html#cfn-pinpoint-apnssandboxchannel-applicationid
        """
        return self._values.get('application_id')

    @property
    def bundle_id(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::APNSSandboxChannel.BundleId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnssandboxchannel.html#cfn-pinpoint-apnssandboxchannel-bundleid
        """
        return self._values.get('bundle_id')

    @property
    def certificate(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::APNSSandboxChannel.Certificate``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnssandboxchannel.html#cfn-pinpoint-apnssandboxchannel-certificate
        """
        return self._values.get('certificate')

    @property
    def default_authentication_method(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::APNSSandboxChannel.DefaultAuthenticationMethod``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnssandboxchannel.html#cfn-pinpoint-apnssandboxchannel-defaultauthenticationmethod
        """
        return self._values.get('default_authentication_method')

    @property
    def enabled(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::Pinpoint::APNSSandboxChannel.Enabled``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnssandboxchannel.html#cfn-pinpoint-apnssandboxchannel-enabled
        """
        return self._values.get('enabled')

    @property
    def private_key(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::APNSSandboxChannel.PrivateKey``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnssandboxchannel.html#cfn-pinpoint-apnssandboxchannel-privatekey
        """
        return self._values.get('private_key')

    @property
    def team_id(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::APNSSandboxChannel.TeamId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnssandboxchannel.html#cfn-pinpoint-apnssandboxchannel-teamid
        """
        return self._values.get('team_id')

    @property
    def token_key(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::APNSSandboxChannel.TokenKey``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnssandboxchannel.html#cfn-pinpoint-apnssandboxchannel-tokenkey
        """
        return self._values.get('token_key')

    @property
    def token_key_id(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::APNSSandboxChannel.TokenKeyId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnssandboxchannel.html#cfn-pinpoint-apnssandboxchannel-tokenkeyid
        """
        return self._values.get('token_key_id')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnAPNSSandboxChannelProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnAPNSVoipChannel(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-pinpoint.CfnAPNSVoipChannel"):
    """A CloudFormation ``AWS::Pinpoint::APNSVoipChannel``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnsvoipchannel.html
    cloudformationResource:
    :cloudformationResource:: AWS::Pinpoint::APNSVoipChannel
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, application_id: str, bundle_id: typing.Optional[str]=None, certificate: typing.Optional[str]=None, default_authentication_method: typing.Optional[str]=None, enabled: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, private_key: typing.Optional[str]=None, team_id: typing.Optional[str]=None, token_key: typing.Optional[str]=None, token_key_id: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::Pinpoint::APNSVoipChannel``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param application_id: ``AWS::Pinpoint::APNSVoipChannel.ApplicationId``.
        :param bundle_id: ``AWS::Pinpoint::APNSVoipChannel.BundleId``.
        :param certificate: ``AWS::Pinpoint::APNSVoipChannel.Certificate``.
        :param default_authentication_method: ``AWS::Pinpoint::APNSVoipChannel.DefaultAuthenticationMethod``.
        :param enabled: ``AWS::Pinpoint::APNSVoipChannel.Enabled``.
        :param private_key: ``AWS::Pinpoint::APNSVoipChannel.PrivateKey``.
        :param team_id: ``AWS::Pinpoint::APNSVoipChannel.TeamId``.
        :param token_key: ``AWS::Pinpoint::APNSVoipChannel.TokenKey``.
        :param token_key_id: ``AWS::Pinpoint::APNSVoipChannel.TokenKeyId``.
        """
        props = CfnAPNSVoipChannelProps(application_id=application_id, bundle_id=bundle_id, certificate=certificate, default_authentication_method=default_authentication_method, enabled=enabled, private_key=private_key, team_id=team_id, token_key=token_key, token_key_id=token_key_id)

        jsii.create(CfnAPNSVoipChannel, self, [scope, id, props])

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
    @jsii.member(jsii_name="applicationId")
    def application_id(self) -> str:
        """``AWS::Pinpoint::APNSVoipChannel.ApplicationId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnsvoipchannel.html#cfn-pinpoint-apnsvoipchannel-applicationid
        """
        return jsii.get(self, "applicationId")

    @application_id.setter
    def application_id(self, value: str):
        return jsii.set(self, "applicationId", value)

    @property
    @jsii.member(jsii_name="bundleId")
    def bundle_id(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::APNSVoipChannel.BundleId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnsvoipchannel.html#cfn-pinpoint-apnsvoipchannel-bundleid
        """
        return jsii.get(self, "bundleId")

    @bundle_id.setter
    def bundle_id(self, value: typing.Optional[str]):
        return jsii.set(self, "bundleId", value)

    @property
    @jsii.member(jsii_name="certificate")
    def certificate(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::APNSVoipChannel.Certificate``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnsvoipchannel.html#cfn-pinpoint-apnsvoipchannel-certificate
        """
        return jsii.get(self, "certificate")

    @certificate.setter
    def certificate(self, value: typing.Optional[str]):
        return jsii.set(self, "certificate", value)

    @property
    @jsii.member(jsii_name="defaultAuthenticationMethod")
    def default_authentication_method(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::APNSVoipChannel.DefaultAuthenticationMethod``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnsvoipchannel.html#cfn-pinpoint-apnsvoipchannel-defaultauthenticationmethod
        """
        return jsii.get(self, "defaultAuthenticationMethod")

    @default_authentication_method.setter
    def default_authentication_method(self, value: typing.Optional[str]):
        return jsii.set(self, "defaultAuthenticationMethod", value)

    @property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::Pinpoint::APNSVoipChannel.Enabled``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnsvoipchannel.html#cfn-pinpoint-apnsvoipchannel-enabled
        """
        return jsii.get(self, "enabled")

    @enabled.setter
    def enabled(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "enabled", value)

    @property
    @jsii.member(jsii_name="privateKey")
    def private_key(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::APNSVoipChannel.PrivateKey``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnsvoipchannel.html#cfn-pinpoint-apnsvoipchannel-privatekey
        """
        return jsii.get(self, "privateKey")

    @private_key.setter
    def private_key(self, value: typing.Optional[str]):
        return jsii.set(self, "privateKey", value)

    @property
    @jsii.member(jsii_name="teamId")
    def team_id(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::APNSVoipChannel.TeamId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnsvoipchannel.html#cfn-pinpoint-apnsvoipchannel-teamid
        """
        return jsii.get(self, "teamId")

    @team_id.setter
    def team_id(self, value: typing.Optional[str]):
        return jsii.set(self, "teamId", value)

    @property
    @jsii.member(jsii_name="tokenKey")
    def token_key(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::APNSVoipChannel.TokenKey``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnsvoipchannel.html#cfn-pinpoint-apnsvoipchannel-tokenkey
        """
        return jsii.get(self, "tokenKey")

    @token_key.setter
    def token_key(self, value: typing.Optional[str]):
        return jsii.set(self, "tokenKey", value)

    @property
    @jsii.member(jsii_name="tokenKeyId")
    def token_key_id(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::APNSVoipChannel.TokenKeyId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnsvoipchannel.html#cfn-pinpoint-apnsvoipchannel-tokenkeyid
        """
        return jsii.get(self, "tokenKeyId")

    @token_key_id.setter
    def token_key_id(self, value: typing.Optional[str]):
        return jsii.set(self, "tokenKeyId", value)


@jsii.data_type(jsii_type="@aws-cdk/aws-pinpoint.CfnAPNSVoipChannelProps", jsii_struct_bases=[], name_mapping={'application_id': 'applicationId', 'bundle_id': 'bundleId', 'certificate': 'certificate', 'default_authentication_method': 'defaultAuthenticationMethod', 'enabled': 'enabled', 'private_key': 'privateKey', 'team_id': 'teamId', 'token_key': 'tokenKey', 'token_key_id': 'tokenKeyId'})
class CfnAPNSVoipChannelProps():
    def __init__(self, *, application_id: str, bundle_id: typing.Optional[str]=None, certificate: typing.Optional[str]=None, default_authentication_method: typing.Optional[str]=None, enabled: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, private_key: typing.Optional[str]=None, team_id: typing.Optional[str]=None, token_key: typing.Optional[str]=None, token_key_id: typing.Optional[str]=None):
        """Properties for defining a ``AWS::Pinpoint::APNSVoipChannel``.

        :param application_id: ``AWS::Pinpoint::APNSVoipChannel.ApplicationId``.
        :param bundle_id: ``AWS::Pinpoint::APNSVoipChannel.BundleId``.
        :param certificate: ``AWS::Pinpoint::APNSVoipChannel.Certificate``.
        :param default_authentication_method: ``AWS::Pinpoint::APNSVoipChannel.DefaultAuthenticationMethod``.
        :param enabled: ``AWS::Pinpoint::APNSVoipChannel.Enabled``.
        :param private_key: ``AWS::Pinpoint::APNSVoipChannel.PrivateKey``.
        :param team_id: ``AWS::Pinpoint::APNSVoipChannel.TeamId``.
        :param token_key: ``AWS::Pinpoint::APNSVoipChannel.TokenKey``.
        :param token_key_id: ``AWS::Pinpoint::APNSVoipChannel.TokenKeyId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnsvoipchannel.html
        """
        self._values = {
            'application_id': application_id,
        }
        if bundle_id is not None: self._values["bundle_id"] = bundle_id
        if certificate is not None: self._values["certificate"] = certificate
        if default_authentication_method is not None: self._values["default_authentication_method"] = default_authentication_method
        if enabled is not None: self._values["enabled"] = enabled
        if private_key is not None: self._values["private_key"] = private_key
        if team_id is not None: self._values["team_id"] = team_id
        if token_key is not None: self._values["token_key"] = token_key
        if token_key_id is not None: self._values["token_key_id"] = token_key_id

    @property
    def application_id(self) -> str:
        """``AWS::Pinpoint::APNSVoipChannel.ApplicationId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnsvoipchannel.html#cfn-pinpoint-apnsvoipchannel-applicationid
        """
        return self._values.get('application_id')

    @property
    def bundle_id(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::APNSVoipChannel.BundleId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnsvoipchannel.html#cfn-pinpoint-apnsvoipchannel-bundleid
        """
        return self._values.get('bundle_id')

    @property
    def certificate(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::APNSVoipChannel.Certificate``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnsvoipchannel.html#cfn-pinpoint-apnsvoipchannel-certificate
        """
        return self._values.get('certificate')

    @property
    def default_authentication_method(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::APNSVoipChannel.DefaultAuthenticationMethod``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnsvoipchannel.html#cfn-pinpoint-apnsvoipchannel-defaultauthenticationmethod
        """
        return self._values.get('default_authentication_method')

    @property
    def enabled(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::Pinpoint::APNSVoipChannel.Enabled``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnsvoipchannel.html#cfn-pinpoint-apnsvoipchannel-enabled
        """
        return self._values.get('enabled')

    @property
    def private_key(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::APNSVoipChannel.PrivateKey``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnsvoipchannel.html#cfn-pinpoint-apnsvoipchannel-privatekey
        """
        return self._values.get('private_key')

    @property
    def team_id(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::APNSVoipChannel.TeamId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnsvoipchannel.html#cfn-pinpoint-apnsvoipchannel-teamid
        """
        return self._values.get('team_id')

    @property
    def token_key(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::APNSVoipChannel.TokenKey``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnsvoipchannel.html#cfn-pinpoint-apnsvoipchannel-tokenkey
        """
        return self._values.get('token_key')

    @property
    def token_key_id(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::APNSVoipChannel.TokenKeyId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnsvoipchannel.html#cfn-pinpoint-apnsvoipchannel-tokenkeyid
        """
        return self._values.get('token_key_id')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnAPNSVoipChannelProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnAPNSVoipSandboxChannel(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-pinpoint.CfnAPNSVoipSandboxChannel"):
    """A CloudFormation ``AWS::Pinpoint::APNSVoipSandboxChannel``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnsvoipsandboxchannel.html
    cloudformationResource:
    :cloudformationResource:: AWS::Pinpoint::APNSVoipSandboxChannel
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, application_id: str, bundle_id: typing.Optional[str]=None, certificate: typing.Optional[str]=None, default_authentication_method: typing.Optional[str]=None, enabled: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, private_key: typing.Optional[str]=None, team_id: typing.Optional[str]=None, token_key: typing.Optional[str]=None, token_key_id: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::Pinpoint::APNSVoipSandboxChannel``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param application_id: ``AWS::Pinpoint::APNSVoipSandboxChannel.ApplicationId``.
        :param bundle_id: ``AWS::Pinpoint::APNSVoipSandboxChannel.BundleId``.
        :param certificate: ``AWS::Pinpoint::APNSVoipSandboxChannel.Certificate``.
        :param default_authentication_method: ``AWS::Pinpoint::APNSVoipSandboxChannel.DefaultAuthenticationMethod``.
        :param enabled: ``AWS::Pinpoint::APNSVoipSandboxChannel.Enabled``.
        :param private_key: ``AWS::Pinpoint::APNSVoipSandboxChannel.PrivateKey``.
        :param team_id: ``AWS::Pinpoint::APNSVoipSandboxChannel.TeamId``.
        :param token_key: ``AWS::Pinpoint::APNSVoipSandboxChannel.TokenKey``.
        :param token_key_id: ``AWS::Pinpoint::APNSVoipSandboxChannel.TokenKeyId``.
        """
        props = CfnAPNSVoipSandboxChannelProps(application_id=application_id, bundle_id=bundle_id, certificate=certificate, default_authentication_method=default_authentication_method, enabled=enabled, private_key=private_key, team_id=team_id, token_key=token_key, token_key_id=token_key_id)

        jsii.create(CfnAPNSVoipSandboxChannel, self, [scope, id, props])

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
    @jsii.member(jsii_name="applicationId")
    def application_id(self) -> str:
        """``AWS::Pinpoint::APNSVoipSandboxChannel.ApplicationId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnsvoipsandboxchannel.html#cfn-pinpoint-apnsvoipsandboxchannel-applicationid
        """
        return jsii.get(self, "applicationId")

    @application_id.setter
    def application_id(self, value: str):
        return jsii.set(self, "applicationId", value)

    @property
    @jsii.member(jsii_name="bundleId")
    def bundle_id(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::APNSVoipSandboxChannel.BundleId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnsvoipsandboxchannel.html#cfn-pinpoint-apnsvoipsandboxchannel-bundleid
        """
        return jsii.get(self, "bundleId")

    @bundle_id.setter
    def bundle_id(self, value: typing.Optional[str]):
        return jsii.set(self, "bundleId", value)

    @property
    @jsii.member(jsii_name="certificate")
    def certificate(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::APNSVoipSandboxChannel.Certificate``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnsvoipsandboxchannel.html#cfn-pinpoint-apnsvoipsandboxchannel-certificate
        """
        return jsii.get(self, "certificate")

    @certificate.setter
    def certificate(self, value: typing.Optional[str]):
        return jsii.set(self, "certificate", value)

    @property
    @jsii.member(jsii_name="defaultAuthenticationMethod")
    def default_authentication_method(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::APNSVoipSandboxChannel.DefaultAuthenticationMethod``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnsvoipsandboxchannel.html#cfn-pinpoint-apnsvoipsandboxchannel-defaultauthenticationmethod
        """
        return jsii.get(self, "defaultAuthenticationMethod")

    @default_authentication_method.setter
    def default_authentication_method(self, value: typing.Optional[str]):
        return jsii.set(self, "defaultAuthenticationMethod", value)

    @property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::Pinpoint::APNSVoipSandboxChannel.Enabled``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnsvoipsandboxchannel.html#cfn-pinpoint-apnsvoipsandboxchannel-enabled
        """
        return jsii.get(self, "enabled")

    @enabled.setter
    def enabled(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "enabled", value)

    @property
    @jsii.member(jsii_name="privateKey")
    def private_key(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::APNSVoipSandboxChannel.PrivateKey``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnsvoipsandboxchannel.html#cfn-pinpoint-apnsvoipsandboxchannel-privatekey
        """
        return jsii.get(self, "privateKey")

    @private_key.setter
    def private_key(self, value: typing.Optional[str]):
        return jsii.set(self, "privateKey", value)

    @property
    @jsii.member(jsii_name="teamId")
    def team_id(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::APNSVoipSandboxChannel.TeamId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnsvoipsandboxchannel.html#cfn-pinpoint-apnsvoipsandboxchannel-teamid
        """
        return jsii.get(self, "teamId")

    @team_id.setter
    def team_id(self, value: typing.Optional[str]):
        return jsii.set(self, "teamId", value)

    @property
    @jsii.member(jsii_name="tokenKey")
    def token_key(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::APNSVoipSandboxChannel.TokenKey``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnsvoipsandboxchannel.html#cfn-pinpoint-apnsvoipsandboxchannel-tokenkey
        """
        return jsii.get(self, "tokenKey")

    @token_key.setter
    def token_key(self, value: typing.Optional[str]):
        return jsii.set(self, "tokenKey", value)

    @property
    @jsii.member(jsii_name="tokenKeyId")
    def token_key_id(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::APNSVoipSandboxChannel.TokenKeyId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnsvoipsandboxchannel.html#cfn-pinpoint-apnsvoipsandboxchannel-tokenkeyid
        """
        return jsii.get(self, "tokenKeyId")

    @token_key_id.setter
    def token_key_id(self, value: typing.Optional[str]):
        return jsii.set(self, "tokenKeyId", value)


@jsii.data_type(jsii_type="@aws-cdk/aws-pinpoint.CfnAPNSVoipSandboxChannelProps", jsii_struct_bases=[], name_mapping={'application_id': 'applicationId', 'bundle_id': 'bundleId', 'certificate': 'certificate', 'default_authentication_method': 'defaultAuthenticationMethod', 'enabled': 'enabled', 'private_key': 'privateKey', 'team_id': 'teamId', 'token_key': 'tokenKey', 'token_key_id': 'tokenKeyId'})
class CfnAPNSVoipSandboxChannelProps():
    def __init__(self, *, application_id: str, bundle_id: typing.Optional[str]=None, certificate: typing.Optional[str]=None, default_authentication_method: typing.Optional[str]=None, enabled: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, private_key: typing.Optional[str]=None, team_id: typing.Optional[str]=None, token_key: typing.Optional[str]=None, token_key_id: typing.Optional[str]=None):
        """Properties for defining a ``AWS::Pinpoint::APNSVoipSandboxChannel``.

        :param application_id: ``AWS::Pinpoint::APNSVoipSandboxChannel.ApplicationId``.
        :param bundle_id: ``AWS::Pinpoint::APNSVoipSandboxChannel.BundleId``.
        :param certificate: ``AWS::Pinpoint::APNSVoipSandboxChannel.Certificate``.
        :param default_authentication_method: ``AWS::Pinpoint::APNSVoipSandboxChannel.DefaultAuthenticationMethod``.
        :param enabled: ``AWS::Pinpoint::APNSVoipSandboxChannel.Enabled``.
        :param private_key: ``AWS::Pinpoint::APNSVoipSandboxChannel.PrivateKey``.
        :param team_id: ``AWS::Pinpoint::APNSVoipSandboxChannel.TeamId``.
        :param token_key: ``AWS::Pinpoint::APNSVoipSandboxChannel.TokenKey``.
        :param token_key_id: ``AWS::Pinpoint::APNSVoipSandboxChannel.TokenKeyId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnsvoipsandboxchannel.html
        """
        self._values = {
            'application_id': application_id,
        }
        if bundle_id is not None: self._values["bundle_id"] = bundle_id
        if certificate is not None: self._values["certificate"] = certificate
        if default_authentication_method is not None: self._values["default_authentication_method"] = default_authentication_method
        if enabled is not None: self._values["enabled"] = enabled
        if private_key is not None: self._values["private_key"] = private_key
        if team_id is not None: self._values["team_id"] = team_id
        if token_key is not None: self._values["token_key"] = token_key
        if token_key_id is not None: self._values["token_key_id"] = token_key_id

    @property
    def application_id(self) -> str:
        """``AWS::Pinpoint::APNSVoipSandboxChannel.ApplicationId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnsvoipsandboxchannel.html#cfn-pinpoint-apnsvoipsandboxchannel-applicationid
        """
        return self._values.get('application_id')

    @property
    def bundle_id(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::APNSVoipSandboxChannel.BundleId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnsvoipsandboxchannel.html#cfn-pinpoint-apnsvoipsandboxchannel-bundleid
        """
        return self._values.get('bundle_id')

    @property
    def certificate(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::APNSVoipSandboxChannel.Certificate``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnsvoipsandboxchannel.html#cfn-pinpoint-apnsvoipsandboxchannel-certificate
        """
        return self._values.get('certificate')

    @property
    def default_authentication_method(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::APNSVoipSandboxChannel.DefaultAuthenticationMethod``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnsvoipsandboxchannel.html#cfn-pinpoint-apnsvoipsandboxchannel-defaultauthenticationmethod
        """
        return self._values.get('default_authentication_method')

    @property
    def enabled(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::Pinpoint::APNSVoipSandboxChannel.Enabled``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnsvoipsandboxchannel.html#cfn-pinpoint-apnsvoipsandboxchannel-enabled
        """
        return self._values.get('enabled')

    @property
    def private_key(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::APNSVoipSandboxChannel.PrivateKey``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnsvoipsandboxchannel.html#cfn-pinpoint-apnsvoipsandboxchannel-privatekey
        """
        return self._values.get('private_key')

    @property
    def team_id(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::APNSVoipSandboxChannel.TeamId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnsvoipsandboxchannel.html#cfn-pinpoint-apnsvoipsandboxchannel-teamid
        """
        return self._values.get('team_id')

    @property
    def token_key(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::APNSVoipSandboxChannel.TokenKey``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnsvoipsandboxchannel.html#cfn-pinpoint-apnsvoipsandboxchannel-tokenkey
        """
        return self._values.get('token_key')

    @property
    def token_key_id(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::APNSVoipSandboxChannel.TokenKeyId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-apnsvoipsandboxchannel.html#cfn-pinpoint-apnsvoipsandboxchannel-tokenkeyid
        """
        return self._values.get('token_key_id')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnAPNSVoipSandboxChannelProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnApp(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-pinpoint.CfnApp"):
    """A CloudFormation ``AWS::Pinpoint::App``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-app.html
    cloudformationResource:
    :cloudformationResource:: AWS::Pinpoint::App
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, name: str, tags: typing.Any=None) -> None:
        """Create a new ``AWS::Pinpoint::App``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param name: ``AWS::Pinpoint::App.Name``.
        :param tags: ``AWS::Pinpoint::App.Tags``.
        """
        props = CfnAppProps(name=name, tags=tags)

        jsii.create(CfnApp, self, [scope, id, props])

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
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        """``AWS::Pinpoint::App.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-app.html#cfn-pinpoint-app-tags
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> str:
        """``AWS::Pinpoint::App.Name``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-app.html#cfn-pinpoint-app-name
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: str):
        return jsii.set(self, "name", value)


@jsii.data_type(jsii_type="@aws-cdk/aws-pinpoint.CfnAppProps", jsii_struct_bases=[], name_mapping={'name': 'name', 'tags': 'tags'})
class CfnAppProps():
    def __init__(self, *, name: str, tags: typing.Any=None):
        """Properties for defining a ``AWS::Pinpoint::App``.

        :param name: ``AWS::Pinpoint::App.Name``.
        :param tags: ``AWS::Pinpoint::App.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-app.html
        """
        self._values = {
            'name': name,
        }
        if tags is not None: self._values["tags"] = tags

    @property
    def name(self) -> str:
        """``AWS::Pinpoint::App.Name``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-app.html#cfn-pinpoint-app-name
        """
        return self._values.get('name')

    @property
    def tags(self) -> typing.Any:
        """``AWS::Pinpoint::App.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-app.html#cfn-pinpoint-app-tags
        """
        return self._values.get('tags')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnAppProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnApplicationSettings(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-pinpoint.CfnApplicationSettings"):
    """A CloudFormation ``AWS::Pinpoint::ApplicationSettings``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-applicationsettings.html
    cloudformationResource:
    :cloudformationResource:: AWS::Pinpoint::ApplicationSettings
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, application_id: str, campaign_hook: typing.Optional[typing.Union[typing.Optional["CampaignHookProperty"], typing.Optional[aws_cdk.core.IResolvable]]]=None, cloud_watch_metrics_enabled: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, limits: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["LimitsProperty"]]]=None, quiet_time: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["QuietTimeProperty"]]]=None) -> None:
        """Create a new ``AWS::Pinpoint::ApplicationSettings``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param application_id: ``AWS::Pinpoint::ApplicationSettings.ApplicationId``.
        :param campaign_hook: ``AWS::Pinpoint::ApplicationSettings.CampaignHook``.
        :param cloud_watch_metrics_enabled: ``AWS::Pinpoint::ApplicationSettings.CloudWatchMetricsEnabled``.
        :param limits: ``AWS::Pinpoint::ApplicationSettings.Limits``.
        :param quiet_time: ``AWS::Pinpoint::ApplicationSettings.QuietTime``.
        """
        props = CfnApplicationSettingsProps(application_id=application_id, campaign_hook=campaign_hook, cloud_watch_metrics_enabled=cloud_watch_metrics_enabled, limits=limits, quiet_time=quiet_time)

        jsii.create(CfnApplicationSettings, self, [scope, id, props])

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
    @jsii.member(jsii_name="applicationId")
    def application_id(self) -> str:
        """``AWS::Pinpoint::ApplicationSettings.ApplicationId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-applicationsettings.html#cfn-pinpoint-applicationsettings-applicationid
        """
        return jsii.get(self, "applicationId")

    @application_id.setter
    def application_id(self, value: str):
        return jsii.set(self, "applicationId", value)

    @property
    @jsii.member(jsii_name="campaignHook")
    def campaign_hook(self) -> typing.Optional[typing.Union[typing.Optional["CampaignHookProperty"], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::Pinpoint::ApplicationSettings.CampaignHook``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-applicationsettings.html#cfn-pinpoint-applicationsettings-campaignhook
        """
        return jsii.get(self, "campaignHook")

    @campaign_hook.setter
    def campaign_hook(self, value: typing.Optional[typing.Union[typing.Optional["CampaignHookProperty"], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "campaignHook", value)

    @property
    @jsii.member(jsii_name="cloudWatchMetricsEnabled")
    def cloud_watch_metrics_enabled(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::Pinpoint::ApplicationSettings.CloudWatchMetricsEnabled``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-applicationsettings.html#cfn-pinpoint-applicationsettings-cloudwatchmetricsenabled
        """
        return jsii.get(self, "cloudWatchMetricsEnabled")

    @cloud_watch_metrics_enabled.setter
    def cloud_watch_metrics_enabled(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "cloudWatchMetricsEnabled", value)

    @property
    @jsii.member(jsii_name="limits")
    def limits(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["LimitsProperty"]]]:
        """``AWS::Pinpoint::ApplicationSettings.Limits``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-applicationsettings.html#cfn-pinpoint-applicationsettings-limits
        """
        return jsii.get(self, "limits")

    @limits.setter
    def limits(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["LimitsProperty"]]]):
        return jsii.set(self, "limits", value)

    @property
    @jsii.member(jsii_name="quietTime")
    def quiet_time(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["QuietTimeProperty"]]]:
        """``AWS::Pinpoint::ApplicationSettings.QuietTime``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-applicationsettings.html#cfn-pinpoint-applicationsettings-quiettime
        """
        return jsii.get(self, "quietTime")

    @quiet_time.setter
    def quiet_time(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["QuietTimeProperty"]]]):
        return jsii.set(self, "quietTime", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-pinpoint.CfnApplicationSettings.CampaignHookProperty", jsii_struct_bases=[], name_mapping={'lambda_function_name': 'lambdaFunctionName', 'mode': 'mode', 'web_url': 'webUrl'})
    class CampaignHookProperty():
        def __init__(self, *, lambda_function_name: typing.Optional[str]=None, mode: typing.Optional[str]=None, web_url: typing.Optional[str]=None):
            """
            :param lambda_function_name: ``CfnApplicationSettings.CampaignHookProperty.LambdaFunctionName``.
            :param mode: ``CfnApplicationSettings.CampaignHookProperty.Mode``.
            :param web_url: ``CfnApplicationSettings.CampaignHookProperty.WebUrl``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-applicationsettings-campaignhook.html
            """
            self._values = {
            }
            if lambda_function_name is not None: self._values["lambda_function_name"] = lambda_function_name
            if mode is not None: self._values["mode"] = mode
            if web_url is not None: self._values["web_url"] = web_url

        @property
        def lambda_function_name(self) -> typing.Optional[str]:
            """``CfnApplicationSettings.CampaignHookProperty.LambdaFunctionName``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-applicationsettings-campaignhook.html#cfn-pinpoint-applicationsettings-campaignhook-lambdafunctionname
            """
            return self._values.get('lambda_function_name')

        @property
        def mode(self) -> typing.Optional[str]:
            """``CfnApplicationSettings.CampaignHookProperty.Mode``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-applicationsettings-campaignhook.html#cfn-pinpoint-applicationsettings-campaignhook-mode
            """
            return self._values.get('mode')

        @property
        def web_url(self) -> typing.Optional[str]:
            """``CfnApplicationSettings.CampaignHookProperty.WebUrl``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-applicationsettings-campaignhook.html#cfn-pinpoint-applicationsettings-campaignhook-weburl
            """
            return self._values.get('web_url')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'CampaignHookProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-pinpoint.CfnApplicationSettings.LimitsProperty", jsii_struct_bases=[], name_mapping={'daily': 'daily', 'maximum_duration': 'maximumDuration', 'messages_per_second': 'messagesPerSecond', 'total': 'total'})
    class LimitsProperty():
        def __init__(self, *, daily: typing.Optional[jsii.Number]=None, maximum_duration: typing.Optional[jsii.Number]=None, messages_per_second: typing.Optional[jsii.Number]=None, total: typing.Optional[jsii.Number]=None):
            """
            :param daily: ``CfnApplicationSettings.LimitsProperty.Daily``.
            :param maximum_duration: ``CfnApplicationSettings.LimitsProperty.MaximumDuration``.
            :param messages_per_second: ``CfnApplicationSettings.LimitsProperty.MessagesPerSecond``.
            :param total: ``CfnApplicationSettings.LimitsProperty.Total``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-applicationsettings-limits.html
            """
            self._values = {
            }
            if daily is not None: self._values["daily"] = daily
            if maximum_duration is not None: self._values["maximum_duration"] = maximum_duration
            if messages_per_second is not None: self._values["messages_per_second"] = messages_per_second
            if total is not None: self._values["total"] = total

        @property
        def daily(self) -> typing.Optional[jsii.Number]:
            """``CfnApplicationSettings.LimitsProperty.Daily``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-applicationsettings-limits.html#cfn-pinpoint-applicationsettings-limits-daily
            """
            return self._values.get('daily')

        @property
        def maximum_duration(self) -> typing.Optional[jsii.Number]:
            """``CfnApplicationSettings.LimitsProperty.MaximumDuration``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-applicationsettings-limits.html#cfn-pinpoint-applicationsettings-limits-maximumduration
            """
            return self._values.get('maximum_duration')

        @property
        def messages_per_second(self) -> typing.Optional[jsii.Number]:
            """``CfnApplicationSettings.LimitsProperty.MessagesPerSecond``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-applicationsettings-limits.html#cfn-pinpoint-applicationsettings-limits-messagespersecond
            """
            return self._values.get('messages_per_second')

        @property
        def total(self) -> typing.Optional[jsii.Number]:
            """``CfnApplicationSettings.LimitsProperty.Total``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-applicationsettings-limits.html#cfn-pinpoint-applicationsettings-limits-total
            """
            return self._values.get('total')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'LimitsProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-pinpoint.CfnApplicationSettings.QuietTimeProperty", jsii_struct_bases=[], name_mapping={'end': 'end', 'start': 'start'})
    class QuietTimeProperty():
        def __init__(self, *, end: str, start: str):
            """
            :param end: ``CfnApplicationSettings.QuietTimeProperty.End``.
            :param start: ``CfnApplicationSettings.QuietTimeProperty.Start``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-applicationsettings-quiettime.html
            """
            self._values = {
                'end': end,
                'start': start,
            }

        @property
        def end(self) -> str:
            """``CfnApplicationSettings.QuietTimeProperty.End``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-applicationsettings-quiettime.html#cfn-pinpoint-applicationsettings-quiettime-end
            """
            return self._values.get('end')

        @property
        def start(self) -> str:
            """``CfnApplicationSettings.QuietTimeProperty.Start``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-applicationsettings-quiettime.html#cfn-pinpoint-applicationsettings-quiettime-start
            """
            return self._values.get('start')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'QuietTimeProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



@jsii.data_type(jsii_type="@aws-cdk/aws-pinpoint.CfnApplicationSettingsProps", jsii_struct_bases=[], name_mapping={'application_id': 'applicationId', 'campaign_hook': 'campaignHook', 'cloud_watch_metrics_enabled': 'cloudWatchMetricsEnabled', 'limits': 'limits', 'quiet_time': 'quietTime'})
class CfnApplicationSettingsProps():
    def __init__(self, *, application_id: str, campaign_hook: typing.Optional[typing.Union[typing.Optional["CfnApplicationSettings.CampaignHookProperty"], typing.Optional[aws_cdk.core.IResolvable]]]=None, cloud_watch_metrics_enabled: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, limits: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnApplicationSettings.LimitsProperty"]]]=None, quiet_time: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnApplicationSettings.QuietTimeProperty"]]]=None):
        """Properties for defining a ``AWS::Pinpoint::ApplicationSettings``.

        :param application_id: ``AWS::Pinpoint::ApplicationSettings.ApplicationId``.
        :param campaign_hook: ``AWS::Pinpoint::ApplicationSettings.CampaignHook``.
        :param cloud_watch_metrics_enabled: ``AWS::Pinpoint::ApplicationSettings.CloudWatchMetricsEnabled``.
        :param limits: ``AWS::Pinpoint::ApplicationSettings.Limits``.
        :param quiet_time: ``AWS::Pinpoint::ApplicationSettings.QuietTime``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-applicationsettings.html
        """
        self._values = {
            'application_id': application_id,
        }
        if campaign_hook is not None: self._values["campaign_hook"] = campaign_hook
        if cloud_watch_metrics_enabled is not None: self._values["cloud_watch_metrics_enabled"] = cloud_watch_metrics_enabled
        if limits is not None: self._values["limits"] = limits
        if quiet_time is not None: self._values["quiet_time"] = quiet_time

    @property
    def application_id(self) -> str:
        """``AWS::Pinpoint::ApplicationSettings.ApplicationId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-applicationsettings.html#cfn-pinpoint-applicationsettings-applicationid
        """
        return self._values.get('application_id')

    @property
    def campaign_hook(self) -> typing.Optional[typing.Union[typing.Optional["CfnApplicationSettings.CampaignHookProperty"], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::Pinpoint::ApplicationSettings.CampaignHook``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-applicationsettings.html#cfn-pinpoint-applicationsettings-campaignhook
        """
        return self._values.get('campaign_hook')

    @property
    def cloud_watch_metrics_enabled(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::Pinpoint::ApplicationSettings.CloudWatchMetricsEnabled``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-applicationsettings.html#cfn-pinpoint-applicationsettings-cloudwatchmetricsenabled
        """
        return self._values.get('cloud_watch_metrics_enabled')

    @property
    def limits(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnApplicationSettings.LimitsProperty"]]]:
        """``AWS::Pinpoint::ApplicationSettings.Limits``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-applicationsettings.html#cfn-pinpoint-applicationsettings-limits
        """
        return self._values.get('limits')

    @property
    def quiet_time(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnApplicationSettings.QuietTimeProperty"]]]:
        """``AWS::Pinpoint::ApplicationSettings.QuietTime``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-applicationsettings.html#cfn-pinpoint-applicationsettings-quiettime
        """
        return self._values.get('quiet_time')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnApplicationSettingsProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnBaiduChannel(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-pinpoint.CfnBaiduChannel"):
    """A CloudFormation ``AWS::Pinpoint::BaiduChannel``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-baiduchannel.html
    cloudformationResource:
    :cloudformationResource:: AWS::Pinpoint::BaiduChannel
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, api_key: str, application_id: str, secret_key: str, enabled: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None) -> None:
        """Create a new ``AWS::Pinpoint::BaiduChannel``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param api_key: ``AWS::Pinpoint::BaiduChannel.ApiKey``.
        :param application_id: ``AWS::Pinpoint::BaiduChannel.ApplicationId``.
        :param secret_key: ``AWS::Pinpoint::BaiduChannel.SecretKey``.
        :param enabled: ``AWS::Pinpoint::BaiduChannel.Enabled``.
        """
        props = CfnBaiduChannelProps(api_key=api_key, application_id=application_id, secret_key=secret_key, enabled=enabled)

        jsii.create(CfnBaiduChannel, self, [scope, id, props])

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
    @jsii.member(jsii_name="apiKey")
    def api_key(self) -> str:
        """``AWS::Pinpoint::BaiduChannel.ApiKey``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-baiduchannel.html#cfn-pinpoint-baiduchannel-apikey
        """
        return jsii.get(self, "apiKey")

    @api_key.setter
    def api_key(self, value: str):
        return jsii.set(self, "apiKey", value)

    @property
    @jsii.member(jsii_name="applicationId")
    def application_id(self) -> str:
        """``AWS::Pinpoint::BaiduChannel.ApplicationId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-baiduchannel.html#cfn-pinpoint-baiduchannel-applicationid
        """
        return jsii.get(self, "applicationId")

    @application_id.setter
    def application_id(self, value: str):
        return jsii.set(self, "applicationId", value)

    @property
    @jsii.member(jsii_name="secretKey")
    def secret_key(self) -> str:
        """``AWS::Pinpoint::BaiduChannel.SecretKey``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-baiduchannel.html#cfn-pinpoint-baiduchannel-secretkey
        """
        return jsii.get(self, "secretKey")

    @secret_key.setter
    def secret_key(self, value: str):
        return jsii.set(self, "secretKey", value)

    @property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::Pinpoint::BaiduChannel.Enabled``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-baiduchannel.html#cfn-pinpoint-baiduchannel-enabled
        """
        return jsii.get(self, "enabled")

    @enabled.setter
    def enabled(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "enabled", value)


@jsii.data_type(jsii_type="@aws-cdk/aws-pinpoint.CfnBaiduChannelProps", jsii_struct_bases=[], name_mapping={'api_key': 'apiKey', 'application_id': 'applicationId', 'secret_key': 'secretKey', 'enabled': 'enabled'})
class CfnBaiduChannelProps():
    def __init__(self, *, api_key: str, application_id: str, secret_key: str, enabled: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None):
        """Properties for defining a ``AWS::Pinpoint::BaiduChannel``.

        :param api_key: ``AWS::Pinpoint::BaiduChannel.ApiKey``.
        :param application_id: ``AWS::Pinpoint::BaiduChannel.ApplicationId``.
        :param secret_key: ``AWS::Pinpoint::BaiduChannel.SecretKey``.
        :param enabled: ``AWS::Pinpoint::BaiduChannel.Enabled``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-baiduchannel.html
        """
        self._values = {
            'api_key': api_key,
            'application_id': application_id,
            'secret_key': secret_key,
        }
        if enabled is not None: self._values["enabled"] = enabled

    @property
    def api_key(self) -> str:
        """``AWS::Pinpoint::BaiduChannel.ApiKey``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-baiduchannel.html#cfn-pinpoint-baiduchannel-apikey
        """
        return self._values.get('api_key')

    @property
    def application_id(self) -> str:
        """``AWS::Pinpoint::BaiduChannel.ApplicationId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-baiduchannel.html#cfn-pinpoint-baiduchannel-applicationid
        """
        return self._values.get('application_id')

    @property
    def secret_key(self) -> str:
        """``AWS::Pinpoint::BaiduChannel.SecretKey``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-baiduchannel.html#cfn-pinpoint-baiduchannel-secretkey
        """
        return self._values.get('secret_key')

    @property
    def enabled(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::Pinpoint::BaiduChannel.Enabled``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-baiduchannel.html#cfn-pinpoint-baiduchannel-enabled
        """
        return self._values.get('enabled')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnBaiduChannelProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnCampaign(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-pinpoint.CfnCampaign"):
    """A CloudFormation ``AWS::Pinpoint::Campaign``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-campaign.html
    cloudformationResource:
    :cloudformationResource:: AWS::Pinpoint::Campaign
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, application_id: str, message_configuration: typing.Union[aws_cdk.core.IResolvable, "MessageConfigurationProperty"], name: str, schedule: typing.Union[aws_cdk.core.IResolvable, "ScheduleProperty"], segment_id: str, additional_treatments: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "WriteTreatmentResourceProperty"]]]]]=None, campaign_hook: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CampaignHookProperty"]]]=None, description: typing.Optional[str]=None, holdout_percent: typing.Optional[jsii.Number]=None, is_paused: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, limits: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["LimitsProperty"]]]=None, segment_version: typing.Optional[jsii.Number]=None, tags: typing.Any=None, treatment_description: typing.Optional[str]=None, treatment_name: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::Pinpoint::Campaign``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param application_id: ``AWS::Pinpoint::Campaign.ApplicationId``.
        :param message_configuration: ``AWS::Pinpoint::Campaign.MessageConfiguration``.
        :param name: ``AWS::Pinpoint::Campaign.Name``.
        :param schedule: ``AWS::Pinpoint::Campaign.Schedule``.
        :param segment_id: ``AWS::Pinpoint::Campaign.SegmentId``.
        :param additional_treatments: ``AWS::Pinpoint::Campaign.AdditionalTreatments``.
        :param campaign_hook: ``AWS::Pinpoint::Campaign.CampaignHook``.
        :param description: ``AWS::Pinpoint::Campaign.Description``.
        :param holdout_percent: ``AWS::Pinpoint::Campaign.HoldoutPercent``.
        :param is_paused: ``AWS::Pinpoint::Campaign.IsPaused``.
        :param limits: ``AWS::Pinpoint::Campaign.Limits``.
        :param segment_version: ``AWS::Pinpoint::Campaign.SegmentVersion``.
        :param tags: ``AWS::Pinpoint::Campaign.Tags``.
        :param treatment_description: ``AWS::Pinpoint::Campaign.TreatmentDescription``.
        :param treatment_name: ``AWS::Pinpoint::Campaign.TreatmentName``.
        """
        props = CfnCampaignProps(application_id=application_id, message_configuration=message_configuration, name=name, schedule=schedule, segment_id=segment_id, additional_treatments=additional_treatments, campaign_hook=campaign_hook, description=description, holdout_percent=holdout_percent, is_paused=is_paused, limits=limits, segment_version=segment_version, tags=tags, treatment_description=treatment_description, treatment_name=treatment_name)

        jsii.create(CfnCampaign, self, [scope, id, props])

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
    @jsii.member(jsii_name="attrCampaignId")
    def attr_campaign_id(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: CampaignId
        """
        return jsii.get(self, "attrCampaignId")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        """``AWS::Pinpoint::Campaign.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-campaign.html#cfn-pinpoint-campaign-tags
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="applicationId")
    def application_id(self) -> str:
        """``AWS::Pinpoint::Campaign.ApplicationId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-campaign.html#cfn-pinpoint-campaign-applicationid
        """
        return jsii.get(self, "applicationId")

    @application_id.setter
    def application_id(self, value: str):
        return jsii.set(self, "applicationId", value)

    @property
    @jsii.member(jsii_name="messageConfiguration")
    def message_configuration(self) -> typing.Union[aws_cdk.core.IResolvable, "MessageConfigurationProperty"]:
        """``AWS::Pinpoint::Campaign.MessageConfiguration``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-campaign.html#cfn-pinpoint-campaign-messageconfiguration
        """
        return jsii.get(self, "messageConfiguration")

    @message_configuration.setter
    def message_configuration(self, value: typing.Union[aws_cdk.core.IResolvable, "MessageConfigurationProperty"]):
        return jsii.set(self, "messageConfiguration", value)

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> str:
        """``AWS::Pinpoint::Campaign.Name``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-campaign.html#cfn-pinpoint-campaign-name
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: str):
        return jsii.set(self, "name", value)

    @property
    @jsii.member(jsii_name="schedule")
    def schedule(self) -> typing.Union[aws_cdk.core.IResolvable, "ScheduleProperty"]:
        """``AWS::Pinpoint::Campaign.Schedule``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-campaign.html#cfn-pinpoint-campaign-schedule
        """
        return jsii.get(self, "schedule")

    @schedule.setter
    def schedule(self, value: typing.Union[aws_cdk.core.IResolvable, "ScheduleProperty"]):
        return jsii.set(self, "schedule", value)

    @property
    @jsii.member(jsii_name="segmentId")
    def segment_id(self) -> str:
        """``AWS::Pinpoint::Campaign.SegmentId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-campaign.html#cfn-pinpoint-campaign-segmentid
        """
        return jsii.get(self, "segmentId")

    @segment_id.setter
    def segment_id(self, value: str):
        return jsii.set(self, "segmentId", value)

    @property
    @jsii.member(jsii_name="additionalTreatments")
    def additional_treatments(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "WriteTreatmentResourceProperty"]]]]]:
        """``AWS::Pinpoint::Campaign.AdditionalTreatments``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-campaign.html#cfn-pinpoint-campaign-additionaltreatments
        """
        return jsii.get(self, "additionalTreatments")

    @additional_treatments.setter
    def additional_treatments(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "WriteTreatmentResourceProperty"]]]]]):
        return jsii.set(self, "additionalTreatments", value)

    @property
    @jsii.member(jsii_name="campaignHook")
    def campaign_hook(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CampaignHookProperty"]]]:
        """``AWS::Pinpoint::Campaign.CampaignHook``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-campaign.html#cfn-pinpoint-campaign-campaignhook
        """
        return jsii.get(self, "campaignHook")

    @campaign_hook.setter
    def campaign_hook(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CampaignHookProperty"]]]):
        return jsii.set(self, "campaignHook", value)

    @property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::Campaign.Description``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-campaign.html#cfn-pinpoint-campaign-description
        """
        return jsii.get(self, "description")

    @description.setter
    def description(self, value: typing.Optional[str]):
        return jsii.set(self, "description", value)

    @property
    @jsii.member(jsii_name="holdoutPercent")
    def holdout_percent(self) -> typing.Optional[jsii.Number]:
        """``AWS::Pinpoint::Campaign.HoldoutPercent``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-campaign.html#cfn-pinpoint-campaign-holdoutpercent
        """
        return jsii.get(self, "holdoutPercent")

    @holdout_percent.setter
    def holdout_percent(self, value: typing.Optional[jsii.Number]):
        return jsii.set(self, "holdoutPercent", value)

    @property
    @jsii.member(jsii_name="isPaused")
    def is_paused(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::Pinpoint::Campaign.IsPaused``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-campaign.html#cfn-pinpoint-campaign-ispaused
        """
        return jsii.get(self, "isPaused")

    @is_paused.setter
    def is_paused(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "isPaused", value)

    @property
    @jsii.member(jsii_name="limits")
    def limits(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["LimitsProperty"]]]:
        """``AWS::Pinpoint::Campaign.Limits``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-campaign.html#cfn-pinpoint-campaign-limits
        """
        return jsii.get(self, "limits")

    @limits.setter
    def limits(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["LimitsProperty"]]]):
        return jsii.set(self, "limits", value)

    @property
    @jsii.member(jsii_name="segmentVersion")
    def segment_version(self) -> typing.Optional[jsii.Number]:
        """``AWS::Pinpoint::Campaign.SegmentVersion``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-campaign.html#cfn-pinpoint-campaign-segmentversion
        """
        return jsii.get(self, "segmentVersion")

    @segment_version.setter
    def segment_version(self, value: typing.Optional[jsii.Number]):
        return jsii.set(self, "segmentVersion", value)

    @property
    @jsii.member(jsii_name="treatmentDescription")
    def treatment_description(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::Campaign.TreatmentDescription``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-campaign.html#cfn-pinpoint-campaign-treatmentdescription
        """
        return jsii.get(self, "treatmentDescription")

    @treatment_description.setter
    def treatment_description(self, value: typing.Optional[str]):
        return jsii.set(self, "treatmentDescription", value)

    @property
    @jsii.member(jsii_name="treatmentName")
    def treatment_name(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::Campaign.TreatmentName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-campaign.html#cfn-pinpoint-campaign-treatmentname
        """
        return jsii.get(self, "treatmentName")

    @treatment_name.setter
    def treatment_name(self, value: typing.Optional[str]):
        return jsii.set(self, "treatmentName", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-pinpoint.CfnCampaign.AttributeDimensionProperty", jsii_struct_bases=[], name_mapping={'attribute_type': 'attributeType', 'values': 'values'})
    class AttributeDimensionProperty():
        def __init__(self, *, attribute_type: typing.Optional[str]=None, values: typing.Optional[typing.List[str]]=None):
            """
            :param attribute_type: ``CfnCampaign.AttributeDimensionProperty.AttributeType``.
            :param values: ``CfnCampaign.AttributeDimensionProperty.Values``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-attributedimension.html
            """
            self._values = {
            }
            if attribute_type is not None: self._values["attribute_type"] = attribute_type
            if values is not None: self._values["values"] = values

        @property
        def attribute_type(self) -> typing.Optional[str]:
            """``CfnCampaign.AttributeDimensionProperty.AttributeType``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-attributedimension.html#cfn-pinpoint-campaign-attributedimension-attributetype
            """
            return self._values.get('attribute_type')

        @property
        def values(self) -> typing.Optional[typing.List[str]]:
            """``CfnCampaign.AttributeDimensionProperty.Values``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-attributedimension.html#cfn-pinpoint-campaign-attributedimension-values
            """
            return self._values.get('values')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'AttributeDimensionProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-pinpoint.CfnCampaign.CampaignEmailMessageProperty", jsii_struct_bases=[], name_mapping={'body': 'body', 'from_address': 'fromAddress', 'html_body': 'htmlBody', 'title': 'title'})
    class CampaignEmailMessageProperty():
        def __init__(self, *, body: typing.Optional[str]=None, from_address: typing.Optional[str]=None, html_body: typing.Optional[str]=None, title: typing.Optional[str]=None):
            """
            :param body: ``CfnCampaign.CampaignEmailMessageProperty.Body``.
            :param from_address: ``CfnCampaign.CampaignEmailMessageProperty.FromAddress``.
            :param html_body: ``CfnCampaign.CampaignEmailMessageProperty.HtmlBody``.
            :param title: ``CfnCampaign.CampaignEmailMessageProperty.Title``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-campaignemailmessage.html
            """
            self._values = {
            }
            if body is not None: self._values["body"] = body
            if from_address is not None: self._values["from_address"] = from_address
            if html_body is not None: self._values["html_body"] = html_body
            if title is not None: self._values["title"] = title

        @property
        def body(self) -> typing.Optional[str]:
            """``CfnCampaign.CampaignEmailMessageProperty.Body``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-campaignemailmessage.html#cfn-pinpoint-campaign-campaignemailmessage-body
            """
            return self._values.get('body')

        @property
        def from_address(self) -> typing.Optional[str]:
            """``CfnCampaign.CampaignEmailMessageProperty.FromAddress``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-campaignemailmessage.html#cfn-pinpoint-campaign-campaignemailmessage-fromaddress
            """
            return self._values.get('from_address')

        @property
        def html_body(self) -> typing.Optional[str]:
            """``CfnCampaign.CampaignEmailMessageProperty.HtmlBody``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-campaignemailmessage.html#cfn-pinpoint-campaign-campaignemailmessage-htmlbody
            """
            return self._values.get('html_body')

        @property
        def title(self) -> typing.Optional[str]:
            """``CfnCampaign.CampaignEmailMessageProperty.Title``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-campaignemailmessage.html#cfn-pinpoint-campaign-campaignemailmessage-title
            """
            return self._values.get('title')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'CampaignEmailMessageProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-pinpoint.CfnCampaign.CampaignEventFilterProperty", jsii_struct_bases=[], name_mapping={'dimensions': 'dimensions', 'filter_type': 'filterType'})
    class CampaignEventFilterProperty():
        def __init__(self, *, dimensions: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnCampaign.EventDimensionsProperty"]]]=None, filter_type: typing.Optional[str]=None):
            """
            :param dimensions: ``CfnCampaign.CampaignEventFilterProperty.Dimensions``.
            :param filter_type: ``CfnCampaign.CampaignEventFilterProperty.FilterType``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-campaigneventfilter.html
            """
            self._values = {
            }
            if dimensions is not None: self._values["dimensions"] = dimensions
            if filter_type is not None: self._values["filter_type"] = filter_type

        @property
        def dimensions(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnCampaign.EventDimensionsProperty"]]]:
            """``CfnCampaign.CampaignEventFilterProperty.Dimensions``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-campaigneventfilter.html#cfn-pinpoint-campaign-campaigneventfilter-dimensions
            """
            return self._values.get('dimensions')

        @property
        def filter_type(self) -> typing.Optional[str]:
            """``CfnCampaign.CampaignEventFilterProperty.FilterType``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-campaigneventfilter.html#cfn-pinpoint-campaign-campaigneventfilter-filtertype
            """
            return self._values.get('filter_type')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'CampaignEventFilterProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-pinpoint.CfnCampaign.CampaignHookProperty", jsii_struct_bases=[], name_mapping={'lambda_function_name': 'lambdaFunctionName', 'mode': 'mode', 'web_url': 'webUrl'})
    class CampaignHookProperty():
        def __init__(self, *, lambda_function_name: typing.Optional[str]=None, mode: typing.Optional[str]=None, web_url: typing.Optional[str]=None):
            """
            :param lambda_function_name: ``CfnCampaign.CampaignHookProperty.LambdaFunctionName``.
            :param mode: ``CfnCampaign.CampaignHookProperty.Mode``.
            :param web_url: ``CfnCampaign.CampaignHookProperty.WebUrl``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-campaignhook.html
            """
            self._values = {
            }
            if lambda_function_name is not None: self._values["lambda_function_name"] = lambda_function_name
            if mode is not None: self._values["mode"] = mode
            if web_url is not None: self._values["web_url"] = web_url

        @property
        def lambda_function_name(self) -> typing.Optional[str]:
            """``CfnCampaign.CampaignHookProperty.LambdaFunctionName``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-campaignhook.html#cfn-pinpoint-campaign-campaignhook-lambdafunctionname
            """
            return self._values.get('lambda_function_name')

        @property
        def mode(self) -> typing.Optional[str]:
            """``CfnCampaign.CampaignHookProperty.Mode``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-campaignhook.html#cfn-pinpoint-campaign-campaignhook-mode
            """
            return self._values.get('mode')

        @property
        def web_url(self) -> typing.Optional[str]:
            """``CfnCampaign.CampaignHookProperty.WebUrl``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-campaignhook.html#cfn-pinpoint-campaign-campaignhook-weburl
            """
            return self._values.get('web_url')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'CampaignHookProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-pinpoint.CfnCampaign.CampaignSmsMessageProperty", jsii_struct_bases=[], name_mapping={'body': 'body', 'message_type': 'messageType', 'sender_id': 'senderId'})
    class CampaignSmsMessageProperty():
        def __init__(self, *, body: typing.Optional[str]=None, message_type: typing.Optional[str]=None, sender_id: typing.Optional[str]=None):
            """
            :param body: ``CfnCampaign.CampaignSmsMessageProperty.Body``.
            :param message_type: ``CfnCampaign.CampaignSmsMessageProperty.MessageType``.
            :param sender_id: ``CfnCampaign.CampaignSmsMessageProperty.SenderId``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-campaignsmsmessage.html
            """
            self._values = {
            }
            if body is not None: self._values["body"] = body
            if message_type is not None: self._values["message_type"] = message_type
            if sender_id is not None: self._values["sender_id"] = sender_id

        @property
        def body(self) -> typing.Optional[str]:
            """``CfnCampaign.CampaignSmsMessageProperty.Body``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-campaignsmsmessage.html#cfn-pinpoint-campaign-campaignsmsmessage-body
            """
            return self._values.get('body')

        @property
        def message_type(self) -> typing.Optional[str]:
            """``CfnCampaign.CampaignSmsMessageProperty.MessageType``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-campaignsmsmessage.html#cfn-pinpoint-campaign-campaignsmsmessage-messagetype
            """
            return self._values.get('message_type')

        @property
        def sender_id(self) -> typing.Optional[str]:
            """``CfnCampaign.CampaignSmsMessageProperty.SenderId``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-campaignsmsmessage.html#cfn-pinpoint-campaign-campaignsmsmessage-senderid
            """
            return self._values.get('sender_id')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'CampaignSmsMessageProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-pinpoint.CfnCampaign.EventDimensionsProperty", jsii_struct_bases=[], name_mapping={'attributes': 'attributes', 'event_type': 'eventType', 'metrics': 'metrics'})
    class EventDimensionsProperty():
        def __init__(self, *, attributes: typing.Any=None, event_type: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnCampaign.SetDimensionProperty"]]]=None, metrics: typing.Any=None):
            """
            :param attributes: ``CfnCampaign.EventDimensionsProperty.Attributes``.
            :param event_type: ``CfnCampaign.EventDimensionsProperty.EventType``.
            :param metrics: ``CfnCampaign.EventDimensionsProperty.Metrics``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-eventdimensions.html
            """
            self._values = {
            }
            if attributes is not None: self._values["attributes"] = attributes
            if event_type is not None: self._values["event_type"] = event_type
            if metrics is not None: self._values["metrics"] = metrics

        @property
        def attributes(self) -> typing.Any:
            """``CfnCampaign.EventDimensionsProperty.Attributes``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-eventdimensions.html#cfn-pinpoint-campaign-eventdimensions-attributes
            """
            return self._values.get('attributes')

        @property
        def event_type(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnCampaign.SetDimensionProperty"]]]:
            """``CfnCampaign.EventDimensionsProperty.EventType``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-eventdimensions.html#cfn-pinpoint-campaign-eventdimensions-eventtype
            """
            return self._values.get('event_type')

        @property
        def metrics(self) -> typing.Any:
            """``CfnCampaign.EventDimensionsProperty.Metrics``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-eventdimensions.html#cfn-pinpoint-campaign-eventdimensions-metrics
            """
            return self._values.get('metrics')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'EventDimensionsProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-pinpoint.CfnCampaign.LimitsProperty", jsii_struct_bases=[], name_mapping={'daily': 'daily', 'maximum_duration': 'maximumDuration', 'messages_per_second': 'messagesPerSecond', 'total': 'total'})
    class LimitsProperty():
        def __init__(self, *, daily: typing.Optional[jsii.Number]=None, maximum_duration: typing.Optional[jsii.Number]=None, messages_per_second: typing.Optional[jsii.Number]=None, total: typing.Optional[jsii.Number]=None):
            """
            :param daily: ``CfnCampaign.LimitsProperty.Daily``.
            :param maximum_duration: ``CfnCampaign.LimitsProperty.MaximumDuration``.
            :param messages_per_second: ``CfnCampaign.LimitsProperty.MessagesPerSecond``.
            :param total: ``CfnCampaign.LimitsProperty.Total``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-limits.html
            """
            self._values = {
            }
            if daily is not None: self._values["daily"] = daily
            if maximum_duration is not None: self._values["maximum_duration"] = maximum_duration
            if messages_per_second is not None: self._values["messages_per_second"] = messages_per_second
            if total is not None: self._values["total"] = total

        @property
        def daily(self) -> typing.Optional[jsii.Number]:
            """``CfnCampaign.LimitsProperty.Daily``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-limits.html#cfn-pinpoint-campaign-limits-daily
            """
            return self._values.get('daily')

        @property
        def maximum_duration(self) -> typing.Optional[jsii.Number]:
            """``CfnCampaign.LimitsProperty.MaximumDuration``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-limits.html#cfn-pinpoint-campaign-limits-maximumduration
            """
            return self._values.get('maximum_duration')

        @property
        def messages_per_second(self) -> typing.Optional[jsii.Number]:
            """``CfnCampaign.LimitsProperty.MessagesPerSecond``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-limits.html#cfn-pinpoint-campaign-limits-messagespersecond
            """
            return self._values.get('messages_per_second')

        @property
        def total(self) -> typing.Optional[jsii.Number]:
            """``CfnCampaign.LimitsProperty.Total``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-limits.html#cfn-pinpoint-campaign-limits-total
            """
            return self._values.get('total')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'LimitsProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-pinpoint.CfnCampaign.MessageConfigurationProperty", jsii_struct_bases=[], name_mapping={'adm_message': 'admMessage', 'apns_message': 'apnsMessage', 'baidu_message': 'baiduMessage', 'default_message': 'defaultMessage', 'email_message': 'emailMessage', 'gcm_message': 'gcmMessage', 'sms_message': 'smsMessage'})
    class MessageConfigurationProperty():
        def __init__(self, *, adm_message: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnCampaign.MessageProperty"]]]=None, apns_message: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnCampaign.MessageProperty"]]]=None, baidu_message: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnCampaign.MessageProperty"]]]=None, default_message: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnCampaign.MessageProperty"]]]=None, email_message: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnCampaign.CampaignEmailMessageProperty"]]]=None, gcm_message: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnCampaign.MessageProperty"]]]=None, sms_message: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnCampaign.CampaignSmsMessageProperty"]]]=None):
            """
            :param adm_message: ``CfnCampaign.MessageConfigurationProperty.ADMMessage``.
            :param apns_message: ``CfnCampaign.MessageConfigurationProperty.APNSMessage``.
            :param baidu_message: ``CfnCampaign.MessageConfigurationProperty.BaiduMessage``.
            :param default_message: ``CfnCampaign.MessageConfigurationProperty.DefaultMessage``.
            :param email_message: ``CfnCampaign.MessageConfigurationProperty.EmailMessage``.
            :param gcm_message: ``CfnCampaign.MessageConfigurationProperty.GCMMessage``.
            :param sms_message: ``CfnCampaign.MessageConfigurationProperty.SMSMessage``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-messageconfiguration.html
            """
            self._values = {
            }
            if adm_message is not None: self._values["adm_message"] = adm_message
            if apns_message is not None: self._values["apns_message"] = apns_message
            if baidu_message is not None: self._values["baidu_message"] = baidu_message
            if default_message is not None: self._values["default_message"] = default_message
            if email_message is not None: self._values["email_message"] = email_message
            if gcm_message is not None: self._values["gcm_message"] = gcm_message
            if sms_message is not None: self._values["sms_message"] = sms_message

        @property
        def adm_message(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnCampaign.MessageProperty"]]]:
            """``CfnCampaign.MessageConfigurationProperty.ADMMessage``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-messageconfiguration.html#cfn-pinpoint-campaign-messageconfiguration-admmessage
            """
            return self._values.get('adm_message')

        @property
        def apns_message(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnCampaign.MessageProperty"]]]:
            """``CfnCampaign.MessageConfigurationProperty.APNSMessage``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-messageconfiguration.html#cfn-pinpoint-campaign-messageconfiguration-apnsmessage
            """
            return self._values.get('apns_message')

        @property
        def baidu_message(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnCampaign.MessageProperty"]]]:
            """``CfnCampaign.MessageConfigurationProperty.BaiduMessage``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-messageconfiguration.html#cfn-pinpoint-campaign-messageconfiguration-baidumessage
            """
            return self._values.get('baidu_message')

        @property
        def default_message(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnCampaign.MessageProperty"]]]:
            """``CfnCampaign.MessageConfigurationProperty.DefaultMessage``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-messageconfiguration.html#cfn-pinpoint-campaign-messageconfiguration-defaultmessage
            """
            return self._values.get('default_message')

        @property
        def email_message(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnCampaign.CampaignEmailMessageProperty"]]]:
            """``CfnCampaign.MessageConfigurationProperty.EmailMessage``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-messageconfiguration.html#cfn-pinpoint-campaign-messageconfiguration-emailmessage
            """
            return self._values.get('email_message')

        @property
        def gcm_message(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnCampaign.MessageProperty"]]]:
            """``CfnCampaign.MessageConfigurationProperty.GCMMessage``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-messageconfiguration.html#cfn-pinpoint-campaign-messageconfiguration-gcmmessage
            """
            return self._values.get('gcm_message')

        @property
        def sms_message(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnCampaign.CampaignSmsMessageProperty"]]]:
            """``CfnCampaign.MessageConfigurationProperty.SMSMessage``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-messageconfiguration.html#cfn-pinpoint-campaign-messageconfiguration-smsmessage
            """
            return self._values.get('sms_message')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'MessageConfigurationProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-pinpoint.CfnCampaign.MessageProperty", jsii_struct_bases=[], name_mapping={'action': 'action', 'body': 'body', 'image_icon_url': 'imageIconUrl', 'image_small_icon_url': 'imageSmallIconUrl', 'image_url': 'imageUrl', 'json_body': 'jsonBody', 'media_url': 'mediaUrl', 'raw_content': 'rawContent', 'silent_push': 'silentPush', 'time_to_live': 'timeToLive', 'title': 'title', 'url': 'url'})
    class MessageProperty():
        def __init__(self, *, action: typing.Optional[str]=None, body: typing.Optional[str]=None, image_icon_url: typing.Optional[str]=None, image_small_icon_url: typing.Optional[str]=None, image_url: typing.Optional[str]=None, json_body: typing.Optional[str]=None, media_url: typing.Optional[str]=None, raw_content: typing.Optional[str]=None, silent_push: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, time_to_live: typing.Optional[jsii.Number]=None, title: typing.Optional[str]=None, url: typing.Optional[str]=None):
            """
            :param action: ``CfnCampaign.MessageProperty.Action``.
            :param body: ``CfnCampaign.MessageProperty.Body``.
            :param image_icon_url: ``CfnCampaign.MessageProperty.ImageIconUrl``.
            :param image_small_icon_url: ``CfnCampaign.MessageProperty.ImageSmallIconUrl``.
            :param image_url: ``CfnCampaign.MessageProperty.ImageUrl``.
            :param json_body: ``CfnCampaign.MessageProperty.JsonBody``.
            :param media_url: ``CfnCampaign.MessageProperty.MediaUrl``.
            :param raw_content: ``CfnCampaign.MessageProperty.RawContent``.
            :param silent_push: ``CfnCampaign.MessageProperty.SilentPush``.
            :param time_to_live: ``CfnCampaign.MessageProperty.TimeToLive``.
            :param title: ``CfnCampaign.MessageProperty.Title``.
            :param url: ``CfnCampaign.MessageProperty.Url``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-message.html
            """
            self._values = {
            }
            if action is not None: self._values["action"] = action
            if body is not None: self._values["body"] = body
            if image_icon_url is not None: self._values["image_icon_url"] = image_icon_url
            if image_small_icon_url is not None: self._values["image_small_icon_url"] = image_small_icon_url
            if image_url is not None: self._values["image_url"] = image_url
            if json_body is not None: self._values["json_body"] = json_body
            if media_url is not None: self._values["media_url"] = media_url
            if raw_content is not None: self._values["raw_content"] = raw_content
            if silent_push is not None: self._values["silent_push"] = silent_push
            if time_to_live is not None: self._values["time_to_live"] = time_to_live
            if title is not None: self._values["title"] = title
            if url is not None: self._values["url"] = url

        @property
        def action(self) -> typing.Optional[str]:
            """``CfnCampaign.MessageProperty.Action``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-message.html#cfn-pinpoint-campaign-message-action
            """
            return self._values.get('action')

        @property
        def body(self) -> typing.Optional[str]:
            """``CfnCampaign.MessageProperty.Body``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-message.html#cfn-pinpoint-campaign-message-body
            """
            return self._values.get('body')

        @property
        def image_icon_url(self) -> typing.Optional[str]:
            """``CfnCampaign.MessageProperty.ImageIconUrl``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-message.html#cfn-pinpoint-campaign-message-imageiconurl
            """
            return self._values.get('image_icon_url')

        @property
        def image_small_icon_url(self) -> typing.Optional[str]:
            """``CfnCampaign.MessageProperty.ImageSmallIconUrl``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-message.html#cfn-pinpoint-campaign-message-imagesmalliconurl
            """
            return self._values.get('image_small_icon_url')

        @property
        def image_url(self) -> typing.Optional[str]:
            """``CfnCampaign.MessageProperty.ImageUrl``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-message.html#cfn-pinpoint-campaign-message-imageurl
            """
            return self._values.get('image_url')

        @property
        def json_body(self) -> typing.Optional[str]:
            """``CfnCampaign.MessageProperty.JsonBody``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-message.html#cfn-pinpoint-campaign-message-jsonbody
            """
            return self._values.get('json_body')

        @property
        def media_url(self) -> typing.Optional[str]:
            """``CfnCampaign.MessageProperty.MediaUrl``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-message.html#cfn-pinpoint-campaign-message-mediaurl
            """
            return self._values.get('media_url')

        @property
        def raw_content(self) -> typing.Optional[str]:
            """``CfnCampaign.MessageProperty.RawContent``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-message.html#cfn-pinpoint-campaign-message-rawcontent
            """
            return self._values.get('raw_content')

        @property
        def silent_push(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
            """``CfnCampaign.MessageProperty.SilentPush``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-message.html#cfn-pinpoint-campaign-message-silentpush
            """
            return self._values.get('silent_push')

        @property
        def time_to_live(self) -> typing.Optional[jsii.Number]:
            """``CfnCampaign.MessageProperty.TimeToLive``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-message.html#cfn-pinpoint-campaign-message-timetolive
            """
            return self._values.get('time_to_live')

        @property
        def title(self) -> typing.Optional[str]:
            """``CfnCampaign.MessageProperty.Title``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-message.html#cfn-pinpoint-campaign-message-title
            """
            return self._values.get('title')

        @property
        def url(self) -> typing.Optional[str]:
            """``CfnCampaign.MessageProperty.Url``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-message.html#cfn-pinpoint-campaign-message-url
            """
            return self._values.get('url')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'MessageProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-pinpoint.CfnCampaign.MetricDimensionProperty", jsii_struct_bases=[], name_mapping={'comparison_operator': 'comparisonOperator', 'value': 'value'})
    class MetricDimensionProperty():
        def __init__(self, *, comparison_operator: typing.Optional[str]=None, value: typing.Optional[jsii.Number]=None):
            """
            :param comparison_operator: ``CfnCampaign.MetricDimensionProperty.ComparisonOperator``.
            :param value: ``CfnCampaign.MetricDimensionProperty.Value``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-metricdimension.html
            """
            self._values = {
            }
            if comparison_operator is not None: self._values["comparison_operator"] = comparison_operator
            if value is not None: self._values["value"] = value

        @property
        def comparison_operator(self) -> typing.Optional[str]:
            """``CfnCampaign.MetricDimensionProperty.ComparisonOperator``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-metricdimension.html#cfn-pinpoint-campaign-metricdimension-comparisonoperator
            """
            return self._values.get('comparison_operator')

        @property
        def value(self) -> typing.Optional[jsii.Number]:
            """``CfnCampaign.MetricDimensionProperty.Value``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-metricdimension.html#cfn-pinpoint-campaign-metricdimension-value
            """
            return self._values.get('value')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'MetricDimensionProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-pinpoint.CfnCampaign.QuietTimeProperty", jsii_struct_bases=[], name_mapping={'end': 'end', 'start': 'start'})
    class QuietTimeProperty():
        def __init__(self, *, end: str, start: str):
            """
            :param end: ``CfnCampaign.QuietTimeProperty.End``.
            :param start: ``CfnCampaign.QuietTimeProperty.Start``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-schedule-quiettime.html
            """
            self._values = {
                'end': end,
                'start': start,
            }

        @property
        def end(self) -> str:
            """``CfnCampaign.QuietTimeProperty.End``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-schedule-quiettime.html#cfn-pinpoint-campaign-schedule-quiettime-end
            """
            return self._values.get('end')

        @property
        def start(self) -> str:
            """``CfnCampaign.QuietTimeProperty.Start``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-schedule-quiettime.html#cfn-pinpoint-campaign-schedule-quiettime-start
            """
            return self._values.get('start')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'QuietTimeProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-pinpoint.CfnCampaign.ScheduleProperty", jsii_struct_bases=[], name_mapping={'end_time': 'endTime', 'event_filter': 'eventFilter', 'frequency': 'frequency', 'is_local_time': 'isLocalTime', 'quiet_time': 'quietTime', 'start_time': 'startTime', 'time_zone': 'timeZone'})
    class ScheduleProperty():
        def __init__(self, *, end_time: typing.Optional[str]=None, event_filter: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnCampaign.CampaignEventFilterProperty"]]]=None, frequency: typing.Optional[str]=None, is_local_time: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, quiet_time: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnCampaign.QuietTimeProperty"]]]=None, start_time: typing.Optional[str]=None, time_zone: typing.Optional[str]=None):
            """
            :param end_time: ``CfnCampaign.ScheduleProperty.EndTime``.
            :param event_filter: ``CfnCampaign.ScheduleProperty.EventFilter``.
            :param frequency: ``CfnCampaign.ScheduleProperty.Frequency``.
            :param is_local_time: ``CfnCampaign.ScheduleProperty.IsLocalTime``.
            :param quiet_time: ``CfnCampaign.ScheduleProperty.QuietTime``.
            :param start_time: ``CfnCampaign.ScheduleProperty.StartTime``.
            :param time_zone: ``CfnCampaign.ScheduleProperty.TimeZone``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-schedule.html
            """
            self._values = {
            }
            if end_time is not None: self._values["end_time"] = end_time
            if event_filter is not None: self._values["event_filter"] = event_filter
            if frequency is not None: self._values["frequency"] = frequency
            if is_local_time is not None: self._values["is_local_time"] = is_local_time
            if quiet_time is not None: self._values["quiet_time"] = quiet_time
            if start_time is not None: self._values["start_time"] = start_time
            if time_zone is not None: self._values["time_zone"] = time_zone

        @property
        def end_time(self) -> typing.Optional[str]:
            """``CfnCampaign.ScheduleProperty.EndTime``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-schedule.html#cfn-pinpoint-campaign-schedule-endtime
            """
            return self._values.get('end_time')

        @property
        def event_filter(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnCampaign.CampaignEventFilterProperty"]]]:
            """``CfnCampaign.ScheduleProperty.EventFilter``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-schedule.html#cfn-pinpoint-campaign-schedule-eventfilter
            """
            return self._values.get('event_filter')

        @property
        def frequency(self) -> typing.Optional[str]:
            """``CfnCampaign.ScheduleProperty.Frequency``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-schedule.html#cfn-pinpoint-campaign-schedule-frequency
            """
            return self._values.get('frequency')

        @property
        def is_local_time(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
            """``CfnCampaign.ScheduleProperty.IsLocalTime``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-schedule.html#cfn-pinpoint-campaign-schedule-islocaltime
            """
            return self._values.get('is_local_time')

        @property
        def quiet_time(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnCampaign.QuietTimeProperty"]]]:
            """``CfnCampaign.ScheduleProperty.QuietTime``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-schedule.html#cfn-pinpoint-campaign-schedule-quiettime
            """
            return self._values.get('quiet_time')

        @property
        def start_time(self) -> typing.Optional[str]:
            """``CfnCampaign.ScheduleProperty.StartTime``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-schedule.html#cfn-pinpoint-campaign-schedule-starttime
            """
            return self._values.get('start_time')

        @property
        def time_zone(self) -> typing.Optional[str]:
            """``CfnCampaign.ScheduleProperty.TimeZone``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-schedule.html#cfn-pinpoint-campaign-schedule-timezone
            """
            return self._values.get('time_zone')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'ScheduleProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-pinpoint.CfnCampaign.SetDimensionProperty", jsii_struct_bases=[], name_mapping={'dimension_type': 'dimensionType', 'values': 'values'})
    class SetDimensionProperty():
        def __init__(self, *, dimension_type: typing.Optional[str]=None, values: typing.Optional[typing.List[str]]=None):
            """
            :param dimension_type: ``CfnCampaign.SetDimensionProperty.DimensionType``.
            :param values: ``CfnCampaign.SetDimensionProperty.Values``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-setdimension.html
            """
            self._values = {
            }
            if dimension_type is not None: self._values["dimension_type"] = dimension_type
            if values is not None: self._values["values"] = values

        @property
        def dimension_type(self) -> typing.Optional[str]:
            """``CfnCampaign.SetDimensionProperty.DimensionType``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-setdimension.html#cfn-pinpoint-campaign-setdimension-dimensiontype
            """
            return self._values.get('dimension_type')

        @property
        def values(self) -> typing.Optional[typing.List[str]]:
            """``CfnCampaign.SetDimensionProperty.Values``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-setdimension.html#cfn-pinpoint-campaign-setdimension-values
            """
            return self._values.get('values')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'SetDimensionProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-pinpoint.CfnCampaign.WriteTreatmentResourceProperty", jsii_struct_bases=[], name_mapping={'message_configuration': 'messageConfiguration', 'schedule': 'schedule', 'size_percent': 'sizePercent', 'treatment_description': 'treatmentDescription', 'treatment_name': 'treatmentName'})
    class WriteTreatmentResourceProperty():
        def __init__(self, *, message_configuration: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnCampaign.MessageConfigurationProperty"]]]=None, schedule: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnCampaign.ScheduleProperty"]]]=None, size_percent: typing.Optional[jsii.Number]=None, treatment_description: typing.Optional[str]=None, treatment_name: typing.Optional[str]=None):
            """
            :param message_configuration: ``CfnCampaign.WriteTreatmentResourceProperty.MessageConfiguration``.
            :param schedule: ``CfnCampaign.WriteTreatmentResourceProperty.Schedule``.
            :param size_percent: ``CfnCampaign.WriteTreatmentResourceProperty.SizePercent``.
            :param treatment_description: ``CfnCampaign.WriteTreatmentResourceProperty.TreatmentDescription``.
            :param treatment_name: ``CfnCampaign.WriteTreatmentResourceProperty.TreatmentName``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-writetreatmentresource.html
            """
            self._values = {
            }
            if message_configuration is not None: self._values["message_configuration"] = message_configuration
            if schedule is not None: self._values["schedule"] = schedule
            if size_percent is not None: self._values["size_percent"] = size_percent
            if treatment_description is not None: self._values["treatment_description"] = treatment_description
            if treatment_name is not None: self._values["treatment_name"] = treatment_name

        @property
        def message_configuration(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnCampaign.MessageConfigurationProperty"]]]:
            """``CfnCampaign.WriteTreatmentResourceProperty.MessageConfiguration``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-writetreatmentresource.html#cfn-pinpoint-campaign-writetreatmentresource-messageconfiguration
            """
            return self._values.get('message_configuration')

        @property
        def schedule(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnCampaign.ScheduleProperty"]]]:
            """``CfnCampaign.WriteTreatmentResourceProperty.Schedule``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-writetreatmentresource.html#cfn-pinpoint-campaign-writetreatmentresource-schedule
            """
            return self._values.get('schedule')

        @property
        def size_percent(self) -> typing.Optional[jsii.Number]:
            """``CfnCampaign.WriteTreatmentResourceProperty.SizePercent``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-writetreatmentresource.html#cfn-pinpoint-campaign-writetreatmentresource-sizepercent
            """
            return self._values.get('size_percent')

        @property
        def treatment_description(self) -> typing.Optional[str]:
            """``CfnCampaign.WriteTreatmentResourceProperty.TreatmentDescription``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-writetreatmentresource.html#cfn-pinpoint-campaign-writetreatmentresource-treatmentdescription
            """
            return self._values.get('treatment_description')

        @property
        def treatment_name(self) -> typing.Optional[str]:
            """``CfnCampaign.WriteTreatmentResourceProperty.TreatmentName``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-campaign-writetreatmentresource.html#cfn-pinpoint-campaign-writetreatmentresource-treatmentname
            """
            return self._values.get('treatment_name')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'WriteTreatmentResourceProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



@jsii.data_type(jsii_type="@aws-cdk/aws-pinpoint.CfnCampaignProps", jsii_struct_bases=[], name_mapping={'application_id': 'applicationId', 'message_configuration': 'messageConfiguration', 'name': 'name', 'schedule': 'schedule', 'segment_id': 'segmentId', 'additional_treatments': 'additionalTreatments', 'campaign_hook': 'campaignHook', 'description': 'description', 'holdout_percent': 'holdoutPercent', 'is_paused': 'isPaused', 'limits': 'limits', 'segment_version': 'segmentVersion', 'tags': 'tags', 'treatment_description': 'treatmentDescription', 'treatment_name': 'treatmentName'})
class CfnCampaignProps():
    def __init__(self, *, application_id: str, message_configuration: typing.Union[aws_cdk.core.IResolvable, "CfnCampaign.MessageConfigurationProperty"], name: str, schedule: typing.Union[aws_cdk.core.IResolvable, "CfnCampaign.ScheduleProperty"], segment_id: str, additional_treatments: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnCampaign.WriteTreatmentResourceProperty"]]]]]=None, campaign_hook: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnCampaign.CampaignHookProperty"]]]=None, description: typing.Optional[str]=None, holdout_percent: typing.Optional[jsii.Number]=None, is_paused: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, limits: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnCampaign.LimitsProperty"]]]=None, segment_version: typing.Optional[jsii.Number]=None, tags: typing.Any=None, treatment_description: typing.Optional[str]=None, treatment_name: typing.Optional[str]=None):
        """Properties for defining a ``AWS::Pinpoint::Campaign``.

        :param application_id: ``AWS::Pinpoint::Campaign.ApplicationId``.
        :param message_configuration: ``AWS::Pinpoint::Campaign.MessageConfiguration``.
        :param name: ``AWS::Pinpoint::Campaign.Name``.
        :param schedule: ``AWS::Pinpoint::Campaign.Schedule``.
        :param segment_id: ``AWS::Pinpoint::Campaign.SegmentId``.
        :param additional_treatments: ``AWS::Pinpoint::Campaign.AdditionalTreatments``.
        :param campaign_hook: ``AWS::Pinpoint::Campaign.CampaignHook``.
        :param description: ``AWS::Pinpoint::Campaign.Description``.
        :param holdout_percent: ``AWS::Pinpoint::Campaign.HoldoutPercent``.
        :param is_paused: ``AWS::Pinpoint::Campaign.IsPaused``.
        :param limits: ``AWS::Pinpoint::Campaign.Limits``.
        :param segment_version: ``AWS::Pinpoint::Campaign.SegmentVersion``.
        :param tags: ``AWS::Pinpoint::Campaign.Tags``.
        :param treatment_description: ``AWS::Pinpoint::Campaign.TreatmentDescription``.
        :param treatment_name: ``AWS::Pinpoint::Campaign.TreatmentName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-campaign.html
        """
        self._values = {
            'application_id': application_id,
            'message_configuration': message_configuration,
            'name': name,
            'schedule': schedule,
            'segment_id': segment_id,
        }
        if additional_treatments is not None: self._values["additional_treatments"] = additional_treatments
        if campaign_hook is not None: self._values["campaign_hook"] = campaign_hook
        if description is not None: self._values["description"] = description
        if holdout_percent is not None: self._values["holdout_percent"] = holdout_percent
        if is_paused is not None: self._values["is_paused"] = is_paused
        if limits is not None: self._values["limits"] = limits
        if segment_version is not None: self._values["segment_version"] = segment_version
        if tags is not None: self._values["tags"] = tags
        if treatment_description is not None: self._values["treatment_description"] = treatment_description
        if treatment_name is not None: self._values["treatment_name"] = treatment_name

    @property
    def application_id(self) -> str:
        """``AWS::Pinpoint::Campaign.ApplicationId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-campaign.html#cfn-pinpoint-campaign-applicationid
        """
        return self._values.get('application_id')

    @property
    def message_configuration(self) -> typing.Union[aws_cdk.core.IResolvable, "CfnCampaign.MessageConfigurationProperty"]:
        """``AWS::Pinpoint::Campaign.MessageConfiguration``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-campaign.html#cfn-pinpoint-campaign-messageconfiguration
        """
        return self._values.get('message_configuration')

    @property
    def name(self) -> str:
        """``AWS::Pinpoint::Campaign.Name``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-campaign.html#cfn-pinpoint-campaign-name
        """
        return self._values.get('name')

    @property
    def schedule(self) -> typing.Union[aws_cdk.core.IResolvable, "CfnCampaign.ScheduleProperty"]:
        """``AWS::Pinpoint::Campaign.Schedule``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-campaign.html#cfn-pinpoint-campaign-schedule
        """
        return self._values.get('schedule')

    @property
    def segment_id(self) -> str:
        """``AWS::Pinpoint::Campaign.SegmentId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-campaign.html#cfn-pinpoint-campaign-segmentid
        """
        return self._values.get('segment_id')

    @property
    def additional_treatments(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnCampaign.WriteTreatmentResourceProperty"]]]]]:
        """``AWS::Pinpoint::Campaign.AdditionalTreatments``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-campaign.html#cfn-pinpoint-campaign-additionaltreatments
        """
        return self._values.get('additional_treatments')

    @property
    def campaign_hook(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnCampaign.CampaignHookProperty"]]]:
        """``AWS::Pinpoint::Campaign.CampaignHook``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-campaign.html#cfn-pinpoint-campaign-campaignhook
        """
        return self._values.get('campaign_hook')

    @property
    def description(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::Campaign.Description``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-campaign.html#cfn-pinpoint-campaign-description
        """
        return self._values.get('description')

    @property
    def holdout_percent(self) -> typing.Optional[jsii.Number]:
        """``AWS::Pinpoint::Campaign.HoldoutPercent``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-campaign.html#cfn-pinpoint-campaign-holdoutpercent
        """
        return self._values.get('holdout_percent')

    @property
    def is_paused(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::Pinpoint::Campaign.IsPaused``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-campaign.html#cfn-pinpoint-campaign-ispaused
        """
        return self._values.get('is_paused')

    @property
    def limits(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnCampaign.LimitsProperty"]]]:
        """``AWS::Pinpoint::Campaign.Limits``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-campaign.html#cfn-pinpoint-campaign-limits
        """
        return self._values.get('limits')

    @property
    def segment_version(self) -> typing.Optional[jsii.Number]:
        """``AWS::Pinpoint::Campaign.SegmentVersion``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-campaign.html#cfn-pinpoint-campaign-segmentversion
        """
        return self._values.get('segment_version')

    @property
    def tags(self) -> typing.Any:
        """``AWS::Pinpoint::Campaign.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-campaign.html#cfn-pinpoint-campaign-tags
        """
        return self._values.get('tags')

    @property
    def treatment_description(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::Campaign.TreatmentDescription``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-campaign.html#cfn-pinpoint-campaign-treatmentdescription
        """
        return self._values.get('treatment_description')

    @property
    def treatment_name(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::Campaign.TreatmentName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-campaign.html#cfn-pinpoint-campaign-treatmentname
        """
        return self._values.get('treatment_name')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnCampaignProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnEmailChannel(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-pinpoint.CfnEmailChannel"):
    """A CloudFormation ``AWS::Pinpoint::EmailChannel``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-emailchannel.html
    cloudformationResource:
    :cloudformationResource:: AWS::Pinpoint::EmailChannel
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, application_id: str, from_address: str, identity: str, configuration_set: typing.Optional[str]=None, enabled: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, role_arn: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::Pinpoint::EmailChannel``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param application_id: ``AWS::Pinpoint::EmailChannel.ApplicationId``.
        :param from_address: ``AWS::Pinpoint::EmailChannel.FromAddress``.
        :param identity: ``AWS::Pinpoint::EmailChannel.Identity``.
        :param configuration_set: ``AWS::Pinpoint::EmailChannel.ConfigurationSet``.
        :param enabled: ``AWS::Pinpoint::EmailChannel.Enabled``.
        :param role_arn: ``AWS::Pinpoint::EmailChannel.RoleArn``.
        """
        props = CfnEmailChannelProps(application_id=application_id, from_address=from_address, identity=identity, configuration_set=configuration_set, enabled=enabled, role_arn=role_arn)

        jsii.create(CfnEmailChannel, self, [scope, id, props])

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
    @jsii.member(jsii_name="applicationId")
    def application_id(self) -> str:
        """``AWS::Pinpoint::EmailChannel.ApplicationId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-emailchannel.html#cfn-pinpoint-emailchannel-applicationid
        """
        return jsii.get(self, "applicationId")

    @application_id.setter
    def application_id(self, value: str):
        return jsii.set(self, "applicationId", value)

    @property
    @jsii.member(jsii_name="fromAddress")
    def from_address(self) -> str:
        """``AWS::Pinpoint::EmailChannel.FromAddress``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-emailchannel.html#cfn-pinpoint-emailchannel-fromaddress
        """
        return jsii.get(self, "fromAddress")

    @from_address.setter
    def from_address(self, value: str):
        return jsii.set(self, "fromAddress", value)

    @property
    @jsii.member(jsii_name="identity")
    def identity(self) -> str:
        """``AWS::Pinpoint::EmailChannel.Identity``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-emailchannel.html#cfn-pinpoint-emailchannel-identity
        """
        return jsii.get(self, "identity")

    @identity.setter
    def identity(self, value: str):
        return jsii.set(self, "identity", value)

    @property
    @jsii.member(jsii_name="configurationSet")
    def configuration_set(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::EmailChannel.ConfigurationSet``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-emailchannel.html#cfn-pinpoint-emailchannel-configurationset
        """
        return jsii.get(self, "configurationSet")

    @configuration_set.setter
    def configuration_set(self, value: typing.Optional[str]):
        return jsii.set(self, "configurationSet", value)

    @property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::Pinpoint::EmailChannel.Enabled``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-emailchannel.html#cfn-pinpoint-emailchannel-enabled
        """
        return jsii.get(self, "enabled")

    @enabled.setter
    def enabled(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "enabled", value)

    @property
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::EmailChannel.RoleArn``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-emailchannel.html#cfn-pinpoint-emailchannel-rolearn
        """
        return jsii.get(self, "roleArn")

    @role_arn.setter
    def role_arn(self, value: typing.Optional[str]):
        return jsii.set(self, "roleArn", value)


@jsii.data_type(jsii_type="@aws-cdk/aws-pinpoint.CfnEmailChannelProps", jsii_struct_bases=[], name_mapping={'application_id': 'applicationId', 'from_address': 'fromAddress', 'identity': 'identity', 'configuration_set': 'configurationSet', 'enabled': 'enabled', 'role_arn': 'roleArn'})
class CfnEmailChannelProps():
    def __init__(self, *, application_id: str, from_address: str, identity: str, configuration_set: typing.Optional[str]=None, enabled: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, role_arn: typing.Optional[str]=None):
        """Properties for defining a ``AWS::Pinpoint::EmailChannel``.

        :param application_id: ``AWS::Pinpoint::EmailChannel.ApplicationId``.
        :param from_address: ``AWS::Pinpoint::EmailChannel.FromAddress``.
        :param identity: ``AWS::Pinpoint::EmailChannel.Identity``.
        :param configuration_set: ``AWS::Pinpoint::EmailChannel.ConfigurationSet``.
        :param enabled: ``AWS::Pinpoint::EmailChannel.Enabled``.
        :param role_arn: ``AWS::Pinpoint::EmailChannel.RoleArn``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-emailchannel.html
        """
        self._values = {
            'application_id': application_id,
            'from_address': from_address,
            'identity': identity,
        }
        if configuration_set is not None: self._values["configuration_set"] = configuration_set
        if enabled is not None: self._values["enabled"] = enabled
        if role_arn is not None: self._values["role_arn"] = role_arn

    @property
    def application_id(self) -> str:
        """``AWS::Pinpoint::EmailChannel.ApplicationId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-emailchannel.html#cfn-pinpoint-emailchannel-applicationid
        """
        return self._values.get('application_id')

    @property
    def from_address(self) -> str:
        """``AWS::Pinpoint::EmailChannel.FromAddress``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-emailchannel.html#cfn-pinpoint-emailchannel-fromaddress
        """
        return self._values.get('from_address')

    @property
    def identity(self) -> str:
        """``AWS::Pinpoint::EmailChannel.Identity``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-emailchannel.html#cfn-pinpoint-emailchannel-identity
        """
        return self._values.get('identity')

    @property
    def configuration_set(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::EmailChannel.ConfigurationSet``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-emailchannel.html#cfn-pinpoint-emailchannel-configurationset
        """
        return self._values.get('configuration_set')

    @property
    def enabled(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::Pinpoint::EmailChannel.Enabled``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-emailchannel.html#cfn-pinpoint-emailchannel-enabled
        """
        return self._values.get('enabled')

    @property
    def role_arn(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::EmailChannel.RoleArn``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-emailchannel.html#cfn-pinpoint-emailchannel-rolearn
        """
        return self._values.get('role_arn')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnEmailChannelProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnEventStream(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-pinpoint.CfnEventStream"):
    """A CloudFormation ``AWS::Pinpoint::EventStream``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-eventstream.html
    cloudformationResource:
    :cloudformationResource:: AWS::Pinpoint::EventStream
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, application_id: str, destination_stream_arn: str, role_arn: str) -> None:
        """Create a new ``AWS::Pinpoint::EventStream``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param application_id: ``AWS::Pinpoint::EventStream.ApplicationId``.
        :param destination_stream_arn: ``AWS::Pinpoint::EventStream.DestinationStreamArn``.
        :param role_arn: ``AWS::Pinpoint::EventStream.RoleArn``.
        """
        props = CfnEventStreamProps(application_id=application_id, destination_stream_arn=destination_stream_arn, role_arn=role_arn)

        jsii.create(CfnEventStream, self, [scope, id, props])

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
    @jsii.member(jsii_name="applicationId")
    def application_id(self) -> str:
        """``AWS::Pinpoint::EventStream.ApplicationId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-eventstream.html#cfn-pinpoint-eventstream-applicationid
        """
        return jsii.get(self, "applicationId")

    @application_id.setter
    def application_id(self, value: str):
        return jsii.set(self, "applicationId", value)

    @property
    @jsii.member(jsii_name="destinationStreamArn")
    def destination_stream_arn(self) -> str:
        """``AWS::Pinpoint::EventStream.DestinationStreamArn``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-eventstream.html#cfn-pinpoint-eventstream-destinationstreamarn
        """
        return jsii.get(self, "destinationStreamArn")

    @destination_stream_arn.setter
    def destination_stream_arn(self, value: str):
        return jsii.set(self, "destinationStreamArn", value)

    @property
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> str:
        """``AWS::Pinpoint::EventStream.RoleArn``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-eventstream.html#cfn-pinpoint-eventstream-rolearn
        """
        return jsii.get(self, "roleArn")

    @role_arn.setter
    def role_arn(self, value: str):
        return jsii.set(self, "roleArn", value)


@jsii.data_type(jsii_type="@aws-cdk/aws-pinpoint.CfnEventStreamProps", jsii_struct_bases=[], name_mapping={'application_id': 'applicationId', 'destination_stream_arn': 'destinationStreamArn', 'role_arn': 'roleArn'})
class CfnEventStreamProps():
    def __init__(self, *, application_id: str, destination_stream_arn: str, role_arn: str):
        """Properties for defining a ``AWS::Pinpoint::EventStream``.

        :param application_id: ``AWS::Pinpoint::EventStream.ApplicationId``.
        :param destination_stream_arn: ``AWS::Pinpoint::EventStream.DestinationStreamArn``.
        :param role_arn: ``AWS::Pinpoint::EventStream.RoleArn``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-eventstream.html
        """
        self._values = {
            'application_id': application_id,
            'destination_stream_arn': destination_stream_arn,
            'role_arn': role_arn,
        }

    @property
    def application_id(self) -> str:
        """``AWS::Pinpoint::EventStream.ApplicationId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-eventstream.html#cfn-pinpoint-eventstream-applicationid
        """
        return self._values.get('application_id')

    @property
    def destination_stream_arn(self) -> str:
        """``AWS::Pinpoint::EventStream.DestinationStreamArn``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-eventstream.html#cfn-pinpoint-eventstream-destinationstreamarn
        """
        return self._values.get('destination_stream_arn')

    @property
    def role_arn(self) -> str:
        """``AWS::Pinpoint::EventStream.RoleArn``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-eventstream.html#cfn-pinpoint-eventstream-rolearn
        """
        return self._values.get('role_arn')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnEventStreamProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnGCMChannel(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-pinpoint.CfnGCMChannel"):
    """A CloudFormation ``AWS::Pinpoint::GCMChannel``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-gcmchannel.html
    cloudformationResource:
    :cloudformationResource:: AWS::Pinpoint::GCMChannel
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, api_key: str, application_id: str, enabled: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None) -> None:
        """Create a new ``AWS::Pinpoint::GCMChannel``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param api_key: ``AWS::Pinpoint::GCMChannel.ApiKey``.
        :param application_id: ``AWS::Pinpoint::GCMChannel.ApplicationId``.
        :param enabled: ``AWS::Pinpoint::GCMChannel.Enabled``.
        """
        props = CfnGCMChannelProps(api_key=api_key, application_id=application_id, enabled=enabled)

        jsii.create(CfnGCMChannel, self, [scope, id, props])

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
    @jsii.member(jsii_name="apiKey")
    def api_key(self) -> str:
        """``AWS::Pinpoint::GCMChannel.ApiKey``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-gcmchannel.html#cfn-pinpoint-gcmchannel-apikey
        """
        return jsii.get(self, "apiKey")

    @api_key.setter
    def api_key(self, value: str):
        return jsii.set(self, "apiKey", value)

    @property
    @jsii.member(jsii_name="applicationId")
    def application_id(self) -> str:
        """``AWS::Pinpoint::GCMChannel.ApplicationId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-gcmchannel.html#cfn-pinpoint-gcmchannel-applicationid
        """
        return jsii.get(self, "applicationId")

    @application_id.setter
    def application_id(self, value: str):
        return jsii.set(self, "applicationId", value)

    @property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::Pinpoint::GCMChannel.Enabled``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-gcmchannel.html#cfn-pinpoint-gcmchannel-enabled
        """
        return jsii.get(self, "enabled")

    @enabled.setter
    def enabled(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "enabled", value)


@jsii.data_type(jsii_type="@aws-cdk/aws-pinpoint.CfnGCMChannelProps", jsii_struct_bases=[], name_mapping={'api_key': 'apiKey', 'application_id': 'applicationId', 'enabled': 'enabled'})
class CfnGCMChannelProps():
    def __init__(self, *, api_key: str, application_id: str, enabled: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None):
        """Properties for defining a ``AWS::Pinpoint::GCMChannel``.

        :param api_key: ``AWS::Pinpoint::GCMChannel.ApiKey``.
        :param application_id: ``AWS::Pinpoint::GCMChannel.ApplicationId``.
        :param enabled: ``AWS::Pinpoint::GCMChannel.Enabled``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-gcmchannel.html
        """
        self._values = {
            'api_key': api_key,
            'application_id': application_id,
        }
        if enabled is not None: self._values["enabled"] = enabled

    @property
    def api_key(self) -> str:
        """``AWS::Pinpoint::GCMChannel.ApiKey``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-gcmchannel.html#cfn-pinpoint-gcmchannel-apikey
        """
        return self._values.get('api_key')

    @property
    def application_id(self) -> str:
        """``AWS::Pinpoint::GCMChannel.ApplicationId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-gcmchannel.html#cfn-pinpoint-gcmchannel-applicationid
        """
        return self._values.get('application_id')

    @property
    def enabled(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::Pinpoint::GCMChannel.Enabled``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-gcmchannel.html#cfn-pinpoint-gcmchannel-enabled
        """
        return self._values.get('enabled')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnGCMChannelProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnSMSChannel(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-pinpoint.CfnSMSChannel"):
    """A CloudFormation ``AWS::Pinpoint::SMSChannel``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-smschannel.html
    cloudformationResource:
    :cloudformationResource:: AWS::Pinpoint::SMSChannel
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, application_id: str, enabled: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, sender_id: typing.Optional[str]=None, short_code: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::Pinpoint::SMSChannel``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param application_id: ``AWS::Pinpoint::SMSChannel.ApplicationId``.
        :param enabled: ``AWS::Pinpoint::SMSChannel.Enabled``.
        :param sender_id: ``AWS::Pinpoint::SMSChannel.SenderId``.
        :param short_code: ``AWS::Pinpoint::SMSChannel.ShortCode``.
        """
        props = CfnSMSChannelProps(application_id=application_id, enabled=enabled, sender_id=sender_id, short_code=short_code)

        jsii.create(CfnSMSChannel, self, [scope, id, props])

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
    @jsii.member(jsii_name="applicationId")
    def application_id(self) -> str:
        """``AWS::Pinpoint::SMSChannel.ApplicationId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-smschannel.html#cfn-pinpoint-smschannel-applicationid
        """
        return jsii.get(self, "applicationId")

    @application_id.setter
    def application_id(self, value: str):
        return jsii.set(self, "applicationId", value)

    @property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::Pinpoint::SMSChannel.Enabled``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-smschannel.html#cfn-pinpoint-smschannel-enabled
        """
        return jsii.get(self, "enabled")

    @enabled.setter
    def enabled(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "enabled", value)

    @property
    @jsii.member(jsii_name="senderId")
    def sender_id(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::SMSChannel.SenderId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-smschannel.html#cfn-pinpoint-smschannel-senderid
        """
        return jsii.get(self, "senderId")

    @sender_id.setter
    def sender_id(self, value: typing.Optional[str]):
        return jsii.set(self, "senderId", value)

    @property
    @jsii.member(jsii_name="shortCode")
    def short_code(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::SMSChannel.ShortCode``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-smschannel.html#cfn-pinpoint-smschannel-shortcode
        """
        return jsii.get(self, "shortCode")

    @short_code.setter
    def short_code(self, value: typing.Optional[str]):
        return jsii.set(self, "shortCode", value)


@jsii.data_type(jsii_type="@aws-cdk/aws-pinpoint.CfnSMSChannelProps", jsii_struct_bases=[], name_mapping={'application_id': 'applicationId', 'enabled': 'enabled', 'sender_id': 'senderId', 'short_code': 'shortCode'})
class CfnSMSChannelProps():
    def __init__(self, *, application_id: str, enabled: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, sender_id: typing.Optional[str]=None, short_code: typing.Optional[str]=None):
        """Properties for defining a ``AWS::Pinpoint::SMSChannel``.

        :param application_id: ``AWS::Pinpoint::SMSChannel.ApplicationId``.
        :param enabled: ``AWS::Pinpoint::SMSChannel.Enabled``.
        :param sender_id: ``AWS::Pinpoint::SMSChannel.SenderId``.
        :param short_code: ``AWS::Pinpoint::SMSChannel.ShortCode``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-smschannel.html
        """
        self._values = {
            'application_id': application_id,
        }
        if enabled is not None: self._values["enabled"] = enabled
        if sender_id is not None: self._values["sender_id"] = sender_id
        if short_code is not None: self._values["short_code"] = short_code

    @property
    def application_id(self) -> str:
        """``AWS::Pinpoint::SMSChannel.ApplicationId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-smschannel.html#cfn-pinpoint-smschannel-applicationid
        """
        return self._values.get('application_id')

    @property
    def enabled(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::Pinpoint::SMSChannel.Enabled``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-smschannel.html#cfn-pinpoint-smschannel-enabled
        """
        return self._values.get('enabled')

    @property
    def sender_id(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::SMSChannel.SenderId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-smschannel.html#cfn-pinpoint-smschannel-senderid
        """
        return self._values.get('sender_id')

    @property
    def short_code(self) -> typing.Optional[str]:
        """``AWS::Pinpoint::SMSChannel.ShortCode``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-smschannel.html#cfn-pinpoint-smschannel-shortcode
        """
        return self._values.get('short_code')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnSMSChannelProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnSegment(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-pinpoint.CfnSegment"):
    """A CloudFormation ``AWS::Pinpoint::Segment``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-segment.html
    cloudformationResource:
    :cloudformationResource:: AWS::Pinpoint::Segment
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, application_id: str, name: str, dimensions: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["SegmentDimensionsProperty"]]]=None, segment_groups: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["SegmentGroupsProperty"]]]=None, tags: typing.Any=None) -> None:
        """Create a new ``AWS::Pinpoint::Segment``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param application_id: ``AWS::Pinpoint::Segment.ApplicationId``.
        :param name: ``AWS::Pinpoint::Segment.Name``.
        :param dimensions: ``AWS::Pinpoint::Segment.Dimensions``.
        :param segment_groups: ``AWS::Pinpoint::Segment.SegmentGroups``.
        :param tags: ``AWS::Pinpoint::Segment.Tags``.
        """
        props = CfnSegmentProps(application_id=application_id, name=name, dimensions=dimensions, segment_groups=segment_groups, tags=tags)

        jsii.create(CfnSegment, self, [scope, id, props])

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
    @jsii.member(jsii_name="attrSegmentId")
    def attr_segment_id(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: SegmentId
        """
        return jsii.get(self, "attrSegmentId")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        """``AWS::Pinpoint::Segment.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-segment.html#cfn-pinpoint-segment-tags
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="applicationId")
    def application_id(self) -> str:
        """``AWS::Pinpoint::Segment.ApplicationId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-segment.html#cfn-pinpoint-segment-applicationid
        """
        return jsii.get(self, "applicationId")

    @application_id.setter
    def application_id(self, value: str):
        return jsii.set(self, "applicationId", value)

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> str:
        """``AWS::Pinpoint::Segment.Name``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-segment.html#cfn-pinpoint-segment-name
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: str):
        return jsii.set(self, "name", value)

    @property
    @jsii.member(jsii_name="dimensions")
    def dimensions(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["SegmentDimensionsProperty"]]]:
        """``AWS::Pinpoint::Segment.Dimensions``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-segment.html#cfn-pinpoint-segment-dimensions
        """
        return jsii.get(self, "dimensions")

    @dimensions.setter
    def dimensions(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["SegmentDimensionsProperty"]]]):
        return jsii.set(self, "dimensions", value)

    @property
    @jsii.member(jsii_name="segmentGroups")
    def segment_groups(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["SegmentGroupsProperty"]]]:
        """``AWS::Pinpoint::Segment.SegmentGroups``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-segment.html#cfn-pinpoint-segment-segmentgroups
        """
        return jsii.get(self, "segmentGroups")

    @segment_groups.setter
    def segment_groups(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["SegmentGroupsProperty"]]]):
        return jsii.set(self, "segmentGroups", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-pinpoint.CfnSegment.AttributeDimensionProperty", jsii_struct_bases=[], name_mapping={'attribute_type': 'attributeType', 'values': 'values'})
    class AttributeDimensionProperty():
        def __init__(self, *, attribute_type: typing.Optional[str]=None, values: typing.Optional[typing.List[str]]=None):
            """
            :param attribute_type: ``CfnSegment.AttributeDimensionProperty.AttributeType``.
            :param values: ``CfnSegment.AttributeDimensionProperty.Values``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-segment-attributedimension.html
            """
            self._values = {
            }
            if attribute_type is not None: self._values["attribute_type"] = attribute_type
            if values is not None: self._values["values"] = values

        @property
        def attribute_type(self) -> typing.Optional[str]:
            """``CfnSegment.AttributeDimensionProperty.AttributeType``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-segment-attributedimension.html#cfn-pinpoint-segment-attributedimension-attributetype
            """
            return self._values.get('attribute_type')

        @property
        def values(self) -> typing.Optional[typing.List[str]]:
            """``CfnSegment.AttributeDimensionProperty.Values``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-segment-attributedimension.html#cfn-pinpoint-segment-attributedimension-values
            """
            return self._values.get('values')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'AttributeDimensionProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-pinpoint.CfnSegment.BehaviorProperty", jsii_struct_bases=[], name_mapping={'recency': 'recency'})
    class BehaviorProperty():
        def __init__(self, *, recency: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnSegment.RecencyProperty"]]]=None):
            """
            :param recency: ``CfnSegment.BehaviorProperty.Recency``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-segment-segmentdimensions-behavior.html
            """
            self._values = {
            }
            if recency is not None: self._values["recency"] = recency

        @property
        def recency(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnSegment.RecencyProperty"]]]:
            """``CfnSegment.BehaviorProperty.Recency``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-segment-segmentdimensions-behavior.html#cfn-pinpoint-segment-segmentdimensions-behavior-recency
            """
            return self._values.get('recency')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'BehaviorProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-pinpoint.CfnSegment.CoordinatesProperty", jsii_struct_bases=[], name_mapping={'latitude': 'latitude', 'longitude': 'longitude'})
    class CoordinatesProperty():
        def __init__(self, *, latitude: jsii.Number, longitude: jsii.Number):
            """
            :param latitude: ``CfnSegment.CoordinatesProperty.Latitude``.
            :param longitude: ``CfnSegment.CoordinatesProperty.Longitude``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-segment-segmentdimensions-location-gpspoint-coordinates.html
            """
            self._values = {
                'latitude': latitude,
                'longitude': longitude,
            }

        @property
        def latitude(self) -> jsii.Number:
            """``CfnSegment.CoordinatesProperty.Latitude``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-segment-segmentdimensions-location-gpspoint-coordinates.html#cfn-pinpoint-segment-segmentdimensions-location-gpspoint-coordinates-latitude
            """
            return self._values.get('latitude')

        @property
        def longitude(self) -> jsii.Number:
            """``CfnSegment.CoordinatesProperty.Longitude``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-segment-segmentdimensions-location-gpspoint-coordinates.html#cfn-pinpoint-segment-segmentdimensions-location-gpspoint-coordinates-longitude
            """
            return self._values.get('longitude')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'CoordinatesProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-pinpoint.CfnSegment.DemographicProperty", jsii_struct_bases=[], name_mapping={'app_version': 'appVersion', 'channel': 'channel', 'device_type': 'deviceType', 'make': 'make', 'model': 'model', 'platform': 'platform'})
    class DemographicProperty():
        def __init__(self, *, app_version: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnSegment.SetDimensionProperty"]]]=None, channel: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnSegment.SetDimensionProperty"]]]=None, device_type: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnSegment.SetDimensionProperty"]]]=None, make: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnSegment.SetDimensionProperty"]]]=None, model: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnSegment.SetDimensionProperty"]]]=None, platform: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnSegment.SetDimensionProperty"]]]=None):
            """
            :param app_version: ``CfnSegment.DemographicProperty.AppVersion``.
            :param channel: ``CfnSegment.DemographicProperty.Channel``.
            :param device_type: ``CfnSegment.DemographicProperty.DeviceType``.
            :param make: ``CfnSegment.DemographicProperty.Make``.
            :param model: ``CfnSegment.DemographicProperty.Model``.
            :param platform: ``CfnSegment.DemographicProperty.Platform``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-segment-segmentdimensions-demographic.html
            """
            self._values = {
            }
            if app_version is not None: self._values["app_version"] = app_version
            if channel is not None: self._values["channel"] = channel
            if device_type is not None: self._values["device_type"] = device_type
            if make is not None: self._values["make"] = make
            if model is not None: self._values["model"] = model
            if platform is not None: self._values["platform"] = platform

        @property
        def app_version(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnSegment.SetDimensionProperty"]]]:
            """``CfnSegment.DemographicProperty.AppVersion``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-segment-segmentdimensions-demographic.html#cfn-pinpoint-segment-segmentdimensions-demographic-appversion
            """
            return self._values.get('app_version')

        @property
        def channel(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnSegment.SetDimensionProperty"]]]:
            """``CfnSegment.DemographicProperty.Channel``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-segment-segmentdimensions-demographic.html#cfn-pinpoint-segment-segmentdimensions-demographic-channel
            """
            return self._values.get('channel')

        @property
        def device_type(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnSegment.SetDimensionProperty"]]]:
            """``CfnSegment.DemographicProperty.DeviceType``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-segment-segmentdimensions-demographic.html#cfn-pinpoint-segment-segmentdimensions-demographic-devicetype
            """
            return self._values.get('device_type')

        @property
        def make(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnSegment.SetDimensionProperty"]]]:
            """``CfnSegment.DemographicProperty.Make``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-segment-segmentdimensions-demographic.html#cfn-pinpoint-segment-segmentdimensions-demographic-make
            """
            return self._values.get('make')

        @property
        def model(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnSegment.SetDimensionProperty"]]]:
            """``CfnSegment.DemographicProperty.Model``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-segment-segmentdimensions-demographic.html#cfn-pinpoint-segment-segmentdimensions-demographic-model
            """
            return self._values.get('model')

        @property
        def platform(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnSegment.SetDimensionProperty"]]]:
            """``CfnSegment.DemographicProperty.Platform``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-segment-segmentdimensions-demographic.html#cfn-pinpoint-segment-segmentdimensions-demographic-platform
            """
            return self._values.get('platform')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'DemographicProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-pinpoint.CfnSegment.GPSPointProperty", jsii_struct_bases=[], name_mapping={'coordinates': 'coordinates', 'range_in_kilometers': 'rangeInKilometers'})
    class GPSPointProperty():
        def __init__(self, *, coordinates: typing.Union[aws_cdk.core.IResolvable, "CfnSegment.CoordinatesProperty"], range_in_kilometers: jsii.Number):
            """
            :param coordinates: ``CfnSegment.GPSPointProperty.Coordinates``.
            :param range_in_kilometers: ``CfnSegment.GPSPointProperty.RangeInKilometers``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-segment-segmentdimensions-location-gpspoint.html
            """
            self._values = {
                'coordinates': coordinates,
                'range_in_kilometers': range_in_kilometers,
            }

        @property
        def coordinates(self) -> typing.Union[aws_cdk.core.IResolvable, "CfnSegment.CoordinatesProperty"]:
            """``CfnSegment.GPSPointProperty.Coordinates``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-segment-segmentdimensions-location-gpspoint.html#cfn-pinpoint-segment-segmentdimensions-location-gpspoint-coordinates
            """
            return self._values.get('coordinates')

        @property
        def range_in_kilometers(self) -> jsii.Number:
            """``CfnSegment.GPSPointProperty.RangeInKilometers``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-segment-segmentdimensions-location-gpspoint.html#cfn-pinpoint-segment-segmentdimensions-location-gpspoint-rangeinkilometers
            """
            return self._values.get('range_in_kilometers')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'GPSPointProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-pinpoint.CfnSegment.GroupsProperty", jsii_struct_bases=[], name_mapping={'dimensions': 'dimensions', 'source_segments': 'sourceSegments', 'source_type': 'sourceType', 'type': 'type'})
    class GroupsProperty():
        def __init__(self, *, dimensions: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnSegment.SegmentDimensionsProperty"]]]]]=None, source_segments: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnSegment.SourceSegmentsProperty"]]]]]=None, source_type: typing.Optional[str]=None, type: typing.Optional[str]=None):
            """
            :param dimensions: ``CfnSegment.GroupsProperty.Dimensions``.
            :param source_segments: ``CfnSegment.GroupsProperty.SourceSegments``.
            :param source_type: ``CfnSegment.GroupsProperty.SourceType``.
            :param type: ``CfnSegment.GroupsProperty.Type``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-segment-segmentgroups-groups.html
            """
            self._values = {
            }
            if dimensions is not None: self._values["dimensions"] = dimensions
            if source_segments is not None: self._values["source_segments"] = source_segments
            if source_type is not None: self._values["source_type"] = source_type
            if type is not None: self._values["type"] = type

        @property
        def dimensions(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnSegment.SegmentDimensionsProperty"]]]]]:
            """``CfnSegment.GroupsProperty.Dimensions``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-segment-segmentgroups-groups.html#cfn-pinpoint-segment-segmentgroups-groups-dimensions
            """
            return self._values.get('dimensions')

        @property
        def source_segments(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnSegment.SourceSegmentsProperty"]]]]]:
            """``CfnSegment.GroupsProperty.SourceSegments``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-segment-segmentgroups-groups.html#cfn-pinpoint-segment-segmentgroups-groups-sourcesegments
            """
            return self._values.get('source_segments')

        @property
        def source_type(self) -> typing.Optional[str]:
            """``CfnSegment.GroupsProperty.SourceType``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-segment-segmentgroups-groups.html#cfn-pinpoint-segment-segmentgroups-groups-sourcetype
            """
            return self._values.get('source_type')

        @property
        def type(self) -> typing.Optional[str]:
            """``CfnSegment.GroupsProperty.Type``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-segment-segmentgroups-groups.html#cfn-pinpoint-segment-segmentgroups-groups-type
            """
            return self._values.get('type')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'GroupsProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-pinpoint.CfnSegment.LocationProperty", jsii_struct_bases=[], name_mapping={'country': 'country', 'gps_point': 'gpsPoint'})
    class LocationProperty():
        def __init__(self, *, country: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnSegment.SetDimensionProperty"]]]=None, gps_point: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnSegment.GPSPointProperty"]]]=None):
            """
            :param country: ``CfnSegment.LocationProperty.Country``.
            :param gps_point: ``CfnSegment.LocationProperty.GPSPoint``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-segment-segmentdimensions-location.html
            """
            self._values = {
            }
            if country is not None: self._values["country"] = country
            if gps_point is not None: self._values["gps_point"] = gps_point

        @property
        def country(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnSegment.SetDimensionProperty"]]]:
            """``CfnSegment.LocationProperty.Country``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-segment-segmentdimensions-location.html#cfn-pinpoint-segment-segmentdimensions-location-country
            """
            return self._values.get('country')

        @property
        def gps_point(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnSegment.GPSPointProperty"]]]:
            """``CfnSegment.LocationProperty.GPSPoint``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-segment-segmentdimensions-location.html#cfn-pinpoint-segment-segmentdimensions-location-gpspoint
            """
            return self._values.get('gps_point')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'LocationProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-pinpoint.CfnSegment.RecencyProperty", jsii_struct_bases=[], name_mapping={'duration': 'duration', 'recency_type': 'recencyType'})
    class RecencyProperty():
        def __init__(self, *, duration: str, recency_type: str):
            """
            :param duration: ``CfnSegment.RecencyProperty.Duration``.
            :param recency_type: ``CfnSegment.RecencyProperty.RecencyType``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-segment-segmentdimensions-behavior-recency.html
            """
            self._values = {
                'duration': duration,
                'recency_type': recency_type,
            }

        @property
        def duration(self) -> str:
            """``CfnSegment.RecencyProperty.Duration``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-segment-segmentdimensions-behavior-recency.html#cfn-pinpoint-segment-segmentdimensions-behavior-recency-duration
            """
            return self._values.get('duration')

        @property
        def recency_type(self) -> str:
            """``CfnSegment.RecencyProperty.RecencyType``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-segment-segmentdimensions-behavior-recency.html#cfn-pinpoint-segment-segmentdimensions-behavior-recency-recencytype
            """
            return self._values.get('recency_type')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'RecencyProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-pinpoint.CfnSegment.SegmentDimensionsProperty", jsii_struct_bases=[], name_mapping={'attributes': 'attributes', 'behavior': 'behavior', 'demographic': 'demographic', 'location': 'location', 'metrics': 'metrics', 'user_attributes': 'userAttributes'})
    class SegmentDimensionsProperty():
        def __init__(self, *, attributes: typing.Any=None, behavior: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnSegment.BehaviorProperty"]]]=None, demographic: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnSegment.DemographicProperty"]]]=None, location: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnSegment.LocationProperty"]]]=None, metrics: typing.Any=None, user_attributes: typing.Any=None):
            """
            :param attributes: ``CfnSegment.SegmentDimensionsProperty.Attributes``.
            :param behavior: ``CfnSegment.SegmentDimensionsProperty.Behavior``.
            :param demographic: ``CfnSegment.SegmentDimensionsProperty.Demographic``.
            :param location: ``CfnSegment.SegmentDimensionsProperty.Location``.
            :param metrics: ``CfnSegment.SegmentDimensionsProperty.Metrics``.
            :param user_attributes: ``CfnSegment.SegmentDimensionsProperty.UserAttributes``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-segment-segmentdimensions.html
            """
            self._values = {
            }
            if attributes is not None: self._values["attributes"] = attributes
            if behavior is not None: self._values["behavior"] = behavior
            if demographic is not None: self._values["demographic"] = demographic
            if location is not None: self._values["location"] = location
            if metrics is not None: self._values["metrics"] = metrics
            if user_attributes is not None: self._values["user_attributes"] = user_attributes

        @property
        def attributes(self) -> typing.Any:
            """``CfnSegment.SegmentDimensionsProperty.Attributes``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-segment-segmentdimensions.html#cfn-pinpoint-segment-segmentdimensions-attributes
            """
            return self._values.get('attributes')

        @property
        def behavior(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnSegment.BehaviorProperty"]]]:
            """``CfnSegment.SegmentDimensionsProperty.Behavior``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-segment-segmentdimensions.html#cfn-pinpoint-segment-segmentdimensions-behavior
            """
            return self._values.get('behavior')

        @property
        def demographic(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnSegment.DemographicProperty"]]]:
            """``CfnSegment.SegmentDimensionsProperty.Demographic``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-segment-segmentdimensions.html#cfn-pinpoint-segment-segmentdimensions-demographic
            """
            return self._values.get('demographic')

        @property
        def location(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnSegment.LocationProperty"]]]:
            """``CfnSegment.SegmentDimensionsProperty.Location``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-segment-segmentdimensions.html#cfn-pinpoint-segment-segmentdimensions-location
            """
            return self._values.get('location')

        @property
        def metrics(self) -> typing.Any:
            """``CfnSegment.SegmentDimensionsProperty.Metrics``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-segment-segmentdimensions.html#cfn-pinpoint-segment-segmentdimensions-metrics
            """
            return self._values.get('metrics')

        @property
        def user_attributes(self) -> typing.Any:
            """``CfnSegment.SegmentDimensionsProperty.UserAttributes``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-segment-segmentdimensions.html#cfn-pinpoint-segment-segmentdimensions-userattributes
            """
            return self._values.get('user_attributes')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'SegmentDimensionsProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-pinpoint.CfnSegment.SegmentGroupsProperty", jsii_struct_bases=[], name_mapping={'groups': 'groups', 'include': 'include'})
    class SegmentGroupsProperty():
        def __init__(self, *, groups: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnSegment.GroupsProperty"]]]]]=None, include: typing.Optional[str]=None):
            """
            :param groups: ``CfnSegment.SegmentGroupsProperty.Groups``.
            :param include: ``CfnSegment.SegmentGroupsProperty.Include``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-segment-segmentgroups.html
            """
            self._values = {
            }
            if groups is not None: self._values["groups"] = groups
            if include is not None: self._values["include"] = include

        @property
        def groups(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnSegment.GroupsProperty"]]]]]:
            """``CfnSegment.SegmentGroupsProperty.Groups``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-segment-segmentgroups.html#cfn-pinpoint-segment-segmentgroups-groups
            """
            return self._values.get('groups')

        @property
        def include(self) -> typing.Optional[str]:
            """``CfnSegment.SegmentGroupsProperty.Include``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-segment-segmentgroups.html#cfn-pinpoint-segment-segmentgroups-include
            """
            return self._values.get('include')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'SegmentGroupsProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-pinpoint.CfnSegment.SetDimensionProperty", jsii_struct_bases=[], name_mapping={'dimension_type': 'dimensionType', 'values': 'values'})
    class SetDimensionProperty():
        def __init__(self, *, dimension_type: typing.Optional[str]=None, values: typing.Optional[typing.List[str]]=None):
            """
            :param dimension_type: ``CfnSegment.SetDimensionProperty.DimensionType``.
            :param values: ``CfnSegment.SetDimensionProperty.Values``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-segment-setdimension.html
            """
            self._values = {
            }
            if dimension_type is not None: self._values["dimension_type"] = dimension_type
            if values is not None: self._values["values"] = values

        @property
        def dimension_type(self) -> typing.Optional[str]:
            """``CfnSegment.SetDimensionProperty.DimensionType``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-segment-setdimension.html#cfn-pinpoint-segment-setdimension-dimensiontype
            """
            return self._values.get('dimension_type')

        @property
        def values(self) -> typing.Optional[typing.List[str]]:
            """``CfnSegment.SetDimensionProperty.Values``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-segment-setdimension.html#cfn-pinpoint-segment-setdimension-values
            """
            return self._values.get('values')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'SetDimensionProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-pinpoint.CfnSegment.SourceSegmentsProperty", jsii_struct_bases=[], name_mapping={'id': 'id', 'version': 'version'})
    class SourceSegmentsProperty():
        def __init__(self, *, id: str, version: typing.Optional[jsii.Number]=None):
            """
            :param id: ``CfnSegment.SourceSegmentsProperty.Id``.
            :param version: ``CfnSegment.SourceSegmentsProperty.Version``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-segment-segmentgroups-groups-sourcesegments.html
            """
            self._values = {
                'id': id,
            }
            if version is not None: self._values["version"] = version

        @property
        def id(self) -> str:
            """``CfnSegment.SourceSegmentsProperty.Id``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-segment-segmentgroups-groups-sourcesegments.html#cfn-pinpoint-segment-segmentgroups-groups-sourcesegments-id
            """
            return self._values.get('id')

        @property
        def version(self) -> typing.Optional[jsii.Number]:
            """``CfnSegment.SourceSegmentsProperty.Version``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpoint-segment-segmentgroups-groups-sourcesegments.html#cfn-pinpoint-segment-segmentgroups-groups-sourcesegments-version
            """
            return self._values.get('version')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'SourceSegmentsProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



@jsii.data_type(jsii_type="@aws-cdk/aws-pinpoint.CfnSegmentProps", jsii_struct_bases=[], name_mapping={'application_id': 'applicationId', 'name': 'name', 'dimensions': 'dimensions', 'segment_groups': 'segmentGroups', 'tags': 'tags'})
class CfnSegmentProps():
    def __init__(self, *, application_id: str, name: str, dimensions: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnSegment.SegmentDimensionsProperty"]]]=None, segment_groups: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnSegment.SegmentGroupsProperty"]]]=None, tags: typing.Any=None):
        """Properties for defining a ``AWS::Pinpoint::Segment``.

        :param application_id: ``AWS::Pinpoint::Segment.ApplicationId``.
        :param name: ``AWS::Pinpoint::Segment.Name``.
        :param dimensions: ``AWS::Pinpoint::Segment.Dimensions``.
        :param segment_groups: ``AWS::Pinpoint::Segment.SegmentGroups``.
        :param tags: ``AWS::Pinpoint::Segment.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-segment.html
        """
        self._values = {
            'application_id': application_id,
            'name': name,
        }
        if dimensions is not None: self._values["dimensions"] = dimensions
        if segment_groups is not None: self._values["segment_groups"] = segment_groups
        if tags is not None: self._values["tags"] = tags

    @property
    def application_id(self) -> str:
        """``AWS::Pinpoint::Segment.ApplicationId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-segment.html#cfn-pinpoint-segment-applicationid
        """
        return self._values.get('application_id')

    @property
    def name(self) -> str:
        """``AWS::Pinpoint::Segment.Name``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-segment.html#cfn-pinpoint-segment-name
        """
        return self._values.get('name')

    @property
    def dimensions(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnSegment.SegmentDimensionsProperty"]]]:
        """``AWS::Pinpoint::Segment.Dimensions``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-segment.html#cfn-pinpoint-segment-dimensions
        """
        return self._values.get('dimensions')

    @property
    def segment_groups(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnSegment.SegmentGroupsProperty"]]]:
        """``AWS::Pinpoint::Segment.SegmentGroups``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-segment.html#cfn-pinpoint-segment-segmentgroups
        """
        return self._values.get('segment_groups')

    @property
    def tags(self) -> typing.Any:
        """``AWS::Pinpoint::Segment.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-segment.html#cfn-pinpoint-segment-tags
        """
        return self._values.get('tags')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnSegmentProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnVoiceChannel(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-pinpoint.CfnVoiceChannel"):
    """A CloudFormation ``AWS::Pinpoint::VoiceChannel``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-voicechannel.html
    cloudformationResource:
    :cloudformationResource:: AWS::Pinpoint::VoiceChannel
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, application_id: str, enabled: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None) -> None:
        """Create a new ``AWS::Pinpoint::VoiceChannel``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param application_id: ``AWS::Pinpoint::VoiceChannel.ApplicationId``.
        :param enabled: ``AWS::Pinpoint::VoiceChannel.Enabled``.
        """
        props = CfnVoiceChannelProps(application_id=application_id, enabled=enabled)

        jsii.create(CfnVoiceChannel, self, [scope, id, props])

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
    @jsii.member(jsii_name="applicationId")
    def application_id(self) -> str:
        """``AWS::Pinpoint::VoiceChannel.ApplicationId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-voicechannel.html#cfn-pinpoint-voicechannel-applicationid
        """
        return jsii.get(self, "applicationId")

    @application_id.setter
    def application_id(self, value: str):
        return jsii.set(self, "applicationId", value)

    @property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::Pinpoint::VoiceChannel.Enabled``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-voicechannel.html#cfn-pinpoint-voicechannel-enabled
        """
        return jsii.get(self, "enabled")

    @enabled.setter
    def enabled(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "enabled", value)


@jsii.data_type(jsii_type="@aws-cdk/aws-pinpoint.CfnVoiceChannelProps", jsii_struct_bases=[], name_mapping={'application_id': 'applicationId', 'enabled': 'enabled'})
class CfnVoiceChannelProps():
    def __init__(self, *, application_id: str, enabled: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None):
        """Properties for defining a ``AWS::Pinpoint::VoiceChannel``.

        :param application_id: ``AWS::Pinpoint::VoiceChannel.ApplicationId``.
        :param enabled: ``AWS::Pinpoint::VoiceChannel.Enabled``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-voicechannel.html
        """
        self._values = {
            'application_id': application_id,
        }
        if enabled is not None: self._values["enabled"] = enabled

    @property
    def application_id(self) -> str:
        """``AWS::Pinpoint::VoiceChannel.ApplicationId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-voicechannel.html#cfn-pinpoint-voicechannel-applicationid
        """
        return self._values.get('application_id')

    @property
    def enabled(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::Pinpoint::VoiceChannel.Enabled``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpoint-voicechannel.html#cfn-pinpoint-voicechannel-enabled
        """
        return self._values.get('enabled')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnVoiceChannelProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


__all__ = ["CfnADMChannel", "CfnADMChannelProps", "CfnAPNSChannel", "CfnAPNSChannelProps", "CfnAPNSSandboxChannel", "CfnAPNSSandboxChannelProps", "CfnAPNSVoipChannel", "CfnAPNSVoipChannelProps", "CfnAPNSVoipSandboxChannel", "CfnAPNSVoipSandboxChannelProps", "CfnApp", "CfnAppProps", "CfnApplicationSettings", "CfnApplicationSettingsProps", "CfnBaiduChannel", "CfnBaiduChannelProps", "CfnCampaign", "CfnCampaignProps", "CfnEmailChannel", "CfnEmailChannelProps", "CfnEventStream", "CfnEventStreamProps", "CfnGCMChannel", "CfnGCMChannelProps", "CfnSMSChannel", "CfnSMSChannelProps", "CfnSegment", "CfnSegmentProps", "CfnVoiceChannel", "CfnVoiceChannelProps", "__jsii_assembly__"]

publication.publish()
