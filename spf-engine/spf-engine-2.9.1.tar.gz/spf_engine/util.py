# drop_priviledges (from https://github.com/nigelb/Static-UPnP)
# Copyright (C) 2016  NigelB
# Copyright (C) 2018 Scott Kitterman
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.


def fold(header):
    """Fold a header line into multiple crlf-separated lines at column 72.
    Borrowed from dkimpy and updated to only add \n instead of \r\n because
    that's what the milter protocol wants.

    >>> text(fold('foo'))
    'foo'
    >>> text(fold('foo  '+'foo'*24).splitlines()[0])
    'foo  '
    >>> text(fold('foo'*25).splitlines()[-1])
    ' foo'
    >>> len(fold('foo'*25).splitlines()[0])
    72
    """
    i = header.rfind("\r\n ")
    if i == -1:
        pre = ""
    else:
        i += 3
        pre = header[:i]
        header = header[i:]
    maxleng = 72
    while len(header) > maxleng:
        i = header[:maxleng].rfind(" ")
        if i == -1:
            j = maxleng
        else:
            j = i + 1
        pre += header[:j] + "\n   "
        header = header[j:]
    return pre + header


def user_group(userid):
    """Return user and group from UserID"""
    import grp
    import pwd

    userlist = userid.split(':')
    if len(userlist) == 1:
        gidname = userlist[0]
    else:
        gidname = userlist[1]
    # Get the uid/gid from the name
    running_uid = pwd.getpwnam(userlist[0]).pw_uid
    running_gid = grp.getgrnam(gidname).gr_gid
    return running_uid, running_gid


def drop_privileges(milterconfig):
    import os
    import syslog

    if os.getuid() != 0:
        if milterconfig.get('Syslog'):
            syslog.syslog('drop_privileges: Not root. No action taken.')
        return

    # Get user and group
    uid, gid = user_group(milterconfig.get('UserID'))

    # Remove group privileges
    os.setgroups([])

    # Try setting the new uid/gid
    os.setgid(gid)
    os.setuid(uid)

    # Set umask
    old_umask = os.umask(milterconfig.get('UMask'))


def write_pid(milterconfig):
    """Write PID in pidfile.  Will not overwrite an existing file."""
    import os
    import syslog
    if not os.path.isfile(milterconfig.get('PidFile')):
        pid = str(os.getpid())
        try:
            f = open(milterconfig.get('PidFile'), 'w')
        except IOError as e:
            if str(e)[:35] == '[Errno 2] No such file or directory':
                piddir = milterconfig.get('PidFile').rsplit('/', 1)[0]
                os.mkdir(piddir)
                user, group = user_group(milterconfig.get('UserID'))
                os.chown(piddir, user, group)
                f = open(milterconfig.get('PidFile'), 'w')
                if milterconfig.get('Syslog'):
                    syslog.syslog('PID dir created: {0}'.format(piddir))
            else:
                if milterconfig.get('Syslog'):
                    syslog.syslog('Unable to write pidfle {0}.  IOError: {1}'
                                  .format(milterconfig.get('PidFile'), e))
                raise
        f.write(pid)
        f.close()
        user, group = user_group(milterconfig.get('UserID'))
        os.chown(milterconfig.get('PidFile'), user, group)
    else:
        if milterconfig.get('Syslog'):
            syslog.syslog('Unable to write pidfle {0}.  File exists.'
                          .format(milterconfig.get('PidFile')))
        raise RuntimeError('Unable to write pidfle {0}.  File exists.'
                           .format(milterconfig.get('PidFile')))
    return pid


def own_socketfile(milterconfig):
    """If socket is Unix socket, chown to UserID before dropping privileges"""
    import os
    user, group = user_group(milterconfig.get('UserID'))
    if milterconfig.get('Socket')[:1] == '/':
        os.chown(milterconfig.get('Socket')[1:], user, group)
    if milterconfig.get('Socket')[:6] == "local:":
        os.chown(milterconfig.get('Socket')[6:], user, group)


