# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['ssis_validator']

package_data = \
{'': ['*']}

install_requires = \
['colorama>=0.4.1,<0.5.0',
 'crayons>=0.2.0,<0.3.0',
 'gitpython>=3.0,<4.0',
 'lxml>=4.4,<5.0']

entry_points = \
{'console_scripts': ['ssis_validator = ssis_validator.__main__:main']}

setup_kwargs = {
    'name': 'ssis-validator',
    'version': '0.1.1',
    'description': 'A Python package for validating SQL Server Integration Services (SSIS) packages',
    'long_description': '# ssis_validator\n\nA Python package for validating SQL Server Integration Services (SSIS) projects. It can be used as a part of Continuous Integration pipeline.\n\nThis Python application is written for Python 3.7+.\n\n## Install\n\nThis package is available on [PyPi](https://pypi.org/project/ssis-validator/) package repository. You can install it like below:\n\n`pip install ssis_validator`\n\n## Usage\n\n### 1. Projects\n\nSpecify one or multiple `--project` arguments and provide the full path to the SSIS Projects that you want to validate.\n\n```bash\nssis_validator --project Project_1 --project Project_2\n```\n\n### 2. Repository Staging\n\nSpecify `--repository` optional argument along with one `--project` argument passing the Git repository hosting multiple SSIS Projects. The validator only checks SSIS projects that are staged.\n\n\n```bash\nssis_validator --project Project_1 --repository\n```\n\n## Validation Criteria\n\nThe following validation criteria are currently checked. The current version has the accepted specifications hard-coded. The next version will parameterize all of them in a configuration file.\n\n### Project\n\n1. Project Server Version: `SQLServer2014`, `SQLServer2016`\n2. Project Protection Level: `EncryptSensitiveWithPassword`\n3. Packages Presence in Project: `True`\n4. Linkage of Packages: `True`\n5. Project Deployment Model: `Project`\n\n### Package\n\n1. Package Last Modified Visual Studio Version: `SSIS_2016`\n2. Package Protection Level: `EncryptSensitiveWithPassword`\n3. (Optional) PragmaticWorks BIxPress Server Name: `server_name`\n4. (Optional) PragmaticWorks BIxPress Continue Execution on Error: `True`\n5. (Optional) PragmaticWorks BIxPress Reporting of Error on Failure: `False`\n\n## Contribution\n\nSee an area for improvement, please open an issue or send a PR.\n\n## Future Improvements\n\n- [ ] mypy type hints\n- [ ] add configuration file\n',
    'author': 'Mike Hosseini',
    'author_email': 'mahdihosseini75@gmail.com',
    'url': 'https://github.com/mahdi-hosseini/ssis_validator',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
