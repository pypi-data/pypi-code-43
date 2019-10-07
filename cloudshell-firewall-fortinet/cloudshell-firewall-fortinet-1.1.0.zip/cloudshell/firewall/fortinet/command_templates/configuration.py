import re

from cloudshell.cli.command_template.command_template import CommandTemplate


BACKUP_CONF = CommandTemplate(
    'execute backup config '
    '[flash{flash} {file_name}]'  # file system
    '[ftp{ftp} {file_path} {host}][:{port}][ {user}][ {password}]'
    '[tftp{tftp} {file_path} {host}]',
    error_map={
        r'fail': 'Fail to backup config',
        r'^((?!(OK|done)).)*$': 'Fail to copy a file',
    }
)

RESTORE_CONF = CommandTemplate(
    'execute restore config '
    '[flash{flash} {revision_id}]'  # file system
    '[ftp{ftp} {file_path} {host}][:{port}][ {user}][ {password}]'
    '[tftp{tftp} {file_path} {host}]',
    action_map={
        re.escape('(y/n)'): lambda session, logger: session.send_line('y', logger),
    },
    error_map={
        r'fail': 'Fail to restore config',
    }
)

SHOW_REVISIONS = CommandTemplate('execute revision list config')

LOAD_FIRMWARE = CommandTemplate(
    'execute restore image '
    '[flash{flash} {revision_id}]'  # file system
    '[ftp{ftp} {file_path} {host}][:{port}][ {user}][ {password}]'
    '[tftp{tftp} {file_path} {host}]',
    action_map={
        re.escape('(y/n)'): lambda session, logger: session.send_line('y', logger),
    },
    error_map={
        r'fail': 'Fail to load firmware',
    }
)
