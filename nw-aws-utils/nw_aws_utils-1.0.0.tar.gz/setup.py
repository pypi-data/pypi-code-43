from setuptools import setup

required = [
    'boto3>=1.9',
]

# Get current version
with open("CURRENT_VERSION.txt") as f:
    current_version = f.read().strip()

setup(name='nw_aws_utils',
      version=current_version,
      description='Reusable components for interacting with AWS services',
      url='http://github.com/marple-newsrobot/newsworthy-aws-utils',
      author='Journalism Robotics Stockholm',
      author_email='contact@newsworthy.se',
      license='MIT',
      packages=['aws_utils'],
      include_package_data=True,
      install_requires=required,
      zip_safe=False)
