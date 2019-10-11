from cdp_validator_for_aws import policy_manager as pm
import botocore.exceptions
import logging


class Role:
    def __init__(self, role_description):
        self.role_arn = role_description["Role"]["Arn"]
        self.trust_policy = role_description["Role"]["AssumeRolePolicyDocument"]

    def __str__(self):
        return self.role_arn

    def trusts(self, rhs):
        if "AWS" in self.trust_policy["Statement"][0]["Principal"].keys():
            return (type(rhs) == type(self)) and self.trusts_role(rhs.role_arn)
        else:
            return False

    def trusts_role(self, arn):
        statement = self.trust_policy["Statement"][0]
        return (statement["Principal"]["AWS"] == arn and
                statement["Effect"] == "Allow" and
                statement["Action"] == "sts:AssumeRole")

    def trusts_ec2_service(self):
        if ("Service" in self.trust_policy["Statement"][0]["Principal"].keys()):
            statement = self.trust_policy["Statement"][0]
            return (statement["Principal"]["Service"] == "ec2.amazonaws.com" and
                    statement["Effect"] == "Allow" and
                    statement["Action"] == "sts:AssumeRole")
        else:
            return False


def check_role_trust_relationships(admin_role, idbroker_role,
                                   log_role, ranger_role, issues):
    '''Check the trust relationships amongst the roles, reporting errors
    back in the issues collector

    '''
    if not idbroker_role.trusts_ec2_service():
        issues.append("IdBroker role {} doesn't trust the EC2 service".format(
            idbroker_role.role_arn))

    if not admin_role.trusts(idbroker_role):
        issues.append("Admin Role {} doesn't trust the IDBroker role {}".format(admin_role.role_arn,
                                                                                idbroker_role.role_arn))
    if not log_role.trusts_ec2_service():
        issues.append("Log Role {} doesn't trust the EC2 service".format(
            log_role.role_arn, idbroker_role.role_arn))
    if not ranger_role.trusts(idbroker_role):
        issues.append("Ranger Role {} doesn't trust the IDBroker role {}".format(ranger_role.role_arn,
                                                                                 idbroker_role.role_arn))


def check_all_roles_policies(admin_role,
                             idbroker_role,
                             log_role,
                             ranger_role,
                             substitutions,
                             iam_client,
                             issues):
    simulate_policies_for_role(pm.get_admin_policies(substitutions),
                               admin_role,
                               iam_client,
                               issues)
    simulate_policies_for_role(pm.get_idbroker_policies(substitutions),
                               idbroker_role,
                               iam_client,
                               issues)
    simulate_policies_for_role(pm.get_log_policies(substitutions),
                               log_role,
                               iam_client,
                               issues)
    simulate_policies_for_role(pm.get_ranger_policies(substitutions),
                               ranger_role,
                               iam_client,
                               issues)


def convert_instance_profile_to_role(arn, iam_client):
    '''Convert the arn to an instance profile

    Both role and instance profile arns are accepted
    raises botocore.exceptions.ClientError if there's a problem with the iam_client
    raises ValueError if there's a problem converting the arn to a role
    '''
    if ':instance-profile/' in arn:
        name = arn.split(':instance-profile/')[-1]
        return iam_client.get_instance_profile(InstanceProfileName=name)["InstanceProfile"]["Roles"][0]["Arn"]
    elif ':role/' in arn:
        return arn
    else:
        return ValueError("Arn {} not recognized as either an instance-profile or a role".format(arn))


def get_role(ip_or_role_arn, iam_client):
    '''Get a role, given an arn which could be for a role or an
    instance_profile

    If there're any boto exceptions these are logged and a Role
    with possibly null instance args is returned
    '''
    try:
        role_arn = convert_instance_profile_to_role(
            ip_or_role_arn, iam_client)
        return Role(get_role_description(role_arn, iam_client))
    except botocore.exceptions.ClientError as ce:
        logger = logging.getLogger('cdp_validator_for_aws.role')
        logger.warning(
            'Exception trying to get role information for role {}. Expect further errors'.format(ip_or_role_arn))
        logger.warning(ce)
        return None


def get_role_description(role_arn, iam_client):
    '''Get a role description for the given role arn

    Throws botocore.exceptions.ClientError if the description for
    a role cannot be found from the given arn
    '''
    return iam_client.get_role(
        RoleName=role_arn.split('/')[-1])


def simulate_policies_for_role(policies, role,
                               iam_client, issues):
    '''Amend details about any simulation errors for the given policies to the issues list'''
    list_of_errors = [e for policy in policies
                      for e in simulate_policy_for_role(policy,
                                                        role,
                                                        iam_client,
                                                        issues)]
    issues.extend(["Role: {} Denied: Action: {} Resource: {}".
                   format(role.role_arn,
                          result["EvalActionName"],
                          result["EvalResourceName"])
                   for result in list_of_errors
                   if result["EvalDecision"] != "allowed"])

    return {"EvaluationResults": list_of_errors}


def simulate_policy_for_role(policy, role, client, issues):
    '''Return a list of the evaluation results for the given policy'''
    if "file" in policy.keys():
        msg = "Simulating policy from {} for role {}".format(
            policy["file"], role)
        logging.getLogger('cdp_validator_for_aws.role').info(msg)
    return [e for statement in policy["Statement"]
            for e in simulate_statement_for_role(statement,
                                                 role,
                                                 client)]


def simulate_principal_policy(actions, resource_arns, role_arn, iam_client):
    '''This returns an EvaluationResults object'''
    spp = iam_client.simulate_principal_policy(ActionNames=actions,
                                               ResourceArns=resource_arns,
                                               PolicySourceArn=role_arn)["EvaluationResults"]
    return spp


def simulate_statement_for_role(statement, role,
                                client):
    resources = statement["Resource"]
    result = simulate_principal_policy(
        statement["Action"], resources, role.role_arn, client)
    return result


def validate_roles_with_roles(admin_role,
                              idbroker_role,
                              log_role,
                              ranger_role,
                              substitutions,
                              iam_client,
                              issues):
    check_all_roles_policies(admin_role,
                             idbroker_role,
                             log_role,
                             ranger_role,
                             substitutions,
                             iam_client,
                             issues)
    check_role_trust_relationships(admin_role,
                                   idbroker_role,
                                   log_role,
                                   ranger_role,
                                   issues)


def validate_roles(admin_role_arn,
                   idbroker_instance_profile_arn,
                   log_instance_profile_arn,
                   ranger_role_arn,
                   substitutions,
                   iam_client,
                   issues):
    admin_role = get_role(admin_role_arn, iam_client)
    idbroker_role = get_role(idbroker_instance_profile_arn, iam_client)
    log_role = get_role(log_instance_profile_arn, iam_client)
    ranger_role = get_role(ranger_role_arn, iam_client)
    validate_roles_with_roles(admin_role,
                              idbroker_role,
                              log_role,
                              ranger_role,
                              substitutions,
                              iam_client,
                              issues)
