from doka.kernel.definition.entities import UnitEntity, StackEntity, ProjectEntity, StackSchema, UnitSchema


def represent_none(self, _):
    return self.represent_scalar('tag:yaml.org,2002:null', '')


def _extract_image_name(repo):
    return repo.split("/").pop().replace('.git', '').split('.').pop().replace('-', '_')


def create_unstacked_stack(project_entity: ProjectEntity):
    from doka.kernel.repository.repositories import StackRepository
    import yaml

    stack_entity = StackEntity(
        name='unstacked',
        project_name=project_entity.name,
        compose_directory=project_entity.metadir.joinpath("stacks"),
        network="default"
    )

    with project_entity.metadir.joinpath("stacks", stack_entity.name).with_suffix('.yml').open('wt') as f:
        yaml.dump(
            {
                "version": '2',
                "services": None,
                "networks": {
                    "_".join([project_entity.name, stack_entity.network]): {
                        "external": True
                    }
                }
            },
            f,
            default_flow_style=False,
            sort_keys=False
        )

        StackRepository(project_entity).save(stack_entity)


def project_post_sync(project_name):
    import json
    import yaml
    import shutil
    import socket
    from doka.kernel.repository.repositories import ProjectRepository

    project_entity = ProjectRepository().get_one(project_name)

    yaml.add_representer(type(None), represent_none)

    stacks = []
    units = []
    hostname = socket.gethostname()
    for entry in project_entity.metadir.joinpath("stacks").glob('**/*.yml'):
        with entry.open('rt') as f:
            yml = yaml.load(f, Loader=yaml.FullLoader)

        stack = StackEntity(
            name=entry.name.replace('.yml', ''),
            project_name=project_name,
            compose_directory=project_entity.metadir.joinpath("stacks"),
            network="default",
            volumes=yml.get("volumes")
        )

        services = yml.get("services")
        for unit_name, unit_settings in services.items():
            unit_entity = UnitEntity(
                name="{}.{}".format(stack.name, unit_name),
                image_name=None,
                project_name=project_name,
                stack_name=stack.name
            )
            unit_settings["networks"] = ["_".join([project_name, stack.network])]
            if "build" in unit_settings:
                image_name = _extract_image_name(unit_settings.get("build"))
                unit_entity.image_name = "_".join([project_name, stack.name, image_name])
                unit_entity.codedir = project_entity.workdir.joinpath(*[stack.name, image_name])
                unit_entity.repo = unit_settings.get("build")
                unit_entity.working_dir = unit_settings.get("working_dir") or '/code'

                unit_settings["image"] = unit_entity.image_name
                unit_settings["env_file"] = ".{}.env".format(unit_entity.name)
                unit_settings["hostname"] = "{}_{}.".format(hostname, unit_name)
                # if not unit_settings.get("volumes"):
                #    unit_settings["volumes"] = []
                # unit_settings["volumes"].append('{}:{}'.format(unit_entity.codedir, unit_entity.working_dir))

                unit_settings.pop("build", None)
                unit_settings.pop("working_dir", None)

            units.append(unit_entity)

        yml["services"] = services

        yml["networks"] = {
            "_".join([project_name, stack.network]): {
                "external": True
            }
        }

        with entry.open("wt") as f:
            yaml.dump(yml, f, default_flow_style=False, sort_keys=False)

        stacks.append(stack)

    with open(project_entity.metadir.joinpath("units.json"), 'wt') as f:
        json.dump(UnitSchema(many=True).dump(units).data, f, indent=2)

    with open(project_entity.metadir.joinpath("stacks.json"), "wt") as f:
        json.dump(StackSchema(many=True).dump(stacks).data, f, indent=2)

    shutil.rmtree(project_entity.metadir.joinpath(".git"))


def move_project_environment_to_stack(project: ProjectEntity):
    import shutil
    shutil.copyfile(
        src=project.metadir.joinpath("environments", ".env.{}".format(project.env)),
        dst=project.metadir.joinpath("stacks", ".env".format(project.env)),
    )


def move_unit_environment_to_stack(unit_entity: UnitEntity):
    from doka.kernel.storage.env import ProjectEnvStorage, UnitEnvStorage, StacksEnvStorage
    from doka.kernel.repository.repositories import ProjectRepository

    project_environment = ProjectEnvStorage(ProjectRepository().get_one(unit_entity.project_name)).read()

    try:
        unit_environment = UnitEnvStorage(unit_entity).read() or {}
    except FileNotFoundError:
        unit_environment = {}
        print("!!!Cannot find .env file for unit {}. Empty environment set".format(unit_entity.name))

    env = {}
    for k, v in unit_environment.items():
        if not v:
            v = project_environment.get(k, v)
        env[k] = v
    StacksEnvStorage(unit_entity).save(env)


def move_unit_environment_to_deploy(project_entity: ProjectEntity, unit_entity: UnitEntity):
    import shutil
    src = unit_entity.codedir.joinpath('.env.example')
    dst = project_entity.metadir.joinpath('deploy', ".{}.env".format(unit_entity.name))
    shutil.copy(src, dst)


def delete_unit_environment_from_stack(unit_entity: UnitEntity):
    from doka.kernel.repository.repositories import ProjectRepository
    project_entity = ProjectRepository().get_one(unit_entity.project_name)
    project_entity.metadir.joinpath(*['stacks', '.{}.env'.format(unit_entity.name)]).unlink()
