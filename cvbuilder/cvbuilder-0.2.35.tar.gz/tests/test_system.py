from cvbuilder import systems
from pathlib import Path

current = Path(Path(__file__).parent).joinpath("os-release")


def test_debian():
    lsb = systems.read_os_release(current.joinpath("debian"))

    assert lsb.id == "debian"
    assert lsb.version_id == "9"


def test_manjaro():
    lsb = systems.read_os_release(current.joinpath("manjaro"))

    assert lsb.id == "manjaro"
    assert not hasattr(lsb, "version_id")


def test_ubuntu():
    lsb = systems.read_os_release(current.joinpath("ubuntu"))

    assert lsb.id == "ubuntu"
    assert lsb.version_id == "16.04"
