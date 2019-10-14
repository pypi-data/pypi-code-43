import plx
import environ
import packaging
import pathlib

from attrs_patch import attr

__version__ = "0.3.0"

# _prefix = '_'.join(__name__.upper().split('.')[:-1])
_config_prefix = "v2"


def _default_dataset_dir():
    path = pathlib.Path.cwd() / "dataset"
    if path.exists() and path.is_dir():
        return path

    path = pathlib.Path(__file__).parent.parent.parent / "dataset"
    return path


#: Proxy to global unit registry. This is a reference to the :class:`pint.UnitRegistry` proxy :data:`plx.units` in the
#: lcg-neuro-plx_ library, which this library depends on. If you need to operate with a different unit registry, use
#: :meth:`plx.units.set_registry` to update the global :class:`pint.UnitRegistry` object and keep consistency.
units = plx.units

#: These are the dataset versions the library is compatible with.
compatible_dataset_version_range = (
    packaging.version.parse("0.2.1"),
    packaging.version.parse("1.0.0"),
)


@environ.config(prefix=_config_prefix)
class Config:
    """Environment configuration required by this package, specified declaratively via environ_config_.
    """

    #: This is the directory were dataset files are kept. If not provided, defaults to the first valid directory of the
    #: following: the ``dataset`` sub-directory of the current working directory, or the ``dataset`` sub-directory of
    #: the source-code repository's root.
    dataset_dir: pathlib.Path = environ.var(
        default=_default_dataset_dir(),
        converter=lambda path: pathlib.Path(path).resolve(),
        validator=attr.validators.path_is_dir,
    )


#: Contains the environment configuration required by :mod:`v2_dataset`.
config: Config = environ.to_config(Config)
