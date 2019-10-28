import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.core
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-emr", "1.15.0", __name__, "aws-emr@1.15.0.jsii.tgz")
class CfnCluster(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-emr.CfnCluster"):
    """A CloudFormation ``AWS::EMR::Cluster``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-cluster.html
    cloudformationResource:
    :cloudformationResource:: AWS::EMR::Cluster
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, instances: typing.Union["JobFlowInstancesConfigProperty", aws_cdk.core.IResolvable], job_flow_role: str, name: str, service_role: str, additional_info: typing.Any=None, applications: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "ApplicationProperty"]]]]]=None, auto_scaling_role: typing.Optional[str]=None, bootstrap_actions: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "BootstrapActionConfigProperty"]]]]]=None, configurations: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "ConfigurationProperty"]]]]]=None, custom_ami_id: typing.Optional[str]=None, ebs_root_volume_size: typing.Optional[jsii.Number]=None, kerberos_attributes: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["KerberosAttributesProperty"]]]=None, log_uri: typing.Optional[str]=None, release_label: typing.Optional[str]=None, scale_down_behavior: typing.Optional[str]=None, security_configuration: typing.Optional[str]=None, steps: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "StepConfigProperty"]]]]]=None, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None, visible_to_all_users: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None) -> None:
        """Create a new ``AWS::EMR::Cluster``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param instances: ``AWS::EMR::Cluster.Instances``.
        :param job_flow_role: ``AWS::EMR::Cluster.JobFlowRole``.
        :param name: ``AWS::EMR::Cluster.Name``.
        :param service_role: ``AWS::EMR::Cluster.ServiceRole``.
        :param additional_info: ``AWS::EMR::Cluster.AdditionalInfo``.
        :param applications: ``AWS::EMR::Cluster.Applications``.
        :param auto_scaling_role: ``AWS::EMR::Cluster.AutoScalingRole``.
        :param bootstrap_actions: ``AWS::EMR::Cluster.BootstrapActions``.
        :param configurations: ``AWS::EMR::Cluster.Configurations``.
        :param custom_ami_id: ``AWS::EMR::Cluster.CustomAmiId``.
        :param ebs_root_volume_size: ``AWS::EMR::Cluster.EbsRootVolumeSize``.
        :param kerberos_attributes: ``AWS::EMR::Cluster.KerberosAttributes``.
        :param log_uri: ``AWS::EMR::Cluster.LogUri``.
        :param release_label: ``AWS::EMR::Cluster.ReleaseLabel``.
        :param scale_down_behavior: ``AWS::EMR::Cluster.ScaleDownBehavior``.
        :param security_configuration: ``AWS::EMR::Cluster.SecurityConfiguration``.
        :param steps: ``AWS::EMR::Cluster.Steps``.
        :param tags: ``AWS::EMR::Cluster.Tags``.
        :param visible_to_all_users: ``AWS::EMR::Cluster.VisibleToAllUsers``.
        """
        props = CfnClusterProps(instances=instances, job_flow_role=job_flow_role, name=name, service_role=service_role, additional_info=additional_info, applications=applications, auto_scaling_role=auto_scaling_role, bootstrap_actions=bootstrap_actions, configurations=configurations, custom_ami_id=custom_ami_id, ebs_root_volume_size=ebs_root_volume_size, kerberos_attributes=kerberos_attributes, log_uri=log_uri, release_label=release_label, scale_down_behavior=scale_down_behavior, security_configuration=security_configuration, steps=steps, tags=tags, visible_to_all_users=visible_to_all_users)

        jsii.create(CfnCluster, self, [scope, id, props])

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
    @jsii.member(jsii_name="attrMasterPublicDns")
    def attr_master_public_dns(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: MasterPublicDNS
        """
        return jsii.get(self, "attrMasterPublicDns")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        """``AWS::EMR::Cluster.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-cluster.html#cfn-elasticmapreduce-cluster-tags
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="additionalInfo")
    def additional_info(self) -> typing.Any:
        """``AWS::EMR::Cluster.AdditionalInfo``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-cluster.html#cfn-elasticmapreduce-cluster-additionalinfo
        """
        return jsii.get(self, "additionalInfo")

    @additional_info.setter
    def additional_info(self, value: typing.Any):
        return jsii.set(self, "additionalInfo", value)

    @property
    @jsii.member(jsii_name="instances")
    def instances(self) -> typing.Union["JobFlowInstancesConfigProperty", aws_cdk.core.IResolvable]:
        """``AWS::EMR::Cluster.Instances``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-cluster.html#cfn-elasticmapreduce-cluster-instances
        """
        return jsii.get(self, "instances")

    @instances.setter
    def instances(self, value: typing.Union["JobFlowInstancesConfigProperty", aws_cdk.core.IResolvable]):
        return jsii.set(self, "instances", value)

    @property
    @jsii.member(jsii_name="jobFlowRole")
    def job_flow_role(self) -> str:
        """``AWS::EMR::Cluster.JobFlowRole``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-cluster.html#cfn-elasticmapreduce-cluster-jobflowrole
        """
        return jsii.get(self, "jobFlowRole")

    @job_flow_role.setter
    def job_flow_role(self, value: str):
        return jsii.set(self, "jobFlowRole", value)

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> str:
        """``AWS::EMR::Cluster.Name``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-cluster.html#cfn-elasticmapreduce-cluster-name
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: str):
        return jsii.set(self, "name", value)

    @property
    @jsii.member(jsii_name="serviceRole")
    def service_role(self) -> str:
        """``AWS::EMR::Cluster.ServiceRole``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-cluster.html#cfn-elasticmapreduce-cluster-servicerole
        """
        return jsii.get(self, "serviceRole")

    @service_role.setter
    def service_role(self, value: str):
        return jsii.set(self, "serviceRole", value)

    @property
    @jsii.member(jsii_name="applications")
    def applications(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "ApplicationProperty"]]]]]:
        """``AWS::EMR::Cluster.Applications``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-cluster.html#cfn-elasticmapreduce-cluster-applications
        """
        return jsii.get(self, "applications")

    @applications.setter
    def applications(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "ApplicationProperty"]]]]]):
        return jsii.set(self, "applications", value)

    @property
    @jsii.member(jsii_name="autoScalingRole")
    def auto_scaling_role(self) -> typing.Optional[str]:
        """``AWS::EMR::Cluster.AutoScalingRole``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-cluster.html#cfn-elasticmapreduce-cluster-autoscalingrole
        """
        return jsii.get(self, "autoScalingRole")

    @auto_scaling_role.setter
    def auto_scaling_role(self, value: typing.Optional[str]):
        return jsii.set(self, "autoScalingRole", value)

    @property
    @jsii.member(jsii_name="bootstrapActions")
    def bootstrap_actions(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "BootstrapActionConfigProperty"]]]]]:
        """``AWS::EMR::Cluster.BootstrapActions``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-cluster.html#cfn-elasticmapreduce-cluster-bootstrapactions
        """
        return jsii.get(self, "bootstrapActions")

    @bootstrap_actions.setter
    def bootstrap_actions(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "BootstrapActionConfigProperty"]]]]]):
        return jsii.set(self, "bootstrapActions", value)

    @property
    @jsii.member(jsii_name="configurations")
    def configurations(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "ConfigurationProperty"]]]]]:
        """``AWS::EMR::Cluster.Configurations``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-cluster.html#cfn-elasticmapreduce-cluster-configurations
        """
        return jsii.get(self, "configurations")

    @configurations.setter
    def configurations(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "ConfigurationProperty"]]]]]):
        return jsii.set(self, "configurations", value)

    @property
    @jsii.member(jsii_name="customAmiId")
    def custom_ami_id(self) -> typing.Optional[str]:
        """``AWS::EMR::Cluster.CustomAmiId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-cluster.html#cfn-elasticmapreduce-cluster-customamiid
        """
        return jsii.get(self, "customAmiId")

    @custom_ami_id.setter
    def custom_ami_id(self, value: typing.Optional[str]):
        return jsii.set(self, "customAmiId", value)

    @property
    @jsii.member(jsii_name="ebsRootVolumeSize")
    def ebs_root_volume_size(self) -> typing.Optional[jsii.Number]:
        """``AWS::EMR::Cluster.EbsRootVolumeSize``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-cluster.html#cfn-elasticmapreduce-cluster-ebsrootvolumesize
        """
        return jsii.get(self, "ebsRootVolumeSize")

    @ebs_root_volume_size.setter
    def ebs_root_volume_size(self, value: typing.Optional[jsii.Number]):
        return jsii.set(self, "ebsRootVolumeSize", value)

    @property
    @jsii.member(jsii_name="kerberosAttributes")
    def kerberos_attributes(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["KerberosAttributesProperty"]]]:
        """``AWS::EMR::Cluster.KerberosAttributes``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-cluster.html#cfn-elasticmapreduce-cluster-kerberosattributes
        """
        return jsii.get(self, "kerberosAttributes")

    @kerberos_attributes.setter
    def kerberos_attributes(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["KerberosAttributesProperty"]]]):
        return jsii.set(self, "kerberosAttributes", value)

    @property
    @jsii.member(jsii_name="logUri")
    def log_uri(self) -> typing.Optional[str]:
        """``AWS::EMR::Cluster.LogUri``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-cluster.html#cfn-elasticmapreduce-cluster-loguri
        """
        return jsii.get(self, "logUri")

    @log_uri.setter
    def log_uri(self, value: typing.Optional[str]):
        return jsii.set(self, "logUri", value)

    @property
    @jsii.member(jsii_name="releaseLabel")
    def release_label(self) -> typing.Optional[str]:
        """``AWS::EMR::Cluster.ReleaseLabel``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-cluster.html#cfn-elasticmapreduce-cluster-releaselabel
        """
        return jsii.get(self, "releaseLabel")

    @release_label.setter
    def release_label(self, value: typing.Optional[str]):
        return jsii.set(self, "releaseLabel", value)

    @property
    @jsii.member(jsii_name="scaleDownBehavior")
    def scale_down_behavior(self) -> typing.Optional[str]:
        """``AWS::EMR::Cluster.ScaleDownBehavior``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-cluster.html#cfn-elasticmapreduce-cluster-scaledownbehavior
        """
        return jsii.get(self, "scaleDownBehavior")

    @scale_down_behavior.setter
    def scale_down_behavior(self, value: typing.Optional[str]):
        return jsii.set(self, "scaleDownBehavior", value)

    @property
    @jsii.member(jsii_name="securityConfiguration")
    def security_configuration(self) -> typing.Optional[str]:
        """``AWS::EMR::Cluster.SecurityConfiguration``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-cluster.html#cfn-elasticmapreduce-cluster-securityconfiguration
        """
        return jsii.get(self, "securityConfiguration")

    @security_configuration.setter
    def security_configuration(self, value: typing.Optional[str]):
        return jsii.set(self, "securityConfiguration", value)

    @property
    @jsii.member(jsii_name="steps")
    def steps(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "StepConfigProperty"]]]]]:
        """``AWS::EMR::Cluster.Steps``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-cluster.html#cfn-elasticmapreduce-cluster-steps
        """
        return jsii.get(self, "steps")

    @steps.setter
    def steps(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "StepConfigProperty"]]]]]):
        return jsii.set(self, "steps", value)

    @property
    @jsii.member(jsii_name="visibleToAllUsers")
    def visible_to_all_users(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::EMR::Cluster.VisibleToAllUsers``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-cluster.html#cfn-elasticmapreduce-cluster-visibletoallusers
        """
        return jsii.get(self, "visibleToAllUsers")

    @visible_to_all_users.setter
    def visible_to_all_users(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "visibleToAllUsers", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnCluster.ApplicationProperty", jsii_struct_bases=[], name_mapping={'additional_info': 'additionalInfo', 'args': 'args', 'name': 'name', 'version': 'version'})
    class ApplicationProperty():
        def __init__(self, *, additional_info: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.Mapping[str,str]]]]=None, args: typing.Optional[typing.List[str]]=None, name: typing.Optional[str]=None, version: typing.Optional[str]=None):
            """
            :param additional_info: ``CfnCluster.ApplicationProperty.AdditionalInfo``.
            :param args: ``CfnCluster.ApplicationProperty.Args``.
            :param name: ``CfnCluster.ApplicationProperty.Name``.
            :param version: ``CfnCluster.ApplicationProperty.Version``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-application.html
            """
            self._values = {
            }
            if additional_info is not None: self._values["additional_info"] = additional_info
            if args is not None: self._values["args"] = args
            if name is not None: self._values["name"] = name
            if version is not None: self._values["version"] = version

        @property
        def additional_info(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.Mapping[str,str]]]]:
            """``CfnCluster.ApplicationProperty.AdditionalInfo``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-application.html#cfn-elasticmapreduce-cluster-application-additionalinfo
            """
            return self._values.get('additional_info')

        @property
        def args(self) -> typing.Optional[typing.List[str]]:
            """``CfnCluster.ApplicationProperty.Args``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-application.html#cfn-elasticmapreduce-cluster-application-args
            """
            return self._values.get('args')

        @property
        def name(self) -> typing.Optional[str]:
            """``CfnCluster.ApplicationProperty.Name``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-application.html#cfn-elasticmapreduce-cluster-application-name
            """
            return self._values.get('name')

        @property
        def version(self) -> typing.Optional[str]:
            """``CfnCluster.ApplicationProperty.Version``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-application.html#cfn-elasticmapreduce-cluster-application-version
            """
            return self._values.get('version')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'ApplicationProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnCluster.AutoScalingPolicyProperty", jsii_struct_bases=[], name_mapping={'constraints': 'constraints', 'rules': 'rules'})
    class AutoScalingPolicyProperty():
        def __init__(self, *, constraints: typing.Union[aws_cdk.core.IResolvable, "CfnCluster.ScalingConstraintsProperty"], rules: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnCluster.ScalingRuleProperty"]]]):
            """
            :param constraints: ``CfnCluster.AutoScalingPolicyProperty.Constraints``.
            :param rules: ``CfnCluster.AutoScalingPolicyProperty.Rules``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-autoscalingpolicy.html
            """
            self._values = {
                'constraints': constraints,
                'rules': rules,
            }

        @property
        def constraints(self) -> typing.Union[aws_cdk.core.IResolvable, "CfnCluster.ScalingConstraintsProperty"]:
            """``CfnCluster.AutoScalingPolicyProperty.Constraints``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-autoscalingpolicy.html#cfn-elasticmapreduce-cluster-autoscalingpolicy-constraints
            """
            return self._values.get('constraints')

        @property
        def rules(self) -> typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnCluster.ScalingRuleProperty"]]]:
            """``CfnCluster.AutoScalingPolicyProperty.Rules``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-autoscalingpolicy.html#cfn-elasticmapreduce-cluster-autoscalingpolicy-rules
            """
            return self._values.get('rules')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'AutoScalingPolicyProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnCluster.BootstrapActionConfigProperty", jsii_struct_bases=[], name_mapping={'name': 'name', 'script_bootstrap_action': 'scriptBootstrapAction'})
    class BootstrapActionConfigProperty():
        def __init__(self, *, name: str, script_bootstrap_action: typing.Union[aws_cdk.core.IResolvable, "CfnCluster.ScriptBootstrapActionConfigProperty"]):
            """
            :param name: ``CfnCluster.BootstrapActionConfigProperty.Name``.
            :param script_bootstrap_action: ``CfnCluster.BootstrapActionConfigProperty.ScriptBootstrapAction``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-bootstrapactionconfig.html
            """
            self._values = {
                'name': name,
                'script_bootstrap_action': script_bootstrap_action,
            }

        @property
        def name(self) -> str:
            """``CfnCluster.BootstrapActionConfigProperty.Name``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-bootstrapactionconfig.html#cfn-elasticmapreduce-cluster-bootstrapactionconfig-name
            """
            return self._values.get('name')

        @property
        def script_bootstrap_action(self) -> typing.Union[aws_cdk.core.IResolvable, "CfnCluster.ScriptBootstrapActionConfigProperty"]:
            """``CfnCluster.BootstrapActionConfigProperty.ScriptBootstrapAction``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-bootstrapactionconfig.html#cfn-elasticmapreduce-cluster-bootstrapactionconfig-scriptbootstrapaction
            """
            return self._values.get('script_bootstrap_action')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'BootstrapActionConfigProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnCluster.CloudWatchAlarmDefinitionProperty", jsii_struct_bases=[], name_mapping={'comparison_operator': 'comparisonOperator', 'metric_name': 'metricName', 'period': 'period', 'threshold': 'threshold', 'dimensions': 'dimensions', 'evaluation_periods': 'evaluationPeriods', 'namespace': 'namespace', 'statistic': 'statistic', 'unit': 'unit'})
    class CloudWatchAlarmDefinitionProperty():
        def __init__(self, *, comparison_operator: str, metric_name: str, period: jsii.Number, threshold: jsii.Number, dimensions: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnCluster.MetricDimensionProperty"]]]]]=None, evaluation_periods: typing.Optional[jsii.Number]=None, namespace: typing.Optional[str]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[str]=None):
            """
            :param comparison_operator: ``CfnCluster.CloudWatchAlarmDefinitionProperty.ComparisonOperator``.
            :param metric_name: ``CfnCluster.CloudWatchAlarmDefinitionProperty.MetricName``.
            :param period: ``CfnCluster.CloudWatchAlarmDefinitionProperty.Period``.
            :param threshold: ``CfnCluster.CloudWatchAlarmDefinitionProperty.Threshold``.
            :param dimensions: ``CfnCluster.CloudWatchAlarmDefinitionProperty.Dimensions``.
            :param evaluation_periods: ``CfnCluster.CloudWatchAlarmDefinitionProperty.EvaluationPeriods``.
            :param namespace: ``CfnCluster.CloudWatchAlarmDefinitionProperty.Namespace``.
            :param statistic: ``CfnCluster.CloudWatchAlarmDefinitionProperty.Statistic``.
            :param unit: ``CfnCluster.CloudWatchAlarmDefinitionProperty.Unit``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-cloudwatchalarmdefinition.html
            """
            self._values = {
                'comparison_operator': comparison_operator,
                'metric_name': metric_name,
                'period': period,
                'threshold': threshold,
            }
            if dimensions is not None: self._values["dimensions"] = dimensions
            if evaluation_periods is not None: self._values["evaluation_periods"] = evaluation_periods
            if namespace is not None: self._values["namespace"] = namespace
            if statistic is not None: self._values["statistic"] = statistic
            if unit is not None: self._values["unit"] = unit

        @property
        def comparison_operator(self) -> str:
            """``CfnCluster.CloudWatchAlarmDefinitionProperty.ComparisonOperator``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-cloudwatchalarmdefinition.html#cfn-elasticmapreduce-cluster-cloudwatchalarmdefinition-comparisonoperator
            """
            return self._values.get('comparison_operator')

        @property
        def metric_name(self) -> str:
            """``CfnCluster.CloudWatchAlarmDefinitionProperty.MetricName``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-cloudwatchalarmdefinition.html#cfn-elasticmapreduce-cluster-cloudwatchalarmdefinition-metricname
            """
            return self._values.get('metric_name')

        @property
        def period(self) -> jsii.Number:
            """``CfnCluster.CloudWatchAlarmDefinitionProperty.Period``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-cloudwatchalarmdefinition.html#cfn-elasticmapreduce-cluster-cloudwatchalarmdefinition-period
            """
            return self._values.get('period')

        @property
        def threshold(self) -> jsii.Number:
            """``CfnCluster.CloudWatchAlarmDefinitionProperty.Threshold``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-cloudwatchalarmdefinition.html#cfn-elasticmapreduce-cluster-cloudwatchalarmdefinition-threshold
            """
            return self._values.get('threshold')

        @property
        def dimensions(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnCluster.MetricDimensionProperty"]]]]]:
            """``CfnCluster.CloudWatchAlarmDefinitionProperty.Dimensions``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-cloudwatchalarmdefinition.html#cfn-elasticmapreduce-cluster-cloudwatchalarmdefinition-dimensions
            """
            return self._values.get('dimensions')

        @property
        def evaluation_periods(self) -> typing.Optional[jsii.Number]:
            """``CfnCluster.CloudWatchAlarmDefinitionProperty.EvaluationPeriods``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-cloudwatchalarmdefinition.html#cfn-elasticmapreduce-cluster-cloudwatchalarmdefinition-evaluationperiods
            """
            return self._values.get('evaluation_periods')

        @property
        def namespace(self) -> typing.Optional[str]:
            """``CfnCluster.CloudWatchAlarmDefinitionProperty.Namespace``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-cloudwatchalarmdefinition.html#cfn-elasticmapreduce-cluster-cloudwatchalarmdefinition-namespace
            """
            return self._values.get('namespace')

        @property
        def statistic(self) -> typing.Optional[str]:
            """``CfnCluster.CloudWatchAlarmDefinitionProperty.Statistic``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-cloudwatchalarmdefinition.html#cfn-elasticmapreduce-cluster-cloudwatchalarmdefinition-statistic
            """
            return self._values.get('statistic')

        @property
        def unit(self) -> typing.Optional[str]:
            """``CfnCluster.CloudWatchAlarmDefinitionProperty.Unit``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-cloudwatchalarmdefinition.html#cfn-elasticmapreduce-cluster-cloudwatchalarmdefinition-unit
            """
            return self._values.get('unit')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'CloudWatchAlarmDefinitionProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnCluster.ConfigurationProperty", jsii_struct_bases=[], name_mapping={'classification': 'classification', 'configuration_properties': 'configurationProperties', 'configurations': 'configurations'})
    class ConfigurationProperty():
        def __init__(self, *, classification: typing.Optional[str]=None, configuration_properties: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.Mapping[str,str]]]]=None, configurations: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnCluster.ConfigurationProperty"]]]]]=None):
            """
            :param classification: ``CfnCluster.ConfigurationProperty.Classification``.
            :param configuration_properties: ``CfnCluster.ConfigurationProperty.ConfigurationProperties``.
            :param configurations: ``CfnCluster.ConfigurationProperty.Configurations``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-configuration.html
            """
            self._values = {
            }
            if classification is not None: self._values["classification"] = classification
            if configuration_properties is not None: self._values["configuration_properties"] = configuration_properties
            if configurations is not None: self._values["configurations"] = configurations

        @property
        def classification(self) -> typing.Optional[str]:
            """``CfnCluster.ConfigurationProperty.Classification``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-configuration.html#cfn-elasticmapreduce-cluster-configuration-classification
            """
            return self._values.get('classification')

        @property
        def configuration_properties(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.Mapping[str,str]]]]:
            """``CfnCluster.ConfigurationProperty.ConfigurationProperties``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-configuration.html#cfn-elasticmapreduce-cluster-configuration-configurationproperties
            """
            return self._values.get('configuration_properties')

        @property
        def configurations(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnCluster.ConfigurationProperty"]]]]]:
            """``CfnCluster.ConfigurationProperty.Configurations``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-configuration.html#cfn-elasticmapreduce-cluster-configuration-configurations
            """
            return self._values.get('configurations')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'ConfigurationProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnCluster.EbsBlockDeviceConfigProperty", jsii_struct_bases=[], name_mapping={'volume_specification': 'volumeSpecification', 'volumes_per_instance': 'volumesPerInstance'})
    class EbsBlockDeviceConfigProperty():
        def __init__(self, *, volume_specification: typing.Union[aws_cdk.core.IResolvable, "CfnCluster.VolumeSpecificationProperty"], volumes_per_instance: typing.Optional[jsii.Number]=None):
            """
            :param volume_specification: ``CfnCluster.EbsBlockDeviceConfigProperty.VolumeSpecification``.
            :param volumes_per_instance: ``CfnCluster.EbsBlockDeviceConfigProperty.VolumesPerInstance``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-ebsblockdeviceconfig.html
            """
            self._values = {
                'volume_specification': volume_specification,
            }
            if volumes_per_instance is not None: self._values["volumes_per_instance"] = volumes_per_instance

        @property
        def volume_specification(self) -> typing.Union[aws_cdk.core.IResolvable, "CfnCluster.VolumeSpecificationProperty"]:
            """``CfnCluster.EbsBlockDeviceConfigProperty.VolumeSpecification``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-ebsblockdeviceconfig.html#cfn-elasticmapreduce-cluster-ebsblockdeviceconfig-volumespecification
            """
            return self._values.get('volume_specification')

        @property
        def volumes_per_instance(self) -> typing.Optional[jsii.Number]:
            """``CfnCluster.EbsBlockDeviceConfigProperty.VolumesPerInstance``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-ebsblockdeviceconfig.html#cfn-elasticmapreduce-cluster-ebsblockdeviceconfig-volumesperinstance
            """
            return self._values.get('volumes_per_instance')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'EbsBlockDeviceConfigProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnCluster.EbsConfigurationProperty", jsii_struct_bases=[], name_mapping={'ebs_block_device_configs': 'ebsBlockDeviceConfigs', 'ebs_optimized': 'ebsOptimized'})
    class EbsConfigurationProperty():
        def __init__(self, *, ebs_block_device_configs: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnCluster.EbsBlockDeviceConfigProperty"]]]]]=None, ebs_optimized: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None):
            """
            :param ebs_block_device_configs: ``CfnCluster.EbsConfigurationProperty.EbsBlockDeviceConfigs``.
            :param ebs_optimized: ``CfnCluster.EbsConfigurationProperty.EbsOptimized``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-ebsconfiguration.html
            """
            self._values = {
            }
            if ebs_block_device_configs is not None: self._values["ebs_block_device_configs"] = ebs_block_device_configs
            if ebs_optimized is not None: self._values["ebs_optimized"] = ebs_optimized

        @property
        def ebs_block_device_configs(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnCluster.EbsBlockDeviceConfigProperty"]]]]]:
            """``CfnCluster.EbsConfigurationProperty.EbsBlockDeviceConfigs``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-ebsconfiguration.html#cfn-elasticmapreduce-cluster-ebsconfiguration-ebsblockdeviceconfigs
            """
            return self._values.get('ebs_block_device_configs')

        @property
        def ebs_optimized(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
            """``CfnCluster.EbsConfigurationProperty.EbsOptimized``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-ebsconfiguration.html#cfn-elasticmapreduce-cluster-ebsconfiguration-ebsoptimized
            """
            return self._values.get('ebs_optimized')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'EbsConfigurationProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnCluster.HadoopJarStepConfigProperty", jsii_struct_bases=[], name_mapping={'jar': 'jar', 'args': 'args', 'main_class': 'mainClass', 'step_properties': 'stepProperties'})
    class HadoopJarStepConfigProperty():
        def __init__(self, *, jar: str, args: typing.Optional[typing.List[str]]=None, main_class: typing.Optional[str]=None, step_properties: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnCluster.KeyValueProperty"]]]]]=None):
            """
            :param jar: ``CfnCluster.HadoopJarStepConfigProperty.Jar``.
            :param args: ``CfnCluster.HadoopJarStepConfigProperty.Args``.
            :param main_class: ``CfnCluster.HadoopJarStepConfigProperty.MainClass``.
            :param step_properties: ``CfnCluster.HadoopJarStepConfigProperty.StepProperties``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-hadoopjarstepconfig.html
            """
            self._values = {
                'jar': jar,
            }
            if args is not None: self._values["args"] = args
            if main_class is not None: self._values["main_class"] = main_class
            if step_properties is not None: self._values["step_properties"] = step_properties

        @property
        def jar(self) -> str:
            """``CfnCluster.HadoopJarStepConfigProperty.Jar``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-hadoopjarstepconfig.html#cfn-elasticmapreduce-cluster-hadoopjarstepconfig-jar
            """
            return self._values.get('jar')

        @property
        def args(self) -> typing.Optional[typing.List[str]]:
            """``CfnCluster.HadoopJarStepConfigProperty.Args``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-hadoopjarstepconfig.html#cfn-elasticmapreduce-cluster-hadoopjarstepconfig-args
            """
            return self._values.get('args')

        @property
        def main_class(self) -> typing.Optional[str]:
            """``CfnCluster.HadoopJarStepConfigProperty.MainClass``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-hadoopjarstepconfig.html#cfn-elasticmapreduce-cluster-hadoopjarstepconfig-mainclass
            """
            return self._values.get('main_class')

        @property
        def step_properties(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnCluster.KeyValueProperty"]]]]]:
            """``CfnCluster.HadoopJarStepConfigProperty.StepProperties``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-hadoopjarstepconfig.html#cfn-elasticmapreduce-cluster-hadoopjarstepconfig-stepproperties
            """
            return self._values.get('step_properties')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'HadoopJarStepConfigProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnCluster.InstanceFleetConfigProperty", jsii_struct_bases=[], name_mapping={'instance_type_configs': 'instanceTypeConfigs', 'launch_specifications': 'launchSpecifications', 'name': 'name', 'target_on_demand_capacity': 'targetOnDemandCapacity', 'target_spot_capacity': 'targetSpotCapacity'})
    class InstanceFleetConfigProperty():
        def __init__(self, *, instance_type_configs: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnCluster.InstanceTypeConfigProperty"]]]]]=None, launch_specifications: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnCluster.InstanceFleetProvisioningSpecificationsProperty"]]]=None, name: typing.Optional[str]=None, target_on_demand_capacity: typing.Optional[jsii.Number]=None, target_spot_capacity: typing.Optional[jsii.Number]=None):
            """
            :param instance_type_configs: ``CfnCluster.InstanceFleetConfigProperty.InstanceTypeConfigs``.
            :param launch_specifications: ``CfnCluster.InstanceFleetConfigProperty.LaunchSpecifications``.
            :param name: ``CfnCluster.InstanceFleetConfigProperty.Name``.
            :param target_on_demand_capacity: ``CfnCluster.InstanceFleetConfigProperty.TargetOnDemandCapacity``.
            :param target_spot_capacity: ``CfnCluster.InstanceFleetConfigProperty.TargetSpotCapacity``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-instancefleetconfig.html
            """
            self._values = {
            }
            if instance_type_configs is not None: self._values["instance_type_configs"] = instance_type_configs
            if launch_specifications is not None: self._values["launch_specifications"] = launch_specifications
            if name is not None: self._values["name"] = name
            if target_on_demand_capacity is not None: self._values["target_on_demand_capacity"] = target_on_demand_capacity
            if target_spot_capacity is not None: self._values["target_spot_capacity"] = target_spot_capacity

        @property
        def instance_type_configs(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnCluster.InstanceTypeConfigProperty"]]]]]:
            """``CfnCluster.InstanceFleetConfigProperty.InstanceTypeConfigs``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-instancefleetconfig.html#cfn-elasticmapreduce-cluster-instancefleetconfig-instancetypeconfigs
            """
            return self._values.get('instance_type_configs')

        @property
        def launch_specifications(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnCluster.InstanceFleetProvisioningSpecificationsProperty"]]]:
            """``CfnCluster.InstanceFleetConfigProperty.LaunchSpecifications``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-instancefleetconfig.html#cfn-elasticmapreduce-cluster-instancefleetconfig-launchspecifications
            """
            return self._values.get('launch_specifications')

        @property
        def name(self) -> typing.Optional[str]:
            """``CfnCluster.InstanceFleetConfigProperty.Name``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-instancefleetconfig.html#cfn-elasticmapreduce-cluster-instancefleetconfig-name
            """
            return self._values.get('name')

        @property
        def target_on_demand_capacity(self) -> typing.Optional[jsii.Number]:
            """``CfnCluster.InstanceFleetConfigProperty.TargetOnDemandCapacity``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-instancefleetconfig.html#cfn-elasticmapreduce-cluster-instancefleetconfig-targetondemandcapacity
            """
            return self._values.get('target_on_demand_capacity')

        @property
        def target_spot_capacity(self) -> typing.Optional[jsii.Number]:
            """``CfnCluster.InstanceFleetConfigProperty.TargetSpotCapacity``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-instancefleetconfig.html#cfn-elasticmapreduce-cluster-instancefleetconfig-targetspotcapacity
            """
            return self._values.get('target_spot_capacity')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'InstanceFleetConfigProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnCluster.InstanceFleetProvisioningSpecificationsProperty", jsii_struct_bases=[], name_mapping={'spot_specification': 'spotSpecification'})
    class InstanceFleetProvisioningSpecificationsProperty():
        def __init__(self, *, spot_specification: typing.Union[aws_cdk.core.IResolvable, "CfnCluster.SpotProvisioningSpecificationProperty"]):
            """
            :param spot_specification: ``CfnCluster.InstanceFleetProvisioningSpecificationsProperty.SpotSpecification``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-instancefleetprovisioningspecifications.html
            """
            self._values = {
                'spot_specification': spot_specification,
            }

        @property
        def spot_specification(self) -> typing.Union[aws_cdk.core.IResolvable, "CfnCluster.SpotProvisioningSpecificationProperty"]:
            """``CfnCluster.InstanceFleetProvisioningSpecificationsProperty.SpotSpecification``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-instancefleetprovisioningspecifications.html#cfn-elasticmapreduce-cluster-instancefleetprovisioningspecifications-spotspecification
            """
            return self._values.get('spot_specification')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'InstanceFleetProvisioningSpecificationsProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnCluster.InstanceGroupConfigProperty", jsii_struct_bases=[], name_mapping={'instance_count': 'instanceCount', 'instance_type': 'instanceType', 'auto_scaling_policy': 'autoScalingPolicy', 'bid_price': 'bidPrice', 'configurations': 'configurations', 'ebs_configuration': 'ebsConfiguration', 'market': 'market', 'name': 'name'})
    class InstanceGroupConfigProperty():
        def __init__(self, *, instance_count: jsii.Number, instance_type: str, auto_scaling_policy: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnCluster.AutoScalingPolicyProperty"]]]=None, bid_price: typing.Optional[str]=None, configurations: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnCluster.ConfigurationProperty"]]]]]=None, ebs_configuration: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnCluster.EbsConfigurationProperty"]]]=None, market: typing.Optional[str]=None, name: typing.Optional[str]=None):
            """
            :param instance_count: ``CfnCluster.InstanceGroupConfigProperty.InstanceCount``.
            :param instance_type: ``CfnCluster.InstanceGroupConfigProperty.InstanceType``.
            :param auto_scaling_policy: ``CfnCluster.InstanceGroupConfigProperty.AutoScalingPolicy``.
            :param bid_price: ``CfnCluster.InstanceGroupConfigProperty.BidPrice``.
            :param configurations: ``CfnCluster.InstanceGroupConfigProperty.Configurations``.
            :param ebs_configuration: ``CfnCluster.InstanceGroupConfigProperty.EbsConfiguration``.
            :param market: ``CfnCluster.InstanceGroupConfigProperty.Market``.
            :param name: ``CfnCluster.InstanceGroupConfigProperty.Name``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-instancegroupconfig.html
            """
            self._values = {
                'instance_count': instance_count,
                'instance_type': instance_type,
            }
            if auto_scaling_policy is not None: self._values["auto_scaling_policy"] = auto_scaling_policy
            if bid_price is not None: self._values["bid_price"] = bid_price
            if configurations is not None: self._values["configurations"] = configurations
            if ebs_configuration is not None: self._values["ebs_configuration"] = ebs_configuration
            if market is not None: self._values["market"] = market
            if name is not None: self._values["name"] = name

        @property
        def instance_count(self) -> jsii.Number:
            """``CfnCluster.InstanceGroupConfigProperty.InstanceCount``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-instancegroupconfig.html#cfn-elasticmapreduce-cluster-instancegroupconfig-instancecount
            """
            return self._values.get('instance_count')

        @property
        def instance_type(self) -> str:
            """``CfnCluster.InstanceGroupConfigProperty.InstanceType``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-instancegroupconfig.html#cfn-elasticmapreduce-cluster-instancegroupconfig-instancetype
            """
            return self._values.get('instance_type')

        @property
        def auto_scaling_policy(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnCluster.AutoScalingPolicyProperty"]]]:
            """``CfnCluster.InstanceGroupConfigProperty.AutoScalingPolicy``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-instancegroupconfig.html#cfn-elasticmapreduce-cluster-instancegroupconfig-autoscalingpolicy
            """
            return self._values.get('auto_scaling_policy')

        @property
        def bid_price(self) -> typing.Optional[str]:
            """``CfnCluster.InstanceGroupConfigProperty.BidPrice``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-instancegroupconfig.html#cfn-elasticmapreduce-cluster-instancegroupconfig-bidprice
            """
            return self._values.get('bid_price')

        @property
        def configurations(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnCluster.ConfigurationProperty"]]]]]:
            """``CfnCluster.InstanceGroupConfigProperty.Configurations``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-instancegroupconfig.html#cfn-elasticmapreduce-cluster-instancegroupconfig-configurations
            """
            return self._values.get('configurations')

        @property
        def ebs_configuration(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnCluster.EbsConfigurationProperty"]]]:
            """``CfnCluster.InstanceGroupConfigProperty.EbsConfiguration``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-instancegroupconfig.html#cfn-elasticmapreduce-cluster-instancegroupconfig-ebsconfiguration
            """
            return self._values.get('ebs_configuration')

        @property
        def market(self) -> typing.Optional[str]:
            """``CfnCluster.InstanceGroupConfigProperty.Market``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-instancegroupconfig.html#cfn-elasticmapreduce-cluster-instancegroupconfig-market
            """
            return self._values.get('market')

        @property
        def name(self) -> typing.Optional[str]:
            """``CfnCluster.InstanceGroupConfigProperty.Name``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-instancegroupconfig.html#cfn-elasticmapreduce-cluster-instancegroupconfig-name
            """
            return self._values.get('name')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'InstanceGroupConfigProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnCluster.InstanceTypeConfigProperty", jsii_struct_bases=[], name_mapping={'instance_type': 'instanceType', 'bid_price': 'bidPrice', 'bid_price_as_percentage_of_on_demand_price': 'bidPriceAsPercentageOfOnDemandPrice', 'configurations': 'configurations', 'ebs_configuration': 'ebsConfiguration', 'weighted_capacity': 'weightedCapacity'})
    class InstanceTypeConfigProperty():
        def __init__(self, *, instance_type: str, bid_price: typing.Optional[str]=None, bid_price_as_percentage_of_on_demand_price: typing.Optional[jsii.Number]=None, configurations: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnCluster.ConfigurationProperty"]]]]]=None, ebs_configuration: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnCluster.EbsConfigurationProperty"]]]=None, weighted_capacity: typing.Optional[jsii.Number]=None):
            """
            :param instance_type: ``CfnCluster.InstanceTypeConfigProperty.InstanceType``.
            :param bid_price: ``CfnCluster.InstanceTypeConfigProperty.BidPrice``.
            :param bid_price_as_percentage_of_on_demand_price: ``CfnCluster.InstanceTypeConfigProperty.BidPriceAsPercentageOfOnDemandPrice``.
            :param configurations: ``CfnCluster.InstanceTypeConfigProperty.Configurations``.
            :param ebs_configuration: ``CfnCluster.InstanceTypeConfigProperty.EbsConfiguration``.
            :param weighted_capacity: ``CfnCluster.InstanceTypeConfigProperty.WeightedCapacity``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-instancetypeconfig.html
            """
            self._values = {
                'instance_type': instance_type,
            }
            if bid_price is not None: self._values["bid_price"] = bid_price
            if bid_price_as_percentage_of_on_demand_price is not None: self._values["bid_price_as_percentage_of_on_demand_price"] = bid_price_as_percentage_of_on_demand_price
            if configurations is not None: self._values["configurations"] = configurations
            if ebs_configuration is not None: self._values["ebs_configuration"] = ebs_configuration
            if weighted_capacity is not None: self._values["weighted_capacity"] = weighted_capacity

        @property
        def instance_type(self) -> str:
            """``CfnCluster.InstanceTypeConfigProperty.InstanceType``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-instancetypeconfig.html#cfn-elasticmapreduce-cluster-instancetypeconfig-instancetype
            """
            return self._values.get('instance_type')

        @property
        def bid_price(self) -> typing.Optional[str]:
            """``CfnCluster.InstanceTypeConfigProperty.BidPrice``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-instancetypeconfig.html#cfn-elasticmapreduce-cluster-instancetypeconfig-bidprice
            """
            return self._values.get('bid_price')

        @property
        def bid_price_as_percentage_of_on_demand_price(self) -> typing.Optional[jsii.Number]:
            """``CfnCluster.InstanceTypeConfigProperty.BidPriceAsPercentageOfOnDemandPrice``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-instancetypeconfig.html#cfn-elasticmapreduce-cluster-instancetypeconfig-bidpriceaspercentageofondemandprice
            """
            return self._values.get('bid_price_as_percentage_of_on_demand_price')

        @property
        def configurations(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnCluster.ConfigurationProperty"]]]]]:
            """``CfnCluster.InstanceTypeConfigProperty.Configurations``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-instancetypeconfig.html#cfn-elasticmapreduce-cluster-instancetypeconfig-configurations
            """
            return self._values.get('configurations')

        @property
        def ebs_configuration(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnCluster.EbsConfigurationProperty"]]]:
            """``CfnCluster.InstanceTypeConfigProperty.EbsConfiguration``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-instancetypeconfig.html#cfn-elasticmapreduce-cluster-instancetypeconfig-ebsconfiguration
            """
            return self._values.get('ebs_configuration')

        @property
        def weighted_capacity(self) -> typing.Optional[jsii.Number]:
            """``CfnCluster.InstanceTypeConfigProperty.WeightedCapacity``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-instancetypeconfig.html#cfn-elasticmapreduce-cluster-instancetypeconfig-weightedcapacity
            """
            return self._values.get('weighted_capacity')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'InstanceTypeConfigProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnCluster.JobFlowInstancesConfigProperty", jsii_struct_bases=[], name_mapping={'additional_master_security_groups': 'additionalMasterSecurityGroups', 'additional_slave_security_groups': 'additionalSlaveSecurityGroups', 'core_instance_fleet': 'coreInstanceFleet', 'core_instance_group': 'coreInstanceGroup', 'ec2_key_name': 'ec2KeyName', 'ec2_subnet_id': 'ec2SubnetId', 'ec2_subnet_ids': 'ec2SubnetIds', 'emr_managed_master_security_group': 'emrManagedMasterSecurityGroup', 'emr_managed_slave_security_group': 'emrManagedSlaveSecurityGroup', 'hadoop_version': 'hadoopVersion', 'keep_job_flow_alive_when_no_steps': 'keepJobFlowAliveWhenNoSteps', 'master_instance_fleet': 'masterInstanceFleet', 'master_instance_group': 'masterInstanceGroup', 'placement': 'placement', 'service_access_security_group': 'serviceAccessSecurityGroup', 'termination_protected': 'terminationProtected'})
    class JobFlowInstancesConfigProperty():
        def __init__(self, *, additional_master_security_groups: typing.Optional[typing.List[str]]=None, additional_slave_security_groups: typing.Optional[typing.List[str]]=None, core_instance_fleet: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnCluster.InstanceFleetConfigProperty"]]]=None, core_instance_group: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnCluster.InstanceGroupConfigProperty"]]]=None, ec2_key_name: typing.Optional[str]=None, ec2_subnet_id: typing.Optional[str]=None, ec2_subnet_ids: typing.Optional[typing.List[str]]=None, emr_managed_master_security_group: typing.Optional[str]=None, emr_managed_slave_security_group: typing.Optional[str]=None, hadoop_version: typing.Optional[str]=None, keep_job_flow_alive_when_no_steps: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, master_instance_fleet: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnCluster.InstanceFleetConfigProperty"]]]=None, master_instance_group: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnCluster.InstanceGroupConfigProperty"]]]=None, placement: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnCluster.PlacementTypeProperty"]]]=None, service_access_security_group: typing.Optional[str]=None, termination_protected: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None):
            """
            :param additional_master_security_groups: ``CfnCluster.JobFlowInstancesConfigProperty.AdditionalMasterSecurityGroups``.
            :param additional_slave_security_groups: ``CfnCluster.JobFlowInstancesConfigProperty.AdditionalSlaveSecurityGroups``.
            :param core_instance_fleet: ``CfnCluster.JobFlowInstancesConfigProperty.CoreInstanceFleet``.
            :param core_instance_group: ``CfnCluster.JobFlowInstancesConfigProperty.CoreInstanceGroup``.
            :param ec2_key_name: ``CfnCluster.JobFlowInstancesConfigProperty.Ec2KeyName``.
            :param ec2_subnet_id: ``CfnCluster.JobFlowInstancesConfigProperty.Ec2SubnetId``.
            :param ec2_subnet_ids: ``CfnCluster.JobFlowInstancesConfigProperty.Ec2SubnetIds``.
            :param emr_managed_master_security_group: ``CfnCluster.JobFlowInstancesConfigProperty.EmrManagedMasterSecurityGroup``.
            :param emr_managed_slave_security_group: ``CfnCluster.JobFlowInstancesConfigProperty.EmrManagedSlaveSecurityGroup``.
            :param hadoop_version: ``CfnCluster.JobFlowInstancesConfigProperty.HadoopVersion``.
            :param keep_job_flow_alive_when_no_steps: ``CfnCluster.JobFlowInstancesConfigProperty.KeepJobFlowAliveWhenNoSteps``.
            :param master_instance_fleet: ``CfnCluster.JobFlowInstancesConfigProperty.MasterInstanceFleet``.
            :param master_instance_group: ``CfnCluster.JobFlowInstancesConfigProperty.MasterInstanceGroup``.
            :param placement: ``CfnCluster.JobFlowInstancesConfigProperty.Placement``.
            :param service_access_security_group: ``CfnCluster.JobFlowInstancesConfigProperty.ServiceAccessSecurityGroup``.
            :param termination_protected: ``CfnCluster.JobFlowInstancesConfigProperty.TerminationProtected``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-jobflowinstancesconfig.html
            """
            self._values = {
            }
            if additional_master_security_groups is not None: self._values["additional_master_security_groups"] = additional_master_security_groups
            if additional_slave_security_groups is not None: self._values["additional_slave_security_groups"] = additional_slave_security_groups
            if core_instance_fleet is not None: self._values["core_instance_fleet"] = core_instance_fleet
            if core_instance_group is not None: self._values["core_instance_group"] = core_instance_group
            if ec2_key_name is not None: self._values["ec2_key_name"] = ec2_key_name
            if ec2_subnet_id is not None: self._values["ec2_subnet_id"] = ec2_subnet_id
            if ec2_subnet_ids is not None: self._values["ec2_subnet_ids"] = ec2_subnet_ids
            if emr_managed_master_security_group is not None: self._values["emr_managed_master_security_group"] = emr_managed_master_security_group
            if emr_managed_slave_security_group is not None: self._values["emr_managed_slave_security_group"] = emr_managed_slave_security_group
            if hadoop_version is not None: self._values["hadoop_version"] = hadoop_version
            if keep_job_flow_alive_when_no_steps is not None: self._values["keep_job_flow_alive_when_no_steps"] = keep_job_flow_alive_when_no_steps
            if master_instance_fleet is not None: self._values["master_instance_fleet"] = master_instance_fleet
            if master_instance_group is not None: self._values["master_instance_group"] = master_instance_group
            if placement is not None: self._values["placement"] = placement
            if service_access_security_group is not None: self._values["service_access_security_group"] = service_access_security_group
            if termination_protected is not None: self._values["termination_protected"] = termination_protected

        @property
        def additional_master_security_groups(self) -> typing.Optional[typing.List[str]]:
            """``CfnCluster.JobFlowInstancesConfigProperty.AdditionalMasterSecurityGroups``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-jobflowinstancesconfig.html#cfn-elasticmapreduce-cluster-jobflowinstancesconfig-additionalmastersecuritygroups
            """
            return self._values.get('additional_master_security_groups')

        @property
        def additional_slave_security_groups(self) -> typing.Optional[typing.List[str]]:
            """``CfnCluster.JobFlowInstancesConfigProperty.AdditionalSlaveSecurityGroups``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-jobflowinstancesconfig.html#cfn-elasticmapreduce-cluster-jobflowinstancesconfig-additionalslavesecuritygroups
            """
            return self._values.get('additional_slave_security_groups')

        @property
        def core_instance_fleet(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnCluster.InstanceFleetConfigProperty"]]]:
            """``CfnCluster.JobFlowInstancesConfigProperty.CoreInstanceFleet``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-jobflowinstancesconfig.html#cfn-elasticmapreduce-cluster-jobflowinstancesconfig-coreinstancefleet
            """
            return self._values.get('core_instance_fleet')

        @property
        def core_instance_group(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnCluster.InstanceGroupConfigProperty"]]]:
            """``CfnCluster.JobFlowInstancesConfigProperty.CoreInstanceGroup``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-jobflowinstancesconfig.html#cfn-elasticmapreduce-cluster-jobflowinstancesconfig-coreinstancegroup
            """
            return self._values.get('core_instance_group')

        @property
        def ec2_key_name(self) -> typing.Optional[str]:
            """``CfnCluster.JobFlowInstancesConfigProperty.Ec2KeyName``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-jobflowinstancesconfig.html#cfn-elasticmapreduce-cluster-jobflowinstancesconfig-ec2keyname
            """
            return self._values.get('ec2_key_name')

        @property
        def ec2_subnet_id(self) -> typing.Optional[str]:
            """``CfnCluster.JobFlowInstancesConfigProperty.Ec2SubnetId``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-jobflowinstancesconfig.html#cfn-elasticmapreduce-cluster-jobflowinstancesconfig-ec2subnetid
            """
            return self._values.get('ec2_subnet_id')

        @property
        def ec2_subnet_ids(self) -> typing.Optional[typing.List[str]]:
            """``CfnCluster.JobFlowInstancesConfigProperty.Ec2SubnetIds``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-jobflowinstancesconfig.html#cfn-elasticmapreduce-cluster-jobflowinstancesconfig-ec2subnetids
            """
            return self._values.get('ec2_subnet_ids')

        @property
        def emr_managed_master_security_group(self) -> typing.Optional[str]:
            """``CfnCluster.JobFlowInstancesConfigProperty.EmrManagedMasterSecurityGroup``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-jobflowinstancesconfig.html#cfn-elasticmapreduce-cluster-jobflowinstancesconfig-emrmanagedmastersecuritygroup
            """
            return self._values.get('emr_managed_master_security_group')

        @property
        def emr_managed_slave_security_group(self) -> typing.Optional[str]:
            """``CfnCluster.JobFlowInstancesConfigProperty.EmrManagedSlaveSecurityGroup``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-jobflowinstancesconfig.html#cfn-elasticmapreduce-cluster-jobflowinstancesconfig-emrmanagedslavesecuritygroup
            """
            return self._values.get('emr_managed_slave_security_group')

        @property
        def hadoop_version(self) -> typing.Optional[str]:
            """``CfnCluster.JobFlowInstancesConfigProperty.HadoopVersion``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-jobflowinstancesconfig.html#cfn-elasticmapreduce-cluster-jobflowinstancesconfig-hadoopversion
            """
            return self._values.get('hadoop_version')

        @property
        def keep_job_flow_alive_when_no_steps(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
            """``CfnCluster.JobFlowInstancesConfigProperty.KeepJobFlowAliveWhenNoSteps``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-jobflowinstancesconfig.html#cfn-elasticmapreduce-cluster-jobflowinstancesconfig-keepjobflowalivewhennosteps
            """
            return self._values.get('keep_job_flow_alive_when_no_steps')

        @property
        def master_instance_fleet(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnCluster.InstanceFleetConfigProperty"]]]:
            """``CfnCluster.JobFlowInstancesConfigProperty.MasterInstanceFleet``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-jobflowinstancesconfig.html#cfn-elasticmapreduce-cluster-jobflowinstancesconfig-masterinstancefleet
            """
            return self._values.get('master_instance_fleet')

        @property
        def master_instance_group(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnCluster.InstanceGroupConfigProperty"]]]:
            """``CfnCluster.JobFlowInstancesConfigProperty.MasterInstanceGroup``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-jobflowinstancesconfig.html#cfn-elasticmapreduce-cluster-jobflowinstancesconfig-masterinstancegroup
            """
            return self._values.get('master_instance_group')

        @property
        def placement(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnCluster.PlacementTypeProperty"]]]:
            """``CfnCluster.JobFlowInstancesConfigProperty.Placement``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-jobflowinstancesconfig.html#cfn-elasticmapreduce-cluster-jobflowinstancesconfig-placement
            """
            return self._values.get('placement')

        @property
        def service_access_security_group(self) -> typing.Optional[str]:
            """``CfnCluster.JobFlowInstancesConfigProperty.ServiceAccessSecurityGroup``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-jobflowinstancesconfig.html#cfn-elasticmapreduce-cluster-jobflowinstancesconfig-serviceaccesssecuritygroup
            """
            return self._values.get('service_access_security_group')

        @property
        def termination_protected(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
            """``CfnCluster.JobFlowInstancesConfigProperty.TerminationProtected``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-jobflowinstancesconfig.html#cfn-elasticmapreduce-cluster-jobflowinstancesconfig-terminationprotected
            """
            return self._values.get('termination_protected')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'JobFlowInstancesConfigProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnCluster.KerberosAttributesProperty", jsii_struct_bases=[], name_mapping={'kdc_admin_password': 'kdcAdminPassword', 'realm': 'realm', 'ad_domain_join_password': 'adDomainJoinPassword', 'ad_domain_join_user': 'adDomainJoinUser', 'cross_realm_trust_principal_password': 'crossRealmTrustPrincipalPassword'})
    class KerberosAttributesProperty():
        def __init__(self, *, kdc_admin_password: str, realm: str, ad_domain_join_password: typing.Optional[str]=None, ad_domain_join_user: typing.Optional[str]=None, cross_realm_trust_principal_password: typing.Optional[str]=None):
            """
            :param kdc_admin_password: ``CfnCluster.KerberosAttributesProperty.KdcAdminPassword``.
            :param realm: ``CfnCluster.KerberosAttributesProperty.Realm``.
            :param ad_domain_join_password: ``CfnCluster.KerberosAttributesProperty.ADDomainJoinPassword``.
            :param ad_domain_join_user: ``CfnCluster.KerberosAttributesProperty.ADDomainJoinUser``.
            :param cross_realm_trust_principal_password: ``CfnCluster.KerberosAttributesProperty.CrossRealmTrustPrincipalPassword``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-kerberosattributes.html
            """
            self._values = {
                'kdc_admin_password': kdc_admin_password,
                'realm': realm,
            }
            if ad_domain_join_password is not None: self._values["ad_domain_join_password"] = ad_domain_join_password
            if ad_domain_join_user is not None: self._values["ad_domain_join_user"] = ad_domain_join_user
            if cross_realm_trust_principal_password is not None: self._values["cross_realm_trust_principal_password"] = cross_realm_trust_principal_password

        @property
        def kdc_admin_password(self) -> str:
            """``CfnCluster.KerberosAttributesProperty.KdcAdminPassword``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-kerberosattributes.html#cfn-elasticmapreduce-cluster-kerberosattributes-kdcadminpassword
            """
            return self._values.get('kdc_admin_password')

        @property
        def realm(self) -> str:
            """``CfnCluster.KerberosAttributesProperty.Realm``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-kerberosattributes.html#cfn-elasticmapreduce-cluster-kerberosattributes-realm
            """
            return self._values.get('realm')

        @property
        def ad_domain_join_password(self) -> typing.Optional[str]:
            """``CfnCluster.KerberosAttributesProperty.ADDomainJoinPassword``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-kerberosattributes.html#cfn-elasticmapreduce-cluster-kerberosattributes-addomainjoinpassword
            """
            return self._values.get('ad_domain_join_password')

        @property
        def ad_domain_join_user(self) -> typing.Optional[str]:
            """``CfnCluster.KerberosAttributesProperty.ADDomainJoinUser``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-kerberosattributes.html#cfn-elasticmapreduce-cluster-kerberosattributes-addomainjoinuser
            """
            return self._values.get('ad_domain_join_user')

        @property
        def cross_realm_trust_principal_password(self) -> typing.Optional[str]:
            """``CfnCluster.KerberosAttributesProperty.CrossRealmTrustPrincipalPassword``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-kerberosattributes.html#cfn-elasticmapreduce-cluster-kerberosattributes-crossrealmtrustprincipalpassword
            """
            return self._values.get('cross_realm_trust_principal_password')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'KerberosAttributesProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnCluster.KeyValueProperty", jsii_struct_bases=[], name_mapping={'key': 'key', 'value': 'value'})
    class KeyValueProperty():
        def __init__(self, *, key: typing.Optional[str]=None, value: typing.Optional[str]=None):
            """
            :param key: ``CfnCluster.KeyValueProperty.Key``.
            :param value: ``CfnCluster.KeyValueProperty.Value``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-keyvalue.html
            """
            self._values = {
            }
            if key is not None: self._values["key"] = key
            if value is not None: self._values["value"] = value

        @property
        def key(self) -> typing.Optional[str]:
            """``CfnCluster.KeyValueProperty.Key``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-keyvalue.html#cfn-elasticmapreduce-cluster-keyvalue-key
            """
            return self._values.get('key')

        @property
        def value(self) -> typing.Optional[str]:
            """``CfnCluster.KeyValueProperty.Value``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-keyvalue.html#cfn-elasticmapreduce-cluster-keyvalue-value
            """
            return self._values.get('value')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'KeyValueProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnCluster.MetricDimensionProperty", jsii_struct_bases=[], name_mapping={'key': 'key', 'value': 'value'})
    class MetricDimensionProperty():
        def __init__(self, *, key: str, value: str):
            """
            :param key: ``CfnCluster.MetricDimensionProperty.Key``.
            :param value: ``CfnCluster.MetricDimensionProperty.Value``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-metricdimension.html
            """
            self._values = {
                'key': key,
                'value': value,
            }

        @property
        def key(self) -> str:
            """``CfnCluster.MetricDimensionProperty.Key``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-metricdimension.html#cfn-elasticmapreduce-cluster-metricdimension-key
            """
            return self._values.get('key')

        @property
        def value(self) -> str:
            """``CfnCluster.MetricDimensionProperty.Value``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-metricdimension.html#cfn-elasticmapreduce-cluster-metricdimension-value
            """
            return self._values.get('value')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'MetricDimensionProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnCluster.PlacementTypeProperty", jsii_struct_bases=[], name_mapping={'availability_zone': 'availabilityZone'})
    class PlacementTypeProperty():
        def __init__(self, *, availability_zone: str):
            """
            :param availability_zone: ``CfnCluster.PlacementTypeProperty.AvailabilityZone``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-placementtype.html
            """
            self._values = {
                'availability_zone': availability_zone,
            }

        @property
        def availability_zone(self) -> str:
            """``CfnCluster.PlacementTypeProperty.AvailabilityZone``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-placementtype.html#cfn-elasticmapreduce-cluster-placementtype-availabilityzone
            """
            return self._values.get('availability_zone')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'PlacementTypeProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnCluster.ScalingActionProperty", jsii_struct_bases=[], name_mapping={'simple_scaling_policy_configuration': 'simpleScalingPolicyConfiguration', 'market': 'market'})
    class ScalingActionProperty():
        def __init__(self, *, simple_scaling_policy_configuration: typing.Union[aws_cdk.core.IResolvable, "CfnCluster.SimpleScalingPolicyConfigurationProperty"], market: typing.Optional[str]=None):
            """
            :param simple_scaling_policy_configuration: ``CfnCluster.ScalingActionProperty.SimpleScalingPolicyConfiguration``.
            :param market: ``CfnCluster.ScalingActionProperty.Market``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-scalingaction.html
            """
            self._values = {
                'simple_scaling_policy_configuration': simple_scaling_policy_configuration,
            }
            if market is not None: self._values["market"] = market

        @property
        def simple_scaling_policy_configuration(self) -> typing.Union[aws_cdk.core.IResolvable, "CfnCluster.SimpleScalingPolicyConfigurationProperty"]:
            """``CfnCluster.ScalingActionProperty.SimpleScalingPolicyConfiguration``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-scalingaction.html#cfn-elasticmapreduce-cluster-scalingaction-simplescalingpolicyconfiguration
            """
            return self._values.get('simple_scaling_policy_configuration')

        @property
        def market(self) -> typing.Optional[str]:
            """``CfnCluster.ScalingActionProperty.Market``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-scalingaction.html#cfn-elasticmapreduce-cluster-scalingaction-market
            """
            return self._values.get('market')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'ScalingActionProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnCluster.ScalingConstraintsProperty", jsii_struct_bases=[], name_mapping={'max_capacity': 'maxCapacity', 'min_capacity': 'minCapacity'})
    class ScalingConstraintsProperty():
        def __init__(self, *, max_capacity: jsii.Number, min_capacity: jsii.Number):
            """
            :param max_capacity: ``CfnCluster.ScalingConstraintsProperty.MaxCapacity``.
            :param min_capacity: ``CfnCluster.ScalingConstraintsProperty.MinCapacity``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-scalingconstraints.html
            """
            self._values = {
                'max_capacity': max_capacity,
                'min_capacity': min_capacity,
            }

        @property
        def max_capacity(self) -> jsii.Number:
            """``CfnCluster.ScalingConstraintsProperty.MaxCapacity``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-scalingconstraints.html#cfn-elasticmapreduce-cluster-scalingconstraints-maxcapacity
            """
            return self._values.get('max_capacity')

        @property
        def min_capacity(self) -> jsii.Number:
            """``CfnCluster.ScalingConstraintsProperty.MinCapacity``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-scalingconstraints.html#cfn-elasticmapreduce-cluster-scalingconstraints-mincapacity
            """
            return self._values.get('min_capacity')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'ScalingConstraintsProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnCluster.ScalingRuleProperty", jsii_struct_bases=[], name_mapping={'action': 'action', 'name': 'name', 'trigger': 'trigger', 'description': 'description'})
    class ScalingRuleProperty():
        def __init__(self, *, action: typing.Union[aws_cdk.core.IResolvable, "CfnCluster.ScalingActionProperty"], name: str, trigger: typing.Union[aws_cdk.core.IResolvable, "CfnCluster.ScalingTriggerProperty"], description: typing.Optional[str]=None):
            """
            :param action: ``CfnCluster.ScalingRuleProperty.Action``.
            :param name: ``CfnCluster.ScalingRuleProperty.Name``.
            :param trigger: ``CfnCluster.ScalingRuleProperty.Trigger``.
            :param description: ``CfnCluster.ScalingRuleProperty.Description``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-scalingrule.html
            """
            self._values = {
                'action': action,
                'name': name,
                'trigger': trigger,
            }
            if description is not None: self._values["description"] = description

        @property
        def action(self) -> typing.Union[aws_cdk.core.IResolvable, "CfnCluster.ScalingActionProperty"]:
            """``CfnCluster.ScalingRuleProperty.Action``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-scalingrule.html#cfn-elasticmapreduce-cluster-scalingrule-action
            """
            return self._values.get('action')

        @property
        def name(self) -> str:
            """``CfnCluster.ScalingRuleProperty.Name``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-scalingrule.html#cfn-elasticmapreduce-cluster-scalingrule-name
            """
            return self._values.get('name')

        @property
        def trigger(self) -> typing.Union[aws_cdk.core.IResolvable, "CfnCluster.ScalingTriggerProperty"]:
            """``CfnCluster.ScalingRuleProperty.Trigger``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-scalingrule.html#cfn-elasticmapreduce-cluster-scalingrule-trigger
            """
            return self._values.get('trigger')

        @property
        def description(self) -> typing.Optional[str]:
            """``CfnCluster.ScalingRuleProperty.Description``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-scalingrule.html#cfn-elasticmapreduce-cluster-scalingrule-description
            """
            return self._values.get('description')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'ScalingRuleProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnCluster.ScalingTriggerProperty", jsii_struct_bases=[], name_mapping={'cloud_watch_alarm_definition': 'cloudWatchAlarmDefinition'})
    class ScalingTriggerProperty():
        def __init__(self, *, cloud_watch_alarm_definition: typing.Union[aws_cdk.core.IResolvable, "CfnCluster.CloudWatchAlarmDefinitionProperty"]):
            """
            :param cloud_watch_alarm_definition: ``CfnCluster.ScalingTriggerProperty.CloudWatchAlarmDefinition``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-scalingtrigger.html
            """
            self._values = {
                'cloud_watch_alarm_definition': cloud_watch_alarm_definition,
            }

        @property
        def cloud_watch_alarm_definition(self) -> typing.Union[aws_cdk.core.IResolvable, "CfnCluster.CloudWatchAlarmDefinitionProperty"]:
            """``CfnCluster.ScalingTriggerProperty.CloudWatchAlarmDefinition``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-scalingtrigger.html#cfn-elasticmapreduce-cluster-scalingtrigger-cloudwatchalarmdefinition
            """
            return self._values.get('cloud_watch_alarm_definition')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'ScalingTriggerProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnCluster.ScriptBootstrapActionConfigProperty", jsii_struct_bases=[], name_mapping={'path': 'path', 'args': 'args'})
    class ScriptBootstrapActionConfigProperty():
        def __init__(self, *, path: str, args: typing.Optional[typing.List[str]]=None):
            """
            :param path: ``CfnCluster.ScriptBootstrapActionConfigProperty.Path``.
            :param args: ``CfnCluster.ScriptBootstrapActionConfigProperty.Args``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-scriptbootstrapactionconfig.html
            """
            self._values = {
                'path': path,
            }
            if args is not None: self._values["args"] = args

        @property
        def path(self) -> str:
            """``CfnCluster.ScriptBootstrapActionConfigProperty.Path``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-scriptbootstrapactionconfig.html#cfn-elasticmapreduce-cluster-scriptbootstrapactionconfig-path
            """
            return self._values.get('path')

        @property
        def args(self) -> typing.Optional[typing.List[str]]:
            """``CfnCluster.ScriptBootstrapActionConfigProperty.Args``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-scriptbootstrapactionconfig.html#cfn-elasticmapreduce-cluster-scriptbootstrapactionconfig-args
            """
            return self._values.get('args')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'ScriptBootstrapActionConfigProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnCluster.SimpleScalingPolicyConfigurationProperty", jsii_struct_bases=[], name_mapping={'scaling_adjustment': 'scalingAdjustment', 'adjustment_type': 'adjustmentType', 'cool_down': 'coolDown'})
    class SimpleScalingPolicyConfigurationProperty():
        def __init__(self, *, scaling_adjustment: jsii.Number, adjustment_type: typing.Optional[str]=None, cool_down: typing.Optional[jsii.Number]=None):
            """
            :param scaling_adjustment: ``CfnCluster.SimpleScalingPolicyConfigurationProperty.ScalingAdjustment``.
            :param adjustment_type: ``CfnCluster.SimpleScalingPolicyConfigurationProperty.AdjustmentType``.
            :param cool_down: ``CfnCluster.SimpleScalingPolicyConfigurationProperty.CoolDown``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-simplescalingpolicyconfiguration.html
            """
            self._values = {
                'scaling_adjustment': scaling_adjustment,
            }
            if adjustment_type is not None: self._values["adjustment_type"] = adjustment_type
            if cool_down is not None: self._values["cool_down"] = cool_down

        @property
        def scaling_adjustment(self) -> jsii.Number:
            """``CfnCluster.SimpleScalingPolicyConfigurationProperty.ScalingAdjustment``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-simplescalingpolicyconfiguration.html#cfn-elasticmapreduce-cluster-simplescalingpolicyconfiguration-scalingadjustment
            """
            return self._values.get('scaling_adjustment')

        @property
        def adjustment_type(self) -> typing.Optional[str]:
            """``CfnCluster.SimpleScalingPolicyConfigurationProperty.AdjustmentType``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-simplescalingpolicyconfiguration.html#cfn-elasticmapreduce-cluster-simplescalingpolicyconfiguration-adjustmenttype
            """
            return self._values.get('adjustment_type')

        @property
        def cool_down(self) -> typing.Optional[jsii.Number]:
            """``CfnCluster.SimpleScalingPolicyConfigurationProperty.CoolDown``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-simplescalingpolicyconfiguration.html#cfn-elasticmapreduce-cluster-simplescalingpolicyconfiguration-cooldown
            """
            return self._values.get('cool_down')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'SimpleScalingPolicyConfigurationProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnCluster.SpotProvisioningSpecificationProperty", jsii_struct_bases=[], name_mapping={'timeout_action': 'timeoutAction', 'timeout_duration_minutes': 'timeoutDurationMinutes', 'block_duration_minutes': 'blockDurationMinutes'})
    class SpotProvisioningSpecificationProperty():
        def __init__(self, *, timeout_action: str, timeout_duration_minutes: jsii.Number, block_duration_minutes: typing.Optional[jsii.Number]=None):
            """
            :param timeout_action: ``CfnCluster.SpotProvisioningSpecificationProperty.TimeoutAction``.
            :param timeout_duration_minutes: ``CfnCluster.SpotProvisioningSpecificationProperty.TimeoutDurationMinutes``.
            :param block_duration_minutes: ``CfnCluster.SpotProvisioningSpecificationProperty.BlockDurationMinutes``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-spotprovisioningspecification.html
            """
            self._values = {
                'timeout_action': timeout_action,
                'timeout_duration_minutes': timeout_duration_minutes,
            }
            if block_duration_minutes is not None: self._values["block_duration_minutes"] = block_duration_minutes

        @property
        def timeout_action(self) -> str:
            """``CfnCluster.SpotProvisioningSpecificationProperty.TimeoutAction``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-spotprovisioningspecification.html#cfn-elasticmapreduce-cluster-spotprovisioningspecification-timeoutaction
            """
            return self._values.get('timeout_action')

        @property
        def timeout_duration_minutes(self) -> jsii.Number:
            """``CfnCluster.SpotProvisioningSpecificationProperty.TimeoutDurationMinutes``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-spotprovisioningspecification.html#cfn-elasticmapreduce-cluster-spotprovisioningspecification-timeoutdurationminutes
            """
            return self._values.get('timeout_duration_minutes')

        @property
        def block_duration_minutes(self) -> typing.Optional[jsii.Number]:
            """``CfnCluster.SpotProvisioningSpecificationProperty.BlockDurationMinutes``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-spotprovisioningspecification.html#cfn-elasticmapreduce-cluster-spotprovisioningspecification-blockdurationminutes
            """
            return self._values.get('block_duration_minutes')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'SpotProvisioningSpecificationProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnCluster.StepConfigProperty", jsii_struct_bases=[], name_mapping={'hadoop_jar_step': 'hadoopJarStep', 'name': 'name', 'action_on_failure': 'actionOnFailure'})
    class StepConfigProperty():
        def __init__(self, *, hadoop_jar_step: typing.Union[aws_cdk.core.IResolvable, "CfnCluster.HadoopJarStepConfigProperty"], name: str, action_on_failure: typing.Optional[str]=None):
            """
            :param hadoop_jar_step: ``CfnCluster.StepConfigProperty.HadoopJarStep``.
            :param name: ``CfnCluster.StepConfigProperty.Name``.
            :param action_on_failure: ``CfnCluster.StepConfigProperty.ActionOnFailure``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-stepconfig.html
            """
            self._values = {
                'hadoop_jar_step': hadoop_jar_step,
                'name': name,
            }
            if action_on_failure is not None: self._values["action_on_failure"] = action_on_failure

        @property
        def hadoop_jar_step(self) -> typing.Union[aws_cdk.core.IResolvable, "CfnCluster.HadoopJarStepConfigProperty"]:
            """``CfnCluster.StepConfigProperty.HadoopJarStep``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-stepconfig.html#cfn-elasticmapreduce-cluster-stepconfig-hadoopjarstep
            """
            return self._values.get('hadoop_jar_step')

        @property
        def name(self) -> str:
            """``CfnCluster.StepConfigProperty.Name``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-stepconfig.html#cfn-elasticmapreduce-cluster-stepconfig-name
            """
            return self._values.get('name')

        @property
        def action_on_failure(self) -> typing.Optional[str]:
            """``CfnCluster.StepConfigProperty.ActionOnFailure``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-stepconfig.html#cfn-elasticmapreduce-cluster-stepconfig-actiononfailure
            """
            return self._values.get('action_on_failure')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'StepConfigProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnCluster.VolumeSpecificationProperty", jsii_struct_bases=[], name_mapping={'size_in_gb': 'sizeInGb', 'volume_type': 'volumeType', 'iops': 'iops'})
    class VolumeSpecificationProperty():
        def __init__(self, *, size_in_gb: jsii.Number, volume_type: str, iops: typing.Optional[jsii.Number]=None):
            """
            :param size_in_gb: ``CfnCluster.VolumeSpecificationProperty.SizeInGB``.
            :param volume_type: ``CfnCluster.VolumeSpecificationProperty.VolumeType``.
            :param iops: ``CfnCluster.VolumeSpecificationProperty.Iops``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-volumespecification.html
            """
            self._values = {
                'size_in_gb': size_in_gb,
                'volume_type': volume_type,
            }
            if iops is not None: self._values["iops"] = iops

        @property
        def size_in_gb(self) -> jsii.Number:
            """``CfnCluster.VolumeSpecificationProperty.SizeInGB``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-volumespecification.html#cfn-elasticmapreduce-cluster-volumespecification-sizeingb
            """
            return self._values.get('size_in_gb')

        @property
        def volume_type(self) -> str:
            """``CfnCluster.VolumeSpecificationProperty.VolumeType``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-volumespecification.html#cfn-elasticmapreduce-cluster-volumespecification-volumetype
            """
            return self._values.get('volume_type')

        @property
        def iops(self) -> typing.Optional[jsii.Number]:
            """``CfnCluster.VolumeSpecificationProperty.Iops``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-volumespecification.html#cfn-elasticmapreduce-cluster-volumespecification-iops
            """
            return self._values.get('iops')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'VolumeSpecificationProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



@jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnClusterProps", jsii_struct_bases=[], name_mapping={'instances': 'instances', 'job_flow_role': 'jobFlowRole', 'name': 'name', 'service_role': 'serviceRole', 'additional_info': 'additionalInfo', 'applications': 'applications', 'auto_scaling_role': 'autoScalingRole', 'bootstrap_actions': 'bootstrapActions', 'configurations': 'configurations', 'custom_ami_id': 'customAmiId', 'ebs_root_volume_size': 'ebsRootVolumeSize', 'kerberos_attributes': 'kerberosAttributes', 'log_uri': 'logUri', 'release_label': 'releaseLabel', 'scale_down_behavior': 'scaleDownBehavior', 'security_configuration': 'securityConfiguration', 'steps': 'steps', 'tags': 'tags', 'visible_to_all_users': 'visibleToAllUsers'})
class CfnClusterProps():
    def __init__(self, *, instances: typing.Union["CfnCluster.JobFlowInstancesConfigProperty", aws_cdk.core.IResolvable], job_flow_role: str, name: str, service_role: str, additional_info: typing.Any=None, applications: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnCluster.ApplicationProperty"]]]]]=None, auto_scaling_role: typing.Optional[str]=None, bootstrap_actions: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnCluster.BootstrapActionConfigProperty"]]]]]=None, configurations: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnCluster.ConfigurationProperty"]]]]]=None, custom_ami_id: typing.Optional[str]=None, ebs_root_volume_size: typing.Optional[jsii.Number]=None, kerberos_attributes: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnCluster.KerberosAttributesProperty"]]]=None, log_uri: typing.Optional[str]=None, release_label: typing.Optional[str]=None, scale_down_behavior: typing.Optional[str]=None, security_configuration: typing.Optional[str]=None, steps: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnCluster.StepConfigProperty"]]]]]=None, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None, visible_to_all_users: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None):
        """Properties for defining a ``AWS::EMR::Cluster``.

        :param instances: ``AWS::EMR::Cluster.Instances``.
        :param job_flow_role: ``AWS::EMR::Cluster.JobFlowRole``.
        :param name: ``AWS::EMR::Cluster.Name``.
        :param service_role: ``AWS::EMR::Cluster.ServiceRole``.
        :param additional_info: ``AWS::EMR::Cluster.AdditionalInfo``.
        :param applications: ``AWS::EMR::Cluster.Applications``.
        :param auto_scaling_role: ``AWS::EMR::Cluster.AutoScalingRole``.
        :param bootstrap_actions: ``AWS::EMR::Cluster.BootstrapActions``.
        :param configurations: ``AWS::EMR::Cluster.Configurations``.
        :param custom_ami_id: ``AWS::EMR::Cluster.CustomAmiId``.
        :param ebs_root_volume_size: ``AWS::EMR::Cluster.EbsRootVolumeSize``.
        :param kerberos_attributes: ``AWS::EMR::Cluster.KerberosAttributes``.
        :param log_uri: ``AWS::EMR::Cluster.LogUri``.
        :param release_label: ``AWS::EMR::Cluster.ReleaseLabel``.
        :param scale_down_behavior: ``AWS::EMR::Cluster.ScaleDownBehavior``.
        :param security_configuration: ``AWS::EMR::Cluster.SecurityConfiguration``.
        :param steps: ``AWS::EMR::Cluster.Steps``.
        :param tags: ``AWS::EMR::Cluster.Tags``.
        :param visible_to_all_users: ``AWS::EMR::Cluster.VisibleToAllUsers``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-cluster.html
        """
        self._values = {
            'instances': instances,
            'job_flow_role': job_flow_role,
            'name': name,
            'service_role': service_role,
        }
        if additional_info is not None: self._values["additional_info"] = additional_info
        if applications is not None: self._values["applications"] = applications
        if auto_scaling_role is not None: self._values["auto_scaling_role"] = auto_scaling_role
        if bootstrap_actions is not None: self._values["bootstrap_actions"] = bootstrap_actions
        if configurations is not None: self._values["configurations"] = configurations
        if custom_ami_id is not None: self._values["custom_ami_id"] = custom_ami_id
        if ebs_root_volume_size is not None: self._values["ebs_root_volume_size"] = ebs_root_volume_size
        if kerberos_attributes is not None: self._values["kerberos_attributes"] = kerberos_attributes
        if log_uri is not None: self._values["log_uri"] = log_uri
        if release_label is not None: self._values["release_label"] = release_label
        if scale_down_behavior is not None: self._values["scale_down_behavior"] = scale_down_behavior
        if security_configuration is not None: self._values["security_configuration"] = security_configuration
        if steps is not None: self._values["steps"] = steps
        if tags is not None: self._values["tags"] = tags
        if visible_to_all_users is not None: self._values["visible_to_all_users"] = visible_to_all_users

    @property
    def instances(self) -> typing.Union["CfnCluster.JobFlowInstancesConfigProperty", aws_cdk.core.IResolvable]:
        """``AWS::EMR::Cluster.Instances``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-cluster.html#cfn-elasticmapreduce-cluster-instances
        """
        return self._values.get('instances')

    @property
    def job_flow_role(self) -> str:
        """``AWS::EMR::Cluster.JobFlowRole``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-cluster.html#cfn-elasticmapreduce-cluster-jobflowrole
        """
        return self._values.get('job_flow_role')

    @property
    def name(self) -> str:
        """``AWS::EMR::Cluster.Name``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-cluster.html#cfn-elasticmapreduce-cluster-name
        """
        return self._values.get('name')

    @property
    def service_role(self) -> str:
        """``AWS::EMR::Cluster.ServiceRole``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-cluster.html#cfn-elasticmapreduce-cluster-servicerole
        """
        return self._values.get('service_role')

    @property
    def additional_info(self) -> typing.Any:
        """``AWS::EMR::Cluster.AdditionalInfo``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-cluster.html#cfn-elasticmapreduce-cluster-additionalinfo
        """
        return self._values.get('additional_info')

    @property
    def applications(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnCluster.ApplicationProperty"]]]]]:
        """``AWS::EMR::Cluster.Applications``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-cluster.html#cfn-elasticmapreduce-cluster-applications
        """
        return self._values.get('applications')

    @property
    def auto_scaling_role(self) -> typing.Optional[str]:
        """``AWS::EMR::Cluster.AutoScalingRole``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-cluster.html#cfn-elasticmapreduce-cluster-autoscalingrole
        """
        return self._values.get('auto_scaling_role')

    @property
    def bootstrap_actions(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnCluster.BootstrapActionConfigProperty"]]]]]:
        """``AWS::EMR::Cluster.BootstrapActions``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-cluster.html#cfn-elasticmapreduce-cluster-bootstrapactions
        """
        return self._values.get('bootstrap_actions')

    @property
    def configurations(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnCluster.ConfigurationProperty"]]]]]:
        """``AWS::EMR::Cluster.Configurations``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-cluster.html#cfn-elasticmapreduce-cluster-configurations
        """
        return self._values.get('configurations')

    @property
    def custom_ami_id(self) -> typing.Optional[str]:
        """``AWS::EMR::Cluster.CustomAmiId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-cluster.html#cfn-elasticmapreduce-cluster-customamiid
        """
        return self._values.get('custom_ami_id')

    @property
    def ebs_root_volume_size(self) -> typing.Optional[jsii.Number]:
        """``AWS::EMR::Cluster.EbsRootVolumeSize``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-cluster.html#cfn-elasticmapreduce-cluster-ebsrootvolumesize
        """
        return self._values.get('ebs_root_volume_size')

    @property
    def kerberos_attributes(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnCluster.KerberosAttributesProperty"]]]:
        """``AWS::EMR::Cluster.KerberosAttributes``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-cluster.html#cfn-elasticmapreduce-cluster-kerberosattributes
        """
        return self._values.get('kerberos_attributes')

    @property
    def log_uri(self) -> typing.Optional[str]:
        """``AWS::EMR::Cluster.LogUri``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-cluster.html#cfn-elasticmapreduce-cluster-loguri
        """
        return self._values.get('log_uri')

    @property
    def release_label(self) -> typing.Optional[str]:
        """``AWS::EMR::Cluster.ReleaseLabel``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-cluster.html#cfn-elasticmapreduce-cluster-releaselabel
        """
        return self._values.get('release_label')

    @property
    def scale_down_behavior(self) -> typing.Optional[str]:
        """``AWS::EMR::Cluster.ScaleDownBehavior``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-cluster.html#cfn-elasticmapreduce-cluster-scaledownbehavior
        """
        return self._values.get('scale_down_behavior')

    @property
    def security_configuration(self) -> typing.Optional[str]:
        """``AWS::EMR::Cluster.SecurityConfiguration``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-cluster.html#cfn-elasticmapreduce-cluster-securityconfiguration
        """
        return self._values.get('security_configuration')

    @property
    def steps(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnCluster.StepConfigProperty"]]]]]:
        """``AWS::EMR::Cluster.Steps``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-cluster.html#cfn-elasticmapreduce-cluster-steps
        """
        return self._values.get('steps')

    @property
    def tags(self) -> typing.Optional[typing.List[aws_cdk.core.CfnTag]]:
        """``AWS::EMR::Cluster.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-cluster.html#cfn-elasticmapreduce-cluster-tags
        """
        return self._values.get('tags')

    @property
    def visible_to_all_users(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::EMR::Cluster.VisibleToAllUsers``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-cluster.html#cfn-elasticmapreduce-cluster-visibletoallusers
        """
        return self._values.get('visible_to_all_users')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnClusterProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnInstanceFleetConfig(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-emr.CfnInstanceFleetConfig"):
    """A CloudFormation ``AWS::EMR::InstanceFleetConfig``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-instancefleetconfig.html
    cloudformationResource:
    :cloudformationResource:: AWS::EMR::InstanceFleetConfig
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, cluster_id: str, instance_fleet_type: str, instance_type_configs: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "InstanceTypeConfigProperty"]]]]]=None, launch_specifications: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["InstanceFleetProvisioningSpecificationsProperty"]]]=None, name: typing.Optional[str]=None, target_on_demand_capacity: typing.Optional[jsii.Number]=None, target_spot_capacity: typing.Optional[jsii.Number]=None) -> None:
        """Create a new ``AWS::EMR::InstanceFleetConfig``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param cluster_id: ``AWS::EMR::InstanceFleetConfig.ClusterId``.
        :param instance_fleet_type: ``AWS::EMR::InstanceFleetConfig.InstanceFleetType``.
        :param instance_type_configs: ``AWS::EMR::InstanceFleetConfig.InstanceTypeConfigs``.
        :param launch_specifications: ``AWS::EMR::InstanceFleetConfig.LaunchSpecifications``.
        :param name: ``AWS::EMR::InstanceFleetConfig.Name``.
        :param target_on_demand_capacity: ``AWS::EMR::InstanceFleetConfig.TargetOnDemandCapacity``.
        :param target_spot_capacity: ``AWS::EMR::InstanceFleetConfig.TargetSpotCapacity``.
        """
        props = CfnInstanceFleetConfigProps(cluster_id=cluster_id, instance_fleet_type=instance_fleet_type, instance_type_configs=instance_type_configs, launch_specifications=launch_specifications, name=name, target_on_demand_capacity=target_on_demand_capacity, target_spot_capacity=target_spot_capacity)

        jsii.create(CfnInstanceFleetConfig, self, [scope, id, props])

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
    @jsii.member(jsii_name="clusterId")
    def cluster_id(self) -> str:
        """``AWS::EMR::InstanceFleetConfig.ClusterId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-instancefleetconfig.html#cfn-elasticmapreduce-instancefleetconfig-clusterid
        """
        return jsii.get(self, "clusterId")

    @cluster_id.setter
    def cluster_id(self, value: str):
        return jsii.set(self, "clusterId", value)

    @property
    @jsii.member(jsii_name="instanceFleetType")
    def instance_fleet_type(self) -> str:
        """``AWS::EMR::InstanceFleetConfig.InstanceFleetType``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-instancefleetconfig.html#cfn-elasticmapreduce-instancefleetconfig-instancefleettype
        """
        return jsii.get(self, "instanceFleetType")

    @instance_fleet_type.setter
    def instance_fleet_type(self, value: str):
        return jsii.set(self, "instanceFleetType", value)

    @property
    @jsii.member(jsii_name="instanceTypeConfigs")
    def instance_type_configs(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "InstanceTypeConfigProperty"]]]]]:
        """``AWS::EMR::InstanceFleetConfig.InstanceTypeConfigs``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-instancefleetconfig.html#cfn-elasticmapreduce-instancefleetconfig-instancetypeconfigs
        """
        return jsii.get(self, "instanceTypeConfigs")

    @instance_type_configs.setter
    def instance_type_configs(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "InstanceTypeConfigProperty"]]]]]):
        return jsii.set(self, "instanceTypeConfigs", value)

    @property
    @jsii.member(jsii_name="launchSpecifications")
    def launch_specifications(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["InstanceFleetProvisioningSpecificationsProperty"]]]:
        """``AWS::EMR::InstanceFleetConfig.LaunchSpecifications``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-instancefleetconfig.html#cfn-elasticmapreduce-instancefleetconfig-launchspecifications
        """
        return jsii.get(self, "launchSpecifications")

    @launch_specifications.setter
    def launch_specifications(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["InstanceFleetProvisioningSpecificationsProperty"]]]):
        return jsii.set(self, "launchSpecifications", value)

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[str]:
        """``AWS::EMR::InstanceFleetConfig.Name``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-instancefleetconfig.html#cfn-elasticmapreduce-instancefleetconfig-name
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: typing.Optional[str]):
        return jsii.set(self, "name", value)

    @property
    @jsii.member(jsii_name="targetOnDemandCapacity")
    def target_on_demand_capacity(self) -> typing.Optional[jsii.Number]:
        """``AWS::EMR::InstanceFleetConfig.TargetOnDemandCapacity``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-instancefleetconfig.html#cfn-elasticmapreduce-instancefleetconfig-targetondemandcapacity
        """
        return jsii.get(self, "targetOnDemandCapacity")

    @target_on_demand_capacity.setter
    def target_on_demand_capacity(self, value: typing.Optional[jsii.Number]):
        return jsii.set(self, "targetOnDemandCapacity", value)

    @property
    @jsii.member(jsii_name="targetSpotCapacity")
    def target_spot_capacity(self) -> typing.Optional[jsii.Number]:
        """``AWS::EMR::InstanceFleetConfig.TargetSpotCapacity``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-instancefleetconfig.html#cfn-elasticmapreduce-instancefleetconfig-targetspotcapacity
        """
        return jsii.get(self, "targetSpotCapacity")

    @target_spot_capacity.setter
    def target_spot_capacity(self, value: typing.Optional[jsii.Number]):
        return jsii.set(self, "targetSpotCapacity", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnInstanceFleetConfig.ConfigurationProperty", jsii_struct_bases=[], name_mapping={'classification': 'classification', 'configuration_properties': 'configurationProperties', 'configurations': 'configurations'})
    class ConfigurationProperty():
        def __init__(self, *, classification: typing.Optional[str]=None, configuration_properties: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.Mapping[str,str]]]]=None, configurations: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnInstanceFleetConfig.ConfigurationProperty"]]]]]=None):
            """
            :param classification: ``CfnInstanceFleetConfig.ConfigurationProperty.Classification``.
            :param configuration_properties: ``CfnInstanceFleetConfig.ConfigurationProperty.ConfigurationProperties``.
            :param configurations: ``CfnInstanceFleetConfig.ConfigurationProperty.Configurations``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancefleetconfig-configuration.html
            """
            self._values = {
            }
            if classification is not None: self._values["classification"] = classification
            if configuration_properties is not None: self._values["configuration_properties"] = configuration_properties
            if configurations is not None: self._values["configurations"] = configurations

        @property
        def classification(self) -> typing.Optional[str]:
            """``CfnInstanceFleetConfig.ConfigurationProperty.Classification``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancefleetconfig-configuration.html#cfn-elasticmapreduce-instancefleetconfig-configuration-classification
            """
            return self._values.get('classification')

        @property
        def configuration_properties(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.Mapping[str,str]]]]:
            """``CfnInstanceFleetConfig.ConfigurationProperty.ConfigurationProperties``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancefleetconfig-configuration.html#cfn-elasticmapreduce-instancefleetconfig-configuration-configurationproperties
            """
            return self._values.get('configuration_properties')

        @property
        def configurations(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnInstanceFleetConfig.ConfigurationProperty"]]]]]:
            """``CfnInstanceFleetConfig.ConfigurationProperty.Configurations``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancefleetconfig-configuration.html#cfn-elasticmapreduce-instancefleetconfig-configuration-configurations
            """
            return self._values.get('configurations')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'ConfigurationProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnInstanceFleetConfig.EbsBlockDeviceConfigProperty", jsii_struct_bases=[], name_mapping={'volume_specification': 'volumeSpecification', 'volumes_per_instance': 'volumesPerInstance'})
    class EbsBlockDeviceConfigProperty():
        def __init__(self, *, volume_specification: typing.Union[aws_cdk.core.IResolvable, "CfnInstanceFleetConfig.VolumeSpecificationProperty"], volumes_per_instance: typing.Optional[jsii.Number]=None):
            """
            :param volume_specification: ``CfnInstanceFleetConfig.EbsBlockDeviceConfigProperty.VolumeSpecification``.
            :param volumes_per_instance: ``CfnInstanceFleetConfig.EbsBlockDeviceConfigProperty.VolumesPerInstance``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancefleetconfig-ebsblockdeviceconfig.html
            """
            self._values = {
                'volume_specification': volume_specification,
            }
            if volumes_per_instance is not None: self._values["volumes_per_instance"] = volumes_per_instance

        @property
        def volume_specification(self) -> typing.Union[aws_cdk.core.IResolvable, "CfnInstanceFleetConfig.VolumeSpecificationProperty"]:
            """``CfnInstanceFleetConfig.EbsBlockDeviceConfigProperty.VolumeSpecification``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancefleetconfig-ebsblockdeviceconfig.html#cfn-elasticmapreduce-instancefleetconfig-ebsblockdeviceconfig-volumespecification
            """
            return self._values.get('volume_specification')

        @property
        def volumes_per_instance(self) -> typing.Optional[jsii.Number]:
            """``CfnInstanceFleetConfig.EbsBlockDeviceConfigProperty.VolumesPerInstance``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancefleetconfig-ebsblockdeviceconfig.html#cfn-elasticmapreduce-instancefleetconfig-ebsblockdeviceconfig-volumesperinstance
            """
            return self._values.get('volumes_per_instance')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'EbsBlockDeviceConfigProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnInstanceFleetConfig.EbsConfigurationProperty", jsii_struct_bases=[], name_mapping={'ebs_block_device_configs': 'ebsBlockDeviceConfigs', 'ebs_optimized': 'ebsOptimized'})
    class EbsConfigurationProperty():
        def __init__(self, *, ebs_block_device_configs: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnInstanceFleetConfig.EbsBlockDeviceConfigProperty"]]]]]=None, ebs_optimized: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None):
            """
            :param ebs_block_device_configs: ``CfnInstanceFleetConfig.EbsConfigurationProperty.EbsBlockDeviceConfigs``.
            :param ebs_optimized: ``CfnInstanceFleetConfig.EbsConfigurationProperty.EbsOptimized``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancefleetconfig-ebsconfiguration.html
            """
            self._values = {
            }
            if ebs_block_device_configs is not None: self._values["ebs_block_device_configs"] = ebs_block_device_configs
            if ebs_optimized is not None: self._values["ebs_optimized"] = ebs_optimized

        @property
        def ebs_block_device_configs(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnInstanceFleetConfig.EbsBlockDeviceConfigProperty"]]]]]:
            """``CfnInstanceFleetConfig.EbsConfigurationProperty.EbsBlockDeviceConfigs``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancefleetconfig-ebsconfiguration.html#cfn-elasticmapreduce-instancefleetconfig-ebsconfiguration-ebsblockdeviceconfigs
            """
            return self._values.get('ebs_block_device_configs')

        @property
        def ebs_optimized(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
            """``CfnInstanceFleetConfig.EbsConfigurationProperty.EbsOptimized``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancefleetconfig-ebsconfiguration.html#cfn-elasticmapreduce-instancefleetconfig-ebsconfiguration-ebsoptimized
            """
            return self._values.get('ebs_optimized')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'EbsConfigurationProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnInstanceFleetConfig.InstanceFleetProvisioningSpecificationsProperty", jsii_struct_bases=[], name_mapping={'spot_specification': 'spotSpecification'})
    class InstanceFleetProvisioningSpecificationsProperty():
        def __init__(self, *, spot_specification: typing.Union[aws_cdk.core.IResolvable, "CfnInstanceFleetConfig.SpotProvisioningSpecificationProperty"]):
            """
            :param spot_specification: ``CfnInstanceFleetConfig.InstanceFleetProvisioningSpecificationsProperty.SpotSpecification``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancefleetconfig-instancefleetprovisioningspecifications.html
            """
            self._values = {
                'spot_specification': spot_specification,
            }

        @property
        def spot_specification(self) -> typing.Union[aws_cdk.core.IResolvable, "CfnInstanceFleetConfig.SpotProvisioningSpecificationProperty"]:
            """``CfnInstanceFleetConfig.InstanceFleetProvisioningSpecificationsProperty.SpotSpecification``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancefleetconfig-instancefleetprovisioningspecifications.html#cfn-elasticmapreduce-instancefleetconfig-instancefleetprovisioningspecifications-spotspecification
            """
            return self._values.get('spot_specification')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'InstanceFleetProvisioningSpecificationsProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnInstanceFleetConfig.InstanceTypeConfigProperty", jsii_struct_bases=[], name_mapping={'instance_type': 'instanceType', 'bid_price': 'bidPrice', 'bid_price_as_percentage_of_on_demand_price': 'bidPriceAsPercentageOfOnDemandPrice', 'configurations': 'configurations', 'ebs_configuration': 'ebsConfiguration', 'weighted_capacity': 'weightedCapacity'})
    class InstanceTypeConfigProperty():
        def __init__(self, *, instance_type: str, bid_price: typing.Optional[str]=None, bid_price_as_percentage_of_on_demand_price: typing.Optional[jsii.Number]=None, configurations: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnInstanceFleetConfig.ConfigurationProperty"]]]]]=None, ebs_configuration: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnInstanceFleetConfig.EbsConfigurationProperty"]]]=None, weighted_capacity: typing.Optional[jsii.Number]=None):
            """
            :param instance_type: ``CfnInstanceFleetConfig.InstanceTypeConfigProperty.InstanceType``.
            :param bid_price: ``CfnInstanceFleetConfig.InstanceTypeConfigProperty.BidPrice``.
            :param bid_price_as_percentage_of_on_demand_price: ``CfnInstanceFleetConfig.InstanceTypeConfigProperty.BidPriceAsPercentageOfOnDemandPrice``.
            :param configurations: ``CfnInstanceFleetConfig.InstanceTypeConfigProperty.Configurations``.
            :param ebs_configuration: ``CfnInstanceFleetConfig.InstanceTypeConfigProperty.EbsConfiguration``.
            :param weighted_capacity: ``CfnInstanceFleetConfig.InstanceTypeConfigProperty.WeightedCapacity``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancefleetconfig-instancetypeconfig.html
            """
            self._values = {
                'instance_type': instance_type,
            }
            if bid_price is not None: self._values["bid_price"] = bid_price
            if bid_price_as_percentage_of_on_demand_price is not None: self._values["bid_price_as_percentage_of_on_demand_price"] = bid_price_as_percentage_of_on_demand_price
            if configurations is not None: self._values["configurations"] = configurations
            if ebs_configuration is not None: self._values["ebs_configuration"] = ebs_configuration
            if weighted_capacity is not None: self._values["weighted_capacity"] = weighted_capacity

        @property
        def instance_type(self) -> str:
            """``CfnInstanceFleetConfig.InstanceTypeConfigProperty.InstanceType``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancefleetconfig-instancetypeconfig.html#cfn-elasticmapreduce-instancefleetconfig-instancetypeconfig-instancetype
            """
            return self._values.get('instance_type')

        @property
        def bid_price(self) -> typing.Optional[str]:
            """``CfnInstanceFleetConfig.InstanceTypeConfigProperty.BidPrice``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancefleetconfig-instancetypeconfig.html#cfn-elasticmapreduce-instancefleetconfig-instancetypeconfig-bidprice
            """
            return self._values.get('bid_price')

        @property
        def bid_price_as_percentage_of_on_demand_price(self) -> typing.Optional[jsii.Number]:
            """``CfnInstanceFleetConfig.InstanceTypeConfigProperty.BidPriceAsPercentageOfOnDemandPrice``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancefleetconfig-instancetypeconfig.html#cfn-elasticmapreduce-instancefleetconfig-instancetypeconfig-bidpriceaspercentageofondemandprice
            """
            return self._values.get('bid_price_as_percentage_of_on_demand_price')

        @property
        def configurations(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnInstanceFleetConfig.ConfigurationProperty"]]]]]:
            """``CfnInstanceFleetConfig.InstanceTypeConfigProperty.Configurations``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancefleetconfig-instancetypeconfig.html#cfn-elasticmapreduce-instancefleetconfig-instancetypeconfig-configurations
            """
            return self._values.get('configurations')

        @property
        def ebs_configuration(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnInstanceFleetConfig.EbsConfigurationProperty"]]]:
            """``CfnInstanceFleetConfig.InstanceTypeConfigProperty.EbsConfiguration``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancefleetconfig-instancetypeconfig.html#cfn-elasticmapreduce-instancefleetconfig-instancetypeconfig-ebsconfiguration
            """
            return self._values.get('ebs_configuration')

        @property
        def weighted_capacity(self) -> typing.Optional[jsii.Number]:
            """``CfnInstanceFleetConfig.InstanceTypeConfigProperty.WeightedCapacity``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancefleetconfig-instancetypeconfig.html#cfn-elasticmapreduce-instancefleetconfig-instancetypeconfig-weightedcapacity
            """
            return self._values.get('weighted_capacity')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'InstanceTypeConfigProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnInstanceFleetConfig.SpotProvisioningSpecificationProperty", jsii_struct_bases=[], name_mapping={'timeout_action': 'timeoutAction', 'timeout_duration_minutes': 'timeoutDurationMinutes', 'block_duration_minutes': 'blockDurationMinutes'})
    class SpotProvisioningSpecificationProperty():
        def __init__(self, *, timeout_action: str, timeout_duration_minutes: jsii.Number, block_duration_minutes: typing.Optional[jsii.Number]=None):
            """
            :param timeout_action: ``CfnInstanceFleetConfig.SpotProvisioningSpecificationProperty.TimeoutAction``.
            :param timeout_duration_minutes: ``CfnInstanceFleetConfig.SpotProvisioningSpecificationProperty.TimeoutDurationMinutes``.
            :param block_duration_minutes: ``CfnInstanceFleetConfig.SpotProvisioningSpecificationProperty.BlockDurationMinutes``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancefleetconfig-spotprovisioningspecification.html
            """
            self._values = {
                'timeout_action': timeout_action,
                'timeout_duration_minutes': timeout_duration_minutes,
            }
            if block_duration_minutes is not None: self._values["block_duration_minutes"] = block_duration_minutes

        @property
        def timeout_action(self) -> str:
            """``CfnInstanceFleetConfig.SpotProvisioningSpecificationProperty.TimeoutAction``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancefleetconfig-spotprovisioningspecification.html#cfn-elasticmapreduce-instancefleetconfig-spotprovisioningspecification-timeoutaction
            """
            return self._values.get('timeout_action')

        @property
        def timeout_duration_minutes(self) -> jsii.Number:
            """``CfnInstanceFleetConfig.SpotProvisioningSpecificationProperty.TimeoutDurationMinutes``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancefleetconfig-spotprovisioningspecification.html#cfn-elasticmapreduce-instancefleetconfig-spotprovisioningspecification-timeoutdurationminutes
            """
            return self._values.get('timeout_duration_minutes')

        @property
        def block_duration_minutes(self) -> typing.Optional[jsii.Number]:
            """``CfnInstanceFleetConfig.SpotProvisioningSpecificationProperty.BlockDurationMinutes``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancefleetconfig-spotprovisioningspecification.html#cfn-elasticmapreduce-instancefleetconfig-spotprovisioningspecification-blockdurationminutes
            """
            return self._values.get('block_duration_minutes')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'SpotProvisioningSpecificationProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnInstanceFleetConfig.VolumeSpecificationProperty", jsii_struct_bases=[], name_mapping={'size_in_gb': 'sizeInGb', 'volume_type': 'volumeType', 'iops': 'iops'})
    class VolumeSpecificationProperty():
        def __init__(self, *, size_in_gb: jsii.Number, volume_type: str, iops: typing.Optional[jsii.Number]=None):
            """
            :param size_in_gb: ``CfnInstanceFleetConfig.VolumeSpecificationProperty.SizeInGB``.
            :param volume_type: ``CfnInstanceFleetConfig.VolumeSpecificationProperty.VolumeType``.
            :param iops: ``CfnInstanceFleetConfig.VolumeSpecificationProperty.Iops``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancefleetconfig-volumespecification.html
            """
            self._values = {
                'size_in_gb': size_in_gb,
                'volume_type': volume_type,
            }
            if iops is not None: self._values["iops"] = iops

        @property
        def size_in_gb(self) -> jsii.Number:
            """``CfnInstanceFleetConfig.VolumeSpecificationProperty.SizeInGB``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancefleetconfig-volumespecification.html#cfn-elasticmapreduce-instancefleetconfig-volumespecification-sizeingb
            """
            return self._values.get('size_in_gb')

        @property
        def volume_type(self) -> str:
            """``CfnInstanceFleetConfig.VolumeSpecificationProperty.VolumeType``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancefleetconfig-volumespecification.html#cfn-elasticmapreduce-instancefleetconfig-volumespecification-volumetype
            """
            return self._values.get('volume_type')

        @property
        def iops(self) -> typing.Optional[jsii.Number]:
            """``CfnInstanceFleetConfig.VolumeSpecificationProperty.Iops``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancefleetconfig-volumespecification.html#cfn-elasticmapreduce-instancefleetconfig-volumespecification-iops
            """
            return self._values.get('iops')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'VolumeSpecificationProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



@jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnInstanceFleetConfigProps", jsii_struct_bases=[], name_mapping={'cluster_id': 'clusterId', 'instance_fleet_type': 'instanceFleetType', 'instance_type_configs': 'instanceTypeConfigs', 'launch_specifications': 'launchSpecifications', 'name': 'name', 'target_on_demand_capacity': 'targetOnDemandCapacity', 'target_spot_capacity': 'targetSpotCapacity'})
class CfnInstanceFleetConfigProps():
    def __init__(self, *, cluster_id: str, instance_fleet_type: str, instance_type_configs: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnInstanceFleetConfig.InstanceTypeConfigProperty"]]]]]=None, launch_specifications: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnInstanceFleetConfig.InstanceFleetProvisioningSpecificationsProperty"]]]=None, name: typing.Optional[str]=None, target_on_demand_capacity: typing.Optional[jsii.Number]=None, target_spot_capacity: typing.Optional[jsii.Number]=None):
        """Properties for defining a ``AWS::EMR::InstanceFleetConfig``.

        :param cluster_id: ``AWS::EMR::InstanceFleetConfig.ClusterId``.
        :param instance_fleet_type: ``AWS::EMR::InstanceFleetConfig.InstanceFleetType``.
        :param instance_type_configs: ``AWS::EMR::InstanceFleetConfig.InstanceTypeConfigs``.
        :param launch_specifications: ``AWS::EMR::InstanceFleetConfig.LaunchSpecifications``.
        :param name: ``AWS::EMR::InstanceFleetConfig.Name``.
        :param target_on_demand_capacity: ``AWS::EMR::InstanceFleetConfig.TargetOnDemandCapacity``.
        :param target_spot_capacity: ``AWS::EMR::InstanceFleetConfig.TargetSpotCapacity``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-instancefleetconfig.html
        """
        self._values = {
            'cluster_id': cluster_id,
            'instance_fleet_type': instance_fleet_type,
        }
        if instance_type_configs is not None: self._values["instance_type_configs"] = instance_type_configs
        if launch_specifications is not None: self._values["launch_specifications"] = launch_specifications
        if name is not None: self._values["name"] = name
        if target_on_demand_capacity is not None: self._values["target_on_demand_capacity"] = target_on_demand_capacity
        if target_spot_capacity is not None: self._values["target_spot_capacity"] = target_spot_capacity

    @property
    def cluster_id(self) -> str:
        """``AWS::EMR::InstanceFleetConfig.ClusterId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-instancefleetconfig.html#cfn-elasticmapreduce-instancefleetconfig-clusterid
        """
        return self._values.get('cluster_id')

    @property
    def instance_fleet_type(self) -> str:
        """``AWS::EMR::InstanceFleetConfig.InstanceFleetType``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-instancefleetconfig.html#cfn-elasticmapreduce-instancefleetconfig-instancefleettype
        """
        return self._values.get('instance_fleet_type')

    @property
    def instance_type_configs(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnInstanceFleetConfig.InstanceTypeConfigProperty"]]]]]:
        """``AWS::EMR::InstanceFleetConfig.InstanceTypeConfigs``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-instancefleetconfig.html#cfn-elasticmapreduce-instancefleetconfig-instancetypeconfigs
        """
        return self._values.get('instance_type_configs')

    @property
    def launch_specifications(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnInstanceFleetConfig.InstanceFleetProvisioningSpecificationsProperty"]]]:
        """``AWS::EMR::InstanceFleetConfig.LaunchSpecifications``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-instancefleetconfig.html#cfn-elasticmapreduce-instancefleetconfig-launchspecifications
        """
        return self._values.get('launch_specifications')

    @property
    def name(self) -> typing.Optional[str]:
        """``AWS::EMR::InstanceFleetConfig.Name``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-instancefleetconfig.html#cfn-elasticmapreduce-instancefleetconfig-name
        """
        return self._values.get('name')

    @property
    def target_on_demand_capacity(self) -> typing.Optional[jsii.Number]:
        """``AWS::EMR::InstanceFleetConfig.TargetOnDemandCapacity``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-instancefleetconfig.html#cfn-elasticmapreduce-instancefleetconfig-targetondemandcapacity
        """
        return self._values.get('target_on_demand_capacity')

    @property
    def target_spot_capacity(self) -> typing.Optional[jsii.Number]:
        """``AWS::EMR::InstanceFleetConfig.TargetSpotCapacity``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-instancefleetconfig.html#cfn-elasticmapreduce-instancefleetconfig-targetspotcapacity
        """
        return self._values.get('target_spot_capacity')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnInstanceFleetConfigProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnInstanceGroupConfig(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-emr.CfnInstanceGroupConfig"):
    """A CloudFormation ``AWS::EMR::InstanceGroupConfig``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-emr-instancegroupconfig.html
    cloudformationResource:
    :cloudformationResource:: AWS::EMR::InstanceGroupConfig
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, instance_count: jsii.Number, instance_role: str, instance_type: str, job_flow_id: str, auto_scaling_policy: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["AutoScalingPolicyProperty"]]]=None, bid_price: typing.Optional[str]=None, configurations: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "ConfigurationProperty"]]]]]=None, ebs_configuration: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["EbsConfigurationProperty"]]]=None, market: typing.Optional[str]=None, name: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::EMR::InstanceGroupConfig``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param instance_count: ``AWS::EMR::InstanceGroupConfig.InstanceCount``.
        :param instance_role: ``AWS::EMR::InstanceGroupConfig.InstanceRole``.
        :param instance_type: ``AWS::EMR::InstanceGroupConfig.InstanceType``.
        :param job_flow_id: ``AWS::EMR::InstanceGroupConfig.JobFlowId``.
        :param auto_scaling_policy: ``AWS::EMR::InstanceGroupConfig.AutoScalingPolicy``.
        :param bid_price: ``AWS::EMR::InstanceGroupConfig.BidPrice``.
        :param configurations: ``AWS::EMR::InstanceGroupConfig.Configurations``.
        :param ebs_configuration: ``AWS::EMR::InstanceGroupConfig.EbsConfiguration``.
        :param market: ``AWS::EMR::InstanceGroupConfig.Market``.
        :param name: ``AWS::EMR::InstanceGroupConfig.Name``.
        """
        props = CfnInstanceGroupConfigProps(instance_count=instance_count, instance_role=instance_role, instance_type=instance_type, job_flow_id=job_flow_id, auto_scaling_policy=auto_scaling_policy, bid_price=bid_price, configurations=configurations, ebs_configuration=ebs_configuration, market=market, name=name)

        jsii.create(CfnInstanceGroupConfig, self, [scope, id, props])

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
    @jsii.member(jsii_name="instanceCount")
    def instance_count(self) -> jsii.Number:
        """``AWS::EMR::InstanceGroupConfig.InstanceCount``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-emr-instancegroupconfig.html#cfn-emr-instancegroupconfiginstancecount-
        """
        return jsii.get(self, "instanceCount")

    @instance_count.setter
    def instance_count(self, value: jsii.Number):
        return jsii.set(self, "instanceCount", value)

    @property
    @jsii.member(jsii_name="instanceRole")
    def instance_role(self) -> str:
        """``AWS::EMR::InstanceGroupConfig.InstanceRole``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-emr-instancegroupconfig.html#cfn-emr-instancegroupconfig-instancerole
        """
        return jsii.get(self, "instanceRole")

    @instance_role.setter
    def instance_role(self, value: str):
        return jsii.set(self, "instanceRole", value)

    @property
    @jsii.member(jsii_name="instanceType")
    def instance_type(self) -> str:
        """``AWS::EMR::InstanceGroupConfig.InstanceType``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-emr-instancegroupconfig.html#cfn-emr-instancegroupconfig-instancetype
        """
        return jsii.get(self, "instanceType")

    @instance_type.setter
    def instance_type(self, value: str):
        return jsii.set(self, "instanceType", value)

    @property
    @jsii.member(jsii_name="jobFlowId")
    def job_flow_id(self) -> str:
        """``AWS::EMR::InstanceGroupConfig.JobFlowId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-emr-instancegroupconfig.html#cfn-emr-instancegroupconfig-jobflowid
        """
        return jsii.get(self, "jobFlowId")

    @job_flow_id.setter
    def job_flow_id(self, value: str):
        return jsii.set(self, "jobFlowId", value)

    @property
    @jsii.member(jsii_name="autoScalingPolicy")
    def auto_scaling_policy(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["AutoScalingPolicyProperty"]]]:
        """``AWS::EMR::InstanceGroupConfig.AutoScalingPolicy``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-emr-instancegroupconfig.html#cfn-elasticmapreduce-instancegroupconfig-autoscalingpolicy
        """
        return jsii.get(self, "autoScalingPolicy")

    @auto_scaling_policy.setter
    def auto_scaling_policy(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["AutoScalingPolicyProperty"]]]):
        return jsii.set(self, "autoScalingPolicy", value)

    @property
    @jsii.member(jsii_name="bidPrice")
    def bid_price(self) -> typing.Optional[str]:
        """``AWS::EMR::InstanceGroupConfig.BidPrice``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-emr-instancegroupconfig.html#cfn-emr-instancegroupconfig-bidprice
        """
        return jsii.get(self, "bidPrice")

    @bid_price.setter
    def bid_price(self, value: typing.Optional[str]):
        return jsii.set(self, "bidPrice", value)

    @property
    @jsii.member(jsii_name="configurations")
    def configurations(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "ConfigurationProperty"]]]]]:
        """``AWS::EMR::InstanceGroupConfig.Configurations``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-emr-instancegroupconfig.html#cfn-emr-instancegroupconfig-configurations
        """
        return jsii.get(self, "configurations")

    @configurations.setter
    def configurations(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "ConfigurationProperty"]]]]]):
        return jsii.set(self, "configurations", value)

    @property
    @jsii.member(jsii_name="ebsConfiguration")
    def ebs_configuration(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["EbsConfigurationProperty"]]]:
        """``AWS::EMR::InstanceGroupConfig.EbsConfiguration``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-emr-instancegroupconfig.html#cfn-emr-instancegroupconfig-ebsconfiguration
        """
        return jsii.get(self, "ebsConfiguration")

    @ebs_configuration.setter
    def ebs_configuration(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["EbsConfigurationProperty"]]]):
        return jsii.set(self, "ebsConfiguration", value)

    @property
    @jsii.member(jsii_name="market")
    def market(self) -> typing.Optional[str]:
        """``AWS::EMR::InstanceGroupConfig.Market``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-emr-instancegroupconfig.html#cfn-emr-instancegroupconfig-market
        """
        return jsii.get(self, "market")

    @market.setter
    def market(self, value: typing.Optional[str]):
        return jsii.set(self, "market", value)

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[str]:
        """``AWS::EMR::InstanceGroupConfig.Name``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-emr-instancegroupconfig.html#cfn-emr-instancegroupconfig-name
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: typing.Optional[str]):
        return jsii.set(self, "name", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnInstanceGroupConfig.AutoScalingPolicyProperty", jsii_struct_bases=[], name_mapping={'constraints': 'constraints', 'rules': 'rules'})
    class AutoScalingPolicyProperty():
        def __init__(self, *, constraints: typing.Union[aws_cdk.core.IResolvable, "CfnInstanceGroupConfig.ScalingConstraintsProperty"], rules: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnInstanceGroupConfig.ScalingRuleProperty"]]]):
            """
            :param constraints: ``CfnInstanceGroupConfig.AutoScalingPolicyProperty.Constraints``.
            :param rules: ``CfnInstanceGroupConfig.AutoScalingPolicyProperty.Rules``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancegroupconfig-autoscalingpolicy.html
            """
            self._values = {
                'constraints': constraints,
                'rules': rules,
            }

        @property
        def constraints(self) -> typing.Union[aws_cdk.core.IResolvable, "CfnInstanceGroupConfig.ScalingConstraintsProperty"]:
            """``CfnInstanceGroupConfig.AutoScalingPolicyProperty.Constraints``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancegroupconfig-autoscalingpolicy.html#cfn-elasticmapreduce-instancegroupconfig-autoscalingpolicy-constraints
            """
            return self._values.get('constraints')

        @property
        def rules(self) -> typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnInstanceGroupConfig.ScalingRuleProperty"]]]:
            """``CfnInstanceGroupConfig.AutoScalingPolicyProperty.Rules``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancegroupconfig-autoscalingpolicy.html#cfn-elasticmapreduce-instancegroupconfig-autoscalingpolicy-rules
            """
            return self._values.get('rules')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'AutoScalingPolicyProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnInstanceGroupConfig.CloudWatchAlarmDefinitionProperty", jsii_struct_bases=[], name_mapping={'comparison_operator': 'comparisonOperator', 'metric_name': 'metricName', 'period': 'period', 'threshold': 'threshold', 'dimensions': 'dimensions', 'evaluation_periods': 'evaluationPeriods', 'namespace': 'namespace', 'statistic': 'statistic', 'unit': 'unit'})
    class CloudWatchAlarmDefinitionProperty():
        def __init__(self, *, comparison_operator: str, metric_name: str, period: jsii.Number, threshold: jsii.Number, dimensions: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnInstanceGroupConfig.MetricDimensionProperty"]]]]]=None, evaluation_periods: typing.Optional[jsii.Number]=None, namespace: typing.Optional[str]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[str]=None):
            """
            :param comparison_operator: ``CfnInstanceGroupConfig.CloudWatchAlarmDefinitionProperty.ComparisonOperator``.
            :param metric_name: ``CfnInstanceGroupConfig.CloudWatchAlarmDefinitionProperty.MetricName``.
            :param period: ``CfnInstanceGroupConfig.CloudWatchAlarmDefinitionProperty.Period``.
            :param threshold: ``CfnInstanceGroupConfig.CloudWatchAlarmDefinitionProperty.Threshold``.
            :param dimensions: ``CfnInstanceGroupConfig.CloudWatchAlarmDefinitionProperty.Dimensions``.
            :param evaluation_periods: ``CfnInstanceGroupConfig.CloudWatchAlarmDefinitionProperty.EvaluationPeriods``.
            :param namespace: ``CfnInstanceGroupConfig.CloudWatchAlarmDefinitionProperty.Namespace``.
            :param statistic: ``CfnInstanceGroupConfig.CloudWatchAlarmDefinitionProperty.Statistic``.
            :param unit: ``CfnInstanceGroupConfig.CloudWatchAlarmDefinitionProperty.Unit``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancegroupconfig-cloudwatchalarmdefinition.html
            """
            self._values = {
                'comparison_operator': comparison_operator,
                'metric_name': metric_name,
                'period': period,
                'threshold': threshold,
            }
            if dimensions is not None: self._values["dimensions"] = dimensions
            if evaluation_periods is not None: self._values["evaluation_periods"] = evaluation_periods
            if namespace is not None: self._values["namespace"] = namespace
            if statistic is not None: self._values["statistic"] = statistic
            if unit is not None: self._values["unit"] = unit

        @property
        def comparison_operator(self) -> str:
            """``CfnInstanceGroupConfig.CloudWatchAlarmDefinitionProperty.ComparisonOperator``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancegroupconfig-cloudwatchalarmdefinition.html#cfn-elasticmapreduce-instancegroupconfig-cloudwatchalarmdefinition-comparisonoperator
            """
            return self._values.get('comparison_operator')

        @property
        def metric_name(self) -> str:
            """``CfnInstanceGroupConfig.CloudWatchAlarmDefinitionProperty.MetricName``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancegroupconfig-cloudwatchalarmdefinition.html#cfn-elasticmapreduce-instancegroupconfig-cloudwatchalarmdefinition-metricname
            """
            return self._values.get('metric_name')

        @property
        def period(self) -> jsii.Number:
            """``CfnInstanceGroupConfig.CloudWatchAlarmDefinitionProperty.Period``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancegroupconfig-cloudwatchalarmdefinition.html#cfn-elasticmapreduce-instancegroupconfig-cloudwatchalarmdefinition-period
            """
            return self._values.get('period')

        @property
        def threshold(self) -> jsii.Number:
            """``CfnInstanceGroupConfig.CloudWatchAlarmDefinitionProperty.Threshold``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancegroupconfig-cloudwatchalarmdefinition.html#cfn-elasticmapreduce-instancegroupconfig-cloudwatchalarmdefinition-threshold
            """
            return self._values.get('threshold')

        @property
        def dimensions(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnInstanceGroupConfig.MetricDimensionProperty"]]]]]:
            """``CfnInstanceGroupConfig.CloudWatchAlarmDefinitionProperty.Dimensions``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancegroupconfig-cloudwatchalarmdefinition.html#cfn-elasticmapreduce-instancegroupconfig-cloudwatchalarmdefinition-dimensions
            """
            return self._values.get('dimensions')

        @property
        def evaluation_periods(self) -> typing.Optional[jsii.Number]:
            """``CfnInstanceGroupConfig.CloudWatchAlarmDefinitionProperty.EvaluationPeriods``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancegroupconfig-cloudwatchalarmdefinition.html#cfn-elasticmapreduce-instancegroupconfig-cloudwatchalarmdefinition-evaluationperiods
            """
            return self._values.get('evaluation_periods')

        @property
        def namespace(self) -> typing.Optional[str]:
            """``CfnInstanceGroupConfig.CloudWatchAlarmDefinitionProperty.Namespace``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancegroupconfig-cloudwatchalarmdefinition.html#cfn-elasticmapreduce-instancegroupconfig-cloudwatchalarmdefinition-namespace
            """
            return self._values.get('namespace')

        @property
        def statistic(self) -> typing.Optional[str]:
            """``CfnInstanceGroupConfig.CloudWatchAlarmDefinitionProperty.Statistic``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancegroupconfig-cloudwatchalarmdefinition.html#cfn-elasticmapreduce-instancegroupconfig-cloudwatchalarmdefinition-statistic
            """
            return self._values.get('statistic')

        @property
        def unit(self) -> typing.Optional[str]:
            """``CfnInstanceGroupConfig.CloudWatchAlarmDefinitionProperty.Unit``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancegroupconfig-cloudwatchalarmdefinition.html#cfn-elasticmapreduce-instancegroupconfig-cloudwatchalarmdefinition-unit
            """
            return self._values.get('unit')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'CloudWatchAlarmDefinitionProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnInstanceGroupConfig.ConfigurationProperty", jsii_struct_bases=[], name_mapping={'classification': 'classification', 'configuration_properties': 'configurationProperties', 'configurations': 'configurations'})
    class ConfigurationProperty():
        def __init__(self, *, classification: typing.Optional[str]=None, configuration_properties: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.Mapping[str,str]]]]=None, configurations: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnInstanceGroupConfig.ConfigurationProperty"]]]]]=None):
            """
            :param classification: ``CfnInstanceGroupConfig.ConfigurationProperty.Classification``.
            :param configuration_properties: ``CfnInstanceGroupConfig.ConfigurationProperty.ConfigurationProperties``.
            :param configurations: ``CfnInstanceGroupConfig.ConfigurationProperty.Configurations``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-cluster-configuration.html
            """
            self._values = {
            }
            if classification is not None: self._values["classification"] = classification
            if configuration_properties is not None: self._values["configuration_properties"] = configuration_properties
            if configurations is not None: self._values["configurations"] = configurations

        @property
        def classification(self) -> typing.Optional[str]:
            """``CfnInstanceGroupConfig.ConfigurationProperty.Classification``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-cluster-configuration.html#cfn-emr-cluster-configuration-classification
            """
            return self._values.get('classification')

        @property
        def configuration_properties(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.Mapping[str,str]]]]:
            """``CfnInstanceGroupConfig.ConfigurationProperty.ConfigurationProperties``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-cluster-configuration.html#cfn-emr-cluster-configuration-configurationproperties
            """
            return self._values.get('configuration_properties')

        @property
        def configurations(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnInstanceGroupConfig.ConfigurationProperty"]]]]]:
            """``CfnInstanceGroupConfig.ConfigurationProperty.Configurations``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-cluster-configuration.html#cfn-emr-cluster-configuration-configurations
            """
            return self._values.get('configurations')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'ConfigurationProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnInstanceGroupConfig.EbsBlockDeviceConfigProperty", jsii_struct_bases=[], name_mapping={'volume_specification': 'volumeSpecification', 'volumes_per_instance': 'volumesPerInstance'})
    class EbsBlockDeviceConfigProperty():
        def __init__(self, *, volume_specification: typing.Union[aws_cdk.core.IResolvable, "CfnInstanceGroupConfig.VolumeSpecificationProperty"], volumes_per_instance: typing.Optional[jsii.Number]=None):
            """
            :param volume_specification: ``CfnInstanceGroupConfig.EbsBlockDeviceConfigProperty.VolumeSpecification``.
            :param volumes_per_instance: ``CfnInstanceGroupConfig.EbsBlockDeviceConfigProperty.VolumesPerInstance``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-ebsconfiguration-ebsblockdeviceconfig.html
            """
            self._values = {
                'volume_specification': volume_specification,
            }
            if volumes_per_instance is not None: self._values["volumes_per_instance"] = volumes_per_instance

        @property
        def volume_specification(self) -> typing.Union[aws_cdk.core.IResolvable, "CfnInstanceGroupConfig.VolumeSpecificationProperty"]:
            """``CfnInstanceGroupConfig.EbsBlockDeviceConfigProperty.VolumeSpecification``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-ebsconfiguration-ebsblockdeviceconfig.html#cfn-emr-ebsconfiguration-ebsblockdeviceconfig-volumespecification
            """
            return self._values.get('volume_specification')

        @property
        def volumes_per_instance(self) -> typing.Optional[jsii.Number]:
            """``CfnInstanceGroupConfig.EbsBlockDeviceConfigProperty.VolumesPerInstance``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-ebsconfiguration-ebsblockdeviceconfig.html#cfn-emr-ebsconfiguration-ebsblockdeviceconfig-volumesperinstance
            """
            return self._values.get('volumes_per_instance')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'EbsBlockDeviceConfigProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnInstanceGroupConfig.EbsConfigurationProperty", jsii_struct_bases=[], name_mapping={'ebs_block_device_configs': 'ebsBlockDeviceConfigs', 'ebs_optimized': 'ebsOptimized'})
    class EbsConfigurationProperty():
        def __init__(self, *, ebs_block_device_configs: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnInstanceGroupConfig.EbsBlockDeviceConfigProperty"]]]]]=None, ebs_optimized: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None):
            """
            :param ebs_block_device_configs: ``CfnInstanceGroupConfig.EbsConfigurationProperty.EbsBlockDeviceConfigs``.
            :param ebs_optimized: ``CfnInstanceGroupConfig.EbsConfigurationProperty.EbsOptimized``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-ebsconfiguration.html
            """
            self._values = {
            }
            if ebs_block_device_configs is not None: self._values["ebs_block_device_configs"] = ebs_block_device_configs
            if ebs_optimized is not None: self._values["ebs_optimized"] = ebs_optimized

        @property
        def ebs_block_device_configs(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnInstanceGroupConfig.EbsBlockDeviceConfigProperty"]]]]]:
            """``CfnInstanceGroupConfig.EbsConfigurationProperty.EbsBlockDeviceConfigs``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-ebsconfiguration.html#cfn-emr-ebsconfiguration-ebsblockdeviceconfigs
            """
            return self._values.get('ebs_block_device_configs')

        @property
        def ebs_optimized(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
            """``CfnInstanceGroupConfig.EbsConfigurationProperty.EbsOptimized``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-ebsconfiguration.html#cfn-emr-ebsconfiguration-ebsoptimized
            """
            return self._values.get('ebs_optimized')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'EbsConfigurationProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnInstanceGroupConfig.MetricDimensionProperty", jsii_struct_bases=[], name_mapping={'key': 'key', 'value': 'value'})
    class MetricDimensionProperty():
        def __init__(self, *, key: str, value: str):
            """
            :param key: ``CfnInstanceGroupConfig.MetricDimensionProperty.Key``.
            :param value: ``CfnInstanceGroupConfig.MetricDimensionProperty.Value``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancegroupconfig-metricdimension.html
            """
            self._values = {
                'key': key,
                'value': value,
            }

        @property
        def key(self) -> str:
            """``CfnInstanceGroupConfig.MetricDimensionProperty.Key``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancegroupconfig-metricdimension.html#cfn-elasticmapreduce-instancegroupconfig-metricdimension-key
            """
            return self._values.get('key')

        @property
        def value(self) -> str:
            """``CfnInstanceGroupConfig.MetricDimensionProperty.Value``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancegroupconfig-metricdimension.html#cfn-elasticmapreduce-instancegroupconfig-metricdimension-value
            """
            return self._values.get('value')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'MetricDimensionProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnInstanceGroupConfig.ScalingActionProperty", jsii_struct_bases=[], name_mapping={'simple_scaling_policy_configuration': 'simpleScalingPolicyConfiguration', 'market': 'market'})
    class ScalingActionProperty():
        def __init__(self, *, simple_scaling_policy_configuration: typing.Union[aws_cdk.core.IResolvable, "CfnInstanceGroupConfig.SimpleScalingPolicyConfigurationProperty"], market: typing.Optional[str]=None):
            """
            :param simple_scaling_policy_configuration: ``CfnInstanceGroupConfig.ScalingActionProperty.SimpleScalingPolicyConfiguration``.
            :param market: ``CfnInstanceGroupConfig.ScalingActionProperty.Market``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancegroupconfig-scalingaction.html
            """
            self._values = {
                'simple_scaling_policy_configuration': simple_scaling_policy_configuration,
            }
            if market is not None: self._values["market"] = market

        @property
        def simple_scaling_policy_configuration(self) -> typing.Union[aws_cdk.core.IResolvable, "CfnInstanceGroupConfig.SimpleScalingPolicyConfigurationProperty"]:
            """``CfnInstanceGroupConfig.ScalingActionProperty.SimpleScalingPolicyConfiguration``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancegroupconfig-scalingaction.html#cfn-elasticmapreduce-instancegroupconfig-scalingaction-simplescalingpolicyconfiguration
            """
            return self._values.get('simple_scaling_policy_configuration')

        @property
        def market(self) -> typing.Optional[str]:
            """``CfnInstanceGroupConfig.ScalingActionProperty.Market``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancegroupconfig-scalingaction.html#cfn-elasticmapreduce-instancegroupconfig-scalingaction-market
            """
            return self._values.get('market')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'ScalingActionProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnInstanceGroupConfig.ScalingConstraintsProperty", jsii_struct_bases=[], name_mapping={'max_capacity': 'maxCapacity', 'min_capacity': 'minCapacity'})
    class ScalingConstraintsProperty():
        def __init__(self, *, max_capacity: jsii.Number, min_capacity: jsii.Number):
            """
            :param max_capacity: ``CfnInstanceGroupConfig.ScalingConstraintsProperty.MaxCapacity``.
            :param min_capacity: ``CfnInstanceGroupConfig.ScalingConstraintsProperty.MinCapacity``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancegroupconfig-scalingconstraints.html
            """
            self._values = {
                'max_capacity': max_capacity,
                'min_capacity': min_capacity,
            }

        @property
        def max_capacity(self) -> jsii.Number:
            """``CfnInstanceGroupConfig.ScalingConstraintsProperty.MaxCapacity``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancegroupconfig-scalingconstraints.html#cfn-elasticmapreduce-instancegroupconfig-scalingconstraints-maxcapacity
            """
            return self._values.get('max_capacity')

        @property
        def min_capacity(self) -> jsii.Number:
            """``CfnInstanceGroupConfig.ScalingConstraintsProperty.MinCapacity``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancegroupconfig-scalingconstraints.html#cfn-elasticmapreduce-instancegroupconfig-scalingconstraints-mincapacity
            """
            return self._values.get('min_capacity')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'ScalingConstraintsProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnInstanceGroupConfig.ScalingRuleProperty", jsii_struct_bases=[], name_mapping={'action': 'action', 'name': 'name', 'trigger': 'trigger', 'description': 'description'})
    class ScalingRuleProperty():
        def __init__(self, *, action: typing.Union[aws_cdk.core.IResolvable, "CfnInstanceGroupConfig.ScalingActionProperty"], name: str, trigger: typing.Union[aws_cdk.core.IResolvable, "CfnInstanceGroupConfig.ScalingTriggerProperty"], description: typing.Optional[str]=None):
            """
            :param action: ``CfnInstanceGroupConfig.ScalingRuleProperty.Action``.
            :param name: ``CfnInstanceGroupConfig.ScalingRuleProperty.Name``.
            :param trigger: ``CfnInstanceGroupConfig.ScalingRuleProperty.Trigger``.
            :param description: ``CfnInstanceGroupConfig.ScalingRuleProperty.Description``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancegroupconfig-scalingrule.html
            """
            self._values = {
                'action': action,
                'name': name,
                'trigger': trigger,
            }
            if description is not None: self._values["description"] = description

        @property
        def action(self) -> typing.Union[aws_cdk.core.IResolvable, "CfnInstanceGroupConfig.ScalingActionProperty"]:
            """``CfnInstanceGroupConfig.ScalingRuleProperty.Action``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancegroupconfig-scalingrule.html#cfn-elasticmapreduce-instancegroupconfig-scalingrule-action
            """
            return self._values.get('action')

        @property
        def name(self) -> str:
            """``CfnInstanceGroupConfig.ScalingRuleProperty.Name``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancegroupconfig-scalingrule.html#cfn-elasticmapreduce-instancegroupconfig-scalingrule-name
            """
            return self._values.get('name')

        @property
        def trigger(self) -> typing.Union[aws_cdk.core.IResolvable, "CfnInstanceGroupConfig.ScalingTriggerProperty"]:
            """``CfnInstanceGroupConfig.ScalingRuleProperty.Trigger``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancegroupconfig-scalingrule.html#cfn-elasticmapreduce-instancegroupconfig-scalingrule-trigger
            """
            return self._values.get('trigger')

        @property
        def description(self) -> typing.Optional[str]:
            """``CfnInstanceGroupConfig.ScalingRuleProperty.Description``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancegroupconfig-scalingrule.html#cfn-elasticmapreduce-instancegroupconfig-scalingrule-description
            """
            return self._values.get('description')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'ScalingRuleProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnInstanceGroupConfig.ScalingTriggerProperty", jsii_struct_bases=[], name_mapping={'cloud_watch_alarm_definition': 'cloudWatchAlarmDefinition'})
    class ScalingTriggerProperty():
        def __init__(self, *, cloud_watch_alarm_definition: typing.Union[aws_cdk.core.IResolvable, "CfnInstanceGroupConfig.CloudWatchAlarmDefinitionProperty"]):
            """
            :param cloud_watch_alarm_definition: ``CfnInstanceGroupConfig.ScalingTriggerProperty.CloudWatchAlarmDefinition``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancegroupconfig-scalingtrigger.html
            """
            self._values = {
                'cloud_watch_alarm_definition': cloud_watch_alarm_definition,
            }

        @property
        def cloud_watch_alarm_definition(self) -> typing.Union[aws_cdk.core.IResolvable, "CfnInstanceGroupConfig.CloudWatchAlarmDefinitionProperty"]:
            """``CfnInstanceGroupConfig.ScalingTriggerProperty.CloudWatchAlarmDefinition``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancegroupconfig-scalingtrigger.html#cfn-elasticmapreduce-instancegroupconfig-scalingtrigger-cloudwatchalarmdefinition
            """
            return self._values.get('cloud_watch_alarm_definition')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'ScalingTriggerProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnInstanceGroupConfig.SimpleScalingPolicyConfigurationProperty", jsii_struct_bases=[], name_mapping={'scaling_adjustment': 'scalingAdjustment', 'adjustment_type': 'adjustmentType', 'cool_down': 'coolDown'})
    class SimpleScalingPolicyConfigurationProperty():
        def __init__(self, *, scaling_adjustment: jsii.Number, adjustment_type: typing.Optional[str]=None, cool_down: typing.Optional[jsii.Number]=None):
            """
            :param scaling_adjustment: ``CfnInstanceGroupConfig.SimpleScalingPolicyConfigurationProperty.ScalingAdjustment``.
            :param adjustment_type: ``CfnInstanceGroupConfig.SimpleScalingPolicyConfigurationProperty.AdjustmentType``.
            :param cool_down: ``CfnInstanceGroupConfig.SimpleScalingPolicyConfigurationProperty.CoolDown``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancegroupconfig-simplescalingpolicyconfiguration.html
            """
            self._values = {
                'scaling_adjustment': scaling_adjustment,
            }
            if adjustment_type is not None: self._values["adjustment_type"] = adjustment_type
            if cool_down is not None: self._values["cool_down"] = cool_down

        @property
        def scaling_adjustment(self) -> jsii.Number:
            """``CfnInstanceGroupConfig.SimpleScalingPolicyConfigurationProperty.ScalingAdjustment``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancegroupconfig-simplescalingpolicyconfiguration.html#cfn-elasticmapreduce-instancegroupconfig-simplescalingpolicyconfiguration-scalingadjustment
            """
            return self._values.get('scaling_adjustment')

        @property
        def adjustment_type(self) -> typing.Optional[str]:
            """``CfnInstanceGroupConfig.SimpleScalingPolicyConfigurationProperty.AdjustmentType``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancegroupconfig-simplescalingpolicyconfiguration.html#cfn-elasticmapreduce-instancegroupconfig-simplescalingpolicyconfiguration-adjustmenttype
            """
            return self._values.get('adjustment_type')

        @property
        def cool_down(self) -> typing.Optional[jsii.Number]:
            """``CfnInstanceGroupConfig.SimpleScalingPolicyConfigurationProperty.CoolDown``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancegroupconfig-simplescalingpolicyconfiguration.html#cfn-elasticmapreduce-instancegroupconfig-simplescalingpolicyconfiguration-cooldown
            """
            return self._values.get('cool_down')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'SimpleScalingPolicyConfigurationProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnInstanceGroupConfig.VolumeSpecificationProperty", jsii_struct_bases=[], name_mapping={'size_in_gb': 'sizeInGb', 'volume_type': 'volumeType', 'iops': 'iops'})
    class VolumeSpecificationProperty():
        def __init__(self, *, size_in_gb: jsii.Number, volume_type: str, iops: typing.Optional[jsii.Number]=None):
            """
            :param size_in_gb: ``CfnInstanceGroupConfig.VolumeSpecificationProperty.SizeInGB``.
            :param volume_type: ``CfnInstanceGroupConfig.VolumeSpecificationProperty.VolumeType``.
            :param iops: ``CfnInstanceGroupConfig.VolumeSpecificationProperty.Iops``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-ebsconfiguration-ebsblockdeviceconfig-volumespecification.html
            """
            self._values = {
                'size_in_gb': size_in_gb,
                'volume_type': volume_type,
            }
            if iops is not None: self._values["iops"] = iops

        @property
        def size_in_gb(self) -> jsii.Number:
            """``CfnInstanceGroupConfig.VolumeSpecificationProperty.SizeInGB``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-ebsconfiguration-ebsblockdeviceconfig-volumespecification.html#cfn-emr-ebsconfiguration-ebsblockdeviceconfig-volumespecification-sizeingb
            """
            return self._values.get('size_in_gb')

        @property
        def volume_type(self) -> str:
            """``CfnInstanceGroupConfig.VolumeSpecificationProperty.VolumeType``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-ebsconfiguration-ebsblockdeviceconfig-volumespecification.html#cfn-emr-ebsconfiguration-ebsblockdeviceconfig-volumespecification-volumetype
            """
            return self._values.get('volume_type')

        @property
        def iops(self) -> typing.Optional[jsii.Number]:
            """``CfnInstanceGroupConfig.VolumeSpecificationProperty.Iops``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-ebsconfiguration-ebsblockdeviceconfig-volumespecification.html#cfn-emr-ebsconfiguration-ebsblockdeviceconfig-volumespecification-iops
            """
            return self._values.get('iops')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'VolumeSpecificationProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



@jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnInstanceGroupConfigProps", jsii_struct_bases=[], name_mapping={'instance_count': 'instanceCount', 'instance_role': 'instanceRole', 'instance_type': 'instanceType', 'job_flow_id': 'jobFlowId', 'auto_scaling_policy': 'autoScalingPolicy', 'bid_price': 'bidPrice', 'configurations': 'configurations', 'ebs_configuration': 'ebsConfiguration', 'market': 'market', 'name': 'name'})
class CfnInstanceGroupConfigProps():
    def __init__(self, *, instance_count: jsii.Number, instance_role: str, instance_type: str, job_flow_id: str, auto_scaling_policy: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnInstanceGroupConfig.AutoScalingPolicyProperty"]]]=None, bid_price: typing.Optional[str]=None, configurations: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnInstanceGroupConfig.ConfigurationProperty"]]]]]=None, ebs_configuration: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnInstanceGroupConfig.EbsConfigurationProperty"]]]=None, market: typing.Optional[str]=None, name: typing.Optional[str]=None):
        """Properties for defining a ``AWS::EMR::InstanceGroupConfig``.

        :param instance_count: ``AWS::EMR::InstanceGroupConfig.InstanceCount``.
        :param instance_role: ``AWS::EMR::InstanceGroupConfig.InstanceRole``.
        :param instance_type: ``AWS::EMR::InstanceGroupConfig.InstanceType``.
        :param job_flow_id: ``AWS::EMR::InstanceGroupConfig.JobFlowId``.
        :param auto_scaling_policy: ``AWS::EMR::InstanceGroupConfig.AutoScalingPolicy``.
        :param bid_price: ``AWS::EMR::InstanceGroupConfig.BidPrice``.
        :param configurations: ``AWS::EMR::InstanceGroupConfig.Configurations``.
        :param ebs_configuration: ``AWS::EMR::InstanceGroupConfig.EbsConfiguration``.
        :param market: ``AWS::EMR::InstanceGroupConfig.Market``.
        :param name: ``AWS::EMR::InstanceGroupConfig.Name``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-emr-instancegroupconfig.html
        """
        self._values = {
            'instance_count': instance_count,
            'instance_role': instance_role,
            'instance_type': instance_type,
            'job_flow_id': job_flow_id,
        }
        if auto_scaling_policy is not None: self._values["auto_scaling_policy"] = auto_scaling_policy
        if bid_price is not None: self._values["bid_price"] = bid_price
        if configurations is not None: self._values["configurations"] = configurations
        if ebs_configuration is not None: self._values["ebs_configuration"] = ebs_configuration
        if market is not None: self._values["market"] = market
        if name is not None: self._values["name"] = name

    @property
    def instance_count(self) -> jsii.Number:
        """``AWS::EMR::InstanceGroupConfig.InstanceCount``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-emr-instancegroupconfig.html#cfn-emr-instancegroupconfiginstancecount-
        """
        return self._values.get('instance_count')

    @property
    def instance_role(self) -> str:
        """``AWS::EMR::InstanceGroupConfig.InstanceRole``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-emr-instancegroupconfig.html#cfn-emr-instancegroupconfig-instancerole
        """
        return self._values.get('instance_role')

    @property
    def instance_type(self) -> str:
        """``AWS::EMR::InstanceGroupConfig.InstanceType``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-emr-instancegroupconfig.html#cfn-emr-instancegroupconfig-instancetype
        """
        return self._values.get('instance_type')

    @property
    def job_flow_id(self) -> str:
        """``AWS::EMR::InstanceGroupConfig.JobFlowId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-emr-instancegroupconfig.html#cfn-emr-instancegroupconfig-jobflowid
        """
        return self._values.get('job_flow_id')

    @property
    def auto_scaling_policy(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnInstanceGroupConfig.AutoScalingPolicyProperty"]]]:
        """``AWS::EMR::InstanceGroupConfig.AutoScalingPolicy``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-emr-instancegroupconfig.html#cfn-elasticmapreduce-instancegroupconfig-autoscalingpolicy
        """
        return self._values.get('auto_scaling_policy')

    @property
    def bid_price(self) -> typing.Optional[str]:
        """``AWS::EMR::InstanceGroupConfig.BidPrice``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-emr-instancegroupconfig.html#cfn-emr-instancegroupconfig-bidprice
        """
        return self._values.get('bid_price')

    @property
    def configurations(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnInstanceGroupConfig.ConfigurationProperty"]]]]]:
        """``AWS::EMR::InstanceGroupConfig.Configurations``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-emr-instancegroupconfig.html#cfn-emr-instancegroupconfig-configurations
        """
        return self._values.get('configurations')

    @property
    def ebs_configuration(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnInstanceGroupConfig.EbsConfigurationProperty"]]]:
        """``AWS::EMR::InstanceGroupConfig.EbsConfiguration``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-emr-instancegroupconfig.html#cfn-emr-instancegroupconfig-ebsconfiguration
        """
        return self._values.get('ebs_configuration')

    @property
    def market(self) -> typing.Optional[str]:
        """``AWS::EMR::InstanceGroupConfig.Market``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-emr-instancegroupconfig.html#cfn-emr-instancegroupconfig-market
        """
        return self._values.get('market')

    @property
    def name(self) -> typing.Optional[str]:
        """``AWS::EMR::InstanceGroupConfig.Name``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-emr-instancegroupconfig.html#cfn-emr-instancegroupconfig-name
        """
        return self._values.get('name')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnInstanceGroupConfigProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnSecurityConfiguration(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-emr.CfnSecurityConfiguration"):
    """A CloudFormation ``AWS::EMR::SecurityConfiguration``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-emr-securityconfiguration.html
    cloudformationResource:
    :cloudformationResource:: AWS::EMR::SecurityConfiguration
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, security_configuration: typing.Any, name: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::EMR::SecurityConfiguration``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param security_configuration: ``AWS::EMR::SecurityConfiguration.SecurityConfiguration``.
        :param name: ``AWS::EMR::SecurityConfiguration.Name``.
        """
        props = CfnSecurityConfigurationProps(security_configuration=security_configuration, name=name)

        jsii.create(CfnSecurityConfiguration, self, [scope, id, props])

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
    @jsii.member(jsii_name="securityConfiguration")
    def security_configuration(self) -> typing.Any:
        """``AWS::EMR::SecurityConfiguration.SecurityConfiguration``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-emr-securityconfiguration.html#cfn-emr-securityconfiguration-securityconfiguration
        """
        return jsii.get(self, "securityConfiguration")

    @security_configuration.setter
    def security_configuration(self, value: typing.Any):
        return jsii.set(self, "securityConfiguration", value)

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[str]:
        """``AWS::EMR::SecurityConfiguration.Name``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-emr-securityconfiguration.html#cfn-emr-securityconfiguration-name
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: typing.Optional[str]):
        return jsii.set(self, "name", value)


@jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnSecurityConfigurationProps", jsii_struct_bases=[], name_mapping={'security_configuration': 'securityConfiguration', 'name': 'name'})
class CfnSecurityConfigurationProps():
    def __init__(self, *, security_configuration: typing.Any, name: typing.Optional[str]=None):
        """Properties for defining a ``AWS::EMR::SecurityConfiguration``.

        :param security_configuration: ``AWS::EMR::SecurityConfiguration.SecurityConfiguration``.
        :param name: ``AWS::EMR::SecurityConfiguration.Name``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-emr-securityconfiguration.html
        """
        self._values = {
            'security_configuration': security_configuration,
        }
        if name is not None: self._values["name"] = name

    @property
    def security_configuration(self) -> typing.Any:
        """``AWS::EMR::SecurityConfiguration.SecurityConfiguration``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-emr-securityconfiguration.html#cfn-emr-securityconfiguration-securityconfiguration
        """
        return self._values.get('security_configuration')

    @property
    def name(self) -> typing.Optional[str]:
        """``AWS::EMR::SecurityConfiguration.Name``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-emr-securityconfiguration.html#cfn-emr-securityconfiguration-name
        """
        return self._values.get('name')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnSecurityConfigurationProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnStep(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-emr.CfnStep"):
    """A CloudFormation ``AWS::EMR::Step``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-emr-step.html
    cloudformationResource:
    :cloudformationResource:: AWS::EMR::Step
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, action_on_failure: str, hadoop_jar_step: typing.Union[aws_cdk.core.IResolvable, "HadoopJarStepConfigProperty"], job_flow_id: str, name: str) -> None:
        """Create a new ``AWS::EMR::Step``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param action_on_failure: ``AWS::EMR::Step.ActionOnFailure``.
        :param hadoop_jar_step: ``AWS::EMR::Step.HadoopJarStep``.
        :param job_flow_id: ``AWS::EMR::Step.JobFlowId``.
        :param name: ``AWS::EMR::Step.Name``.
        """
        props = CfnStepProps(action_on_failure=action_on_failure, hadoop_jar_step=hadoop_jar_step, job_flow_id=job_flow_id, name=name)

        jsii.create(CfnStep, self, [scope, id, props])

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
    @jsii.member(jsii_name="actionOnFailure")
    def action_on_failure(self) -> str:
        """``AWS::EMR::Step.ActionOnFailure``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-emr-step.html#cfn-elasticmapreduce-step-actiononfailure
        """
        return jsii.get(self, "actionOnFailure")

    @action_on_failure.setter
    def action_on_failure(self, value: str):
        return jsii.set(self, "actionOnFailure", value)

    @property
    @jsii.member(jsii_name="hadoopJarStep")
    def hadoop_jar_step(self) -> typing.Union[aws_cdk.core.IResolvable, "HadoopJarStepConfigProperty"]:
        """``AWS::EMR::Step.HadoopJarStep``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-emr-step.html#cfn-elasticmapreduce-step-hadoopjarstep
        """
        return jsii.get(self, "hadoopJarStep")

    @hadoop_jar_step.setter
    def hadoop_jar_step(self, value: typing.Union[aws_cdk.core.IResolvable, "HadoopJarStepConfigProperty"]):
        return jsii.set(self, "hadoopJarStep", value)

    @property
    @jsii.member(jsii_name="jobFlowId")
    def job_flow_id(self) -> str:
        """``AWS::EMR::Step.JobFlowId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-emr-step.html#cfn-elasticmapreduce-step-jobflowid
        """
        return jsii.get(self, "jobFlowId")

    @job_flow_id.setter
    def job_flow_id(self, value: str):
        return jsii.set(self, "jobFlowId", value)

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> str:
        """``AWS::EMR::Step.Name``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-emr-step.html#cfn-elasticmapreduce-step-name
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: str):
        return jsii.set(self, "name", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnStep.HadoopJarStepConfigProperty", jsii_struct_bases=[], name_mapping={'jar': 'jar', 'args': 'args', 'main_class': 'mainClass', 'step_properties': 'stepProperties'})
    class HadoopJarStepConfigProperty():
        def __init__(self, *, jar: str, args: typing.Optional[typing.List[str]]=None, main_class: typing.Optional[str]=None, step_properties: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnStep.KeyValueProperty"]]]]]=None):
            """
            :param jar: ``CfnStep.HadoopJarStepConfigProperty.Jar``.
            :param args: ``CfnStep.HadoopJarStepConfigProperty.Args``.
            :param main_class: ``CfnStep.HadoopJarStepConfigProperty.MainClass``.
            :param step_properties: ``CfnStep.HadoopJarStepConfigProperty.StepProperties``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-step-hadoopjarstepconfig.html
            """
            self._values = {
                'jar': jar,
            }
            if args is not None: self._values["args"] = args
            if main_class is not None: self._values["main_class"] = main_class
            if step_properties is not None: self._values["step_properties"] = step_properties

        @property
        def jar(self) -> str:
            """``CfnStep.HadoopJarStepConfigProperty.Jar``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-step-hadoopjarstepconfig.html#cfn-elasticmapreduce-step-hadoopjarstepconfig-jar
            """
            return self._values.get('jar')

        @property
        def args(self) -> typing.Optional[typing.List[str]]:
            """``CfnStep.HadoopJarStepConfigProperty.Args``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-step-hadoopjarstepconfig.html#cfn-elasticmapreduce-step-hadoopjarstepconfig-args
            """
            return self._values.get('args')

        @property
        def main_class(self) -> typing.Optional[str]:
            """``CfnStep.HadoopJarStepConfigProperty.MainClass``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-step-hadoopjarstepconfig.html#cfn-elasticmapreduce-step-hadoopjarstepconfig-mainclass
            """
            return self._values.get('main_class')

        @property
        def step_properties(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnStep.KeyValueProperty"]]]]]:
            """``CfnStep.HadoopJarStepConfigProperty.StepProperties``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-step-hadoopjarstepconfig.html#cfn-elasticmapreduce-step-hadoopjarstepconfig-stepproperties
            """
            return self._values.get('step_properties')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'HadoopJarStepConfigProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnStep.KeyValueProperty", jsii_struct_bases=[], name_mapping={'key': 'key', 'value': 'value'})
    class KeyValueProperty():
        def __init__(self, *, key: typing.Optional[str]=None, value: typing.Optional[str]=None):
            """
            :param key: ``CfnStep.KeyValueProperty.Key``.
            :param value: ``CfnStep.KeyValueProperty.Value``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-step-keyvalue.html
            """
            self._values = {
            }
            if key is not None: self._values["key"] = key
            if value is not None: self._values["value"] = value

        @property
        def key(self) -> typing.Optional[str]:
            """``CfnStep.KeyValueProperty.Key``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-step-keyvalue.html#cfn-elasticmapreduce-step-keyvalue-key
            """
            return self._values.get('key')

        @property
        def value(self) -> typing.Optional[str]:
            """``CfnStep.KeyValueProperty.Value``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-step-keyvalue.html#cfn-elasticmapreduce-step-keyvalue-value
            """
            return self._values.get('value')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'KeyValueProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



@jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnStepProps", jsii_struct_bases=[], name_mapping={'action_on_failure': 'actionOnFailure', 'hadoop_jar_step': 'hadoopJarStep', 'job_flow_id': 'jobFlowId', 'name': 'name'})
class CfnStepProps():
    def __init__(self, *, action_on_failure: str, hadoop_jar_step: typing.Union[aws_cdk.core.IResolvable, "CfnStep.HadoopJarStepConfigProperty"], job_flow_id: str, name: str):
        """Properties for defining a ``AWS::EMR::Step``.

        :param action_on_failure: ``AWS::EMR::Step.ActionOnFailure``.
        :param hadoop_jar_step: ``AWS::EMR::Step.HadoopJarStep``.
        :param job_flow_id: ``AWS::EMR::Step.JobFlowId``.
        :param name: ``AWS::EMR::Step.Name``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-emr-step.html
        """
        self._values = {
            'action_on_failure': action_on_failure,
            'hadoop_jar_step': hadoop_jar_step,
            'job_flow_id': job_flow_id,
            'name': name,
        }

    @property
    def action_on_failure(self) -> str:
        """``AWS::EMR::Step.ActionOnFailure``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-emr-step.html#cfn-elasticmapreduce-step-actiononfailure
        """
        return self._values.get('action_on_failure')

    @property
    def hadoop_jar_step(self) -> typing.Union[aws_cdk.core.IResolvable, "CfnStep.HadoopJarStepConfigProperty"]:
        """``AWS::EMR::Step.HadoopJarStep``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-emr-step.html#cfn-elasticmapreduce-step-hadoopjarstep
        """
        return self._values.get('hadoop_jar_step')

    @property
    def job_flow_id(self) -> str:
        """``AWS::EMR::Step.JobFlowId``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-emr-step.html#cfn-elasticmapreduce-step-jobflowid
        """
        return self._values.get('job_flow_id')

    @property
    def name(self) -> str:
        """``AWS::EMR::Step.Name``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-emr-step.html#cfn-elasticmapreduce-step-name
        """
        return self._values.get('name')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnStepProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


__all__ = ["CfnCluster", "CfnClusterProps", "CfnInstanceFleetConfig", "CfnInstanceFleetConfigProps", "CfnInstanceGroupConfig", "CfnInstanceGroupConfigProps", "CfnSecurityConfiguration", "CfnSecurityConfigurationProps", "CfnStep", "CfnStepProps", "__jsii_assembly__"]

publication.publish()
