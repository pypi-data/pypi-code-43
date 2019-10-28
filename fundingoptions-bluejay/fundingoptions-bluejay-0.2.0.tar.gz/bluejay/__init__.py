"""The BlueJay Client

A thin client around the BlueJay interface.

Currently supports:
- SNS
- Stdout (via Logging)
"""

__version__ = "0.2.0"

from . import backend, client, event

Client = client.Client

__all__ = ("Client",)
