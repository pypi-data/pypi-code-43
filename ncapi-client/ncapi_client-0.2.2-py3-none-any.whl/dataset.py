"""
 NEURAL CONCEPT CONFIDENTIAL
 __________________
 
  [2018] Neural Concept SA-SARL, Lausanne, Switzerland
  All Rights Reserved.
 
 If you are reading this NOTICE as a result of a de-obfuscation
 or a reverse Engineering of Neural Concept’s software, you are likely
 breaking Neural Concept Shape’s End-User Licence Agreement. 
 Please contact Neural Concept Sarl without any delay.

 NOTICE:  All information contained herein is, and remains
 the property of Neural Concept and its suppliers,
 if any.  The intellectual and technical concepts contained
 herein are proprietary to Neural Concept
 and its suppliers and may be covered by European and Foreign Patents,
 patents in process, and are protected by trade secret or copyright law.
 Dissemination or usage of this information or reproduction of this material
 is strictly forbidden unless prior written permission is obtained
 from Neural Concept.
 Usage of file or code is subject to the terms and conditions defined in
 Neural Concept Shape’s End-User Licence Agreement.
""" 

from ncapi_client.utils import (
    AttrDict,
    ResourceList,
    map_response,
    handle_response,
    list_files_subdirs,
    wait_for_completion,
    delete_dependent_jobs,
    asyncio_run,
)
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from ncapi_client.job import Job
import warnings


class Dataset:
    """Dataset"""

    def __init__(self, client, uuid):
        """__init__

        Args:
            client: API client object
            uuid (str): uuid or name of the dataset
        """
        self._session = client._session
        self.url = client.url
        self.uuid = uuid
        # needed to force delete, not very nice though
        self._client = client

    @staticmethod
    def add(
        client,
        name,
        files,
        description=None,
        split=None,
        max_degree=10,
        notebook=True,
        user_config=None,
    ):
        """Add a new dataset

        Args:
            client: API client
            name (str): name of the new dataset
            files : list of paths to the files to add to the dataset, or path to a directory containing all the files to add
            description: dict description of the dataset, defaults to None
            split: dict representing the split, defaults to None
            max_degree (int): maximum number of neighbours in the data, defaults to 10
            user_config (dict): if provided, specifies a custom reader config, defaults to None

        Returns:
            The new dataset. Automatically starts its conversion to npy indiv
        """
        dataset = None
        if not description:
            description = {}
        description["name"] = name
        if split:
            description["split"] = split
        if max_degree:
            description["max_degree"] = max_degree
        resp = handle_response(
            client._session.post(f"{client.url}/api/dataset", json=description)
        )
        dataset = Dataset(client, resp["uuid"])
        if isinstance(files, str):
            files = list_files_subdirs(files)
            if len(files) == 0:
                warnings.warn(
                    "No data file was found. Please make sure the path provided is correct."
                )
                return dataset
        dataset.files_add(files)
        job = dataset.convert(user_config=user_config)
        wait_for_completion(job, jobtype="Conversion", notebook=notebook)
        return dataset

    def convert(self, target_format="npy_indiv", user_config=None):
        """Convert the dataset

        Args:
            target_format (str): for now only npy_indiv is supported. Defaults to npy_indiv
            user_config (dict): if provided, specifies a custom reader config, defaults to None

        Returns:
            API response, as AttrDict
        """
        payload = {}
        if target_format != "npy_indiv":
            raise NotImplementedError("Only npy_indiv target format is supported")
        payload["target_format"] = target_format
        if user_config is not None:
            payload["user_config"] = user_config
        resp = handle_response(
            self._session.post(
                f"{self.url}/api/dataset/{self.uuid}/convert", json=payload
            )
        )
        return Job(AttrDict(url=self.url, _session=self._session), uuid=resp["uuid"])

    @property
    @map_response
    def info(self):
        """AttrDict, verbose info for this dataset"""
        return self._session.get(f"{self.url}/api/dataset/{self.uuid}")

    @property
    @map_response
    def schema(self):
        """AttrDict, schema info for this dataset"""
        return self._session.get(f"{self.url}/api/dataset/{self.uuid}/schema")

    @map_response
    def delete(self, force=False):
        """delete
        Args:
            force (bool): force deletion of dependent resources (default False)
        """
        if force:
            delete_dependent_jobs(self._client, {"dataset": self.info.name})
        return self._session.delete(f"{self.url}/api/dataset/{self.uuid}")

    @property
    @map_response
    def files(self):
        """files list"""
        return self._session.get(f"{self.url}/api/dataset/{self.uuid}/files")

    def files_add(self, files):
        def upload(f):
            return self._session.post(
                f"{self.url}/api/dataset/{self.uuid}/files",
                files=[("file", open(f, "rb") if isinstance(f, str) else f)]
            )
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(upload, f) for f in files]
            for response in tqdm(as_completed(futures), total=len(files)):
                handle_response(response.result())
        return self.info

    @map_response
    def file_delete(self, file_id):
        """Delete a file from the dataset

        Args:
            file_id (str): id of the file

        Returns:
            AttrDict, API response
        """
        return self._session.delete(
            f"{self.url}/api/dataset/{self.uuid}/files/{file_id}"
        )

    @map_response
    def file(self, file_id):
        """Get verbose info about a file

        Args:
            file_id (str): id of the file

        Returns:
            AttrDict, the API response
        """
        return self._session.get(f"{self.url}/api/dataset/{self.uuid}/files/{file_id}")

    @property
    @map_response
    def samples(self):
        """samples list"""
        return self._session.get(f"{self.url}/api/dataset/{self.uuid}/samples")

    @map_response
    def sample(self, sample_id):
        """Return a dataset sample

        Args:
            sample_id (str): id of the sample

        Returns:
            The sample, as AttrDict
        """
        return self._session.get(
            f"{self.url}/api/dataset/{self.uuid}/samples/{sample_id}"
        )

    @property
    @map_response
    def split(self):
        """Dataset split as AttrDict"""
        return self._session.get(f"{self.url}/api/dataset/{self.uuid}/split")

    @property
    @map_response
    def formats(self):
        """List of formats"""
        return self._session.get(f"{self.url}/api/dataset/{self.uuid}/format/")

    @map_response
    def format(self, data_format):
        """Get verbose information about a format

        Args:
            data_format (str): data format

        Returns:
            API reponse as AttrDict
        """
        return self._session.get(
            f"{self.url}/api/dataset/{self.uuid}/format/{data_format}"
        )

    @map_response
    def format_delete(self, data_format):
        """Delete a format from thsi dataset

        Args:
            data_format (str): Format to delete

        Returns:
            API response as AttrDict
        """
        return self._session.delete(
            f"{self.url}/api/dataset/{self.uuid}/format/{data_format}"
        )

    def get_jobs(self):
        """get_jobs
        
        Returns:
            list of jobs related to this dataset
        """
        resp = handle_response(self._session.get(f"{self.url}/api/jobs"))
        name = self.info["name"]
        res = [
            d for d in resp if ("dataset" in d.keys() and d["dataset"] == name)
        ]  # TODO: hack - do we need a conversion API?
        return ResourceList(res)
