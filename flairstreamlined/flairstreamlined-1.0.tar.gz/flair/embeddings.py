import re
from typing import List, Union

import numpy as np
from torch.nn import Module
from torch import cat, float, zeros, no_grad, enable_grad, FloatTensor


from torch.nn.utils.rnn import pack_padded_sequence, pad_packed_sequence

import flair
from .data import Sentence


class Embeddings(Module):
    """Abstract base class for all embeddings. Every new type of embedding must implement these methods."""

    def embed(self, sentences: Union[Sentence, List[Sentence]]) -> List[Sentence]:
        """Add embeddings to all words in a list of sentences. If embeddings are already added, updates only if embeddings
        are non-static."""
        # if only one sentence is passed, convert to list of sentence
        if type(sentences) is Sentence:
            sentences = [sentences]

        everything_embedded: bool = True

        if self.embedding_type == "word-level":
            for sentence in sentences:
                for token in sentence.tokens:
                    if self.name not in token._embeddings.keys():
                        everything_embedded = False
        else:
            for sentence in sentences:
                if self.name not in sentence._embeddings.keys():
                    everything_embedded = False

        if not everything_embedded or not self.static_embeddings:
            self._add_embeddings_internal(sentences)

        return sentences


class TokenEmbeddings(Embeddings):
    """Abstract base class for all token-level embeddings. Ever new type of word embedding must implement these methods."""

    @property
    def embedding_type(self) -> str:
        return "word-level"


class DocumentEmbeddings(Embeddings):
    """Abstract base class for all document-level embeddings. Ever new type of document embedding must implement these methods."""


class StackedEmbeddings(TokenEmbeddings):
    """A stack of embeddings, used if you need to combine several different embedding types."""

    def embed(
        self, sentences: Union[Sentence, List[Sentence]], static_embeddings: bool = True
    ):
        # if only one sentence is passed, convert to list of sentence
        if type(sentences) is Sentence:
            sentences = [sentences]

        for embedding in self.embeddings:
            embedding.embed(sentences)

    @property
    def embedding_length(self) -> int:
        return self.__embedding_length


class WordEmbeddings(TokenEmbeddings):
    """Standard static word embeddings, such as GloVe or FastText."""

    def _add_embeddings_internal(self, sentences: List[Sentence]) -> List[Sentence]:

        for i, sentence in enumerate(sentences):

            for token, token_idx in zip(sentence.tokens, range(len(sentence.tokens))):

                if "field" not in self.__dict__ or self.field is None:
                    word = token.text
                else:
                    word = token.get_tag(self.field).value

                if word in self.precomputed_word_embeddings:
                    word_embedding = self.precomputed_word_embeddings[word]
                elif word.lower() in self.precomputed_word_embeddings:
                    word_embedding = self.precomputed_word_embeddings[word.lower()]
                elif (
                    re.sub(r"\d", "#", word.lower()) in self.precomputed_word_embeddings
                ):
                    word_embedding = self.precomputed_word_embeddings[
                        re.sub(r"\d", "#", word.lower())
                    ]
                elif (
                    re.sub(r"\d", "0", word.lower()) in self.precomputed_word_embeddings
                ):
                    word_embedding = self.precomputed_word_embeddings[
                        re.sub(r"\d", "0", word.lower())
                    ]
                else:
                    word_embedding = np.zeros(self.embedding_length, dtype="float")

                word_embedding = FloatTensor(word_embedding)

                token.set_embedding(self.name, word_embedding)

        return sentences

class FlairEmbeddings(TokenEmbeddings):
    """Contextual string embeddings of words, as proposed in Akbik et al., 2018."""

    def train(self, mode=True):

        # make compatible with serialized models (TODO: remove)
        if "fine_tune" not in self.__dict__:
            self.fine_tune = False
        if "chars_per_chunk" not in self.__dict__:
            self.chars_per_chunk = 512

        if not self.fine_tune:
            pass
        else:
            super(FlairEmbeddings, self).train(mode)

    def _add_embeddings_internal(self, sentences: List[Sentence]) -> List[Sentence]:

        # gradients are enable if fine-tuning is enabled
        gradient_context = enable_grad() if self.fine_tune else no_grad()

        with gradient_context:

            # if this is not possible, use LM to generate embedding. First, get text sentences
            text_sentences = [sentence.to_tokenized_string() for sentence in sentences]

            longest_character_sequence_in_batch: int = len(max(text_sentences, key=len))

            # pad strings with whitespaces to longest sentence
            sentences_padded: List[str] = []
            append_padded_sentence = sentences_padded.append

            start_marker = "\n"

            end_marker = " "
            extra_offset = len(start_marker)
            for sentence_text in text_sentences:
                pad_by = longest_character_sequence_in_batch - len(sentence_text)
                if self.is_forward_lm:
                    padded = "{}{}{}{}".format(
                        start_marker, sentence_text, end_marker, pad_by * " "
                    )
                    append_padded_sentence(padded)
                else:
                    padded = "{}{}{}{}".format(
                        start_marker, sentence_text[::-1], end_marker, pad_by * " "
                    )
                    append_padded_sentence(padded)

            # get hidden states from language model
            all_hidden_states_in_lm = self.lm.get_representation(
                sentences_padded, self.chars_per_chunk
            )

            # take first or last hidden states from language model as word representation
            for i, sentence in enumerate(sentences):
                sentence_text = sentence.to_tokenized_string()

                offset_forward: int = extra_offset
                offset_backward: int = len(sentence_text) + extra_offset

                for token in sentence.tokens:

                    offset_forward += len(token.text)

                    if self.is_forward_lm:
                        offset = offset_forward
                    else:
                        offset = offset_backward

                    embedding = all_hidden_states_in_lm[offset, i, :]

                    # if self.tokenized_lm or token.whitespace_after:
                    offset_forward += 1
                    offset_backward -= 1

                    offset_backward -= len(token.text)

                    if not self.fine_tune:
                        embedding = embedding.detach()

                    token.set_embedding(self.name, embedding.clone())

            all_hidden_states_in_lm = all_hidden_states_in_lm.detach()
            all_hidden_states_in_lm = None

        return sentences

class DocumentRNNEmbeddings(DocumentEmbeddings):

    @property
    def embedding_length(self) -> int:
        return self.__embedding_length

    def embed(self, sentences: Union[List[Sentence], Sentence]):
        """Add embeddings to all sentences in the given list of sentences. If embeddings are already added, update
         only if embeddings are non-static."""

        if type(sentences) is Sentence:
            sentences = [sentences]

        self.rnn.zero_grad()

        # the permutation that sorts the sentences by length, descending
        sort_perm = np.argsort([len(s) for s in sentences])[::-1]

        # the inverse permutation that restores the input order; it's an index tensor therefore LongTensor
        sort_invperm = np.argsort(sort_perm)

        # sort sentences by number of tokens
        sentences = [sentences[i] for i in sort_perm]

        self.embeddings.embed(sentences)

        longest_token_sequence_in_batch: int = len(sentences[0])

        # all_sentence_tensors = []
        lengths: List[int] = []

        # initialize zero-padded word embeddings tensor
        sentence_tensor = zeros(
            [
                len(sentences),
                longest_token_sequence_in_batch,
                self.embeddings.embedding_length,
            ],
            dtype=float,
            device=flair.device,
        )

        # fill values with word embeddings
        for s_id, sentence in enumerate(sentences):
            lengths.append(len(sentence.tokens))

            sentence_tensor[s_id][: len(sentence)] = cat(
                [token.get_embedding().unsqueeze(0) for token in sentence], 0
            )

        # TODO: this can only be removed once the implementations of word_dropout and locked_dropout have a batch_first mode
        sentence_tensor = sentence_tensor.transpose_(0, 1)

        # --------------------------------------------------------------------
        # FF PART
        # --------------------------------------------------------------------
        # use word dropout if set
        if self.use_word_dropout:
            sentence_tensor = self.word_dropout(sentence_tensor)

        if self.reproject_words:
            sentence_tensor = self.word_reprojection_map(sentence_tensor)

        sentence_tensor = self.dropout(sentence_tensor)
        packed = pack_padded_sequence(sentence_tensor, lengths)

        self.rnn.flatten_parameters()

        rnn_out, hidden = self.rnn(packed)

        outputs, output_lengths = pad_packed_sequence(rnn_out)

        outputs = self.dropout(outputs)

        # --------------------------------------------------------------------
        # EXTRACT EMBEDDINGS FROM RNN
        # --------------------------------------------------------------------
        for sentence_no, length in enumerate(lengths):
            last_rep = outputs[length - 1, sentence_no]

            embedding = last_rep
            if self.bidirectional:
                first_rep = outputs[0, sentence_no]
                embedding = cat([first_rep, last_rep], 0)

            sentence = sentences[sentence_no]
            sentence.set_embedding(self.name, embedding)

        # restore original order of sentences in the batch
        sentences = [sentences[i] for i in sort_invperm]
