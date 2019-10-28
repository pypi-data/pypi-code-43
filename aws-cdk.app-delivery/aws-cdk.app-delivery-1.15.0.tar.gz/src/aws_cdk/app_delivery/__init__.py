import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.aws_cloudformation
import aws_cdk.aws_codebuild
import aws_cdk.aws_codepipeline
import aws_cdk.aws_codepipeline_actions
import aws_cdk.aws_events
import aws_cdk.aws_iam
import aws_cdk.core
import aws_cdk.cx_api
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/app-delivery", "1.15.0", __name__, "app-delivery@1.15.0.jsii.tgz")
@jsii.implements(aws_cdk.aws_codepipeline.IAction)
class PipelineDeployStackAction(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/app-delivery.PipelineDeployStackAction"):
    """A class to deploy a stack that is part of a CDK App, using CodePipeline. This composite Action takes care of preparing and executing a CloudFormation ChangeSet.

    It currently does *not* support stacks that make use of ``Asset``s, and
    requires the deployed stack is in the same account and region where the
    CodePipeline is hosted.

    stability
    :stability: experimental
    """
    def __init__(self, *, admin_permissions: bool, input: aws_cdk.aws_codepipeline.Artifact, stack: aws_cdk.core.Stack, capabilities: typing.Optional[typing.List[aws_cdk.aws_cloudformation.CloudFormationCapabilities]]=None, change_set_name: typing.Optional[str]=None, create_change_set_run_order: typing.Optional[jsii.Number]=None, execute_change_set_run_order: typing.Optional[jsii.Number]=None, role: typing.Optional[aws_cdk.aws_iam.IRole]=None) -> None:
        """
        :param props: -
        :param admin_permissions: Whether to grant admin permissions to CloudFormation while deploying this template. Setting this to ``true`` affects the defaults for ``role`` and ``capabilities``, if you don't specify any alternatives. The default role that will be created for you will have admin (i.e., ``*``) permissions on all resources, and the deployment will have named IAM capabilities (i.e., able to create all IAM resources). This is a shorthand that you can use if you fully trust the templates that are deployed in this pipeline. If you want more fine-grained permissions, use ``addToRolePolicy`` and ``capabilities`` to control what the CloudFormation deployment is allowed to do.
        :param input: The CodePipeline artifact that holds the synthesized app, which is the contents of the ``<directory>`` when running ``cdk synth -o <directory>``.
        :param stack: The CDK stack to be deployed.
        :param capabilities: Acknowledge certain changes made as part of deployment. For stacks that contain certain resources, explicit acknowledgement that AWS CloudFormation might create or update those resources. For example, you must specify AnonymousIAM if your stack template contains AWS Identity and Access Management (IAM) resources. For more information Default: [AnonymousIAM, AutoExpand], unless ``adminPermissions`` is true
        :param change_set_name: The name to use when creating a ChangeSet for the stack. Default: CDK-CodePipeline-ChangeSet
        :param create_change_set_run_order: The runOrder for the CodePipeline action creating the ChangeSet. Default: 1
        :param execute_change_set_run_order: The runOrder for the CodePipeline action executing the ChangeSet. Default: ``createChangeSetRunOrder + 1``
        :param role: IAM role to assume when deploying changes. If not specified, a fresh role is created. The role is created with zero permissions unless ``adminPermissions`` is true, in which case the role will have admin permissions. Default: A fresh role with admin or no permissions (depending on the value of ``adminPermissions``).

        stability
        :stability: experimental
        """
        props = PipelineDeployStackActionProps(admin_permissions=admin_permissions, input=input, stack=stack, capabilities=capabilities, change_set_name=change_set_name, create_change_set_run_order=create_change_set_run_order, execute_change_set_run_order=execute_change_set_run_order, role=role)

        jsii.create(PipelineDeployStackAction, self, [props])

    @jsii.member(jsii_name="addToDeploymentRolePolicy")
    def add_to_deployment_role_policy(self, statement: aws_cdk.aws_iam.PolicyStatement) -> None:
        """Add policy statements to the role deploying the stack.

        This role is passed to CloudFormation and must have the IAM permissions
        necessary to deploy the stack or you can grant this role ``adminPermissions``
        by using that option during creation. If you do not grant
        ``adminPermissions`` you need to identify the proper statements to add to
        this role based on the CloudFormation Resources in your stack.

        :param statement: -

        stability
        :stability: experimental
        """
        return jsii.invoke(self, "addToDeploymentRolePolicy", [statement])

    @jsii.member(jsii_name="bind")
    def bind(self, scope: aws_cdk.core.Construct, stage: aws_cdk.aws_codepipeline.IStage, *, bucket: aws_cdk.aws_s3.IBucket, role: aws_cdk.aws_iam.IRole) -> aws_cdk.aws_codepipeline.ActionConfig:
        """
        :param scope: -
        :param stage: -
        :param options: -
        :param bucket: 
        :param role: 

        stability
        :stability: experimental
        """
        options = aws_cdk.aws_codepipeline.ActionBindOptions(bucket=bucket, role=role)

        return jsii.invoke(self, "bind", [scope, stage, options])

    @jsii.member(jsii_name="onStateChange")
    def on_state_change(self, name: str, target: typing.Optional[aws_cdk.aws_events.IRuleTarget]=None, *, description: typing.Optional[str]=None, enabled: typing.Optional[bool]=None, event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern]=None, rule_name: typing.Optional[str]=None, schedule: typing.Optional[aws_cdk.aws_events.Schedule]=None, targets: typing.Optional[typing.List[aws_cdk.aws_events.IRuleTarget]]=None) -> aws_cdk.aws_events.Rule:
        """
        :param name: -
        :param target: -
        :param options: -
        :param description: A description of the rule's purpose. Default: - No description.
        :param enabled: Indicates whether the rule is enabled. Default: true
        :param event_pattern: Describes which events CloudWatch Events routes to the specified target. These routed events are matched events. For more information, see Events and Event Patterns in the Amazon CloudWatch User Guide. Default: - None.
        :param rule_name: A name for the rule. Default: - AWS CloudFormation generates a unique physical ID and uses that ID for the rule name. For more information, see Name Type.
        :param schedule: The schedule or rate (frequency) that determines when CloudWatch Events runs the rule. For more information, see Schedule Expression Syntax for Rules in the Amazon CloudWatch User Guide. Default: - None.
        :param targets: Targets to invoke when this rule matches an event. Input will be the full matched event. If you wish to specify custom target input, use ``addTarget(target[, inputOptions])``. Default: - No targets.

        stability
        :stability: experimental
        """
        options = aws_cdk.aws_events.RuleProps(description=description, enabled=enabled, event_pattern=event_pattern, rule_name=rule_name, schedule=schedule, targets=targets)

        return jsii.invoke(self, "onStateChange", [name, target, options])

    @property
    @jsii.member(jsii_name="actionProperties")
    def action_properties(self) -> aws_cdk.aws_codepipeline.ActionProperties:
        """
        stability
        :stability: experimental
        """
        return jsii.get(self, "actionProperties")

    @property
    @jsii.member(jsii_name="deploymentRole")
    def deployment_role(self) -> aws_cdk.aws_iam.IRole:
        """
        stability
        :stability: experimental
        """
        return jsii.get(self, "deploymentRole")


@jsii.data_type(jsii_type="@aws-cdk/app-delivery.PipelineDeployStackActionProps", jsii_struct_bases=[], name_mapping={'admin_permissions': 'adminPermissions', 'input': 'input', 'stack': 'stack', 'capabilities': 'capabilities', 'change_set_name': 'changeSetName', 'create_change_set_run_order': 'createChangeSetRunOrder', 'execute_change_set_run_order': 'executeChangeSetRunOrder', 'role': 'role'})
class PipelineDeployStackActionProps():
    def __init__(self, *, admin_permissions: bool, input: aws_cdk.aws_codepipeline.Artifact, stack: aws_cdk.core.Stack, capabilities: typing.Optional[typing.List[aws_cdk.aws_cloudformation.CloudFormationCapabilities]]=None, change_set_name: typing.Optional[str]=None, create_change_set_run_order: typing.Optional[jsii.Number]=None, execute_change_set_run_order: typing.Optional[jsii.Number]=None, role: typing.Optional[aws_cdk.aws_iam.IRole]=None):
        """
        :param admin_permissions: Whether to grant admin permissions to CloudFormation while deploying this template. Setting this to ``true`` affects the defaults for ``role`` and ``capabilities``, if you don't specify any alternatives. The default role that will be created for you will have admin (i.e., ``*``) permissions on all resources, and the deployment will have named IAM capabilities (i.e., able to create all IAM resources). This is a shorthand that you can use if you fully trust the templates that are deployed in this pipeline. If you want more fine-grained permissions, use ``addToRolePolicy`` and ``capabilities`` to control what the CloudFormation deployment is allowed to do.
        :param input: The CodePipeline artifact that holds the synthesized app, which is the contents of the ``<directory>`` when running ``cdk synth -o <directory>``.
        :param stack: The CDK stack to be deployed.
        :param capabilities: Acknowledge certain changes made as part of deployment. For stacks that contain certain resources, explicit acknowledgement that AWS CloudFormation might create or update those resources. For example, you must specify AnonymousIAM if your stack template contains AWS Identity and Access Management (IAM) resources. For more information Default: [AnonymousIAM, AutoExpand], unless ``adminPermissions`` is true
        :param change_set_name: The name to use when creating a ChangeSet for the stack. Default: CDK-CodePipeline-ChangeSet
        :param create_change_set_run_order: The runOrder for the CodePipeline action creating the ChangeSet. Default: 1
        :param execute_change_set_run_order: The runOrder for the CodePipeline action executing the ChangeSet. Default: ``createChangeSetRunOrder + 1``
        :param role: IAM role to assume when deploying changes. If not specified, a fresh role is created. The role is created with zero permissions unless ``adminPermissions`` is true, in which case the role will have admin permissions. Default: A fresh role with admin or no permissions (depending on the value of ``adminPermissions``).

        stability
        :stability: experimental
        """
        self._values = {
            'admin_permissions': admin_permissions,
            'input': input,
            'stack': stack,
        }
        if capabilities is not None: self._values["capabilities"] = capabilities
        if change_set_name is not None: self._values["change_set_name"] = change_set_name
        if create_change_set_run_order is not None: self._values["create_change_set_run_order"] = create_change_set_run_order
        if execute_change_set_run_order is not None: self._values["execute_change_set_run_order"] = execute_change_set_run_order
        if role is not None: self._values["role"] = role

    @property
    def admin_permissions(self) -> bool:
        """Whether to grant admin permissions to CloudFormation while deploying this template.

        Setting this to ``true`` affects the defaults for ``role`` and ``capabilities``, if you
        don't specify any alternatives.

        The default role that will be created for you will have admin (i.e., ``*``)
        permissions on all resources, and the deployment will have named IAM
        capabilities (i.e., able to create all IAM resources).

        This is a shorthand that you can use if you fully trust the templates that
        are deployed in this pipeline. If you want more fine-grained permissions,
        use ``addToRolePolicy`` and ``capabilities`` to control what the CloudFormation
        deployment is allowed to do.

        stability
        :stability: experimental
        """
        return self._values.get('admin_permissions')

    @property
    def input(self) -> aws_cdk.aws_codepipeline.Artifact:
        """The CodePipeline artifact that holds the synthesized app, which is the contents of the ``<directory>`` when running ``cdk synth -o <directory>``.

        stability
        :stability: experimental
        """
        return self._values.get('input')

    @property
    def stack(self) -> aws_cdk.core.Stack:
        """The CDK stack to be deployed.

        stability
        :stability: experimental
        """
        return self._values.get('stack')

    @property
    def capabilities(self) -> typing.Optional[typing.List[aws_cdk.aws_cloudformation.CloudFormationCapabilities]]:
        """Acknowledge certain changes made as part of deployment.

        For stacks that contain certain resources, explicit acknowledgement that AWS CloudFormation
        might create or update those resources. For example, you must specify AnonymousIAM if your
        stack template contains AWS Identity and Access Management (IAM) resources. For more
        information

        default
        :default: [AnonymousIAM, AutoExpand], unless ``adminPermissions`` is true

        see
        :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-iam-template.html#using-iam-capabilities
        stability
        :stability: experimental
        """
        return self._values.get('capabilities')

    @property
    def change_set_name(self) -> typing.Optional[str]:
        """The name to use when creating a ChangeSet for the stack.

        default
        :default: CDK-CodePipeline-ChangeSet

        stability
        :stability: experimental
        """
        return self._values.get('change_set_name')

    @property
    def create_change_set_run_order(self) -> typing.Optional[jsii.Number]:
        """The runOrder for the CodePipeline action creating the ChangeSet.

        default
        :default: 1

        stability
        :stability: experimental
        """
        return self._values.get('create_change_set_run_order')

    @property
    def execute_change_set_run_order(self) -> typing.Optional[jsii.Number]:
        """The runOrder for the CodePipeline action executing the ChangeSet.

        default
        :default: ``createChangeSetRunOrder + 1``

        stability
        :stability: experimental
        """
        return self._values.get('execute_change_set_run_order')

    @property
    def role(self) -> typing.Optional[aws_cdk.aws_iam.IRole]:
        """IAM role to assume when deploying changes.

        If not specified, a fresh role is created. The role is created with zero
        permissions unless ``adminPermissions`` is true, in which case the role will have
        admin permissions.

        default
        :default: A fresh role with admin or no permissions (depending on the value of ``adminPermissions``).

        stability
        :stability: experimental
        """
        return self._values.get('role')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'PipelineDeployStackActionProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


__all__ = ["PipelineDeployStackAction", "PipelineDeployStackActionProps", "__jsii_assembly__"]

publication.publish()
