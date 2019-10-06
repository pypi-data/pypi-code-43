import logging
import numpy as np

from overrides import overrides
import torch
from torch.nn.functional import embedding

from vtorch.common.checks import ConfigurationError
from vtorch.data import Vocabulary
from vtorch.modules.token_embedders.token_embedder import TokenEmbedder
from vtorch.common import loading
from vtorch.modules.time_distributed import TimeDistributed
from vtorch.nn import utils

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


@TokenEmbedder.register("embedding")
class Embedding(TokenEmbedder):
    """
    A more featureful embedding module than the default in Pytorch.  Adds the ability to:

        1. embed higher-order inputs
        2. pre-specify the weight matrix
        3. use a non-trainable embedding
        4. project the resultant embeddings to some other dimension (which only makes sense with
           non-trainable embeddings).
        5. build all of this easily ``from_params``

    Note that if you are using our data API and are trying to embed a
    :class:`~vtorch.data.fields.TextField`, you should use a
    :class:`~vtorch.modules.TextFieldEmbedder` instead of using this directly.

    Parameters
    ----------
    num_embeddings : int
        Size of the dictionary of embeddings (vocabulary size).
    embedding_dim : int
        The size of each embedding vector.
    projection_dim : int, (optional, default=None)
        If given, we add a projection layer after the embedding layer.  This really only makes
        sense if ``trainable`` is ``False``.
    weight : torch.FloatTensor, (optional, default=None)
        A pre-initialised weight matrix for the embedding lookup, allowing the use of
        pretrained vectors.
    padding_index : int, (optional, default=None)
        If given, pads the output with zeros whenever it encounters the index.
    trainable : bool, (optional, default=True)
        Whether or not to optimize the embedding parameters.
    max_norm : float, (optional, default=None)
        If given, will renormalize the embeddings to always have a norm lesser than this
    norm_type : float, (optional, default=2)
        The p of the p-norm to compute for the max_norm option
    scale_grad_by_freq : boolean, (optional, default=False)
        If given, this will scale gradients by the frequency of the words in the mini-batch.
    sparse : bool, (optional, default=False)
        Whether or not the Pytorch backend should use a sparse representation of the embedding weight.
    pretrained_file : str, (optional, default=None)
        Used to keep track of what is the source of the weights and loading more embeddings at test time.
        **It does not load the weights from this pretrained_file.** For that purpose, use
        ``Embedding.from_params``.

    Returns
    -------
    An Embedding module.
    """
    def __init__(self,
                 num_embeddings: int,
                 embedding_dim: int,
                 projection_dim: int = None,
                 weight: torch.FloatTensor = None,
                 padding_index: int = None,
                 trainable: bool = True,
                 max_norm: float = None,
                 norm_type: float = 2.,
                 scale_grad_by_freq: bool = False,
                 sparse: bool = False,
                 pretrained_file_path: str = None, **kwargs) -> None:
        super(Embedding, self).__init__()
        self.num_embeddings = num_embeddings
        self.padding_index = padding_index
        self.max_norm = max_norm
        self.norm_type = norm_type
        self.scale_grad_by_freq = scale_grad_by_freq
        self.sparse = sparse
        self.output_dim = projection_dim or embedding_dim

        if weight is None and pretrained_file_path is None:
            if embedding_dim is None or num_embeddings is None:
                raise ConfigurationError("You have to define embedding_dim if you don't use pretrained weights")
            weight = torch.FloatTensor(num_embeddings, embedding_dim)
            self.weight = torch.nn.Parameter(weight, requires_grad=trainable)
            torch.nn.init.xavier_uniform_(self.weight)
        else:
            if pretrained_file_path is not None:
                weight = _read_pretrained_embeddings_file(file_path=pretrained_file_path, vocab=kwargs["vocab"],
                                                          namespace=kwargs["namespace"])
            if weight.size() != (num_embeddings, embedding_dim):
                raise ConfigurationError("A weight matrix was passed with contradictory embedding shapes.")
            self.weight = torch.nn.Parameter(weight, requires_grad=trainable)

        if self.padding_index is not None:
            self.weight.data[self.padding_index].fill_(0)

        if projection_dim:
            self._projection = torch.nn.Linear(embedding_dim, projection_dim)
        else:
            self._projection = None

    @overrides
    def get_output_dim(self) -> int:
        return self.output_dim

    @overrides
    def forward(self, inputs):  # pylint: disable=arguments-differ
        # inputs may have extra dimensions (batch_size, d1, ..., dn, sequence_length),
        # but embedding expects (batch_size, sequence_length), so pass inputs to
        # util.combine_initial_dims (which is a no-op if there are no extra dimensions).
        # Remember the original size.
        original_size = inputs.size()
        inputs = utils.combine_initial_dims(inputs)

        embedded = embedding(inputs, self.weight,
                             max_norm=self.max_norm,
                             norm_type=self.norm_type,
                             scale_grad_by_freq=self.scale_grad_by_freq,
                             sparse=self.sparse)

        # Now (if necessary) add back in the extra dimensions.
        embedded = utils.uncombine_initial_dims(embedded, original_size)

        if self._projection:
            projection = self._projection
            for _ in range(embedded.dim() - 2):
                projection = TimeDistributed(projection)
            embedded = projection(embedded)
        return embedded


def _read_pretrained_embeddings_file(file_path: str,
                                     vocab: Vocabulary,
                                     namespace: str = "tokens") -> torch.FloatTensor:
    """
    Returns and embedding matrix for the given vocabulary using the pretrained embeddings
    contained in the given file. Embeddings for tokens not found in the pretrained embedding file
    are randomly initialized using a normal distribution with mean and standard deviation equal to
    those of the pretrained embeddings.

    Parameters
    ----------
    file_path : str, required.
       A file path to embeddings stored locally
    vocab : Vocabulary, required.
        A Vocabulary object.
    namespace : str, (optional, default=tokens)
        The namespace of the vocabulary to find pretrained embeddings for.

    Returns
    -------
    A weight matrix with embeddings initialized from the read file.  The matrix has shape
    ``(vocab.get_vocab_size(namespace), embedding_dim)``, where the indices of words appearing in
    the pretrained embedding file are initialized to the pretrained embedding value.
    """

    vocab_size = vocab.get_vocab_size(namespace)
    model = loading.load_pickled_w2v_embeddings(file_path)
    embeddings_all = model.vectors
    embeddings_mean = float(np.mean(embeddings_all))
    embeddings_std = float(np.std(embeddings_all))
    embedding_matrix = torch.FloatTensor(vocab_size, model.vector_size).normal_(embeddings_mean, embeddings_std)
    index_to_token = vocab.get_index_to_token_vocabulary(namespace)
    for index, token in index_to_token.items():
        if token in model:
            embedding_matrix[index] = torch.FloatTensor(model[token])
    return embedding_matrix
