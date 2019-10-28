import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.core
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-route53resolver", "1.15.0", __name__, "aws-route53resolver@1.15.0.jsii.tgz")
class CfnResolverEndpoint(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-route53resolver.CfnResolverEndpoint"):
    """A CloudFormation ``AWS::Route53Resolver::ResolverEndpoint``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverendpoint.html
    cloudformationResource:
    :cloudformationResource:: AWS::Route53Resolver::ResolverEndpoint
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, direction: str, ip_addresses: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union["IpAddressRequestProperty", aws_cdk.core.IResolvable]]], security_group_ids: typing.List[str], name: typing.Optional[str]=None, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None) -> None:
        """Create a new ``AWS::Route53Resolver::ResolverEndpoint``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param direction: ``AWS::Route53Resolver::ResolverEndpoint.Direction``.
        :param ip_addresses: ``AWS::Route53Resolver::ResolverEndpoint.IpAddresses``.
        :param security_group_ids: ``AWS::Route53Resolver::ResolverEndpoint.SecurityGroupIds``.
        :param name: ``AWS::Route53Resolver::ResolverEndpoint.Name``.
        :param tags: ``AWS::Route53Resolver::ResolverEndpoint.Tags``.
        """
        props = CfnResolverEndpointProps(direction=direction, ip_addresses=ip_addresses, security_group_ids=security_group_ids, name=name, tags=tags)

        jsii.create(CfnResolverEndpoint, self, [scope, id, props])

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
    @jsii.member(jsii_name="attrDirection")
    def attr_direction(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: Direction
        """
        return jsii.get(self, "attrDirection")

    @property
    @jsii.member(jsii_name="attrHostVpcId")
    def attr_host_vpc_id(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: HostVPCId
        """
        return jsii.get(self, "attrHostVpcId")

    @property
    @jsii.member(jsii_name="attrIpAddressCount")
    def attr_ip_address_count(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: IpAddressCount
        """
        return jsii.get(self, "attrIpAddressCount")

    @property
    @jsii.member(jsii_name="attrName")
    def attr_name(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: Name
        """
        return jsii.get(self, "attrName")

    @property
    @jsii.member(jsii_name="attrResolverEndpointId")
    def attr_resolver_endpoint_id(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: ResolverEndpointId
        """
        return jsii.get(self, "attrResolverEndpointId")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        """``AWS::Route53Resolver::ResolverEndpoint.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverendpoint.html#cfn-route53resolver-resolverendpoint-tags
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="direction")
    def direction(self) -> str:
        """``AWS::Route53Resolver::ResolverEndpoint.Direction``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverendpoint.html#cfn-route53resolver-resolverendpoint-direction
        """
        return jsii.get(self, "direction")

    @direction.setter
    def direction(self, value: str):
        return jsii.set(self, "direction", value)

    @property
    @jsii.member(jsii_name="ipAddresses")
    def ip_addresses(self) -> typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union["IpAddressRequestProperty", aws_cdk.core.IResolvable]]]:
        """``AWS::Route53Resolver::ResolverEndpoint.IpAddresses``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverendpoint.html#cfn-route53resolver-resolverendpoint-ipaddresses
        """
        return jsii.get(self, "ipAddresses")

    @ip_addresses.setter
    def ip_addresses(self, value: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union["IpAddressRequestProperty", aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "ipAddresses", value)

    @property
    @jsii.member(jsii_name="securityGroupIds")
    def security_group_ids(self) -> typing.List[str]:
        """``AWS::Route53Resolver::ResolverEndpoint.SecurityGroupIds``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverendpoint.html#cfn-route53resolver-resolverendpoint-securitygroupids
        """
        return jsii.get(self, "securityGroupIds")

    @security_group_ids.setter
    def security_group_ids(self, value: typing.List[str]):
        return jsii.set(self, "securityGroupIds", value)

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[str]:
        """``AWS::Route53Resolver::ResolverEndpoint.Name``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverendpoint.html#cfn-route53resolver-resolverendpoint-name
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: typing.Optional[str]):
        return jsii.set(self, "name", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-route53resolver.CfnResolverEndpoint.IpAddressRequestProperty", jsii_struct_bases=[], name_mapping={'subnet_id': 'subnetId', 'ip': 'ip'})
    class IpAddressRequestProperty():
        def __init__(self, *, subnet_id: str, ip: typing.Optional[str]=None):
            """
            :param subnet_id: ``CfnResolverEndpoint.IpAddressRequestProperty.SubnetId``.
            :param ip: ``CfnResolverEndpoint.IpAddressRequestProperty.Ip``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53resolver-resolverendpoint-ipaddressrequest.html
            """
            self._values = {
                'subnet_id': subnet_id,
            }
            if ip is not None: self._values["ip"] = ip

        @property
        def subnet_id(self) -> str:
            """``CfnResolverEndpoint.IpAddressRequestProperty.SubnetId``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53resolver-resolverendpoint-ipaddressrequest.html#cfn-route53resolver-resolverendpoint-ipaddressrequest-subnetid
            """
            return self._values.get('subnet_id')

        @property
        def ip(self) -> typing.Optional[str]:
            """``CfnResolverEndpoint.IpAddressRequestProperty.Ip``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53resolver-resolverendpoint-ipaddressrequest.html#cfn-route53resolver-resolverendpoint-ipaddressrequest-ip
            """
            return self._values.get('ip')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'IpAddressRequestProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



@jsii.data_type(jsii_type="@aws-cdk/aws-route53resolver.CfnResolverEndpointProps", jsii_struct_bases=[], name_mapping={'direction': 'direction', 'ip_addresses': 'ipAddresses', 'security_group_ids': 'securityGroupIds', 'name': 'name', 'tags': 'tags'})
class CfnResolverEndpointProps():
    def __init__(self, *, direction: str, ip_addresses: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union["CfnResolverEndpoint.IpAddressRequestProperty", aws_cdk.core.IResolvable]]], security_group_ids: typing.List[str], name: typing.Optional[str]=None, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None):
        """Properties for defining a ``AWS::Route53Resolver::ResolverEndpoint``.

        :param direction: ``AWS::Route53Resolver::ResolverEndpoint.Direction``.
        :param ip_addresses: ``AWS::Route53Resolver::ResolverEndpoint.IpAddresses``.
        :param security_group_ids: ``AWS::Route53Resolver::ResolverEndpoint.SecurityGroupIds``.
        :param name: ``AWS::Route53Resolver::ResolverEndpoint.Name``.
        :param tags: ``AWS::Route53Resolver::ResolverEndpoint.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverendpoint.html
        """
        self._values = {
            'direction': direction,
            'ip_addresses': ip_addresses,
            'security_group_ids': security_group_ids,
        }
        if name is not None: self._values["name"] = name
        if tags is not None: self._values["tags"] = tags

    @property
    def direction(self) -> str:
        """``AWS::Route53Resolver::ResolverEndpoint.Direction``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverendpoint.html#cfn-route53resolver-resolverendpoint-direction
        """
        return self._values.get('direction')

    @property
    def ip_addresses(self) -> typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union["CfnResolverEndpoint.IpAddressRequestProperty", aws_cdk.core.IResolvable]]]:
        """``AWS::Route53Resolver::ResolverEndpoint.IpAddresses``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverendpoint.html#cfn-route53resolver-resolverendpoint-ipaddresses
        """
        return self._values.get('ip_addresses')

    @property
    def security_group_ids(self) -> typing.List[str]:
        """``AWS::Route53Resolver::ResolverEndpoint.SecurityGroupIds``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverendpoint.html#cfn-route53resolver-resolverendpoint-securitygroupids
        """
        return self._values.get('security_group_ids')

    @property
    def name(self) -> typing.Optional[str]:
        """``AWS::Route53Resolver::ResolverEndpoint.Name``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverendpoint.html#cfn-route53resolver-resolverendpoint-name
        """
        return self._values.get('name')

    @property
    def tags(self) -> typing.Optional[typing.List[aws_cdk.core.CfnTag]]:
        """``AWS::Route53Resolver::ResolverEndpoint.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverendpoint.html#cfn-route53resolver-resolverendpoint-tags
        """
        return self._values.get('tags')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnResolverEndpointProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnResolverRule(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-route53resolver.CfnResolverRule"):
    """A CloudFormation ``AWS::Route53Resolver::ResolverRule``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverrule.html
    cloudformationResource:
    :cloudformationResource:: AWS::Route53Resolver::ResolverRule
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, domain_name: str, rule_type: str, name: typing.Optional[str]=None, resolver_endpoint_id: typing.Optional[str]=None, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None, target_ips: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "TargetAddressProperty"]]]]]=None) -> None:
        """Create a new ``AWS::Route53Resolver::ResolverRule``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param domain_name: ``AWS::Route53Resolver::ResolverRule.DomainName``.
        :param rule_type: ``AWS::Route53Resolver::ResolverRule.RuleType``.
        :param name: ``AWS::Route53Resolver::ResolverRule.Name``.
        :param resolver_endpoint_id: ``AWS::Route53Resolver::ResolverRule.ResolverEndpointId``.
        :param tags: ``AWS::Route53Resolver::ResolverRule.Tags``.
        :param target_ips: ``AWS::Route53Resolver::ResolverRule.TargetIps``.
        """
        props = CfnResolverRuleProps(domain_name=domain_name, rule_type=rule_type, name=name, resolver_endpoint_id=resolver_endpoint_id, tags=tags, target_ips=target_ips)

        jsii.create(CfnResolverRule, self, [scope, id, props])

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
    @jsii.member(jsii_name="attrDomainName")
    def attr_domain_name(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: DomainName
        """
        return jsii.get(self, "attrDomainName")

    @property
    @jsii.member(jsii_name="attrName")
    def attr_name(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: Name
        """
        return jsii.get(self, "attrName")

    @property
    @jsii.member(jsii_name="attrResolverEndpointId")
    def attr_resolver_endpoint_id(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: ResolverEndpointId
        """
        return jsii.get(self, "attrResolverEndpointId")

    @property
    @jsii.member(jsii_name="attrResolverRuleId")
    def attr_resolver_rule_id(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: ResolverRuleId
        """
        return jsii.get(self, "attrResolverRuleId")

    @property
    @jsii.member(jsii_name="attrTargetIps")
    def attr_target_ips(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: TargetIps
        """
        return jsii.get(self, "attrTargetIps")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        """``AWS::Route53Resolver::ResolverRule.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverrule.html#cfn-route53resolver-resolverrule-tags
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="domainName")
    def domain_name(self) -> str:
        """``AWS::Route53Resolver::ResolverRule.DomainName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverrule.html#cfn-route53resolver-resolverrule-domainname
        """
        return jsii.get(self, "domainName")

    @domain_name.setter
    def domain_name(self, value: str):
        return jsii.set(self, "domainName", value)

    @property
    @jsii.member(jsii_name="ruleType")
    def rule_type(self) -> str:
        """``AWS::Route53Resolver::ResolverRule.RuleType``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverrule.html#cfn-route53resolver-resolverrule-ruletype
        """
        return jsii.get(self, "ruleType")

    @rule_type.setter
    def rule_type(self, value: str):
        return jsii.set(self, "ruleType", value)

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[str]:
        """``AWS::Route53Resolver::ResolverRule.Name``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverrule.html#cfn-route53resolver-resolverrule-name
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: typing.Optional[str]):
        return jsii.set(self, "name", value)

    @property
    @jsii.member(jsii_name="resolverEndpointId")
    def resolver_endpoint_id(self) -> typing.Optional[str]:
        """``AWS::Route53Resolver::ResolverRule.ResolverEndpointId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverrule.html#cfn-route53resolver-resolverrule-resolverendpointid
        """
        return jsii.get(self, "resolverEndpointId")

    @resolver_endpoint_id.setter
    def resolver_endpoint_id(self, value: typing.Optional[str]):
        return jsii.set(self, "resolverEndpointId", value)

    @property
    @jsii.member(jsii_name="targetIps")
    def target_ips(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "TargetAddressProperty"]]]]]:
        """``AWS::Route53Resolver::ResolverRule.TargetIps``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverrule.html#cfn-route53resolver-resolverrule-targetips
        """
        return jsii.get(self, "targetIps")

    @target_ips.setter
    def target_ips(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "TargetAddressProperty"]]]]]):
        return jsii.set(self, "targetIps", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-route53resolver.CfnResolverRule.TargetAddressProperty", jsii_struct_bases=[], name_mapping={'ip': 'ip', 'port': 'port'})
    class TargetAddressProperty():
        def __init__(self, *, ip: str, port: typing.Optional[str]=None):
            """
            :param ip: ``CfnResolverRule.TargetAddressProperty.Ip``.
            :param port: ``CfnResolverRule.TargetAddressProperty.Port``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53resolver-resolverrule-targetaddress.html
            """
            self._values = {
                'ip': ip,
            }
            if port is not None: self._values["port"] = port

        @property
        def ip(self) -> str:
            """``CfnResolverRule.TargetAddressProperty.Ip``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53resolver-resolverrule-targetaddress.html#cfn-route53resolver-resolverrule-targetaddress-ip
            """
            return self._values.get('ip')

        @property
        def port(self) -> typing.Optional[str]:
            """``CfnResolverRule.TargetAddressProperty.Port``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53resolver-resolverrule-targetaddress.html#cfn-route53resolver-resolverrule-targetaddress-port
            """
            return self._values.get('port')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'TargetAddressProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



class CfnResolverRuleAssociation(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-route53resolver.CfnResolverRuleAssociation"):
    """A CloudFormation ``AWS::Route53Resolver::ResolverRuleAssociation``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverruleassociation.html
    cloudformationResource:
    :cloudformationResource:: AWS::Route53Resolver::ResolverRuleAssociation
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, resolver_rule_id: str, vpc_id: str, name: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::Route53Resolver::ResolverRuleAssociation``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param resolver_rule_id: ``AWS::Route53Resolver::ResolverRuleAssociation.ResolverRuleId``.
        :param vpc_id: ``AWS::Route53Resolver::ResolverRuleAssociation.VPCId``.
        :param name: ``AWS::Route53Resolver::ResolverRuleAssociation.Name``.
        """
        props = CfnResolverRuleAssociationProps(resolver_rule_id=resolver_rule_id, vpc_id=vpc_id, name=name)

        jsii.create(CfnResolverRuleAssociation, self, [scope, id, props])

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
    @jsii.member(jsii_name="attrName")
    def attr_name(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: Name
        """
        return jsii.get(self, "attrName")

    @property
    @jsii.member(jsii_name="attrResolverRuleAssociationId")
    def attr_resolver_rule_association_id(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: ResolverRuleAssociationId
        """
        return jsii.get(self, "attrResolverRuleAssociationId")

    @property
    @jsii.member(jsii_name="attrResolverRuleId")
    def attr_resolver_rule_id(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: ResolverRuleId
        """
        return jsii.get(self, "attrResolverRuleId")

    @property
    @jsii.member(jsii_name="attrVpcId")
    def attr_vpc_id(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: VPCId
        """
        return jsii.get(self, "attrVpcId")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="resolverRuleId")
    def resolver_rule_id(self) -> str:
        """``AWS::Route53Resolver::ResolverRuleAssociation.ResolverRuleId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverruleassociation.html#cfn-route53resolver-resolverruleassociation-resolverruleid
        """
        return jsii.get(self, "resolverRuleId")

    @resolver_rule_id.setter
    def resolver_rule_id(self, value: str):
        return jsii.set(self, "resolverRuleId", value)

    @property
    @jsii.member(jsii_name="vpcId")
    def vpc_id(self) -> str:
        """``AWS::Route53Resolver::ResolverRuleAssociation.VPCId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverruleassociation.html#cfn-route53resolver-resolverruleassociation-vpcid
        """
        return jsii.get(self, "vpcId")

    @vpc_id.setter
    def vpc_id(self, value: str):
        return jsii.set(self, "vpcId", value)

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[str]:
        """``AWS::Route53Resolver::ResolverRuleAssociation.Name``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverruleassociation.html#cfn-route53resolver-resolverruleassociation-name
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: typing.Optional[str]):
        return jsii.set(self, "name", value)


@jsii.data_type(jsii_type="@aws-cdk/aws-route53resolver.CfnResolverRuleAssociationProps", jsii_struct_bases=[], name_mapping={'resolver_rule_id': 'resolverRuleId', 'vpc_id': 'vpcId', 'name': 'name'})
class CfnResolverRuleAssociationProps():
    def __init__(self, *, resolver_rule_id: str, vpc_id: str, name: typing.Optional[str]=None):
        """Properties for defining a ``AWS::Route53Resolver::ResolverRuleAssociation``.

        :param resolver_rule_id: ``AWS::Route53Resolver::ResolverRuleAssociation.ResolverRuleId``.
        :param vpc_id: ``AWS::Route53Resolver::ResolverRuleAssociation.VPCId``.
        :param name: ``AWS::Route53Resolver::ResolverRuleAssociation.Name``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverruleassociation.html
        """
        self._values = {
            'resolver_rule_id': resolver_rule_id,
            'vpc_id': vpc_id,
        }
        if name is not None: self._values["name"] = name

    @property
    def resolver_rule_id(self) -> str:
        """``AWS::Route53Resolver::ResolverRuleAssociation.ResolverRuleId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverruleassociation.html#cfn-route53resolver-resolverruleassociation-resolverruleid
        """
        return self._values.get('resolver_rule_id')

    @property
    def vpc_id(self) -> str:
        """``AWS::Route53Resolver::ResolverRuleAssociation.VPCId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverruleassociation.html#cfn-route53resolver-resolverruleassociation-vpcid
        """
        return self._values.get('vpc_id')

    @property
    def name(self) -> typing.Optional[str]:
        """``AWS::Route53Resolver::ResolverRuleAssociation.Name``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverruleassociation.html#cfn-route53resolver-resolverruleassociation-name
        """
        return self._values.get('name')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnResolverRuleAssociationProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


@jsii.data_type(jsii_type="@aws-cdk/aws-route53resolver.CfnResolverRuleProps", jsii_struct_bases=[], name_mapping={'domain_name': 'domainName', 'rule_type': 'ruleType', 'name': 'name', 'resolver_endpoint_id': 'resolverEndpointId', 'tags': 'tags', 'target_ips': 'targetIps'})
class CfnResolverRuleProps():
    def __init__(self, *, domain_name: str, rule_type: str, name: typing.Optional[str]=None, resolver_endpoint_id: typing.Optional[str]=None, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None, target_ips: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnResolverRule.TargetAddressProperty"]]]]]=None):
        """Properties for defining a ``AWS::Route53Resolver::ResolverRule``.

        :param domain_name: ``AWS::Route53Resolver::ResolverRule.DomainName``.
        :param rule_type: ``AWS::Route53Resolver::ResolverRule.RuleType``.
        :param name: ``AWS::Route53Resolver::ResolverRule.Name``.
        :param resolver_endpoint_id: ``AWS::Route53Resolver::ResolverRule.ResolverEndpointId``.
        :param tags: ``AWS::Route53Resolver::ResolverRule.Tags``.
        :param target_ips: ``AWS::Route53Resolver::ResolverRule.TargetIps``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverrule.html
        """
        self._values = {
            'domain_name': domain_name,
            'rule_type': rule_type,
        }
        if name is not None: self._values["name"] = name
        if resolver_endpoint_id is not None: self._values["resolver_endpoint_id"] = resolver_endpoint_id
        if tags is not None: self._values["tags"] = tags
        if target_ips is not None: self._values["target_ips"] = target_ips

    @property
    def domain_name(self) -> str:
        """``AWS::Route53Resolver::ResolverRule.DomainName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverrule.html#cfn-route53resolver-resolverrule-domainname
        """
        return self._values.get('domain_name')

    @property
    def rule_type(self) -> str:
        """``AWS::Route53Resolver::ResolverRule.RuleType``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverrule.html#cfn-route53resolver-resolverrule-ruletype
        """
        return self._values.get('rule_type')

    @property
    def name(self) -> typing.Optional[str]:
        """``AWS::Route53Resolver::ResolverRule.Name``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverrule.html#cfn-route53resolver-resolverrule-name
        """
        return self._values.get('name')

    @property
    def resolver_endpoint_id(self) -> typing.Optional[str]:
        """``AWS::Route53Resolver::ResolverRule.ResolverEndpointId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverrule.html#cfn-route53resolver-resolverrule-resolverendpointid
        """
        return self._values.get('resolver_endpoint_id')

    @property
    def tags(self) -> typing.Optional[typing.List[aws_cdk.core.CfnTag]]:
        """``AWS::Route53Resolver::ResolverRule.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverrule.html#cfn-route53resolver-resolverrule-tags
        """
        return self._values.get('tags')

    @property
    def target_ips(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnResolverRule.TargetAddressProperty"]]]]]:
        """``AWS::Route53Resolver::ResolverRule.TargetIps``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverrule.html#cfn-route53resolver-resolverrule-targetips
        """
        return self._values.get('target_ips')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnResolverRuleProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


__all__ = ["CfnResolverEndpoint", "CfnResolverEndpointProps", "CfnResolverRule", "CfnResolverRuleAssociation", "CfnResolverRuleAssociationProps", "CfnResolverRuleProps", "__jsii_assembly__"]

publication.publish()
