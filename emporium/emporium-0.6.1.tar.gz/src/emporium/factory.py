from emporium.local import LocalStore
from emporium.memory import InMemoryStore
from emporium.s3 import RemoteStoreS3


def create_store(config, **extras):
    """Create a store, depending on config.

    :param config: Dictionary with the store configuration.  Should include a
        key ``type`` to determine which store gets instantiated.  Valid values
        for ``type`` are ``s3``, ``memory`` and ``local``.
    :param extras: Key-value pairs mapping type to a `from_config` like
        constructor.

    :returns: A store that implements :class:`emporium.base.AbstractStore`.
    """

    if "type" not in config:
        raise ValueError("Need to include key `type`")

    options = {
        "s3": RemoteStoreS3.from_config,
        "memory": InMemoryStore.from_config,
        "local": LocalStore.from_config,
    }
    options.update(extras)

    store_type = config["type"]
    if store_type in options:
        return options[store_type](config)
    raise ValueError("Value under `type` needs to one of {}".format(options.keys()))
