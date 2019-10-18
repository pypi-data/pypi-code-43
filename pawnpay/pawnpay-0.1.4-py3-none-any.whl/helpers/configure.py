#!/usr/local/bin/python3
#  Copyright (c) 2019 | Advancing Technology Systems, LLC
#  See LICENSE for any grants of usage, distribution, or modification

from __future__ import print_function, unicode_literals

import sentry_sdk
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

sentry_sdk.init(
    dsn="https://999ed128c1f348f08be04770dd1e60b0@sentry.io/1764324", integrations=[SqlalchemyIntegration()]
)

from os import system, name
from uuid import UUID
from PyInquirer import *
from logo import print_pawn_pay_logo

import pickle
from pathlib import Path

from pprint import *


class ErrorReport(Exception):
    pass


def clear():
    _ = system("cls") if name == "nt" else system("clear")


def report_sync_error(pps_id: str, msg: str):
    raise ErrorReport(
        "Sync error reported by store [ " + pps_id + " ]. " + (("Attached message: " + msg) if msg != "" else "")
    )


def validate_uuid(uuid_string):
    try:
        val = UUID(uuid_string, version=4)
    except ValueError:
        return False
    return val.hex == uuid_string.replace("-", "").lower()


pawnpay_style = style_from_dict(
    {
        Token.Separator: "#008FFF",
        Token.QuestionMark: "#FFFB00 bold",
        Token.Selected: "#FFC100",  # default
        Token.Pointer: "#FFC100 bold",
        Token.Instruction: "",  # default
        Token.Answer: "#DDDDDD bold",
        Token.Question: "#008FFF",
    }
)

actions = [
    {
        "type": "list",
        "name": "action",
        "message": "What would you like to do?",
        "choices": [
            "[Generate] a new configuration",
            {"name": "[Edit] an existing configuration", "disabled": "Coming Soon™"},
            {"name": "[Test] an existing configuration", "disabled": "Coming Soon™"},
            Separator(),
            "[Report] a problem sync problem",
        ],
    }
]

sql_drivers = [
    "postgresql",
    "postgresql+psycopg2",
    "postgresql+pg8000",
    "postgresql+psycopg2cffi",
    "postgresql+pypostgresql",
    "postgresql+pygresql",
    "postgresql+zxjdbc",
    "mysql",
    "mysql+mysqldb",
    "mysql+pymysql",
    "mysql+mysqlconnector",
    "mysql+cymysql",
    "mysql+oursql",
    "mysql+gaerdbms",
    "mysql+pyodbc",
    "mysql+zxjdbc",
    "sqlite",
    "sqlite+pysqlite",
    "sqlite+pysqlcipher",
    "oracle",
    "oracle+cx_oracle",
    "oracle+zxjdbc",
    "mssql",
    "mssql+pyodbc",
    "mssql+mxodbc",
    "mssql+pymssql",
    "mssql+zxjdbc",
    "mssql+adodbapi",
]

prompts = [
    {
        "type": "list",
        "name": "action",
        "message": "What would you like to do?",
        "choices": [
            "[Generate] a new configuration",
            {"name": "[Edit] an existing configuration", "disabled": "Coming Soon™"},
            {"name": "[Test] an existing configuration", "disabled": "Coming Soon™"},
            Separator(),
            "[Report] a problem sync problem",
        ],
    },
    {
        "type": "input",
        "name": "pps_id",
        "message": "What's your Pawn-Pay Store ID?",
        "validate": (
            lambda val: validate_uuid(val.strip())
                        or "That doesn't look quite right... Pawn-Pay Store IDs should have some numbers, some letters, and a few dashes in them"
        ),
        "filter": lambda val: val.strip(),
        "when": lambda action: (("[Generate]" in action["action"]) or ("[Report]" in action["action"])),
    },
    {
        "type": "input",
        "name": "pps_key",
        "message": "What's your Pawn-Pay API Key?",
        "validate": lambda val: len(val.strip()) == 80
                                and not str(val.strip()).isalpha()
                                and not str(val.strip()).isnumeric()
                                and str(val.strip()).isalnum()
                                or "That doesn't look quite right...",
        "when": lambda action: "[Generate]" in action["action"],
    },
    {
        "type": "checkbox",
        "message": "What kind of records would you like to sync?",
        "name": "sync",
        "token": "> ",
        "choices": [
            Separator("-- Uncheck Record Types You Don't Want to Sync --"),
            {"name": "Tickets", "checked": True},
            {"name": "Customers", "checked": True},
            {"name": "Payments", "checked": True},
        ],
        "filter": lambda val: [x.lower() for x in val],
        "validate": (
            lambda answer: "You must choose at least *one* record type to sync" if len(answer) == 0 else True
        ),
        "when": lambda action: "[Generate]" in action["action"],
    },
    {
        "type": "list",
        "name": "data_source_type",
        "message": "Where should sync data from?",
        "choices": [
            "[A Database Server] (Used by programs like PawnMaster & PawnWizard)",
            "[A Folder -or- Files] (Used by programs like PawnDex & Hi-Tech Pawn)",
        ],
        "filter": lambda val: "path" if "Folder" in val else "sql",
        "when": lambda action: "[Generate]" in action["action"],
    },
    {
        "type": "input",
        "name": "data_path",
        "message": "Please enter the complete (absolute) path to sync data from:",
        "validate": lambda val: Path(val).exists()
                                and Path(val).is_dir()
                                or "That either doesn't appear to be a folder or it doesn't exist",
        "filter": lambda path: str(Path(path).resolve()),
        "when": lambda action: (("[Generate]" in action["action"]) and (action["data_source_type"] == "path")),
    },
    {
        "type": "input",
        "name": "driver",
        "message": "What DB driver would you like to use?",
        "default": "mssql+pymssql",
        "validate": lambda val: val in sql_drivers or "Supported drivers are: " + str(sql_drivers),
        "when": lambda action: (("[Generate]" in action["action"]) and (action["data_source_type"] == "sql")),
    },
    {
        "type": "input",
        "name": "host",
        "message": "Where is the DB you'd like to use?",
        "default": "127.0.0.1",
        "validate": lambda val: (
                                        isinstance(val, str)
                                        and not val.isnumeric()
                                        and not val.isalpha()
                                        and not val.isalnum()
                                        and val.isprintable()
        )
                                or "Please enter either an IP address or an FQDN",
        "when": lambda action: (("[Generate]" in action["action"]) and (action["data_source_type"] == "sql")),
    },
    {
        "type": "input",
        "name": "port",
        "message": "What port does the DB listen for connections on?",
        "default": "1433",
        "validate": (
            lambda val: (val.isnumeric() and not val.isalpha()) or "Please enter a number between 0 and 65535"
        ),
        "when": lambda action: (("[Generate]" in action["action"]) and (action["data_source_type"] == "sql")),
    },
    {
        "type": "input",
        "name": "db",
        "message": "Specify a DB or instance name (or leave blank):",
        "when": lambda action: (("[Generate]" in action["action"]) and (action["data_source_type"] == "sql")),
    },
    {
        "type": "list",
        "name": "trusted",
        "message": "What type of authentication should we use?",
        "choices": ["Windows Authentication", "SQL Server Authenticaton"],
        "filter": lambda val: ("SQL" not in val),
        "when": lambda action: (("[Generate]" in action["action"]) and (action["data_source_type"] == "sql")),
    },
    {
        "type": "input",
        "name": "user",
        "message": "What username should we use?",
        "default": "SA",
        "validate": lambda val: val is not None and val != "",
        "when": (
            lambda action: (
                    ("[Generate]" in action["action"])
                    and (action["data_source_type"] == "sql")
                    and (not action["trusted"])
            )
        ),
    },
    {
        "type": "password",
        "name": "password",
        "message": "What password should we use?",
        "validate": lambda val: val is not None and val != "",
        "when": (
            lambda action: (
                    ("[Generate]" in action["action"])
                    and (action["data_source_type"] == "sql")
                    and (not action["trusted"])
            )
        ),
    },
    {
        "type": "input",
        "name": "save_path",
        "message": "Where should we save the new configuration file?",
        "validate": (lambda val: Path(val).parent.resolve().exists() and not Path(val).is_dir())
                    or "That either doesn't appear to be a folder we can write to",
        "filter": lambda path: Path(path).resolve(),
        "when": lambda action: "[Generate]" in action["action"],
    },
    {
        "type": "confirm",
        "message": "Would you like to include a message?",
        "name": "include_message",
        "default": True,
        "when": lambda action: "[Report]" in action["action"],
    },
    {
        "type": "input",
        "name": "error_report",
        "message": "Please type your message and press [ENTER] when you are done:",
        "validate": lambda msg: len(msg) > 10 or "Your message should be a *least* 10 characters long",
        "when": lambda action: "[Report]" in action["action"] and action["include_message"],
    }
]

clear()
print_pawn_pay_logo("Sync Configuration Utility", "Need a hand?")

settings = prompt(prompts, style=pawnpay_style)

if "[Generate]" in settings['action']:
    save_path = settings["save_path"]

    settings = {
        "pps": {
            "id": settings["pps_id"],
            "key": settings["pps_key"],
        },
        "sync": settings["sync"],
        "data": {
            "source": settings["data_source_type"],
            "path": settings["data_path"] if "data_path" in settings.keys() else None,
            "sql": {
                "driver": settings["driver"],
                "host": settings["host"],
                "port": settings["port"],
                "user": settings["user"] if not settings["trusted"] else None,
                "password": settings["password"] if not settings["trusted"] else None,
                "trusted": settings["trusted"]
            } if settings["data_source_type"] == "sql" else None
        }
    }

    save_path.write_bytes(pickle.dumps(settings))

    print("Wrote: ")
    pprint(settings)
    print("\nTo " + str(save_path))

elif "[Report]" in settings['action']:
    try:
        report_sync_error(settings["pps_id"], msg=settings["error_report"] if settings["include_message"] else None)
    except ErrorReport as err:
        sentry_sdk.capture_exception(err)
else:
    exit()

exit()

#  Copyright (c) 2019 | Advancing Technology Systems, LLC
#  See LICENSE for any grants of usage, distribution, or modification
