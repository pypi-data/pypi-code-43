# Info - prints extended information of the EJPM state

import click

from ejpm.engine.context import pass_ejpm_context, EjpmContext
from ejpm.engine.db import INSTALL_PATH
from ejpm.engine.output import markup_print as mprint


_cmake_opt_help = "List packages in terms of CMake flags"
_flag_help_db = "Prints information about ejpm DB"
_flag_help_db_path = "Prints ejpm json DB path"


def _no_flags_set(flag_cmake, flag_db, flag_db_path):
    return flag_cmake and flag_db and flag_db_path


@click.command()
@click.option('--cmake', 'flag_cmake', flag_value='cmake', help=_cmake_opt_help)
@click.option('--db', 'flag_db', flag_value='cmake', help=_cmake_opt_help)
@click.option('--db-path', 'flag_db_path', flag_value='cmake', help=_cmake_opt_help)
@pass_ejpm_context
@click.pass_context
def info(ctx, ectx, flag_cmake, flag_db, flag_db_path):
    """info - Description

    \b
    Example:
      info --cmake
      info --db-path
    """

    if _no_flags_set(flag_cmake, flag_db, flag_db_path):
        flag_db = True

    assert isinstance(ectx, EjpmContext)

    # We need DB ready for this cli command
    ectx.ensure_db_exists()

    if flag_cmake:
        _print_cmake(ectx)


def _print_cmake(ectx):
    db = ectx.db
    pm = ectx.pm

    flag_names_by_packet_names = pm.recipes_by_name["ejana"].cmake_deps_flag_names

    flags = ['-D{}="{}"'.format(flag_names_by_packet_names[name], install_info[INSTALL_PATH])
             for name, install_info in zip(db.packet_names, map(db.get_active_install, db.packet_names))
             if name in flag_names_by_packet_names.keys() and install_info]

    # Fancy print of installed packets
    print(" ".join(flags))


def _print_installed(db):
    installed_names = [name for name in db.packet_names]

    # Fancy print of installed packets
    if installed_names:
        mprint('\n<b><magenta>INSTALLED PACKETS:</magenta></b> (*-active):')
        for packet_name in installed_names:
            mprint(' <b><blue>{}</blue></b>:'.format(packet_name))
            installs = db.get_installs(packet_name)
            for i, installation in enumerate(installs):
                from ejpm.engine.db import IS_OWNED, IS_ACTIVE, INSTALL_PATH

                is_owned_str = '<green>(owned)</green>' if installation[IS_OWNED] else ''
                is_active = installation[IS_ACTIVE]
                is_active_str = '*' if is_active else ' '
                path_str = installation[INSTALL_PATH]
                id_str = "[{}]".format(i).rjust(4) if len(installs) > 1 else ""
                mprint("  {}{} {} {}".format(is_active_str, id_str, path_str, is_owned_str))