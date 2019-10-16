from distutils.core import setup

setup(name='partialCopy',
      version='0.1',
      description='A tool to copy big data to multiple smaller disks ',
      author='Mohamed El-Kalioby',
      author_email='mkalioby@mkalioby.com',
      url='https://github.com/mkalioby/partialCopy',
      packages=['partialCopy'],
      keywords = ['admin','utils', 'notification'],
      data_files=[('/etc/',['partialCopy/pcp.cfg']),('/usr/local/bin/',['pcp'])]
     )
