# -*- coding:utf-8 -*-
import re
from setuptools_scm import get_version


if __name__ == '__main__':
    version = get_version('..', relative_to=__file__)
    result = re.match(r'^\d+.\d+.\d+(-rc.\d)?$', version)

    print('YES' if result else 'NO')
