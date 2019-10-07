import pkg_resources
from string import Template
import os
import json
import logging

ADMIN_POLICY_FILES = ['datalake-admin-policy-s3access.json',
                      'bucket-policy-s3access.json',
                      'dynamodb-policy.json']

IDBROKER_POLICY_FILES = ['idbroker-assume-role-policy.json']

LOG_POLICY_FILES = ['log-policy-s3access.json',
                    'bucket-policy-s3access.json']

RANGER_POLICY_FILES = ['ranger-audit-policy-s3access.json',
                       'bucket-policy-s3access.json',
                       'dynamodb-policy.json']

POLICY_DIR = pkg_resources.resource_filename(
    'cdp_validator_for_aws', "policies/")


def create_substitutes(logs_location_base, storage_location_base,
                       dynamodb_table_name):
    '''Return an object which can be used to replace strings in the policy
    files

    The two *_base strings are expected to be bucket/path representations
    Current strings supported are:
    - ${DATALAKE_BUCKET}
    - ${DYNAMODB_TABLE_NAME}
    - ${LOGS_LOCATION_BASE}
    - ${STORAGE_LOCATION_BASE}

'''
    s = {"LOGS_LOCATION_BASE": logs_location_base,
         "STORAGE_LOCATION_BASE": storage_location_base,
         "DYNAMODB_TABLE_NAME": dynamodb_table_name,
         "DATALAKE_BUCKET": storage_location_base.split('/')[0]
         }
    return s


def get_idbroker_policies(substitutes):
    '''Return a list of the policies to be checked for the admin role'''
    return get_policies(get_idbroker_files(), substitutes)


def get_admin_policies(substitutes):
    '''Return a list of the policies to be checked for the admin role'''
    return get_policies(get_admin_files(), substitutes)


def get_log_policies(substitutes):
    '''Return a list of the policies to be checked for the log role'''
    return get_policies(get_log_files(), substitutes)


def get_ranger_policies(substitutes):
    '''Return a list of the policies to be checked for the log role'''
    return get_policies(get_ranger_files(), substitutes)


def get_policies(files, substitutes):
    '''Return a list of policies from the given files'''
    return [get_policy_with_replacement(file, substitutes) for file in files]


def get_idbroker_files(): return IDBROKER_POLICY_FILES


def get_admin_files(): return ADMIN_POLICY_FILES


def get_log_files(): return LOG_POLICY_FILES


def get_ranger_files(): return RANGER_POLICY_FILES


def get_policy_with_replacement(file, substitutes):
    policy = get_policy(file)
    policy["file"] = str(file)
    # actions = get_actions()
    for statement in policy["Statement"]:
        if isinstance(statement["Action"], str):
            statement["Action"] = [statement["Action"]]
        # statement["Action"] = [action for action_pattern in statement["Action"]
        #                        for action in match_action(action_pattern, actions)]
        if isinstance(statement["Resource"], str):
            statement["Resource"] = [statement["Resource"]]
        statement["Resource"] = get_resources_with_substitution(statement["Resource"],
                                                                substitutes)

    return policy


# def match_action(action_pattern, actions):
#     logging.getLogger().debug("matching {} against {}".format(action_pattern, str(actions)))
#     result = [i for i in filter(
#         lambda x: fnmatch.fnmatch(x, action_pattern), actions)]
#     logging.getLogger().debug("Result: ".format(str(result)))
#     return result


# def get_actions():
#     ''' Return the actions that can be used in AWS policy files'''
#     actions = []
#     actions_dir_path = os.path.join(os.getcwd(), ACTIONS_DIR, '*.txt')
#     if len(actions) == 0:
#         for filename in glob.glob(actions_dir_path):
#             logging.getLogger('cdp_validator').debug(
#                 'Reading file {} for actions'.format(filename))
#             with open(filename, 'rt') as file:
#                 actions.extend([line.strip() for line in file.readlines()])
#     return actions


def get_policy(json_file):
    '''Return a policy object from the given json file'''
    with open(os.path.join(os.getcwd(), POLICY_DIR, json_file), 'rt') as f:
        return json.load(f)


def get_resources_with_substitution(resources, substitutes):
    '''Return the list of resources, substituting for variables in the resources from the list of substitutes

        A substitute is a key value pair encoded as a tuple pair
        '''
    if isinstance(resources, str):
        resources = [resources]

    result = []
    for resource in resources:
        template = Template(resource)
        try:
            new_resource = template.substitute(substitutes)
        except KeyError:
            new_resource = template.safe_substitute(substitutes)
            logging.getLogger().warning(
                "Resource {} had a variable substitution error. Checks will use this resource: {}".format(resource, new_resource))

        logging.getLogger().debug(
            "Resource {} was replaced by {}".format(resource, new_resource))
        result.append(new_resource)

    return result
