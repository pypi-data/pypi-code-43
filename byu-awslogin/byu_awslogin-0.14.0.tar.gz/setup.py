# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['byu_awslogin', 'byu_awslogin.auth', 'byu_awslogin.util']

package_data = \
{'': ['*']}

install_requires = \
['beautifulsoup4>=4.7,<5.0',
 'boto3>=1.9,<2.0',
 'click>=7.0,<8.0',
 'configparser>=3.7,<5.0',
 'future>=0.17.1,<0.19.0',
 'lxml>=4.3,<5.0',
 'prompt-toolkit>=2.0,<3.0',
 'requests>=2.21,<3.0']

entry_points = \
{'console_scripts': ['awslogin = byu_awslogin.index:cli']}

setup_kwargs = {
    'name': 'byu-awslogin',
    'version': '0.14.0',
    'description': "An aws-adfs spinoff that fits BYU's needs",
    'long_description': "# AWSLOGIN\nPython script for CLI and SDK access to AWS via ADFS while requiring MFA\naccess using <https://duo.com/>\n\n# History and Purpose\n\nBYU used to use the great [aws-adfs](https://github.com/venth/aws-adfs)\nCLI tool to login to our AWS accounts. It worked great, especially the\nDUO 2FA support. Eventually, we decided to write our own similar tool\nbut make it BYU-specific so that we could tailor it to our needs (which\nbasically means hard-code certain BYU-specific things) and remove some\nof the required parameters. Since this tool will be used by BYU\nemployees only we had that option. We then morphed it a little more for\nour use cases. This isn't something that you could use outside of BYU,\nsorry.\n\n# Installation\n\n  - Python > 3.6 is recommended but it should work with Python 2.7. See\n    the [installation\n    options](https://github.com/byu-oit/awslogin/blob/master/INSTALLATION_OPTIONS.md) For additional options\n    page for step by step instructions for installing in various\n    environments.\n  - See <https://www.python.org/downloads/> for a windows installation\n    method.\n  - In linux you may be able to use apt, rpm or\n    <https://www.python.org/downloads/>.\n  - In Mac you can use homebrew, macports or\n    <https://www.python.org/downloads/>.\n  - Run `pip3 install byu_awslogin` or `pip install byu_awslogin` as\n    appropriate for your python installation\n\n# Upgrading\n\nIf you already have byu\\_awslogin install and are looking to upgrade\nsimply run\n\n`pip3 install --upgrade byu_awslogin` or `pip install --upgrade\nbyu_awslogin` as appropriate for your python installation\n\n# Usage\n\nawslogin defaults to the default profile in your \\~/.aws/config and\n\\~/.aws/credentials files. **\\*If you already have a default profile you\nwant to save in your \\~/.aws files make sure to do that before running\nawslogin.**\\*\n\nOnce you're logged in, you can execute commands using the AWS CLI or AWS\nSDK. Try running `aws s3 ls`.\n\nCurrently, AWS temporary credentials are only valid for 1 hour. We cache\nyour ADFS session, however, so you can just re-run `awslogin` again to\nget a new set of AWS credentials without logging in again to ADFS. Your\nADFS login session is valid for 8 hours, after which time you'll be\nrequired to login to ADFS again to obtain a new session.\n\nTo switch accounts after you've already authenticated to an account,\njust run awslogin again and select a new account/role combination.\n\nTo use it:\n\n  - Run `awslogin` and it will prompt you for the AWS account and role\n    to use.\n  - Run `awslogin --account <account name> --role <role name>` to skip\n    the prompting for account and name. You could specify just one of\n    the arguments as well.\n  - Run `awslogin --profile <profile name>` to specifiy an alternative\n    profile\n  - Run `awslogin --region <region name>` to specify a different region.\n    The default region is *us-west-2*.\n  - Run `awslogin --status` for the current status of the default\n    profile\n  - Run `awslogin --status --profile dev` for the current status of the\n    dev profile\n  - Run `awslogin --status --profile all` for the current status of the\n    all profiles\n  - Run `awslogin --logout` to logout of a cached ADFS session\n  - Run `awslogin --version` to display the running version of awslogin\n  - Run `awslogin --help` for full help message\n\n# Reporting bugs or requesting features\n\n  - Enter an issue on the github repo.\n  - Or, even better if you can, fix the issue and make a pull request.\n\n# Deploying changes\n\n  - Update the version.\n  - Commit the change and push. Handel-codepipeline will run the\n    automated tests and if they pass it will build and upload a new\n    version to pypi.\n\n# TODO\n\n  -   - Write tests\n        \n          - Write more tests to increase overall coverage\n",
    'author': 'BYU OIT Application Development',
    'author_email': 'it@byu.edu',
    'url': 'https://github.com/byu-oit/awslogin',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*',
}


setup(**setup_kwargs)
