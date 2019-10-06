import click
import sys
import json
from subprocess import check_output
from pytijo import parser
from pytijo_api_client import command


@click.command(
    name="tijo",
    context_settings=dict(ignore_unknown_options=True, allow_extra_args=True),
    help="Tijo command line. Just execute 'tijo <any-command>' and tijo will the most suitable template to parse the output of the given command. The output is printed in json format.",
)
@click.option(
    "--tijo-template", type=click.File(), help="A tijo template file to be used"
)
@click.option(
    "--tijo-output-beauty", is_flag=True, default=False, help="Beautify json output"
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
@click.option(
    "--tijo-disable-cache",
    is_flag=True,
    default=False,
    help="Disable local cache to force obtaining the template from the Tijo API.",
)
@click.pass_context
def tijo(
    ctx,
    tijo_template,
    tijo_output_beauty,
    tijo_base_api,
    tijo_insecure,
    tijo_timeout,
    tijo_disable_cache,
):
    if len(ctx.args) <= 0 and tijo_template is None:
        print("--tijo-template is required if a command is not provided")
        raise click.Abort()

    template = None
    if tijo_template:
        template = json.load(tijo_template)
    else:
        cmd = command.Command(
            ctx.args,
            tijo_api=tijo_base_api,
            insecure=tijo_insecure,
            timeout=tijo_timeout,
        )
        template = cmd.get_template(disable_cache=tijo_disable_cache)
        if template is None:
            print("template not found")
            raise click.Abort()

    output = None
    if len(ctx.args) <= 0:
        output = "".join(sys.stdin)
    else:
        output = check_output(ctx.args).decode("utf-8")

    result = parser.parse(output, template)
    output = json.dumps(result, indent=4) if tijo_output_beauty else result
    click.echo(output)


def main():
    tijo()


if __name__ == "__main__":
    tijo()
