# -*- coding: utf-8 -*-
from pathlib import Path

import pytest

from cenv_tool.init_cenv import initialize_cenv
from cenv_tool.init_cenv import RC_CONTENT


@pytest.mark.datafiles('tests/home_test')
def test_initialize_cenv(datafiles):
    expected_result = 'some content\n' + RC_CONTENT
    config_path = Path(datafiles) / '.config/cenv'
    config_file = config_path / 'cenv.yml'
    autoenv_script_path = config_path / 'cenv.sh'
    zshrc = Path(datafiles) / '.zshrc'
    bashrc = Path(datafiles) / '.bashrc'
    autoenv_script_source_path = Path('cenv_tool/cenv.sh')
    config_file_source = Path('cenv_tool/cenv.yml')
    for _ in range(2):
        initialize_cenv(
            config_path=config_path,
            autoenv_script_path=autoenv_script_path,
            autoenv_script_source_path=autoenv_script_source_path,
            config_file=config_file,
            config_file_source=config_file_source,
            zshrc=zshrc,
            bashrc=bashrc,
        )
        assert expected_result == zshrc.read_text()
        assert expected_result == bashrc.read_text()
        assert autoenv_script_path.exists()
        assert config_file.exists()
        assert config_path.exists()
