"""matwrap.py: wrapper around matplotlib."""
import json
import warnings
from pkg_resources import resource_filename


class MatWrap:

    _rc_defaults_path = resource_filename("shinyutils", "data/mplcfg.json")
    with open(_rc_defaults_path, "r") as f:
        _rc_defaults = json.load(f)

    _mpl = None
    _plt = None
    _sns = None

    @classmethod
    def configure(
        cls,
        context="paper",
        style="ticks",
        font="Latin Modern Roman",
        latex_pkgs=None,
        **rc_extra,
    ):
        """
        Arguments:
            context: seaborn context (paper/notebook/poster).
            style: seaborn style (whitegrid, darkgrid, etc.)
            font: latex font (passed directly to fontspec).
            latex_pkgs: list of packages to load in pgf preamble.
            rc_extra: matplotlib params (will overwrite defaults).
        """
        rc = MatWrap._rc_defaults.copy()
        rc["pgf.preamble"] = [r"\usepackage{fontspec}"]
        rc["pgf.preamble"].append(rf"\setmainfont{{{font}}}")
        rc["pgf.preamble"].append(rf"\setsansfont{{{font}}}")
        if latex_pkgs is not None:
            for pkg in reversed(latex_pkgs):
                rc["pgf.preamble"].insert(0, rf"\usepackage{{{pkg}}}")
        rc.update(rc_extra)

        if cls._mpl is None:
            import matplotlib

            cls._mpl = matplotlib
            cls._mpl.rcParams.update(rc)

            import matplotlib.pyplot
            import seaborn

            cls._plt = matplotlib.pyplot
            cls._sns = seaborn
        else:
            cls._mpl.rcParams.update(rc)
        cls._sns.set(context, style, rc=rc)

    def __new__(cls):
        raise NotImplementedError(
            "MatWrap does not provide instances. Use the class methods."
        )

    @classmethod
    def _ensure_conf(cls):
        if cls._mpl is None:
            cls.configure()

    @classmethod
    def mpl(cls):
        cls._ensure_conf()
        return cls._mpl

    @classmethod
    def plt(cls):
        cls._ensure_conf()
        return cls._plt

    @classmethod
    def sns(cls):
        cls._ensure_conf()
        return cls._sns

    @classmethod
    def palette(cls):
        return [
            "#e41a1c",
            "#6a3d9a",
            "#d55e00",
            "#34495e",
            "#377eb8",
            "#4daf4a",
            "#95a5a6",
            "#222222",
        ]

    @staticmethod
    def set_size_tight(fig, size):
        warnings.warn(
            "constrained_layout is enabled by default: don't use tight_layout",
            DeprecationWarning,
        )
        fig.set_size_inches(*size)
        fig.tight_layout(pad=0, w_pad=0, h_pad=0)
