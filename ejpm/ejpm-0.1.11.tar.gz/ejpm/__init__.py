import os
import click

from ejpm.engine.context import pass_ejpm_context, DB_FILE_PATH, ENV_CSH_PATH, ENV_SH_PATH, EjpmContext
from ejpm.engine.db import PacketStateDatabase
from ejpm.engine.output import markup_print as mprint


def print_first_time_message():
    mprint("""
The database file doesn't exist. Probably you run 'ejpm' for one of the first times.

1. Install or check OS maintained required packages:
    > ejpm req ubuntu         # for all packets ejpm knows to built/install
    > ejpm req usubnu ejana   # for ejana and its dependencies only
   
   * - at this point put 'ubuntu' for debian and 'centos' for RHEL and CentOS systems. 
   Will be updated in future to support macOS, and to have grained versions

1. Set <b><blue>top-dir</blue></b> to start. This is where all missing packets will be installed.   

   > ejpm --top-dir=<where-to-install-all>
   
2. You may have CERN.ROOT installed (req. version >= 6.14.00). Run this:

   > ejpm set root `$ROOTSYS`
   
   You may set paths for other installed dependencies:
   > ejpm install ejana --missing --explain    # to see missing dependencies
   > ejpm set <name> <path>                    # to set dependency path
   
3. Then you can install all missing dependencies:

   > ejpm install ejana --missing
   

P.S - you can read this message by adding --help-first flag
    - EJPM gitlab: https://gitlab.com/eic/ejpm
    - This message will disappear after running any command that make changes
    """)
    click.echo()


_starting_workdir = ""

def _print_packets_info(db):
    """Prints known installations of packets and what packet is selected"""

    from ejpm.engine.db import IS_OWNED, IS_ACTIVE, INSTALL_PATH
    assert (isinstance(db, PacketStateDatabase))

    installed_names = [name for name in db.packet_names]

    # Fancy print of installed packets
    if installed_names:
        mprint('\n<b><magenta>INSTALLED PACKETS:</magenta></b> (*-active):')
        for packet_name in installed_names:
            mprint(' <b><blue>{}</blue></b>:'.format(packet_name))
            installs = db.get_installs(packet_name)
            for i, installation in enumerate(installs):
                is_owned_str = '<green>(owned)</green>' if installation[IS_OWNED] else ''
                is_active = installation[IS_ACTIVE]
                is_active_str = '*' if is_active else ' '
                path_str = installation[INSTALL_PATH]
                id_str = "[{}]".format(i).rjust(4) if len(installs) > 1 else ""
                mprint("  {}{} {} {}".format(is_active_str, id_str, path_str, is_owned_str))


    not_installed_names = [name for name in db.known_packet_names if name not in installed_names]

    # Fancy print of installed packets
    if not_installed_names:
        mprint("\n<b><magenta>NOT INSTALLED:</magenta></b>\n(could be installed by 'ejpm install')")
        for packet_name in not_installed_names:
            mprint(' <b><blue>{}</blue></b>'.format(packet_name))


@click.group(invoke_without_command=True)
@click.option('--debug/--no-debug', default=False)
@click.option('--top-dir', default="")
@pass_ejpm_context
@click.pass_context
def ejpm_cli(ctx, ectx, debug, top_dir):
    """EJPM stands for EIC Jana Packet Manager"""

    assert isinstance(ectx, EjpmContext)    # Type check for ectx

    # Load db and modules from disk
    db_existed = ectx.load_shmoad_ugly_toad()    # False => Couldn't load and used default

    # user asks to set the top dir
    if top_dir:
        ectx.db.top_dir = os.path.abspath(os.path.normpath(top_dir))
        ectx.db.save()
        db_existed = True

    # check if DB file already exists
    if not db_existed:
        print_first_time_message()
    else:
        # if there is no commands and we loaded the DB lets print some info:
        if ctx.invoked_subcommand is None:
            from ejpm.version import version
            mprint("<b><blue>EJPM</blue></b> v{}".format(version))
            mprint("<b><blue>top dir :</blue></b>\n  {}", ectx.db.top_dir)
            mprint("<b><blue>state db :</blue></b>\n  {}", ectx.config[DB_FILE_PATH])
            mprint("  (users are encouraged to inspect/edit it)")
            mprint("<b><blue>env files :</blue></b>\n  {}\n  {}", ectx.config[ENV_SH_PATH], ectx.config[ENV_CSH_PATH])
            _print_packets_info(ectx.db)


from ejpm.cli.env import env as env_group
from ejpm.cli.install import install as install_group
from ejpm.cli.find import find as find_group
from ejpm.cli.req import req as requirements_command
from ejpm.cli.set import set as set_command
from ejpm.cli.rm import rm as rm_command
from ejpm.cli.pwd import pwd as pwd_command
from ejpm.cli.clean import clean as clean_command
from ejpm.cli.info import info as info_command
from ejpm .cli.config import config as config_command

ejpm_cli.add_command(install_group)
ejpm_cli.add_command(find_group)
ejpm_cli.add_command(env_group)
ejpm_cli.add_command(requirements_command)
ejpm_cli.add_command(set_command)
ejpm_cli.add_command(rm_command)
ejpm_cli.add_command(pwd_command)
ejpm_cli.add_command(clean_command)
ejpm_cli.add_command(info_command)
ejpm_cli.add_command(config_command)

if __name__ == '__main__':
    ejpm_cli()
