# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Various constants used throughout AutoML."""


class FeaturizationConfigMode:
    Auto = 'auto'
    Off = 'off'


class FeatureType:
    """Names for feature types that are recognized."""

    Numeric = 'Numeric'
    DateTime = 'DateTime'
    Categorical = 'Categorical'
    CategoricalHash = 'CategoricalHash'
    Text = 'Text'
    Hashes = 'Hashes'
    Ignore = 'Ignore'
    AllNan = 'AllNan'

    FULL_SET = {Numeric, DateTime, Categorical, CategoricalHash, Text, Hashes, Ignore, AllNan}

    # List of features types that are dropped and not featurized
    DROP_SET = {Hashes, Ignore, AllNan}


class _FeaturizersType:
    """Names for featurizer factory types"""
    Numeric = 'numeric'
    DateTime = 'datetime'
    Categorical = 'categorical'
    Text = 'text'
    Generic = 'generic'


class SupportedTransformers:
    """Customer Facing Names for transformers supported by AutoML."""

    # Generic
    ImputationMarker = 'ImputationMarker'
    Imputer = 'Imputer'
    MaxAbsScaler = 'MaxAbsScaler'

    # Categorical
    CatImputer = 'CatImputer'
    HashOneHotEncoder = 'HashOneHotEncoder'
    LabelEncoder = 'LabelEncoder'
    CatTargetEncoder = 'CatTargetEncoder'
    WoETargetEncoder = 'WoETargetEncoder'
    OneHotEncoder = 'OneHotEncoder'

    # DateTime
    DateTimeTransformer = 'DateTimeTransformer'

    # Text
    CountVectorizer = 'CountVectorizer'
    NaiveBayes = 'NaiveBayes'
    StringCast = 'StringCast'
    TextTargetEncoder = 'TextTargetEncoder'
    TfIdf = 'TfIdf'
    WordEmbedding = 'WordEmbedding'

    BLOCK_TRANSFORMERS = {
        HashOneHotEncoder,
        LabelEncoder,
        CatTargetEncoder,
        WoETargetEncoder,
        OneHotEncoder,
        CountVectorizer,
        NaiveBayes,
        TextTargetEncoder,
        TfIdf,
        WordEmbedding
    }

    FULL_SET = {
        ImputationMarker,
        Imputer,
        MaxAbsScaler,
        CatImputer,
        HashOneHotEncoder,
        LabelEncoder,
        CatTargetEncoder,
        WoETargetEncoder,
        OneHotEncoder,
        DateTimeTransformer,
        CountVectorizer,
        NaiveBayes,
        StringCast,
        TextTargetEncoder,
        TfIdf,
        WordEmbedding
    }


class SupportedTransformersInternal(SupportedTransformers):
    """Transformer Names for all transformers supported by AutoML, including those not exposed."""

    # Generic
    LambdaTransformer = 'LambdaTransformer'
    MiniBatchKMeans = 'MiniBatchKMeans'

    # Numeric
    BinTransformer = 'BinTransformer'

    # Text
    BagOfWordsTransformer = 'BagOfWordsTransformer'
    StringConcat = 'StringConcat'
    TextStats = 'TextStats'
    AveragedPerceptronTextTargetEncoder = 'AveragedPerceptronTextTargetEncoder'

    # TimeSeries
    GrainMarker = 'GrainMarker'
    MaxHorizonFeaturizer = 'MaxHorizonFeaturizer'
    Lag = 'Lag'
    RollingWindow = 'RollingWindow'
    STLFeaturizer = 'STLFeaturizer'

    # Ignore
    Drop = ''

    FULL_SET = {
        LambdaTransformer,
        MiniBatchKMeans,
        BinTransformer,
        BagOfWordsTransformer,
        StringConcat,
        TextStats,
        AveragedPerceptronTextTargetEncoder,
        GrainMarker,
        MaxHorizonFeaturizer,
        Lag,
        RollingWindow,
        STLFeaturizer,
        Drop
    }.union(set(SupportedTransformers.FULL_SET))


class SupportedTransformersFactoryNames:
    """Method names for transformers. This is Featurizers factory method names."""

    class Generic:
        """Supported transformer factory method for generic type data."""

        ImputationMarker = 'imputation_marker'
        LambdaTransformer = 'lambda_featurizer'
        Imputer = 'imputer'
        MiniBatchKMeans = 'minibatchkmeans_featurizer'
        MaxAbsScaler = 'maxabsscaler'

    class Numeric:
        """Supported transformer factory method for numeric type data."""

        BinTransformer = 'bin_transformer'

    class Categorical:
        """Supported transformer factory method for categorical type data."""

        CatImputer = 'cat_imputer'
        HashOneHotVectorizerTransformer = 'hashonehot_vectorizer'
        LabelEncoderTransformer = 'labelencoder'
        CatTargetEncoder = 'cat_targetencoder'
        WoEBasedTargetEncoder = 'woe_targetencoder'
        OneHotEncoderTransformer = 'onehotencoder'

    class DateTime:
        """Supported transformer factory method for datetime type data."""

        DateTimeFeaturesTransformer = 'datetime_transformer'

    class Text:
        """Supported transformer factory method for text type data."""

        BagOfWordsTransformer = 'bow_transformer'
        CountVectorizer = 'count_vectorizer'
        NaiveBayes = 'naive_bayes'
        StringCastTransformer = 'string_cast'
        StringConcatTransformer = 'string_concat'
        StatsTransformer = 'text_stats'
        TextTargetEncoder = 'text_target_encoder'
        AveragedPerceptronTextTargetEncoder = 'averaged_perceptron_text_target_encoder'
        TfidfVectorizer = 'tfidf_vectorizer'
        WordEmbeddingTransformer = 'word_embeddings'


class TransformerName:
    """Transformer names with customer and factory method names."""

    def __init__(self, customer_transformer_name, transformer_method_name):
        """Init TransformerName."""
        self.customer_transformer_name = customer_transformer_name
        self.transformer_method_name = transformer_method_name


class SupportedTransformerNames:
    """A list of supported transformers with all customer name and factory method name."""

    SupportedGenericTransformerList = [
        TransformerName(
            SupportedTransformersInternal.ImputationMarker,
            SupportedTransformersFactoryNames.Generic.ImputationMarker
        ),
        TransformerName(
            SupportedTransformersInternal.LambdaTransformer,
            SupportedTransformersFactoryNames.Generic.LambdaTransformer
        ),
        TransformerName(
            SupportedTransformersInternal.Imputer,
            SupportedTransformersFactoryNames.Generic.Imputer
        ),
        TransformerName(
            SupportedTransformersInternal.MiniBatchKMeans,
            SupportedTransformersFactoryNames.Generic.MiniBatchKMeans
        ),
        TransformerName(
            SupportedTransformersInternal.MaxAbsScaler,
            SupportedTransformersFactoryNames.Generic.MaxAbsScaler
        ),
    ]

    SupportedNumericTransformerList = [
        TransformerName(
            SupportedTransformersInternal.BinTransformer,
            SupportedTransformersFactoryNames.Numeric.BinTransformer
        )
    ]

    SupportedCategoricalTransformerList = [
        TransformerName(
            SupportedTransformersInternal.CatImputer,
            SupportedTransformersFactoryNames.Categorical.CatImputer
        ),
        TransformerName(
            SupportedTransformersInternal.HashOneHotEncoder,
            SupportedTransformersFactoryNames.Categorical.HashOneHotVectorizerTransformer
        ),
        TransformerName(
            SupportedTransformersInternal.LabelEncoder,
            SupportedTransformersFactoryNames.Categorical.LabelEncoderTransformer
        ),
        TransformerName(
            SupportedTransformersInternal.CatTargetEncoder,
            SupportedTransformersFactoryNames.Categorical.CatTargetEncoder
        ),
        TransformerName(
            SupportedTransformersInternal.WoETargetEncoder,
            SupportedTransformersFactoryNames.Categorical.WoEBasedTargetEncoder
        ),
        TransformerName(
            SupportedTransformersInternal.OneHotEncoder,
            SupportedTransformersFactoryNames.Categorical.OneHotEncoderTransformer)
    ]

    SupportedDateTimeTransformerList = [
        TransformerName(
            SupportedTransformersInternal.DateTimeTransformer,
            SupportedTransformersFactoryNames.DateTime.DateTimeFeaturesTransformer
        )
    ]

    SupportedTextTransformerList = [
        TransformerName(
            SupportedTransformersInternal.BagOfWordsTransformer,
            SupportedTransformersFactoryNames.Text.BagOfWordsTransformer
        ),
        TransformerName(
            SupportedTransformersInternal.CountVectorizer,
            SupportedTransformersFactoryNames.Text.CountVectorizer
        ),
        TransformerName(
            SupportedTransformersInternal.NaiveBayes,
            SupportedTransformersFactoryNames.Text.NaiveBayes
        ),
        TransformerName(
            SupportedTransformersInternal.StringCast,
            SupportedTransformersFactoryNames.Text.StringCastTransformer
        ),
        TransformerName(
            SupportedTransformersInternal.StringConcat,
            SupportedTransformersFactoryNames.Text.StringConcatTransformer
        ),
        TransformerName(
            SupportedTransformersInternal.TextStats,
            SupportedTransformersFactoryNames.Text.StatsTransformer
        ),
        TransformerName(
            SupportedTransformersInternal.TextTargetEncoder,
            SupportedTransformersFactoryNames.Text.TextTargetEncoder
        ),
        TransformerName(
            SupportedTransformersInternal.TfIdf,
            SupportedTransformersFactoryNames.Text.TfidfVectorizer
        ),
        TransformerName(
            SupportedTransformersInternal.AveragedPerceptronTextTargetEncoder,
            SupportedTransformersFactoryNames.Text.AveragedPerceptronTextTargetEncoder
        ),
        TransformerName(
            SupportedTransformersInternal.WordEmbedding,
            SupportedTransformersFactoryNames.Text.WordEmbeddingTransformer
        )
    ]


class TransformerNameMappings:
    """Transformer name mappings."""

    CustomerFacingTransformerToTransformerMapGenericType = dict(zip(
        [transformer.customer_transformer_name for transformer
         in SupportedTransformerNames.SupportedGenericTransformerList],
        [transformer.transformer_method_name for transformer
         in SupportedTransformerNames.SupportedGenericTransformerList]))

    CustomerFacingTransformerToTransformerMapCategoricalType = dict(zip(
        [transformer.customer_transformer_name for transformer
         in SupportedTransformerNames.SupportedCategoricalTransformerList],
        [transformer.transformer_method_name for transformer
         in SupportedTransformerNames.SupportedCategoricalTransformerList]))

    CustomerFacingTransformerToTransformerMapNumericType = dict(zip(
        [transformer.customer_transformer_name for transformer
         in SupportedTransformerNames.SupportedNumericTransformerList],
        [transformer.transformer_method_name for transformer
         in SupportedTransformerNames.SupportedNumericTransformerList]))

    CustomerFacingTransformerToTransformerMapDateTimeType = dict(zip(
        [transformer.customer_transformer_name for transformer
         in SupportedTransformerNames.SupportedDateTimeTransformerList],
        [transformer.transformer_method_name for transformer
         in SupportedTransformerNames.SupportedDateTimeTransformerList]))

    CustomerFacingTransformerToTransformerMapText = dict(zip(
        [transformer.customer_transformer_name for transformer
         in SupportedTransformerNames.SupportedTextTransformerList],
        [transformer.transformer_method_name for transformer
         in SupportedTransformerNames.SupportedTextTransformerList]))


class _TransformerOperatorMappings:
    from azureml.automl.core._engineered_feature_names import _OperatorNames
    Imputer = {
        'mean': _OperatorNames.Mean,
        'most_frequent': _OperatorNames.Mode,
        'median': _OperatorNames.Median
    }


class TextNeuralNetworks:
    """Names of neural models swept for text classification."""

    BILSTM = "BiLSTMTextEmbeddings"
    BERT = "PreTrainedDNNEmbeddings"
    ALL = [BILSTM, BERT]
