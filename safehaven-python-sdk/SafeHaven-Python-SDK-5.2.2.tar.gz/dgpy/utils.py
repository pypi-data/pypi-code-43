#
# Helper functions
#
import re
import os
import sys
import time
import yaml
import json
import string

import pwd
import spwd
import crypt
import struct
import socket
import smtplib
import logging
import operator
import collections
import subprocess
import ConfigParser

from itertools       import islice, imap, starmap, tee, groupby, ifilter, ifilterfalse
from cStringIO       import StringIO
from google.protobuf import json_format

#-----------------------------------------------------------------------------------------------
# Files, I/O, Logging
#-----------------------------------------------------------------------------------------------
def init_logging(default_level=logging.INFO, handlers=[], show_time=True):
    """Sets up root logger by adding a console handler.
    @default_level: default console logging level (use logging.DEBUG for highest verbosity)
    @handlers:      additional handlers to register (optional)
    @show_time:     whether to print the timestamp for each console log entry
    """
    root = logging.getLogger()
    if not root.handlers:
        # Logger itself should capture everything.
        root.setLevel(logging.DEBUG)

        # Log >= @default_level to console
        console = logging.StreamHandler()
        console.setLevel(default_level)

        console_fmt = "%(name)-15s  %(levelname)-7s %(message)s"
        if show_time:
                console_fmt = "%(asctime)s " + console_fmt
        console.setFormatter(logging.Formatter(console_fmt))

        # Events to be filtered out on the console
        root.addHandler(console)

    # This function should be idempotent.
    # It relies on addHandler to not add the same handler twice.
    for handler in handlers:
        root.addHandler(handler)
    return root


def die(msg):
    """Pretend that Python is Perl."""
    print >>sys.stderr, msg.rstrip()
    sys.exit(-1)

def fatal(msg):
    die("FATAL: %s" % msg)

def load_protobuf(filename, message):
    """Parses JSON|YAML data contained in @file into the protobuf @message."""
    with open(filename) as f:
        data = f.read()
        if filename.endswith('.yaml'):
            return json_format.ParseDict(yaml.safe_load(data), message)
        elif filename.endswith('.json'):
            return json_format.Parse(data, message)
        die("File name must end either in .json or .yaml (not: '{}').".format(filename))

def get_input(prompt, default=None, type=None, valfnc=None, choices=None):
    """Get user input from stdin. Silently continue prompting if
    - type is present and type conversion threw an exception,
    - valfnc returns negative result,
    - choices are present and response did not match choices.
    @prompt:  prompt string to ask
    @default: default value to return in case no value was entered
    @type:    one-argument conversion function (optional, e.g. str, int, ...)
    @valfnc:  validation function (optional)
    @choices: array of permissible choices (optional)
    """
    if not os.isatty(sys.stdin.fileno()):
        fatal("stdin is not from a terminal - aborting.")
    if default is not None and default != '':
        prompt += ' [%s]' % default
    while True:
        try:
            resp = raw_input(prompt + ': ').strip()
        except (EOFError, KeyboardInterrupt):
            die("... exiting")
        if resp:
            try:
                if type:
                    resp = type(resp)
                if (not valfnc or bool(valfnc(resp))) and (not choices or resp in choices):
                    return resp
            except Exception as e:
                pass
        elif default is not None:
            return default

def parse_key_value_from_fo(fo, allow_whitespace_in_values=False):
    """Read (Syntropy) key/value configuration from file object @fo
    @fo:                          file object to use
    @allow_white_space_in_values: generate error on leading/trailing whitespace in values
    and return a dictionary of mappings.
    """
    config = ConfigParser.RawConfigParser()
    # Preserve case of configuration keys, see
    # http://stackoverflow.com/questions/19359556/configparser-reads-capital-keys-and-make-them-lower-case
    config.optionxform = str

    # Use a fake section.
    # Suggestion from http://stackoverflow.com/questions/2885190/using-pythons-configparser-to-read-a-file-without-section-name
    FAKE_SECTION = 'fake_section'
    ini_str      = '[%s]\n' % FAKE_SECTION
    ini_str     += fo.read()
    fo.close()

    # Strip comments up to end of line.
    ini_fp = StringIO(re.sub('[#;].*$', '', ini_str, flags=re.MULTILINE))
    config.readfp(ini_fp)

    conf = { k:v.strip('"') for k,v in config.items(FAKE_SECTION) }
    if not conf:
        raise LookupError("empty configuration - no items.")
    elif not allow_whitespace_in_values:
        for k,v in conf.iteritems():
            if re.search('(^\s+|\s+$)', v):
                raise ValueError("whitespace in configuration: %s = %r" % (k, v))
    return conf

def TokenizeFile(filename):
    """Split a file into a list of lines. Discards comments starting with '#'.
    Strips leading/trailing whitespace and ignores empty lines.
    """
    return filter(bool, (re.sub('#.*$', '', l).strip() for l in open(filename)))

def first_file_by_stat_key(file_list, stat_fn=os.stat, key='st_mtime'):
    """Order elements in @file_list according to stat-result @key, and return first element.
    @file_list: list of file paths
    @stat_fn:   function to call for obtaining stat results
    @key:       key name (must be one of the attributes in posix.stat_result)
    """
    if file_list:
        return sorted(file_list, key=lambda f: getattr(stat_fn(f), key), reverse=True)[0]

#-----------------------------------------------------------------------------------------------
# General System Administration
#-----------------------------------------------------------------------------------------------
def run_cmd(command, stdin=None, wait=True, **kwargs):
    """Run @command locally.
    @command: command string (all in one), or sequence of program/arguments
    @stdin:   string to pass to stdin of @command
    @wait:    whether to run @command in the background
    @kwargs:  optional keyword arguments to be passed to Popen()

    Returns (exit_code, stdout, stderr) if wait=False, else a Popen object.
    """
    process = subprocess.Popen(args      = command,
                               shell     = isinstance(command, basestring),
                               close_fds = True,
                               stdin     = subprocess.PIPE,
                               stdout    = subprocess.PIPE,
                               stderr    = subprocess.PIPE,
                               **kwargs)
    if not wait:
        return process
    stdout, stderr = process.communicate(stdin if stdin else '')
    # Strip trailing newlines from output.
    return process.returncode, stdout.strip(), stderr.strip()


def system(command, stdin=None):
    """Emulate os.system.
    Returns True if command ran without error, False/None otherwise.
    """
    try:
        rc, stdout, stderr = run_cmd(command, stdin)
        logging.debug(stdout)
        if stderr:
            logging.warning(stderr)
        return rc == 0
    except Exception:
        logging.exception("Command '%r' failed" % command)


def get_current_user():
    """Determine the name of the user running this script.
    Note that os.getlogin() will not do the job, since it looks at the login name, not the UID
    """
    return pwd.getpwuid(os.getuid()).pw_name


def get_process_uid_and_gid(pid):
    """Return (euid, egid) of process @pid.
    Raises an error if @pid does not exist
    """
    pid_dir = os.path.join('/proc', pid)
    if not os.path.isdir(pid_dir):
        raise KeyError("No such PID %d" % pid)
    st = os.stat(pid_dir)
    return st.st_uid, st.st_gid


def check_system_password(user, passwd):
    """Check whether @passwd is the right password for @user."""
    try:
        pw = pwd.getpwnam(user)
    except KeyError:
        fatal("No such user: '%s'" % user)

    if pw.pw_passwd == 'x':   # shadow password
        # In order to read the shadow database, the current user must
        # either be root, or may be a member of the 'shadow' group.
        if not os.access('/etc/shadow', os.R_OK):
            fatal("Insufficient permissions to access shadow database")
        sys_pass = spwd.getspnam(user).sp_pwd
    else:
        sys_pass = pw.pw_passwd
    return crypt.crypt(passwd, sys_pass) == sys_pass

def human_time(sec):
    """Format @sec as a human-readable time string."""
    seconds = abs(int(sec))
    d, h, m = seconds / 86400, (seconds % 86400) / 3600, (seconds % 3600) / 60
    if d:
        if h:
            return '%ud %uh' % (d, h)
        elif m:
            return '%ud %um' % (d, m)
        return '%u day%s' % (d, "" if d == 1 else "s")
    elif h:
        return '%u:%02uh' % (h, m)
    elif m:
        return '%u:%02um' % (m, seconds % 60)
    elif type(sec) is float:
        return '%.2g sec' % sec
    else:
        return "%d sec" % seconds

def lvm_size(str_or_number):
    """Convert a LVM size string/number into the corresponding integral number of bytes.
    For example: 10M -> 10485760, 10GB -> 10737418240
    """
    p = re.compile(r'^(\d+(?:\.\d+)?)\s*(K|KB|M|MB|G|GB|T|TB|B)?$', re.IGNORECASE)
    m = p.match(str(str_or_number))
    if not m:
        raise ValueError("Invalid LVM size: %r" % str_or_number)

    size = float(m.group(1))
    if m.group(2):
        suffix = m.group(2).upper()[0]
        if suffix == 'B':
            pass
        elif suffix == 'K':
            size *= 1024
        elif suffix == 'M':
            size *= 1024**2
        elif suffix == 'G':
            size *= 1024**3
        elif suffix == 'T':
            size *= 1024**4
        else:
            raise TypeError("Invalid LVM suffix %r" % m.group(2))
    return int(round(size))

def to_lvm_size(number_of_bytes, fmt="%.1f"):
    """Inverse of lvm_size() using numeric string format @fmt."""
    size = float(number_of_bytes)
    if size >= 1024**3:
        return (fmt + "G") % (size/1024**3)
    elif size >= 1024**2:
        return (fmt + "M") % (size/1024**2)
    elif size >= 1024:
        return (fmt + "K") % (size/1024)
    return "%dB" % size

def avg(generator_expression):
    """Return the average of the numbers listed in @generator_expression."""
    l = list(generator_expression)
    return sum(l)/len(l) if l else 0

#-----------------------------------------------------------------------------------------------
# Networking
#-----------------------------------------------------------------------------------------------
def get_bound_local_ports_from_fd(fd):
    """Return (listen-IP, port) set of bound TCP/UDPv4 ports. See proc(5).
    @fd: open file descriptor pointing to /proc/net/tcp or /proc/net/udp.
    """
    return set(imap(lambda e: (socket.inet_ntoa(struct.pack("<I", int(e[0], 16))), int(e[1], 16)),
               re.findall('^\s*\d+:\s*([\dA-F]{8}(?:[\dA-F]{24})?):([\dA-F]{4})\s',
                          fd.read(), re.MULTILINE)))

def is_valid_ip(ips):
    """Test whether @ips is a valid IPv4 string"""
    return re.match('(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$', ips)

def is_private_ip(ips):
    """Primitive check to see if @ips is a private IP address (as specified in RFC 1918)."""
    return re.match('^10\.\d{1,3}\.\d{1,3}.\d{1,3}$', ips) or \
           re.match('^192\.168\.\d{123}\.\d{1,3}$', ips)   or \
           re.match('^172.(1[6-9]|2\d|3[0-1])\.\d{1,3}\.\d{1,3}$', ips)

def is_valid_dns_name(hostname):
    """Check if @hostname is a valid DNS name, according to RFCs 952 and 1123:
    * may only contain letters (A-Za-z), digits (0-9), hyphens ('-') and dots ('.')
    * as specified in RFC 1123, may start with a letter or digit,
    * may be up to 63 characters long, should support up to 255 characters.
    See ticket #1031.
    Adapted from http://stackoverflow.com/questions/2532053/validate-a-hostname-string
    """
    if len(hostname) <= 255:
        if hostname.endswith("."):   # A single trailing dot is legal
            hostname = hostname[:-1] # strip exactly one dot from the right, if present
        allowed = re.compile("(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)
        return all(allowed.match(x) for x in hostname.split("."))

def is_valid_port_number(port):
    """Return True if @port evaluates to a number in the range 1..2^16-1"""
    prt = re.compile('\s*(6553[0-5]|655[0-2]\d|65[0-4](\d){2}|6[0-4](\d){3}|[1-5](\d){4}|[1-9](\d){0,3})\s*$')
    return prt.match(str(port))

def find_first_open_port(bind_address='0.0.0.0', port=1024):
    """Look for the first open TCPv4 port
    @bind_address: IPv4 address (not hostname)
    @port:        port number to start at
    """
    assert port > 0
    with open('/proc/net/tcp') as proc_net_tcp:
        bound = get_bound_local_ports_from_fd(proc_net_tcp)

    # Maximum port number is 2^16-1, as TCP uses 2-byte port numbers.
    while port < 1<<16:
        if (bind_address, port) not in bound and ('0.0.0.0', port) not in bound:
            break
        port += 1
    else:
        fatal("Can not find an open TCPv4 port for %s" % bind_address)
    return port

def send_email(subject, body, sender='grenker@datagardens.com'):
    """Send an email with @body and @subject to @sender.
    Low-level email interface (text-based message, no  MIME or attachments at this level).
    """
    # FIXME: mail.datagardens.com has been down since 2015. Add a replacement here.
    die("send_email is defunct since the mail host is down. Please find an SMTP provider")
    # Restrict the maximum body length. Some mailers limit at 1 or 2MB, others at 10,20 or 50MB.
    MAX_BODY_LEN = 1 * 1024**2
    if len(body) > MAX_BODY_LEN:
        tmp = StringIO(body)
        tmp.seek(-MAX_BODY_LEN, 2)
        body = 'WARNING: original message truncated to %d MB due to excessive length (%.1f MB):\n\n' % (
                MAX_BODY_LEN/1024**2, len(body)/1024**2)
        body += tmp.read()
        tmp.close()
    try:
        smtpobj = smtplib.SMTP('mail.datagardens.com', '1025')
        smtpobj.sendmail(sender, sender,
                         'From: %s\n' \
                         'To: %s\n' \
                         'Subject: %s\n\n' \
                         '%s' % (sender, sender, subject, body))
    except Exception as e:
        logging.critical('Failed to send email')

#-----------------------------------------------------------------------------------------------
# Python Extensions
#-----------------------------------------------------------------------------------------------
def enum(*sequential, **named):
    """Create an enum in Python 2.x (in 3.x enums are a basic type).
    From http://stackoverflow.com/questions/36932/how-can-i-represent-an-enum-in-python
    """
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)

def hasmethod(obj, method_name):
    """
    Determine if @object has a method @method_name.
    From http://stackoverflow.com/questions/5963729/check-if-a-function-is-a-method-of-some-object
    """
    return hasattr(obj, method_name) and callable(getattr(obj, method_name))

#-----------------------------------------------------------------------------------------------
# Generator Utilities
#-----------------------------------------------------------------------------------------------
def subseq(seq, l):
    """Generate sequence of 'subsequences' of @seq, each of length @l.
    If the length of @seq does not evenly divide into @l, the last sub-sequence will be shorter.
    """
    idx = 0
    tl  = len(seq)
    while idx < tl:
        yield seq[idx:idx+l]
        idx += l

# 3.3 itertools function
def accumulate(list, sum=0):
    """Return cumulative sums of @list, starting at @sum."""
    for el in list:
        yield sum
        sum += el

def flatten(it):
    """Generator function which turns nested iterable @it into a shallow sequence."""
    for e in it:
        if hasattr(e, '__iter__'):
            for f in flatten(e):
                yield f
        else:
            yield e

def gen_first_n(it, n=10):
    """Return up to the first @n elements of input sequence @it."""
    i = 1
    for el in it:
        if i >= n:
            it.close()
        i += 1
        yield el

def gen_last_n(it, n=10):
    """Return (up to) the last @n elements from input sequence @it."""
    for el in collections.deque(it, n):
        yield el

def partition(seq, func=None):
    """Split @seq into (True-parts, False-parts) depending on @func.
    @seq:  iterable
    @func: Boolean function of one argument or None
    If @func is None, split according to which elements of @seq evaluate to True/False.
    """
    s1, s2 = tee(seq)
    return ifilter(func, s1), ifilterfalse(func, s2)

def field_map(dictseq, key_map):
    """Field mapping function from David Beazley's excellent series on generators
    @dictseq: iterable producing dictionaries
    @key_map: mapping { key -> func } where @key must be a valid key in @dictseq elements
    Produce sequence of dictionaries, with values for keys replaced by function results
    """
    for d in dictseq:
        for key, func in key_map.iteritems():
            d[key] = func(d[key])
        yield d

def invert_dictionary_with_duplicates(d):
    """Invert dictionary @d by generating a map (value, [list-of-keys for value])."""
    key, value = operator.itemgetter(0), operator.itemgetter(1)
    return [ (v, map(key, g)) for v,g in groupby(sorted(d.iteritems(),
                                                        key=value), value) ]

def gen_grep(pat, lines):
    """From the excellent 'Generators for System Programmers' series by David Beazley."""
    patc = re.compile(pat)
    for line in lines:
        if patc.search(line):
            yield line

def gen_upto_mark(it, pred):
    """Produce @nlines of output of input sequence @it until and including when predicate @pred is True."""
    for el in it:
        yield el
        if pred(el):
            it.close()		# Shut down input iterator

def gen_after_mark(it, pred):
    """Generate sequence elements from @it (strictly) after mark indicated by predicate @pred."""
    for el in it:
        if pred(el):
           break
    return it

def nfield(it, n=1):
    """Filter input in @it to produce only the @n-th column (counting fields like awk)."""
    assert n > 0
    for el in it:
        yield el.split()[n-1]

def ifilter_multi(predicates, it, eval_any=False):
    """Like ifilter, but allow a list of @predicates to be evaluated over @it.
    If @eval_any is set, results are OR-ed, else they are AND-ed.
    ifilter_multi([lambda x: x % 2, lambda y: y > 5], range(10))       -> [7, 9]
    ifilter_multi([lambda x: x < 2, lambda y: y > 8], range(10), True) -> [0, 1, 9]
    """
    if not predicates:
        predicates = [bool]
    evaluator = any if eval_any else all
    for i in it:
        if evaluator(pred(i) for pred in predicates):
            yield i


if __name__ == '__main__':
    init_logging()
    logging.info('test')
