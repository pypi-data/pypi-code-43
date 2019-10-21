import pandas as pd
import pytest

from azureml.studio.common.error import NotExpectedLabelColumnError
from azureml.studio.modules.datatransform.common.named_encoder import BinaryNamedLabelEncoder
from azureml.studio.modules.ml.initialize_models.evaluator import BinaryClassificationEvaluator

Scored_Label_Column = "Label"
Prob_Column = "Prob"


@pytest.mark.parametrize(
    'df',
    [
        pd.DataFrame(
            columns=[Scored_Label_Column, Prob_Column],
            data=[
                [0, 0.01],
                [1, 0.51],
                [0, 0.49],
                [1, 0.78]
            ]),
        pd.DataFrame(
            columns=[Scored_Label_Column, Prob_Column],
            data=[
                [0, 0.01],
                [1, 0.50],
                [0, 0.49],
                [1, 0.78]
            ]),
        pd.DataFrame(
            columns=[Scored_Label_Column, Prob_Column],
            data=[
                [0, 0.01],
                [1, 0.51],
                [0, 0.50],
                [1, 0.78]
            ]),
        pd.DataFrame(
            columns=[Scored_Label_Column, Prob_Column],
            data=[
                [0, 0.50],
                [1, 0.50],
                [0, 0.01],
                [1, 0.78]
            ])
    ]
)
def test_detect_label_mapping_two_labels(df):
    evaluator = BinaryClassificationEvaluator()
    evaluator.scored_label_column_name = Scored_Label_Column
    evaluator.prob_column_name = Prob_Column
    evaluator.label_encoder = BinaryNamedLabelEncoder()

    evaluator.detect_label_mapping(df)

    assert evaluator.label_encoder.positive_label == 1
    assert evaluator.label_encoder.negative_label == 0


@pytest.mark.parametrize(
    'df,expected_label_catetory',
    [
        (pd.DataFrame(
            columns=[Scored_Label_Column, Prob_Column],
            data=[
                [0, 0.01],
                [0, 0.49]
            ]), "negative_label"),
        (pd.DataFrame(
            columns=[Scored_Label_Column, Prob_Column],
            data=[
                [0, 0.51],
                [0, 0.78]
            ]), "positive_label"),
        (pd.DataFrame(
            columns=[Scored_Label_Column, Prob_Column],
            data=[
                [0, 0.01],
                [0, 0.50]
            ]), "negative_label"),
        (pd.DataFrame(
            columns=[Scored_Label_Column, Prob_Column],
            data=[
                [0, 0.50],
                [0, 0.78]
            ]), "positive_label")
    ]
)
def test_detect_label_mapping_one_label(df, expected_label_catetory):
    evaluator = BinaryClassificationEvaluator()
    evaluator.scored_label_column_name = Scored_Label_Column
    evaluator.prob_column_name = Prob_Column
    evaluator.label_encoder = BinaryNamedLabelEncoder()

    evaluator.detect_label_mapping(df)

    assert getattr(evaluator.label_encoder, expected_label_catetory) == 0


def test_detect_label_mapping_multi_labels():
    df = pd.DataFrame(
            columns=[Scored_Label_Column, Prob_Column],
            data=[
                [0, 0.01],
                [1, 0.49],
                [2, 0.78]
            ])

    evaluator = BinaryClassificationEvaluator()
    evaluator.scored_label_column_name = Scored_Label_Column
    evaluator.prob_column_name = Prob_Column
    evaluator.label_encoder = BinaryNamedLabelEncoder()

    evaluator.dataset_name = "Input Dataset"

    with pytest.raises(expected_exception=NotExpectedLabelColumnError,
                       match=f"The label column \"{evaluator.scored_label_column_name}\" is not expected in"
                       f" \"{evaluator.dataset_name}\""):
        evaluator.detect_label_mapping(df)
