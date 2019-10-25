from datasetmaker import clients
from datasetmaker.models import Client


def create_client(source: str) -> Client:
    """
    Factory function for creating new client instances.

    Parameters
    ----------
    source : str
        Name of source.
    """
    return clients.available[source]()  # type: ignore
