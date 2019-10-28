"""The validation schema for profile files."""


def _scalar_or_pair(type_, **rules):
    """Expand scalar type to also allow a two-element list of the former.

    Parameters
    ----------
    type_ : str
        The type string.
    **rules
        Additional rules to include.

    Returns
    -------
    composite_type : dict
        A dictionary that allows a scalar or two-element list of the former.
    """
    return {
        "type": [type_, "list"],
        "schema": {"type": type_, **rules},
        "minlength": 2,
        "maxlength": 2,
        **rules,
    }


#: Sub-schema for validation of general fields in a profile.
_GENERAL = {
    "type": "dict",
    "schema": {
        "data_files": {"type": "string", "glob": "no_dirs", "required": True},
        "subset": {
            "type": "dict",
            "default": {"start": None, "step": None, "stop": None},
            "schema": {
                "start": {"type": "integer", "default": None, "nullable": True},
                "step": {"type": "integer", "default": None, "nullable": True},
                "stop": {"type": "integer", "default": None, "nullable": True},
            },
        },
        "storage_file": {"type": "string", "path": "parent", "required": True},
        "default_steps": {
            "type": "list",
            "schema": {"allowed": ["locate", "link", "diff"]},
            "required": True,
        },
    },
}


#: Sub-schema for validation of the section "step_locate" in a profile.
_STEP_LOCATE = {
    "type": "dict",
    "schema": {
        "remove_background": {"type": "boolean", "required": True},
        "particle_shape": {"allowed": ["blob", "helix"], "required": True},
        "parallel": {"type": "integer", "min": 1, "required": True},
        "trackpy_locate": {
            "type": "dict",
            "schema": {
                "diameter": {
                    **_scalar_or_pair("integer", min=0, odd=True),
                    "required": True,
                },
                "minmass": {"type": "float", "min": 0, "required": True},
                "maxsize": {
                    "type": "float",
                    "min": 0,
                    "default": None,
                    "nullable": True,
                },
                "separation": {
                    **_scalar_or_pair("float", min=0),
                    "default": None,
                    "nullable": True,
                },
                "noise_size": {**_scalar_or_pair("float", min=0), "required": True},
                "smoothing_size": {
                    **_scalar_or_pair("float", min=0),
                    "default": None,
                    "nullable": True,
                },
                "threshold": {"type": "float", "default": None, "nullable": True},
                "percentile": {"type": "float", "min": 0, "required": True},
                "topn": {
                    "type": "integer",
                    "min": 0,
                    "default": None,
                    "nullable": True,
                },
                "preprocess": {"type": "boolean", "required": True},
                "max_iterations": {"type": "integer", "min": 0, "required": True},
                "characterize": {"type": "boolean", "required": True},
                "engine": {"allowed": ["auto", "python", "numba"], "required": True},
            },
        },
        "helix": {
            "type": "dict",
            "schema": {
                "min_distance": {"type": "float", "min": 0, "required": True},
                "max_distance": {"type": "float", "min": 0, "required": True},
                "unique": {"type": "boolean", "required": True},
                "save_old_pos": {"type": "boolean", "required": True},
            },
        },
    },
}


#: Sub-schema for validation of the section "step_link" in a profile.
_STEP_LINK = {
    "type": "dict",
    "schema": {
        "trackpy_link": {
            "type": "dict",
            "schema": {
                "search_range": {**_scalar_or_pair("float", min=0), "required": True},
                "memory": {"type": "integer", "min": 0, "required": True},
                "adaptive_stop": {
                    "type": "float",
                    "min": 0,
                    "default": None,
                    "nullable": True,
                },
                "adaptive_step": {
                    "type": "float",
                    "min": 0,
                    "max": 1,
                    "required": True,
                },
                "neighbor_strategy": {"allowed": ["KDTree", "BTree"], "required": True},
                "link_strategy": {
                    "allowed": [
                        "recursive",
                        "nonrecursive",
                        "numba",
                        "hybrid",
                        "drop",
                        "auto",
                    ],
                    "required": True,
                },
            },
        },
        "trackpy_filter_stubs": {
            "type": "dict",
            "schema": {"threshold": {"type": "integer", "min": 0, "required": True}},
        },
    },
}


#: Sub-schema for validation of the section "step_diff" in a profile.
_STEP_DIFF = {
    "type": "dict",
    "schema": {"diff_step": {"type": "integer", "min": 0, "required": True}},
}


#: Root validation schema for a profile. Combines other sub-schemas.
SCHEMA = {
    "general": _GENERAL,
    "step_locate": _STEP_LOCATE,
    "step_link": _STEP_LINK,
    "step_diff": _STEP_DIFF,
}
