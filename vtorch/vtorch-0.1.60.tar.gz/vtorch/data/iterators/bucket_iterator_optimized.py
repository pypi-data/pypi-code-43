import os
import json
import logging
import random
from typing import List, Tuple, Iterable

from overrides import overrides

from vtorch.common.checks import ConfigurationError
from vtorch.data.dataset import Batch
from vtorch.data.instance import Instance
from vtorch.data.iterators import DataIterator
from vtorch.data.vocabulary import Vocabulary
from vtorch.data.fields import MetadataField

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


def sort_by_padding_reverse(instances: List[Instance],
                            fields_with_pretrained_tokenizers: List[str],
                            sorting_keys: List[Tuple[str, str]],  # pylint: disable=invalid-sequence-index
                            vocab: Vocabulary) -> List[Instance]:
    """
    Sorts the instances by their padding lengths, using the keys in
    ``sorting_keys`` (in the order in which they are provided).  ``sorting_keys`` is a list of
    ``(field_name, padding_key)`` tuples.
    """
    instances_with_lengths = []
    for serial_index, instance in enumerate(instances):
        # Make sure instance is indexed before calling .get_padding
        instance.index_fields(vocab, fields_with_pretrained_tokenizers, serial_index)
        padding_lengths = instance.get_padding_lengths()
        instance.add_field("sequence_length",
                           MetadataField([padding_lengths[field_name][padding_key]
                                          for (field_name, padding_key) in sorting_keys])
                           )
        instances_with_lengths.append(instance)
    instances_with_lengths.sort(key=lambda x: x["sequence_length"].metadata, reverse=True)
    # we can't have zero-length instances in case of ``pack_padded_sequence``
    for instance in instances_with_lengths:
        if instance["sequence_length"] == [0]:
            instance["sequence_length"].metadata = [1]
            instance["text"]._indexed_tokens = [1]
    return instances_with_lengths


@DataIterator.register("bucket_optimized")
class BucketIteratorOptimized(DataIterator):
    """
    An iterators which by default, pads batches with respect to the maximum input lengths `per
    batch`. Additionally, you can provide a list of field names and padding keys which the dataset
    will be sorted by before doing this batching, causing inputs with similar length to be batched
    together, making computation more efficient (as less time is wasted on padded elements of the
    batch).
    Parameters
    ----------
    sorting_keys : List[Tuple[str, str]]
        To bucket inputs into batches, we want to group the instances by padding length, so that we
        minimize the amount of padding necessary per batch. In order to do this, we need to know
        which fields need what type of padding, and in what order.
        For example, ``[("sentence1", "num_tokens"), ("sentence2", "num_tokens"), ("sentence1",
        "num_token_characters")]`` would sort a dataset first by the "num_tokens" of the
        "sentence1" field, then by the "num_tokens" of the "sentence2" field, and finally by the
        "num_token_characters" of the "sentence1" field.
        documentation somewhere that gives the standard padding keys used by different fields.
    biggest_batch_first : bool, optional (default=False)
        This is largely for testing, to see how large of a batch you can safely use with your GPU.
        This will let you try out the largest batch that you have in the data `first`, so that if
        you're going to run out of memory, you know it early, instead of waiting through the whole
        epoch to find out at the end that you're going to crash.
        Note that if you specify ``max_instances_in_memory``, the first batch will only be the
        biggest from among the first "max instances in memory" instances.
    batch_size : int, optional, (default = 32)
        The size of each batch of instances yielded when calling the iterators.
    batch_first : ``bool`` (default = ``False``)
            For many pytorch implementation batch_first=``False`` is default setting.
            Change it if you need.
    instances_per_epoch : int, optional, (default = None)
        See :class:`BasicIterator`.
    max_instances_in_memory : int, optional, (default = None)
        See :class:`BasicIterator`.
    maximum_samples_per_batch : ``Tuple[str, int]``, (default = None)
        See :class:`BasicIterator`.
    """

    def __init__(self,
                 sorting_keys: List[Tuple[str, str]],
                 biggest_batch_first: bool = False,
                 batch_size: int = 32,
                 batch_optimization_step_size: int = 10,
                 batch_first: bool = False,
                 batch_reverse_sort: bool = False,
                 instances_per_epoch: int = None,
                 max_instances_in_memory: int = None,
                 cache_instances: bool = False,
                 track_epoch: bool = False,
                 maximum_samples_per_batch: Tuple[str, int] = None,
                 fields_with_pretrained_tokenizers: List[str] = ()) -> None:
        if not sorting_keys:
            raise ConfigurationError("BucketIterator requires sorting_keys to be specified")

        super().__init__(cache_instances=cache_instances,
                         track_epoch=track_epoch,
                         batch_first=batch_first,
                         batch_size=batch_size,
                         instances_per_epoch=instances_per_epoch,
                         max_instances_in_memory=max_instances_in_memory,
                         maximum_samples_per_batch=maximum_samples_per_batch,
                         fields_with_pretrained_tokenizers=fields_with_pretrained_tokenizers)
        self._sorting_keys = sorting_keys
        self._biggest_batch_first = biggest_batch_first
        self._batch_optimization_step_size = batch_optimization_step_size
        self._batch_reverse_sort = batch_reverse_sort
        with open(os.path.abspath(os.path.join(os.path.dirname(__file__), 'length_bs_time.json')), 'r') as fp:
            self._length_bs_time = json.load(fp)
            self._MAX_BATCH_SIZE = 75

    @staticmethod
    def _get_max_sequence_length(instances: List[Instance]) -> int:
        return max([instance["sequence_length"].metadata[0] for instance in instances])

    def _get_new_batch(self, current_batch, left_data):
        # batch could not be bigger then maximum batch size
        if len(current_batch) >= self._MAX_BATCH_SIZE - self._batch_optimization_step_size:
            return current_batch, left_data[:self._batch_optimization_step_size], \
                   left_data[self._batch_optimization_step_size:]
        # add to current batch left data, if its size smaller then _batch_optimization_step_size
        if len(left_data) < self._batch_optimization_step_size + 1:
            return current_batch + left_data, [], []
        batch_max_length = self._get_max_sequence_length(current_batch)
        contender_max_length = self._get_max_sequence_length(left_data[:self._batch_optimization_step_size])
        if self._length_bs_time[f"{contender_max_length}"][f"{len(current_batch) + self._batch_optimization_step_size}"] > \
                self._length_bs_time[f"{batch_max_length}"][f"{len(current_batch)}"] + \
                self._length_bs_time[f"{contender_max_length}"][f"{self._batch_optimization_step_size}"]:
            return current_batch, left_data[:self._batch_optimization_step_size], \
                   left_data[self._batch_optimization_step_size:]
        return self._get_new_batch(current_batch + left_data[:self._batch_optimization_step_size],
                                   left_data[self._batch_optimization_step_size:])

    def _optimize_batching(self, data):
        batches = []
        if len(data) <= self._batch_optimization_step_size:
            return [Batch(data)]
        data.sort(key=lambda x: x["sequence_length"].metadata, reverse=self._batch_reverse_sort)
        current_batch = data[:self._batch_optimization_step_size]
        left_data = data[self._batch_optimization_step_size:]
        while len(current_batch) > 0:
            final_batch, current_batch, left_data = self._get_new_batch(current_batch, left_data)
            batches.append(Batch(final_batch))

        return batches

    @overrides
    def _create_batches(self, instances: Iterable[Instance], shuffle: bool) -> Iterable[Batch]:
        for instance_list in self._memory_sized_lists(instances):
            instance_list = sort_by_padding_reverse(instance_list,
                                                    self._fields_with_pretrained_tokenizers,
                                                    self._sorting_keys,
                                                    self.vocab)

            batches = self._optimize_batching(instance_list)
            move_to_front = self._biggest_batch_first and len(batches) > 1
            if move_to_front:
                # We'll actually pop the last _two_ batches, because the last one might not be full.
                batches.reverse()
                last_batch = batches.pop()
                penultimate_batch = batches.pop()
            if shuffle:
                # NOTE: if shuffle is false, the data will still be in a different order
                # because of the bucket sorting.
                random.shuffle(batches)
            if move_to_front:
                batches.insert(0, penultimate_batch)
                batches.insert(0, last_batch)
            yield from batches
