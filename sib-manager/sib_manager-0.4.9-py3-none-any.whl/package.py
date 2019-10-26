from os import mkdir
from pkg_resources import resource_filename

class Package(object):

    def __init__(self, name, folder):

        self.package_name = name
        self.package_folder = folder

    def get_template(self):
        return resource_filename(__name__, 'templates/package')

    def create(self):

        # create package folder
        mkdir(self.package_folder)

        try:
            from django.core import management
            from django.template.exceptions import TemplateSyntaxError

            # init django app
            management.call_command(
                'startapp',
                self.package_name,
                self.package_folder,
                template=self.get_template(),
                name=['README.md', 'setup.cfg']
            )

        except ModuleNotFoundError as e:
            print('[ERROR] Django not imported: {}'.format(e))
            return False

        except TemplateSyntaxError as e:
            print('[ERROR] Package template is wrong: {}'.format(e))
            return False

        return True
