# -*- coding: utf-8 -*-
r"""This module is used to use the GitLab API to automatically create a MR for a specific project, assigned to you.
This Python library is intended to be used by in a Docker image in the GitLab CI. Hence lots of the cli options can
also be environment variables, most of which will be provided with the GitLab CI. However this package allows you
to do this using the CLI if you so wish. It does the following:

    * It checks if the source branch is the target branch
    * It checks if the MR already exists for that target onto the source
    * Gets any extra issue data
    * It then creates the MR
    * Finally it updates the MR which extra attributes i.e. Squash commits or Auto Merge etc

Example:
    ::

        $ pip install -e .
        $ gitlab_auto_mr --private-token xxx --source-branch feature --project-id 11121006 \
                            --project-url https://gitlab.com/gitlab-automation-toolkit/gitlab-auto-mr --user-id 2902137

.. _Google Python Style Guide:
    http://google.github.io/styleguide/pyguide.html

"""
import os
import re
import sys

import click
import gitlab


@click.command()
@click.option(
    "--private-token",
    envvar="GITLAB_PRIVATE_TOKEN",
    required=True,
    help="Private GITLAB token, used to authenticate when calling the MR API.",
)
@click.option("--source-branch", envvar="CI_COMMIT_REF_NAME", required=True, help="The source branch to merge into.")
@click.option(
    "--project-id",
    envvar="CI_PROJECT_ID",
    required=True,
    type=int,
    help="The project ID on GitLab to create the MR for.",
)
@click.option("--gitlab-url", envvar="CI_PROJECT_URL", required=True, help="The GitLab URL i.e. gitlab.com.")
@click.option(
    "--user-id",
    envvar="GITLAB_USER_ID",
    required=True,
    type=int,
    help="The GitLab user ID to assign the created MR to.",
)
@click.option("--target-branch", "-t", help="The target branch to merge onto.")
@click.option("--commit-prefix", "-c", default="WIP", help="Prefix for the MR title i.e. WIP.")
@click.option(
    "--remove-branch", "-r", is_flag=True, help="Set to True if you want the source branch to be removed after MR."
)
@click.option("--squash-commits", "-s", is_flag=True, help="Set to True if you want commits to be squashed.")
@click.option("--description", "-d", type=str, help="Path to file to use as the description for the MR.")
@click.option(
    "--use-issue-name",
    is_flag=True,
    help="If set to True will use information from issue in branch name, must be in the form #issue-number, i.e feature/#6.",
)
@click.option(
    "--allow-collaboration",
    is_flag=True,
    help="If set to True allow, commits from members who can merge to the target branch.",
)
def cli(
    private_token,
    source_branch,
    project_id,
    gitlab_url,
    user_id,
    target_branch,
    commit_prefix,
    remove_branch,
    squash_commits,
    description,
    use_issue_name,
    allow_collaboration,
):
    """Gitlab Auto MR Tool."""
    if gitlab_url == os.environ["CI_PROJECT_URL"]:
        gitlab_url = re.search("^https?://[^/]+", gitlab_url).group(0)

    gl = gitlab.Gitlab(gitlab_url, private_token=private_token)
    try:
        project = gl.projects.get(project_id)
    except gitlab.exceptions.GitlabGetError as e:
        print(f"Unable to get project {project_id}. Error: {e}.")
        sys.exit(1)

    if not target_branch:
        target_branch = project.default_branch

    check_if_mr_is_valid(project, source_branch, target_branch)

    commit_title = get_mr_title(commit_prefix, source_branch)
    description_data = get_description_data(description)
    data = {
        "source_branch": source_branch,
        "target_branch": target_branch,
        "remove_source_branch": remove_branch,
        "squash": squash_commits,
        "title": commit_title,
        "assignee_id": user_id,
        "description": description_data,
        "allow_collaboration": allow_collaboration,
    }

    issue_data = get_issue_data(project, source_branch, use_issue_name)
    data = {**issue_data, **data}
    project.mergerequests.create(data)
    print(f"Created a new MR {commit_title}, assigned to you.")


def get_mr_title(commit_prefix, source_branch):
    """Gets the title of the MR. If a prefix exists we add it to the URL. By default we add a prefix of WIP, so the
    MR doesn't get merged by accident.

    Args:
        commit_prefix (str): Prefix for the MR title i.e. WIP.
        source_branch (str): The source branch to merge into..

    Returns:
        str: Title of the MR we will create .

    """
    commit_title = source_branch
    if commit_prefix:
        commit_title = f"{commit_prefix}: {commit_title}"
    return commit_title


def check_if_mr_is_valid(project, source_branch, target_branch):
    """Checks if the MR is valid:

    * Are source branch is target branch, exits with an error.
    * Does MR already exist for this source branch, exits without an error.

    Args:
        project (gitlab.v4.objects.Project): The json response from API checking which MRs are currently open.
        source_branch (str): The source branch to merge into (i.e. feature/#67).
        target_branch (str): The target branch to merge onto (i.e. master).

    """
    if source_branch == target_branch:
        print(
            f"Source Branch and Target branches must be different, source: {source_branch} and target: {target_branch}."
        )
        sys.exit(1)

    exists = does_mr_exists(project, source_branch)
    if exists:
        print(f"no new merge request opened, one already exists for this branch {source_branch}.")
        sys.exit(0)


def does_mr_exists(project, source_branch):
    """Checks if an MR for the source branch (i.e. feature/abc) already exists.

    Args:
        project (gitlab.v4.objects.Project): The json response from API checking which MRs are currently open.
        source_branch (str): The source branch to merge into (i.e. feature/#67).

    Returns
        bool: True if the MR already exists, else returns False.

    """
    mrs = project.mergerequests.list(state="opened")
    exists = False
    source_branch_mr = [mr for mr in mrs if mr.source_branch == source_branch]
    if source_branch_mr:
        exists = True
    return exists


def get_description_data(description):
    """If description is set will try to open the file (at given path), and read the contents.
    To use as the description for the MR.

    Args:
        description (str): Path to description for MR.

    Returns
        str: The description to use for the MR.

    Raises:
        OSError: If couldn't open file for some reason.

    """
    description_data = ""
    if description:
        try:
            with open(description) as mr_description:
                description_data = mr_description.read()
        except FileNotFoundError:
            print(f"Unable to find description file at {description}. No description will be set.")
        except OSError:
            print(f"Unable to open description file at {description}. No description will be set.")

    return description_data


def get_issue_data(project, source_branch, use_issue_name):
    """If the use issue name flag is set then tries to get more information to use with the
    MR from the issue, such as Milestone and Labels.

    Args:
        description (str): Path to description for MR.

    Returns
        dict: With the extra fields from issue, such as labels and milestone. This
        is empty if could not find issue.

    """
    data = {}
    if use_issue_name:
        try:
            issue = re.search("#[0-9]+", source_branch).group(0)
            issue_id = int(issue.replace("#", ""))
            issue = project.issues.get(issue_id)
            data = {"milestone_id": issue.milestone["id"], "labels": issue.labels}
        except gitlab.exceptions.GitlabGetError as e:
            print(f"Issue {issue} not found, {e}.")
        except (IndexError, AttributeError, TypeError):
            print(f"Issue Number not found in branch name {source_branch}")

    return data
