# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['policykit']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=5.1,<6.0',
 'attrs>=19.3,<20.0',
 'click>=7.0,<8.0',
 'colorama>=0.4.1,<0.5.0']

entry_points = \
{'console_scripts': ['kubectl-pk = policykit.cli:cli',
                     'pk = policykit.cli:cli',
                     'policykit = policykit.cli:cli']}

setup_kwargs = {
    'name': 'policykit',
    'version': '0.1.1',
    'description': 'A set of utilities and classes for working with Open Policy Agent based tools, including Gatekeeper and Conftest',
    'long_description': '# Policy Kit\n\nA set of utilities and classes for working with [Open Policy Agent](https://www.openpolicyagent.org/) based tools, including [Gatekeeper](https://github.com/open-policy-agent/gatekeeper) and [Conftest](https://github.com/instrumenta/conftest).\n\n\n## Installation\n\nPolicy Kit can be installed from PyPI using `pip` or similar tools:\n\n```\npip install policykit\n```\n\n\n## CLI\n\nThe module provides a CLI tool called `pk` for using some of the functionality.\n\n```console\n$ pk build *.rego\n[SecurityControls] Generating a ConstraintTemplate from "SecurityControls.rego"\n[SecurityControls] Searching "lib" for additional rego files\n[SecurityControls] Adding library from "lib/kubernetes.rego"\n[SecurityControls] Saving to "SecurityControls.yaml"\n```\n\nYou can also use the tool via Docker:\n\n```\ndocker run --rm -it -v $(pwd):/app  garethr/policykit build\n```\n\n\n## Python\n\nThis module currently contains one class, for working with `ConstraintTemplates` in Gatekeeper.\n\n```python\nfrom policykit import ConstraintTemplate\n\nwith open(path_to_rego_source_file, "r") as rego:\n    ct = ConstraintTemplate(name, rego.read())\nprint(ct.yaml())\n```\n\n\n## Action\n\n```\non: push\nname: Build\njobs:\n  gatekeeper:\n    runs-on: ubuntu-latest\n    steps:\n    - uses: actions/checkout@master\n    - name: Generate ConstraintTemplates for Gatekeeper\n      uses: garethr/policykit/action@master\n      with:\n        args: <directory-of-rego-source-files>\n    - name: Commit to repository\n      env:\n        GITHUB_TOKEN: ${{ secrets.github_token }}\n        COMMIT_MSG: |\n          Generated new ConstraintTemplates from Rego source\n          skip-checks: true\n      run: |\n        # Hard-code user config\n        git config user.email "<your-email-address>"\n        git config user.name "<your-username>"\n        git config --get-regexp "user\\.(name|email)"\n        # Update origin with token\n        git remote set-url origin https://x-access-token:${GITHUB_TOKEN}@github.com/${GITHUB_REPOSITORY}.git\n        # Checkout the branch so we can push back to it\n        git checkout master\n        git add .\n        # Only commit and push if we have changes\n        git diff --quiet && git diff --staged --quiet || (git commit -m "${COMMIT_MSG}"; git push origin master\n```\n\n\n## Notes\n\nA few caveats for anyone trying to use this module.\n\n* [Loading libraries with `lib`](https://github.com/open-policy-agent/frameworks/commit/55fa33d1cca93f3b133e76a48d2e19adbdeb9de3) is only supported in Gatekeeper HEAD today but should be in the next release.\n* This module does not support parameterized ConstraintTemplates\n',
    'author': 'Gareth Rushgrove',
    'author_email': 'gareth@morethanseven.net',
    'url': 'https://github.com/garethr/policykit',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
