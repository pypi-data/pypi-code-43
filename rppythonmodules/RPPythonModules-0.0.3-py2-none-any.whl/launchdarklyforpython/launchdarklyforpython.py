from __future__ import print_function
from launchdarkly_api.rest import ApiException
import launchdarkly_api

# helper function to get a list of all users in a dictionary with the key being the user key and the value being the user name
def get_users(project_key, environment_key, configuration):
    api_instance = launchdarkly_api.UsersApi(launchdarkly_api.ApiClient(configuration))
    api_response = api_instance.get_users(project_key, environment_key)
    user_count = api_response.total_count
    user_list = dict()

    try:
        api_response = api_instance.get_users(project_key, environment_key, limit=int(user_count))
        user_items = api_response.items

        for user in user_items:
            user_list[user.user.key] = user.user.name

    except ApiException as e:
        print("Exception when calling UsersApi->get_users: %s\n" % e)

    return user_list

# helper function to check whether a user key exists in a project and environment by returning a boolean
def get_user(project_key, environment_key, user_key, configuration):
    api_instance = launchdarkly_api.UsersApi(launchdarkly_api.ApiClient(configuration))
    
    try:
        api_response = api_instance.get_user(project_key, environment_key, user_key)
        return True
    except ApiException as e:
        return False

# helper function to enable a feature for a user in an environment and a project
def enable_feature(project_key, environment_key, feature, flagKeys, user_key, configuration):
    print("Enabling feature toggles for feature [{}]".format(feature))
    api_instance = launchdarkly_api.UserSettingsApi(launchdarkly_api.ApiClient(configuration))
    user_settings_body = launchdarkly_api.UserSettingsBody(True)  

    for key in flagKeys:
        try:
            # specifically enable a feature flag for a user based on their key.
            api_instance.put_flag_setting(project_key, environment_key, user_key, key, user_settings_body)
            print("Flag [{}] for feature [{}] was turned on".format(key, feature))
        except ApiException as e:
            print("Exception when calling UserSettingsApi->put_flag_setting: %s\n" % e)
    print("Successfully enabled feature toggles for feature [{}]".format(feature))

# helper function to disable a feature for a user in an environment and a project
def disable_feature(project_key, environment_key, feature, flagKeys, user_key, configuration):
    print("Disabling feature toggles for feature [{}]".format(feature))
    api_instance = launchdarkly_api.UserSettingsApi(launchdarkly_api.ApiClient(configuration))
    user_settings_body = launchdarkly_api.UserSettingsBody(False)

    for key in flagKeys:
        try:
            # specifically disable a feature flag for a user based on their key.
            api_instance.put_flag_setting(project_key, environment_key, user_key, key, user_settings_body)
            print("Flag [{}] for feature [{}] was turned off".format(key, feature))
        except ApiException as e:
            print("Exception when calling UserSettingsApi->put_flag_setting: %s\n" % e)
    print("Successfully disabled feature toggles for feature [{}]".format(feature))