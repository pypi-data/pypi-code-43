import os
import sys
import subprocess
import glob

import distutils.command.build as distutils_build
from distutils import log as dist_log
from setuptools import setup, find_packages, Command

basepath = os.path.dirname(__file__)


class NoOptsCmd(Command):
    def initialize_options(self):
        pass

    def finalize_options(self):
        pass


class BuildManpages(NoOptsCmd):
    """Builds manpages in docs/build/man"""
    user_options = []

    def run(self):
        try:
            subprocess.check_call(['make', '-C', 'docs', 'man'])
        except Exception:
            print("Failed to build manpages; they won't be available",
                  file=sys.stderr)

            # Create a dummy manual for the needs of data_files
            manpage = os.path.join('docs', 'build', 'man', 'man1',
                                   'twc.1')
            if not os.path.exists(os.path.dirname(manpage)):
                os.makedirs(os.path.dirname(manpage))
            if not os.path.exists(manpage):
                with open(manpage, 'w') as f_:
                    f_.write('Manpage for TWC wasn\'t generated\n')


class BuildTWC(distutils_build.build):
    """Overrides a default install_data"""
    user_options = []

    def run(self):
        self.run_command('build_man')
        super().run()
        self.clean()

    def clean(self):
        dist_log.info('running build cleanup')
        # establish a path to build/lib, where build artifacts (before creating
        # wheels or bdist) are copied. We'll use distutils_build.build.build_lib
        # property for that.
        build_dir = os.path.join(basepath, self.build_lib)

        # file names relative to build/lib/twc directory
        to_clean = []

        for expr in to_clean:
            for file_ in glob.glob(os.path.join(build_dir, expr)):
                dist_log.info('removing %s' % file_)
                os.unlink(file_)


with open('README.rst', encoding='utf-8') as f_:
    long_description = f_.read()


def main():
    setup(name='twc',
          description="TaskWarrior's interactive terminal frontend",
          long_description=long_description,
          use_scm_version={'write_to': 'src/twc/_version.py'},
          license='GPLv3+',
          author='Michał Góral',
          author_email='dev@mgoral.org',
          url='https://gitlab.com/mgoral/twc',
          platforms=['linux'],
          python_requires='>=3.5,<3.8',
          setup_requires=['setuptools_scm'],
          install_requires=['prompt_toolkit==2.0.9',
                            'tasklib==1.1.0',
                            'attrs==19.1.0',
                            'mgcomm>=0.2.0'],

          # https://pypi.python.org/pypi?%3Aaction=list_classifiers
          classifiers=['Development Status :: 4 - Beta',
                       'Environment :: Console',
                       'Intended Audience :: End Users/Desktop',
                       'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
                       'Natural Language :: English',
                       'Operating System :: POSIX',
                       'Programming Language :: Python :: 3 :: Only',
                       'Programming Language :: Python :: 3.5',
                       'Programming Language :: Python :: 3.6',
                       'Programming Language :: Python :: 3.7',
                       'Topic :: Utilities',
                       ],

          packages=find_packages('src'),
          package_dir={'': 'src'},

          data_files=[
              ('share/man/man1', ['docs/build/man/man1/twc.1'])
          ],

          entry_points={
              'console_scripts': ['twc=twc.app:main'],
          },

          cmdclass={
              'build': BuildTWC,
              'build_man': BuildManpages,
          })


if __name__ == '__main__':
    main()
