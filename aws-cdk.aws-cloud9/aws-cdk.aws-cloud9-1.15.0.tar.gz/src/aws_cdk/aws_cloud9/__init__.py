import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.core
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-cloud9", "1.15.0", __name__, "aws-cloud9@1.15.0.jsii.tgz")
class CfnEnvironmentEC2(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-cloud9.CfnEnvironmentEC2"):
    """A CloudFormation ``AWS::Cloud9::EnvironmentEC2``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloud9-environmentec2.html
    cloudformationResource:
    :cloudformationResource:: AWS::Cloud9::EnvironmentEC2
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, instance_type: str, automatic_stop_time_minutes: typing.Optional[jsii.Number]=None, description: typing.Optional[str]=None, name: typing.Optional[str]=None, owner_arn: typing.Optional[str]=None, repositories: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union["RepositoryProperty", aws_cdk.core.IResolvable]]]]]=None, subnet_id: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::Cloud9::EnvironmentEC2``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param instance_type: ``AWS::Cloud9::EnvironmentEC2.InstanceType``.
        :param automatic_stop_time_minutes: ``AWS::Cloud9::EnvironmentEC2.AutomaticStopTimeMinutes``.
        :param description: ``AWS::Cloud9::EnvironmentEC2.Description``.
        :param name: ``AWS::Cloud9::EnvironmentEC2.Name``.
        :param owner_arn: ``AWS::Cloud9::EnvironmentEC2.OwnerArn``.
        :param repositories: ``AWS::Cloud9::EnvironmentEC2.Repositories``.
        :param subnet_id: ``AWS::Cloud9::EnvironmentEC2.SubnetId``.
        """
        props = CfnEnvironmentEC2Props(instance_type=instance_type, automatic_stop_time_minutes=automatic_stop_time_minutes, description=description, name=name, owner_arn=owner_arn, repositories=repositories, subnet_id=subnet_id)

        jsii.create(CfnEnvironmentEC2, self, [scope, id, props])

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
    @jsii.member(jsii_name="attrName")
    def attr_name(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: Name
        """
        return jsii.get(self, "attrName")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="instanceType")
    def instance_type(self) -> str:
        """``AWS::Cloud9::EnvironmentEC2.InstanceType``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloud9-environmentec2.html#cfn-cloud9-environmentec2-instancetype
        """
        return jsii.get(self, "instanceType")

    @instance_type.setter
    def instance_type(self, value: str):
        return jsii.set(self, "instanceType", value)

    @property
    @jsii.member(jsii_name="automaticStopTimeMinutes")
    def automatic_stop_time_minutes(self) -> typing.Optional[jsii.Number]:
        """``AWS::Cloud9::EnvironmentEC2.AutomaticStopTimeMinutes``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloud9-environmentec2.html#cfn-cloud9-environmentec2-automaticstoptimeminutes
        """
        return jsii.get(self, "automaticStopTimeMinutes")

    @automatic_stop_time_minutes.setter
    def automatic_stop_time_minutes(self, value: typing.Optional[jsii.Number]):
        return jsii.set(self, "automaticStopTimeMinutes", value)

    @property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[str]:
        """``AWS::Cloud9::EnvironmentEC2.Description``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloud9-environmentec2.html#cfn-cloud9-environmentec2-description
        """
        return jsii.get(self, "description")

    @description.setter
    def description(self, value: typing.Optional[str]):
        return jsii.set(self, "description", value)

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[str]:
        """``AWS::Cloud9::EnvironmentEC2.Name``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloud9-environmentec2.html#cfn-cloud9-environmentec2-name
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: typing.Optional[str]):
        return jsii.set(self, "name", value)

    @property
    @jsii.member(jsii_name="ownerArn")
    def owner_arn(self) -> typing.Optional[str]:
        """``AWS::Cloud9::EnvironmentEC2.OwnerArn``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloud9-environmentec2.html#cfn-cloud9-environmentec2-ownerarn
        """
        return jsii.get(self, "ownerArn")

    @owner_arn.setter
    def owner_arn(self, value: typing.Optional[str]):
        return jsii.set(self, "ownerArn", value)

    @property
    @jsii.member(jsii_name="repositories")
    def repositories(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union["RepositoryProperty", aws_cdk.core.IResolvable]]]]]:
        """``AWS::Cloud9::EnvironmentEC2.Repositories``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloud9-environmentec2.html#cfn-cloud9-environmentec2-repositories
        """
        return jsii.get(self, "repositories")

    @repositories.setter
    def repositories(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union["RepositoryProperty", aws_cdk.core.IResolvable]]]]]):
        return jsii.set(self, "repositories", value)

    @property
    @jsii.member(jsii_name="subnetId")
    def subnet_id(self) -> typing.Optional[str]:
        """``AWS::Cloud9::EnvironmentEC2.SubnetId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloud9-environmentec2.html#cfn-cloud9-environmentec2-subnetid
        """
        return jsii.get(self, "subnetId")

    @subnet_id.setter
    def subnet_id(self, value: typing.Optional[str]):
        return jsii.set(self, "subnetId", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-cloud9.CfnEnvironmentEC2.RepositoryProperty", jsii_struct_bases=[], name_mapping={'path_component': 'pathComponent', 'repository_url': 'repositoryUrl'})
    class RepositoryProperty():
        def __init__(self, *, path_component: str, repository_url: str):
            """
            :param path_component: ``CfnEnvironmentEC2.RepositoryProperty.PathComponent``.
            :param repository_url: ``CfnEnvironmentEC2.RepositoryProperty.RepositoryUrl``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cloud9-environmentec2-repository.html
            """
            self._values = {
                'path_component': path_component,
                'repository_url': repository_url,
            }

        @property
        def path_component(self) -> str:
            """``CfnEnvironmentEC2.RepositoryProperty.PathComponent``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cloud9-environmentec2-repository.html#cfn-cloud9-environmentec2-repository-pathcomponent
            """
            return self._values.get('path_component')

        @property
        def repository_url(self) -> str:
            """``CfnEnvironmentEC2.RepositoryProperty.RepositoryUrl``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cloud9-environmentec2-repository.html#cfn-cloud9-environmentec2-repository-repositoryurl
            """
            return self._values.get('repository_url')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'RepositoryProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



@jsii.data_type(jsii_type="@aws-cdk/aws-cloud9.CfnEnvironmentEC2Props", jsii_struct_bases=[], name_mapping={'instance_type': 'instanceType', 'automatic_stop_time_minutes': 'automaticStopTimeMinutes', 'description': 'description', 'name': 'name', 'owner_arn': 'ownerArn', 'repositories': 'repositories', 'subnet_id': 'subnetId'})
class CfnEnvironmentEC2Props():
    def __init__(self, *, instance_type: str, automatic_stop_time_minutes: typing.Optional[jsii.Number]=None, description: typing.Optional[str]=None, name: typing.Optional[str]=None, owner_arn: typing.Optional[str]=None, repositories: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union["CfnEnvironmentEC2.RepositoryProperty", aws_cdk.core.IResolvable]]]]]=None, subnet_id: typing.Optional[str]=None):
        """Properties for defining a ``AWS::Cloud9::EnvironmentEC2``.

        :param instance_type: ``AWS::Cloud9::EnvironmentEC2.InstanceType``.
        :param automatic_stop_time_minutes: ``AWS::Cloud9::EnvironmentEC2.AutomaticStopTimeMinutes``.
        :param description: ``AWS::Cloud9::EnvironmentEC2.Description``.
        :param name: ``AWS::Cloud9::EnvironmentEC2.Name``.
        :param owner_arn: ``AWS::Cloud9::EnvironmentEC2.OwnerArn``.
        :param repositories: ``AWS::Cloud9::EnvironmentEC2.Repositories``.
        :param subnet_id: ``AWS::Cloud9::EnvironmentEC2.SubnetId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloud9-environmentec2.html
        """
        self._values = {
            'instance_type': instance_type,
        }
        if automatic_stop_time_minutes is not None: self._values["automatic_stop_time_minutes"] = automatic_stop_time_minutes
        if description is not None: self._values["description"] = description
        if name is not None: self._values["name"] = name
        if owner_arn is not None: self._values["owner_arn"] = owner_arn
        if repositories is not None: self._values["repositories"] = repositories
        if subnet_id is not None: self._values["subnet_id"] = subnet_id

    @property
    def instance_type(self) -> str:
        """``AWS::Cloud9::EnvironmentEC2.InstanceType``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloud9-environmentec2.html#cfn-cloud9-environmentec2-instancetype
        """
        return self._values.get('instance_type')

    @property
    def automatic_stop_time_minutes(self) -> typing.Optional[jsii.Number]:
        """``AWS::Cloud9::EnvironmentEC2.AutomaticStopTimeMinutes``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloud9-environmentec2.html#cfn-cloud9-environmentec2-automaticstoptimeminutes
        """
        return self._values.get('automatic_stop_time_minutes')

    @property
    def description(self) -> typing.Optional[str]:
        """``AWS::Cloud9::EnvironmentEC2.Description``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloud9-environmentec2.html#cfn-cloud9-environmentec2-description
        """
        return self._values.get('description')

    @property
    def name(self) -> typing.Optional[str]:
        """``AWS::Cloud9::EnvironmentEC2.Name``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloud9-environmentec2.html#cfn-cloud9-environmentec2-name
        """
        return self._values.get('name')

    @property
    def owner_arn(self) -> typing.Optional[str]:
        """``AWS::Cloud9::EnvironmentEC2.OwnerArn``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloud9-environmentec2.html#cfn-cloud9-environmentec2-ownerarn
        """
        return self._values.get('owner_arn')

    @property
    def repositories(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union["CfnEnvironmentEC2.RepositoryProperty", aws_cdk.core.IResolvable]]]]]:
        """``AWS::Cloud9::EnvironmentEC2.Repositories``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloud9-environmentec2.html#cfn-cloud9-environmentec2-repositories
        """
        return self._values.get('repositories')

    @property
    def subnet_id(self) -> typing.Optional[str]:
        """``AWS::Cloud9::EnvironmentEC2.SubnetId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloud9-environmentec2.html#cfn-cloud9-environmentec2-subnetid
        """
        return self._values.get('subnet_id')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnEnvironmentEC2Props(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


__all__ = ["CfnEnvironmentEC2", "CfnEnvironmentEC2Props", "__jsii_assembly__"]

publication.publish()
