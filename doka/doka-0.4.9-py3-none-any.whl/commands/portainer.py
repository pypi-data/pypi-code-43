import subprocess


class Portainer(object):
    def up(self):
        subprocess.run(
            "docker volume create portainer_data || true",
            shell=True,
            check=True,
            stderr=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL
        )
        subprocess.run(
            "if docker inspect portainer | grep exited > /dev/null; then docker restart portainer; fi",
            shell=True,
            check=True,
            stderr=subprocess.DEVNULL
        ),
        subprocess.run(
            "if "
            "docker inspect -f '{{.State.Running}}' portainer | grep true > /dev/null; then echo \"Nothing to do, portainer is running\"; "
            "else "
            "docker run -d --name portainer -p 9100:9000 -v /var/run/docker.sock:/var/run/docker.sock -v portainer_data:/data portainer/portainer && echo \"Portainer has started\"; "
            "fi",
            shell=True,
            check=True,
            stderr=subprocess.DEVNULL
        )

    def down(self):
        subprocess.run(
            "docker stop portainer && docker rm portainer",
            shell=True,
            check=True
        )
