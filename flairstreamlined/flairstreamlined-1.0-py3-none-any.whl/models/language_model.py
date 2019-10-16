from torch.nn import Module
from torch import tensor, long, cat
import math
from typing import List

from flair import device

# can maybe delete nn?

class LanguageModel(Module):
    """Container module with an encoder, a recurrent module, and a decoder."""

    def forward(self, input, hidden, ordered_sequence_lengths=None):
        encoded = self.encoder(input)
        emb = self.drop(encoded)

        self.rnn.flatten_parameters()

        output, hidden = self.rnn(emb, hidden)

        if self.proj is not None:
            output = self.proj(output)

        output = self.drop(output)

        decoded = self.decoder(
            output.view(output.size(0) * output.size(1), output.size(2))
        )

        return (
            decoded.view(output.size(0), output.size(1), decoded.size(1)),
            output,
            hidden,
        )

    def init_hidden(self, bsz):
        weight = next(self.parameters()).detach()
        return (
            weight.new(self.nlayers, bsz, self.hidden_size).zero_().clone().detach(),
            weight.new(self.nlayers, bsz, self.hidden_size).zero_().clone().detach(),
        )

    def get_representation(self, strings: List[str], chars_per_chunk: int = 512):
        # cut up the input into chunks of max charlength = chunk_size
        longest = len(strings[0])
        chunks = []
        splice_begin = 0
        for splice_end in range(chars_per_chunk, longest, chars_per_chunk):
            chunks.append([text[splice_begin:splice_end] for text in strings])
            splice_begin = splice_end

        chunks.append([text[splice_begin:longest] for text in strings])
        hidden = self.init_hidden(len(chunks[0]))

        output_parts = []

        # push each chunk through the RNN language model
        for chunk in chunks:

            sequences_as_char_indices: List[List[int]] = []
            for string in chunk:
                char_indices = [
                    self.dictionary.get_idx_for_item(char) for char in string
                ]
                sequences_as_char_indices.append(char_indices)

            batch = tensor(
                sequences_as_char_indices, dtype=long, device=device
            ).transpose(0, 1)

            prediction, rnn_output, hidden = self.forward(batch, hidden)

            output_parts.append(rnn_output)

        # concatenate all chunks to make final output
        output = cat(output_parts)

        return output

