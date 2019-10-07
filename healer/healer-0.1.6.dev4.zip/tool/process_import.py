#!/usr/bin/env python

"""
Apply global import policy
https://helpmanual.io/help/isort/
https://github.com/timothycrosley/isort/wiki/isort-Settings
"""

from __future__ import annotations

import os

from devrepo import base_dir, shell

project_dir = base_dir()
source_main_dir = f"{project_dir}/src/main"

for base_path, dir_name_list, file_name_list in os.walk(source_main_dir):
    dir_name_list.sort()  # string sort
    file_name_list.sort()  # string sort
    for file_name in file_name_list:
        file_path = os.path.join(base_path, file_name)
        if '__target__' in file_path:
            continue
        if '__pycache__' in file_path:
            continue
        if not file_path.endswith('.py'):
            continue
        if "healer/station/client" in file_path:
            print(f"{file_path} :: skip web client")
            continue
        print(file_path)
        command = (
            f'isort '
            f'-y '  # say 'yes'
            f'-sl '  # force single line
            f'-a "from __future__ import annotations" '  # add this import
            f"{file_path}"
        )
        os.system(command)
