from __future__ import absolute_import
import os
import re
import argparse
import ctl
import subprocess
import confu.schema
from ctl.auth import expose
from ctl.exceptions import OperationNotExposed
from ctl.plugins import PluginBase
from ctl.plugins.command import CommandPlugin
from ctl.plugins.repository import RepositoryPlugin

try:
    import urllib.parse as urlparse
except ImportError:
    import urlparse


def temporary_plugin(ctl, name, path, **config):
    """
    Instantiate a temporary git plugin pointing
    at an existing checkout path.

    Argument(s):

        - ctl: ctl instance
        - name: plugin name
        - path: file path to a cloned git repository

    Keyword Argument(s):

        Any keyword arguments will be passed on to
        plugin config

    Returns:

        - GitPlugin instance
    """

    config.update({"checkout_path": path})
    return GitPlugin({"type": "git", "name": name, "config": config}, ctl)


@ctl.plugin.register("git")
class GitPlugin(RepositoryPlugin):
    @property
    def uuid(self):
        """ return recent commit hash of the repo """
        command = self.command("rev-parse", "--short", "HEAD")
        return self.run_git_command(command)[0].strip()

    @property
    def is_cloned(self):
        """
        returns whether or not the checkout_path location is a valid
        git repo or not
        """
        return os.path.exists(os.path.join(self.checkout_path, ".git"))

    @property
    def is_clean(self):
        """
        Return whether the current repo checkout is clean
        """
        check_clean = self.command("status", "--porcelain")
        result = self.run_git_command(check_clean)
        return len(result) == 0

    @property
    def branch(self):
        """
        Return current branch name
        """
        get_branch = self.command("rev-parse", "--abbrev-ref", "HEAD")
        result = self.run_git_command(get_branch)
        return result[0].strip()

    def branch_exists(self, name):
        """
        Return if a branch exists in the local repo or not
        """
        get_branch = self.command("rev-parse", "--verify", name)
        try:
            result = self.run_git_command(get_branch)
        except Exception as exc:
            if "{}".format(exc).find("fatal: Needed a single revision") > -1:
                return False
            raise
        return True

    @classmethod
    def add_arguments(cls, parser, plugin_config):

        shared_parser = argparse.ArgumentParser(add_help=False)
        group = shared_parser.add_mutually_exclusive_group(required=False)
        group.add_argument("--repo-url", type=str)
        group.add_argument("--checkout-path", type=str)

        # subparser that routes operation
        sub = parser.add_subparsers(title="Operation", dest="op")

        # operation `clone`
        op_clone_parser = sub.add_parser(
            "clone", help="clone repo", parents=[shared_parser]
        )

        # operation `pull`
        op_pull_parser = sub.add_parser(
            "pull", help="pull remote", parents=[shared_parser]
        )

        # operation `checkout`
        op_checkout_parser = sub.add_parser(
            "checkout", help="checkout tag or branch", parents=[shared_parser]
        )
        op_checkout_parser.add_argument("tag", nargs=1, help="tag or branch")

    def execute(self, **kwargs):
        super(GitPlugin, self).execute(**kwargs)

        op = kwargs.get("op")

        if kwargs.get("checkout_path"):
            # checkout path was overwritten via input
            self.checkout_path = os.path.abspath(kwargs.get("checkout_path"))

        if kwargs.get("repo_url"):
            # repo url was overwritten via input
            self.repo_url = kwargs.get("repo_url")

        if not op:
            # TODO UsageError
            raise ValueError("operation not defined")

        fn = getattr(self, op)

        if not getattr(fn, "exposed", False):
            raise OperationNotExposed(op)

        del kwargs["op"]

        fn(**kwargs)

    def command(self, *command):
        """
        Prep git command list to use with run_git_command()

        Will automaticdally prepare --git-dir and --work-tree options
        """
        return [
            "git",
            "--git-dir",
            os.path.join(self.checkout_path, ".git"),
            "--work-tree",
            self.checkout_path,
        ] + list(command)

    def run_git_command(self, command):
        """
        Execute git command

        Use command() to prepare command
        """
        proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        stdout = []
        stderr = []
        with proc.stdout:
            for line in iter(proc.stdout.readline, b""):
                stdout.append(line.decode("utf-8").strip())

        with proc.stderr:
            for line in iter(proc.stderr.readline, b""):
                stderr.append(line.decode("utf-8").strip())

        for msg in stdout:
            self.log.info(msg)

        for err in stderr:
            self.log.error(err)

        if stderr:
            if re.search("(error|fatal):", "\n".join(stderr)):
                raise RuntimeError("\n".join(stderr))

        return stdout

    def commit(self, **kwargs):
        """
        Commit changes

        Keyword arguments:
            - files <list>: list of files to commit, should be
                filenames relative to the repo root
            - message <str>: commit message
            - push <bool=True>: push immediately
        """

        files = kwargs.get("files")
        message = kwargs.get("message")

        # TODO: do we still need this in some situations ?
        # files = [os.path.join(self.checkout_path, f) for f in files]

        self.log.debug("COMMIT {} : {}".format(files, message))

        command_add = self.command("add", *files)
        self.run_git_command(command_add)

        command_commit = self.command("commit", *files) + ["-m", message]
        self.run_git_command(command_commit)

        self.log.debug("COMMIT COMPLETE".format(files))
        if kwargs.get("push"):
            self.push()

    @expose("ctl.{plugin_name}.clone")
    def clone(self, **kwargs):
        """
        Clone the repo specified at config.repo_url to config.checkout_path

        Will only clone if there is no valid git repo at ceckout_path
        already
        """

        if self.is_cloned:
            return

        self.log.debug("Cloning {s.repo_url}".format(s=self))
        command = ["git", "clone", self.repo_url, self.checkout_path]

        self.run_git_command(command)

        self.log.debug("Cloned {s.repo_url} in {s.checkout_path}".format(s=self))

    @expose("ctl.{plugin_name}.pull")
    def pull(self, **kwargs):
        """
        Pull the repo
        """
        self.log.debug("PULL {}".format(self.checkout_path))
        command_pull = self.command("pull")
        self.run_git_command(command_pull)
        self.log.debug("PULL {} complete".format(self.checkout_path))

    def push(self, **kwargs):
        """
        Push commits
        """
        self.log.debug("PUSH {}".format(self.checkout_path))
        command_push = self.command("push", "origin", self.branch)
        if kwargs.get("tags"):
            command_push += ["--tags"]
        self.run_git_command(command_push)
        self.log.debug("PUSH {} complete".format(self.checkout_path))

    def tag(self, version, message, **kwargs):
        command_tag = self.command("tag", "-a", version, "-m", message)
        self.run_git_command(command_tag)
        if kwargs.get("push"):
            self.push(tags=True)

    @expose("ctl.{plugin_name}.checkout")
    def checkout(self, branch, **kwargs):
        if not self.branch_exists(branch) and kwargs.get("create"):
            self.run_git_command(self.command("branch", branch))
        command_checkout = self.command("checkout", branch)
        self.run_git_command(command_checkout)

    def merge(self, branch_a, branch_b, **kwargs):
        old_branch = self.branch
        self.checkout(branch_b)
        self.run_git_command(self.command("merge", branch_a))
        if kwargs.get("push"):
            self.push()
        self.checkout(old_branch)
