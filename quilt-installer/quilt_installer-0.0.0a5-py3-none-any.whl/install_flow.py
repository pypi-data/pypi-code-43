import click

from .config import INSTALLER_CONFIG_SCHEMA_VERSION, retrieve_config_yaml_from_s3, retrieve_config_yaml_from_file, \
    ConfigConsts
from .cli_input import wait_for_cli_input
from .cloudformation import get_cfn_outputs, deploy_cfn_stack, watch_cfn_stack_events_until_done, \
    convert_param_representation_to_cfn
from .cloudformation import SUCCESSFUL_TERMINAL_STATES as CFN_SUCCESSFUL_TERMINAL_STATES
from .route53 import find_route53_hosted_zone, add_route53_cname_record
from .session_log import SessionLog
from .user_input_params import UserInputParam


def attempt_to_debug_cfn_failure(cfn_stack_id):
    # TODO: Implement this as we discover failures that we can automatically recover from
    pass





def update_cnames(stack_id, domain_name):
    hz_id = find_route53_hosted_zone(domain_name)
    sources = ["QuiltWebHost", "RegistryHost", "S3ProxyHost"]
    dest = "LoadBalancerDNSName"
    outputs = get_cfn_outputs(stack_id, [dest] + sources)
    for source in sources:
        print("Creating CNAME entry from", outputs[source], "to", outputs[dest])
        add_route53_cname_record(hz_id, outputs[source], outputs[dest])




def install(installer_config_yaml_loc=None, disable_telemetry=False):
    """
    The main installer flow:
     - get Installer Config YAML
     - prompt user for inputs
     - launch stack
     - wait for stack to be ready.
     - if stack succeeded set route53 cname entries if user desires.
     - if stack failed, point user to the right channel to get help from Quilt team with debug info we will need.

    :param installer_config_yaml_loc: If None, will use the default Installer Config location. During developing,
                                      can pass in a custom s3 path or local file path and that will be used as the
                                      Installer Config YAML
    :param disable_telemetry: Bool to disable telemetry.
    """

    with SessionLog(disable_metrics=disable_telemetry) as session_log:
        ############################################################################################################
        # Get Installer Config YAML
        ############################################################################################################
        if installer_config_yaml_loc is None:
            config_yaml = retrieve_config_yaml_from_s3()
        else:
            if installer_config_yaml_loc.startswith("s3://"):
                config_yaml = retrieve_config_yaml_from_s3(s3_loc=installer_config_yaml_loc)
            else:
                config_yaml = retrieve_config_yaml_from_file(installer_config_yaml_loc)

        ############################################################################################################
        # Check code knows how to handle Installer Config schema. Extract data into convenience classes
        ############################################################################################################
        meta = config_yaml["meta"]
        if meta["schema_version"] != INSTALLER_CONFIG_SCHEMA_VERSION:
            print("Error! There is a mismatch between the Installer version and the Installer Config file.")
            if meta["schema_version"] < INSTALLER_CONFIG_SCHEMA_VERSION:
                print("This version of the quilt-installer is more recent than the Installer Config file. This should "
                      "only be possible when developing the installer. You are probably explicitly passing in an "
                      "Installer Config that is out of date.")
            else:
                print("This version of the quilt-installer is out of date. Please upgrade by running "
                      "'pip install --upgrade quilt-installer'")
            raise RuntimeError("Version mismatch between quilt-installer and the Installer Config file.")

        config = ConfigConsts(config_yaml["consts"]["TemplateUrl"],
                              config_yaml["consts"]["MarketplaceSubscribePrompt"],
                              config_yaml["consts"]["InstallSuccessMessage"],
                              config_yaml["consts"]["InstallFailedOpenTicketMessage"])

        user_input_params = []
        for p in config_yaml["params"]:
            uip = UserInputParam(p["name"],
                                 p["description"],
                                 default_value=p["default_value"],
                                 is_password=bool(p["is_password"]),
                                 required=bool(p["required"]),
                                 validation_regex=p["validation_regex"])
            user_input_params.append(uip)

        session_log.log_start(config_file_version=meta["file_version"],
                              config_schema_version=meta["schema_version"],
                              template_url=config.cfn_template_url)

        ############################################################################################################
        # Prompt user to subscribe via AWS Marketplace
        ############################################################################################################
        print(config.subscribe_prompt)
        wait_for_cli_input(prompt="Press Enter to continue", default_val=None, is_required=False, show_default=False)

        ############################################################################################################
        # Loop through list of params and get user input
        ############################################################################################################
        for param in user_input_params:
            print()
            print(f"{param.description}")
            while True:

                user_input = wait_for_cli_input(prompt=param.input_prompt(),
                                                default_val=param.default,
                                                is_password=param.is_password,
                                                is_required=param.required)
                is_valid, failed_reason = param.is_valid(user_input)
                if is_valid:
                    param.set_val(user_input)
                    session_log.log_valid_param_set_event(param.name)
                    break
                else:
                    print(failed_reason, "Please try again.")
        print()

        for param in user_input_params:
            assert param.val_is_set, f"At this point all params that rely on user input should have been set. Param " \
                                     f"{param.name} has not been set."

        param_dict = {p.name: p.param_value for p in user_input_params}

        ############################################################################################################
        # Handle any special params:
        #   - StackName which is a boto3 keyword argument, not a cfn param
        ############################################################################################################
        stack_name = param_dict['StackName']
        del param_dict['StackName']


        ############################################################################################################
        # Launch CFN stack and wait for it to complete
        ############################################################################################################
        print("Launching CloudFormation stack:")
        stack_id = deploy_cfn_stack(stack_name,
                                    config.cfn_template_url,
                                    convert_param_representation_to_cfn(param_dict))


        final_status, status_detail = watch_cfn_stack_events_until_done(stack_id, session_log)
        session_log.log_cfn_stack_reached_terminal_state(final_status, status_detail)

        ############################################################################################################
        # Handle success or failure of CFN stack
        ############################################################################################################
        if final_status in CFN_SUCCESSFUL_TERMINAL_STATES:
            quilt_web_host = [uip.param_value for uip in user_input_params if uip.name == "QuiltWebHost"][0]
            domain_name = ".".join(quilt_web_host.split(".")[1:])


            print()
            print("CloudFormation stack is up! The only step left is to set three CNAME entries so Quilt runs under "
                  f"the domain ({domain_name}) you specified earlier. If your domain is hosted in route53, Quilt can "
                  f"automatically create those CNAME entries.")
            print()
            autocreate_cname_entries = click.prompt("Would you like Quilt to create these CNAME entries now "
                                                    "(route53 only)? [y/N]",
                                                    type=bool,
                                                    default=False,
                                                    show_default=False)

            show_manual_cname_steps = False
            if not autocreate_cname_entries:
                show_manual_cname_steps = True
            else:

                hz_id = find_route53_hosted_zone(domain_name)
                if hz_id is not None:
                    update_cnames(stack_id, domain_name)
                else:
                    show_manual_cname_steps = True
                    print(f"Unable to find a hosted zone for the domain '{domain_name}'.")

            if show_manual_cname_steps:
                print("You will need to set the CNAME entries manually. These are the mappings you need to create:")
                sources = ["QuiltWebHost", "RegistryHost", "S3ProxyHost"]
                dest = "LoadBalancerDNSName"
                outputs = get_cfn_outputs(stack_id, [dest] + sources)
                for source in sources:
                    print("\t", outputs[source], "->", outputs[dest])

            print()
            print(config.install_success_message)

        else:
            print()
            print(config.install_failed_open_ticket_message)
            print(f"Please include the following base64 string in the email so "
                  f"we can help you debug: DEBUG_STRING={session_log.dump_base64()}")
            print(f"(To inspect exactly what information you are sending, use "
                  f"'quilt-installer utils decode-debug-str $DEBUG_STRING')")
