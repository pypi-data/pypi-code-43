import os
import shutil
import subprocess
import tempfile
import platform
import time

IS_WINDOWS = platform.system() == "Windows"


def envs_to_cmdline(envs):
    cmdline = []
    for env in envs:
        value = envs[env]
        if value:
            cmdline.extend(["-e", "{}={}".format(env, value)])
        else:
            cmdline.extend(["-e", env])
    return cmdline


def start(image, folder, envs, priv, entrypoint=None):
    """
    Run a container as root and leave it in the background
    :param image:
    :param folder:
    :param envs:
    :param: priv:
    :param: entrypoint
    :return:
    """
    cmdline = ["docker", "run", "-d", "--rm",
               "-w", folder,
               "-v", "{}:{}".format(folder, folder)
               ]

    cmdline.extend(envs_to_cmdline(envs))

    if not IS_WINDOWS:
        if entrypoint:
            cmdline.extend(["--entrypoint", entrypoint])
        if priv:
            cmdline.append("--privileged")

        cmdline.append("-t")

    cmdline.append(image)

    if IS_WINDOWS:
        # should wait forever
        cmdline.extend(["powershell", "-Command", "Wait-Event"])
    else:
        cmdline.extend(["sleep", "infinity"])

    container_id = subprocess.check_output(cmdline).decode().strip()
    return container_id


def execute(container, uid, workdir, envs, commandline, interactive=False, priv=False):
    """
    Execute a command with interactive tty
    :param container:
    :param uid:
    :param workdir:
    :param envs: a list of NAME=VALUE pairs (passed to docker exec as `-e X=Y`
    :param commandline:
    :param priv:
    :param interactive:
    :return:
    """
    if not commandline:
        if not IS_WINDOWS:
            commandline = ["/bin/sh"]
        else:
            commandline = ["C:\\WINDOWS\\system32\\cmd.exe"]

    cmdline = ["docker", "exec", "-w", workdir]

    if not IS_WINDOWS:
        cmdline.extend(["-u", str(uid)])
        if priv:
            cmdline.append("--privileged")

    cmdline.extend(envs_to_cmdline(envs))

    if interactive:
        cmdline.append("-i")

    cmdline.append("-t")
    cmdline.append(container)
    cmdline.extend(commandline)

    rv = subprocess.call(cmdline)
    return rv


def add_user(container, uid, gid, username):
    """
    Add a user to the container by editing it's etc passwd
    :param container:
    :param uid:
    :param username:
    :return:
    """
    temp = tempfile.mkdtemp()
    try:
        cmdline = ["docker", "cp", "{}:/etc/passwd".format(container), temp]
        subprocess.check_call(cmdline)
        with open(os.path.join(temp, "passwd"), "a") as tf:
            tf.write("{}:x:{}:{}:docker user:/tmp:/bin/sh\n".format(
                username, uid, gid
            ))
        cmdline = ["docker", "cp", os.path.join(temp, "passwd"), "{}:/etc/passwd".format(container)]
        subprocess.check_call(cmdline)
    finally:
        shutil.rmtree(temp)


def stop(container):
    """
    Kill a container
    :param container:
    :return:
    """
    cmdline = ["docker", "kill", container]
    try:
        subprocess.check_output(cmdline)
    except subprocess.CalledProcessError:
        pass


class Container(object):
    """
    Represent a dockhere controlled container
    """

    def __init__(self, image, cwd, envs, priv=False, root=False):
        self.image = image
        self.cwd = cwd
        self.id = None
        self.priv = priv
        self.root = root
        env_dict = {}
        if envs:
            for item in envs:
                if "=" in item:
                    name, value = item.split("=", 1)
                    env_dict[name] = value
                else:
                    env_dict[item] = None
        self.envs = env_dict
        self.entrypoint = None
        self.uid = 0

    def stop(self):
        """
        Stop the container
        :return:
        """
        if self.id:
            stop(self.id)

    def start(self):
        """
        Launch the container
        :return:
        """
        self.id = start(self.image, self.cwd, self.envs, self.priv, entrypoint=self.entrypoint)
        try:
            if not IS_WINDOWS:
                if self.root:
                    self.envs["USER"] = "root"
                else:
                    import getpass
                    self.uid = os.getuid()
                    username = getpass.getuser()
                    add_user(self.id, self.uid, os.getgid(), username)
                    self.envs["USER"] = username
        except Exception:
            self.stop()
            raise

        # wait a few seconds in case the container dies instantly
        time.sleep(3)
        # use docker inspect to make sure it is still alive
        subprocess.check_output(["docker", "inspect", self.id])

        return self.id

    def execute(self, args, interactive=False):
        """
        Execute a command in the container
        :param args:
        :param interactive:
        :return:
        """
        try:
            return execute(self.id, self.uid, self.cwd, self.envs, args, interactive=interactive, priv=self.priv)
        finally:
            self.stop()
