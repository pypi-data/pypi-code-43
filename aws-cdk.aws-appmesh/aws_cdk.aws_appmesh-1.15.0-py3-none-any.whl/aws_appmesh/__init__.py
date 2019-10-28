import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.aws_ec2
import aws_cdk.aws_iam
import aws_cdk.aws_servicediscovery
import aws_cdk.core
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-appmesh", "1.15.0", __name__, "aws-appmesh@1.15.0.jsii.tgz")
class CfnMesh(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-appmesh.CfnMesh"):
    """A CloudFormation ``AWS::AppMesh::Mesh``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-mesh.html
    cloudformationResource:
    :cloudformationResource:: AWS::AppMesh::Mesh
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, mesh_name: str, spec: typing.Optional[typing.Union[typing.Optional["MeshSpecProperty"], typing.Optional[aws_cdk.core.IResolvable]]]=None, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None) -> None:
        """Create a new ``AWS::AppMesh::Mesh``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param mesh_name: ``AWS::AppMesh::Mesh.MeshName``.
        :param spec: ``AWS::AppMesh::Mesh.Spec``.
        :param tags: ``AWS::AppMesh::Mesh.Tags``.
        """
        props = CfnMeshProps(mesh_name=mesh_name, spec=spec, tags=tags)

        jsii.create(CfnMesh, self, [scope, id, props])

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
    @jsii.member(jsii_name="attrMeshName")
    def attr_mesh_name(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: MeshName
        """
        return jsii.get(self, "attrMeshName")

    @property
    @jsii.member(jsii_name="attrUid")
    def attr_uid(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: Uid
        """
        return jsii.get(self, "attrUid")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        """``AWS::AppMesh::Mesh.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-mesh.html#cfn-appmesh-mesh-tags
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="meshName")
    def mesh_name(self) -> str:
        """``AWS::AppMesh::Mesh.MeshName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-mesh.html#cfn-appmesh-mesh-meshname
        """
        return jsii.get(self, "meshName")

    @mesh_name.setter
    def mesh_name(self, value: str):
        return jsii.set(self, "meshName", value)

    @property
    @jsii.member(jsii_name="spec")
    def spec(self) -> typing.Optional[typing.Union[typing.Optional["MeshSpecProperty"], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::AppMesh::Mesh.Spec``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-mesh.html#cfn-appmesh-mesh-spec
        """
        return jsii.get(self, "spec")

    @spec.setter
    def spec(self, value: typing.Optional[typing.Union[typing.Optional["MeshSpecProperty"], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "spec", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-appmesh.CfnMesh.EgressFilterProperty", jsii_struct_bases=[], name_mapping={'type': 'type'})
    class EgressFilterProperty():
        def __init__(self, *, type: str):
            """
            :param type: ``CfnMesh.EgressFilterProperty.Type``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-mesh-egressfilter.html
            """
            self._values = {
                'type': type,
            }

        @property
        def type(self) -> str:
            """``CfnMesh.EgressFilterProperty.Type``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-mesh-egressfilter.html#cfn-appmesh-mesh-egressfilter-type
            """
            return self._values.get('type')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'EgressFilterProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-appmesh.CfnMesh.MeshSpecProperty", jsii_struct_bases=[], name_mapping={'egress_filter': 'egressFilter'})
    class MeshSpecProperty():
        def __init__(self, *, egress_filter: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnMesh.EgressFilterProperty"]]]=None):
            """
            :param egress_filter: ``CfnMesh.MeshSpecProperty.EgressFilter``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-mesh-meshspec.html
            """
            self._values = {
            }
            if egress_filter is not None: self._values["egress_filter"] = egress_filter

        @property
        def egress_filter(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnMesh.EgressFilterProperty"]]]:
            """``CfnMesh.MeshSpecProperty.EgressFilter``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-mesh-meshspec.html#cfn-appmesh-mesh-meshspec-egressfilter
            """
            return self._values.get('egress_filter')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'MeshSpecProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



@jsii.data_type(jsii_type="@aws-cdk/aws-appmesh.CfnMeshProps", jsii_struct_bases=[], name_mapping={'mesh_name': 'meshName', 'spec': 'spec', 'tags': 'tags'})
class CfnMeshProps():
    def __init__(self, *, mesh_name: str, spec: typing.Optional[typing.Union[typing.Optional["CfnMesh.MeshSpecProperty"], typing.Optional[aws_cdk.core.IResolvable]]]=None, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None):
        """Properties for defining a ``AWS::AppMesh::Mesh``.

        :param mesh_name: ``AWS::AppMesh::Mesh.MeshName``.
        :param spec: ``AWS::AppMesh::Mesh.Spec``.
        :param tags: ``AWS::AppMesh::Mesh.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-mesh.html
        """
        self._values = {
            'mesh_name': mesh_name,
        }
        if spec is not None: self._values["spec"] = spec
        if tags is not None: self._values["tags"] = tags

    @property
    def mesh_name(self) -> str:
        """``AWS::AppMesh::Mesh.MeshName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-mesh.html#cfn-appmesh-mesh-meshname
        """
        return self._values.get('mesh_name')

    @property
    def spec(self) -> typing.Optional[typing.Union[typing.Optional["CfnMesh.MeshSpecProperty"], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::AppMesh::Mesh.Spec``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-mesh.html#cfn-appmesh-mesh-spec
        """
        return self._values.get('spec')

    @property
    def tags(self) -> typing.Optional[typing.List[aws_cdk.core.CfnTag]]:
        """``AWS::AppMesh::Mesh.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-mesh.html#cfn-appmesh-mesh-tags
        """
        return self._values.get('tags')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnMeshProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnRoute(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-appmesh.CfnRoute"):
    """A CloudFormation ``AWS::AppMesh::Route``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-route.html
    cloudformationResource:
    :cloudformationResource:: AWS::AppMesh::Route
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, mesh_name: str, route_name: str, spec: typing.Union[aws_cdk.core.IResolvable, "RouteSpecProperty"], virtual_router_name: str, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None) -> None:
        """Create a new ``AWS::AppMesh::Route``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param mesh_name: ``AWS::AppMesh::Route.MeshName``.
        :param route_name: ``AWS::AppMesh::Route.RouteName``.
        :param spec: ``AWS::AppMesh::Route.Spec``.
        :param virtual_router_name: ``AWS::AppMesh::Route.VirtualRouterName``.
        :param tags: ``AWS::AppMesh::Route.Tags``.
        """
        props = CfnRouteProps(mesh_name=mesh_name, route_name=route_name, spec=spec, virtual_router_name=virtual_router_name, tags=tags)

        jsii.create(CfnRoute, self, [scope, id, props])

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
    @jsii.member(jsii_name="attrMeshName")
    def attr_mesh_name(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: MeshName
        """
        return jsii.get(self, "attrMeshName")

    @property
    @jsii.member(jsii_name="attrRouteName")
    def attr_route_name(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: RouteName
        """
        return jsii.get(self, "attrRouteName")

    @property
    @jsii.member(jsii_name="attrUid")
    def attr_uid(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: Uid
        """
        return jsii.get(self, "attrUid")

    @property
    @jsii.member(jsii_name="attrVirtualRouterName")
    def attr_virtual_router_name(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: VirtualRouterName
        """
        return jsii.get(self, "attrVirtualRouterName")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        """``AWS::AppMesh::Route.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-route.html#cfn-appmesh-route-tags
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="meshName")
    def mesh_name(self) -> str:
        """``AWS::AppMesh::Route.MeshName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-route.html#cfn-appmesh-route-meshname
        """
        return jsii.get(self, "meshName")

    @mesh_name.setter
    def mesh_name(self, value: str):
        return jsii.set(self, "meshName", value)

    @property
    @jsii.member(jsii_name="routeName")
    def route_name(self) -> str:
        """``AWS::AppMesh::Route.RouteName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-route.html#cfn-appmesh-route-routename
        """
        return jsii.get(self, "routeName")

    @route_name.setter
    def route_name(self, value: str):
        return jsii.set(self, "routeName", value)

    @property
    @jsii.member(jsii_name="spec")
    def spec(self) -> typing.Union[aws_cdk.core.IResolvable, "RouteSpecProperty"]:
        """``AWS::AppMesh::Route.Spec``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-route.html#cfn-appmesh-route-spec
        """
        return jsii.get(self, "spec")

    @spec.setter
    def spec(self, value: typing.Union[aws_cdk.core.IResolvable, "RouteSpecProperty"]):
        return jsii.set(self, "spec", value)

    @property
    @jsii.member(jsii_name="virtualRouterName")
    def virtual_router_name(self) -> str:
        """``AWS::AppMesh::Route.VirtualRouterName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-route.html#cfn-appmesh-route-virtualroutername
        """
        return jsii.get(self, "virtualRouterName")

    @virtual_router_name.setter
    def virtual_router_name(self, value: str):
        return jsii.set(self, "virtualRouterName", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-appmesh.CfnRoute.DurationProperty", jsii_struct_bases=[], name_mapping={'unit': 'unit', 'value': 'value'})
    class DurationProperty():
        def __init__(self, *, unit: str, value: jsii.Number):
            """
            :param unit: ``CfnRoute.DurationProperty.Unit``.
            :param value: ``CfnRoute.DurationProperty.Value``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-route-duration.html
            """
            self._values = {
                'unit': unit,
                'value': value,
            }

        @property
        def unit(self) -> str:
            """``CfnRoute.DurationProperty.Unit``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-route-duration.html#cfn-appmesh-route-duration-unit
            """
            return self._values.get('unit')

        @property
        def value(self) -> jsii.Number:
            """``CfnRoute.DurationProperty.Value``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-route-duration.html#cfn-appmesh-route-duration-value
            """
            return self._values.get('value')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'DurationProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-appmesh.CfnRoute.HeaderMatchMethodProperty", jsii_struct_bases=[], name_mapping={'exact': 'exact', 'prefix': 'prefix', 'range': 'range', 'regex': 'regex', 'suffix': 'suffix'})
    class HeaderMatchMethodProperty():
        def __init__(self, *, exact: typing.Optional[str]=None, prefix: typing.Optional[str]=None, range: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnRoute.MatchRangeProperty"]]]=None, regex: typing.Optional[str]=None, suffix: typing.Optional[str]=None):
            """
            :param exact: ``CfnRoute.HeaderMatchMethodProperty.Exact``.
            :param prefix: ``CfnRoute.HeaderMatchMethodProperty.Prefix``.
            :param range: ``CfnRoute.HeaderMatchMethodProperty.Range``.
            :param regex: ``CfnRoute.HeaderMatchMethodProperty.Regex``.
            :param suffix: ``CfnRoute.HeaderMatchMethodProperty.Suffix``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-route-headermatchmethod.html
            """
            self._values = {
            }
            if exact is not None: self._values["exact"] = exact
            if prefix is not None: self._values["prefix"] = prefix
            if range is not None: self._values["range"] = range
            if regex is not None: self._values["regex"] = regex
            if suffix is not None: self._values["suffix"] = suffix

        @property
        def exact(self) -> typing.Optional[str]:
            """``CfnRoute.HeaderMatchMethodProperty.Exact``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-route-headermatchmethod.html#cfn-appmesh-route-headermatchmethod-exact
            """
            return self._values.get('exact')

        @property
        def prefix(self) -> typing.Optional[str]:
            """``CfnRoute.HeaderMatchMethodProperty.Prefix``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-route-headermatchmethod.html#cfn-appmesh-route-headermatchmethod-prefix
            """
            return self._values.get('prefix')

        @property
        def range(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnRoute.MatchRangeProperty"]]]:
            """``CfnRoute.HeaderMatchMethodProperty.Range``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-route-headermatchmethod.html#cfn-appmesh-route-headermatchmethod-range
            """
            return self._values.get('range')

        @property
        def regex(self) -> typing.Optional[str]:
            """``CfnRoute.HeaderMatchMethodProperty.Regex``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-route-headermatchmethod.html#cfn-appmesh-route-headermatchmethod-regex
            """
            return self._values.get('regex')

        @property
        def suffix(self) -> typing.Optional[str]:
            """``CfnRoute.HeaderMatchMethodProperty.Suffix``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-route-headermatchmethod.html#cfn-appmesh-route-headermatchmethod-suffix
            """
            return self._values.get('suffix')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'HeaderMatchMethodProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-appmesh.CfnRoute.HttpRetryPolicyProperty", jsii_struct_bases=[], name_mapping={'max_retries': 'maxRetries', 'per_retry_timeout': 'perRetryTimeout', 'http_retry_events': 'httpRetryEvents', 'tcp_retry_events': 'tcpRetryEvents'})
    class HttpRetryPolicyProperty():
        def __init__(self, *, max_retries: jsii.Number, per_retry_timeout: typing.Union[aws_cdk.core.IResolvable, "CfnRoute.DurationProperty"], http_retry_events: typing.Optional[typing.List[str]]=None, tcp_retry_events: typing.Optional[typing.List[str]]=None):
            """
            :param max_retries: ``CfnRoute.HttpRetryPolicyProperty.MaxRetries``.
            :param per_retry_timeout: ``CfnRoute.HttpRetryPolicyProperty.PerRetryTimeout``.
            :param http_retry_events: ``CfnRoute.HttpRetryPolicyProperty.HttpRetryEvents``.
            :param tcp_retry_events: ``CfnRoute.HttpRetryPolicyProperty.TcpRetryEvents``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-route-httpretrypolicy.html
            """
            self._values = {
                'max_retries': max_retries,
                'per_retry_timeout': per_retry_timeout,
            }
            if http_retry_events is not None: self._values["http_retry_events"] = http_retry_events
            if tcp_retry_events is not None: self._values["tcp_retry_events"] = tcp_retry_events

        @property
        def max_retries(self) -> jsii.Number:
            """``CfnRoute.HttpRetryPolicyProperty.MaxRetries``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-route-httpretrypolicy.html#cfn-appmesh-route-httpretrypolicy-maxretries
            """
            return self._values.get('max_retries')

        @property
        def per_retry_timeout(self) -> typing.Union[aws_cdk.core.IResolvable, "CfnRoute.DurationProperty"]:
            """``CfnRoute.HttpRetryPolicyProperty.PerRetryTimeout``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-route-httpretrypolicy.html#cfn-appmesh-route-httpretrypolicy-perretrytimeout
            """
            return self._values.get('per_retry_timeout')

        @property
        def http_retry_events(self) -> typing.Optional[typing.List[str]]:
            """``CfnRoute.HttpRetryPolicyProperty.HttpRetryEvents``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-route-httpretrypolicy.html#cfn-appmesh-route-httpretrypolicy-httpretryevents
            """
            return self._values.get('http_retry_events')

        @property
        def tcp_retry_events(self) -> typing.Optional[typing.List[str]]:
            """``CfnRoute.HttpRetryPolicyProperty.TcpRetryEvents``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-route-httpretrypolicy.html#cfn-appmesh-route-httpretrypolicy-tcpretryevents
            """
            return self._values.get('tcp_retry_events')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'HttpRetryPolicyProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-appmesh.CfnRoute.HttpRouteActionProperty", jsii_struct_bases=[], name_mapping={'weighted_targets': 'weightedTargets'})
    class HttpRouteActionProperty():
        def __init__(self, *, weighted_targets: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnRoute.WeightedTargetProperty"]]]):
            """
            :param weighted_targets: ``CfnRoute.HttpRouteActionProperty.WeightedTargets``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-route-httprouteaction.html
            """
            self._values = {
                'weighted_targets': weighted_targets,
            }

        @property
        def weighted_targets(self) -> typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnRoute.WeightedTargetProperty"]]]:
            """``CfnRoute.HttpRouteActionProperty.WeightedTargets``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-route-httprouteaction.html#cfn-appmesh-route-httprouteaction-weightedtargets
            """
            return self._values.get('weighted_targets')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'HttpRouteActionProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-appmesh.CfnRoute.HttpRouteHeaderProperty", jsii_struct_bases=[], name_mapping={'name': 'name', 'invert': 'invert', 'match': 'match'})
    class HttpRouteHeaderProperty():
        def __init__(self, *, name: str, invert: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, match: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnRoute.HeaderMatchMethodProperty"]]]=None):
            """
            :param name: ``CfnRoute.HttpRouteHeaderProperty.Name``.
            :param invert: ``CfnRoute.HttpRouteHeaderProperty.Invert``.
            :param match: ``CfnRoute.HttpRouteHeaderProperty.Match``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-route-httprouteheader.html
            """
            self._values = {
                'name': name,
            }
            if invert is not None: self._values["invert"] = invert
            if match is not None: self._values["match"] = match

        @property
        def name(self) -> str:
            """``CfnRoute.HttpRouteHeaderProperty.Name``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-route-httprouteheader.html#cfn-appmesh-route-httprouteheader-name
            """
            return self._values.get('name')

        @property
        def invert(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
            """``CfnRoute.HttpRouteHeaderProperty.Invert``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-route-httprouteheader.html#cfn-appmesh-route-httprouteheader-invert
            """
            return self._values.get('invert')

        @property
        def match(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnRoute.HeaderMatchMethodProperty"]]]:
            """``CfnRoute.HttpRouteHeaderProperty.Match``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-route-httprouteheader.html#cfn-appmesh-route-httprouteheader-match
            """
            return self._values.get('match')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'HttpRouteHeaderProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-appmesh.CfnRoute.HttpRouteMatchProperty", jsii_struct_bases=[], name_mapping={'prefix': 'prefix', 'headers': 'headers', 'method': 'method', 'scheme': 'scheme'})
    class HttpRouteMatchProperty():
        def __init__(self, *, prefix: str, headers: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnRoute.HttpRouteHeaderProperty"]]]]]=None, method: typing.Optional[str]=None, scheme: typing.Optional[str]=None):
            """
            :param prefix: ``CfnRoute.HttpRouteMatchProperty.Prefix``.
            :param headers: ``CfnRoute.HttpRouteMatchProperty.Headers``.
            :param method: ``CfnRoute.HttpRouteMatchProperty.Method``.
            :param scheme: ``CfnRoute.HttpRouteMatchProperty.Scheme``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-route-httproutematch.html
            """
            self._values = {
                'prefix': prefix,
            }
            if headers is not None: self._values["headers"] = headers
            if method is not None: self._values["method"] = method
            if scheme is not None: self._values["scheme"] = scheme

        @property
        def prefix(self) -> str:
            """``CfnRoute.HttpRouteMatchProperty.Prefix``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-route-httproutematch.html#cfn-appmesh-route-httproutematch-prefix
            """
            return self._values.get('prefix')

        @property
        def headers(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnRoute.HttpRouteHeaderProperty"]]]]]:
            """``CfnRoute.HttpRouteMatchProperty.Headers``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-route-httproutematch.html#cfn-appmesh-route-httproutematch-headers
            """
            return self._values.get('headers')

        @property
        def method(self) -> typing.Optional[str]:
            """``CfnRoute.HttpRouteMatchProperty.Method``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-route-httproutematch.html#cfn-appmesh-route-httproutematch-method
            """
            return self._values.get('method')

        @property
        def scheme(self) -> typing.Optional[str]:
            """``CfnRoute.HttpRouteMatchProperty.Scheme``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-route-httproutematch.html#cfn-appmesh-route-httproutematch-scheme
            """
            return self._values.get('scheme')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'HttpRouteMatchProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-appmesh.CfnRoute.HttpRouteProperty", jsii_struct_bases=[], name_mapping={'action': 'action', 'match': 'match', 'retry_policy': 'retryPolicy'})
    class HttpRouteProperty():
        def __init__(self, *, action: typing.Union[aws_cdk.core.IResolvable, "CfnRoute.HttpRouteActionProperty"], match: typing.Union[aws_cdk.core.IResolvable, "CfnRoute.HttpRouteMatchProperty"], retry_policy: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnRoute.HttpRetryPolicyProperty"]]]=None):
            """
            :param action: ``CfnRoute.HttpRouteProperty.Action``.
            :param match: ``CfnRoute.HttpRouteProperty.Match``.
            :param retry_policy: ``CfnRoute.HttpRouteProperty.RetryPolicy``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-route-httproute.html
            """
            self._values = {
                'action': action,
                'match': match,
            }
            if retry_policy is not None: self._values["retry_policy"] = retry_policy

        @property
        def action(self) -> typing.Union[aws_cdk.core.IResolvable, "CfnRoute.HttpRouteActionProperty"]:
            """``CfnRoute.HttpRouteProperty.Action``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-route-httproute.html#cfn-appmesh-route-httproute-action
            """
            return self._values.get('action')

        @property
        def match(self) -> typing.Union[aws_cdk.core.IResolvable, "CfnRoute.HttpRouteMatchProperty"]:
            """``CfnRoute.HttpRouteProperty.Match``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-route-httproute.html#cfn-appmesh-route-httproute-match
            """
            return self._values.get('match')

        @property
        def retry_policy(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnRoute.HttpRetryPolicyProperty"]]]:
            """``CfnRoute.HttpRouteProperty.RetryPolicy``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-route-httproute.html#cfn-appmesh-route-httproute-retrypolicy
            """
            return self._values.get('retry_policy')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'HttpRouteProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-appmesh.CfnRoute.MatchRangeProperty", jsii_struct_bases=[], name_mapping={'end': 'end', 'start': 'start'})
    class MatchRangeProperty():
        def __init__(self, *, end: jsii.Number, start: jsii.Number):
            """
            :param end: ``CfnRoute.MatchRangeProperty.End``.
            :param start: ``CfnRoute.MatchRangeProperty.Start``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-route-matchrange.html
            """
            self._values = {
                'end': end,
                'start': start,
            }

        @property
        def end(self) -> jsii.Number:
            """``CfnRoute.MatchRangeProperty.End``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-route-matchrange.html#cfn-appmesh-route-matchrange-end
            """
            return self._values.get('end')

        @property
        def start(self) -> jsii.Number:
            """``CfnRoute.MatchRangeProperty.Start``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-route-matchrange.html#cfn-appmesh-route-matchrange-start
            """
            return self._values.get('start')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'MatchRangeProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-appmesh.CfnRoute.RouteSpecProperty", jsii_struct_bases=[], name_mapping={'http_route': 'httpRoute', 'priority': 'priority', 'tcp_route': 'tcpRoute'})
    class RouteSpecProperty():
        def __init__(self, *, http_route: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnRoute.HttpRouteProperty"]]]=None, priority: typing.Optional[jsii.Number]=None, tcp_route: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnRoute.TcpRouteProperty"]]]=None):
            """
            :param http_route: ``CfnRoute.RouteSpecProperty.HttpRoute``.
            :param priority: ``CfnRoute.RouteSpecProperty.Priority``.
            :param tcp_route: ``CfnRoute.RouteSpecProperty.TcpRoute``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-route-routespec.html
            """
            self._values = {
            }
            if http_route is not None: self._values["http_route"] = http_route
            if priority is not None: self._values["priority"] = priority
            if tcp_route is not None: self._values["tcp_route"] = tcp_route

        @property
        def http_route(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnRoute.HttpRouteProperty"]]]:
            """``CfnRoute.RouteSpecProperty.HttpRoute``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-route-routespec.html#cfn-appmesh-route-routespec-httproute
            """
            return self._values.get('http_route')

        @property
        def priority(self) -> typing.Optional[jsii.Number]:
            """``CfnRoute.RouteSpecProperty.Priority``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-route-routespec.html#cfn-appmesh-route-routespec-priority
            """
            return self._values.get('priority')

        @property
        def tcp_route(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnRoute.TcpRouteProperty"]]]:
            """``CfnRoute.RouteSpecProperty.TcpRoute``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-route-routespec.html#cfn-appmesh-route-routespec-tcproute
            """
            return self._values.get('tcp_route')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'RouteSpecProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-appmesh.CfnRoute.TcpRouteActionProperty", jsii_struct_bases=[], name_mapping={'weighted_targets': 'weightedTargets'})
    class TcpRouteActionProperty():
        def __init__(self, *, weighted_targets: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnRoute.WeightedTargetProperty"]]]):
            """
            :param weighted_targets: ``CfnRoute.TcpRouteActionProperty.WeightedTargets``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-route-tcprouteaction.html
            """
            self._values = {
                'weighted_targets': weighted_targets,
            }

        @property
        def weighted_targets(self) -> typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnRoute.WeightedTargetProperty"]]]:
            """``CfnRoute.TcpRouteActionProperty.WeightedTargets``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-route-tcprouteaction.html#cfn-appmesh-route-tcprouteaction-weightedtargets
            """
            return self._values.get('weighted_targets')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'TcpRouteActionProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-appmesh.CfnRoute.TcpRouteProperty", jsii_struct_bases=[], name_mapping={'action': 'action'})
    class TcpRouteProperty():
        def __init__(self, *, action: typing.Union[aws_cdk.core.IResolvable, "CfnRoute.TcpRouteActionProperty"]):
            """
            :param action: ``CfnRoute.TcpRouteProperty.Action``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-route-tcproute.html
            """
            self._values = {
                'action': action,
            }

        @property
        def action(self) -> typing.Union[aws_cdk.core.IResolvable, "CfnRoute.TcpRouteActionProperty"]:
            """``CfnRoute.TcpRouteProperty.Action``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-route-tcproute.html#cfn-appmesh-route-tcproute-action
            """
            return self._values.get('action')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'TcpRouteProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-appmesh.CfnRoute.WeightedTargetProperty", jsii_struct_bases=[], name_mapping={'virtual_node': 'virtualNode', 'weight': 'weight'})
    class WeightedTargetProperty():
        def __init__(self, *, virtual_node: str, weight: jsii.Number):
            """
            :param virtual_node: ``CfnRoute.WeightedTargetProperty.VirtualNode``.
            :param weight: ``CfnRoute.WeightedTargetProperty.Weight``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-route-weightedtarget.html
            """
            self._values = {
                'virtual_node': virtual_node,
                'weight': weight,
            }

        @property
        def virtual_node(self) -> str:
            """``CfnRoute.WeightedTargetProperty.VirtualNode``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-route-weightedtarget.html#cfn-appmesh-route-weightedtarget-virtualnode
            """
            return self._values.get('virtual_node')

        @property
        def weight(self) -> jsii.Number:
            """``CfnRoute.WeightedTargetProperty.Weight``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-route-weightedtarget.html#cfn-appmesh-route-weightedtarget-weight
            """
            return self._values.get('weight')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'WeightedTargetProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



@jsii.data_type(jsii_type="@aws-cdk/aws-appmesh.CfnRouteProps", jsii_struct_bases=[], name_mapping={'mesh_name': 'meshName', 'route_name': 'routeName', 'spec': 'spec', 'virtual_router_name': 'virtualRouterName', 'tags': 'tags'})
class CfnRouteProps():
    def __init__(self, *, mesh_name: str, route_name: str, spec: typing.Union[aws_cdk.core.IResolvable, "CfnRoute.RouteSpecProperty"], virtual_router_name: str, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None):
        """Properties for defining a ``AWS::AppMesh::Route``.

        :param mesh_name: ``AWS::AppMesh::Route.MeshName``.
        :param route_name: ``AWS::AppMesh::Route.RouteName``.
        :param spec: ``AWS::AppMesh::Route.Spec``.
        :param virtual_router_name: ``AWS::AppMesh::Route.VirtualRouterName``.
        :param tags: ``AWS::AppMesh::Route.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-route.html
        """
        self._values = {
            'mesh_name': mesh_name,
            'route_name': route_name,
            'spec': spec,
            'virtual_router_name': virtual_router_name,
        }
        if tags is not None: self._values["tags"] = tags

    @property
    def mesh_name(self) -> str:
        """``AWS::AppMesh::Route.MeshName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-route.html#cfn-appmesh-route-meshname
        """
        return self._values.get('mesh_name')

    @property
    def route_name(self) -> str:
        """``AWS::AppMesh::Route.RouteName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-route.html#cfn-appmesh-route-routename
        """
        return self._values.get('route_name')

    @property
    def spec(self) -> typing.Union[aws_cdk.core.IResolvable, "CfnRoute.RouteSpecProperty"]:
        """``AWS::AppMesh::Route.Spec``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-route.html#cfn-appmesh-route-spec
        """
        return self._values.get('spec')

    @property
    def virtual_router_name(self) -> str:
        """``AWS::AppMesh::Route.VirtualRouterName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-route.html#cfn-appmesh-route-virtualroutername
        """
        return self._values.get('virtual_router_name')

    @property
    def tags(self) -> typing.Optional[typing.List[aws_cdk.core.CfnTag]]:
        """``AWS::AppMesh::Route.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-route.html#cfn-appmesh-route-tags
        """
        return self._values.get('tags')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnRouteProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnVirtualNode(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-appmesh.CfnVirtualNode"):
    """A CloudFormation ``AWS::AppMesh::VirtualNode``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-virtualnode.html
    cloudformationResource:
    :cloudformationResource:: AWS::AppMesh::VirtualNode
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, mesh_name: str, spec: typing.Union[aws_cdk.core.IResolvable, "VirtualNodeSpecProperty"], virtual_node_name: str, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None) -> None:
        """Create a new ``AWS::AppMesh::VirtualNode``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param mesh_name: ``AWS::AppMesh::VirtualNode.MeshName``.
        :param spec: ``AWS::AppMesh::VirtualNode.Spec``.
        :param virtual_node_name: ``AWS::AppMesh::VirtualNode.VirtualNodeName``.
        :param tags: ``AWS::AppMesh::VirtualNode.Tags``.
        """
        props = CfnVirtualNodeProps(mesh_name=mesh_name, spec=spec, virtual_node_name=virtual_node_name, tags=tags)

        jsii.create(CfnVirtualNode, self, [scope, id, props])

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
    @jsii.member(jsii_name="attrMeshName")
    def attr_mesh_name(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: MeshName
        """
        return jsii.get(self, "attrMeshName")

    @property
    @jsii.member(jsii_name="attrUid")
    def attr_uid(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: Uid
        """
        return jsii.get(self, "attrUid")

    @property
    @jsii.member(jsii_name="attrVirtualNodeName")
    def attr_virtual_node_name(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: VirtualNodeName
        """
        return jsii.get(self, "attrVirtualNodeName")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        """``AWS::AppMesh::VirtualNode.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-virtualnode.html#cfn-appmesh-virtualnode-tags
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="meshName")
    def mesh_name(self) -> str:
        """``AWS::AppMesh::VirtualNode.MeshName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-virtualnode.html#cfn-appmesh-virtualnode-meshname
        """
        return jsii.get(self, "meshName")

    @mesh_name.setter
    def mesh_name(self, value: str):
        return jsii.set(self, "meshName", value)

    @property
    @jsii.member(jsii_name="spec")
    def spec(self) -> typing.Union[aws_cdk.core.IResolvable, "VirtualNodeSpecProperty"]:
        """``AWS::AppMesh::VirtualNode.Spec``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-virtualnode.html#cfn-appmesh-virtualnode-spec
        """
        return jsii.get(self, "spec")

    @spec.setter
    def spec(self, value: typing.Union[aws_cdk.core.IResolvable, "VirtualNodeSpecProperty"]):
        return jsii.set(self, "spec", value)

    @property
    @jsii.member(jsii_name="virtualNodeName")
    def virtual_node_name(self) -> str:
        """``AWS::AppMesh::VirtualNode.VirtualNodeName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-virtualnode.html#cfn-appmesh-virtualnode-virtualnodename
        """
        return jsii.get(self, "virtualNodeName")

    @virtual_node_name.setter
    def virtual_node_name(self, value: str):
        return jsii.set(self, "virtualNodeName", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-appmesh.CfnVirtualNode.AccessLogProperty", jsii_struct_bases=[], name_mapping={'file': 'file'})
    class AccessLogProperty():
        def __init__(self, *, file: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnVirtualNode.FileAccessLogProperty"]]]=None):
            """
            :param file: ``CfnVirtualNode.AccessLogProperty.File``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualnode-accesslog.html
            """
            self._values = {
            }
            if file is not None: self._values["file"] = file

        @property
        def file(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnVirtualNode.FileAccessLogProperty"]]]:
            """``CfnVirtualNode.AccessLogProperty.File``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualnode-accesslog.html#cfn-appmesh-virtualnode-accesslog-file
            """
            return self._values.get('file')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'AccessLogProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-appmesh.CfnVirtualNode.AwsCloudMapInstanceAttributeProperty", jsii_struct_bases=[], name_mapping={'key': 'key', 'value': 'value'})
    class AwsCloudMapInstanceAttributeProperty():
        def __init__(self, *, key: str, value: str):
            """
            :param key: ``CfnVirtualNode.AwsCloudMapInstanceAttributeProperty.Key``.
            :param value: ``CfnVirtualNode.AwsCloudMapInstanceAttributeProperty.Value``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualnode-awscloudmapinstanceattribute.html
            """
            self._values = {
                'key': key,
                'value': value,
            }

        @property
        def key(self) -> str:
            """``CfnVirtualNode.AwsCloudMapInstanceAttributeProperty.Key``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualnode-awscloudmapinstanceattribute.html#cfn-appmesh-virtualnode-awscloudmapinstanceattribute-key
            """
            return self._values.get('key')

        @property
        def value(self) -> str:
            """``CfnVirtualNode.AwsCloudMapInstanceAttributeProperty.Value``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualnode-awscloudmapinstanceattribute.html#cfn-appmesh-virtualnode-awscloudmapinstanceattribute-value
            """
            return self._values.get('value')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'AwsCloudMapInstanceAttributeProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-appmesh.CfnVirtualNode.AwsCloudMapServiceDiscoveryProperty", jsii_struct_bases=[], name_mapping={'namespace_name': 'namespaceName', 'service_name': 'serviceName', 'attributes': 'attributes'})
    class AwsCloudMapServiceDiscoveryProperty():
        def __init__(self, *, namespace_name: str, service_name: str, attributes: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnVirtualNode.AwsCloudMapInstanceAttributeProperty"]]]]]=None):
            """
            :param namespace_name: ``CfnVirtualNode.AwsCloudMapServiceDiscoveryProperty.NamespaceName``.
            :param service_name: ``CfnVirtualNode.AwsCloudMapServiceDiscoveryProperty.ServiceName``.
            :param attributes: ``CfnVirtualNode.AwsCloudMapServiceDiscoveryProperty.Attributes``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualnode-awscloudmapservicediscovery.html
            """
            self._values = {
                'namespace_name': namespace_name,
                'service_name': service_name,
            }
            if attributes is not None: self._values["attributes"] = attributes

        @property
        def namespace_name(self) -> str:
            """``CfnVirtualNode.AwsCloudMapServiceDiscoveryProperty.NamespaceName``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualnode-awscloudmapservicediscovery.html#cfn-appmesh-virtualnode-awscloudmapservicediscovery-namespacename
            """
            return self._values.get('namespace_name')

        @property
        def service_name(self) -> str:
            """``CfnVirtualNode.AwsCloudMapServiceDiscoveryProperty.ServiceName``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualnode-awscloudmapservicediscovery.html#cfn-appmesh-virtualnode-awscloudmapservicediscovery-servicename
            """
            return self._values.get('service_name')

        @property
        def attributes(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnVirtualNode.AwsCloudMapInstanceAttributeProperty"]]]]]:
            """``CfnVirtualNode.AwsCloudMapServiceDiscoveryProperty.Attributes``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualnode-awscloudmapservicediscovery.html#cfn-appmesh-virtualnode-awscloudmapservicediscovery-attributes
            """
            return self._values.get('attributes')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'AwsCloudMapServiceDiscoveryProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-appmesh.CfnVirtualNode.BackendProperty", jsii_struct_bases=[], name_mapping={'virtual_service': 'virtualService'})
    class BackendProperty():
        def __init__(self, *, virtual_service: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnVirtualNode.VirtualServiceBackendProperty"]]]=None):
            """
            :param virtual_service: ``CfnVirtualNode.BackendProperty.VirtualService``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualnode-backend.html
            """
            self._values = {
            }
            if virtual_service is not None: self._values["virtual_service"] = virtual_service

        @property
        def virtual_service(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnVirtualNode.VirtualServiceBackendProperty"]]]:
            """``CfnVirtualNode.BackendProperty.VirtualService``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualnode-backend.html#cfn-appmesh-virtualnode-backend-virtualservice
            """
            return self._values.get('virtual_service')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'BackendProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-appmesh.CfnVirtualNode.DnsServiceDiscoveryProperty", jsii_struct_bases=[], name_mapping={'hostname': 'hostname'})
    class DnsServiceDiscoveryProperty():
        def __init__(self, *, hostname: str):
            """
            :param hostname: ``CfnVirtualNode.DnsServiceDiscoveryProperty.Hostname``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualnode-dnsservicediscovery.html
            """
            self._values = {
                'hostname': hostname,
            }

        @property
        def hostname(self) -> str:
            """``CfnVirtualNode.DnsServiceDiscoveryProperty.Hostname``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualnode-dnsservicediscovery.html#cfn-appmesh-virtualnode-dnsservicediscovery-hostname
            """
            return self._values.get('hostname')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'DnsServiceDiscoveryProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-appmesh.CfnVirtualNode.FileAccessLogProperty", jsii_struct_bases=[], name_mapping={'path': 'path'})
    class FileAccessLogProperty():
        def __init__(self, *, path: str):
            """
            :param path: ``CfnVirtualNode.FileAccessLogProperty.Path``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualnode-fileaccesslog.html
            """
            self._values = {
                'path': path,
            }

        @property
        def path(self) -> str:
            """``CfnVirtualNode.FileAccessLogProperty.Path``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualnode-fileaccesslog.html#cfn-appmesh-virtualnode-fileaccesslog-path
            """
            return self._values.get('path')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'FileAccessLogProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-appmesh.CfnVirtualNode.HealthCheckProperty", jsii_struct_bases=[], name_mapping={'healthy_threshold': 'healthyThreshold', 'interval_millis': 'intervalMillis', 'protocol': 'protocol', 'timeout_millis': 'timeoutMillis', 'unhealthy_threshold': 'unhealthyThreshold', 'path': 'path', 'port': 'port'})
    class HealthCheckProperty():
        def __init__(self, *, healthy_threshold: jsii.Number, interval_millis: jsii.Number, protocol: str, timeout_millis: jsii.Number, unhealthy_threshold: jsii.Number, path: typing.Optional[str]=None, port: typing.Optional[jsii.Number]=None):
            """
            :param healthy_threshold: ``CfnVirtualNode.HealthCheckProperty.HealthyThreshold``.
            :param interval_millis: ``CfnVirtualNode.HealthCheckProperty.IntervalMillis``.
            :param protocol: ``CfnVirtualNode.HealthCheckProperty.Protocol``.
            :param timeout_millis: ``CfnVirtualNode.HealthCheckProperty.TimeoutMillis``.
            :param unhealthy_threshold: ``CfnVirtualNode.HealthCheckProperty.UnhealthyThreshold``.
            :param path: ``CfnVirtualNode.HealthCheckProperty.Path``.
            :param port: ``CfnVirtualNode.HealthCheckProperty.Port``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualnode-healthcheck.html
            """
            self._values = {
                'healthy_threshold': healthy_threshold,
                'interval_millis': interval_millis,
                'protocol': protocol,
                'timeout_millis': timeout_millis,
                'unhealthy_threshold': unhealthy_threshold,
            }
            if path is not None: self._values["path"] = path
            if port is not None: self._values["port"] = port

        @property
        def healthy_threshold(self) -> jsii.Number:
            """``CfnVirtualNode.HealthCheckProperty.HealthyThreshold``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualnode-healthcheck.html#cfn-appmesh-virtualnode-healthcheck-healthythreshold
            """
            return self._values.get('healthy_threshold')

        @property
        def interval_millis(self) -> jsii.Number:
            """``CfnVirtualNode.HealthCheckProperty.IntervalMillis``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualnode-healthcheck.html#cfn-appmesh-virtualnode-healthcheck-intervalmillis
            """
            return self._values.get('interval_millis')

        @property
        def protocol(self) -> str:
            """``CfnVirtualNode.HealthCheckProperty.Protocol``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualnode-healthcheck.html#cfn-appmesh-virtualnode-healthcheck-protocol
            """
            return self._values.get('protocol')

        @property
        def timeout_millis(self) -> jsii.Number:
            """``CfnVirtualNode.HealthCheckProperty.TimeoutMillis``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualnode-healthcheck.html#cfn-appmesh-virtualnode-healthcheck-timeoutmillis
            """
            return self._values.get('timeout_millis')

        @property
        def unhealthy_threshold(self) -> jsii.Number:
            """``CfnVirtualNode.HealthCheckProperty.UnhealthyThreshold``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualnode-healthcheck.html#cfn-appmesh-virtualnode-healthcheck-unhealthythreshold
            """
            return self._values.get('unhealthy_threshold')

        @property
        def path(self) -> typing.Optional[str]:
            """``CfnVirtualNode.HealthCheckProperty.Path``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualnode-healthcheck.html#cfn-appmesh-virtualnode-healthcheck-path
            """
            return self._values.get('path')

        @property
        def port(self) -> typing.Optional[jsii.Number]:
            """``CfnVirtualNode.HealthCheckProperty.Port``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualnode-healthcheck.html#cfn-appmesh-virtualnode-healthcheck-port
            """
            return self._values.get('port')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'HealthCheckProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-appmesh.CfnVirtualNode.ListenerProperty", jsii_struct_bases=[], name_mapping={'port_mapping': 'portMapping', 'health_check': 'healthCheck'})
    class ListenerProperty():
        def __init__(self, *, port_mapping: typing.Union[aws_cdk.core.IResolvable, "CfnVirtualNode.PortMappingProperty"], health_check: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnVirtualNode.HealthCheckProperty"]]]=None):
            """
            :param port_mapping: ``CfnVirtualNode.ListenerProperty.PortMapping``.
            :param health_check: ``CfnVirtualNode.ListenerProperty.HealthCheck``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualnode-listener.html
            """
            self._values = {
                'port_mapping': port_mapping,
            }
            if health_check is not None: self._values["health_check"] = health_check

        @property
        def port_mapping(self) -> typing.Union[aws_cdk.core.IResolvable, "CfnVirtualNode.PortMappingProperty"]:
            """``CfnVirtualNode.ListenerProperty.PortMapping``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualnode-listener.html#cfn-appmesh-virtualnode-listener-portmapping
            """
            return self._values.get('port_mapping')

        @property
        def health_check(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnVirtualNode.HealthCheckProperty"]]]:
            """``CfnVirtualNode.ListenerProperty.HealthCheck``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualnode-listener.html#cfn-appmesh-virtualnode-listener-healthcheck
            """
            return self._values.get('health_check')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'ListenerProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-appmesh.CfnVirtualNode.LoggingProperty", jsii_struct_bases=[], name_mapping={'access_log': 'accessLog'})
    class LoggingProperty():
        def __init__(self, *, access_log: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnVirtualNode.AccessLogProperty"]]]=None):
            """
            :param access_log: ``CfnVirtualNode.LoggingProperty.AccessLog``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualnode-logging.html
            """
            self._values = {
            }
            if access_log is not None: self._values["access_log"] = access_log

        @property
        def access_log(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnVirtualNode.AccessLogProperty"]]]:
            """``CfnVirtualNode.LoggingProperty.AccessLog``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualnode-logging.html#cfn-appmesh-virtualnode-logging-accesslog
            """
            return self._values.get('access_log')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'LoggingProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-appmesh.CfnVirtualNode.PortMappingProperty", jsii_struct_bases=[], name_mapping={'port': 'port', 'protocol': 'protocol'})
    class PortMappingProperty():
        def __init__(self, *, port: jsii.Number, protocol: str):
            """
            :param port: ``CfnVirtualNode.PortMappingProperty.Port``.
            :param protocol: ``CfnVirtualNode.PortMappingProperty.Protocol``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualnode-portmapping.html
            """
            self._values = {
                'port': port,
                'protocol': protocol,
            }

        @property
        def port(self) -> jsii.Number:
            """``CfnVirtualNode.PortMappingProperty.Port``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualnode-portmapping.html#cfn-appmesh-virtualnode-portmapping-port
            """
            return self._values.get('port')

        @property
        def protocol(self) -> str:
            """``CfnVirtualNode.PortMappingProperty.Protocol``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualnode-portmapping.html#cfn-appmesh-virtualnode-portmapping-protocol
            """
            return self._values.get('protocol')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'PortMappingProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-appmesh.CfnVirtualNode.ServiceDiscoveryProperty", jsii_struct_bases=[], name_mapping={'aws_cloud_map': 'awsCloudMap', 'dns': 'dns'})
    class ServiceDiscoveryProperty():
        def __init__(self, *, aws_cloud_map: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnVirtualNode.AwsCloudMapServiceDiscoveryProperty"]]]=None, dns: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnVirtualNode.DnsServiceDiscoveryProperty"]]]=None):
            """
            :param aws_cloud_map: ``CfnVirtualNode.ServiceDiscoveryProperty.AWSCloudMap``.
            :param dns: ``CfnVirtualNode.ServiceDiscoveryProperty.DNS``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualnode-servicediscovery.html
            """
            self._values = {
            }
            if aws_cloud_map is not None: self._values["aws_cloud_map"] = aws_cloud_map
            if dns is not None: self._values["dns"] = dns

        @property
        def aws_cloud_map(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnVirtualNode.AwsCloudMapServiceDiscoveryProperty"]]]:
            """``CfnVirtualNode.ServiceDiscoveryProperty.AWSCloudMap``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualnode-servicediscovery.html#cfn-appmesh-virtualnode-servicediscovery-awscloudmap
            """
            return self._values.get('aws_cloud_map')

        @property
        def dns(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnVirtualNode.DnsServiceDiscoveryProperty"]]]:
            """``CfnVirtualNode.ServiceDiscoveryProperty.DNS``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualnode-servicediscovery.html#cfn-appmesh-virtualnode-servicediscovery-dns
            """
            return self._values.get('dns')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'ServiceDiscoveryProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-appmesh.CfnVirtualNode.VirtualNodeSpecProperty", jsii_struct_bases=[], name_mapping={'backends': 'backends', 'listeners': 'listeners', 'logging': 'logging', 'service_discovery': 'serviceDiscovery'})
    class VirtualNodeSpecProperty():
        def __init__(self, *, backends: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnVirtualNode.BackendProperty"]]]]]=None, listeners: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnVirtualNode.ListenerProperty"]]]]]=None, logging: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnVirtualNode.LoggingProperty"]]]=None, service_discovery: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnVirtualNode.ServiceDiscoveryProperty"]]]=None):
            """
            :param backends: ``CfnVirtualNode.VirtualNodeSpecProperty.Backends``.
            :param listeners: ``CfnVirtualNode.VirtualNodeSpecProperty.Listeners``.
            :param logging: ``CfnVirtualNode.VirtualNodeSpecProperty.Logging``.
            :param service_discovery: ``CfnVirtualNode.VirtualNodeSpecProperty.ServiceDiscovery``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualnode-virtualnodespec.html
            """
            self._values = {
            }
            if backends is not None: self._values["backends"] = backends
            if listeners is not None: self._values["listeners"] = listeners
            if logging is not None: self._values["logging"] = logging
            if service_discovery is not None: self._values["service_discovery"] = service_discovery

        @property
        def backends(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnVirtualNode.BackendProperty"]]]]]:
            """``CfnVirtualNode.VirtualNodeSpecProperty.Backends``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualnode-virtualnodespec.html#cfn-appmesh-virtualnode-virtualnodespec-backends
            """
            return self._values.get('backends')

        @property
        def listeners(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnVirtualNode.ListenerProperty"]]]]]:
            """``CfnVirtualNode.VirtualNodeSpecProperty.Listeners``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualnode-virtualnodespec.html#cfn-appmesh-virtualnode-virtualnodespec-listeners
            """
            return self._values.get('listeners')

        @property
        def logging(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnVirtualNode.LoggingProperty"]]]:
            """``CfnVirtualNode.VirtualNodeSpecProperty.Logging``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualnode-virtualnodespec.html#cfn-appmesh-virtualnode-virtualnodespec-logging
            """
            return self._values.get('logging')

        @property
        def service_discovery(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnVirtualNode.ServiceDiscoveryProperty"]]]:
            """``CfnVirtualNode.VirtualNodeSpecProperty.ServiceDiscovery``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualnode-virtualnodespec.html#cfn-appmesh-virtualnode-virtualnodespec-servicediscovery
            """
            return self._values.get('service_discovery')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'VirtualNodeSpecProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-appmesh.CfnVirtualNode.VirtualServiceBackendProperty", jsii_struct_bases=[], name_mapping={'virtual_service_name': 'virtualServiceName'})
    class VirtualServiceBackendProperty():
        def __init__(self, *, virtual_service_name: str):
            """
            :param virtual_service_name: ``CfnVirtualNode.VirtualServiceBackendProperty.VirtualServiceName``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualnode-virtualservicebackend.html
            """
            self._values = {
                'virtual_service_name': virtual_service_name,
            }

        @property
        def virtual_service_name(self) -> str:
            """``CfnVirtualNode.VirtualServiceBackendProperty.VirtualServiceName``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualnode-virtualservicebackend.html#cfn-appmesh-virtualnode-virtualservicebackend-virtualservicename
            """
            return self._values.get('virtual_service_name')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'VirtualServiceBackendProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



@jsii.data_type(jsii_type="@aws-cdk/aws-appmesh.CfnVirtualNodeProps", jsii_struct_bases=[], name_mapping={'mesh_name': 'meshName', 'spec': 'spec', 'virtual_node_name': 'virtualNodeName', 'tags': 'tags'})
class CfnVirtualNodeProps():
    def __init__(self, *, mesh_name: str, spec: typing.Union[aws_cdk.core.IResolvable, "CfnVirtualNode.VirtualNodeSpecProperty"], virtual_node_name: str, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None):
        """Properties for defining a ``AWS::AppMesh::VirtualNode``.

        :param mesh_name: ``AWS::AppMesh::VirtualNode.MeshName``.
        :param spec: ``AWS::AppMesh::VirtualNode.Spec``.
        :param virtual_node_name: ``AWS::AppMesh::VirtualNode.VirtualNodeName``.
        :param tags: ``AWS::AppMesh::VirtualNode.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-virtualnode.html
        """
        self._values = {
            'mesh_name': mesh_name,
            'spec': spec,
            'virtual_node_name': virtual_node_name,
        }
        if tags is not None: self._values["tags"] = tags

    @property
    def mesh_name(self) -> str:
        """``AWS::AppMesh::VirtualNode.MeshName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-virtualnode.html#cfn-appmesh-virtualnode-meshname
        """
        return self._values.get('mesh_name')

    @property
    def spec(self) -> typing.Union[aws_cdk.core.IResolvable, "CfnVirtualNode.VirtualNodeSpecProperty"]:
        """``AWS::AppMesh::VirtualNode.Spec``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-virtualnode.html#cfn-appmesh-virtualnode-spec
        """
        return self._values.get('spec')

    @property
    def virtual_node_name(self) -> str:
        """``AWS::AppMesh::VirtualNode.VirtualNodeName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-virtualnode.html#cfn-appmesh-virtualnode-virtualnodename
        """
        return self._values.get('virtual_node_name')

    @property
    def tags(self) -> typing.Optional[typing.List[aws_cdk.core.CfnTag]]:
        """``AWS::AppMesh::VirtualNode.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-virtualnode.html#cfn-appmesh-virtualnode-tags
        """
        return self._values.get('tags')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnVirtualNodeProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnVirtualRouter(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-appmesh.CfnVirtualRouter"):
    """A CloudFormation ``AWS::AppMesh::VirtualRouter``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-virtualrouter.html
    cloudformationResource:
    :cloudformationResource:: AWS::AppMesh::VirtualRouter
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, mesh_name: str, spec: typing.Union[aws_cdk.core.IResolvable, "VirtualRouterSpecProperty"], virtual_router_name: str, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None) -> None:
        """Create a new ``AWS::AppMesh::VirtualRouter``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param mesh_name: ``AWS::AppMesh::VirtualRouter.MeshName``.
        :param spec: ``AWS::AppMesh::VirtualRouter.Spec``.
        :param virtual_router_name: ``AWS::AppMesh::VirtualRouter.VirtualRouterName``.
        :param tags: ``AWS::AppMesh::VirtualRouter.Tags``.
        """
        props = CfnVirtualRouterProps(mesh_name=mesh_name, spec=spec, virtual_router_name=virtual_router_name, tags=tags)

        jsii.create(CfnVirtualRouter, self, [scope, id, props])

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
    @jsii.member(jsii_name="attrMeshName")
    def attr_mesh_name(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: MeshName
        """
        return jsii.get(self, "attrMeshName")

    @property
    @jsii.member(jsii_name="attrUid")
    def attr_uid(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: Uid
        """
        return jsii.get(self, "attrUid")

    @property
    @jsii.member(jsii_name="attrVirtualRouterName")
    def attr_virtual_router_name(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: VirtualRouterName
        """
        return jsii.get(self, "attrVirtualRouterName")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        """``AWS::AppMesh::VirtualRouter.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-virtualrouter.html#cfn-appmesh-virtualrouter-tags
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="meshName")
    def mesh_name(self) -> str:
        """``AWS::AppMesh::VirtualRouter.MeshName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-virtualrouter.html#cfn-appmesh-virtualrouter-meshname
        """
        return jsii.get(self, "meshName")

    @mesh_name.setter
    def mesh_name(self, value: str):
        return jsii.set(self, "meshName", value)

    @property
    @jsii.member(jsii_name="spec")
    def spec(self) -> typing.Union[aws_cdk.core.IResolvable, "VirtualRouterSpecProperty"]:
        """``AWS::AppMesh::VirtualRouter.Spec``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-virtualrouter.html#cfn-appmesh-virtualrouter-spec
        """
        return jsii.get(self, "spec")

    @spec.setter
    def spec(self, value: typing.Union[aws_cdk.core.IResolvable, "VirtualRouterSpecProperty"]):
        return jsii.set(self, "spec", value)

    @property
    @jsii.member(jsii_name="virtualRouterName")
    def virtual_router_name(self) -> str:
        """``AWS::AppMesh::VirtualRouter.VirtualRouterName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-virtualrouter.html#cfn-appmesh-virtualrouter-virtualroutername
        """
        return jsii.get(self, "virtualRouterName")

    @virtual_router_name.setter
    def virtual_router_name(self, value: str):
        return jsii.set(self, "virtualRouterName", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-appmesh.CfnVirtualRouter.PortMappingProperty", jsii_struct_bases=[], name_mapping={'port': 'port', 'protocol': 'protocol'})
    class PortMappingProperty():
        def __init__(self, *, port: jsii.Number, protocol: str):
            """
            :param port: ``CfnVirtualRouter.PortMappingProperty.Port``.
            :param protocol: ``CfnVirtualRouter.PortMappingProperty.Protocol``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualrouter-portmapping.html
            """
            self._values = {
                'port': port,
                'protocol': protocol,
            }

        @property
        def port(self) -> jsii.Number:
            """``CfnVirtualRouter.PortMappingProperty.Port``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualrouter-portmapping.html#cfn-appmesh-virtualrouter-portmapping-port
            """
            return self._values.get('port')

        @property
        def protocol(self) -> str:
            """``CfnVirtualRouter.PortMappingProperty.Protocol``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualrouter-portmapping.html#cfn-appmesh-virtualrouter-portmapping-protocol
            """
            return self._values.get('protocol')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'PortMappingProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-appmesh.CfnVirtualRouter.VirtualRouterListenerProperty", jsii_struct_bases=[], name_mapping={'port_mapping': 'portMapping'})
    class VirtualRouterListenerProperty():
        def __init__(self, *, port_mapping: typing.Union[aws_cdk.core.IResolvable, "CfnVirtualRouter.PortMappingProperty"]):
            """
            :param port_mapping: ``CfnVirtualRouter.VirtualRouterListenerProperty.PortMapping``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualrouter-virtualrouterlistener.html
            """
            self._values = {
                'port_mapping': port_mapping,
            }

        @property
        def port_mapping(self) -> typing.Union[aws_cdk.core.IResolvable, "CfnVirtualRouter.PortMappingProperty"]:
            """``CfnVirtualRouter.VirtualRouterListenerProperty.PortMapping``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualrouter-virtualrouterlistener.html#cfn-appmesh-virtualrouter-virtualrouterlistener-portmapping
            """
            return self._values.get('port_mapping')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'VirtualRouterListenerProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-appmesh.CfnVirtualRouter.VirtualRouterSpecProperty", jsii_struct_bases=[], name_mapping={'listeners': 'listeners'})
    class VirtualRouterSpecProperty():
        def __init__(self, *, listeners: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnVirtualRouter.VirtualRouterListenerProperty"]]]):
            """
            :param listeners: ``CfnVirtualRouter.VirtualRouterSpecProperty.Listeners``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualrouter-virtualrouterspec.html
            """
            self._values = {
                'listeners': listeners,
            }

        @property
        def listeners(self) -> typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnVirtualRouter.VirtualRouterListenerProperty"]]]:
            """``CfnVirtualRouter.VirtualRouterSpecProperty.Listeners``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualrouter-virtualrouterspec.html#cfn-appmesh-virtualrouter-virtualrouterspec-listeners
            """
            return self._values.get('listeners')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'VirtualRouterSpecProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



@jsii.data_type(jsii_type="@aws-cdk/aws-appmesh.CfnVirtualRouterProps", jsii_struct_bases=[], name_mapping={'mesh_name': 'meshName', 'spec': 'spec', 'virtual_router_name': 'virtualRouterName', 'tags': 'tags'})
class CfnVirtualRouterProps():
    def __init__(self, *, mesh_name: str, spec: typing.Union[aws_cdk.core.IResolvable, "CfnVirtualRouter.VirtualRouterSpecProperty"], virtual_router_name: str, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None):
        """Properties for defining a ``AWS::AppMesh::VirtualRouter``.

        :param mesh_name: ``AWS::AppMesh::VirtualRouter.MeshName``.
        :param spec: ``AWS::AppMesh::VirtualRouter.Spec``.
        :param virtual_router_name: ``AWS::AppMesh::VirtualRouter.VirtualRouterName``.
        :param tags: ``AWS::AppMesh::VirtualRouter.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-virtualrouter.html
        """
        self._values = {
            'mesh_name': mesh_name,
            'spec': spec,
            'virtual_router_name': virtual_router_name,
        }
        if tags is not None: self._values["tags"] = tags

    @property
    def mesh_name(self) -> str:
        """``AWS::AppMesh::VirtualRouter.MeshName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-virtualrouter.html#cfn-appmesh-virtualrouter-meshname
        """
        return self._values.get('mesh_name')

    @property
    def spec(self) -> typing.Union[aws_cdk.core.IResolvable, "CfnVirtualRouter.VirtualRouterSpecProperty"]:
        """``AWS::AppMesh::VirtualRouter.Spec``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-virtualrouter.html#cfn-appmesh-virtualrouter-spec
        """
        return self._values.get('spec')

    @property
    def virtual_router_name(self) -> str:
        """``AWS::AppMesh::VirtualRouter.VirtualRouterName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-virtualrouter.html#cfn-appmesh-virtualrouter-virtualroutername
        """
        return self._values.get('virtual_router_name')

    @property
    def tags(self) -> typing.Optional[typing.List[aws_cdk.core.CfnTag]]:
        """``AWS::AppMesh::VirtualRouter.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-virtualrouter.html#cfn-appmesh-virtualrouter-tags
        """
        return self._values.get('tags')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnVirtualRouterProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnVirtualService(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-appmesh.CfnVirtualService"):
    """A CloudFormation ``AWS::AppMesh::VirtualService``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-virtualservice.html
    cloudformationResource:
    :cloudformationResource:: AWS::AppMesh::VirtualService
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, mesh_name: str, spec: typing.Union[aws_cdk.core.IResolvable, "VirtualServiceSpecProperty"], virtual_service_name: str, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None) -> None:
        """Create a new ``AWS::AppMesh::VirtualService``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param mesh_name: ``AWS::AppMesh::VirtualService.MeshName``.
        :param spec: ``AWS::AppMesh::VirtualService.Spec``.
        :param virtual_service_name: ``AWS::AppMesh::VirtualService.VirtualServiceName``.
        :param tags: ``AWS::AppMesh::VirtualService.Tags``.
        """
        props = CfnVirtualServiceProps(mesh_name=mesh_name, spec=spec, virtual_service_name=virtual_service_name, tags=tags)

        jsii.create(CfnVirtualService, self, [scope, id, props])

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
    @jsii.member(jsii_name="attrMeshName")
    def attr_mesh_name(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: MeshName
        """
        return jsii.get(self, "attrMeshName")

    @property
    @jsii.member(jsii_name="attrUid")
    def attr_uid(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: Uid
        """
        return jsii.get(self, "attrUid")

    @property
    @jsii.member(jsii_name="attrVirtualServiceName")
    def attr_virtual_service_name(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: VirtualServiceName
        """
        return jsii.get(self, "attrVirtualServiceName")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        """``AWS::AppMesh::VirtualService.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-virtualservice.html#cfn-appmesh-virtualservice-tags
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="meshName")
    def mesh_name(self) -> str:
        """``AWS::AppMesh::VirtualService.MeshName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-virtualservice.html#cfn-appmesh-virtualservice-meshname
        """
        return jsii.get(self, "meshName")

    @mesh_name.setter
    def mesh_name(self, value: str):
        return jsii.set(self, "meshName", value)

    @property
    @jsii.member(jsii_name="spec")
    def spec(self) -> typing.Union[aws_cdk.core.IResolvable, "VirtualServiceSpecProperty"]:
        """``AWS::AppMesh::VirtualService.Spec``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-virtualservice.html#cfn-appmesh-virtualservice-spec
        """
        return jsii.get(self, "spec")

    @spec.setter
    def spec(self, value: typing.Union[aws_cdk.core.IResolvable, "VirtualServiceSpecProperty"]):
        return jsii.set(self, "spec", value)

    @property
    @jsii.member(jsii_name="virtualServiceName")
    def virtual_service_name(self) -> str:
        """``AWS::AppMesh::VirtualService.VirtualServiceName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-virtualservice.html#cfn-appmesh-virtualservice-virtualservicename
        """
        return jsii.get(self, "virtualServiceName")

    @virtual_service_name.setter
    def virtual_service_name(self, value: str):
        return jsii.set(self, "virtualServiceName", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-appmesh.CfnVirtualService.VirtualNodeServiceProviderProperty", jsii_struct_bases=[], name_mapping={'virtual_node_name': 'virtualNodeName'})
    class VirtualNodeServiceProviderProperty():
        def __init__(self, *, virtual_node_name: str):
            """
            :param virtual_node_name: ``CfnVirtualService.VirtualNodeServiceProviderProperty.VirtualNodeName``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualservice-virtualnodeserviceprovider.html
            """
            self._values = {
                'virtual_node_name': virtual_node_name,
            }

        @property
        def virtual_node_name(self) -> str:
            """``CfnVirtualService.VirtualNodeServiceProviderProperty.VirtualNodeName``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualservice-virtualnodeserviceprovider.html#cfn-appmesh-virtualservice-virtualnodeserviceprovider-virtualnodename
            """
            return self._values.get('virtual_node_name')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'VirtualNodeServiceProviderProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-appmesh.CfnVirtualService.VirtualRouterServiceProviderProperty", jsii_struct_bases=[], name_mapping={'virtual_router_name': 'virtualRouterName'})
    class VirtualRouterServiceProviderProperty():
        def __init__(self, *, virtual_router_name: str):
            """
            :param virtual_router_name: ``CfnVirtualService.VirtualRouterServiceProviderProperty.VirtualRouterName``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualservice-virtualrouterserviceprovider.html
            """
            self._values = {
                'virtual_router_name': virtual_router_name,
            }

        @property
        def virtual_router_name(self) -> str:
            """``CfnVirtualService.VirtualRouterServiceProviderProperty.VirtualRouterName``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualservice-virtualrouterserviceprovider.html#cfn-appmesh-virtualservice-virtualrouterserviceprovider-virtualroutername
            """
            return self._values.get('virtual_router_name')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'VirtualRouterServiceProviderProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-appmesh.CfnVirtualService.VirtualServiceProviderProperty", jsii_struct_bases=[], name_mapping={'virtual_node': 'virtualNode', 'virtual_router': 'virtualRouter'})
    class VirtualServiceProviderProperty():
        def __init__(self, *, virtual_node: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnVirtualService.VirtualNodeServiceProviderProperty"]]]=None, virtual_router: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnVirtualService.VirtualRouterServiceProviderProperty"]]]=None):
            """
            :param virtual_node: ``CfnVirtualService.VirtualServiceProviderProperty.VirtualNode``.
            :param virtual_router: ``CfnVirtualService.VirtualServiceProviderProperty.VirtualRouter``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualservice-virtualserviceprovider.html
            """
            self._values = {
            }
            if virtual_node is not None: self._values["virtual_node"] = virtual_node
            if virtual_router is not None: self._values["virtual_router"] = virtual_router

        @property
        def virtual_node(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnVirtualService.VirtualNodeServiceProviderProperty"]]]:
            """``CfnVirtualService.VirtualServiceProviderProperty.VirtualNode``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualservice-virtualserviceprovider.html#cfn-appmesh-virtualservice-virtualserviceprovider-virtualnode
            """
            return self._values.get('virtual_node')

        @property
        def virtual_router(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnVirtualService.VirtualRouterServiceProviderProperty"]]]:
            """``CfnVirtualService.VirtualServiceProviderProperty.VirtualRouter``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualservice-virtualserviceprovider.html#cfn-appmesh-virtualservice-virtualserviceprovider-virtualrouter
            """
            return self._values.get('virtual_router')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'VirtualServiceProviderProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-appmesh.CfnVirtualService.VirtualServiceSpecProperty", jsii_struct_bases=[], name_mapping={'provider': 'provider'})
    class VirtualServiceSpecProperty():
        def __init__(self, *, provider: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnVirtualService.VirtualServiceProviderProperty"]]]=None):
            """
            :param provider: ``CfnVirtualService.VirtualServiceSpecProperty.Provider``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualservice-virtualservicespec.html
            """
            self._values = {
            }
            if provider is not None: self._values["provider"] = provider

        @property
        def provider(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnVirtualService.VirtualServiceProviderProperty"]]]:
            """``CfnVirtualService.VirtualServiceSpecProperty.Provider``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualservice-virtualservicespec.html#cfn-appmesh-virtualservice-virtualservicespec-provider
            """
            return self._values.get('provider')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'VirtualServiceSpecProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



@jsii.data_type(jsii_type="@aws-cdk/aws-appmesh.CfnVirtualServiceProps", jsii_struct_bases=[], name_mapping={'mesh_name': 'meshName', 'spec': 'spec', 'virtual_service_name': 'virtualServiceName', 'tags': 'tags'})
class CfnVirtualServiceProps():
    def __init__(self, *, mesh_name: str, spec: typing.Union[aws_cdk.core.IResolvable, "CfnVirtualService.VirtualServiceSpecProperty"], virtual_service_name: str, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None):
        """Properties for defining a ``AWS::AppMesh::VirtualService``.

        :param mesh_name: ``AWS::AppMesh::VirtualService.MeshName``.
        :param spec: ``AWS::AppMesh::VirtualService.Spec``.
        :param virtual_service_name: ``AWS::AppMesh::VirtualService.VirtualServiceName``.
        :param tags: ``AWS::AppMesh::VirtualService.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-virtualservice.html
        """
        self._values = {
            'mesh_name': mesh_name,
            'spec': spec,
            'virtual_service_name': virtual_service_name,
        }
        if tags is not None: self._values["tags"] = tags

    @property
    def mesh_name(self) -> str:
        """``AWS::AppMesh::VirtualService.MeshName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-virtualservice.html#cfn-appmesh-virtualservice-meshname
        """
        return self._values.get('mesh_name')

    @property
    def spec(self) -> typing.Union[aws_cdk.core.IResolvable, "CfnVirtualService.VirtualServiceSpecProperty"]:
        """``AWS::AppMesh::VirtualService.Spec``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-virtualservice.html#cfn-appmesh-virtualservice-spec
        """
        return self._values.get('spec')

    @property
    def virtual_service_name(self) -> str:
        """``AWS::AppMesh::VirtualService.VirtualServiceName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-virtualservice.html#cfn-appmesh-virtualservice-virtualservicename
        """
        return self._values.get('virtual_service_name')

    @property
    def tags(self) -> typing.Optional[typing.List[aws_cdk.core.CfnTag]]:
        """``AWS::AppMesh::VirtualService.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-virtualservice.html#cfn-appmesh-virtualservice-tags
        """
        return self._values.get('tags')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnVirtualServiceProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


@jsii.data_type(jsii_type="@aws-cdk/aws-appmesh.HealthCheck", jsii_struct_bases=[], name_mapping={'healthy_threshold': 'healthyThreshold', 'interval': 'interval', 'path': 'path', 'port': 'port', 'protocol': 'protocol', 'timeout': 'timeout', 'unhealthy_threshold': 'unhealthyThreshold'})
class HealthCheck():
    def __init__(self, *, healthy_threshold: typing.Optional[jsii.Number]=None, interval: typing.Optional[aws_cdk.core.Duration]=None, path: typing.Optional[str]=None, port: typing.Optional[jsii.Number]=None, protocol: typing.Optional["Protocol"]=None, timeout: typing.Optional[aws_cdk.core.Duration]=None, unhealthy_threshold: typing.Optional[jsii.Number]=None):
        """Properties used to define healthchecks when creating virtual nodes. All values have a default if only specified as {} when creating. If property not set, then no healthchecks will be defined.

        :param healthy_threshold: Number of successful attempts before considering the node UP. Default: 2
        :param interval: Interval in milliseconds to re-check. Default: 5 seconds
        :param path: The path where the application expects any health-checks, this can also be the application path. Default: /
        :param port: The TCP port number for the healthcheck. Default: - same as corresponding port mapping
        :param protocol: The protocol to use for the healthcheck, for convinience a const enum has been defined. Protocol.HTTP or Protocol.TCP. Default: - same as corresponding port mapping
        :param timeout: Timeout in milli-seconds for the healthcheck to be considered a fail. Default: 2 seconds
        :param unhealthy_threshold: Number of failed attempts before considering the node DOWN. Default: 2

        stability
        :stability: experimental
        """
        self._values = {
        }
        if healthy_threshold is not None: self._values["healthy_threshold"] = healthy_threshold
        if interval is not None: self._values["interval"] = interval
        if path is not None: self._values["path"] = path
        if port is not None: self._values["port"] = port
        if protocol is not None: self._values["protocol"] = protocol
        if timeout is not None: self._values["timeout"] = timeout
        if unhealthy_threshold is not None: self._values["unhealthy_threshold"] = unhealthy_threshold

    @property
    def healthy_threshold(self) -> typing.Optional[jsii.Number]:
        """Number of successful attempts before considering the node UP.

        default
        :default: 2

        stability
        :stability: experimental
        """
        return self._values.get('healthy_threshold')

    @property
    def interval(self) -> typing.Optional[aws_cdk.core.Duration]:
        """Interval in milliseconds to re-check.

        default
        :default: 5 seconds

        stability
        :stability: experimental
        """
        return self._values.get('interval')

    @property
    def path(self) -> typing.Optional[str]:
        """The path where the application expects any health-checks, this can also be the application path.

        default
        :default: /

        stability
        :stability: experimental
        """
        return self._values.get('path')

    @property
    def port(self) -> typing.Optional[jsii.Number]:
        """The TCP port number for the healthcheck.

        default
        :default: - same as corresponding port mapping

        stability
        :stability: experimental
        """
        return self._values.get('port')

    @property
    def protocol(self) -> typing.Optional["Protocol"]:
        """The protocol to use for the healthcheck, for convinience a const enum has been defined. Protocol.HTTP or Protocol.TCP.

        default
        :default: - same as corresponding port mapping

        stability
        :stability: experimental
        """
        return self._values.get('protocol')

    @property
    def timeout(self) -> typing.Optional[aws_cdk.core.Duration]:
        """Timeout in milli-seconds for the healthcheck to be considered a fail.

        default
        :default: 2 seconds

        stability
        :stability: experimental
        """
        return self._values.get('timeout')

    @property
    def unhealthy_threshold(self) -> typing.Optional[jsii.Number]:
        """Number of failed attempts before considering the node DOWN.

        default
        :default: 2

        stability
        :stability: experimental
        """
        return self._values.get('unhealthy_threshold')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'HealthCheck(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


@jsii.interface(jsii_type="@aws-cdk/aws-appmesh.IMesh")
class IMesh(aws_cdk.core.IResource, jsii.compat.Protocol):
    """Interface wich all Mesh based classes MUST implement.

    stability
    :stability: experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IMeshProxy

    @property
    @jsii.member(jsii_name="meshArn")
    def mesh_arn(self) -> str:
        """The Amazon Resource Name (ARN) of the AppMesh mesh.

        stability
        :stability: experimental
        attribute:
        :attribute:: true
        """
        ...

    @property
    @jsii.member(jsii_name="meshName")
    def mesh_name(self) -> str:
        """The name of the AppMesh mesh.

        stability
        :stability: experimental
        attribute:
        :attribute:: true
        """
        ...

    @jsii.member(jsii_name="addVirtualNode")
    def add_virtual_node(self, id: str, *, backends: typing.Optional[typing.List["IVirtualService"]]=None, cloud_map_service: typing.Optional[aws_cdk.aws_servicediscovery.IService]=None, cloud_map_service_instance_attributes: typing.Optional[typing.Mapping[str,str]]=None, dns_host_name: typing.Optional[str]=None, listener: typing.Optional["VirtualNodeListener"]=None, virtual_node_name: typing.Optional[str]=None) -> "VirtualNode":
        """Adds a VirtualNode to the Mesh.

        :param id: -
        :param props: -
        :param backends: Virtual Services that this is node expected to send outbound traffic to. Default: - No backends
        :param cloud_map_service: CloudMap service where Virtual Node members register themselves. Instances registering themselves into this CloudMap will be considered part of the Virtual Node. Default: - Don't use CloudMap-based service discovery
        :param cloud_map_service_instance_attributes: Filter down the list of CloudMap service instance. Default: - No CloudMap instance filter
        :param dns_host_name: Host name of DNS record used to discover Virtual Node members. The IP addresses returned by querying this DNS record will be considered part of the Virtual Node. Default: - Don't use DNS-based service discovery
        :param listener: Initial listener for the virtual node. Default: - No listeners
        :param virtual_node_name: The name of the VirtualNode. Default: - A name is automatically determined

        stability
        :stability: experimental
        """
        ...

    @jsii.member(jsii_name="addVirtualRouter")
    def add_virtual_router(self, id: str, *, listener: typing.Optional["Listener"]=None, virtual_router_name: typing.Optional[str]=None) -> "VirtualRouter":
        """Adds a VirtualRouter to the Mesh with the given id and props.

        :param id: -
        :param props: -
        :param listener: Listener specification for the virtual router. Default: - A listener on HTTP port 8080
        :param virtual_router_name: The name of the VirtualRouter. Default: - A name is automatically determined

        stability
        :stability: experimental
        """
        ...

    @jsii.member(jsii_name="addVirtualService")
    def add_virtual_service(self, id: str, *, virtual_node: typing.Optional["IVirtualNode"]=None, virtual_router: typing.Optional["IVirtualRouter"]=None, virtual_service_name: typing.Optional[str]=None) -> "VirtualService":
        """Adds a VirtualService with the given id.

        :param id: -
        :param props: -
        :param virtual_node: The VirtualNode attached to the virtual service. Default: - At most one of virtualRouter and virtualNode is allowed.
        :param virtual_router: The VirtualRouter which the VirtualService uses as provider. Default: - At most one of virtualRouter and virtualNode is allowed.
        :param virtual_service_name: The name of the VirtualService. It is recommended this follows the fully-qualified domain name format, such as "my-service.default.svc.cluster.local". Default: - A name is automatically generated

        stability
        :stability: experimental
        """
        ...


class _IMeshProxy(jsii.proxy_for(aws_cdk.core.IResource)):
    """Interface wich all Mesh based classes MUST implement.

    stability
    :stability: experimental
    """
    __jsii_type__ = "@aws-cdk/aws-appmesh.IMesh"
    @property
    @jsii.member(jsii_name="meshArn")
    def mesh_arn(self) -> str:
        """The Amazon Resource Name (ARN) of the AppMesh mesh.

        stability
        :stability: experimental
        attribute:
        :attribute:: true
        """
        return jsii.get(self, "meshArn")

    @property
    @jsii.member(jsii_name="meshName")
    def mesh_name(self) -> str:
        """The name of the AppMesh mesh.

        stability
        :stability: experimental
        attribute:
        :attribute:: true
        """
        return jsii.get(self, "meshName")

    @jsii.member(jsii_name="addVirtualNode")
    def add_virtual_node(self, id: str, *, backends: typing.Optional[typing.List["IVirtualService"]]=None, cloud_map_service: typing.Optional[aws_cdk.aws_servicediscovery.IService]=None, cloud_map_service_instance_attributes: typing.Optional[typing.Mapping[str,str]]=None, dns_host_name: typing.Optional[str]=None, listener: typing.Optional["VirtualNodeListener"]=None, virtual_node_name: typing.Optional[str]=None) -> "VirtualNode":
        """Adds a VirtualNode to the Mesh.

        :param id: -
        :param props: -
        :param backends: Virtual Services that this is node expected to send outbound traffic to. Default: - No backends
        :param cloud_map_service: CloudMap service where Virtual Node members register themselves. Instances registering themselves into this CloudMap will be considered part of the Virtual Node. Default: - Don't use CloudMap-based service discovery
        :param cloud_map_service_instance_attributes: Filter down the list of CloudMap service instance. Default: - No CloudMap instance filter
        :param dns_host_name: Host name of DNS record used to discover Virtual Node members. The IP addresses returned by querying this DNS record will be considered part of the Virtual Node. Default: - Don't use DNS-based service discovery
        :param listener: Initial listener for the virtual node. Default: - No listeners
        :param virtual_node_name: The name of the VirtualNode. Default: - A name is automatically determined

        stability
        :stability: experimental
        """
        props = VirtualNodeBaseProps(backends=backends, cloud_map_service=cloud_map_service, cloud_map_service_instance_attributes=cloud_map_service_instance_attributes, dns_host_name=dns_host_name, listener=listener, virtual_node_name=virtual_node_name)

        return jsii.invoke(self, "addVirtualNode", [id, props])

    @jsii.member(jsii_name="addVirtualRouter")
    def add_virtual_router(self, id: str, *, listener: typing.Optional["Listener"]=None, virtual_router_name: typing.Optional[str]=None) -> "VirtualRouter":
        """Adds a VirtualRouter to the Mesh with the given id and props.

        :param id: -
        :param props: -
        :param listener: Listener specification for the virtual router. Default: - A listener on HTTP port 8080
        :param virtual_router_name: The name of the VirtualRouter. Default: - A name is automatically determined

        stability
        :stability: experimental
        """
        props = VirtualRouterBaseProps(listener=listener, virtual_router_name=virtual_router_name)

        return jsii.invoke(self, "addVirtualRouter", [id, props])

    @jsii.member(jsii_name="addVirtualService")
    def add_virtual_service(self, id: str, *, virtual_node: typing.Optional["IVirtualNode"]=None, virtual_router: typing.Optional["IVirtualRouter"]=None, virtual_service_name: typing.Optional[str]=None) -> "VirtualService":
        """Adds a VirtualService with the given id.

        :param id: -
        :param props: -
        :param virtual_node: The VirtualNode attached to the virtual service. Default: - At most one of virtualRouter and virtualNode is allowed.
        :param virtual_router: The VirtualRouter which the VirtualService uses as provider. Default: - At most one of virtualRouter and virtualNode is allowed.
        :param virtual_service_name: The name of the VirtualService. It is recommended this follows the fully-qualified domain name format, such as "my-service.default.svc.cluster.local". Default: - A name is automatically generated

        stability
        :stability: experimental
        """
        props = VirtualServiceBaseProps(virtual_node=virtual_node, virtual_router=virtual_router, virtual_service_name=virtual_service_name)

        return jsii.invoke(self, "addVirtualService", [id, props])


@jsii.interface(jsii_type="@aws-cdk/aws-appmesh.IRoute")
class IRoute(aws_cdk.core.IResource, jsii.compat.Protocol):
    """Interface for which all Route based classes MUST implement.

    stability
    :stability: experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IRouteProxy

    @property
    @jsii.member(jsii_name="routeArn")
    def route_arn(self) -> str:
        """The Amazon Resource Name (ARN) for the route.

        stability
        :stability: experimental
        attribute:
        :attribute:: true
        """
        ...

    @property
    @jsii.member(jsii_name="routeName")
    def route_name(self) -> str:
        """The name of the route.

        stability
        :stability: experimental
        attribute:
        :attribute:: true
        """
        ...


class _IRouteProxy(jsii.proxy_for(aws_cdk.core.IResource)):
    """Interface for which all Route based classes MUST implement.

    stability
    :stability: experimental
    """
    __jsii_type__ = "@aws-cdk/aws-appmesh.IRoute"
    @property
    @jsii.member(jsii_name="routeArn")
    def route_arn(self) -> str:
        """The Amazon Resource Name (ARN) for the route.

        stability
        :stability: experimental
        attribute:
        :attribute:: true
        """
        return jsii.get(self, "routeArn")

    @property
    @jsii.member(jsii_name="routeName")
    def route_name(self) -> str:
        """The name of the route.

        stability
        :stability: experimental
        attribute:
        :attribute:: true
        """
        return jsii.get(self, "routeName")


@jsii.interface(jsii_type="@aws-cdk/aws-appmesh.IVirtualNode")
class IVirtualNode(aws_cdk.core.IResource, jsii.compat.Protocol):
    """Interface which all VirtualNode based classes must implement.

    stability
    :stability: experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IVirtualNodeProxy

    @property
    @jsii.member(jsii_name="virtualNodeArn")
    def virtual_node_arn(self) -> str:
        """The Amazon Resource Name belonging to the VirtualNdoe.

        Set this value as the APPMESH_VIRTUAL_NODE_NAME environment variable for
        your task group's Envoy proxy container in your task definition or pod
        spec.

        stability
        :stability: experimental
        attribute:
        :attribute:: true
        """
        ...

    @property
    @jsii.member(jsii_name="virtualNodeName")
    def virtual_node_name(self) -> str:
        """The name of the VirtualNode.

        stability
        :stability: experimental
        attribute:
        :attribute:: true
        """
        ...

    @jsii.member(jsii_name="addBackends")
    def add_backends(self, *props: "IVirtualService") -> None:
        """Utility method to add backends for existing or new VirtualNodes.

        :param props: -

        stability
        :stability: experimental
        """
        ...

    @jsii.member(jsii_name="addListeners")
    def add_listeners(self, *listeners: "VirtualNodeListener") -> None:
        """Utility method to add Node Listeners for new or existing VirtualNodes.

        :param listeners: -

        stability
        :stability: experimental
        """
        ...


class _IVirtualNodeProxy(jsii.proxy_for(aws_cdk.core.IResource)):
    """Interface which all VirtualNode based classes must implement.

    stability
    :stability: experimental
    """
    __jsii_type__ = "@aws-cdk/aws-appmesh.IVirtualNode"
    @property
    @jsii.member(jsii_name="virtualNodeArn")
    def virtual_node_arn(self) -> str:
        """The Amazon Resource Name belonging to the VirtualNdoe.

        Set this value as the APPMESH_VIRTUAL_NODE_NAME environment variable for
        your task group's Envoy proxy container in your task definition or pod
        spec.

        stability
        :stability: experimental
        attribute:
        :attribute:: true
        """
        return jsii.get(self, "virtualNodeArn")

    @property
    @jsii.member(jsii_name="virtualNodeName")
    def virtual_node_name(self) -> str:
        """The name of the VirtualNode.

        stability
        :stability: experimental
        attribute:
        :attribute:: true
        """
        return jsii.get(self, "virtualNodeName")

    @jsii.member(jsii_name="addBackends")
    def add_backends(self, *props: "IVirtualService") -> None:
        """Utility method to add backends for existing or new VirtualNodes.

        :param props: -

        stability
        :stability: experimental
        """
        return jsii.invoke(self, "addBackends", [*props])

    @jsii.member(jsii_name="addListeners")
    def add_listeners(self, *listeners: "VirtualNodeListener") -> None:
        """Utility method to add Node Listeners for new or existing VirtualNodes.

        :param listeners: -

        stability
        :stability: experimental
        """
        return jsii.invoke(self, "addListeners", [*listeners])


@jsii.interface(jsii_type="@aws-cdk/aws-appmesh.IVirtualRouter")
class IVirtualRouter(aws_cdk.core.IResource, jsii.compat.Protocol):
    """Interface which all VirtualRouter based classes MUST implement.

    stability
    :stability: experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IVirtualRouterProxy

    @property
    @jsii.member(jsii_name="mesh")
    def mesh(self) -> "IMesh":
        """The  service mesh that the virtual router resides in.

        stability
        :stability: experimental
        """
        ...

    @property
    @jsii.member(jsii_name="virtualRouterArn")
    def virtual_router_arn(self) -> str:
        """The Amazon Resource Name (ARN) for the VirtualRouter.

        stability
        :stability: experimental
        attribute:
        :attribute:: true
        """
        ...

    @property
    @jsii.member(jsii_name="virtualRouterName")
    def virtual_router_name(self) -> str:
        """The name of the VirtualRouter.

        stability
        :stability: experimental
        attribute:
        :attribute:: true
        """
        ...

    @jsii.member(jsii_name="addRoute")
    def add_route(self, id: str, *, route_targets: typing.List["WeightedTargetProps"], prefix: typing.Optional[str]=None, route_name: typing.Optional[str]=None, route_type: typing.Optional["RouteType"]=None) -> "Route":
        """Add a single route to the router.

        :param id: -
        :param props: -
        :param route_targets: Array of weighted route targets.
        :param prefix: The path prefix to match for the route. Default: "/" if http otherwise none
        :param route_name: The name of the route. Default: - An automatically generated name
        :param route_type: Weather the route is HTTP based. Default: - HTTP if ``prefix`` is given, TCP otherwise

        stability
        :stability: experimental
        """
        ...


class _IVirtualRouterProxy(jsii.proxy_for(aws_cdk.core.IResource)):
    """Interface which all VirtualRouter based classes MUST implement.

    stability
    :stability: experimental
    """
    __jsii_type__ = "@aws-cdk/aws-appmesh.IVirtualRouter"
    @property
    @jsii.member(jsii_name="mesh")
    def mesh(self) -> "IMesh":
        """The  service mesh that the virtual router resides in.

        stability
        :stability: experimental
        """
        return jsii.get(self, "mesh")

    @property
    @jsii.member(jsii_name="virtualRouterArn")
    def virtual_router_arn(self) -> str:
        """The Amazon Resource Name (ARN) for the VirtualRouter.

        stability
        :stability: experimental
        attribute:
        :attribute:: true
        """
        return jsii.get(self, "virtualRouterArn")

    @property
    @jsii.member(jsii_name="virtualRouterName")
    def virtual_router_name(self) -> str:
        """The name of the VirtualRouter.

        stability
        :stability: experimental
        attribute:
        :attribute:: true
        """
        return jsii.get(self, "virtualRouterName")

    @jsii.member(jsii_name="addRoute")
    def add_route(self, id: str, *, route_targets: typing.List["WeightedTargetProps"], prefix: typing.Optional[str]=None, route_name: typing.Optional[str]=None, route_type: typing.Optional["RouteType"]=None) -> "Route":
        """Add a single route to the router.

        :param id: -
        :param props: -
        :param route_targets: Array of weighted route targets.
        :param prefix: The path prefix to match for the route. Default: "/" if http otherwise none
        :param route_name: The name of the route. Default: - An automatically generated name
        :param route_type: Weather the route is HTTP based. Default: - HTTP if ``prefix`` is given, TCP otherwise

        stability
        :stability: experimental
        """
        props = RouteBaseProps(route_targets=route_targets, prefix=prefix, route_name=route_name, route_type=route_type)

        return jsii.invoke(self, "addRoute", [id, props])


@jsii.interface(jsii_type="@aws-cdk/aws-appmesh.IVirtualService")
class IVirtualService(aws_cdk.core.IResource, jsii.compat.Protocol):
    """Represents the interface which all VirtualService based classes MUST implement.

    stability
    :stability: experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IVirtualServiceProxy

    @property
    @jsii.member(jsii_name="virtualServiceArn")
    def virtual_service_arn(self) -> str:
        """The Amazon Resource Name (ARN) for the virtual service.

        stability
        :stability: experimental
        attribute:
        :attribute:: true
        """
        ...

    @property
    @jsii.member(jsii_name="virtualServiceName")
    def virtual_service_name(self) -> str:
        """The name of the VirtualService.

        stability
        :stability: experimental
        attribute:
        :attribute:: true
        """
        ...


class _IVirtualServiceProxy(jsii.proxy_for(aws_cdk.core.IResource)):
    """Represents the interface which all VirtualService based classes MUST implement.

    stability
    :stability: experimental
    """
    __jsii_type__ = "@aws-cdk/aws-appmesh.IVirtualService"
    @property
    @jsii.member(jsii_name="virtualServiceArn")
    def virtual_service_arn(self) -> str:
        """The Amazon Resource Name (ARN) for the virtual service.

        stability
        :stability: experimental
        attribute:
        :attribute:: true
        """
        return jsii.get(self, "virtualServiceArn")

    @property
    @jsii.member(jsii_name="virtualServiceName")
    def virtual_service_name(self) -> str:
        """The name of the VirtualService.

        stability
        :stability: experimental
        attribute:
        :attribute:: true
        """
        return jsii.get(self, "virtualServiceName")


@jsii.data_type(jsii_type="@aws-cdk/aws-appmesh.Listener", jsii_struct_bases=[], name_mapping={'port_mapping': 'portMapping'})
class Listener():
    def __init__(self, *, port_mapping: "PortMapping"):
        """A single listener for.

        :param port_mapping: Listener port for the virtual router.

        stability
        :stability: experimental
        """
        self._values = {
            'port_mapping': port_mapping,
        }

    @property
    def port_mapping(self) -> "PortMapping":
        """Listener port for the virtual router.

        stability
        :stability: experimental
        """
        return self._values.get('port_mapping')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'Listener(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


@jsii.implements(IMesh)
class Mesh(aws_cdk.core.Resource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-appmesh.Mesh"):
    """Define a new AppMesh mesh.

    see
    :see: https://docs.aws.amazon.com/app-mesh/latest/userguide/meshes.html
    stability
    :stability: experimental
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, egress_filter: typing.Optional["MeshFilterType"]=None, mesh_name: typing.Optional[str]=None) -> None:
        """
        :param scope: -
        :param id: -
        :param props: -
        :param egress_filter: Egress filter to be applied to the Mesh. Default: DROP_ALL
        :param mesh_name: The name of the Mesh being defined. Default: - A name is autmoatically generated

        stability
        :stability: experimental
        """
        props = MeshProps(egress_filter=egress_filter, mesh_name=mesh_name)

        jsii.create(Mesh, self, [scope, id, props])

    @jsii.member(jsii_name="fromMeshArn")
    @classmethod
    def from_mesh_arn(cls, scope: aws_cdk.core.Construct, id: str, mesh_arn: str) -> "IMesh":
        """Import an existing mesh by arn.

        :param scope: -
        :param id: -
        :param mesh_arn: -

        stability
        :stability: experimental
        """
        return jsii.sinvoke(cls, "fromMeshArn", [scope, id, mesh_arn])

    @jsii.member(jsii_name="fromMeshName")
    @classmethod
    def from_mesh_name(cls, scope: aws_cdk.core.Construct, id: str, mesh_name: str) -> "IMesh":
        """Import an existing mesh by name.

        :param scope: -
        :param id: -
        :param mesh_name: -

        stability
        :stability: experimental
        """
        return jsii.sinvoke(cls, "fromMeshName", [scope, id, mesh_name])

    @jsii.member(jsii_name="addVirtualNode")
    def add_virtual_node(self, id: str, *, backends: typing.Optional[typing.List["IVirtualService"]]=None, cloud_map_service: typing.Optional[aws_cdk.aws_servicediscovery.IService]=None, cloud_map_service_instance_attributes: typing.Optional[typing.Mapping[str,str]]=None, dns_host_name: typing.Optional[str]=None, listener: typing.Optional["VirtualNodeListener"]=None, virtual_node_name: typing.Optional[str]=None) -> "VirtualNode":
        """Adds a VirtualNode to the Mesh.

        :param id: -
        :param props: -
        :param backends: Virtual Services that this is node expected to send outbound traffic to. Default: - No backends
        :param cloud_map_service: CloudMap service where Virtual Node members register themselves. Instances registering themselves into this CloudMap will be considered part of the Virtual Node. Default: - Don't use CloudMap-based service discovery
        :param cloud_map_service_instance_attributes: Filter down the list of CloudMap service instance. Default: - No CloudMap instance filter
        :param dns_host_name: Host name of DNS record used to discover Virtual Node members. The IP addresses returned by querying this DNS record will be considered part of the Virtual Node. Default: - Don't use DNS-based service discovery
        :param listener: Initial listener for the virtual node. Default: - No listeners
        :param virtual_node_name: The name of the VirtualNode. Default: - A name is automatically determined

        stability
        :stability: experimental
        """
        props = VirtualNodeBaseProps(backends=backends, cloud_map_service=cloud_map_service, cloud_map_service_instance_attributes=cloud_map_service_instance_attributes, dns_host_name=dns_host_name, listener=listener, virtual_node_name=virtual_node_name)

        return jsii.invoke(self, "addVirtualNode", [id, props])

    @jsii.member(jsii_name="addVirtualRouter")
    def add_virtual_router(self, id: str, *, listener: typing.Optional["Listener"]=None, virtual_router_name: typing.Optional[str]=None) -> "VirtualRouter":
        """Adds a VirtualRouter to the Mesh with the given id and props.

        :param id: -
        :param props: -
        :param listener: Listener specification for the virtual router. Default: - A listener on HTTP port 8080
        :param virtual_router_name: The name of the VirtualRouter. Default: - A name is automatically determined

        stability
        :stability: experimental
        """
        props = VirtualRouterBaseProps(listener=listener, virtual_router_name=virtual_router_name)

        return jsii.invoke(self, "addVirtualRouter", [id, props])

    @jsii.member(jsii_name="addVirtualService")
    def add_virtual_service(self, id: str, *, virtual_node: typing.Optional["IVirtualNode"]=None, virtual_router: typing.Optional["IVirtualRouter"]=None, virtual_service_name: typing.Optional[str]=None) -> "VirtualService":
        """Adds a VirtualService with the given id.

        :param id: -
        :param props: -
        :param virtual_node: The VirtualNode attached to the virtual service. Default: - At most one of virtualRouter and virtualNode is allowed.
        :param virtual_router: The VirtualRouter which the VirtualService uses as provider. Default: - At most one of virtualRouter and virtualNode is allowed.
        :param virtual_service_name: The name of the VirtualService. It is recommended this follows the fully-qualified domain name format, such as "my-service.default.svc.cluster.local". Default: - A name is automatically generated

        stability
        :stability: experimental
        """
        props = VirtualServiceBaseProps(virtual_node=virtual_node, virtual_router=virtual_router, virtual_service_name=virtual_service_name)

        return jsii.invoke(self, "addVirtualService", [id, props])

    @property
    @jsii.member(jsii_name="meshArn")
    def mesh_arn(self) -> str:
        """The Amazon Resource Name (ARN) of the AppMesh mesh.

        stability
        :stability: experimental
        """
        return jsii.get(self, "meshArn")

    @property
    @jsii.member(jsii_name="meshName")
    def mesh_name(self) -> str:
        """The name of the AppMesh mesh.

        stability
        :stability: experimental
        """
        return jsii.get(self, "meshName")


@jsii.enum(jsii_type="@aws-cdk/aws-appmesh.MeshFilterType")
class MeshFilterType(enum.Enum):
    """A utility enum defined for the egressFilter type property, the default of DROP_ALL, allows traffic only to other resources inside the mesh, or API calls to amazon resources.

    default
    :default: DROP_ALL

    stability
    :stability: experimental
    """
    ALLOW_ALL = "ALLOW_ALL"
    """Allows all outbound traffic.

    stability
    :stability: experimental
    """
    DROP_ALL = "DROP_ALL"
    """Allows traffic only to other resources inside the mesh, or API calls to amazon resources.

    stability
    :stability: experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-appmesh.MeshProps", jsii_struct_bases=[], name_mapping={'egress_filter': 'egressFilter', 'mesh_name': 'meshName'})
class MeshProps():
    def __init__(self, *, egress_filter: typing.Optional["MeshFilterType"]=None, mesh_name: typing.Optional[str]=None):
        """The set of properties used when creating a Mesh.

        :param egress_filter: Egress filter to be applied to the Mesh. Default: DROP_ALL
        :param mesh_name: The name of the Mesh being defined. Default: - A name is autmoatically generated

        stability
        :stability: experimental
        """
        self._values = {
        }
        if egress_filter is not None: self._values["egress_filter"] = egress_filter
        if mesh_name is not None: self._values["mesh_name"] = mesh_name

    @property
    def egress_filter(self) -> typing.Optional["MeshFilterType"]:
        """Egress filter to be applied to the Mesh.

        default
        :default: DROP_ALL

        stability
        :stability: experimental
        """
        return self._values.get('egress_filter')

    @property
    def mesh_name(self) -> typing.Optional[str]:
        """The name of the Mesh being defined.

        default
        :default: - A name is autmoatically generated

        stability
        :stability: experimental
        """
        return self._values.get('mesh_name')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'MeshProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


@jsii.data_type(jsii_type="@aws-cdk/aws-appmesh.PortMapping", jsii_struct_bases=[], name_mapping={'port': 'port', 'protocol': 'protocol'})
class PortMapping():
    def __init__(self, *, port: jsii.Number, protocol: "Protocol"):
        """Port mappings for resources that require these attributes, such as VirtualNodes and Routes.

        :param port: Port mapped to the VirtualNode / Route. Default: 8080
        :param protocol: Protocol for the VirtualNode / Route, only TCP or HTTP supported. Default: HTTP

        stability
        :stability: experimental
        """
        self._values = {
            'port': port,
            'protocol': protocol,
        }

    @property
    def port(self) -> jsii.Number:
        """Port mapped to the VirtualNode / Route.

        default
        :default: 8080

        stability
        :stability: experimental
        """
        return self._values.get('port')

    @property
    def protocol(self) -> "Protocol":
        """Protocol for the VirtualNode / Route, only TCP or HTTP supported.

        default
        :default: HTTP

        stability
        :stability: experimental
        """
        return self._values.get('protocol')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'PortMapping(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


@jsii.enum(jsii_type="@aws-cdk/aws-appmesh.Protocol")
class Protocol(enum.Enum):
    """Enum of supported AppMesh protocols.

    stability
    :stability: experimental
    """
    HTTP = "HTTP"
    """
    stability
    :stability: experimental
    """
    TCP = "TCP"
    """
    stability
    :stability: experimental
    """

@jsii.implements(IRoute)
class Route(aws_cdk.core.Resource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-appmesh.Route"):
    """Route represents a new or existing route attached to a VirtualRouter and Mesh.

    see
    :see: https://docs.aws.amazon.com/app-mesh/latest/userguide/routes.html
    stability
    :stability: experimental
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, mesh: "IMesh", virtual_router: "IVirtualRouter", route_targets: typing.List["WeightedTargetProps"], prefix: typing.Optional[str]=None, route_name: typing.Optional[str]=None, route_type: typing.Optional["RouteType"]=None) -> None:
        """
        :param scope: -
        :param id: -
        :param props: -
        :param mesh: The service mesh to define the route in.
        :param virtual_router: The virtual router in which to define the route.
        :param route_targets: Array of weighted route targets.
        :param prefix: The path prefix to match for the route. Default: "/" if http otherwise none
        :param route_name: The name of the route. Default: - An automatically generated name
        :param route_type: Weather the route is HTTP based. Default: - HTTP if ``prefix`` is given, TCP otherwise

        stability
        :stability: experimental
        """
        props = RouteProps(mesh=mesh, virtual_router=virtual_router, route_targets=route_targets, prefix=prefix, route_name=route_name, route_type=route_type)

        jsii.create(Route, self, [scope, id, props])

    @jsii.member(jsii_name="fromRouteArn")
    @classmethod
    def from_route_arn(cls, scope: aws_cdk.core.Construct, id: str, route_arn: str) -> "IRoute":
        """Import an existing route given an ARN.

        :param scope: -
        :param id: -
        :param route_arn: -

        stability
        :stability: experimental
        """
        return jsii.sinvoke(cls, "fromRouteArn", [scope, id, route_arn])

    @jsii.member(jsii_name="fromRouteName")
    @classmethod
    def from_route_name(cls, scope: aws_cdk.core.Construct, id: str, mesh_name: str, virtual_router_name: str, route_name: str) -> "IRoute":
        """Import an existing route given its name.

        :param scope: -
        :param id: -
        :param mesh_name: -
        :param virtual_router_name: -
        :param route_name: -

        stability
        :stability: experimental
        """
        return jsii.sinvoke(cls, "fromRouteName", [scope, id, mesh_name, virtual_router_name, route_name])

    @property
    @jsii.member(jsii_name="routeArn")
    def route_arn(self) -> str:
        """The Amazon Resource Name (ARN) for the route.

        stability
        :stability: experimental
        """
        return jsii.get(self, "routeArn")

    @property
    @jsii.member(jsii_name="routeName")
    def route_name(self) -> str:
        """The name of the route.

        stability
        :stability: experimental
        """
        return jsii.get(self, "routeName")

    @property
    @jsii.member(jsii_name="virtualRouter")
    def virtual_router(self) -> "IVirtualRouter":
        """The virtual router this route is a part of.

        stability
        :stability: experimental
        """
        return jsii.get(self, "virtualRouter")


@jsii.data_type(jsii_type="@aws-cdk/aws-appmesh.RouteBaseProps", jsii_struct_bases=[], name_mapping={'route_targets': 'routeTargets', 'prefix': 'prefix', 'route_name': 'routeName', 'route_type': 'routeType'})
class RouteBaseProps():
    def __init__(self, *, route_targets: typing.List["WeightedTargetProps"], prefix: typing.Optional[str]=None, route_name: typing.Optional[str]=None, route_type: typing.Optional["RouteType"]=None):
        """Base interface properties for all Routes.

        :param route_targets: Array of weighted route targets.
        :param prefix: The path prefix to match for the route. Default: "/" if http otherwise none
        :param route_name: The name of the route. Default: - An automatically generated name
        :param route_type: Weather the route is HTTP based. Default: - HTTP if ``prefix`` is given, TCP otherwise

        stability
        :stability: experimental
        """
        self._values = {
            'route_targets': route_targets,
        }
        if prefix is not None: self._values["prefix"] = prefix
        if route_name is not None: self._values["route_name"] = route_name
        if route_type is not None: self._values["route_type"] = route_type

    @property
    def route_targets(self) -> typing.List["WeightedTargetProps"]:
        """Array of weighted route targets.

        stability
        :stability: experimental
        requires:
        :requires:: minimum of 1
        """
        return self._values.get('route_targets')

    @property
    def prefix(self) -> typing.Optional[str]:
        """The path prefix to match for the route.

        default
        :default: "/" if http otherwise none

        stability
        :stability: experimental
        """
        return self._values.get('prefix')

    @property
    def route_name(self) -> typing.Optional[str]:
        """The name of the route.

        default
        :default: - An automatically generated name

        stability
        :stability: experimental
        """
        return self._values.get('route_name')

    @property
    def route_type(self) -> typing.Optional["RouteType"]:
        """Weather the route is HTTP based.

        default
        :default: - HTTP if ``prefix`` is given, TCP otherwise

        stability
        :stability: experimental
        """
        return self._values.get('route_type')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'RouteBaseProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


@jsii.data_type(jsii_type="@aws-cdk/aws-appmesh.RouteProps", jsii_struct_bases=[RouteBaseProps], name_mapping={'route_targets': 'routeTargets', 'prefix': 'prefix', 'route_name': 'routeName', 'route_type': 'routeType', 'mesh': 'mesh', 'virtual_router': 'virtualRouter'})
class RouteProps(RouteBaseProps):
    def __init__(self, *, route_targets: typing.List["WeightedTargetProps"], prefix: typing.Optional[str]=None, route_name: typing.Optional[str]=None, route_type: typing.Optional["RouteType"]=None, mesh: "IMesh", virtual_router: "IVirtualRouter"):
        """Properties to define new Routes.

        :param route_targets: Array of weighted route targets.
        :param prefix: The path prefix to match for the route. Default: "/" if http otherwise none
        :param route_name: The name of the route. Default: - An automatically generated name
        :param route_type: Weather the route is HTTP based. Default: - HTTP if ``prefix`` is given, TCP otherwise
        :param mesh: The service mesh to define the route in.
        :param virtual_router: The virtual router in which to define the route.

        stability
        :stability: experimental
        """
        self._values = {
            'route_targets': route_targets,
            'mesh': mesh,
            'virtual_router': virtual_router,
        }
        if prefix is not None: self._values["prefix"] = prefix
        if route_name is not None: self._values["route_name"] = route_name
        if route_type is not None: self._values["route_type"] = route_type

    @property
    def route_targets(self) -> typing.List["WeightedTargetProps"]:
        """Array of weighted route targets.

        stability
        :stability: experimental
        requires:
        :requires:: minimum of 1
        """
        return self._values.get('route_targets')

    @property
    def prefix(self) -> typing.Optional[str]:
        """The path prefix to match for the route.

        default
        :default: "/" if http otherwise none

        stability
        :stability: experimental
        """
        return self._values.get('prefix')

    @property
    def route_name(self) -> typing.Optional[str]:
        """The name of the route.

        default
        :default: - An automatically generated name

        stability
        :stability: experimental
        """
        return self._values.get('route_name')

    @property
    def route_type(self) -> typing.Optional["RouteType"]:
        """Weather the route is HTTP based.

        default
        :default: - HTTP if ``prefix`` is given, TCP otherwise

        stability
        :stability: experimental
        """
        return self._values.get('route_type')

    @property
    def mesh(self) -> "IMesh":
        """The service mesh to define the route in.

        stability
        :stability: experimental
        """
        return self._values.get('mesh')

    @property
    def virtual_router(self) -> "IVirtualRouter":
        """The virtual router in which to define the route.

        stability
        :stability: experimental
        """
        return self._values.get('virtual_router')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'RouteProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


@jsii.enum(jsii_type="@aws-cdk/aws-appmesh.RouteType")
class RouteType(enum.Enum):
    """Type of route.

    stability
    :stability: experimental
    """
    HTTP = "HTTP"
    """HTTP route.

    stability
    :stability: experimental
    """
    TCP = "TCP"
    """TCP route.

    stability
    :stability: experimental
    """

@jsii.implements(IVirtualNode)
class VirtualNode(aws_cdk.core.Resource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-appmesh.VirtualNode"):
    """VirtualNode represents a newly defined AppMesh VirtualNode.

    Any inbound traffic that your virtual node expects should be specified as a
    listener. Any outbound traffic that your virtual node expects to reach
    should be specified as a backend.

    see
    :see: https://docs.aws.amazon.com/app-mesh/latest/userguide/virtual_nodes.html
    stability
    :stability: experimental
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, mesh: "IMesh", backends: typing.Optional[typing.List["IVirtualService"]]=None, cloud_map_service: typing.Optional[aws_cdk.aws_servicediscovery.IService]=None, cloud_map_service_instance_attributes: typing.Optional[typing.Mapping[str,str]]=None, dns_host_name: typing.Optional[str]=None, listener: typing.Optional["VirtualNodeListener"]=None, virtual_node_name: typing.Optional[str]=None) -> None:
        """
        :param scope: -
        :param id: -
        :param props: -
        :param mesh: The name of the AppMesh which the virtual node belongs to.
        :param backends: Virtual Services that this is node expected to send outbound traffic to. Default: - No backends
        :param cloud_map_service: CloudMap service where Virtual Node members register themselves. Instances registering themselves into this CloudMap will be considered part of the Virtual Node. Default: - Don't use CloudMap-based service discovery
        :param cloud_map_service_instance_attributes: Filter down the list of CloudMap service instance. Default: - No CloudMap instance filter
        :param dns_host_name: Host name of DNS record used to discover Virtual Node members. The IP addresses returned by querying this DNS record will be considered part of the Virtual Node. Default: - Don't use DNS-based service discovery
        :param listener: Initial listener for the virtual node. Default: - No listeners
        :param virtual_node_name: The name of the VirtualNode. Default: - A name is automatically determined

        stability
        :stability: experimental
        """
        props = VirtualNodeProps(mesh=mesh, backends=backends, cloud_map_service=cloud_map_service, cloud_map_service_instance_attributes=cloud_map_service_instance_attributes, dns_host_name=dns_host_name, listener=listener, virtual_node_name=virtual_node_name)

        jsii.create(VirtualNode, self, [scope, id, props])

    @jsii.member(jsii_name="fromVirtualNodeArn")
    @classmethod
    def from_virtual_node_arn(cls, scope: aws_cdk.core.Construct, id: str, virtual_node_arn: str) -> "IVirtualNode":
        """Import an existing VirtualNode given an ARN.

        :param scope: -
        :param id: -
        :param virtual_node_arn: -

        stability
        :stability: experimental
        """
        return jsii.sinvoke(cls, "fromVirtualNodeArn", [scope, id, virtual_node_arn])

    @jsii.member(jsii_name="fromVirtualNodeName")
    @classmethod
    def from_virtual_node_name(cls, scope: aws_cdk.core.Construct, id: str, mesh_name: str, virtual_node_name: str) -> "IVirtualNode":
        """Import an existing VirtualNode given its name.

        :param scope: -
        :param id: -
        :param mesh_name: -
        :param virtual_node_name: -

        stability
        :stability: experimental
        """
        return jsii.sinvoke(cls, "fromVirtualNodeName", [scope, id, mesh_name, virtual_node_name])

    @jsii.member(jsii_name="addBackends")
    def add_backends(self, *props: "IVirtualService") -> None:
        """Add a Virtual Services that this node is expected to send outbound traffic to.

        :param props: -

        stability
        :stability: experimental
        """
        return jsii.invoke(self, "addBackends", [*props])

    @jsii.member(jsii_name="addListeners")
    def add_listeners(self, *listeners: "VirtualNodeListener") -> None:
        """Utility method to add an inbound listener for this virtual node.

        :param listeners: -

        stability
        :stability: experimental
        """
        return jsii.invoke(self, "addListeners", [*listeners])

    @property
    @jsii.member(jsii_name="backends")
    def _backends(self) -> typing.List["CfnVirtualNode.BackendProperty"]:
        """
        stability
        :stability: experimental
        """
        return jsii.get(self, "backends")

    @property
    @jsii.member(jsii_name="listeners")
    def _listeners(self) -> typing.List["CfnVirtualNode.ListenerProperty"]:
        """
        stability
        :stability: experimental
        """
        return jsii.get(self, "listeners")

    @property
    @jsii.member(jsii_name="mesh")
    def mesh(self) -> "IMesh":
        """The service mesh that the virtual node resides in.

        stability
        :stability: experimental
        """
        return jsii.get(self, "mesh")

    @property
    @jsii.member(jsii_name="virtualNodeArn")
    def virtual_node_arn(self) -> str:
        """The Amazon Resource Name belonging to the VirtualNdoe.

        stability
        :stability: experimental
        """
        return jsii.get(self, "virtualNodeArn")

    @property
    @jsii.member(jsii_name="virtualNodeName")
    def virtual_node_name(self) -> str:
        """The name of the VirtualNode.

        stability
        :stability: experimental
        """
        return jsii.get(self, "virtualNodeName")


@jsii.data_type(jsii_type="@aws-cdk/aws-appmesh.VirtualNodeBaseProps", jsii_struct_bases=[], name_mapping={'backends': 'backends', 'cloud_map_service': 'cloudMapService', 'cloud_map_service_instance_attributes': 'cloudMapServiceInstanceAttributes', 'dns_host_name': 'dnsHostName', 'listener': 'listener', 'virtual_node_name': 'virtualNodeName'})
class VirtualNodeBaseProps():
    def __init__(self, *, backends: typing.Optional[typing.List["IVirtualService"]]=None, cloud_map_service: typing.Optional[aws_cdk.aws_servicediscovery.IService]=None, cloud_map_service_instance_attributes: typing.Optional[typing.Mapping[str,str]]=None, dns_host_name: typing.Optional[str]=None, listener: typing.Optional["VirtualNodeListener"]=None, virtual_node_name: typing.Optional[str]=None):
        """Basic configuration properties for a VirtualNode.

        :param backends: Virtual Services that this is node expected to send outbound traffic to. Default: - No backends
        :param cloud_map_service: CloudMap service where Virtual Node members register themselves. Instances registering themselves into this CloudMap will be considered part of the Virtual Node. Default: - Don't use CloudMap-based service discovery
        :param cloud_map_service_instance_attributes: Filter down the list of CloudMap service instance. Default: - No CloudMap instance filter
        :param dns_host_name: Host name of DNS record used to discover Virtual Node members. The IP addresses returned by querying this DNS record will be considered part of the Virtual Node. Default: - Don't use DNS-based service discovery
        :param listener: Initial listener for the virtual node. Default: - No listeners
        :param virtual_node_name: The name of the VirtualNode. Default: - A name is automatically determined

        stability
        :stability: experimental
        """
        self._values = {
        }
        if backends is not None: self._values["backends"] = backends
        if cloud_map_service is not None: self._values["cloud_map_service"] = cloud_map_service
        if cloud_map_service_instance_attributes is not None: self._values["cloud_map_service_instance_attributes"] = cloud_map_service_instance_attributes
        if dns_host_name is not None: self._values["dns_host_name"] = dns_host_name
        if listener is not None: self._values["listener"] = listener
        if virtual_node_name is not None: self._values["virtual_node_name"] = virtual_node_name

    @property
    def backends(self) -> typing.Optional[typing.List["IVirtualService"]]:
        """Virtual Services that this is node expected to send outbound traffic to.

        default
        :default: - No backends

        stability
        :stability: experimental
        """
        return self._values.get('backends')

    @property
    def cloud_map_service(self) -> typing.Optional[aws_cdk.aws_servicediscovery.IService]:
        """CloudMap service where Virtual Node members register themselves.

        Instances registering themselves into this CloudMap will
        be considered part of the Virtual Node.

        default
        :default: - Don't use CloudMap-based service discovery

        stability
        :stability: experimental
        """
        return self._values.get('cloud_map_service')

    @property
    def cloud_map_service_instance_attributes(self) -> typing.Optional[typing.Mapping[str,str]]:
        """Filter down the list of CloudMap service instance.

        default
        :default: - No CloudMap instance filter

        stability
        :stability: experimental
        """
        return self._values.get('cloud_map_service_instance_attributes')

    @property
    def dns_host_name(self) -> typing.Optional[str]:
        """Host name of DNS record used to discover Virtual Node members.

        The IP addresses returned by querying this DNS record will be considered
        part of the Virtual Node.

        default
        :default: - Don't use DNS-based service discovery

        stability
        :stability: experimental
        """
        return self._values.get('dns_host_name')

    @property
    def listener(self) -> typing.Optional["VirtualNodeListener"]:
        """Initial listener for the virtual node.

        default
        :default: - No listeners

        stability
        :stability: experimental
        """
        return self._values.get('listener')

    @property
    def virtual_node_name(self) -> typing.Optional[str]:
        """The name of the VirtualNode.

        default
        :default: - A name is automatically determined

        stability
        :stability: experimental
        """
        return self._values.get('virtual_node_name')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'VirtualNodeBaseProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


@jsii.data_type(jsii_type="@aws-cdk/aws-appmesh.VirtualNodeListener", jsii_struct_bases=[], name_mapping={'health_check': 'healthCheck', 'port_mapping': 'portMapping'})
class VirtualNodeListener():
    def __init__(self, *, health_check: typing.Optional["HealthCheck"]=None, port_mapping: typing.Optional["PortMapping"]=None):
        """Represents the properties needed to define healthy and active listeners for nodes.

        :param health_check: Array fo HealthCheckProps for the node(s). Default: - no healthcheck
        :param port_mapping: Array of PortMappingProps for the listener. Default: - HTTP port 8080

        stability
        :stability: experimental
        """
        self._values = {
        }
        if health_check is not None: self._values["health_check"] = health_check
        if port_mapping is not None: self._values["port_mapping"] = port_mapping

    @property
    def health_check(self) -> typing.Optional["HealthCheck"]:
        """Array fo HealthCheckProps for the node(s).

        default
        :default: - no healthcheck

        stability
        :stability: experimental
        """
        return self._values.get('health_check')

    @property
    def port_mapping(self) -> typing.Optional["PortMapping"]:
        """Array of PortMappingProps for the listener.

        default
        :default: - HTTP port 8080

        stability
        :stability: experimental
        """
        return self._values.get('port_mapping')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'VirtualNodeListener(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


@jsii.data_type(jsii_type="@aws-cdk/aws-appmesh.VirtualNodeProps", jsii_struct_bases=[VirtualNodeBaseProps], name_mapping={'backends': 'backends', 'cloud_map_service': 'cloudMapService', 'cloud_map_service_instance_attributes': 'cloudMapServiceInstanceAttributes', 'dns_host_name': 'dnsHostName', 'listener': 'listener', 'virtual_node_name': 'virtualNodeName', 'mesh': 'mesh'})
class VirtualNodeProps(VirtualNodeBaseProps):
    def __init__(self, *, backends: typing.Optional[typing.List["IVirtualService"]]=None, cloud_map_service: typing.Optional[aws_cdk.aws_servicediscovery.IService]=None, cloud_map_service_instance_attributes: typing.Optional[typing.Mapping[str,str]]=None, dns_host_name: typing.Optional[str]=None, listener: typing.Optional["VirtualNodeListener"]=None, virtual_node_name: typing.Optional[str]=None, mesh: "IMesh"):
        """The properties used when creating a new VirtualNode.

        :param backends: Virtual Services that this is node expected to send outbound traffic to. Default: - No backends
        :param cloud_map_service: CloudMap service where Virtual Node members register themselves. Instances registering themselves into this CloudMap will be considered part of the Virtual Node. Default: - Don't use CloudMap-based service discovery
        :param cloud_map_service_instance_attributes: Filter down the list of CloudMap service instance. Default: - No CloudMap instance filter
        :param dns_host_name: Host name of DNS record used to discover Virtual Node members. The IP addresses returned by querying this DNS record will be considered part of the Virtual Node. Default: - Don't use DNS-based service discovery
        :param listener: Initial listener for the virtual node. Default: - No listeners
        :param virtual_node_name: The name of the VirtualNode. Default: - A name is automatically determined
        :param mesh: The name of the AppMesh which the virtual node belongs to.

        stability
        :stability: experimental
        """
        self._values = {
            'mesh': mesh,
        }
        if backends is not None: self._values["backends"] = backends
        if cloud_map_service is not None: self._values["cloud_map_service"] = cloud_map_service
        if cloud_map_service_instance_attributes is not None: self._values["cloud_map_service_instance_attributes"] = cloud_map_service_instance_attributes
        if dns_host_name is not None: self._values["dns_host_name"] = dns_host_name
        if listener is not None: self._values["listener"] = listener
        if virtual_node_name is not None: self._values["virtual_node_name"] = virtual_node_name

    @property
    def backends(self) -> typing.Optional[typing.List["IVirtualService"]]:
        """Virtual Services that this is node expected to send outbound traffic to.

        default
        :default: - No backends

        stability
        :stability: experimental
        """
        return self._values.get('backends')

    @property
    def cloud_map_service(self) -> typing.Optional[aws_cdk.aws_servicediscovery.IService]:
        """CloudMap service where Virtual Node members register themselves.

        Instances registering themselves into this CloudMap will
        be considered part of the Virtual Node.

        default
        :default: - Don't use CloudMap-based service discovery

        stability
        :stability: experimental
        """
        return self._values.get('cloud_map_service')

    @property
    def cloud_map_service_instance_attributes(self) -> typing.Optional[typing.Mapping[str,str]]:
        """Filter down the list of CloudMap service instance.

        default
        :default: - No CloudMap instance filter

        stability
        :stability: experimental
        """
        return self._values.get('cloud_map_service_instance_attributes')

    @property
    def dns_host_name(self) -> typing.Optional[str]:
        """Host name of DNS record used to discover Virtual Node members.

        The IP addresses returned by querying this DNS record will be considered
        part of the Virtual Node.

        default
        :default: - Don't use DNS-based service discovery

        stability
        :stability: experimental
        """
        return self._values.get('dns_host_name')

    @property
    def listener(self) -> typing.Optional["VirtualNodeListener"]:
        """Initial listener for the virtual node.

        default
        :default: - No listeners

        stability
        :stability: experimental
        """
        return self._values.get('listener')

    @property
    def virtual_node_name(self) -> typing.Optional[str]:
        """The name of the VirtualNode.

        default
        :default: - A name is automatically determined

        stability
        :stability: experimental
        """
        return self._values.get('virtual_node_name')

    @property
    def mesh(self) -> "IMesh":
        """The name of the AppMesh which the virtual node belongs to.

        stability
        :stability: experimental
        """
        return self._values.get('mesh')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'VirtualNodeProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


@jsii.implements(IVirtualRouter)
class VirtualRouter(aws_cdk.core.Resource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-appmesh.VirtualRouter"):
    """
    stability
    :stability: experimental
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, mesh: "IMesh", listener: typing.Optional["Listener"]=None, virtual_router_name: typing.Optional[str]=None) -> None:
        """
        :param scope: -
        :param id: -
        :param props: -
        :param mesh: The AppMesh mesh the VirtualRouter belongs to.
        :param listener: Listener specification for the virtual router. Default: - A listener on HTTP port 8080
        :param virtual_router_name: The name of the VirtualRouter. Default: - A name is automatically determined

        stability
        :stability: experimental
        """
        props = VirtualRouterProps(mesh=mesh, listener=listener, virtual_router_name=virtual_router_name)

        jsii.create(VirtualRouter, self, [scope, id, props])

    @jsii.member(jsii_name="fromVirtualRouterArn")
    @classmethod
    def from_virtual_router_arn(cls, scope: aws_cdk.core.Construct, id: str, virtual_router_arn: str) -> "IVirtualRouter":
        """Import an existing VirtualRouter given an ARN.

        :param scope: -
        :param id: -
        :param virtual_router_arn: -

        stability
        :stability: experimental
        """
        return jsii.sinvoke(cls, "fromVirtualRouterArn", [scope, id, virtual_router_arn])

    @jsii.member(jsii_name="fromVirtualRouterAttributes")
    @classmethod
    def from_virtual_router_attributes(cls, scope: aws_cdk.core.Construct, id: str, *, mesh: typing.Optional["IMesh"]=None, mesh_name: typing.Optional[str]=None, virtual_router_arn: typing.Optional[str]=None, virtual_router_name: typing.Optional[str]=None) -> "IVirtualRouter":
        """Import an existing virtual router given attributes.

        :param scope: -
        :param id: -
        :param attrs: -
        :param mesh: The AppMesh mesh the VirtualRouter belongs to.
        :param mesh_name: The name of the AppMesh mesh the VirtualRouter belongs to.
        :param virtual_router_arn: The Amazon Resource Name (ARN) for the VirtualRouter.
        :param virtual_router_name: The name of the VirtualRouter.

        stability
        :stability: experimental
        """
        attrs = VirtualRouterAttributes(mesh=mesh, mesh_name=mesh_name, virtual_router_arn=virtual_router_arn, virtual_router_name=virtual_router_name)

        return jsii.sinvoke(cls, "fromVirtualRouterAttributes", [scope, id, attrs])

    @jsii.member(jsii_name="fromVirtualRouterName")
    @classmethod
    def from_virtual_router_name(cls, scope: aws_cdk.core.Construct, id: str, mesh_name: str, virtual_router_name: str) -> "IVirtualRouter":
        """Import an existing VirtualRouter given names.

        :param scope: -
        :param id: -
        :param mesh_name: -
        :param virtual_router_name: -

        stability
        :stability: experimental
        """
        return jsii.sinvoke(cls, "fromVirtualRouterName", [scope, id, mesh_name, virtual_router_name])

    @jsii.member(jsii_name="addRoute")
    def add_route(self, id: str, *, route_targets: typing.List["WeightedTargetProps"], prefix: typing.Optional[str]=None, route_name: typing.Optional[str]=None, route_type: typing.Optional["RouteType"]=None) -> "Route":
        """Add a single route to the router.

        :param id: -
        :param props: -
        :param route_targets: Array of weighted route targets.
        :param prefix: The path prefix to match for the route. Default: "/" if http otherwise none
        :param route_name: The name of the route. Default: - An automatically generated name
        :param route_type: Weather the route is HTTP based. Default: - HTTP if ``prefix`` is given, TCP otherwise

        stability
        :stability: experimental
        """
        props = RouteBaseProps(route_targets=route_targets, prefix=prefix, route_name=route_name, route_type=route_type)

        return jsii.invoke(self, "addRoute", [id, props])

    @property
    @jsii.member(jsii_name="mesh")
    def mesh(self) -> "IMesh":
        """The AppMesh mesh the VirtualRouter belongs to.

        stability
        :stability: experimental
        """
        return jsii.get(self, "mesh")

    @property
    @jsii.member(jsii_name="virtualRouterArn")
    def virtual_router_arn(self) -> str:
        """The Amazon Resource Name (ARN) for the VirtualRouter.

        stability
        :stability: experimental
        """
        return jsii.get(self, "virtualRouterArn")

    @property
    @jsii.member(jsii_name="virtualRouterName")
    def virtual_router_name(self) -> str:
        """The name of the VirtualRouter.

        stability
        :stability: experimental
        """
        return jsii.get(self, "virtualRouterName")


@jsii.data_type(jsii_type="@aws-cdk/aws-appmesh.VirtualRouterAttributes", jsii_struct_bases=[], name_mapping={'mesh': 'mesh', 'mesh_name': 'meshName', 'virtual_router_arn': 'virtualRouterArn', 'virtual_router_name': 'virtualRouterName'})
class VirtualRouterAttributes():
    def __init__(self, *, mesh: typing.Optional["IMesh"]=None, mesh_name: typing.Optional[str]=None, virtual_router_arn: typing.Optional[str]=None, virtual_router_name: typing.Optional[str]=None):
        """Interface with properties ncecessary to import a reusable VirtualRouter.

        :param mesh: The AppMesh mesh the VirtualRouter belongs to.
        :param mesh_name: The name of the AppMesh mesh the VirtualRouter belongs to.
        :param virtual_router_arn: The Amazon Resource Name (ARN) for the VirtualRouter.
        :param virtual_router_name: The name of the VirtualRouter.

        stability
        :stability: experimental
        """
        self._values = {
        }
        if mesh is not None: self._values["mesh"] = mesh
        if mesh_name is not None: self._values["mesh_name"] = mesh_name
        if virtual_router_arn is not None: self._values["virtual_router_arn"] = virtual_router_arn
        if virtual_router_name is not None: self._values["virtual_router_name"] = virtual_router_name

    @property
    def mesh(self) -> typing.Optional["IMesh"]:
        """The AppMesh mesh the VirtualRouter belongs to.

        stability
        :stability: experimental
        """
        return self._values.get('mesh')

    @property
    def mesh_name(self) -> typing.Optional[str]:
        """The name of the AppMesh mesh the VirtualRouter belongs to.

        stability
        :stability: experimental
        """
        return self._values.get('mesh_name')

    @property
    def virtual_router_arn(self) -> typing.Optional[str]:
        """The Amazon Resource Name (ARN) for the VirtualRouter.

        stability
        :stability: experimental
        """
        return self._values.get('virtual_router_arn')

    @property
    def virtual_router_name(self) -> typing.Optional[str]:
        """The name of the VirtualRouter.

        stability
        :stability: experimental
        """
        return self._values.get('virtual_router_name')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'VirtualRouterAttributes(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


@jsii.data_type(jsii_type="@aws-cdk/aws-appmesh.VirtualRouterBaseProps", jsii_struct_bases=[], name_mapping={'listener': 'listener', 'virtual_router_name': 'virtualRouterName'})
class VirtualRouterBaseProps():
    def __init__(self, *, listener: typing.Optional["Listener"]=None, virtual_router_name: typing.Optional[str]=None):
        """Interface with base properties all routers willl inherit.

        :param listener: Listener specification for the virtual router. Default: - A listener on HTTP port 8080
        :param virtual_router_name: The name of the VirtualRouter. Default: - A name is automatically determined

        stability
        :stability: experimental
        """
        self._values = {
        }
        if listener is not None: self._values["listener"] = listener
        if virtual_router_name is not None: self._values["virtual_router_name"] = virtual_router_name

    @property
    def listener(self) -> typing.Optional["Listener"]:
        """Listener specification for the virtual router.

        default
        :default: - A listener on HTTP port 8080

        stability
        :stability: experimental
        """
        return self._values.get('listener')

    @property
    def virtual_router_name(self) -> typing.Optional[str]:
        """The name of the VirtualRouter.

        default
        :default: - A name is automatically determined

        stability
        :stability: experimental
        """
        return self._values.get('virtual_router_name')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'VirtualRouterBaseProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


@jsii.data_type(jsii_type="@aws-cdk/aws-appmesh.VirtualRouterProps", jsii_struct_bases=[VirtualRouterBaseProps], name_mapping={'listener': 'listener', 'virtual_router_name': 'virtualRouterName', 'mesh': 'mesh'})
class VirtualRouterProps(VirtualRouterBaseProps):
    def __init__(self, *, listener: typing.Optional["Listener"]=None, virtual_router_name: typing.Optional[str]=None, mesh: "IMesh"):
        """The properties used when creating a new VritualRouter.

        :param listener: Listener specification for the virtual router. Default: - A listener on HTTP port 8080
        :param virtual_router_name: The name of the VirtualRouter. Default: - A name is automatically determined
        :param mesh: The AppMesh mesh the VirtualRouter belongs to.

        stability
        :stability: experimental
        """
        self._values = {
            'mesh': mesh,
        }
        if listener is not None: self._values["listener"] = listener
        if virtual_router_name is not None: self._values["virtual_router_name"] = virtual_router_name

    @property
    def listener(self) -> typing.Optional["Listener"]:
        """Listener specification for the virtual router.

        default
        :default: - A listener on HTTP port 8080

        stability
        :stability: experimental
        """
        return self._values.get('listener')

    @property
    def virtual_router_name(self) -> typing.Optional[str]:
        """The name of the VirtualRouter.

        default
        :default: - A name is automatically determined

        stability
        :stability: experimental
        """
        return self._values.get('virtual_router_name')

    @property
    def mesh(self) -> "IMesh":
        """The AppMesh mesh the VirtualRouter belongs to.

        stability
        :stability: experimental
        """
        return self._values.get('mesh')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'VirtualRouterProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


@jsii.implements(IVirtualService)
class VirtualService(aws_cdk.core.Resource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-appmesh.VirtualService"):
    """VirtualService represents a service inside an AppMesh.

    It routes traffic either to a Virtual Node or to a Virtual Router.

    see
    :see: https://docs.aws.amazon.com/app-mesh/latest/userguide/virtual_services.html
    stability
    :stability: experimental
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, mesh: "IMesh", virtual_node: typing.Optional["IVirtualNode"]=None, virtual_router: typing.Optional["IVirtualRouter"]=None, virtual_service_name: typing.Optional[str]=None) -> None:
        """
        :param scope: -
        :param id: -
        :param props: -
        :param mesh: The AppMesh mesh name for which the VirtualService belongs to.
        :param virtual_node: The VirtualNode attached to the virtual service. Default: - At most one of virtualRouter and virtualNode is allowed.
        :param virtual_router: The VirtualRouter which the VirtualService uses as provider. Default: - At most one of virtualRouter and virtualNode is allowed.
        :param virtual_service_name: The name of the VirtualService. It is recommended this follows the fully-qualified domain name format, such as "my-service.default.svc.cluster.local". Default: - A name is automatically generated

        stability
        :stability: experimental
        """
        props = VirtualServiceProps(mesh=mesh, virtual_node=virtual_node, virtual_router=virtual_router, virtual_service_name=virtual_service_name)

        jsii.create(VirtualService, self, [scope, id, props])

    @jsii.member(jsii_name="fromVirtualServiceArn")
    @classmethod
    def from_virtual_service_arn(cls, scope: aws_cdk.core.Construct, id: str, virtual_service_arn: str) -> "IVirtualService":
        """Import an existing VirtualService given an ARN.

        :param scope: -
        :param id: -
        :param virtual_service_arn: -

        stability
        :stability: experimental
        """
        return jsii.sinvoke(cls, "fromVirtualServiceArn", [scope, id, virtual_service_arn])

    @jsii.member(jsii_name="fromVirtualServiceName")
    @classmethod
    def from_virtual_service_name(cls, scope: aws_cdk.core.Construct, id: str, mesh_name: str, virtual_service_name: str) -> "IVirtualService":
        """Import an existing VirtualService given mesh and service names.

        :param scope: -
        :param id: -
        :param mesh_name: -
        :param virtual_service_name: -

        stability
        :stability: experimental
        """
        return jsii.sinvoke(cls, "fromVirtualServiceName", [scope, id, mesh_name, virtual_service_name])

    @property
    @jsii.member(jsii_name="virtualServiceArn")
    def virtual_service_arn(self) -> str:
        """The Amazon Resource Name (ARN) for the virtual service.

        stability
        :stability: experimental
        """
        return jsii.get(self, "virtualServiceArn")

    @property
    @jsii.member(jsii_name="virtualServiceName")
    def virtual_service_name(self) -> str:
        """The name of the VirtualService, it is recommended this follows the fully-qualified domain name format.

        stability
        :stability: experimental
        """
        return jsii.get(self, "virtualServiceName")


@jsii.data_type(jsii_type="@aws-cdk/aws-appmesh.VirtualServiceBaseProps", jsii_struct_bases=[], name_mapping={'virtual_node': 'virtualNode', 'virtual_router': 'virtualRouter', 'virtual_service_name': 'virtualServiceName'})
class VirtualServiceBaseProps():
    def __init__(self, *, virtual_node: typing.Optional["IVirtualNode"]=None, virtual_router: typing.Optional["IVirtualRouter"]=None, virtual_service_name: typing.Optional[str]=None):
        """The base properties which all classes in VirtualService will inherit from.

        :param virtual_node: The VirtualNode attached to the virtual service. Default: - At most one of virtualRouter and virtualNode is allowed.
        :param virtual_router: The VirtualRouter which the VirtualService uses as provider. Default: - At most one of virtualRouter and virtualNode is allowed.
        :param virtual_service_name: The name of the VirtualService. It is recommended this follows the fully-qualified domain name format, such as "my-service.default.svc.cluster.local". Default: - A name is automatically generated

        stability
        :stability: experimental
        """
        self._values = {
        }
        if virtual_node is not None: self._values["virtual_node"] = virtual_node
        if virtual_router is not None: self._values["virtual_router"] = virtual_router
        if virtual_service_name is not None: self._values["virtual_service_name"] = virtual_service_name

    @property
    def virtual_node(self) -> typing.Optional["IVirtualNode"]:
        """The VirtualNode attached to the virtual service.

        default
        :default: - At most one of virtualRouter and virtualNode is allowed.

        stability
        :stability: experimental
        """
        return self._values.get('virtual_node')

    @property
    def virtual_router(self) -> typing.Optional["IVirtualRouter"]:
        """The VirtualRouter which the VirtualService uses as provider.

        default
        :default: - At most one of virtualRouter and virtualNode is allowed.

        stability
        :stability: experimental
        """
        return self._values.get('virtual_router')

    @property
    def virtual_service_name(self) -> typing.Optional[str]:
        """The name of the VirtualService.

        It is recommended this follows the fully-qualified domain name format,
        such as "my-service.default.svc.cluster.local".

        default
        :default: - A name is automatically generated

        stability
        :stability: experimental

        Example::
            # Example may have issues. See https://github.com/aws/jsii/issues/826
            service.domain.local
        """
        return self._values.get('virtual_service_name')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'VirtualServiceBaseProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


@jsii.data_type(jsii_type="@aws-cdk/aws-appmesh.VirtualServiceProps", jsii_struct_bases=[VirtualServiceBaseProps], name_mapping={'virtual_node': 'virtualNode', 'virtual_router': 'virtualRouter', 'virtual_service_name': 'virtualServiceName', 'mesh': 'mesh'})
class VirtualServiceProps(VirtualServiceBaseProps):
    def __init__(self, *, virtual_node: typing.Optional["IVirtualNode"]=None, virtual_router: typing.Optional["IVirtualRouter"]=None, virtual_service_name: typing.Optional[str]=None, mesh: "IMesh"):
        """The properties applied to the VirtualService being define.

        :param virtual_node: The VirtualNode attached to the virtual service. Default: - At most one of virtualRouter and virtualNode is allowed.
        :param virtual_router: The VirtualRouter which the VirtualService uses as provider. Default: - At most one of virtualRouter and virtualNode is allowed.
        :param virtual_service_name: The name of the VirtualService. It is recommended this follows the fully-qualified domain name format, such as "my-service.default.svc.cluster.local". Default: - A name is automatically generated
        :param mesh: The AppMesh mesh name for which the VirtualService belongs to.

        stability
        :stability: experimental
        """
        self._values = {
            'mesh': mesh,
        }
        if virtual_node is not None: self._values["virtual_node"] = virtual_node
        if virtual_router is not None: self._values["virtual_router"] = virtual_router
        if virtual_service_name is not None: self._values["virtual_service_name"] = virtual_service_name

    @property
    def virtual_node(self) -> typing.Optional["IVirtualNode"]:
        """The VirtualNode attached to the virtual service.

        default
        :default: - At most one of virtualRouter and virtualNode is allowed.

        stability
        :stability: experimental
        """
        return self._values.get('virtual_node')

    @property
    def virtual_router(self) -> typing.Optional["IVirtualRouter"]:
        """The VirtualRouter which the VirtualService uses as provider.

        default
        :default: - At most one of virtualRouter and virtualNode is allowed.

        stability
        :stability: experimental
        """
        return self._values.get('virtual_router')

    @property
    def virtual_service_name(self) -> typing.Optional[str]:
        """The name of the VirtualService.

        It is recommended this follows the fully-qualified domain name format,
        such as "my-service.default.svc.cluster.local".

        default
        :default: - A name is automatically generated

        stability
        :stability: experimental

        Example::
            # Example may have issues. See https://github.com/aws/jsii/issues/826
            service.domain.local
        """
        return self._values.get('virtual_service_name')

    @property
    def mesh(self) -> "IMesh":
        """The AppMesh mesh name for which the VirtualService belongs to.

        stability
        :stability: experimental
        """
        return self._values.get('mesh')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'VirtualServiceProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


@jsii.data_type(jsii_type="@aws-cdk/aws-appmesh.WeightedTargetProps", jsii_struct_bases=[], name_mapping={'virtual_node': 'virtualNode', 'weight': 'weight'})
class WeightedTargetProps():
    def __init__(self, *, virtual_node: "IVirtualNode", weight: typing.Optional[jsii.Number]=None):
        """Properties for the Weighted Targets in the route.

        :param virtual_node: The VirtualNode the route points to.
        :param weight: The weight for the target. Default: 1

        stability
        :stability: experimental
        """
        self._values = {
            'virtual_node': virtual_node,
        }
        if weight is not None: self._values["weight"] = weight

    @property
    def virtual_node(self) -> "IVirtualNode":
        """The VirtualNode the route points to.

        stability
        :stability: experimental
        """
        return self._values.get('virtual_node')

    @property
    def weight(self) -> typing.Optional[jsii.Number]:
        """The weight for the target.

        default
        :default: 1

        stability
        :stability: experimental
        """
        return self._values.get('weight')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'WeightedTargetProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


__all__ = ["CfnMesh", "CfnMeshProps", "CfnRoute", "CfnRouteProps", "CfnVirtualNode", "CfnVirtualNodeProps", "CfnVirtualRouter", "CfnVirtualRouterProps", "CfnVirtualService", "CfnVirtualServiceProps", "HealthCheck", "IMesh", "IRoute", "IVirtualNode", "IVirtualRouter", "IVirtualService", "Listener", "Mesh", "MeshFilterType", "MeshProps", "PortMapping", "Protocol", "Route", "RouteBaseProps", "RouteProps", "RouteType", "VirtualNode", "VirtualNodeBaseProps", "VirtualNodeListener", "VirtualNodeProps", "VirtualRouter", "VirtualRouterAttributes", "VirtualRouterBaseProps", "VirtualRouterProps", "VirtualService", "VirtualServiceBaseProps", "VirtualServiceProps", "WeightedTargetProps", "__jsii_assembly__"]

publication.publish()
