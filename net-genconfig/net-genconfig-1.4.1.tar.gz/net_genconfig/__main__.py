# net_genconfig.__main__


import net_genconfig

import argparse
from copy import deepcopy
import datetime
import jinja2
import os
import re
import sys
import yaml

from net_genconfig.deepops import deepmerge, deepremoveitems

from net_genconfig import netaddr_filter



# --- functions ---



def raise_exception(e):
    """Simple function to raise the specified exception.  This is used
    for the parameter onerror for os.walk(), which otherwise ignores
    errors and skips over problematic directory entries.
    """

    raise e


def warn_helper(msg):
    """Helper function to print a warning inside a Jinja2 template.  The
    supplied message is printed to stderr but execution is not stopped.

    Keyword arguments:

    msg -- warning message to display
    """

    print("warning: " + msg, file=sys.stderr)


    # helper functions return a string to be included in the template; we don't
    # particularly have anything to include but have to return something, so we
    # return an empty string

    return ""


def raise_helper(msg):
    """Helper function to raise an exception inside a Jinja2 template.  The
    generic 'Exception' class is raised in Python.

    Keyword arguments:

    msg -- exception message to display when aborting
    """

    raise Exception(msg)


def assert_helper(condition, msg):
    """Helper function for assertions inside a Jinja2 template.  If the
    supplied condition is False, an exception is raised with the given
    error message.  The 'AssertionError' class is raised by Python.

    If the condition is True, an empty string is returned to avoid
    printing anything.

    Keyword arguments:

    condition -- the condition which must be satisfied to not raise the
    exception

    msg -- message to display in the event of the condition not being
    true
    """

    if not condition:
        raise AssertionError(msg)

    return ""


def re_match_helper(pattern, string):
    """Helper function for matching strings against regular expressions
    in a Jinja2 template.  The regular expression is compiled and
    matched against the supplied string (the Python regular expression
    library caches compiled strings for efficiency) and a boolean is
    returned, indicating whether the match succeeded or not.

    Keyword arguments:

    pattern -- the regular expression to match against

    string -- the string to match against
    """

    return bool(re.match(pattern, string))


def re_match_groups_helper(pattern, string):
    """Helper function for matching strings against regular expressions
    and extract groups of (separated by parentheses) in a Jinja2
    template.  The regular expression is compiled and matched against
    the supplied string (the Python regular expression library caches
    compiled strings for efficiency) and the groups in the expression
    are returned in the form of a list.

    Keyword arguments:

    pattern -- the regular expression to match against; the required
    groups to return should be specified using parentheses

    string -- the string to match and return the groups of
    """

    r = re.match(pattern, string)

    if r is None:
        raise ValueError("'%s' does not match regular expression '%s'" %
                             (string, pattern))

    return r.groups()



# --- command line arguments ---



# create the parser and add in the available command line options

parser = argparse.ArgumentParser(
    # override the program name as running this as a __main__ inside a module
    # directory will use '__main__' by default - this name isn't necessarily
    # correct, but it looks better than that
    prog="net-genconfig",

    # we want the epilog help output to be printed as it and not reformatted or
    # line wrapped
    formatter_class=argparse.RawDescriptionHelpFormatter)


parser.add_argument(
    "-r", "--roles",
    default=((os.environ.get("NET_CONFIG_DIR") + "/roles")
                 if "NET_CONFIG_DIR" in os.environ else "roles"),
    help="directory containing role configuration templates")

parser.add_argument(
    "-n", "--include",
    default=((os.environ.get("NET_CONFIG_DIR") + "/include")
                 if "NET_CONFIG_DIR" in os.environ else "include"),
    help="directory containing included templates / macro libraries")

parser.add_argument(
    "-i", "--inventory",
    default=((os.environ.get("NET_CONFIG_DIR") + "/inventory")
                 if "NET_CONFIG_DIR" in os.environ else "inventory"),
    help="directory containing inventory of devices, networks, etc.")

parser.add_argument(
    "-o", "--output",
    help="write configuration to named file instead of stdout; '%%' can be "
         "used to substitue in the name of the device into the filename")

parser.add_argument(
    "-d", "--define",
    action="append",
    nargs=2,
    default=[],
    help="define variable for use in the template",
    metavar=("VAR", "VALUE"))

parser.add_argument(
    "-q", "--quiet",
    action="store_true",
    help="when generating configuration for multiple devices, don't print the "
         "name of each device, as it's generated")

parser.add_argument(
    "-D", "--debug",
    action="store_true",
    help="enable debug mode")

parser.add_argument(
    "devicename",
    nargs="*",
    help="name(s) of the device(s) to generate the configuration for")

parser.add_argument(
    "--version",
    action="version",
    version=("%(prog)s " + net_genconfig.__version__))


# parse the supplied command line against these options, storing the results

args = parser.parse_args()

roles_dirname = args.roles
include_dirname = args.include
inventory_dirname = args.inventory
output_filename = args.output
quiet = args.quiet
devicenames = args.devicename
debug = args.debug

vars = {}
for var, value in args.define:
    vars[var] = value



# check a couple of nonsensical configurations aren't being use related to
# multiple devices

if len(devicenames) > 1:
    if not output_filename:
        print("error: multiple device names specified but outputting to "
                  "standard output - all configurations would be concatenated",
              file=sys.stderr)

        exit(1)


    elif output_filename.find("%") == -1:
        print("error: multiple device names specified but output filename "
                  "does not contain a '%' to substitute the device name - "
                  "output file would be overwritten",

              file=sys.stderr)

        exit(1)



# --- inventory ---



if debug:
    print("debug: starting to read inventory", file=sys.stderr)



# trawl the inventory directory tree, read and merge all the YAML files into
# one big dictionary

inventory = dict()

item_filepaths = dict()

try:
    # walk the directory tree, raising an exception if there are any
    # problems (oddly, os.walk() doesn't do this by default and skips
    # over any errors)

    for dirpath, dirnames, filenames in \
        os.walk(inventory_dirname, onerror=raise_exception):

        # remove any directories whose name begins with a dot (to skip over
        # things like '.git'; '.' and '..' are already removed) so they're not
        # traversed into on subsequent iterations

        for dirname in dirnames:
            if dirname.startswith("."):
                dirnames.remove(dirname)


        # work through all the files in this directory, in sorted order, and
        # process them

        for filename in sorted(filenames):
            # skip files beginning with a dot (assumed to be temporary,
            # control, or other unwanted files)

            if filename.startswith("."):
                continue


            # read this file as YAML and add it to the inventory

            filepath = os.path.join(dirpath, filename)

            if debug:
                print("debug: reading inventory file '%s'" % filepath,
                      file=sys.stderr)

            try:
                inventory_file = yaml.safe_load(open(filepath))

            except ValueError as exception:
                print("error: failed parsing inventory file: '%s': %s" %
                          (filepath, exception),
                      file=sys.stderr)

                exit(1)


            for area in inventory_file:
                # create this part of the inventory, if it doesn't exist

                if area not in inventory:
                    inventory[area] = dict()
                    item_filepaths[area] = dict()


                else:
                    # if it did exist, raise an error if we already have a
                    # sub-item with the same name in that part

                    for item in inventory_file[area]:
                        if item in inventory[area]:
                            print("error: duplicate entry in inventory "
                                  "files: %s.%s in '%s' and '%s'" %
                                      (area, item, filepath,
                                       item_filepaths[area][item]),
                                  file=sys.stderr)

                            exit(1)


                # add the items to the (possibly empty) part of the inventory

                inventory[area].update(inventory_file[area])


                # record where we found those items

                for item in inventory_file[area]:
                    item_filepaths[area][item] = filepath


                if debug:
                    print("debug: read %d %s" % (len(inventory_file), area),
                          file=sys.stderr)


except OSError as e:
    # this exception catches subclasses of OSError, including things
    # like 'file not found' or 'permission denied'

    print("error: problem reading inventory:", e, file=sys.stderr)

    exit(1)


if debug:
    print("debug: finished reading inventory", file=sys.stderr)



if "devices" not in inventory:
    print("error: no devices found in inventory", file=sys.stderr)
    exit(1)



# build the Jinja2 environment

env = jinja2.Environment(
    loader=jinja2.FileSystemLoader([roles_dirname, include_dirname]),
    extensions=[
        "jinja2.ext.do", "jinja2.ext.loopcontrols", "jinja2.ext.with_"],
    trim_blocks=True)


# add in the special warn(), raise() and assert() functions, as well as
# some other functions we need, into the Jinja2 environment

env.globals["warn"] = warn_helper
env.globals["raise"] = raise_helper
env.globals["assert"] = assert_helper
env.globals["re_match"] = re_match_helper
env.globals["re_match_groups"] = re_match_groups_helper

env.globals["deepcopy"] = deepcopy

env.globals["deepmerge"] = deepmerge
env.globals["deepremoveitems"] = deepremoveitems


# add in the netaddr library functions as additional filters

for filter_name, filter_func in (
    netaddr_filter.FilterModule().filters().items()):

    env.filters[filter_name] = filter_func



def genconfig(devicename):
    """Generate the configuration for the specified device and write it
    to either standard output or a file, depending on the command line
    options specified.
    """

    # this function makes use of global variables defined outside it so
    # must appear here in the code


    # get the definition dictionary for this device from the inventory; because
    # we're not going to modify it, we don't need to copy it
    #
    # we use this variable for some checks here, and to pass it to the starting
    # role template, so it avoids repeatedly fetching it
    #
    # if we're using a device profile, we will overwrite this after merging the
    # profiles in

    if devicename not in inventory["devices"]:
        print("error: device not found in inventory: ", devicename,
              file=sys.stderr)

        exit(1)

    device = inventory["devices"][devicename]

    if device is None:
        print("error: definition for device '%s' is empty" % devicename,
              file=sys.stderr)

        exit(1)


    # if we have profiles for this device, we need to use those as the base for
    # the device definition, so we need to merge them all together and into the
    # explicit device definition itself

    if "profiles" in device:
        if "device-profiles" not in inventory:
            print("error: profile '%s' used for device '%s' but no device "
                  "profiles in inventory" % (device["profile"], devicename),

                  file=sys.stderr)

            exit(1)


        # this dictionary will be used to assemble and merge the list of
        # profiles referenced that we can merge the device configuration into

        profiles_merged = {}


        # go through the imported device profiles in order

        for profile in device["profiles"]:
            # check this particular profile is defined

            if profile not in inventory["device-profiles"]:
                print("error: profile '%s' not found for device '%s'"
                          % (profile, devicename),

                      file=sys.stderr)

                exit(1)


            # it exists - merge a deep copy of the profile into the merged
            # profile
            #
            # we need to deep copy the profiles as we may remove things from
            # them due to the 'profiles-exclude' option

            deepmerge(
                profiles_merged,
                deepcopy(inventory["device-profiles"][profile]))


        # if we're excluding anything from the imported profiles, we now remove
        # these from the merged profile we just assembled

        if "profiles-exclude" in inventory["devices"][devicename]:
            deepremoveitems(profiles_merged, device["profiles-exclude"])


        # finally, we merge the device definition dictionary over the top which
        # will, by default, replace any clashing items, favouring the ones in
        # the local device definition
        #
        # we then replace the device definition with the merged one

        deepmerge(profiles_merged, deepcopy(device))

        device = profiles_merged


    if "role" not in device:
        print("error: missing role for device '%s'" % devicename,
              file=sys.stderr)

        exit(1)


    if "platform" not in device:
        print("error: missing platform for device '%s'" % devicename,
              file=sys.stderr)

        exit(1)


    role = device["role"]
    platform = device["platform"]



    # --- generate configuration ---



    if debug:
        print("debug: generating configuration for '%s' (role '%s', platform "
              "'%s')" % (devicename, role, platform), file=sys.stderr)


    if not os.path.isdir(roles_dirname):
        print("error: role directory does not exist: '%s'" % roles_dirname,
              file=sys.stderr)

        exit(1)

    if not os.path.isdir(include_dirname):
        print("error: include directory does not exist: '%s'"
                  % include_dirname,
              file=sys.stderr)

        exit(1)


    if not os.path.isdir("%s/%s" % (roles_dirname, platform)):
        print("error: platform not found: '%s'" % platform, file=sys.stderr)
        exit(1)


    # read the template file

    role_filename = "%s/%s.j2" % (platform, role)

    if debug:
        print("debug: using role file '%s'" % role_filename, file=sys.stderr)

    try:
        template = env.get_template(role_filename)

    except jinja2.exceptions.TemplateNotFound:
        print("error: role not found: '%s' for platform '%s'"
                  % (role, platform),
              file=sys.stderr)

        exit(1)


    # render the template

    config = template.render(devicename=devicename, device=device,
                             inventory=inventory, **vars)


    # write output to either standard output or a file, depending on the
    # options specified

    if output_filename:
        output_filename_expanded = output_filename.replace("%", devicename)

        if debug:
            print("debug: writing to output file '%s'"
                      % output_filename_expanded, file=sys.stderr)

        with open(output_filename_expanded, "w") as output_file:
            print(config, file=output_file)

    else:
        if debug:
            print("debug: writing to standard output", file=sys.stderr)

        print(config)


# go through all the devices specified, generate and write out their
# configurations

if not devicenames:
    print("warning: no device names specified", file=sys.stderr)

for devicename in devicenames:
    if (not quiet) and (len(devicenames) > 1):
        print(devicename)

    genconfig(devicename)
