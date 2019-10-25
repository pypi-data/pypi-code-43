# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""AutoML word embeddings provider."""
from typing import cast, Optional, Any

import logging
import os
import threading

from gensim.models.keyedvectors import KeyedVectors

from automl.client.core.common import logging_utilities
from automl.client.core.common.exceptions import ConfigException
from azureml.automl.core._downloader import Downloader
from .abstract_wordembeddings_provider import AbstractWordEmbeddingsProvider
from .word_embeddings_info import WordEmbeddingsInfo, EmbeddingInfo


class AutoMLPretrainedDNNProvider(AbstractWordEmbeddingsProvider):
    """AutoML word embeddings provider."""

    def __init__(self, logger: Optional[logging.Logger] = None,
                 model_name: str = "bert-base-uncased"):
        """Initialize class for providing word embeddings."""
        self._logger = logger or logging_utilities.get_logger()

        embeddings_info = WordEmbeddingsInfo.get(model_name)  # type: Optional[EmbeddingInfo]
        if embeddings_info is None:
            raise ConfigException("Unsupported pretrained\
            dnn type {0}".format(model_name))

        self._model = None
        self._dnn_zip_file = None  # type: Optional[KeyedVectors]
        self._lock = threading.Lock()  # type: threading.Lock
        self._embedding_info = embeddings_info
        self._tried_loading = False
        self._already_printed_credits = False
        super().__init__(embeddings_name=model_name)

    def _initialize(self) -> None:
        """
        Initialize the model.

        :return: None
        """
        with self._lock:
            if self._tried_loading is False:
                self._tried_loading = True
                self._load_from_disk()
            else:
                self._logger.info("Already tried loading embeddings but\
                failed. Cancelling retry.")

    def _get_model(self) -> Any:
        # The .model api is not used for pretrained text dnn
        return None

    def get_model_dirname(self) -> Any:
        """
        Return the embeddings model.

        :return: The embeddings model.
        """
        if not self._model:
            self._initialize()
        return self._model

    def _is_lower(self) -> bool:
        """
        Return whether the embeddings trained only on lower cased words.

        :return: Whether the embeddings trained only on lower cased words.
        """
        return self._embedding_info._lower_case

    def _get_vector_size(self) -> int:
        """
        Returns the vector size of the model

        :return: vector size of the model
        """
        return cast(int, self._model.vector_size)\
            if isinstance(self._model, KeyedVectors) else 0

    def _print_credits(self) -> None:
        """
        Print credits for the model being used.

        :return: None.
        """
        if not self._already_printed_credits:
            line_break = "--------------------------------------------------"
            print(line_break)
            print("Credits for document embeddings being used in the SDK.")
            print("Credits: {0}".format(self._embedding_info._credits))
            print("License: {0}".format(self._embedding_info._license))
            print(line_break)
            self._already_printed_credits = True

    def _load_from_disk(self) -> None:
        """
        Load an existing pickled model file.

        :return: None.
        """
        if self._dnn_zip_file is None or \
                Downloader.md5(self._dnn_zip_file) !=\
                self._embedding_info._md5hash:
            self._print_credits()
            self._download()

        if self._dnn_dir_name is None:
            self._logger.warning("Model loading failed from the\
             folder: {path} with error: {error}".format(
                path=self._dnn_dir_name)
            )
        else:
            self._model = self._dnn_dir_name  # return the model name

    def _download(self) -> None:
        """
        Download the pretrained zip file and extract into folder

        :return: None.
        """
        # TODO This should move to a logger.
        line_break = "------------------------------------------------------"
        print(line_break)
        print("Downloading\
        {0}.".format(self._embedding_info._user_friendly_name))

        # Download file.
        self._dnn_zip_file = Downloader.download(
            download_prefix=self._embedding_info._download_prefix,
            file_name=self._embedding_info._file_name,
            target_dir=self.embeddings_dir,
            prefix=str(self.__class__.__name__),
            md5hash=self._embedding_info._md5hash)
        # Unzip file
        self._dnn_file_info = Downloader.unzip_file(zip_fname=self._dnn_zip_file)

        # Get the path of one of the unzipped files, and extract the directory
        self._dnn_dir_name = os.path.dirname(self._dnn_file_info[0].filename)

    def __getstate__(self):
        """
        Overriden to remove model object when pickling.

        :return: this object's state as a dictionary
        """
        state = self.__dict__
        state['_lock'] = None
        state['_logger'] = None
        state['_tried_loading'] = False
        state['_model'] = None
        return state

    def __setstate__(self, state):
        """
        Overriden to set needed objects.

        :param state:
        :return:
        """
        self.__dict__.update(state)
        self._logger = logging_utilities.get_logger()
        self._lock = threading.Lock()
