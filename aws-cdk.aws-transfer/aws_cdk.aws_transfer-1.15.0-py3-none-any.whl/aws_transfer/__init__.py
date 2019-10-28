import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.core
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-transfer", "1.15.0", __name__, "aws-transfer@1.15.0.jsii.tgz")
class CfnServer(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-transfer.CfnServer"):
    """A CloudFormation ``AWS::Transfer::Server``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-transfer-server.html
    cloudformationResource:
    :cloudformationResource:: AWS::Transfer::Server
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, endpoint_details: typing.Optional[typing.Union[typing.Optional["EndpointDetailsProperty"], typing.Optional[aws_cdk.core.IResolvable]]]=None, endpoint_type: typing.Optional[str]=None, identity_provider_details: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["IdentityProviderDetailsProperty"]]]=None, identity_provider_type: typing.Optional[str]=None, logging_role: typing.Optional[str]=None, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None) -> None:
        """Create a new ``AWS::Transfer::Server``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param endpoint_details: ``AWS::Transfer::Server.EndpointDetails``.
        :param endpoint_type: ``AWS::Transfer::Server.EndpointType``.
        :param identity_provider_details: ``AWS::Transfer::Server.IdentityProviderDetails``.
        :param identity_provider_type: ``AWS::Transfer::Server.IdentityProviderType``.
        :param logging_role: ``AWS::Transfer::Server.LoggingRole``.
        :param tags: ``AWS::Transfer::Server.Tags``.
        """
        props = CfnServerProps(endpoint_details=endpoint_details, endpoint_type=endpoint_type, identity_provider_details=identity_provider_details, identity_provider_type=identity_provider_type, logging_role=logging_role, tags=tags)

        jsii.create(CfnServer, self, [scope, id, props])

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
    @jsii.member(jsii_name="attrServerId")
    def attr_server_id(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: ServerId
        """
        return jsii.get(self, "attrServerId")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        """``AWS::Transfer::Server.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-transfer-server.html#cfn-transfer-server-tags
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="endpointDetails")
    def endpoint_details(self) -> typing.Optional[typing.Union[typing.Optional["EndpointDetailsProperty"], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::Transfer::Server.EndpointDetails``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-transfer-server.html#cfn-transfer-server-endpointdetails
        """
        return jsii.get(self, "endpointDetails")

    @endpoint_details.setter
    def endpoint_details(self, value: typing.Optional[typing.Union[typing.Optional["EndpointDetailsProperty"], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "endpointDetails", value)

    @property
    @jsii.member(jsii_name="endpointType")
    def endpoint_type(self) -> typing.Optional[str]:
        """``AWS::Transfer::Server.EndpointType``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-transfer-server.html#cfn-transfer-server-endpointtype
        """
        return jsii.get(self, "endpointType")

    @endpoint_type.setter
    def endpoint_type(self, value: typing.Optional[str]):
        return jsii.set(self, "endpointType", value)

    @property
    @jsii.member(jsii_name="identityProviderDetails")
    def identity_provider_details(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["IdentityProviderDetailsProperty"]]]:
        """``AWS::Transfer::Server.IdentityProviderDetails``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-transfer-server.html#cfn-transfer-server-identityproviderdetails
        """
        return jsii.get(self, "identityProviderDetails")

    @identity_provider_details.setter
    def identity_provider_details(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["IdentityProviderDetailsProperty"]]]):
        return jsii.set(self, "identityProviderDetails", value)

    @property
    @jsii.member(jsii_name="identityProviderType")
    def identity_provider_type(self) -> typing.Optional[str]:
        """``AWS::Transfer::Server.IdentityProviderType``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-transfer-server.html#cfn-transfer-server-identityprovidertype
        """
        return jsii.get(self, "identityProviderType")

    @identity_provider_type.setter
    def identity_provider_type(self, value: typing.Optional[str]):
        return jsii.set(self, "identityProviderType", value)

    @property
    @jsii.member(jsii_name="loggingRole")
    def logging_role(self) -> typing.Optional[str]:
        """``AWS::Transfer::Server.LoggingRole``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-transfer-server.html#cfn-transfer-server-loggingrole
        """
        return jsii.get(self, "loggingRole")

    @logging_role.setter
    def logging_role(self, value: typing.Optional[str]):
        return jsii.set(self, "loggingRole", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-transfer.CfnServer.EndpointDetailsProperty", jsii_struct_bases=[], name_mapping={'vpc_endpoint_id': 'vpcEndpointId'})
    class EndpointDetailsProperty():
        def __init__(self, *, vpc_endpoint_id: str):
            """
            :param vpc_endpoint_id: ``CfnServer.EndpointDetailsProperty.VpcEndpointId``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-transfer-server-endpointdetails.html
            """
            self._values = {
                'vpc_endpoint_id': vpc_endpoint_id,
            }

        @property
        def vpc_endpoint_id(self) -> str:
            """``CfnServer.EndpointDetailsProperty.VpcEndpointId``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-transfer-server-endpointdetails.html#cfn-transfer-server-endpointdetails-vpcendpointid
            """
            return self._values.get('vpc_endpoint_id')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'EndpointDetailsProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-transfer.CfnServer.IdentityProviderDetailsProperty", jsii_struct_bases=[], name_mapping={'invocation_role': 'invocationRole', 'url': 'url'})
    class IdentityProviderDetailsProperty():
        def __init__(self, *, invocation_role: str, url: str):
            """
            :param invocation_role: ``CfnServer.IdentityProviderDetailsProperty.InvocationRole``.
            :param url: ``CfnServer.IdentityProviderDetailsProperty.Url``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-transfer-server-identityproviderdetails.html
            """
            self._values = {
                'invocation_role': invocation_role,
                'url': url,
            }

        @property
        def invocation_role(self) -> str:
            """``CfnServer.IdentityProviderDetailsProperty.InvocationRole``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-transfer-server-identityproviderdetails.html#cfn-transfer-server-identityproviderdetails-invocationrole
            """
            return self._values.get('invocation_role')

        @property
        def url(self) -> str:
            """``CfnServer.IdentityProviderDetailsProperty.Url``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-transfer-server-identityproviderdetails.html#cfn-transfer-server-identityproviderdetails-url
            """
            return self._values.get('url')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'IdentityProviderDetailsProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



@jsii.data_type(jsii_type="@aws-cdk/aws-transfer.CfnServerProps", jsii_struct_bases=[], name_mapping={'endpoint_details': 'endpointDetails', 'endpoint_type': 'endpointType', 'identity_provider_details': 'identityProviderDetails', 'identity_provider_type': 'identityProviderType', 'logging_role': 'loggingRole', 'tags': 'tags'})
class CfnServerProps():
    def __init__(self, *, endpoint_details: typing.Optional[typing.Union[typing.Optional["CfnServer.EndpointDetailsProperty"], typing.Optional[aws_cdk.core.IResolvable]]]=None, endpoint_type: typing.Optional[str]=None, identity_provider_details: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnServer.IdentityProviderDetailsProperty"]]]=None, identity_provider_type: typing.Optional[str]=None, logging_role: typing.Optional[str]=None, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None):
        """Properties for defining a ``AWS::Transfer::Server``.

        :param endpoint_details: ``AWS::Transfer::Server.EndpointDetails``.
        :param endpoint_type: ``AWS::Transfer::Server.EndpointType``.
        :param identity_provider_details: ``AWS::Transfer::Server.IdentityProviderDetails``.
        :param identity_provider_type: ``AWS::Transfer::Server.IdentityProviderType``.
        :param logging_role: ``AWS::Transfer::Server.LoggingRole``.
        :param tags: ``AWS::Transfer::Server.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-transfer-server.html
        """
        self._values = {
        }
        if endpoint_details is not None: self._values["endpoint_details"] = endpoint_details
        if endpoint_type is not None: self._values["endpoint_type"] = endpoint_type
        if identity_provider_details is not None: self._values["identity_provider_details"] = identity_provider_details
        if identity_provider_type is not None: self._values["identity_provider_type"] = identity_provider_type
        if logging_role is not None: self._values["logging_role"] = logging_role
        if tags is not None: self._values["tags"] = tags

    @property
    def endpoint_details(self) -> typing.Optional[typing.Union[typing.Optional["CfnServer.EndpointDetailsProperty"], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::Transfer::Server.EndpointDetails``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-transfer-server.html#cfn-transfer-server-endpointdetails
        """
        return self._values.get('endpoint_details')

    @property
    def endpoint_type(self) -> typing.Optional[str]:
        """``AWS::Transfer::Server.EndpointType``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-transfer-server.html#cfn-transfer-server-endpointtype
        """
        return self._values.get('endpoint_type')

    @property
    def identity_provider_details(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnServer.IdentityProviderDetailsProperty"]]]:
        """``AWS::Transfer::Server.IdentityProviderDetails``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-transfer-server.html#cfn-transfer-server-identityproviderdetails
        """
        return self._values.get('identity_provider_details')

    @property
    def identity_provider_type(self) -> typing.Optional[str]:
        """``AWS::Transfer::Server.IdentityProviderType``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-transfer-server.html#cfn-transfer-server-identityprovidertype
        """
        return self._values.get('identity_provider_type')

    @property
    def logging_role(self) -> typing.Optional[str]:
        """``AWS::Transfer::Server.LoggingRole``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-transfer-server.html#cfn-transfer-server-loggingrole
        """
        return self._values.get('logging_role')

    @property
    def tags(self) -> typing.Optional[typing.List[aws_cdk.core.CfnTag]]:
        """``AWS::Transfer::Server.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-transfer-server.html#cfn-transfer-server-tags
        """
        return self._values.get('tags')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnServerProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnUser(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-transfer.CfnUser"):
    """A CloudFormation ``AWS::Transfer::User``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-transfer-user.html
    cloudformationResource:
    :cloudformationResource:: AWS::Transfer::User
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, role: str, server_id: str, user_name: str, home_directory: typing.Optional[str]=None, policy: typing.Optional[str]=None, ssh_public_keys: typing.Optional[typing.List[str]]=None, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None) -> None:
        """Create a new ``AWS::Transfer::User``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param role: ``AWS::Transfer::User.Role``.
        :param server_id: ``AWS::Transfer::User.ServerId``.
        :param user_name: ``AWS::Transfer::User.UserName``.
        :param home_directory: ``AWS::Transfer::User.HomeDirectory``.
        :param policy: ``AWS::Transfer::User.Policy``.
        :param ssh_public_keys: ``AWS::Transfer::User.SshPublicKeys``.
        :param tags: ``AWS::Transfer::User.Tags``.
        """
        props = CfnUserProps(role=role, server_id=server_id, user_name=user_name, home_directory=home_directory, policy=policy, ssh_public_keys=ssh_public_keys, tags=tags)

        jsii.create(CfnUser, self, [scope, id, props])

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
    @jsii.member(jsii_name="attrServerId")
    def attr_server_id(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: ServerId
        """
        return jsii.get(self, "attrServerId")

    @property
    @jsii.member(jsii_name="attrUserName")
    def attr_user_name(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: UserName
        """
        return jsii.get(self, "attrUserName")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        """``AWS::Transfer::User.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-transfer-user.html#cfn-transfer-user-tags
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="role")
    def role(self) -> str:
        """``AWS::Transfer::User.Role``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-transfer-user.html#cfn-transfer-user-role
        """
        return jsii.get(self, "role")

    @role.setter
    def role(self, value: str):
        return jsii.set(self, "role", value)

    @property
    @jsii.member(jsii_name="serverId")
    def server_id(self) -> str:
        """``AWS::Transfer::User.ServerId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-transfer-user.html#cfn-transfer-user-serverid
        """
        return jsii.get(self, "serverId")

    @server_id.setter
    def server_id(self, value: str):
        return jsii.set(self, "serverId", value)

    @property
    @jsii.member(jsii_name="userName")
    def user_name(self) -> str:
        """``AWS::Transfer::User.UserName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-transfer-user.html#cfn-transfer-user-username
        """
        return jsii.get(self, "userName")

    @user_name.setter
    def user_name(self, value: str):
        return jsii.set(self, "userName", value)

    @property
    @jsii.member(jsii_name="homeDirectory")
    def home_directory(self) -> typing.Optional[str]:
        """``AWS::Transfer::User.HomeDirectory``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-transfer-user.html#cfn-transfer-user-homedirectory
        """
        return jsii.get(self, "homeDirectory")

    @home_directory.setter
    def home_directory(self, value: typing.Optional[str]):
        return jsii.set(self, "homeDirectory", value)

    @property
    @jsii.member(jsii_name="policy")
    def policy(self) -> typing.Optional[str]:
        """``AWS::Transfer::User.Policy``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-transfer-user.html#cfn-transfer-user-policy
        """
        return jsii.get(self, "policy")

    @policy.setter
    def policy(self, value: typing.Optional[str]):
        return jsii.set(self, "policy", value)

    @property
    @jsii.member(jsii_name="sshPublicKeys")
    def ssh_public_keys(self) -> typing.Optional[typing.List[str]]:
        """``AWS::Transfer::User.SshPublicKeys``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-transfer-user.html#cfn-transfer-user-sshpublickeys
        """
        return jsii.get(self, "sshPublicKeys")

    @ssh_public_keys.setter
    def ssh_public_keys(self, value: typing.Optional[typing.List[str]]):
        return jsii.set(self, "sshPublicKeys", value)


@jsii.data_type(jsii_type="@aws-cdk/aws-transfer.CfnUserProps", jsii_struct_bases=[], name_mapping={'role': 'role', 'server_id': 'serverId', 'user_name': 'userName', 'home_directory': 'homeDirectory', 'policy': 'policy', 'ssh_public_keys': 'sshPublicKeys', 'tags': 'tags'})
class CfnUserProps():
    def __init__(self, *, role: str, server_id: str, user_name: str, home_directory: typing.Optional[str]=None, policy: typing.Optional[str]=None, ssh_public_keys: typing.Optional[typing.List[str]]=None, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None):
        """Properties for defining a ``AWS::Transfer::User``.

        :param role: ``AWS::Transfer::User.Role``.
        :param server_id: ``AWS::Transfer::User.ServerId``.
        :param user_name: ``AWS::Transfer::User.UserName``.
        :param home_directory: ``AWS::Transfer::User.HomeDirectory``.
        :param policy: ``AWS::Transfer::User.Policy``.
        :param ssh_public_keys: ``AWS::Transfer::User.SshPublicKeys``.
        :param tags: ``AWS::Transfer::User.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-transfer-user.html
        """
        self._values = {
            'role': role,
            'server_id': server_id,
            'user_name': user_name,
        }
        if home_directory is not None: self._values["home_directory"] = home_directory
        if policy is not None: self._values["policy"] = policy
        if ssh_public_keys is not None: self._values["ssh_public_keys"] = ssh_public_keys
        if tags is not None: self._values["tags"] = tags

    @property
    def role(self) -> str:
        """``AWS::Transfer::User.Role``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-transfer-user.html#cfn-transfer-user-role
        """
        return self._values.get('role')

    @property
    def server_id(self) -> str:
        """``AWS::Transfer::User.ServerId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-transfer-user.html#cfn-transfer-user-serverid
        """
        return self._values.get('server_id')

    @property
    def user_name(self) -> str:
        """``AWS::Transfer::User.UserName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-transfer-user.html#cfn-transfer-user-username
        """
        return self._values.get('user_name')

    @property
    def home_directory(self) -> typing.Optional[str]:
        """``AWS::Transfer::User.HomeDirectory``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-transfer-user.html#cfn-transfer-user-homedirectory
        """
        return self._values.get('home_directory')

    @property
    def policy(self) -> typing.Optional[str]:
        """``AWS::Transfer::User.Policy``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-transfer-user.html#cfn-transfer-user-policy
        """
        return self._values.get('policy')

    @property
    def ssh_public_keys(self) -> typing.Optional[typing.List[str]]:
        """``AWS::Transfer::User.SshPublicKeys``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-transfer-user.html#cfn-transfer-user-sshpublickeys
        """
        return self._values.get('ssh_public_keys')

    @property
    def tags(self) -> typing.Optional[typing.List[aws_cdk.core.CfnTag]]:
        """``AWS::Transfer::User.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-transfer-user.html#cfn-transfer-user-tags
        """
        return self._values.get('tags')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnUserProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


__all__ = ["CfnServer", "CfnServerProps", "CfnUser", "CfnUserProps", "__jsii_assembly__"]

publication.publish()
