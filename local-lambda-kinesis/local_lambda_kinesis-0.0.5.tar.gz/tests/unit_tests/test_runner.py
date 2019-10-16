import pytest

from datetime import datetime
from unittest.mock import Mock, patch, call

from lambda_kinesis.runner import get_records, run_handler_on_stream_records


def test_get_records_parses_response():
    kinesis_client = Mock()

    arrival_time = datetime(2015, 1, 1)
    kinesis_client.get_records.return_value = {
        "Records": [
            {"ApproximateArrivalTimestamp": arrival_time, "Data": b"data", "PartitionKey": "xxx"}
        ],
        "NextShardIterator": "456",
    }

    records, shard_iterator = get_records(
        kinesis_client, stream_name="stream", shard_iterator="123"
    )

    assert records == (
        {
            "kinesis": {
                "data": "ZGF0YQ==",
                "approximateArrivalTimestamp": arrival_time,
                "partitionKey": "xxx",
            },
            "eventSource": "aws:kinesis",
            "eventName": "aws:kinesis:record",
        },
    )

    assert shard_iterator == "456"


@patch("lambda_kinesis.runner.get_records")
def test_run_handler_polls_stream(get_records):
    kinesis_client = Mock()
    handler = Mock()

    kinesis_client.list_shards.return_value = {"Shards": [{"ShardId": "shard"}]}

    kinesis_client.get_shard_iterator.return_value = {"ShardIterator": "iterator"}

    class PleaseStop(Exception):
        pass

    iterator_type = "TRIM_HORIZON"

    records = [str(i) for i in range(30)]
    record_batches = [records[i : i + 10] for i in range(0, 30, 10)]  # NOQA
    shard_iterators = [str(i) for i in range(3)]

    get_records.side_effect = list(zip(record_batches, shard_iterators)) + [PleaseStop]
    with pytest.raises(PleaseStop):
        run_handler_on_stream_records(
            stream_name="stream",
            kinesis_client=kinesis_client,
            shard_iterator_type=iterator_type,
            handler=handler,
            wait_seconds=0,
        )

    kinesis_client.get_shard_iterator.assert_called_once_with(
        StreamName="stream", ShardId="shard", ShardIteratorType=iterator_type
    )

    assert get_records.call_args_list == [
        call(kinesis_client, "stream", "iterator"),
        call(kinesis_client, "stream", "0"),
        call(kinesis_client, "stream", "1"),
        call(kinesis_client, "stream", "2"),
    ]

    assert handler.call_args_list == [
        call({"Records": record_batch}, None) for record_batch in record_batches
    ]
