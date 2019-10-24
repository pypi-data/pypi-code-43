import shutil
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Dict

from allennlp.commands.train import train_model
from allennlp.common import Params
from allennlp.models.archival import load_archive
from allennlp.predictors.predictor import Predictor

import microcosm_sagemaker.frameworks.allennlp.vanilla_predictor  # noqa
from microcosm_sagemaker.artifact import BundleInputArtifact, BundleOutputArtifact
from microcosm_sagemaker.bundle import Bundle
from microcosm_sagemaker.frameworks.allennlp.constants import ARTIFACT_NAME, CUDA_DEVICE
from microcosm_sagemaker.input_data import InputData


class AllenNLPBundle(Bundle):
    """
    Higher-order AllenNLP component that can wrap other models, serializing
    our configuration format the way that they expect.

    Note that any paths which appear in allennlp_parameters are expected to be
    relative to the `input_data` directory.

    """
    # To specify custom predictor
    predictor_name: str = "vanilla_predictor"
    allennlp_parameters: Dict[str, Any]

    def fit(self, input_data: InputData) -> None:
        allennlp_params = Params(self.allennlp_parameters)
        self.temporary_allennlp_dir = TemporaryDirectory()
        self.temporary_allennlp_path = Path(self.temporary_allennlp_dir.name)
        with input_data.cd():
            train_model(
                allennlp_params,
                self.temporary_allennlp_path,
            )

        self._set_predictor(self.temporary_allennlp_path)

    def save(self, output_artifact: BundleOutputArtifact) -> None:
        allen_nlp_path = self._allenlp_path(output_artifact.path)
        allen_nlp_path.mkdir(parents=True)

        for child in self.temporary_allennlp_path.iterdir():
            # NB: It is important to use `shutil.move` here rather than
            # `rename` because the former works across filesystems, and
            # SageMaker uses a different filesystem for its temporary
            # directories and the output artifact directory
            shutil.move(child, allen_nlp_path / child.name)

        self.temporary_allennlp_dir.cleanup()

    def load(self, input_artifact: BundleInputArtifact) -> None:
        self._set_predictor(self._allenlp_path(input_artifact.path))

    def _set_predictor(self, allennlp_path: Path) -> None:
        weights_path = allennlp_path / ARTIFACT_NAME

        archive = load_archive(
            allennlp_path / "model.tar.gz",
            weights_file=weights_path,
            cuda_device=CUDA_DEVICE,
        )

        self.predictor = Predictor.from_archive(archive, self.predictor_name)

    def _allenlp_path(self, artifact_path: Path):
        return Path(artifact_path) / "allennlp"
