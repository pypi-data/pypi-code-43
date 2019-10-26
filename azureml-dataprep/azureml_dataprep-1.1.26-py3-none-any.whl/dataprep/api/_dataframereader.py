from ._pandas_helper import have_numpy, have_pandas, have_pyarrow, ensure_df_native_compat, PandasImportError, NumpyImportError
from .engineapi.api import get_engine_api
from .engineapi.engine import CancellationToken
from .engineapi.typedefinitions import ExecuteAnonymousActivityMessageArguments, AnonymousActivityData
from .errorhandlers import OperationCanceled
from .step import steps_to_block_datas
import io
import json
import math
from threading import Event, Thread
from typing import List
from uuid import uuid4


# 20,000 rows gives a good balance between memory requirement and throughput by requiring that only
# (20000 * CPU_CORES) rows are materialized at once while giving each core a sufficient amount of
# work.
PARTITION_SIZE = 20000


class _InconsistentSchemaError(Exception):
    def __init__(self):
        super().__init__('Inconsistent schemas encountered between partitions.')


class _PartitionIterator:
    def __init__(self, partition_id, table):
        self.id = partition_id
        self.is_canceled = False
        self._completion_event = Event()
        self._current_idx = 0
        self._dataframe = table.to_pandas()

    def __next__(self):
        if self._current_idx == len(self._dataframe):
            self._completion_event.set()
            raise StopIteration

        value = self._dataframe.iloc[self._current_idx]
        self._current_idx = self._current_idx + 1
        return value

    def wait_for_completion(self):
        self._completion_event.wait()

    def cancel(self):
        self.is_canceled = True
        self._completion_event.set()


class RecordIterator:
    def __init__(self, dataflow, cancellation_token: CancellationToken):
        self._iterator_id = str(uuid4())
        self._partition_available_event = Event()
        self._partitions = {}
        self._current_partition = None
        self._next_partition = 0
        self._done = False
        self._cancellation_token = cancellation_token
        get_dataframe_reader().register_iterator(self._iterator_id, self)

        def start_iteration():
            dataflow_to_execute = dataflow.add_step('Microsoft.DPrep.WriteFeatherToSocketBlock', {
                'dataframeId': self._iterator_id,
            })

            try:
                get_engine_api().execute_anonymous_activity(
                    ExecuteAnonymousActivityMessageArguments(anonymous_activity=AnonymousActivityData(blocks=steps_to_block_datas(dataflow_to_execute._steps))),
                    cancellation_token=self._cancellation_token)
            except OperationCanceled:
                pass
            self._clean_up()

        iteration_thread = Thread(target=start_iteration, daemon=True)
        iteration_thread.start()

        cancellation_token.register(self.cancel_iteration)

    def __next__(self):
        while True:
            if self._done and self._current_partition is None and len(self._partitions) == 0:
                raise StopIteration()

            if self._current_partition is None:
                if self._next_partition not in self._partitions:
                    self._partition_available_event.wait()
                    self._partition_available_event.clear()
                    continue
                else:
                    self._current_partition = self._partitions[self._next_partition]
                    self._next_partition = self._next_partition + 1

            if self._current_partition is not None:
                try:
                    return next(self._current_partition)
                except StopIteration:
                    self._partitions.pop(self._current_partition.id)
                    self._current_partition = None

    def cancel_iteration(self):
        for partition in self._partitions.values():
            partition.cancel()
        self._clean_up()

    def process_partition(self, partition: int, table: 'pyarrow.Table'):
        if self._cancellation_token.is_canceled:
            raise RuntimeError('IteratorClosed')

        partition_iter = _PartitionIterator(partition, table)
        self._partitions[partition] = partition_iter
        self._partition_available_event.set()
        partition_iter.wait_for_completion()
        if partition_iter.is_canceled:
            raise RuntimeError('IteratorClosed')

    def _clean_up(self):
        get_dataframe_reader().complete_iterator(self._iterator_id)
        self._done = True
        self._partition_available_event.set()


class RecordIterable:
    def __init__(self, dataflow):
        self._dataflow = dataflow
        self._cancellation_token = CancellationToken()

    def __iter__(self) -> RecordIterator:
        return RecordIterator(self._dataflow, self._cancellation_token)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        self._cancellation_token.cancel()


class _DataFrameReader:
    def __init__(self):
        self._outgoing_dataframes = {}
        self._incoming_dataframes = {}
        self._iterators = {}

    def register_outgoing_dataframe(self, dataframe: 'pandas.DataFrame', dataframe_id: str):
        self._outgoing_dataframes[dataframe_id] = dataframe

    def unregister_outgoing_dataframe(self, dataframe_id: str):
        self._outgoing_dataframes.pop(dataframe_id)

    def _get_partitions(self, dataframe_id: str) -> int:
        dataframe = self._outgoing_dataframes[dataframe_id]
        partition_count = math.ceil(len(dataframe) / PARTITION_SIZE)
        return partition_count

    def _get_data(self, dataframe_id: str, partition: int) -> bytes:
        from azureml.dataprep import native
        dataframe = self._outgoing_dataframes[dataframe_id]
        start = partition * PARTITION_SIZE
        end = min(len(dataframe), start + PARTITION_SIZE)
        dataframe = dataframe.iloc[start:end]

        (new_schema, new_values) = ensure_df_native_compat(dataframe)

        return native.preppy_from_ndarrays(new_values, new_schema)

    def register_incoming_dataframe(self, dataframe_id: str):
        self._incoming_dataframes[dataframe_id] = {}

    def complete_incoming_dataframe(self, dataframe_id: str) -> 'pandas.DataFrame':
        import pyarrow
        partitions_dfs = self._incoming_dataframes[dataframe_id]
        partitions_dfs = [partitions_dfs[key] for key in sorted(partitions_dfs.keys())]
        self._incoming_dataframes.pop(dataframe_id)

        import pandas as pd
        if len(partitions_dfs) == 0:
            return pd.DataFrame({})

        def get_column_names(partition: pyarrow.Table) -> List[str]:
            return partition.schema.names

        def verify_column_names():
            expected_names = get_column_names(partitions_dfs[0])
            expected_count = partitions_dfs[0].num_columns
            for partition in partitions_dfs:
                if partition.num_columns != expected_count:
                    raise _InconsistentSchemaError()
                for (a, b) in zip(expected_names, get_column_names(partition)):
                    if a != b:
                        raise _InconsistentSchemaError()

        def determine_column_type(index: int) -> pyarrow.DataType:
            for partition in partitions_dfs:
                column = partition.column(index)
                if column.type != pyarrow.bool_() or column.null_count != column.length():
                    return column.type
            return pyarrow.bool_()

        def apply_column_types(fields: List[pyarrow.Field]):
            for i in range(0, len(partitions_dfs)):
                partition = partitions_dfs[i]
                for j in range(0, len(fields)):
                    column_type = partition.schema.types[j]
                    if column_type != fields[j].type:
                        if column_type == pyarrow.bool_():
                            column = partition.column(j)
                            import numpy as np
                            def gen_n_of_x(n, x):
                                i = 0
                                while i < n:
                                    yield x
                                    i = i + 1
                            if isinstance(column, pyarrow.ChunkedArray):
                                typed_chunks = []
                                for chunk in column.chunks:
                                    typed_chunks.append(pyarrow.array(gen_n_of_x(chunk.null_count, None), fields[j].type, mask=np.full(chunk.null_count, True)))

                                partition = partition.remove_column(j)
                                partition = partition.add_column(j, fields[j], pyarrow.chunked_array(typed_chunks))
                            else:
                                new_col = pyarrow.column(
                                    fields[j],
                                    pyarrow.array(gen_n_of_x(column.null_count, None), fields[j].type, mask=np.full(column.null_count, True)))
                                partition = partition.remove_column(j)
                                partition = partition.add_column(j, new_col)
                            partitions_dfs[i] = partition
                        else:
                            raise _InconsistentSchemaError()

        verify_column_names()
        first_partition = partitions_dfs[0]
        column_fields = [pyarrow.field(first_partition.schema.names[i], determine_column_type(i)) for i in range(0, first_partition.num_columns)]
        apply_column_types(column_fields)

        from pyarrow import feather
        df = pyarrow.feather.concat_tables(partitions_dfs).to_pandas(use_threads=True)
        return df

    def register_iterator(self, iterator_id: str, iterator: RecordIterator):
        self._iterators[iterator_id] = iterator

    def complete_iterator(self, iterator_id: str):
        if iterator_id in self._iterators:
            self._iterators.pop(iterator_id)

    def _read_incoming_partition(self, dataframe_id: str, partition: int, partition_bytes: bytes):
        if not have_pyarrow():
            raise ImportError('PyArrow is not installed.')
        else:
            from pyarrow import feather

        if dataframe_id in self._incoming_dataframes:
            partitions_dfs = self._incoming_dataframes[dataframe_id]
            df = feather.read_table(io.BytesIO(partition_bytes))
            partitions_dfs[partition] = df
        elif dataframe_id in self._iterators:
            table = feather.read_table(io.BytesIO(partition_bytes))
            self._iterators[dataframe_id].process_partition(partition, table)
        else:
            raise ValueError('Invalid dataframe_id')

    def _cancel(self, dataframe_id: str):
        if dataframe_id in self._iterators:
            self._iterators[dataframe_id].cancel_iteration()

_dataframe_reader = None


def get_dataframe_reader():
    global _dataframe_reader
    if _dataframe_reader is None:
        _dataframe_reader = _DataFrameReader()

    return _dataframe_reader


def ensure_dataframe_reader_handlers(requests_channel):
    requests_channel.register_handler('get_dataframe_partitions', process_get_partitions)
    requests_channel.register_handler('get_dataframe_partition_data', process_get_data)
    requests_channel.register_handler('send_dataframe_partition', process_send_partition)


def process_get_partitions(request, writer, socket):
    dataframe_id = request.get('dataframe_id')
    try:
        partition_count = get_dataframe_reader()._get_partitions(dataframe_id)
        writer.write(json.dumps({'result': 'success', 'partitions': partition_count}))
    except Exception as e:
        writer.write(json.dumps({'result': 'error', 'error': str(e)}))


def process_get_data(request, writer, socket):
    dataframe_id = request.get('dataframe_id')
    partition = request.get('partition')
    try:
        partition_bytes = get_dataframe_reader()._get_data(dataframe_id, partition)
        byte_count = len(partition_bytes)
        byte_count_bytes = byte_count.to_bytes(4, 'little')
        socket.send(byte_count_bytes)
        socket.send(partition_bytes)
    except Exception as e:
        writer.write(json.dumps({'result': 'error', 'error': str(e)}))


def process_send_partition(request, writer, socket):
    dataframe_id = request.get('dataframe_id')
    partition = request.get('partition')
    try:
        writer.write(json.dumps({'result': 'success'}) + '\n')
        writer.flush()
        byte_count = int.from_bytes(socket.recv(8), 'little')
        with socket.makefile('rb') as input:
            partition_bytes = input.read(byte_count)
            get_dataframe_reader()._read_incoming_partition(dataframe_id, partition, partition_bytes)
            writer.write(json.dumps({'result': 'success'}) + '\n')
    except ImportError:
        get_dataframe_reader()._cancel(dataframe_id)
        writer.write(json.dumps({'result': 'error', 'error': 'PyArrowMissing'}))
    except Exception as e:
        get_dataframe_reader()._cancel(dataframe_id)
        writer.write(json.dumps({'result': 'error', 'error': str(e)}))
