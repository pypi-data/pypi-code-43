'''
A command line utility that streamlines the process of creating documentation and text-based programming tutorials in Markdown.
Use snyp to append nicely formatted code snippets from source files into your destination Markdown file.
'''

import configparser
import click
import os 

CONFIG_FNAME = 'snyp.ini'

LINES_MSG = '''
Too many arguments: Use 0, 1 or 2 arguments.
For more details, refer to:
snyp --help
'''

dir_path = os.path.dirname(os.path.realpath(__file__))
configFile = os.path.join(dir_path, CONFIG_FNAME)
if not os.path.exists(configFile):
    raise FileNotFoundError('Could not find snyp.ini')

configuration = configparser.ConfigParser()
configuration.read(configFile)

@click.command()
@click.argument('lines', nargs=-1)
@click.option('-s', '--src', default=configuration['default']['src'], help='The source file from which to extract the code snippet')
@click.option('-d', '--dest', default=configuration['default']['dest'], help='The destination file to which to append the formatted snippet. "-" for stdout')
@click.option('-l', '--lang', default=configuration['default']['default'], help='The language specific formatting to be applied to the code snippet')
@click.option('-c', '--config', is_flag=True, help='Edit the configuration, i.e. to change defaults, add languages, etc.')
def snyp(lines, src, dest, lang, config):
    '''
    Use this tool to extract code snippets from a source file (src) and append them to a markdown file (dest) 
    with proper Github Flavored Markdown formatting. \n 

    You can use 0, 1 or 2 'lines' arguments: \n
    With 0 arguments, the entire source file will be extracted \n
    With 1 argument, the entire source file starting at lines[0] will be extracted \n
    With 2 arguments, lines lines[0] to lines[1] (inclusively) will be extracted from the source file

    Use snip --config to view and update the configuration
    '''
    if config:
        configure()
        return
        

    snippet = ''
    with open(src, 'r') as srcFile:
        for idx, line in enumerate(srcFile):
            if inBounds(lines, idx):
                snippet += line
    prefix = '\n```{}\n'.format(configuration[lang]['lang'])
    prefix += '{} snippet from {} {} {}\n'.format(
        configuration[lang]['commentstart'],
        src,
        getLinesText(lines),
        configuration[lang]['commentend'],
    )
    snippet = prefix + snippet + '\n```\n'
    if dest == '-':
        click.echo(snippet)
    else:
        with open(dest, 'a') as destFile:
            destFile.write(snippet)
    click.echo('Snippet extracted!')

def configure():        
    click.edit(filename=configFile)
    click.echo('Configuration updated!')

#helpers
def inBounds(lines, idx):
    idx += 1 #user enters lines starting at 1, but index starts at 0
    if len(lines) == 0:
        return True
    elif len(lines) == 1:
        return idx >= int(lines[0])
    elif len(lines)==2:
        if int(lines[0])>int(lines[1]):
            raise click.BadArgumentUsage(f'End line ({lines[1]}) should be greater than or equal tostart line ({lines[0]})!')
        return idx >= int(lines[0]) and idx <= int(lines[1])
    else:
        raise click.BadArgumentUsage(LINES_MSG)

def getLinesText(l):
    if not l:
        return ''
    elif len(l) == 1:
        return 'lines {}+'.format(l[0])
    elif len(l) == 2:
        return 'lines {}-{}'.format(l[0], l[1])