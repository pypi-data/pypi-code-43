import os
import re
import shutil
import zipfile
import tempfile

from pathos.multiprocessing import ProcessPool
from bamboo_lib.connectors.drivers.gcs import GCSDriver
from bamboo_lib.helpers import grab_connector, random_char, expand_path
from bamboo_lib.models import PipelineStep, ResultWrapper
from bamboo_lib.logger import logger


class DownloadStep(PipelineStep):
    PARALLEL_WORKERS = 5

    @staticmethod
    def process_connector(raw_connector, connector_path):
        if isinstance(raw_connector, str):
            cpath = connector_path or __file__
            my_connector = grab_connector(cpath, raw_connector)
        else:
            my_connector = raw_connector
        return my_connector

    def __init__(self, connector=None, connector_path=None, callback=None, force=False):
        self.multi_source_mode = False
        if not connector:
            raise ValueError("Must specify a connector")
        if isinstance(connector, list):
            self.connector = [DownloadStep.process_connector(raw_conn, connector_path) for raw_conn in connector]
            self.multi_source_mode = True
        else:
            self.connector = DownloadStep.process_connector(connector, connector_path)
        self.callback = callback
        self.force = force

    def run_step(self, prev, params):
        logger.debug("DOWNLOAD STEP")
        # Download Cube (URL defined in conns.yaml file.)
        # This step will save the contents of the connector target
        # to a file and then pass a file path to the next step
        if self.multi_source_mode:
            ## TODO: in parallel mode for now, we assume all connectors have same path/force/callback settings
            ## but this can be further customized in the future to allow for variation.
            with ProcessPool(nodes=DownloadStep.PARALLEL_WORKERS) as pool:
                def wrapper_fn(my_connector):
                    return my_connector.download(params=params, callback=self.callback, force=self.force)
                return pool.map(wrapper_fn, self.connector)
        else:
            return self.connector.download(params=params, callback=self.callback, force=self.force)


class WildcardDownloadStep(PipelineStep):
    PARALLEL_WORKERS = 5

    @staticmethod
    def process_connector(raw_connector, connector_path):
        if isinstance(raw_connector, str):
            cpath = connector_path or __file__
            my_connector = grab_connector(cpath, raw_connector)
        else:
            my_connector = raw_connector
        return my_connector

    def __init__(self, connector=None, connector_path=None, force=False):
        self.multi_source_mode = False
        if not connector:
            raise ValueError("Must specify a connector")
        if isinstance(connector, list):
            self.connector = [WildcardDownloadStep.process_connector(raw_conn, connector_path) for raw_conn in connector]
            self.multi_source_mode = True
        else:
            self.connector = WildcardDownloadStep.process_connector(connector, connector_path)
        self.force = force

    def run_step(self, prev, params):
        logger.debug("DOWNLOAD STEP")
        # Download Cube (URL defined in conns.yaml file.)
        # This step will save the contents of the connector target
        # to a file and then pass a file path to the next step
        get_targets = self.connector.get_targets(params=params)
        my_gcs_params = self.connector.serialize()
        import os
        os.environ['GOOGLE_CLOUD_DISABLE_GRPC'] = 'true'
        force = True if self.force else False
        with ProcessPool(nodes=WildcardDownloadStep.PARALLEL_WORKERS) as pool:
            def wrapper_fn(my_target):
                my_uri, my_params = my_target
                gcs_driver = GCSDriver(**my_gcs_params)
                gcs_driver._datastore_api_internal = None
                params_local = {k: v for k,v in params.items()}
                params_local.update(my_params)
                return (gcs_driver.download_single(my_uri, params=params_local, force=force), my_params)
            return pool.map(wrapper_fn, get_targets)


class LoadStep(PipelineStep):
    OPTIONS = ["if_exists", "schema", "index", "index_label", "chunksize", "dtype", "pk", "table_schema_only",
               "data_only", "connector_path", "nullable_list", "engine", "engine_params"]

    def __init__(self, table_name, connector, **kwargs):
        self.table_name = table_name
        if isinstance(connector, str):
            cpath = kwargs.get("connector_path", None) or __file__
            self.connector = grab_connector(cpath, connector)
            if "connector_path" in kwargs:
                del kwargs["connector_path"]
        else:
            self.connector = connector
        for key, val in kwargs.items():
            if key in LoadStep.OPTIONS:
                setattr(self, key, val)
            else:
                raise ValueError("Invalid parameter", key, val)

    def run_step(self, prev, params):
        logger.info("Running LoadStep step...")
        df = prev
        kwargs = {key: getattr(self, key) for key in self.OPTIONS if hasattr(self, key)}
        self.connector.write_df(self.table_name, df, **kwargs)
        return prev


class LoadStepDynamic(PipelineStep):
    OPTIONS = ["if_exists", "schema", "index", "index_label", "chunksize", "dtype", "pk"]

    def __init__(self, df_key, table_name_key, connector, **kwargs):
        self.df_key = df_key
        self.table_name_key = table_name_key
        self.connector = connector
        for key, val in kwargs.items():
            if key in LoadStep.OPTIONS:
                setattr(self, key, val)
            else:
                raise ValueError("Invalid parameter", key, val)

    def run_step(self, prev, params):
        logger.info("Running LoadStep step...")
        df = prev.get(self.df_key)
        kwargs = {key: getattr(self, key) for key in self.OPTIONS if hasattr(self, key)}
        self.connector.write_df(prev.get(self.table_name_key), df, **kwargs)
        return prev


class UnzipStep(PipelineStep):
    """
    The UnzipStep class allows users to extract content contained inside a zip file for processing
    UnzipStep effectively performs a temporary unzip operation and returns a handle to a file object
    for each item in the zip folder (or, each item in the zip folder that matches the specified pattern).

    At the moment, only the `.zip` file format is supported.

    Note that UnzipStep's run_step method will return a generator for each step, and therefore is suitable to be
    used in conjunction with :class:`bamboo_lib.models.LoopHelper` (see example usage there) or with custom :meth:`bamboo_lib.models.AdvancedPipelineExecutor.foreach` loops.

    :param compression: A string representing the type of compression. Currently, only `".zip"` is supported.
    :param pattern: A string representing a regular expression pattern. For example `"*.csv"`.
    :return: UnzipStep object
    """
    def __init__(self, compression='zip', pattern=None):
        self.compression = compression
        supported_compression = ['zip']
        self.pattern = pattern
        if self.compression not in supported_compression:
            raise Exception("extension not supported!")

    def run_step(self, filepath, params):
        if self.compression == 'zip':
            zfile = zipfile.ZipFile(filepath)
            for finfo in zfile.infolist():
                if not self.pattern or re.search(self.pattern, finfo.filename):
                    yield zfile.open(finfo)

        # return compressor(full_path)


class UnzipToFolderStep(PipelineStep):
    """
    This PipelineStep class allows users to easily extract a data set to a folder.
    By default, UnzipToFolderStep will utilize a random folder directory, but users
    may pass the target_folder_path parameter to the constructor in order to explicit
    set the path where the files should be unzipped.

    Currently, this step does not support selective unzipping and will unzip all files in the zip archive.
    """
    def __init__(self, compression='zip', target_folder_path=None, initial_path=None, **kwargs):
        super().__init__(**kwargs)
        self.compression = compression
        supported_compression = ['zip']
        self.target_folder_path = target_folder_path
        if self.compression not in supported_compression:
            raise Exception("extension not supported!")
        self.initial_path = None

    def run_step(self, filepath, params):
        tmp_folder_path = tempfile.gettempdir()
        my_data_folder = random_char(16)
        if not self.target_folder_path:
            target_path = os.path.join(tmp_folder_path, my_data_folder)
        else:
            target_path = self.target_folder_path
        if self.compression == 'zip':
            zfile = zipfile.ZipFile(self.initial_path or filepath)
            zfile.extractall(target_path)
            return target_path


class CleanupFileStep(PipelineStep):
    """
    This CleanupFileStep provides a cross-platform way to delete files and folders from the local machine.

    Users may specify either a target_path which could be a String literal such as "/tmp/myfolder" or even
    "/tmp/myfolder/$MYVAR" or target_result_key which will read out a path from a previously saved result from another step
    with the specified key.
    """
    def __init__(self, use_prev_result=None, target_path=None, target_result_key=None):
        if (not target_path and not target_result_key and not use_prev_result):
            raise ValueError("Must specify either prev_result, target_path, or target_result_key")
        self.target_path = target_path
        self.target_result_key = target_result_key
        self.use_prev_result = use_prev_result

    def run_step(self, prev, params):
        pipeline_res_ref = self.get_pipeline_results_ref()
        # to_del = self.target_path if self.target_path else pipeline_res_ref[self.target_result_key]
        if self.use_prev_result:
            to_del = prev
        elif self.target_path:
            to_del = self.target_path
        elif self.target_result_key:
            to_del = pipeline_res_ref[self.target_result_key]
        else:
            raise ValueError("Bad settings for CleanupFileStep")

        to_del = expand_path(to_del)
        shutil.rmtree(to_del)
        return prev  # -- pass through previous result


class WriteDFToDiskStep(PipelineStep):
    def __init__(self, target_path, compression=None):
        self.target_path = target_path
        self.compression = compression

    def run_step(self, df, params):
        df.to_csv(self.target_path, index=False, compression=self.compression)
        return self.target_path


class SCPTransferStep(PipelineStep):
    def __init__(self, target_path, connector, **kwargs):
        if not target_path or not connector:
            raise Exception("You must specify a target path and a connector")
        super(SCPTransferStep, self).__init__(**kwargs)
        self.target_path = target_path
        self.connector = connector

    def run_step(self, file_obj, params):
        logger.debug("Transfering schema file: {} ...".format(self.target_path))
        use_fo = not isinstance(file_obj, str)
        self.connector.send_file(file_obj, self.target_path, use_fo=use_fo)
        logger.debug("Transfer complete!")
        return True


class SSHCommandStep(PipelineStep):
    def __init__(self, cmd, connector, **kwargs):
        if not cmd or not connector:
            raise Exception("You must specify a target path and a connector")
        super(SSHCommandStep, self).__init__(**kwargs)
        self.cmd = cmd
        self.connector = connector

    def run_step(self, input, params):
        logger.debug("Running command on remote host: {} ...".format(self.cmd))
        # self.connector.send_file(file_obj, self.target_path, use_fo=True)
        output = self.connector.run_command(self.cmd)
        logger.debug("Command complete! Result was:\n\n {}\n\n".format(output))
        return ResultWrapper(previous_result=input, current_result=output)


class LockStep(PipelineStep):
    def __init__(self, lock_name, redis_connector, next_step):
        import sherlock  # -- only use if needed
        sherlock.configure(timeout=45, backend=sherlock.backends.REDIS, client=redis_connector.get_client())
        self.lock_name = lock_name
        self.lock = sherlock.Lock(lock_name)
        self.next_step = next_step

    def run_step(self, prev, params):
        logger.debug("Waiting for lock {} ...".format(self.lock_name))
        self.lock.acquire()
        logger.debug("Acquired lock {} ...".format(self.lock_name))
        logger.debug("Running step...")
        result = self.next_step.run_step(prev, params)
        self.lock.release()
        logger.debug("Lock released!")
        return result


class SSHTunnelStartStep(PipelineStep):
    def __init__(self, sshtunnel_connector):
        self.sshtunnel_connector = sshtunnel_connector

    def run_step(self, prev, params):
        self.sshtunnel_connector.start()
        return prev


class SSHTunnelCloseStep(PipelineStep):
    def __init__(self, sshtunnel_connector):
        self.sshtunnel_connector = sshtunnel_connector

    def run_step(self, prev, params):
        self.sshtunnel_connector.close()
        return prev


class IngestMonetStep(PipelineStep):
    def __init__(self, table_name, schema, db_name, conns_path, compression=None):
        self.table_name = table_name
        self.schema = schema
        self.db_name = db_name
        self.conns_path = conns_path
        self.compression = compression

    def run_step(self, prev, params):
        # connectors config
        server_str = params.get("server-connector")
        sftp_connector = grab_connector(self.conns_path, server_str)

        monet_connector = grab_connector(self.conns_path, "monet-remote")
        redis_connector = grab_connector(self.conns_path, "redis-remote")

        lock_name = params.get("lock_name", "monet-lock")

        # prep csv file for write to disk and transfer to server
        # (including compression)
        random_filename = random_char(32)
        target_path = "/tmp/{}-{}.csv".format(self.schema, random_filename)
        if self.compression == "gzip":
            target_path = target_path + ".gz"
        elif self.compression == "bz2":
            target_path = target_path + ".bz2"

        write_to_disk_step = WriteDFToDiskStep(target_path=target_path, compression=self.compression)
        transfer_step = SCPTransferStep(target_path, sftp_connector)

        # Create table
        # Must use lock because Monetdb does not support table creation concurrent
        # with any other transaction (including COPY)
        # put the table gen into a load step which is wrapped by the lock step
        # for ssh tunnel, just have to start one manually, and then latch onto it with
        # the ssh_tunnel step by specifying the port.
        # e.g. ssh -L 6379:localhost:6379 deploy@canon -N

        create_table_step = LoadStep(self.table_name, monet_connector, table_schema_only=True, schema=self.schema)
        create_table_with_lock_step = LockStep(lock_name, redis_connector, create_table_step)

        # Ingest
        ingest_cmd = '''mclient -d {} -h localhost -s "COPY OFFSET 2 INTO {}.{} FROM '{}' USING DELIMITERS ',', '\n', '\\\"' NULL AS '' "'''.format(self.db_name, self.schema, self.table_name, target_path)
        remote_cmd_step = SSHCommandStep(ingest_cmd, sftp_connector)

        # Run steps
        res_1 = create_table_with_lock_step.run_step(prev, params)
        res_2 = write_to_disk_step.run_step(res_1, params)
        res_3 = transfer_step.run_step(res_2, params)
        res_4 = remote_cmd_step.run_step(res_3, params)

        return res_4
