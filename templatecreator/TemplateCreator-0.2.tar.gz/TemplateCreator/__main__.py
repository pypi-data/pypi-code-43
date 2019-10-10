import optparse
from template_creator import TemplatesCreator, TemplateOptions

parser = optparse.OptionParser()
parser.add_option('-t', '--template',
                  action="store", dest="template",
                  help=f'one of {TemplateOptions}')

parser.add_option('-n', '--folder-name',
                  action="store", dest="folder_name",
                  help='any string')

options, args = parser.parse_args()
Creator = TemplatesCreator(template_name=options.template, folder_name=options.folder_name)
Creator.create()
