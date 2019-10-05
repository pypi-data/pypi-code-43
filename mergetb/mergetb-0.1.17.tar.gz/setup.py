from setuptools import setup

setup(name='mergetb',
      version='0.1.17',
      description='The Merge testbed Python client library and CLI',
      long_description="""The Merge testbed Python client library and CLI

      usage:

        mergetb <verb> <object>

      To install bash-completion:

        complete_merge_bash | sudo tee /etc/bash_completion.d/mergetb
      """,
      url='https://gitlab.com/mergetb/python-client',
      author='Ryan Goodfellow',
      author_email='rgoodfel@isi.edu',
      license='Apache2.0',
      packages=['mergetb'],
      install_requires=[
          'pygments>=2.3.1',
          'requests>=2.20.0',
          'PyYAML>=3.13',
          'ipython>=7.1.1'
      ],
      scripts=['bin/complete_merge_bash'],
      entry_points={
          'console_scripts': [
              'mergetb_py = mergetb.mergetb_cli:main'
          ]
      },
      setup_requires=['pytest-runner'],
      tests_require=['pytest'],
      zip_safe=False)
