"""Initialize tests (see conftest.py as well)."""


import os


# Enable debug mode for PtvPy to show all warnings
os.environ["PTVPY_DEBUG"] = "1"


if bool(os.environ.get("CI")):
    import matplotlib

    # Use non-GUI backend if running in CI which is headless
    # SVG seems significantly faster than Agg for some reason
    matplotlib.use("svg")
