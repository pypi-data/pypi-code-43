"""Test module `ptvpy._profile`"""


import os

import pytest
import toml
from cerberus import SchemaError

from ptvpy import _profile


def test_template():
    # Test path to default profile
    assert _profile.template_path().is_file()

    with open(_profile.template_path()) as stream:
        template_str = stream.read()
    # Regression test: ensure ASCII compatibility
    template_str.encode("ascii")

    # Should be valid TOML file
    assert toml.loads(template_str)


def test_create_profile(tmpdir):
    # Create path to file in temporary directory
    file_a = tmpdir.join("profile_a.toml")
    file_b = tmpdir.join("profile_b.toml")

    _profile.create_profile_file(file_a.strpath, data_files="*.tif*")
    assert file_a.isfile()

    with pytest.raises(FileExistsError):
        _profile.create_profile_file(file_a.strpath, data_files="flying/circus")

    # Recreate when overwrite is True
    _profile.create_profile_file(file_b.strpath, data_files="flying/circus")
    # Compare content with original file
    with open(_profile.template_path()) as stream:
        template = stream.read()

    assert file_a.read() == template
    assert file_b.read() != template
    assert "flying/circus" in file_b.read()


class Test_ProfileValidator:
    """Check the custom validators."""

    @pytest.mark.parametrize("number", [-100, -2, 0, 10, 888])
    def test_odd_rule(self, number):
        schema = {"field": {"odd": True, "type": "integer"}}
        validator = _profile.ProfileValidator(schema)
        assert validator.validate({"field": number + 1})
        assert not validator.validate({"field": number})
        assert "must be an odd number" in str(validator.errors)

        schema = {"field": {"odd": False, "type": "integer"}}
        validator = _profile.ProfileValidator(schema)
        assert validator.validate({"field": number})
        assert not validator.validate({"field": number + 1})
        assert "must be an even number" in str(validator.errors)

        with pytest.raises(SchemaError, match="must be of boolean type"):
            _profile.ProfileValidator({"field": {"odd": "true"}})
        with pytest.raises(SchemaError, match="must be of boolean type"):
            _profile.ProfileValidator({"field": {"odd": 1}})

    def test_path_rule(self, tmpdir):
        os.mkdir(tmpdir / "image_folder")
        with open(tmpdir / "image.tiff", "x"):
            pass
        tmpdir = str(tmpdir) + "/"

        schema = {"field": {"path": "file", "type": "string"}}
        validator = _profile.ProfileValidator(schema)
        assert validator.validate({"field": tmpdir + "image.tiff"})
        assert not validator.validate({"field": tmpdir + "image_folder"})
        assert "file doesn't exist" in str(validator.errors)
        assert not validator.validate({"field": tmpdir + "not_existing"})
        assert "file doesn't exist" in str(validator.errors)

        schema = {"field": {"path": "directory", "type": "string"}}
        validator = _profile.ProfileValidator(schema)
        assert validator.validate({"field": tmpdir + "image_folder"})
        assert not validator.validate({"field": tmpdir + "image.tiff"})
        assert "directory doesn't exist" in str(validator.errors)
        assert not validator.validate({"field": tmpdir + "not_existing"})
        assert "directory doesn't exist" in str(validator.errors)

        schema = {"field": {"path": "parent", "type": "string"}}
        validator = _profile.ProfileValidator(schema)
        assert validator.validate({"field": tmpdir + "image_folder"})
        assert validator.validate({"field": tmpdir + "image.tiff"})
        assert validator.validate({"field": tmpdir + "not_existing"})
        assert not validator.validate({"field": tmpdir + "not_existing/*"})
        assert "parent directory doesn't exist" in str(validator.errors)

        schema = {"field": {"path": "absolute", "type": "string"}}
        validator = _profile.ProfileValidator(schema)
        assert validator.validate({"field": tmpdir + "image_folder"})
        assert validator.validate({"field": tmpdir + "image.tiff"})
        assert not validator.validate({"field": "."})
        assert "path is not absolute" in str(validator.errors)

        schema = {"field": {"path": "absolute", "type": "string"}}
        validator = _profile.ProfileValidator(schema)
        assert validator.validate({"field": tmpdir + "image_folder"})
        assert validator.validate({"field": tmpdir + "image.tiff"})
        assert not validator.validate({"field": "."})
        assert "path is not absolute" in str(validator.errors)

        schema = {"field": {"path": ["file", "directory"], "type": "string"}}
        validator = _profile.ProfileValidator(schema)
        assert not validator.validate({"field": tmpdir + "image_folder"})
        assert "file doesn't exist" in str(validator.errors)
        assert not validator.validate({"field": tmpdir + "image.tiff"})
        assert "directory doesn't exist" in str(validator.errors)

        with pytest.raises(SchemaError, match="unallowed value folder"):
            _profile.ProfileValidator({"field": {"path": "folder"}})
        with pytest.raises(SchemaError, match="min length is 1"):
            _profile.ProfileValidator({"field": {"path": []}})

    def test_glob_rule(self, tmpdir):
        os.mkdir(tmpdir / "image_folder")
        with open(tmpdir / "image.tiff", "x"):
            pass
        tmpdir = str(tmpdir) + "/"

        schema = {"field": {"glob": "any", "type": "string"}}
        error_msg = "must match at least once"
        validator = _profile.ProfileValidator(schema)
        assert validator.validate({"field": tmpdir + "image*"})
        assert validator.validate({"field": tmpdir + "image_folder"})
        assert validator.validate({"field": tmpdir + "image.tiff"})
        assert not validator.validate({"field": tmpdir + "image_folder/*"})
        assert error_msg in str(validator.errors)
        assert not validator.validate({"field": tmpdir + "not_existing"})
        assert error_msg in str(validator.errors)

        schema = {"field": {"glob": "no_files", "type": "string"}}
        error_msg = "must match at least once and never a file"
        validator = _profile.ProfileValidator(schema)
        assert validator.validate({"field": tmpdir + "image_*"})
        assert not validator.validate({"field": tmpdir + "image*"})
        assert error_msg in str(validator.errors)

        schema = {"field": {"glob": "no_dirs", "type": "string"}}
        error_msg = "must match at least once and never a directory"
        validator = _profile.ProfileValidator(schema)
        assert validator.validate({"field": tmpdir + "image.*"})
        assert not validator.validate({"field": tmpdir + "image*"})
        assert error_msg in str(validator.errors)

        schema = {"field": {"glob": "never", "type": "string"}}
        error_msg = "must never match"
        validator = _profile.ProfileValidator(schema)
        assert validator.validate({"field": tmpdir + "*/*"})
        assert validator.validate({"field": tmpdir + "not_existing"})
        assert not validator.validate({"field": tmpdir + "image.*"})
        assert error_msg in str(validator.errors)
        assert not validator.validate({"field": tmpdir + "image_*"})
        assert error_msg in str(validator.errors)
        assert not validator.validate({"field": tmpdir + "image*"})
        assert error_msg in str(validator.errors)

        with pytest.raises(SchemaError, match="unallowed value all"):
            _profile.ProfileValidator({"field": {"glob": "all"}})
        with pytest.raises(SchemaError, match="must be of string type"):
            _profile.ProfileValidator({"field": {"glob": False}})
