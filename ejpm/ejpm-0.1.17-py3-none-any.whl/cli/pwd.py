import os

import click

from ejpm.engine.context import pass_ejpm_context, EjpmContext
from ejpm.engine.output import markup_print as mprint


# @click.group(invoke_without_command=True)
@click.command()
@click.argument('packet_names', nargs=-1, metavar='<packet-name>')
@pass_ejpm_context
@click.pass_context
def pwd(ctx, ectx, packet_names):
    """Shows a directory related to the active packet

    Remark:
        Running `ejpm` command shows the directories too, but this command shows the dir
        for a package and can be used in scripts and whatsoever

    Usage:
        ejpm cd                  # cd-s to ejpm top dir
        ejpm cd <packet-name>    # cd-s to <packet-name> installation dir

    """
    from ejpm.engine.db import INSTALL_PATH, IS_OWNED, SOURCE_PATH, BUILD_PATH
    assert isinstance(ectx, EjpmContext)

    # We need DB ready for this cli command
    ectx.ensure_db_exists()

    # Check that the packet name is from known packets
    if not packet_names:
        pwd_path = ectx.db.top_dir
        mprint(pwd_path)

    else:
        # Get installation data for the active install
        packet_name = packet_names[0]
        ectx.ensure_installer_known(packet_name)
        install_data = ectx.db.get_active_install(packet_name)
        if not install_data:
            mprint("No active installation data found for the packet '{}'", packet_name)
            raise click.Abort()

        # If ejpm 'owns' an installation at this point we assume that parent directory usually is needed
        # Like if ejpm owns 'root' it is assumed that <top-dir>/root is needed rather than <top-dir>/root/root-v6-...
        pwd_path = install_data[INSTALL_PATH]
        mprint("<blue><b>Install path: </b></blue>\n{}", pwd_path)

        if install_data[IS_OWNED]:
            pwd_path = os.path.dirname(pwd_path)
            mprint("<blue><b>EJPM 'owned' base path: </b></blue>\n{}", pwd_path)

        # Source path if known
        if SOURCE_PATH in install_data:
            mprint("<blue><b>Sources: </b></blue>\n{}", install_data[SOURCE_PATH])

        if BUILD_PATH in install_data:
            mprint("<blue><b>Build dir: </b></blue>\n{}", install_data[BUILD_PATH])

    # os.chdir(cd_path)




