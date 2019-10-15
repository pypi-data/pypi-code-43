from setuptools import setup

# read the contents of your README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'pubgReports/README.md'), encoding='utf-8') as f:
    long_description = f.read()
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(name='pubg-reports',
      version='0.0.0.1.4.1',
      description='A discord bot that reports PUBG match stats to a discord server',
      url='https://github.com/SulimanCS/pubg-discord-stats-integration-bot',
      entry_points = {
          'console_scripts': ['bot-run=pubgReports.bot:main', 'bot-config-all=pubgReports.config:configAll', 'bot-config-tokens=pubgReports.config:configTokens', 'bot-config-channels=pubgReports.config:configChannels'],
      },
      classifiers=[
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
      ],
      author='Suliman Alsarraf',
      author_email='sulimanAlsarraf@gmail.com',
      license='MIT',
      packages=['pubgReports'],
      install_requires=requirements,
      include_package_data=True,
      data_files=[('', ['pubgReports/PLAYERS.csv', 'pubgReports/TOKENS.csv', 'pubgReports/DISCORDCONFIG.csv',])],
      long_description=long_description,
      long_description_content_type='text/markdown',
      zip_safe=False)
