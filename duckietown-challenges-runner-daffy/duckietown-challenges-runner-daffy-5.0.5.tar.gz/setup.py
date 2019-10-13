from setuptools import find_packages, setup


def get_version(filename):
    import ast
    version = None
    with open(filename) as f:
        for line in f:
            if line.startswith('__version__'):
                version = ast.parse(line).body[0].value.s
                break
        else:
            raise ValueError('No version found in %r.' % filename)
    if version is None:
        raise ValueError(filename)
    return version


version = get_version(filename='src/duckietown_challenges_runner/__init__.py')
line = 'daffy'
setup(name=f'duckietown-challenges-runner-{line}',
      version=version,
      download_url='http://github.com/duckietown/duckietown-challenges-runner/tarball/%s' % version,
      package_dir={'': 'src'},
      packages=find_packages('src'),
      install_requires=[
          'duckietown-challenges-daffy',
          'duckietown-shell>=5,<6',
          'decorator',

          'PyYAML',
          'docker',
          'six',
          'psutil',
          'boto3',
          'ansi2html',
          'termcolor',
          'ipfsapi',
          'timeout-decorator',
      ],

      tests_require=[
      ],

      # This avoids creating the egg file, which is a zip file, which makes our data
      # inaccessible by dir_from_package_name()
      zip_safe=False,

      # without this, the stuff is included but not installed
      include_package_data=True,

      entry_points={
          'console_scripts': [
              'dt-challenges-evaluator = duckietown_challenges_runner:dt_challenges_evaluator',
              'dt-challenges-evaluate-local = duckietown_challenges_runner:runner_local_main',
          ]
      }
      )
