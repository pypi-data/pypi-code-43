import os
import subprocess


class WhatchaReadinPaths:
    _resources = "resources"
    _config = "wr-config.ini"
    _hook_filename = "commit_msg.py"
    _hook_filename_dest = "commit-msg"

    @staticmethod
    def get_git_root_dir() -> str:
        try:
            return (
                subprocess.check_output(
                    ["git", "rev-parse", "--show-toplevel"], stderr=subprocess.STDOUT
                )
                .decode()
                .strip()
            )
        except subprocess.CalledProcessError:
            raise

    @staticmethod
    def get_resources_dir() -> str:
        current = os.path.dirname(os.path.realpath(__file__))
        return os.path.join(current, WhatchaReadinPaths._resources)

    @staticmethod
    def get_src_hook_path() -> str:
        resources = WhatchaReadinPaths.get_resources_dir()
        return os.path.join(resources, WhatchaReadinPaths._hook_filename)

    @staticmethod
    def get_hook_path() -> str:
        git_root_dir = WhatchaReadinPaths.get_git_root_dir()
        return os.path.join(
            git_root_dir, ".git", "hooks", WhatchaReadinPaths._hook_filename_dest
        )

    @staticmethod
    def get_config_path() -> str:
        git_root_dir = WhatchaReadinPaths.get_git_root_dir()
        return os.path.join(git_root_dir, ".git", "hooks", WhatchaReadinPaths._config)
