from setuptools import setup, find_packages

# copied from https://github.com/awslabs/git-remote-codecommit/blob/master/setup.py
import os
def read(fname):
  return open(os.path.join(os.path.dirname(__file__), fname)).read()
  

from matomo_sdk_py import matomoSdkPy_version

# follow https://github.com/awslabs/git-remote-codecommit/blob/master/setup.py
# and https://packaging.python.org/tutorials/packaging-projects/
setup(
    name='matomo_sdk_py',
    version=matomoSdkPy_version,
    author="Shadi Akiki, AutofitCloud",
    author_email="shadi@autofitcloud.com",
    url='https://gitlab.com/autofitcloud/matomoSdkPy',
    description="Python SDK to send POST http requests to matomo",

    # 2019-09-10 not sure what in the README.md is yielding the twine error
    # The description failed to render in the default format of reStructuredText.
    # long_description = read('README.md'),
    long_description = 'Check repository link',
    long_description_content_type="text/markdown",
    
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'requests==2.22.0',
    ],
)
