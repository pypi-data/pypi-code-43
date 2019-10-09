import os
from typing import Any, Dict, List, Optional, Tuple

import msgpack
import redis


class FeatureStore:
    """Feature Store on Bedrock platform

    Feature store backed by Redis.
    FIXME: [BDRK-342] implement this to be run as a service instead.
    """

    def __init__(self, redis):
        self.redis = redis

    def create_feature(self, feature_name: str, schema: Optional[List[str]] = None):
        if schema:
            self.redis.set(f"{feature_name}:schema", msgpack.packb(schema))
        # TODO: [BDRK-320] register feature when there's no schema

    def write_pandas_df(
        self, df: None, feature_name: str, key_col: str = "Index", batch_size: int = 10000
    ):
        """Store a data frame to feature store

        Data will be stored in the format
        feature_name:key

        :param df: pandas dataframe to store
        :type df: DataFrame
        :param feature_name: name to store the key under
        :type feature_name: str
        :param batch_size: size of each storing batch, defaults to 10000
        :param batch_size: int, optional
        """
        try:
            df_dict = df.to_dict("split")  # type:ignore
        except Exception as e:
            print("Error while converting dataframe", str(e))
            return

        schema = df_dict["columns"]
        pipe = self.redis.pipeline()
        pipe.set(f"{feature_name}:schema", msgpack.packb(schema))
        key_idx = df_dict["columns"].index(key_col)

        for row_idx in df_dict["index"]:
            row = df_dict["data"][row_idx]
            key = row[key_idx]
            pipe.set(f"{feature_name}:{key}", msgpack.packb(row, use_bin_type=True))
            # TODO: [BDRK-321] implement rerun on failure
            if ((row_idx + 1) % batch_size) == 0:
                pipe.execute()
        pipe.execute()

    def _get_batch(self, kvs: List[Tuple[str, Any]], batch_size: int) -> List[Dict[str, Any]]:
        batches = []
        current_batch = {}
        for k, v in kvs:
            current_batch[k] = v
            if len(current_batch) == batch_size:
                batches.append(current_batch)
                current_batch = {}
        if len(current_batch):
            batches.append(current_batch)
        return batches

    def write(self, feature_name: str, kvs: List[Tuple[str, Any]], batch_size: int = 10000):
        """Store a list of keys and values in feature store

        :param feature_name: name to store key under
        :type feature_name: str
        :param kvs: list of key-value pairs to store
        :type kvs: List[Tuple[str, str]]
        """
        pipe = self.redis.pipeline()
        batches = self._get_batch(kvs, batch_size)
        for batch in batches:
            for k, v in batch.items():
                pipe.set(f"{feature_name}:{k}", msgpack.packb(v, use_bin_type=True))
                # TODO: [BDRK-321] implement re-run on failure
            pipe.execute()

    def read(self, feature_name: str, keys: List[str]) -> Dict[str, Optional[Dict[str, str]]]:
        pipe = self.redis.pipeline()
        pipe.get(f"{feature_name}:schema")
        for key in keys:
            pipe.get(f"{feature_name}:{key}")
        schema, *values = pipe.execute()
        if schema is not None:
            schema = msgpack.unpackb(schema, raw=False)
        ret: Dict[str, Optional[Dict[str, str]]] = {}
        for idx, value in enumerate(values):
            if value:
                unpacked = msgpack.unpackb(value, use_list=False, raw=False)
                if schema is None:
                    ret[keys[idx]] = unpacked
                else:
                    ret[keys[idx]] = dict(zip(schema, unpacked))
            else:
                ret[keys[idx]] = None
        return ret


def get_feature_store(
    host: Optional[str] = None,
    port: Optional[int] = None,
    mock_feature_store: Optional[bool] = None,
):
    mock_feature_store = (
        mock_feature_store
        if mock_feature_store is not None
        else bool(int(os.getenv("FEATURE_STORE_MOCK", 0)))
    )
    if mock_feature_store:
        import fakeredis

        return FeatureStore(fakeredis.FakeStrictRedis())
    host = host if host else os.getenv("FEATURE_STORE_HOST", "localhost")
    port = port if port else int(os.getenv("FEATURE_STORE_PORT", 6379))
    return FeatureStore(redis.Redis(host=host, port=port))
