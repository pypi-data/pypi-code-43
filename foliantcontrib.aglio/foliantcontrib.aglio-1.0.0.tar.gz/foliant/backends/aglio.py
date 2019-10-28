import os
import re
import shutil
import traceback

from subprocess import run, PIPE, STDOUT, CalledProcessError

from foliant.utils import spinner, output
from foliant.backends.base import BaseBackend
from pathlib import Path, PosixPath


def unique_name(dest_dir: str or PosixPath, old_name: str) -> str:
    """
    Check if file with old_name exists in dest_dir. If it does —
    add incremental numbers until it doesn't.
    """
    counter = 1
    dest_path = Path(dest_dir)
    name = old_name
    while (dest_path / name).exists():
        counter += 1
        name = f'_{counter}'.join(os.path.splitext(old_name))
    return name


class Backend(BaseBackend):

    _flat_src_file_name = '__all__.md'

    targets = ('site')

    defaults = {
        'aglio_path': 'aglio',
        'params': {}
    }

    required_preprocessors_after = {
        'flatten': {
            'flat_src_file_name': _flat_src_file_name
        }
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._aglio_config = {**self.defaults,
                              **self.config.get('backend_config',
                                                {}).get('aglio', {})}

        self._site_dir = Path(f'{self._aglio_config.get("slug", self.get_slug())}.aglio')

        self.logger = self.logger.getChild('aglio')

        self.logger.debug(f'Backend inited: {self.__dict__}')

    def _process_images(self, source: str, target_dir: str or PosixPath) -> str:
        """
        Cleanup target_dir. Copy local images to `target_dir` with unique names, replace their HTML
        definitions in `source` with confluence definitions.

        `source` — string with HTML source code to search images in;
        `rel_dir` — path relative to which image paths are determined.

        Returns a tuple: (new_source, attachments)

        new_source — a modified source with correct image paths
        """

        def _sub(image):
            image_caption = image.group('caption')
            image_path = image.group('path')

            # leave external images as is
            if image_path.startswith('http'):
                return image.group(0)

            image_path = Path(image_path)

            self.logger.debug(f'Found image: {image.group(0)}')

            new_name = unique_name(target_dir, image_path.name)
            new_path = Path(target_dir) / new_name

            self.logger.debug(f'Copying image into: {new_path}')
            shutil.copy(image_path, new_path)

            img_ref = f'![{image_caption}](img/{new_name})'

            self.logger.debug(f'Converted image ref: {img_ref}')
            return img_ref

        image_pattern = re.compile(r'!\[(?P<caption>.*?)\]\((?P<path>.+?)\)')
        self.logger.debug('Processing images')

        return image_pattern.sub(_sub, source)

    def _get_command(
            self,
            options: dict,
            input_file_path: PosixPath,
            output_file_path: PosixPath) -> str:
        '''Generate the site generation command.

        :param options: Options extracted from the diagram definition
        :param input_file_path: Path to the source file
        :param input_file_path: Path to the output html-file

        :returns: Complete site generation command
        '''

        components = [options['aglio_path']]

        params = options.get('params', {})

        for option_name, option_value in params.items():
            if option_value is True:
                components.append(f'--{option_name}')

            else:
                components.append(f'--{option_name} {option_value}')

        components.append(f'-i {input_file_path}')
        components.append(f'-o {output_file_path}')

        return ' '.join(components)

    def make(self, target: str) -> str:
        with spinner(f'Making {target}', self.logger, self.quiet, self.debug):
            try:
                img_dir = self._site_dir / 'img'
                shutil.rmtree(self._site_dir, ignore_errors=True)
                img_dir.mkdir(parents=True)
                source_path = self.working_dir / self._flat_src_file_name
                with open(source_path) as f:
                    source = f.read()

                processed_source = self._process_images(source, img_dir)
                with open(source_path, 'w') as f:
                    f.write(processed_source)

                try:
                    command = self._get_command(self._aglio_config,
                                                source_path,
                                                self._site_dir / "index.html")
                    self.logger.debug(f'Constructed command: {command}')

                    r = run(
                        command,
                        shell=True,
                        check=True,
                        stdout=PIPE,
                        stderr=STDOUT
                    )
                except CalledProcessError as e:
                    raise RuntimeError(e.output.decode('utf8', errors='ignore'))
                command_output_decoded = r.stdout.decode('utf8', errors='ignore')
                output(command_output_decoded, self.quiet)
                return self._site_dir

            except Exception as exception:
                err = traceback.format_exc()
                self.logger.debug(err)
                raise type(exception)(f'Build failed: {err}')
