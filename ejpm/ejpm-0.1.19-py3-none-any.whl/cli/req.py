
import click

from ejpm.engine.context import pass_ejpm_context, EjpmContext
from ejpm.engine.output import markup_print as mprint

# @click.group(invoke_without_command=True)
@click.command()
@click.argument('os_name', nargs=1, metavar='<os-name>')
@click.argument('args', nargs=-1, metavar='<packet-names>')
@click.option('--optional', 'print_mode', flag_value='optional', help="Print optional packages")
@click.option('--required', 'print_mode', flag_value='required', help="Print required packages")
@click.option('--all', 'print_mode', flag_value='all', help="Print all packages (ready for packet manager install)")
@click.option('--all-titles', 'print_mode', flag_value='all_titles', help="Print all packages (human readable)", default=True)
@pass_ejpm_context
@click.pass_context
def req(ctx, ectx, os_name, args, print_mode):
    """req - Shows required packages that can be installed by operating system.

    \b
    Example:
      req ubuntu ejana
      req centos ejana
      req centos root clhep

    By adding --optional, --required, --all flags you can use this command with packet managers:
      req


    """

    assert isinstance(ectx, EjpmContext)

    # We need DB ready for this cli command
    ectx.ensure_db_exists()

    # We have some args, first is os name like 'ubuntu' or 'centos'
    known_os = ectx.pm.os_deps_by_name['ejana']['required'].keys()

    if os_name not in known_os:
        mprint('<red><b>ERROR</b></red>: name "{}" is unknown\nKnown os names are:', os_name)
        for name in known_os:
            mprint('   {}', name)
        click.echo(ctx.get_help())
        ctx.exit(1)

    # We have something like 'ubuntu ejana'
    if args:
        names = []
        for packet_name in args:                                    # get all dependencies
            ectx.ensure_installer_known(packet_name)
            names += ectx.pm.get_installation_chain_names(packet_name)    # this func returns name + its_deps

        names = list(set(names))                                    # remove repeating names

    else:
        names = ectx.pm.recipes_by_name.keys()                   # select all packets

    _print_combined(ectx, os_name, names, print_mode)               # print what we have


def _print_combined(ectx, os_name, packet_names, print_mode):

    required = []
    optional = []
    for name in packet_names:
        required.extend(ectx.pm.os_deps_by_name[name]['required'][os_name].split(' ,'))
        optional.extend(ectx.pm.os_deps_by_name[name]['optional'][os_name].split(' ,'))

    # remove emtpy elements and repeating elements
    required = list(set([r for r in required if r]))
    optional = list(set([o for o in optional if o]))

    if print_mode == "optional":
        mprint(" ".join(optional))
    elif print_mode == "required":
        mprint(" ".join(required))
    elif print_mode == "all":
        mprint(" ".join(optional + required))
    else:
        # print all with juman readable titles
        mprint("<blue><b>REQUIRED</b></blue>:")
        mprint(" ".join(optional))
        mprint("<blue><b>OPTIONAL</b></blue>:")
        mprint(" ".join(required))
