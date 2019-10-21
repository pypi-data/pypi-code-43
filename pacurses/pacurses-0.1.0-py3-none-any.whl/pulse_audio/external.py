import subprocess


def _call_external_command(command):
    return (
        subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        .stdout.read()
        .decode("utf-8")
    )


def call_pacmd(command):
    return _call_external_command("pacmd {0}".format(command))
