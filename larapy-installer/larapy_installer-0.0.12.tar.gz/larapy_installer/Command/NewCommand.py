from cleo import Command
import requests
import zipfile
import shutil


class NewCommand(Command):

    """
    Craft a new Larapy Application

    new
        {name : Name of your Larapy application ?}
    """

    url = "https://github.com/LaravelPython/larapy/archive/master.zip"

    def handle(self):
        name = self.argument('name')
        self.line('<info>Crafting your larapy application...</info>')
        r = requests.get(NewCommand.url, allow_redirects=True)
        open('master.zip', 'wb').write(r.content)
        with zipfile.ZipFile("master.zip", 'r') as zip_ref:
            zip_ref.extractall("working")
        shutil.rmtree('master.zip')
        shutil.move("working/larapy-master", name)
        shutil.rmtree('working')
