"""
| Minecraft server configuration, update synchronisation and startup logic
|
| Maintained by Routh.IO
"""
from .core import MineInit


def main():
    """
    | Script entrypoint
    """
    return MineInit()


if __name__ == "__main__":
    main()
