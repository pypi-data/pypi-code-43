from ncapi_client.utils import (
    map_response,
    AttrDict,
    handle_response,
    delete_dependent_jobs,
)
import yaml


class Model:
    """Model"""

    def __init__(self, client, uuid):
        """__init__

        Args:
            client: API client object
            uuid (str): uuid or name of the dataset§
        """
        self._session = client._session
        self.url = client.url
        self.uuid = uuid
        # needed to force delete, not very nice though
        self._client = client

    @staticmethod
    def add(
        client, name=None, class_name=None, config=None, revision="latest", **kwargs
    ):
        """Add a model

        Args:
            name: name of the model
            class_name: class name, defaults to config value
            config: config, defaults to config value or 'latest'
            revision: model revision (defaults to 'latest')
            **kwargs: additional parameters to override the config

        Returns:
            new Model
        """
        assert name and class_name or config
        if not config:
            config = dict(name=name, class_name=class_name, revision=revision)
            if kwargs:
                config.update(kwargs)
            config = dict(model=config)
        if isinstance(config, str):
            post_kwargs = dict(json=yaml.safe_load(open(config)))
        else:
            post_kwargs = dict(json=config)
        resp = handle_response(
            client._session.post(f"{client.url}/api/model", **post_kwargs)
        )
        return Model(client, resp["uuid"])

    @property
    @map_response
    def info(self):
        """Model verbose info"""
        return self._session.get(f"{self.url}/api/model/{self.uuid}")

    @map_response
    def delete(self, force=False):
        """Delete this model
        Args:
            force (bool): force deletion of dependent resources (default False)
        """
        if force:
            delete_dependent_jobs(self._client, {"model": self.info.name})
        return self._session.delete(f"{self.url}/api/model/{self.uuid}")

    @property
    def config(self):
        """Model config"""
        # Hack - TODO: fix API response so that config is not nested and use map_response
        return AttrDict.convert(
            self._session.get(f"{self.url}/api/model/{self.uuid}/config").json()[
                "model"
            ]
        )

    def is_compatible_with(self, dataset):
        """is_compatible_with
        CLient-side check for compatibility of the model with a dataset. Checks that the dataset contains the required data for the model, and that number of (input/output) fields (resp scalars) are correct.

        Args:
            dataset: a Dataset object, to test compatibility with

        Returns:
            bool, indicating compatibility
        """
        data_schema = dataset.schema
        for k in [
            "input_fields",
            "input_scalars",
            "output_fields",
            "output_scalars",
            "fields",
            "scalars",
        ]:
            config = self.config
            if f"num_{k}" in config.keys() and config[f"num_{k}"] > 0:
                if not k in data_schema.names:
                    return False
                ki = data_schema.names.index(k)
                try:
                    shape = int(data_schema.shapes[ki][-1])
                except ValueError:
                    shape = None
                if not (shape is None or shape == int(config[f"num_{k}"])):
                    return False
        return True
