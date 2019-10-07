from .containator import Containator
from .defs import __version__, app_name, app_description, app_name_desc

def main():
    Containator().run_cli()
