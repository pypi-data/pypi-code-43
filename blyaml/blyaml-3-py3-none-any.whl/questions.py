from blyaml.lists import departments, deployments, platforms, servers, tags

import blyaml.validators as validators


def list_to_list_of_checkbox_dicts(input: list) -> list:
    return [{"name": item} for item in input]


meta_questions = [
    {
        "type": "list",
        "name": "ignore",
        "message": "Ignore this repo?",
        "choices": ["false", "true"],
    }
]

standard_questions = [
    {"type": "input", "name": "name", "message": "What is the name? (in Title Case)"},
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
        "message": "Who are the maintainers? (Comma seperated email prefixes)",
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
        "message": "What are the client ids? (Comma seperated) (To find clients' IDs, visit sesame.brainlabsdigital.com/yaml-validation)",
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
        "choices": list_to_list_of_checkbox_dicts(tags),
    },
    {
        "type": "checkbox",
        "name": "departments",
        "message": "What are the departments?",
        "choices": list_to_list_of_checkbox_dicts(departments),
    },
    {
        "type": "checkbox",
        "name": "platforms",
        "message": "What are the platforms?",
        "choices": list_to_list_of_checkbox_dicts(platforms),
    },
    {
        "type": "input",
        "name": "wiki",
        "message": "What are the wiki urls? (Comma seperated, Optional)",
        "validate": validators.ValidUrlList,
    },
    {
        "type": "input",
        "name": "cards",
        "message": "What are the trello card urls? (Comma seperated, Optional)",
        "validate": validators.ValidUrlList,
    },
    {
        "type": "input",
        "name": "spreadsheets",
        "message": "What are the spreadsheet urls? (Comma seperated, Optional)",
        "validate": validators.ValidUrlList,
    },
    {
        "type": "input",
        "name": "docs",
        "message": "What are the docs urls? (Comma seperated, Optional)",
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
        "message": "Any documentation urls for Tech? (Comma seperated, Optional)",
        "validate": validators.ValidUrlList,
    },
    {
        "type": "checkbox",
        "name": "deployments",
        "message": "How is it deployed?",
        "choices": list_to_list_of_checkbox_dicts(deployments),
        "when": lambda answers: answers["reach"] != "library",
    },
    {
        "type": "input",
        "name": "deployments.tech-managed-google-ads-script.account-id",
        "message": "What is the tech-managed-google-ads-script account id?",
        "when": lambda answers: "tech-managed-google-ads-script"
        in answers["deployments"],
    },
    {
        "type": "input",
        "name": "deployments.tech-managed-google-ads-script.script-name",
        "message": "What is the tech-managed-google-ads-script script name?",
        "when": lambda answers: "tech-managed-google-ads-script"
        in answers["deployments"],
    },
    {
        "type": "input",
        "name": "deployments.tech-managed-google-ads-script.run-name",
        "message": "What is the tech-managed-google-ads-script run name?",
        "when": lambda answers: "tech-managed-google-ads-script"
        in answers["deployments"],
    },
    {
        "type": "input",
        "name": "deployments.tech-managed-google-ads-script.schedule",
        "message": "What is the tech-managed-google-ads-script schedule? (null or cron-style, e.g. 00 7 * * *)",
        "when": lambda answers: "tech-managed-google-ads-script"
        in answers["deployments"],
        "validate": validators.ValidCron,
    },
    {
        "type": "input",
        "name": "deployments.user-managed-google-ads-script.eval-file-urls",
        "message": "What is the user-managed-google-ads-script url? (Comma seperated, Optional)",
        "when": lambda answers: "user-managed-google-ads-script"
        in answers["deployments"],
        "validate": validators.ValidUrlList,
    },
    {
        "type": "list",
        "name": "deployments.server-button-press.server",
        "message": "What is the server-button-press server?",
        "choices": servers,
        "when": lambda answers: "server-button-press" in answers["deployments"],
    },
    {
        "type": "input",
        "name": "deployments.server-button-press.project-directory",
        "message": "What is the server-button-press project directory?",
        "when": lambda answers: "server-button-press" in answers["deployments"],
        "validate": validators.ValidDirectory,
    },
    {
        "type": "input",
        "name": "deployments.server-button-press.domain",
        "message": "What is the server-button-press domain? (Optional)",
        "when": lambda answers: "server-button-press" in answers["deployments"],
        "validate": validators.ValidUrl,
    },
    {
        "type": "list",
        "name": "deployments.web-app.server",
        "message": "What is the web-app server?",
        "choices": servers,
        "when": lambda answers: "web-app" in answers["deployments"],
    },
    {
        "type": "input",
        "name": "deployments.web-app.project-directory",
        "message": "What is the web-app project directory?",
        "when": lambda answers: "web-app" in answers["deployments"],
        "validate": validators.ValidDirectory,
    },
    {
        "type": "input",
        "name": "deployments.web-app.domain",
        "message": "What is the web-app domain? (Optional)",
        "when": lambda answers: "web-app" in answers["deployments"],
        "validate": validators.ValidUrl,
    },
    {
        "type": "input",
        "name": "deployments.tech-managed-apps-script.url",
        "message": "What is the tech-managed-apps-script url?",
        "when": lambda answers: "tech-managed-apps-script" in answers["deployments"],
        "validate": validators.ValidUrl,
    },
    {
        "type": "input",
        "name": "deployments.tech-managed-apps-script.run-name",
        "message": "What is the tech-managed-apps-script run name?",
        "when": lambda answers: "tech-managed-apps-script" in answers["deployments"],
    },
    {
        "type": "input",
        "name": "deployments.tech-managed-apps-script.schedule",
        "message": "What is the tech-managed-apps-script schedule? (null or Cron-style, e.g. 00 7 * * *)",
        "when": lambda answers: "tech-managed-apps-script" in answers["deployments"],
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
        "when": lambda answers: "tech-managed-apps-script" in answers["deployments"],
    },
    {
        "type": "list",
        "name": "deployments.command-line.server",
        "message": "What is the command-line server? (Optional)",
        "choices": ["null"] + servers,
        "when": lambda answers: "command-line" in answers["deployments"],
    },
    {
        "type": "input",
        "name": "deployments.command-line.project-directory",
        "message": "What is the command-line project directory?",
        "when": lambda answers: "command-line" in answers["deployments"],
        "validate": validators.ValidDirectory,
    },
    {
        "type": "input",
        "name": "deployments.glitch.project-name",
        "message": "What is the glitch project name?",
        "when": lambda answers: "glitch" in answers["deployments"],
    },
    {
        "type": "input",
        "name": "deployments.glitch.domain",
        "message": "What is the glitch domain?",
        "when": lambda answers: "glitch" in answers["deployments"],
        "validate": validators.ValidUrl,
    },
    {
        "type": "input",
        "name": "deployments.aws-lambda-function.function-arn",
        "message": "What is the aws-lambda-function function arn?",
        "when": lambda answers: "aws-lambda-function" in answers["deployments"],
    },
]
