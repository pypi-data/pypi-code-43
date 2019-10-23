import argparse
import jinja2
import json
import os.path
import shutil
import subprocess
import sys
import tempfile
import yaml

TPLATE_SUFFIX = '.j2'

# files in this list are allowed in the output directory.
ALLOW_IN_OUTDIR_LIST = ['.DS_Store']
NOCOPY_LIST = ['tplate.yaml', 'tplate.json', '.git', '.DS_Store']


def loadfile(filename):
    result = None
    with open(filename, 'r') as f:
        if filename.endswith('.json'):
            result = json.load(f)
        elif filename.endswith('.yaml') or filename.endswith('.yml'):
            result = yaml.safe_load(f)

    return result


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('template_dir')
    parser.add_argument('output_dir')
    parser.add_argument('--context', )
    parser.add_argument('--update', action='store_true')

    args = parser.parse_args(sys.argv[1:])

    tempdir = None  # this will be set to a TemporaryDirectory object if the template_dir is actually a URL
    template_dir = args.template_dir
    if template_dir.startswith('http:') or template_dir.startswith('https:') or template_dir.startswith('git@'):
        tempdir = tempfile.TemporaryDirectory()
        subprocess.run(['git', 'clone', template_dir, tempdir.name], check=True)
        template_dir = tempdir.name

    try:
        if not os.path.isdir(template_dir):
            sys.exit('The program has exited because the provided template directory ({0}) does not exist.'
                     .format(template_dir))

        if os.path.isfile(args.output_dir):
            sys.exit('The program has exited because the specified output directory is a file.')

        if os.path.isdir(args.output_dir):
            files = os.listdir(args.output_dir)
            files = [f for f in files if f not in ALLOW_IN_OUTDIR_LIST]
            if (not args.update) and (len(files) > 0):
                sys.exit(
                    'The program is exiting because the output directory ({0}) is not empty.'.format(args.output_dir))

        else:
            os.makedirs(args.output_dir)

        context_file = os.path.join(template_dir, 'tplate.json')
        if os.path.exists(context_file):
            environment = loadfile(context_file)

        else:
            context_file = os.path.join(template_dir, 'tplate.yaml')
            if os.path.exists(context_file):
                environment = loadfile(context_file)

            else:
                sys.exit('The program is exiting because a required file (tplate.json or tplate.yaml) was not found in '
                         'the output directory ({0}).'.format(args.output_dir))

        # if a context file was provided, load it on top of the defaults
        if args.context is not None:
            if not os.path.isfile(args.context):
                sys.exit('The program is exiting because the specified context file ({0}) does not exist.'
                         .format(args.context))

            if (not args.context.endswith('.json')) \
                    and (not args.context.endswith('.yaml')) \
                    and (not args.context.endswith('.yml')):
                sys.exit(
                    'The program is exiting because the context argument ({0}) has an unsupported extension. Context '
                    'files must end with ".json" or ".yaml" or "yml.'.format(args.context))

            uservals = loadfile(args.context)

        # otherwise prompt for input
        else:
            uservals = promptforinput(environment)

        environment.update(uservals)

        # add the name of the output directory to the environment so it can be used in a template
        if args.output_dir.endswith('/'):
            environment['output_dir'] = os.path.basename(args.output_dir[0:-1])
        else:
            environment['output_dir'] = os.path.basename(args.output_dir)

        copydir(template_dir, args.output_dir, environment)

        directives = None
        path = os.path.join(args.output_dir, 'tplate_directives.json')
        if os.path.exists(path):
            directives = loadfile(path)
        else:
            path = os.path.join(args.output_dir, 'tplate_directives.yaml')
            if os.path.exists(path):
                directives = loadfile(path)

        if directives is not None:
            do_directives(args, directives)
            os.remove(path)

    finally:
        if tempdir is not None:
            tempdir.cleanup()


def do_directives(args, directives):
    for directive in directives:
        if directive[0] == 'java_package_rename':
            java_package_rename(args.output_dir, directive[1], directive[2])
        else:
            # just ignore unknown directives
            pass


def java_package_rename(basedir, frompackage, topackage):
    frompath = os.path.join(basedir, 'java', *(frompackage.split('.')))
    topath = os.path.join(basedir, 'java', *(topackage.split('.')))
    if os.path.isdir(frompath):
        shutil.rmtree(topath, ignore_errors=True)
        os.renames(frompath, topath)
        # print('renamed {0} to {1}'.format(frompath,topath))
    else:
        for f in os.listdir(basedir):
            path = os.path.join(basedir, f)
            if os.path.isdir(path):
                java_package_rename(path, frompackage, topackage)


def promptforinput(userenv):
    done = False
    userinput = dict()
    while not done:
        print('Please provide values for the following template variables:')
        for key in userenv:
            userinput[key] = input('{0} ({1}): '.format(key, userenv[key]))

        print('You have provided the following values:')
        for key, val in userinput.items():
            print('\t{0}={1}'.format(key, val))
        yn = input('Enter y to proceed or n to re-enter values: ')
        if yn.lower() == 'y':
            done = True
        else:
            done = False

    return userinput


# copy with templating
def copydir(fromdir, todir, environment):
    template_env = jinja2.Environment(loader=jinja2.FileSystemLoader(fromdir), trim_blocks=True, lstrip_blocks=True)
    for f in os.listdir(fromdir):
        if f in NOCOPY_LIST:
            continue

        infile = os.path.join(fromdir, f)
        if os.path.isdir(infile):
            to = os.path.join(todir, f)
            os.makedirs(to, exist_ok=True)
            copydir(infile, to, environment)
        else:
            if f.endswith(TPLATE_SUFFIX):
                template = template_env.get_template(f)
                outfile = os.path.join(todir, f[0:-1 * len(TPLATE_SUFFIX)])
                with open(outfile, 'wt') as fp:
                    template.stream(environment).dump(fp)

            else:
                outfile = os.path.join(todir, f)
                shutil.copyfile(infile, outfile)
