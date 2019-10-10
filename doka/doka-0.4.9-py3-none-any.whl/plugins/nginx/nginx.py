import subprocess
from pathlib import Path
from doka.kernel.definition.entities import UnitEntity
from doka.kernel.repository.repositories import UnitRepository
from doka.kernel.definition.entities import ProjectEntity

base_dir = Path(__file__).resolve().parent


def start(project: ProjectEntity, exclude: list = None):
    NginxConfBuilder(exclude).build(project)
    container_name = 'doka_nginx'
    network = '{}_default'.format(project.name)
    subprocess.run(
        "docker stop {name} && docker rm {name} || true".format(
            name=container_name
        ),
        shell=True,
        check=True
    )
    subprocess.run(
        "docker build -t {image_name} --no-cache {directory} && docker run --name {name} --network {network} -p 80:80 -d {image_name}".format(
            name=container_name,
            image_name='{}_{}'.format(container_name, project.name),
            network=network,
            directory=base_dir
        ),
        shell=True,
        check=True
    )


def stop(project: ProjectEntity):
    container_name = 'doka_nginx'
    subprocess.run(
        "docker stop {name} && docker rm {name} || true".format(
            name=container_name
        ),
        shell=True,
        check=True
    )


def _get_host_name(unit_entity: UnitEntity):
    stack_name, unit_name = unit_entity.name.split(".")
    return "{}.local".format(".".join([unit_name, stack_name, unit_entity.project_name]))


def update_hosts(project: ProjectEntity):
    with open('/etc/hosts') as f:
        content = f.read()

    domains = []
    for unit_entity in UnitRepository(project).get():
        if unit_entity.repo:
            domain = _get_host_name(unit_entity)
            if domain not in content:
                domains.append("127.0.0.1\t{}".format(domain))

    if domains:
        with open('/etc/hosts', "at") as f:
            f.write("\n".join(domains))
            f.write("\n")

    return len(domains)


def _read_template(name):
    return base_dir.joinpath(*["templates", name]).with_suffix(".txt").read_text()


def _write_conf(conf):
    base_dir.joinpath(*["conf", "nginx"]).with_suffix(".conf").write_text(conf)


class NginxConfBuilder:
    def __init__(self, exclude: list = None):
        self._conf_template = _read_template('nginx')
        self._templates = {
            'http_server': _read_template('http_server')
        }
        self._exclude = exclude

    def build(self, project: ProjectEntity):
        data = []
        for unit_entity in UnitRepository(project).get():
            if unit_entity.name not in self._exclude and unit_entity.repo:
                data.append(self._build_http_server_template(unit_entity))

        tpls = {"http_servers": "\n\n".join(data)}
        for tpl, val in tpls.items():
            self._conf_template = self._conf_template.replace("[[{}]]".format(tpl), val)

        _write_conf(self._conf_template)

    def _build_http_server_template(self, unit_entity: UnitEntity):
        vars_map = {
            '$external_host': _get_host_name(unit_entity),
            '$internal_host': "http://{}".format(unit_entity.container_name)
        }
        result = self._templates['http_server']
        for tpl, val in vars_map.items():
            result = result.replace(tpl, val)

        return result


if __name__ == "__main__":
    from doka.kernel.repository.repositories import ProjectRepository

    start(ProjectRepository().get_active())
