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

from ncapi_client.messages import *
from ncapi_client.utils import map_response, SyncWebSocket, handle_response, APIError
from time import sleep
import halo
import re

import numpy as np


# TODO: different clients for different types of sessions?
# TODO: support multiple backends, e.g. 0MQ / REST
class Session:
    """Session"""

    def __init__(
        self,
        client,
        uuid,
        start_client=False,
        notebook=True,
        session_endpoint=None,
        verify_ssl=True,
        socket_params=None,
    ):
        """__init__

        Args:
            client: API client
            uuid: uuid of the session
            start_client: whether to automatically start the websocket client, default False
            notebook: whether to use in notebook mode, defaults to True
            session_endpoint: custom endpoint for websockets, defaults to the client endpoint with port 5000 replaced by 5010
            verify_ssl: whether to verify ssl certificate for websocket connections, defaults to True
            socket_params: custom dict to specify wbesocket connection parameters, such as max message size
                (see https://websockets.readthedocs.io/en/stable/api.html#module-websockets.client)
        """
        self.url = client.url
        self._session = client._session
        self.uuid = uuid
        if session_endpoint is None:
            self._ws_url = f"{self.url.replace('http', 'ws')}/session?jwt={client.access_token}&session_id={uuid}"
        else:
            self._ws_url = f"{session_endpoint}?jwt={client.access_token}&session_id={uuid}"

        self._ws = None
        if start_client:
            self.start_client(
                notebook=notebook, verify_ssl=verify_ssl, socket_params=socket_params
            )

    @staticmethod
    def start(
        client,
        trained_model_id,
        dataset_id,
        sample_id,
        parametrizer_type="rbf",
        notebook=True,
        endpoint=None,
        verify_ssl=True,
        socket_params=None,
    ):
        """Start a session for a given model and sample
        
        Args:
            trained_model_id: the uuid or name of a trained_model
            dataset_id: uuid or name of the dataset
            sample_id: sample id, string
            parametrizer_type: a string definining the type of the parametrizer
            notebook: whether to use in notebook mode, defaults to True
            endpoint: custom endpoint for websockets, defaults to the client endpoint with port 5000 replaced by 5010
            verify_ssl: whether to verify ssl certificate for websocket connections, defaults to True
            socket_params: custom dict to specify wbesocket connection parameters, such as max message size
                (see https://websockets.readthedocs.io/en/stable/api.html#module-websockets.client)
        """
        payload = dict(
            trained_model_id=trained_model_id,
            sample_id=sample_id,
            dataset_id=dataset_id,
            parametrizer_type=parametrizer_type,
        )
        resp = handle_response(
            client._session.post(f"{client.url}/api/session/start", json=payload)
        )
        session = Session(
            client,
            resp["id"],
            start_client=True,
            notebook=notebook,
            session_endpoint=endpoint,
            verify_ssl=verify_ssl,
            socket_params=socket_params,
        )
        return session

    def _wait_until_ready(self, notebook=True, timeout=120):
        status = ""
        if notebook:
            sp_cls = halo.HaloNotebook
        else:
            sp_cls = halo.Halo
        spinner = sp_cls(text="Session starting", spinner="dots")
        spinner.start()
        t = 0
        while status not in ["RUNNING", "ERROR"] and t < timeout:
            status = self.info["status"]
            sleep(1)
        if status == "RUNNING":
            spinner.succeed("Session running!")
            # TODO: status Running indicates deployment of interactive session service is done, the port
            # on the websocket may need more time to respond.
            sleep(30)

        else:
            spinner.fail("Session failed to start")
            sleep(1)

    @property
    def sample(self):
        """Gets current sample as a pair of numpy arrays, [V, 3] verts float32, [F, 3] faces, int64"""
        self._send(MSG_GET_MESH)
        return seq2dict(self._recv())

    @sample.setter
    def sample(self, value):
        if isinstance(value, (list, tuple)) and len(value) == 2:
            if isinstance(value[0], np.ndarray) and isinstance(value[1], np.ndarray):
                self._send(MSG_SET_MESH, value[0], value[1])
                _ = self._recv()
            elif isinstance(value[0], str) and isinstance(value[1], str):
                self._send(MSG_SET_MESH_BY_ID, value[0], value[1])
                _ = self._recv()
            else:
                raise ValueError("Expecting (dataset_id, sample_id) or (verts, adj)")
        else:
            raise ValueError("Expecting (dataset_id, sample_id) or (verts, adj)")

    @property
    def model_id(self):
        """Gets the current model id"""
        self._send(MSG_GET_MODEL)
        model_id = self._recv()
        return model_id

    @model_id.setter
    def model_id(self, value):
        self._send(MSG_SET_MODEL_BY_ID, value)
        _ = self._recv()

    def predict(self, **kwargs):
        """Makes a prediction for the current mesh
        If `dataset_id` or (`verts`, `faces`) are set, prediction is done for the
        provided mesh.
        
        Args:
            dataset_id: identifier of a dataset (uuid or name)
            sample_id: identifier of a sample within the dataset
            verts: [N,3] float32 array, vertex coordinates
            faces: [F,3] int32 array
            input_scalars: [S,] - float32 vector, scalar inputs
            input_fields: [N,NF] - float32 array, field inputs
        
        Returns:
            a dict with the outputs
        """
        self._send(MSG_GET_PREDICTION, *dict2seq(kwargs))
        preds = self._recv()
        return seq2dict(preds)

    # TODO: we should be able to get a list of scalars here

    def apply_deformation(self, **kwargs):
        """Apply deformation given a set of parameters
        
        Args:
            params: a level-one dict
        
        Returns:
            verts: [N,3] float32 array, deformed vertex coordinates
        """
        # TODO: this we can extend with deformation-specific options
        self._send(MSG_APPLY_DEFORMATION, *dict2seq(kwargs))
        verts = self._recv()
        return verts

    @property
    @map_response
    def info(self):
        """Session info"""
        return self._session.get(f"{self.url}/api/session/{self.uuid}")

    @map_response
    def delete(self):
        """Delete session"""
        return self._session.delete(f"{self.url}/api/session/{self.uuid}")

    def start_client(self, notebook=True, verify_ssl=True, socket_params=None):
        """start_client
        Starts websocket client

        Args:
            notebook: whether to use in notebook mode, defaults to True
            verify_ssl: whether to verify ssl certificate for websocket connections, defaults to True
            socket_params: custom dict to specify wbesocket connection parameters, such as max message size
                (see https://websockets.readthedocs.io/en/stable/api.html#module-websockets.client)
        """
        if self._ws is not None:
            return
        self._wait_until_ready(notebook=notebook)
        if socket_params is None:
            socket_params = {}
        self._ws = SyncWebSocket(self._ws_url, verify_ssl=verify_ssl, **socket_params)

    def _send(self, *args):
        if self._ws is None:
            raise RuntimeError("Please start client")
        self._ws.send(msg_multipart(*args))

    def _recv(self):
        if self._ws is None:
            raise RuntimeError("Please start client")
        header, body = msg_parse(self._ws.recv())
        if header != MSG_MULTIPART or len(body) < 1:
            raise ValueError("Expecting multipart message")
        msg_type = body[0]
        if msg_type == MSG_ERROR:
            raise ValueError(f"{body[1]}")

        if len(body) > 2:
            return body[1:]
        elif len(body) == 2:
            return body[1]
        else:
            return msg_type
