import logging
from inspect import currentframe, getouterframes
import datetime
from h5py import File as HDF5File
from .normalize import materialize_attr_values


def deprecated(message: str) -> None:
	frameinfo = getouterframes(currentframe())
	logging.warn(f"╭── " + message)
	logging.warn(f"╰──> at {frameinfo[2].filename}, line {frameinfo[2].lineno}")


def timestamp() -> str:
	return datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%S.%fZ")


def get_loom_spec_version(f: HDF5File) -> str:
	if "attrs" in f and "LOOM_SPEC_VERSION" in f["/attrs"]:
		return materialize_attr_values(f["/attrs"]["LOOM_SPEC_VERSION"][()])
	if "LOOM_SPEC_VERSION" in f.attrs:
		return materialize_attr_values(f.attrs["LOOM_SPEC_VERSION"])
	return "0.0.0"


def compare_loom_spec_version(f: HDF5File, v: str) -> int:
	vf = int("".join(get_loom_spec_version(f).split(".")))
	vc = int("".join(v.split(".")))
	if vf == vc:
		return 0
	if vf > vc:
		return 1
	return -1
