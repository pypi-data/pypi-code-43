import os

import click

from knowledge_search_engine.image_namer import raw_screenshots_namer
from knowledge_search_engine.images_to_text import image_to_text_files

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

MY_ALIASES = {
    "screens_dir_path": "/Users/maistrovas/Documents/My Life/Education/My_Knowledge_Screen_Library",
    "unnamed_screens_path": "/Users/maistrovas/Desktop/Pictures",
    "unnamed_screens_path_test": "/Users/maistrovas/Documents/My Life/Education/test_videos_dir/test_screens",
}


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(version='0.0.1')
def image_processors():
    pass


@image_processors.command()
@click.argument('path', default=MY_ALIASES["unnamed_screens_path_test"])
@click.option('--ignore_named', is_flag=True,
              help='Screens with only default names would be processed. '
                   'Eg: contains "cнимок экрана" or "screen shot" in name ')
def name_screenshots(**kwargs):
    if os.path.isfile(kwargs["path"]):
        print("Please use name_screenshot command for single file")
        return
    raw_screenshots_namer(**kwargs)


@image_processors.command()
@click.argument('path', default=MY_ALIASES["unnamed_screens_path_test"])
@click.option(help="Name single image file")
def name_screenshot(**kwargs):
    if os.path.isdir(kwargs["path"]):
        print("Please use name_screenshots command for directories")
        return
    raw_screenshots_namer(**kwargs)


@image_processors.command()
@click.argument('path', default=MY_ALIASES["screens_dir_path"])
@click.option('--recursive', is_flag=True, help='Process images in all directories that inside specified path.')
def create_text_siblings(**kwargs):
    image_to_text_files(**kwargs)


if __name__ == '__main__':
    image_processors()
