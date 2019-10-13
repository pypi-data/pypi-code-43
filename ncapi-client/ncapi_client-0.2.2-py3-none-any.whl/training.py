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

from ncapi_client.utils import AttrDict, map_response, handle_response
from halo import HaloNotebook
import numpy as np
from time import sleep
from ncapi_client.trained_model import TrainedModel


class Training:
    """Training"""

    def __init__(self, client, uuid):
        """__init__

        Args:
            client: API client
            uuid (str): uuid or name of the model
        """
        self._session = client._session
        self.url = client.url
        self.uuid = uuid

    @staticmethod
    def submit(client, model_id, dataset_id, user_config=None):
        """Submit a new training to the API

        Args:
            client: API client
            model_id (str): uuid or name of the model to use for training
            dataset_id (str): uuid or name of the dataset to use for training
            user_config (dict): user config to override model config, defaults to None

        Returns:
            New Training
        """
        payload = dict(model_id=model_id, dataset_id=dataset_id)
        files = None
        if user_config is not None:
            for k in [
                "batch_size",
                "num_steps",
                "optimizer",
                "loss",
                "summary_every_n_steps",
                "save_every_n_steps",
                "test_every_n_steps",
                "max_to_keep",
            ]:
                if k not in user_config.keys():
                    raise ValueError(f"You  must provide {k} in the user config")
            for k in ["init_lr", "min_lr", "decay_rate", "decay_every"]:
                if k not in user_config["optimizer"].keys():
                    raise ValueError(
                        f"You must provide {k} in the optimizer section of the config"
                    )
            if user_config["batch_size"] != 1:
                raise ValueError("This version only supports a batch size of 1")
            payload.update({"user_config": user_config})
        resp = handle_response(
            client._session.post(f"{client.url}/api/training/submit", json=payload)
        )
        return Training(client, resp["uuid"])

    @map_response
    def delete(self):
        """delete this training

        Returns:
            AttrDict: API reponse
        """
        return self._session.delete(f"{self.url}/api/training/{self.uuid}")

    @property
    @map_response
    def info(self):
        """Get verbose info about the training

       Returns:
            AttrDict: The API response
        """
        return self._session.get(f"{self.url}/api/training/{self.uuid}")

    @map_response
    def stop(self):
        """stop this training

        Returns:
            AttrDict: API reponse
        """
        return self._session.post(f"{self.url}/api/training/{self.uuid}/stop")

    @map_response
    def restart(self):
        """restart this training

        Returns:
            AttrDict: API reponse
        """
        return self._session.post(f"{self.url}/api/training/{self.uuid}/restart")

    @map_response
    def cancel(self):
        """cancel this training"""
        return self._session.post(f"{self.url}/api/training/{self.uuid}/cancel")

    @property
    @map_response
    def logs(self):
        """Get training logs

        Returns:
            AttrDict: logs
        """
        return self._session.get(f"{self.url}/api/training/{self.uuid}/logs")

    @property
    @map_response
    def checkpoints(self):
        """Get training checkpoints

        Returns:
            AttrDict: checkpoints
        """
        return self._session.get(f"{self.url}/api/training/{self.uuid}/checkpoints")

    def save(self, checkpoint_id=None, name=None):
        """Save one of the training checkpoints (if any) as a trained model

        Args:
            checkpoint_id (str): id of the checkpoint to save, defaults to lates
            name (str): name of the saved model, defaults to auto generated

        Returns:
            upon success, a description of the newly created trained model.
        """
        payload = {}
        if checkpoint_id:
            payload["checkpoint_id"] = checkpoint_id
        else:
            payload["checkpoint_id"] = self.checkpoints["checkpoints"][-1]
        if name:
            payload["name"] = name
        resp = handle_response(
            self._session.post(
                f"{self.url}/api/training/{self.uuid}/save", json=payload
            )
        )
        return TrainedModel(
            AttrDict(url=self.url, _session=self._session), resp["uuid"]
        )

    def monitor(self):
        """Plot an interactive graph monitoring training metrics"""
        # we don't want to import these at modulke level, only if we need rendering
        import matplotlib.pyplot as plt
        import matplotlib.animation as animation

        logs = self.logs

        create_plot = True
        status = "RUNNING"
        while status == "RUNNING":
            if create_plot:
                fig = plt.figure(figsize=(10, 8))
                ax = fig.add_subplot(111)
                plt.ion()
                create_plot = False
            else:
                ax.clear()

            if len(logs.train) < 3:
                status = self.info["status"].split(".")[1]
                losses_train = np.array([[0, 1], [1, 1]])
                losses_val = np.array([[0, 1], [1, 1]])

            else:
                losses_train = np.array([[l["step"], l["loss"]] for l in logs.train])
                losses_val = np.array([[l["step"], l["loss"]] for l in logs.val])

            ax.plot(losses_train[:, 0], losses_train[:, 1], label="train")
            ax.plot(losses_val[:, 0], losses_val[:, 1], label="val")
            plt.xlabel("step")
            plt.ylabel("loss")
            fig.legend()

            fig.canvas.draw()
            fig.canvas.flush_events()
            plt.subplots_adjust(bottom=0.30)
            logs = self.logs
            status = self.info["status"].split(".")[1]
            sleep(3)
