def _load_configs():
    from pathlib import Path
    import toml
    import sdarray as sd

    config_dir = Path(sd.__path__[0]) / "config"

    for path in config_dir.glob("*.toml"):
        with open(path) as f:
            globals()[path.stem] = toml.load(f)


_load_configs()
