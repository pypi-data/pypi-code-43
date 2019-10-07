from setuptools import setup
from new_version import get_current_version

required = [
    'requests>=2,<3',
    'requests-cache>=0.4,<1',
    'requests-jwt>=0.4,<1',
]

# Get current version
current_version = get_current_version()

setup(name='nw_connections',
      version=current_version,
      description='Shared Marple python modules',
      url='http://github.com/marple-newsrobot/newsworthy-py-connections',
      author='Journalism Robotics Stockholm',
      author_email='contact@newsworthy.se',
      license='MIT',
      packages=['nw_connections'],
      include_package_data=True,
      install_requires=required,
      zip_safe=False)
