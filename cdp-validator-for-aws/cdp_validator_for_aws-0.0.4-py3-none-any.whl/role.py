from cdp_validator_for_aws import policy_manager as pm
import botocore.exceptions
import logging


class AbstractRoleBuilder():
    def get_idbroker_role(self): pass

    def get_log_role(self): pass

    def get_ranger_role(self): pass

    def get_admin_role(self): pass

    def check_role_trust_relationships(self, issues):
        '''Check the trust relationships amongst the roles, reporting errors
        back in the issues collector

        '''
        if not self.get_idbroker_role():
            logging.getLogger(__name__).warning(
                'IDBroker not created. Skipping role trust validation')
        else:
            idbroker_arn = self.get_idbroker_role().role_arn
            if not self.get_idbroker_role().trusts_ec2_service():
                issues.append(
                    "IdBroker role {} doesn't trust the EC2 service".format(idbroker_arn))
            if self.get_admin_role():
                admin_arn = self.get_admin_role().role_arn
                if not self.get_admin_role().trusts(self.get_idbroker_role()):
                    issues.append("Admin Role {} doesn't trust the IDBroker role {}".format(
                        admin_arn, idbroker_arn))
            if self.get_log_role():
                log_arn = self.get_log_role().role_arn
                if not self.get_log_role().trusts_ec2_service():
                    issues.append("Log Role {} doesn't trust the EC2 service".format(
                        log_arn, idbroker_arn))
            if self.get_ranger_role():
                ranger_arn = self.get_ranger_role().role_arn
                if not self.get_ranger_role().trusts(self.get_idbroker_role()):
                    issues.append(
                        "Ranger Role {} doesn't trust the IDBroker role {}".format(ranger_arn, idbroker_arn))

    def check_all_roles_policies(self, issues):
        if self.get_admin_role():
            self.get_admin_role().evaluate(issues)

        if self.get_idbroker_role():
            self.get_idbroker_role().evaluate(issues)

        if self.get_log_role():
            self.get_log_role().evaluate(issues)

        if self.get_ranger_role():
            self.get_ranger_role().evaluate(issues)

    def validate_roles(self, issues):
        '''Validate the four roles given using the internal policy rules,
        modifying resources using the key/value pairs in the substitutes
        datastructure. Use the iam_client to access AWS.

        Any issues are appended to the issues collector

        '''
        try:
            self.check_all_roles_policies(issues)
            self.check_role_trust_relationships(issues)
        except botocore.exceptions.ParamValidationError:
            logging.get_logger().warning("Parameter error means we cannot validate the roles.")
        return


class RoleBuilder(AbstractRoleBuilder):
    def __init__(self,
                 admin_role_description,
                 admin_evaluation_results,
                 idbroker_role_description,
                 idbroker_evaluation_results,
                 log_role_description,
                 log_evaluation_results,
                 ranger_role_description,
                 ranger_evaluation_results
                 ):
        self.idbroker_role = Role(
            idbroker_role_description,
            idbroker_evaluation_results)
        self.log_role = Role(log_role_description, log_evaluation_results)
        self.ranger_role = Role(
            ranger_role_description, ranger_evaluation_results)
        self.admin_role = Role(
            admin_role_description, admin_evaluation_results)

    def get_idbroker_role(self): return self.idbroker_role

    def get_log_role(self): return self.log_role

    def get_ranger_role(self): return self.ranger_role

    def get_admin_role(self): return self.admin_role


class Role:
    def __init__(self, role_description, evaluation_result=None):
        self.role_arn = role_description["Role"]["Arn"]
        self.trust_policy = role_description["Role"]["AssumeRolePolicyDocument"]
        self.evaluation_result = evaluation_result

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

    def evaluate(self, issues):
        '''Return list of denials found in the policy evaluation result'''
        if self.evaluation_result:
            issues.extend(["Role: {} Denied: Action: {} Resource: {}".
                           format(self.role_arn,
                                  result["EvalActionName"],
                                  result["EvalResourceName"])
                           for result in self.evaluation_result["EvaluationResults"]
                           if result["EvalDecision"] != "allowed"])


class BotoRoleBuilder(AbstractRoleBuilder):
    def __init__(self,
                 admin_instance_profile_arn,
                 idbroker_instance_profile_arn,
                 log_instance_profile_arn,
                 ranger_instance_profile_arn,
                 substitutions,
                 iam_client
                 ):
        self.admin_instance_profile_arn = admin_instance_profile_arn
        self.idbroker_instance_profile_arn = idbroker_instance_profile_arn
        self.log_instance_profile_arn = log_instance_profile_arn
        self.ranger_instance_profile_arn = ranger_instance_profile_arn
        self.iam_client = iam_client
        self.substitutions = substitutions
        self._admin_role = None
        self._idbroker_role = None
        self._log_role = None
        self._ranger_role = None

    def get_admin_role(self):
        '''Return a Role object for the admin role - will be None if there's a
        problem creating the object'''
        if self._admin_role is None:
            self._admin_role = self.get_role(
                self.admin_instance_profile_arn,
                pm.get_admin_policies(self.substitutions))
        return self._admin_role

    def get_idbroker_role(self):
        '''Retun a Role object for the idbroker role - will be None if there's a
        problem creating the object'''
        if self._idbroker_role is None:
            self._idbroker_role = self.get_role(
                self.idbroker_instance_profile_arn,
                pm.get_idbroker_policies(self.substitutions))
        return self._idbroker_role

    def get_log_role(self):
        '''Return a role object for the log role - will be None if there's a
        problem creating the object'''
        if self._log_role is None:
            self._log_role = self.get_role(
                self.log_instance_profile_arn,
                pm.get_log_policies(self.substitutions))
        return self._log_role

    def get_ranger_role(self):
        '''Return a Role object for the ranger role - will be None if there's a
        problem creating the object'''
        if self._ranger_role is None:
            self._ranger_role = self.get_role(
                self.ranger_instance_profile_arn,
                pm.get_ranger_policies(self.substitutions))
        return self._ranger_role

    def get_role(self, ip_or_role_arn, policies):
        '''Get a role, given an arn which could be for a role or an
        instance_profile, and the policies appropriate for the role

        If there're any boto exceptions these are logged and a Role
        with possibly null instance args is returned
        '''
        try:
            role_arn = convert_instance_profile_to_role(
                ip_or_role_arn, self.iam_client)
            return Role(self.get_role_description(role_arn),
                        simulate_policies_for_role(policies,
                                                   role_arn,
                                                   self.iam_client))
        except botocore.exceptions.ClientError as ce:
            logger = logging.getLogger('cdp_validator_for_aws.role')
            logger.warning(
                'Exception trying to get role information for role {}. Expect further errors'.format(ip_or_role_arn))
            logger.warning(ce)

    def get_role_description(self, role_arn):
        '''Get a role description for the given role arn

        Throws botocore.exceptions.ClientError if the description for
        a role cannot be found from the given arn
        '''
        return self.iam_client.get_role(
            RoleName=role_arn.split('/')[-1])


def convert_instance_profile_to_role(arn, iam_client):
    '''Convert the arn to an instance profile

    Both role and instance profile arns are accepted

    Throws botocore.exceptions.ClientError if it is an instance
    profile arn and the corresponding role cannot be found
    '''
    if ':instance-profile/' in arn:
        name = arn.split('/')[-1]
        return iam_client.get_instance_profile(InstanceProfileName=name)["InstanceProfile"]["Roles"][0]["Arn"]
    else:                       # assume its a role arn already
        return arn


def simulate_principal_policy(actions, resource_arns, role_arn, iam_client):
    spp = iam_client.simulate_principal_policy(ActionNames=actions,
                                               ResourceArns=resource_arns,
                                               PolicySourceArn=role_arn)["EvaluationResults"]
    return spp


def simulate_statement_for_role(statement, role_arn,
                                client):
    resources = statement["Resource"]
    result = simulate_principal_policy(
        statement["Action"], resources, role_arn, client)
    return result


def simulate_policy_for_role(policy, role_arn, client):
    if "file" in policy.keys():
        msg = "Simulating policy from {} for role {}".format(
            policy["file"], role_arn)
        logging.getLogger('cdp_validator_for_aws.role').info(msg)
    return [e for statement in policy["Statement"]
            for e in simulate_statement_for_role(statement,
                                                 role_arn,
                                                 client)]


def simulate_policies_for_role(policies, role_arn,
                               iam_client):
    ''' Return a list of errors'''
    list_of_errors = [e for policy in policies
                      for e in simulate_policy_for_role(policy,
                                                        role_arn,
                                                        iam_client)]
    return {"EvaluationResults": list_of_errors}
