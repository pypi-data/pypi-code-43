from functools import partial

import blyaml.validators as validators
from blyaml.lists import departments, deployments, platforms, servers, tags


def list_to_list_of_checkbox_dicts(input: list) -> list:
    return [{"name": item} for item in input]


def meta_questions() -> list:
    return [
        {
            "type": "list",
            "name": "ignore",
            "message": "Ignore this repo?",
            "choices": ["false", "true"],
        }
    ]


def standard_questions(token: str) -> list:
    return [
        {
            "type": "input",
            "name": "name",
            "message": "What is the name? (in Title Case)",
        },
        {
            "type": "list",
            "name": "status",
            "message": "What is the status?",
            "choices": ["active", "building", "inactive"],
        },
        {
            "type": "input",
            "name": "owner",
            "message": "Who is the owner? (email prefix)",
            "validate": validators.ValidEmailPrefix,
        },
        {
            "type": "input",
            "name": "maintainers",
            "message": "Who are the maintainers? (Comma separated email prefixes)",
            "validate": validators.ValidEmailPrefixList,
        },
        {
            "type": "list",
            "name": "reach",
            "message": "What is the reach?",
            "choices": [
                "general-client-tool",
                "client-specific-tool",
                "internal-tool",
                "library",
                "other",
            ],
        },
        {
            "type": "list",
            "name": "tech-implementation",
            "message": "Does it require Tech implementation? (Optional, Null to skip)",
            "choices": ["null", "false", "true"],
        },
        {
            "type": "input",
            "name": "client-ids",
            "message": "What are the client ids? (Comma separated) (To find clients' IDs, visit sesame.brainlabsdigital.com/yaml-validation)",
            "validate": validators.ValidClientIds,
            "when": lambda answers: answers["reach"] == "client-specific-tool",
        },
        {
            "type": "input",
            "name": "release-date",
            "message": "What was the release-date? (yyyy-mm-dd)",
            "when": lambda answers: answers["status"] == "active",
            "validate": validators.ValidDate,
        },
        {
            "type": "checkbox",
            "name": "tags",
            "message": "What are the tags? (Optional)",
            "choices": list_to_list_of_checkbox_dicts(tags(token)),
        },
        {
            "type": "checkbox",
            "name": "departments",
            "message": "What are the departments?",
            "choices": list_to_list_of_checkbox_dicts(departments(token)),
        },
        {
            "type": "checkbox",
            "name": "platforms",
            "message": "What are the platforms?",
            "choices": list_to_list_of_checkbox_dicts(platforms(token)),
        },
        {
            "type": "input",
            "name": "wiki",
            "message": "What are the wiki urls? (Comma separated, Optional)",
            "validate": validators.ValidUrlList,
        },
        {
            "type": "input",
            "name": "cards",
            "message": "What are the trello card urls? (Comma separated, Optional)",
            "validate": validators.ValidUrlList,
        },
        {
            "type": "input",
            "name": "spreadsheets",
            "message": "What are the spreadsheet urls? (Comma separated, Optional)",
            "validate": validators.ValidUrlList,
        },
        {
            "type": "input",
            "name": "docs",
            "message": "What are the docs urls? (Comma separated, Optional)",
            "validate": validators.ValidUrlList,
        },
        {
            "type": "list",
            "name": "trackable",
            "message": "Is it trackable? (Optional, Null to skip)",
            "choices": ["null", "false", "true"],
        },
        {
            "type": "input",
            "name": "documentation",
            "message": "Any documentation urls for Tech? (Comma separated, Optional)",
            "validate": validators.ValidUrlList,
        },
        {
            "type": "checkbox",
            "name": "deployments",
            "message": "How is it deployed?",
            "choices": list_to_list_of_checkbox_dicts(deployments()),
            "when": is_library,
        },
        {
            "type": "input",
            "name": "deployments.tech-managed-google-ads-script.account-id",
            "message": "What is the tech-managed-google-ads-script account id?",
            "when": partial(is_deployment, "tech-managed-google-ads-script"),
        },
        {
            "type": "input",
            "name": "deployments.tech-managed-google-ads-script.script-name",
            "message": "What is the tech-managed-google-ads-script script name?",
            "when": partial(is_deployment, "tech-managed-google-ads-script"),
        },
        {
            "type": "input",
            "name": "deployments.tech-managed-google-ads-script.run-name",
            "message": "What is the tech-managed-google-ads-script run name?",
            "when": partial(is_deployment, "tech-managed-google-ads-script"),
        },
        {
            "type": "input",
            "name": "deployments.tech-managed-google-ads-script.schedule",
            "message": "What is the tech-managed-google-ads-script schedule? (null or cron-style, e.g. 00 7 * * *)",
            "when": partial(is_deployment, "tech-managed-google-ads-script"),
            "validate": validators.ValidCron,
        },
        {
            "type": "input",
            "name": "deployments.user-managed-google-ads-script.eval-file-urls",
            "message": "What is the user-managed-google-ads-script url? (Comma separated, Optional)",
            "when": partial(is_deployment, "user-managed-google-ads-script"),
            "validate": validators.ValidUrlList,
        },
        {
            "type": "list",
            "name": "deployments.server-button-press.server",
            "message": "What is the server-button-press server?",
            "choices": servers(token),
            "when": partial(is_deployment, "server-button-press"),
        },
        {
            "type": "input",
            "name": "deployments.server-button-press.project-directory",
            "message": "What is the server-button-press project directory?",
            "when": partial(is_deployment, "server-button-press"),
            "validate": validators.ValidDirectory,
        },
        {
            "type": "input",
            "name": "deployments.server-button-press.domain",
            "message": "What is the server-button-press domain? (Optional)",
            "when": partial(is_deployment, "server-button-press"),
            "validate": validators.ValidUrl,
        },
        {
            "type": "list",
            "name": "deployments.web-app.server",
            "message": "What is the web-app server?",
            "choices": servers(token),
            "when": partial(is_deployment, "web-app"),
        },
        {
            "type": "input",
            "name": "deployments.web-app.project-directory",
            "message": "What is the web-app project directory?",
            "when": partial(is_deployment, "web-app"),
            "validate": validators.ValidDirectory,
        },
        {
            "type": "input",
            "name": "deployments.web-app.domain",
            "message": "What is the web-app domain? (Optional)",
            "when": partial(is_deployment, "web-app"),
            "validate": validators.ValidUrl,
        },
        {
            "type": "input",
            "name": "deployments.tech-managed-apps-script.url",
            "message": "What is the tech-managed-apps-script url?",
            "when": partial(is_deployment, "tech-managed-apps-script"),
            "validate": validators.ValidUrl,
        },
        {
            "type": "input",
            "name": "deployments.tech-managed-apps-script.run-name",
            "message": "What is the tech-managed-apps-script run name?",
            "when": partial(is_deployment, "tech-managed-apps-script"),
        },
        {
            "type": "input",
            "name": "deployments.tech-managed-apps-script.schedule",
            "message": "What is the tech-managed-apps-script schedule? (null or Cron-style, e.g. 00 7 * * *)",
            "when": partial(is_deployment, "tech-managed-apps-script"),
            "validate": validators.ValidCron,
        },
        {
            "type": "list",
            "name": "deployments.tech-managed-apps-script.trigger",
            "message": "What is the tech-managed-apps-script trigger?",
            "choices": [
                "null",
                "add-on",
                "apps-scripts-web-app",
                "on-button-press",
                "on-form-submit",
                "on-open",
            ],
            "when": partial(is_deployment, "tech-managed-apps-script"),
        },
        {
            "type": "list",
            "name": "deployments.command-line.server",
            "message": "What is the command-line server? (Optional)",
            "choices": ["null"] + servers(token),
            "when": partial(is_deployment, "command-line"),
        },
        {
            "type": "input",
            "name": "deployments.command-line.project-directory",
            "message": "What is the command-line project directory?",
            "when": partial(is_deployment, "command-line"),
            "validate": validators.ValidDirectory,
        },
        {
            "type": "input",
            "name": "deployments.glitch.project-name",
            "message": "What is the glitch project name?",
            "when": partial(is_deployment, "glitch"),
        },
        {
            "type": "input",
            "name": "deployments.glitch.domain",
            "message": "What is the glitch domain?",
            "when": partial(is_deployment, "glitch"),
            "validate": validators.ValidUrl,
        },
        {
            "type": "input",
            "name": "deployments.aws-lambda-function.function-arn",
            "message": "What is the aws-lambda-function function arn?",
            "when": partial(is_deployment, "aws-lambda-function"),
        },
    ]


def is_library(answers: dict) -> bool:
    return answers["reach"] != "library"


def is_deployment(deployment: str, answers: dict) -> bool:
    return is_library(answers) and (deployment in answers["deployments"])
