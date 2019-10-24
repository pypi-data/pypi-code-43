from allennlp.predictors.predictor import Predictor


@Predictor.register("vanilla_predictor")
class VanillaPredictor(Predictor):
    """
    Predictor class that just does default allennlp prediction behavior.

    """
    pass
