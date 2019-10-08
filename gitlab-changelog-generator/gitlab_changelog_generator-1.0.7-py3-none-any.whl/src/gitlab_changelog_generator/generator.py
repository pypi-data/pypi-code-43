import datetime
import os.path

from argparse import ArgumentParser
from log_handlers import logger
from calls import get_last_commit_date, get_commits_since_date


def process_arguments() -> dict:
    parser = ArgumentParser(prog="changegen")
    parser.add_argument(
        "-i",
        "--ip",
        dest="ip",
        help="specify IP address of GitLab repository",
        required=True,
    )
    parser.add_argument(
        "-a",
        "--api",
        dest="api",
        help="specify GitLab API version",
        choices=["1", "2", "3", "4"],
        default="4",
    )
    parser.add_argument(
        "-g",
        "--group",
        dest="group",
        help="specify GitLab group",
        required=True,
    )
    parser.add_argument(
        "-p",
        "--project",
        dest="project",
        help="specify GitLab project",
        required=True,
    )
    parser.add_argument(
        "-b",
        "--branches",
        nargs=2,
        dest="branches",
        help="specify GitLab branches to compare",
        required=True,
    )
    parser.add_argument(
        "-c",
        "--changelog",
        dest="changelog",
        help="specify whether an existing CHANGELOG.md exists",
        choices=["Y", "N"],
        default="N",
    )
    parser.add_argument(
        "-v",
        "--version",
        dest="version",
        help="specify version number",
        required=True,
    )

    args = parser.parse_args()

    return {
        "ip_address": args.ip,
        "api_version": args.api,
        "project_group": args.group,
        "project": args.project,
        "branch_one": args.branches[0],
        "branch_two": args.branches[1],
        "version": args.version,
        "changelog": args.changelog,
    }


def generate_changelog() -> None:
    # Get the command line arguments passed to the script
    cli_args = process_arguments()

    # Get the date of the last commit
    last_commit = get_last_commit_date(cli_args)

    # Get any commits since that date
    new_commits = get_commits_since_date(last_commit, cli_args)

    # Get the current date so that we can add it to the CHANGELOG.md document
    date = datetime.datetime.now()
    current_date = date.strftime("%Y-%m-%d")

    # Determine whether a CHANGELOG.md file already exists
    if os.path.isfile("CHANGELOG.md"):
        if cli_args["changelog"] == "Y":
            with open("CHANGELOG.md", "r") as original_changelog:
                original_changelog_data = original_changelog.read()
                with open("CHANGELOG.md", "w") as modified_changelog:
                    modified_changelog.write(
                        f"## v{cli_args['version']} ({current_date})\n"
                    )
                    [
                        modified_changelog.write(
                            f"* {commit['committed_date'][:10]} - {y} \n"
                        )
                        for commit in new_commits
                        for y in commit["message"].split("\n")
                    ]
                    modified_changelog.write(f"\n")
                    modified_changelog.write(original_changelog_data)
        else:
            logger.info("Existing CHANGELOG.md found but not specified")
            logger.info("Writing CHANGELOG_generated.md as a result...")
            with open("CHANGELOG_generated.md", "w") as changelog:
                changelog.write(f"## v{cli_args['version']} ({current_date})\n")
                [
                    changelog.write(
                        f"* {commit['committed_date'][:10]} - {y} \n"
                    )
                    for commit in new_commits
                    for y in commit["message"].split("\n")
                ]
    else:
        logger.info(
            "Either existing CHANGELOG.md found and not specified, "
            + "or no CHANGELOG.md found..."
        )
        logger.info("Writing CHANGELOG_generated.md as a result...")
        with open("CHANGELOG_generated.md", "w") as changelog:
            changelog.write(f"## v{cli_args['version']} ({current_date})\n")
            [
                changelog.write(f"* {commit['committed_date'][:10]} - {y} \n")
                for commit in new_commits
                for y in commit["message"].split("\n")
            ]


generate_changelog()
