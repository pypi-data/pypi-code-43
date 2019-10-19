"""Local Dense Array TileDB Backend Implementation, Identifier: ``TILEDB_20``

Backend Identifiers
===================

*  Backend: ``2``
*  Version: ``0``
*  Format Code: ``20``
*  Canonical Name: ``TILEDB_20``


Storage Method
==============

*  Data is written to specific subarray indexes inside a tiledb array on disk.

*  In TileDB the atomic units of storage are individual hyper-rectangular
   regions defined by each dimension's ``'tile extent'`` and are known as
   ``'data tiles'``. As such, no space is required to store or index/slice
   through empty or uninitialized elements, since setting elements in tiles is
   the only trigger to write data to disk.

   Intuitively, ``data tiles`` also are defined in the same way when reading
   data from disk. When reading some subarray slice, only the data tiles whose
   space tiles intersect with the subarray selection need to be read from disk.
   These characteristics, combined with our knowledge of access patterns, allow us
   to set tile extents optimal for individual sample read/write speeds.

*  An important optimization is made via a method unique to this module:

   .. automethod:: TILEDB_20_FileHandles._write_chunk_data


Record Format
=============

Fields Recorded for Each Array
------------------------------

*  Format Code
*  File UID
*  Alder32 Checksum
*  Collection Index (0:COLLECTION_SIZE subarray selection)
*  Subarray Shape

Separators used
---------------

*  ``SEP_KEY: ":"``
*  ``SEP_HSH: "$"``
*  ``SEP_LST: " "``
*  ``SEP_SLC: "*"``

Examples
--------

1)  Adding the first piece of data to a file:

    *  Array shape (Subarray Shape): (784,)
    *  File UID: "wQQUbh"
    *  Alder32 Checksum: 1279214320
    *  Collection Index: 2

    ``Record Data => '20:wQQUbh$1279214320$2*784'``

1)  Adding to a piece of data to a the middle of a file:

    *  Array shape (Subarray Shape): (20, 2, 3)
    *  File UID: "Mk23nl"
    *  Alder32 Checksum: 2546668575
    *  Collection Index: 199

    ``Record Data => "10:Mk23nl$2546668575$199*20 2 3"``


Technical Notes
===============

*  In many cases, the dimensions assigned to the array schema will be larger
   than the maximum size an array may occupy. **In cases where the array domain
   cannot be decomposed into integral space tiles, the domain of a dimension is
   inflated to the minimum size required for an integral number of tiles to fit
   along the dimension's axis**. The amount of padding required is determined at
   runtime based on the raw sample schema shape/size and the configured tile
   extent. Note: These elements SHALL NEVER be set with any type of data
   (either sample data or for purposes internal to this module).

*  On each write, an ``alder32`` checksum is calculated. This is not for use as
   the primary hash algorithm, but rather stored in the local record format
   itself to serve as a quick way to verify no disk corruption occurred. This is
   required since tiledb has no built in data integrity validation methods when
   reading from disk.
"""

import asyncio
import os
import re
from math import ceil
from os.path import join as pjoin
from typing import List
from typing import MutableMapping
from typing import NamedTuple
from typing import Tuple
from typing import Optional

import numpy as np
import tiledb
import xxhash

from .. import constants as c
from ..utils import random_string
from ..utils import symlink_rel

# ----------------------------- Configuration ---------------------------------

# number of subarray contents of a single numpy memmap file
# COLLECTION_SIZE = 1_600
# MAX_PACK_SIZE = 200
# MAX_ACCUMULATOR_NBYTES = 1_000_000_000  # ~ 2 GB
MAX_ACCUMULATOR_NBYTES = 5_000_000_000  # ~ 1 GB

CONFIG_PARAMS = {
    'sm.num_reader_threads': '4',
    'sm.num_writer_threads': '4',
    'sm.consolidation.buffer_size': '1000000000',  # 1 GB
}

TDB_CONFIG = tiledb.Config()
TDB_CONFIG.update(CONFIG_PARAMS)

# -------------------------------- Parser Implementation ----------------------

_FmtCode = '20'
# match and remove the following characters: '['   ']'   '('   ')'   ','
_ShapeFmtRE = re.compile('[,\(\)\[\]]')
# split up a formatted parsed string into unique fields
_SplitDecoderRE = re.compile(fr'[\{c.SEP_KEY}\{c.SEP_HSH}\{c.SEP_SLC}]')


TILEDB_20_DataHashSpec = NamedTuple('TILEDB_20_DataHashSpec',
                                    [('backend', str), ('uri', str),
                                     ('checksum', str), ('collection_idx', int),
                                     ('attr_idx', str), ('shape', Tuple[int])])


def tiledb_20_encode(uri: str, checksum: int, collection_idx: int, attr_idx: str, shape: tuple) -> bytes:
    """converts the tiledb data spec to an appropriate db value

    Parameters
    ----------
    uri : str
        file name where this data piece can be found in.
    checksum : int
        adler32 checksum of the data as computed on that local machine.
    collection_idx : int
        collection first axis index in which this data piece resides.
    shape : tuple
        shape of the data sample written to the collection idx. ie: what
        sub-slices of the array should be read to retrieve the sample as
        recorded.

    Returns
    -------
    bytes
        hash data db value recording all input specifications
    """
    out_str = f'{_FmtCode}{c.SEP_KEY}'\
              f'{uri}{c.SEP_HSH}{checksum}'\
              f'{c.SEP_HSH}'\
              f'{collection_idx}'\
              f'{c.SEP_HSH}'\
              f'{attr_idx}'\
              f'{c.SEP_SLC}'\
              f'{_ShapeFmtRE.sub("", str(shape))}'
    return out_str.encode()


def tiledb_20_decode(db_val: bytes) -> TILEDB_20_DataHashSpec:
    """converts a numpy data hash db val into a numpy data python spec

    Parameters
    ----------
    db_val : bytes
        data hash db val

    Returns
    -------
    DataHashSpec
        numpy data hash specification containing `backend`, `schema`, and
        `uid`, `collection_idx` and `shape` fields.
    """
    db_str = db_val.decode()
    _, uri, checksum, collection_idx, attr_idx, shape_vs = _SplitDecoderRE.split(db_str)
    # if the data is of empty shape -> shape_vs = '' str.split() default value
    # of none means split according to any whitespace, and discard empty strings
    # from the result. So long as c.SEP_LST = ' ' this will work
    shape = tuple(int(x) for x in shape_vs.split())
    raw_val = TILEDB_20_DataHashSpec(backend=_FmtCode,
                                     uri=uri,
                                     checksum=checksum,
                                     collection_idx=int(collection_idx),
                                     attr_idx=str(attr_idx),
                                     shape=shape)
    return raw_val


# ------------------------- Accessor Object -----------------------------------


class TILEDB_20_FileHandles(object):

    def __init__(self, repo_path: os.PathLike, schema_shape: tuple, schema_dtype: np.dtype):
        """Manage TileDB Dense Arrays.

        Local disk only. Reads are highly scalable with number of cores.
        """
        self.repo_path = repo_path
        self.schema_shape = schema_shape
        self.schema_dtype = schema_dtype
        self._dflt_backend_opts: Optional[dict] = None

        arr = np.zeros(shape=schema_shape, dtype=schema_dtype)
        max_collection_size = ceil(MAX_ACCUMULATOR_NBYTES / arr.nbytes)
        max_collection_size -= max_collection_size % 8
        self.COLLECTION_SIZE = int(max_collection_size)
        self.MAX_PACK_SIZE = int(max_collection_size / 8)
        self.MAX_ACCUMULATOR_NBYTES = int(self.COLLECTION_SIZE * arr.nbytes)

        self.rFp: MutableMapping[str, tiledb.Array] = {}
        self.wFp: tiledb.DenseArray = None
        self.ctx = tiledb.Ctx(config=TDB_CONFIG)

        self.Accumulator: List[Tuple[int, np.array]] = []
        self.AccumulatorNbytes: int = 0

        self.mode: str = None
        self.w_uri: str = None
        self.hIdx: int = None
        self.aIdx: int = None

        self.slcExpr = np.s_
        self.slcExpr.maketuple = False

        self.STAGEDIR = pjoin(self.repo_path, c.DIR_DATA_STAGE, _FmtCode)
        self.REMOTEDIR = pjoin(self.repo_path, c.DIR_DATA_REMOTE, _FmtCode)
        self.DATADIR = pjoin(self.repo_path, c.DIR_DATA, _FmtCode)
        self.STOREDIR = pjoin(self.repo_path, c.DIR_DATA_STORE, _FmtCode)
        if not os.path.isdir(self.DATADIR):
            os.makedirs(self.DATADIR)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        if self.wFp is not None:
            if len(self.Accumulator) > 0:
                self._write_chunk_data()
            if self.wFp is not None:
                self.wFp.close()
                self.wFp = None

    @property
    def backend_opts(self):
        return self._dflt_backend_opts

    @backend_opts.setter
    def backend_opts(self, val):
        if self.mode == 'a':
            self._dflt_backend_opts = val
            return
        else:
            raise AttributeError(f"can't set property in read only mode")

    def open(self, mode: str, *, remote_operation: bool = False):
        """Parse through in-process/store directory to identify file ``uris`` on disk.

        Rather than opening the arrays for reading when a ``uri`` is found (a
        waste of open file handles and un-necessary IO), we just record it's
        absolute path as a value indexed in a dict by the URI key. As written
        arrays are immutable, this function will only ever populate the ``'r'
        URI`` dict (``rFp``).

        Parameters
        ----------
        mode : str
            one of `a` for `write-enabled` mode or `r` for read-only
        remote_operation : bool, optional, kwarg only
            True if remote operations call this method. Changes the symlink
            directories used while writing., by default False
        """
        self.mode = mode
        if self.mode == 'a':
            refDir = self.REMOTEDIR if remote_operation else self.STAGEDIR
            if not os.path.isdir(refDir):
                os.makedirs(refDir)

            dirConts = os.listdir(refDir)
            ref_uris = [x for x in dirConts if not x.startswith('.')]
            for uri in ref_uris:
                file_pth = pjoin(refDir, uri)
                self.rFp[uri] = file_pth

        if not remote_operation:
            if not os.path.isdir(self.STOREDIR):
                return
            dirConts = os.listdir(self.STOREDIR)
            store_uris = [x for x in dirConts if not x.startswith('.')]
            for uri in store_uris:
                file_pth = pjoin(self.STOREDIR, uri)
                self.rFp[uri] = file_pth

    def close(self, *args, **kwargs):
        """Close any open file handles, flushing any unwritten data to disk.
        """
        if self.mode == 'a':
            if len(self.Accumulator) > 0:
                self._write_chunk_data()
            self.w_uri = None
            self.hIdx = None
            self.aIdx = None
            if self.wFp is not None:
                self.wFp.close()
                self.wFp = None

        for v in self.rFp.values():
            if isinstance(v, tiledb.Array):
                v.close()

    @staticmethod
    def delete_in_process_data(repo_path, *, remote_operation=False):
        """Removes some set of files entirely from the stage/remote directory.

        DANGER ZONE. This should essentially only be used to perform hard resets
        of the repository state.

        Parameters
        ----------
        repo_path : str
            path to the repository on disk
        remote_operation : optional, kwarg only, bool
            If true, modify contents of the remote_dir, if false (default) modify
            contents of the staging directory.
        """
        data_dir = pjoin(repo_path, c.DIR_DATA, _FmtCode)
        PDIR = c.DIR_DATA_STAGE if not remote_operation else c.DIR_DATA_REMOTE
        refDir = pjoin(repo_path, PDIR, _FmtCode)
        if not os.path.isdir(refDir):
            return

        ref_uris = [x for x in os.listdir(refDir) if not x.startswith('.')]
        for uri in ref_uris:
            remove_link_pth = pjoin(refDir, uri)
            remove_data_pth = pjoin(data_dir, uri)
            os.unlink(remove_link_pth)
            tiledb.remove(remove_data_pth)
        os.rmdir(refDir)

    @staticmethod
    def _dataset_opts(complib: str, complevel: int, shuffle: str) -> Optional[tiledb.FilterList]:

        filterlist = []
        ctx = tiledb.Ctx(config=TDB_CONFIG)
        _shuffle_filters = {
            None: None,  # as in, does not appear in filter list
            'none': None,
            'BitShuffleFilter': tiledb.BitShuffleFilter(ctx=ctx),
            'ByteShuffleFilter': tiledb.ByteShuffleFilter(ctx=ctx),
            'BitWidthReductionFilter': tiledb.BitWidthReductionFilter(ctx=ctx),
            'PositiveDeltaFilter': tiledb.PositiveDeltaFilter(ctx=ctx)}
        _compression_filters = {
            None: None,
            'none': None,
            'GzipFilter': tiledb.GzipFilter(level=complevel, ctx=ctx),
            'ZstdFilter': tiledb.ZstdFilter(level=complevel, ctx=ctx),
            'LZ4Filter': tiledb.LZ4Filter(level=complevel, ctx=ctx),
            'RleFilter': tiledb.RleFilter(ctx=ctx),
            'Bzip2Filter': tiledb.Bzip2Filter(level=complevel, ctx=ctx),
            'DoubleDeltaFilter': tiledb.DoubleDeltaFilter(ctx=ctx)}
        shuffler = _shuffle_filters[shuffle]
        compressor = _compression_filters[complib]

        if shuffler is not None:
            filterlist.append(shuffler)
        if compressor is not None:
            filterlist.append(compressor)

        if len(filterlist) > 0:
            tileFilters = tiledb.FilterList(filters=filterlist)
        else:
            tileFilters = None
        return tileFilters

    def _create_schema(self, *, remote_operation: bool = False):
        """use the schema and dtype to create an empty TileDB array for writing.

        Parameters
        ----------
        remote_operation : optional, kwarg only, bool
            if this schema is being created from a remote fetch operation, then
            do not place the file symlink in the staging directory. Instead
            symlink it to a special remote staging directory. (default is
            False, which places the symlink in the stage data directory.)

        Notes
        -----

        From TileDB Docs:

        * When specifying an array domain that cannot be decomposed into
          integral tiles (i.e., some dimension domain is not divisible by the
          tile extent along that dimension), always account for the domain
          expansion. Specifically, make sure to define the dimension domain
          such that expanding by one tile extent does not lead to a domain
          bound overflow (for the selected domain data type).
        """
        ctx = tiledb.Ctx(config=TDB_CONFIG)

        arraySize = int(np.prod(self.schema_shape))
        tileSize = min([1_000_000, arraySize])
        if arraySize % tileSize != 0:
            domainPading = tileSize - (arraySize % tileSize)
            arraySize += domainPading

        collectionDim = tiledb.Dim(name='coldim',
                                   domain=(0, self.MAX_PACK_SIZE - 1),
                                   tile=1,
                                   dtype=np.uint32,
                                   ctx=ctx)
        dataDim = tiledb.Dim(name='datadim',
                             domain=(0, arraySize - 1),
                             tile=arraySize,
                             dtype=np.uint32,
                             ctx=ctx)
        tileDom = tiledb.Domain(collectionDim, dataDim, ctx=ctx)

        tileFilters = self._dataset_opts(**self._dflt_backend_opts)

        tileAttrs = []
        for aidx in range(int(self.COLLECTION_SIZE / self.MAX_PACK_SIZE)):
            tileAttrs.append(tiledb.Attr(name=str(aidx),
                                         dtype=self.schema_dtype,
                                         filters=tileFilters,
                                         ctx=ctx))

        TdbSchema = tiledb.ArraySchema(domain=tileDom,
                                       sparse=False,
                                       attrs=tileAttrs,
                                       ctx=ctx)

        if self.wFp is not None:
            file_path = pjoin(self.DATADIR, f'{self.w_uri}')
            self.rFp[self.w_uri] = file_path

        uri = random_string()
        file_path = pjoin(self.DATADIR, f'{uri}')
        tiledb.DenseArray.create(file_path, TdbSchema, ctx=ctx)
        self.wFp = tiledb.DenseArray(file_path, mode='w', ctx=ctx)
        self.w_uri = uri
        self.hIdx = 0
        self.aIdx = 0

        if remote_operation:
            symlink_file_path = pjoin(self.REMOTEDIR, uri)
        else:
            symlink_file_path = pjoin(self.STAGEDIR, uri)
        symlink_rel(file_path, symlink_file_path, is_dir=True)

    def read_data(self, hashVal: TILEDB_20_DataHashSpec) -> np.ndarray:
        """Read data from disk written in the numpy_00 fmtBackend

        Parameters
        ----------
        hashVal : TILEDB_20_DataHashSpec
            record specification stored in the db

        Returns
        -------
        np.ndarray
            tensor data stored at the provided hashVal specification.

        Raises
        ------
        RuntimeError
            If the recorded checksum does not match the received checksum.

        """
        if self.mode == 'a':
            if len(self.Accumulator) > 0:
                self._write_chunk_data()

        arraySize = int(np.prod(hashVal.shape))
        try:
            if isinstance(self.rFp[hashVal.uri], str):

                self.rFp[hashVal.uri] = tiledb.DenseArray(self.rFp[hashVal.uri], mode='r', ctx=self.ctx)
                for i in range(8):
                    self.rFp[f'{hashVal.uri}/{str(i)}'] = self.rFp[hashVal.uri].query(attrs=(str(i),))
            res = self.rFp[f'{hashVal.uri}/{hashVal.attr_idx}'][hashVal.collection_idx, 0:arraySize][hashVal.attr_idx]
        except KeyError:
            process_dir = self.STAGEDIR if self.mode == 'a' else self.STOREDIR
            file_pth = pjoin(process_dir, f'{hashVal.uri}')
            if os.path.islink(file_pth):
                ctx = tiledb.Ctx(config=TDB_CONFIG)
                self.rFp[hashVal.uri] = tiledb.DenseArray(file_pth, mode='r', ctx=self.ctx)
                for i in range(8):
                    self.rFp[f'{hashVal.uri}/{str(i)}'] = self.rFp[hashVal.uri].query(attrs=(str(i),))
                res = self.rFp[f'{hashVal.uri}/{hashVal.attr_idx}'][hashVal.collection_idx, 0:arraySize][hashVal.attr_idx]
            else:
                raise

        out = res.reshape(hashVal.shape)
        cksum = xxhash.xxh64_intdigest(res)
        if cksum != int(hashVal.checksum):
            msg = f'DATA CORRUPTION ERROR: Checksum {cksum} != recorded for {hashVal}'
            raise RuntimeError(msg)
        return out

    def _write_chunk_data(self):
        """Special management of how data is written to disk.

        In order to (1) avoid costly repeated opening/closing of arrays for
        writing, and (2) avoid generating huge amounts of fragments for every
        sample written, we:

        * perform batch writes of accumulated array data to individual tiledb
          arrays, and consolidate fragments upon completion of batch write.

        * Stack individual arrays along a new first dimension to create
          reasonably size (N x SchemaSize) array stacks which can be block
          ``set`` in a single operation (creating only one fragment per stack),
          greatly reducing amount of fragments.

        This has significant performance implications (2 orders of magnitude
        greater then naive approach), but requires care to ensure all data is
        written in the expected spot, and that it will not overwrite other data
        pieces.

        In addition, as data is not written until this method is called, heavy
        reliance on the context managers is required so to not lose data during
        a crash.
        """
        ctx = tiledb.Ctx(config=TDB_CONFIG)
        with tiledb.DenseArray(self.wFp.uri, mode='w', ctx=ctx) as Arr:

            pidx = 0
            dataCont = np.zeros(shape=(self.MAX_PACK_SIZE, Arr.shape[-1]), dtype=self.schema_dtype)
            outDict = {str(i): np.zeros_like(dataCont) for i in range(8)}
            for aidx, hidx, data in self.Accumulator:
                if pidx < self.MAX_PACK_SIZE:
                    if pidx == 0:
                        dataCont[:] = 0
                        cAidx = aidx
                    dataCont[hidx, 0:data.size] = np.ravel(data, order='C')
                    pidx += 1
                else:
                    outDict[str(cAidx)] = np.array(dataCont)
                    cAidx, pidx = aidx, 0
                    dataCont = outDict[str(cAidx)]
                    dataCont[hidx, 0:data.size] = np.ravel(data, order='C')
                    pidx += 1

            if pidx != 0:
                outDict[str(cAidx)] = dataCont
                pidx = 0

            Arr[:, :] = outDict

        self.Accumulator = []
        self.AccumulatorNbytes = 0
        self.wFp.close()

    def write_data(self, array: np.ndarray, *, remote_operation: bool = False) -> bytes:
        """writes array data to disk in the tiledb_20 fmtBackend

        N.B. unlike most backends, data is not guaranteed to be saved to disk
        when this method returns. In order to ensure data integrity, context
        managers MUST be used while writing data to this backend.

        See discussion in :meth:`_write_chunk_data` for more information.

        Parameters
        ----------
        array : np.ndarray
            tensor to write to disk
        remote_operation : bool, optional, kwarg only
            True if writing in a remote operation, otherwise False. Default is
            False

        Returns
        -------
        bytes
            db hash record value specifying location information
        """
        checksum = xxhash.xxh64_intdigest(array)
        if self.wFp is not None:
            self.hIdx += 1
            if self.hIdx >= self.COLLECTION_SIZE:
                self._write_chunk_data()
                self._create_schema(remote_operation=remote_operation)
        else:
            self._create_schema(remote_operation=remote_operation)

        if (self.hIdx % self.MAX_PACK_SIZE) == 0:
            if self.hIdx != 0:
                self.aIdx += 1

        self.Accumulator.append((self.aIdx, self.hIdx % self.MAX_PACK_SIZE, array.flatten()))
        self.AccumulatorNbytes += array.nbytes
        if self.AccumulatorNbytes > self.MAX_ACCUMULATOR_NBYTES:
            self._write_chunk_data()

        hashVal = tiledb_20_encode(uri=self.w_uri,
                                   checksum=checksum,
                                   collection_idx=self.hIdx % self.MAX_PACK_SIZE,
                                   attr_idx=str(self.aIdx),
                                   shape=array.shape)
        return hashVal
