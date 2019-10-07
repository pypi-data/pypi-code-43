# -*- coding: utf-8 -*-

from .pkg.fingerprint import fingerprint


def upload_cf_template(boto_ses,
                       template_content,
                       bucket_name,
                       prefix,
                       format_is_json=True):
    """
    Upload cloudformation template to s3 bucket and returns template url.

    :type boto_ses:
    :type template_content: str
    :type bucket_name: str
    :type prefix: str
    :type format_is_json: bool

    :rtype: str
    """
    s3_client = boto_ses.client("s3")
    fname = fingerprint.of_text(template_content)
    if prefix.endswith("/"):
        prefix = prefix[:-1]
    if format_is_json:
        ext = "json"
    else:
        ext = "yml"
    s3_key = "{}/{}.{}".format(prefix, fname, ext)
    s3_client.put_object(
        Body=template_content,
        Bucket=bucket_name,
        Key=s3_key,
    )
    template_url = "https://s3.amazonaws.com/{}/{}".format(bucket_name, s3_key)
    return template_url


def deploy_stack(boto_ses,
                 stack_name,
                 template_url,
                 stack_tags,
                 stack_parameters,
                 execution_role_arn=None):
    cf_client = boto_ses.client("cloudformation")
    try:
        res = cf_client.describe_stacks(
            StackName=stack_name
        )
        if len(res["Stacks"]) == 1:
            stack_exists_flag = True

        else:
            stack_exists_flag = False
    except:
        stack_exists_flag = False

    if stack_exists_flag is True:
        res = cf_client.update_stack(
            StackName=stack_name,
            TemplateURL=template_url,
            Parameters=stack_parameters,
            Capabilities=[
                "CAPABILITY_NAMED_IAM",
            ],
            # RoleARN=execution_role_arn,
            Tags=stack_tags,
        )
    else:
        res = cf_client.create_stack(
            StackName=stack_name,
            TemplateURL=template_url,
            Parameters=stack_parameters,
            Capabilities=[
                "CAPABILITY_NAMED_IAM",
            ],
            # RoleARN=execution_role_arn,
        )
    return res


def deploy_stack_set(boto_ses,
                     stack_set_name,
                     template_url,
                     stack_tags,
                     stack_parameters,
                     stack_set_admin_role,
                     accounts,
                     regions):
    cf_client = boto_ses.client("cloudformation")
    try:
        res_describe_stack_set = cf_client.describe_stack_set(
            StackSetName=stack_set_name
        )
        if res_describe_stack_set["StackSet"]["StackSetName"] == stack_set_name:
            stack_set_exists_flag = True
        else:
            stack_set_exists_flag = False
    except:
        stack_set_exists_flag = False

    if stack_set_exists_flag is False:
        res_create_stack_set = cf_client.create_stack_set(
            StackSetName=stack_set_name,
            TemplateURL=template_url,
            Parameters=stack_parameters,
            Tags=stack_tags,
            Capabilities=[
                "CAPABILITY_NAMED_IAM",
            ],
            AdministrationRoleARN=stack_set_admin_role,
            ExecutionRoleName="AWSCloudFormationStackSetExecutionRole",
        )

    res_list_stack_instances = cf_client.list_stack_instances(
        StackSetName=stack_set_name
    )
    if len(res_list_stack_instances["Summaries"]) == 0:
        has_stack_set_instance_flag = False
    else:
        has_stack_set_instance_flag = True

    if has_stack_set_instance_flag:
        res_update_stack_set = cf_client.update_stack_set(
            StackSetName=stack_set_name,
            TemplateURL=template_url,
            Parameters=stack_parameters,
            Capabilities=[
                "CAPABILITY_NAMED_IAM",
            ],
            AdministrationRoleARN=stack_set_admin_role,
            ExecutionRoleName="AWSCloudFormationStackSetExecutionRole",
            Accounts=accounts,
            Regions=regions,
        )
        return res_update_stack_set
    else:
        res_create_stack_instances = cf_client.create_stack_instances(
            StackSetName=stack_set_name,
            Accounts=accounts,
            Regions=regions,
            ParameterOverrides=stack_parameters,
        )
        return res_create_stack_instances
