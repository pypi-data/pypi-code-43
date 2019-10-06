import click
import json
from pytijo_api_client import command


@click.command(
    name="tijo-push",
    context_settings=dict(ignore_unknown_options=True, allow_extra_args=True),
    help="Tijo push command line to upload new templates. tijo-push <template> <any-command>",
)
@click.argument("tijo-template", type=click.File())
@click.option(
    "--tijo-tags", is_flag=True, default=False, help="Tags separated by whitespaces."
)
@click.option(
    "--tijo-include-default-facts",
    is_flag=True,
    default=False,
    help="Add default facts base on this system.",
)
@click.option(
    "--tijo-fact-system", type=click.STRING, default=None, help="Add given system fact."
)
@click.option(
    "--tijo-fact-kernel", type=click.STRING, default=None, help="Add given kernel fact."
)
@click.option(
    "--tijo-fact-machine", type=click.STRING, default=None, help="Add machine fact."
)
@click.option(
    "--tijo-fact-python-version",
    type=click.STRING,
    default=None,
    help="Add python version fact.",
)
@click.option(
    "--tijo-fact-command-path",
    type=click.STRING,
    default=None,
    help="Add command path fact.",
)
@click.option(
    "--tijo-fact-command-path-filesize",
    type=click.STRING,
    default=None,
    help="System fact",
)
@click.option(
    "--tijo-base-api",
    type=click.STRING,
    default="http://api.tijo.io/v1",
    envvar="TIJO_API",
    help="Tijo base REST API endpoint",
)
@click.option(
    "--tijo-insecure",
    is_flag=True,
    default=False,
    help="Allow insecure https connections. SSL certificates are not validated if this option is given.",
)
@click.option("--tijo-timeout", type=click.INT, default=60, help="HTTP(s) timeout")
@click.pass_context
def tijo_push(
    ctx,
    tijo_template,
    tijo_tags,
    tijo_include_default_facts,
    tijo_fact_system,
    tijo_fact_kernel,
    tijo_fact_machine,
    tijo_fact_python_version,
    tijo_fact_command_path,
    tijo_fact_command_path_filesize,
    tijo_base_api,
    tijo_insecure,
    tijo_timeout,
):
    if len(ctx.args) <= 0:
        print("command must be provided.")
        raise click.Abort()

    template = json.load(tijo_template)
    cmd = command.Command(
        ctx.args,
        tijo_api=tijo_base_api,
        insecure=tijo_insecure,
        timeout=tijo_timeout,
        template=template,
    )

    facts = {}
    if tijo_fact_system:
        facts["system"] = tijo_fact_system
    if tijo_fact_kernel:
        facts["kernel"] = tijo_fact_kernel
    if tijo_fact_machine:
        facts["machine"] = tijo_fact_machine
    if tijo_fact_python_version:
        facts["python_version"] = tijo_fact_python_version
    if tijo_fact_command_path:
        facts["command_path"] = tijo_fact_command_path
    if tijo_fact_command_path_filesize:
        facts["command_path_filesize"] = tijo_fact_command_path_filesize

    template = cmd.push_template(
        tags=tijo_tags if tijo_tags else None,
        facts=facts if len(facts) > 0 else None,
        facts_attributes=command.DEFAULT_FACTS if tijo_include_default_facts else None,
    )

    if template is not None and "id" in template:
        click.echo(
            "template with id '{}' has been pushed successfully.".format(template["id"])
        )
    else:
        print("template has not been pushed found")
        raise click.Abort()


def main():
    tijo_push()


if __name__ == "__main__":
    tijo_push()
