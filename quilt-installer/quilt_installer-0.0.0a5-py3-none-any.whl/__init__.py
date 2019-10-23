from pathlib import Path

name = "quilt-installer"

p = Path(__file__).parent/"VERSION"
__version__ = p.open().read()


