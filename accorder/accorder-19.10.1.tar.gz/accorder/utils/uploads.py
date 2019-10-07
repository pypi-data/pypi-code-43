import subprocess
from threading import Thread
import time
import os
from dataclasses import dataclass
import click
from accorder.utils.configs import edit_config
from accorder.utils.configs import check_sections


@dataclass(init=False)
class RsyncTunneled:
    tunnel_port_forward: str
    tunnel_account: str
    tunnel_ssh_port: str
    rsync_password: str
    rsync_local_directory: str
    rsync_user: str
    rsync_endpoint: str
    start_time: str
    rsync_delete: str
    keep_thread: bool = True
    keep: bool = True
    timeout: int = 10

    def run_ssh(self):
        def _setup_timeout(ssh_process):
            self.start_time = time.time()
            while self.keep_thread:
                delta = "*" * (self.timeout - round(time.time() - self.start_time))
                click.echo(
                    "\rConnecting: [{}] ".format(delta.ljust(self.timeout, " ")),
                    nl=False,
                )
                if round(time.time() - self.start_time, 3) > self.timeout:
                    self.keep_thread = False
                    self.keep = False
                    ssh_process.terminate()

        self.ssh_process = subprocess.Popen(
            [
                "ssh",
                "-v",
                "-N",
                "-o",
                "ExitOnForwardFailure=yes",
                "-o",
                "ServerAliveINterval=60",
                "-o",
                "TCPKeepAlive=yes",
                "-o",
                "StrictHostKeyChecking=no",
                "-o",
                "UserKnownHostsFile=/dev/null",
                "-L",
                self.tunnel_port_forward,
                self.tunnel_account,
                "-p",
                self.tunnel_ssh_port,
            ],
            stderr=subprocess.PIPE,
            universal_newlines=True,
            bufsize=0,
        )

        counter = Thread(target=_setup_timeout, args=(self.ssh_process,))
        counter.start()

        line = ""
        while self.keep:
            rbytes = self.ssh_process.stderr.read(1)
            line += rbytes
            if rbytes == "\n":
                if "Entering interactive session." in line.strip():
                    self.keep_thread = False
                    click.echo("\rSecure connection established.")
                    self.keep = False
                    break
                elif "Address already in use" in line.strip():
                    self.keep_thread = False
                    click.echo(
                        "\rLocal port 8873 is already in use. Close the process to release the port and then try again."
                    )
                    self.keep = False
                    return False

                line = ""

        time.sleep(1)
        if self.ssh_process.poll() is not None:
            click.echo("\rSSH tunnel failed. Check your internet connection.")
            return False

        return True

    def run_rsync(self):
        click.echo(
            f"\nLocal: {self.rsync_local_directory}\nRemote: {self.tunnel_port_forward}\n"
        )
        os.environ["RSYNC_PASSWORD"] = self.rsync_password
        command = f"rsync -zvrith --progress {self.rsync_delete} --inplace --no-whole-file {self.rsync_local_directory} rsync://{self.rsync_user}@localhost:8873/{self.rsync_endpoint}/"
        # click.echo(command)
        os.system(command)
        self.ssh_process.terminate()
        click.echo("")


@dataclass(init=False)
class Rclone:
    rclone_configuration: str
    rclone_profile: str
    rclone_url: str
    rclone_local_directory: str
    rclone_copy_or_sync: str

    def run_rclone(self):
        click.echo(
            f"\nLocal: {self.rclone_local_directory}\nRemote: {self.rclone_url}\n"
        )
        command = f"rclone --config={self.rclone_configuration} {self.rclone_copy_or_sync} --fast-list --progress --checkers 64 {self.rclone_local_directory} {self.rclone_profile}_rclone:"
        os.system(command)
        click.echo("")


def run_upload(app_name, profile, directory, delete_residue):
    config = edit_config(app_name, profile, directory=directory)
    sections = check_sections(config, profile)

    if "rsync" not in sections and "rclone" not in sections:
        click.echo(f"{profile} doesn't have any configuration set for the upload. Check out: `accorder configuration --help`")
        click.get_current_context().exit()

    motw_message = ""
    if "motw" in sections:
        motw_subdomain = config[profile]["motw"]["subdomain"]
        motw_domain = config[profile]["motw"]["domain"]
        motw_message = f"TO https://{motw_subdomain}.{motw_domain}"

    click.echo(f">>>> UPLOAD FILES {motw_message}")
    if config[profile]["meta"]["upload"] == "rsync":
        click.echo(">>>> VIA RSYNC")
        r = RsyncTunneled()
        r.tunnel_port_forward = config[profile]["tunnel"]["port_forward"]
        r.tunnel_account = config[profile]["tunnel"]["account"]
        # r.tunnel_account = "tunnel@1.1.1.1"
        r.tunnel_ssh_port = config[profile]["tunnel"]["ssh_port"]

        r.rsync_password = config[profile]["rsync"]["password"]
        r.rsync_local_directory = config[profile]["calibre"]["local_directory"]
        r.rsync_user = config[profile]["rsync"]["user"]
        r.rsync_endpoint = config[profile]["rsync"]["endpoint"]
        r.rsync_delete = ""
        if delete_residue:
            r.rsync_delete = "--delete"

        ssh = r.run_ssh()
        if ssh:
            r.run_rsync()
    elif config[profile]["meta"]["upload"] == "rclone":
        click.echo(">>>> VIA RCLONE")
        r = Rclone()
        r.rclone_profile = profile
        r.rclone_url = config[profile]["rclone"]["url"]
        r.rclone_local_directory = config[profile]["calibre"]["local_directory"]
        r.rclone_configuration = os.path.join(
            click.get_app_dir(app_name), "accorder.ini"
        )
        r.rclone_copy_or_sync = "copy"
        if delete_residue:
            r.rclone_copy_or_sync = "sync"
        r.run_rclone()
