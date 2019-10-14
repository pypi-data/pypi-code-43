import click
import api


@click.group(invoke_without_command=True)
@click.pass_context
def cli_main(ctx):
    if ctx.invoked_subcommand is None:
        api.main()


@cli_main.command()
@click.option('--original', '-o', is_flag=True)
def highlight(original):
    api.main(True, original)


if __name__ == '__main__':
    cli_main()
