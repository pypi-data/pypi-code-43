import click

from ejpm.engine.context import pass_ejpm_context
from ejpm.engine.db import PacketStateDatabase


@click.group(invoke_without_command=True)
@pass_ejpm_context
@click.pass_context
def find(ctx, ectx):
    assert (isinstance(ectx.db, PacketStateDatabase))

    db = ectx.db

    click.echo("installed packets:")

    print(db.installed)
    click.echo("missing packets:")
    print(db.missing)

    if not db.top_dir:

        click.echo("Provide the top dir to install things to:")
        click.echo("Run ejpm with --top-dir=<packets top dir>")
        return

    ctx.invoke('root install')



