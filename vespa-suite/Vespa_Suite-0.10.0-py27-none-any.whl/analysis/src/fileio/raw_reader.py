# Python modules
from __future__ import division
import exceptions
import copy

# 3rd party modules

# Our modules
import vespa.analysis.src.util as util
import vespa.analysis.src.block_prep_fidsum as block_prep_fidsum
import vespa.analysis.src.block_prep_timeseries as block_prep_timeseries
import vespa.analysis.src. block_prep_wbnaa as block_prep_wbnaa
import vespa.analysis.src.block_raw as block_raw
import vespa.common.mrs_data_raw as mrs_data_raw
import vespa.common.mrs_data_raw_probep as mrs_data_raw_probep
import vespa.common.mrs_data_raw_cmrr_slaser as mrs_data_raw_cmrr_slaser
import vespa.common.mrs_data_raw_fidsum as mrs_data_raw_fidsum
import vespa.common.mrs_data_raw_timeseries as mrs_data_raw_timeseries
import vespa.common.mrs_data_raw_wbnaa as mrs_data_raw_wbnaa
import vespa.common.mrs_data_raw_edit_fidsum as mrs_data_raw_edit_fidsum
import vespa.common.mrs_data_raw_uncomb as mrs_data_raw_uncomb
import vespa.common.mrs_data_raw_fidsum_uncomb as mrs_data_raw_fidsum_uncomb
import vespa.common.util.misc as util_misc
import vespa.common.wx_gravy.common_dialogs as common_dialogs

import vespa.common.util.fileio as util_fileio

import vespa.analysis.src.fileio.util_exceptions as util_exceptions



class RawReader(object):
    """
    A base class for classes that transform a specific format (e.g. Siemens
    DICOM or VASF) into a Vespa DataRaw object. It defines the minimal interface
    that subclasses must support and also provides some default implementations.

    Subclasses must override read_raw().

    Subclasses may want to override pickfile(), read_raws() and any of the
    class' "private" methods.

    """
    def __init__(self):
        self.filetype_filter = ""
        self.filenames = [ ]
        self.multiple = True
        self.raws = [ ]


    def pickfile(self, default_path=""):
        self.filenames = \
            common_dialogs.pickfile(filetype_filter=self.filetype_filter,
                                    multiple=self.multiple,
                                    default_path=default_path)

        if not self.multiple:
            # Since we only allowed the user to select one file, we got a
            # string back. Turn it into a list.
            self.filenames = [self.filenames] if self.filenames else [ ]

        return bool(self.filenames)


    def read_raw(self, filename, ignore_data, *args, **kwargs):
        # Subclasses must implement this. See template.py for instructions.
        raise NotImplementedError


    def read_raws(self, ignore_data=False, *args, **kwargs):
        """
        Calls read_raw() once for each filename in self.filenames. It returns
        either a single DataRaw object or a list of them, depending on what
        read_raw() returns. (The implementation of read_raw() is 
        format-specific.)

        There are five possible cases --

        1) There is one file that contains one FID. This function returns a 
        single DataRaw instance with dims [N, 1, 1, 1] where N is the number
        of points in the FID (e.g. 1024). 

          The VASF format is an example.
        
        2) There are multiple files each containing a single FID. This function 
        returns a single DataRaw instance with data concatenated, a.k.a. a
        stack of single voxels. The dims are [N, M, 1, 1] where N is as
        above and M is the number of files.

          Importing multiple VASF files is an example.

        3) There is one file that contains multiple FIDs which are meant to 
        be summed once in Analysis. This is similar to case 2, except that 
        the object returned is a DataRawFidsum. Note - the Raw tab for these
        types of files performs whatever 'summing' is needed. This results in
        a data attribute in Raw that is essentially one spectrum, regardless
        of how many FIDs were read into the DataRawFidsum. For this reason,
        we are not able to 'stack into the screen' multiple spectra of these
        data types.

          Importing a Siemens DICOM Summed FIDs is an example.

        From here it gets complicated...

        4) There is one file that contains multiple FIDs which represent
        multiple datasets. These datasets have to be of one type of the above
        listed object classes, ie. all DataRaw or all DataRawFidsum.
        
        This function returns a list of these instances which will be turned into 
        a dataset in Analysis. It's up to the person who implements read_raw() to
        properly group the FIDs into separate RawData or RawDataFidsum objects.

        5) There are multiple files that contain multiple FIDs which represent
        multiple datasets. This is the same as 4, just more complicated. This
        method doesn't try to handle this case; it's too format-specific. If
        you want to implement this, you'll have to write your own version of 
        this method.



        If you for some reason need to examine the unconcatenated raw objects,
        they're available in this object's .raws attribute after this call 
        completes.

        If this is being called when one or more datasets is already open,
        then one of those open datasets must be passed in the open_dataset 
        param. The attributes of the raw files that this method opens must be 
        consistent with the ones that are already open. If they're not,
        this code raises MultifileAttributeMismatchError.

        Callers should be ready to handle MultifileAttributeMismatchError,
        UnsupportedDimensionalityError, IOError, SIDataError, and 
        FileNotFoundError (for VASF and possibly other formats).
        
        In addition, DataRaw.concatenate() (q.v.) can raise ValueError
        which is not trapped by this method.
        """
        self.raws = [ ]

        for filename in self.filenames:
            # Initially, we assume that read_raw() returns a single object, 
            # as in cases 1, 2, and 3...
            try:
                # This try/except is here because we changed the API from
                # fixed attribute/keywords to variable entries and we don't
                # want to force users to rewrite their code. So, here we
                # first try the new way of calling the user method.
                raw = self.read_raw(filename, ignore_data, *args, **kwargs)
            except:
                # and this is the old way of calling the user method.
                raw = self.read_raw(filename, ignore_data)
            self.raws.append(raw)


        if (len(self.filenames) == 1): 
            
            if util_misc.is_iterable(self.raws[0]):
                # This is case 4 - need to get rid of one level of list dims
                self.raws = self.raws[0]
            
            if type(self.raws[0]) == mrs_data_raw.DataRaw or \
               type(self.raws[0]) == mrs_data_raw_probep.DataRawProbep:
                # This is case 1 or 4
                fidsum_flag = False
            elif type(self.raws[0]) == mrs_data_raw_fidsum.DataRawFidsum or \
                 type(self.raws[0]) == mrs_data_raw_timeseries.DataRawTimeseries or \
                 type(self.raws[0]) == mrs_data_raw_wbnaa.DataRawWbnaa or \
                 type(self.raws[0]) == mrs_data_raw_edit_fidsum.DataRawEditFidsum or \
                 type(self.raws[0]) == mrs_data_raw_uncomb.DataRawUncomb or \
                 type(self.raws[0]) == mrs_data_raw_fidsum_uncomb.DataRawFidsumUncomb or \
                 type(self.raws[0]) == mrs_data_raw_cmrr_slaser.DataRawCmrrSlaser:
                # This is case 3 or 4
                fidsum_flag = True
            
            self._check_consistency(fidsum=fidsum_flag)
            self._check_for_si()
            if 'open_dataset' in kwargs.keys():
                if kwargs['open_dataset'] is not None:
                    self._check_compatibility(self.raws, kwargs['open_dataset'], fidsum=fidsum_flag)

            master = self.raws

        elif (len(self.filenames) > 1):
            if any(util_misc.is_iterable(item) for item in self.raws):
                # This is case 5. 
                raise NotImplementedError
            else:
                # This is case 2 or 4
                if type(self.raws[0]) == mrs_data_raw.DataRaw or \
                   type(self.raws[0]) == mrs_data_raw_probep.DataRawProbep:
                    # This is case 2
                    fidsum_flag = False
                elif type(self.raws[0]) == mrs_data_raw_fidsum.DataRawFidsum or \
                     type(self.raws[0]) == mrs_data_raw_timeseries.DataRawTimeseries or \
                     type(self.raws[0]) == mrs_data_raw_uncomb.DataRawUncomb:
                    # This is case 4
                    fidsum_flag = True
                
                self._check_consistency()   # note. no fidsum flag, dims must match
                self._check_for_si()

                # We need to concatenate multiple files/FIDs into one 
                # DataRaw(Fidsum). This has to happen before we compare to 
                # open datasets to be sure that final dims are compared
                master = copy.deepcopy(self.raws[0])
                for raw in self.raws[1:]:
                    master.concatenate(raw)

                master = [master]
    
                if kwargs['open_dataset']:
                    self._check_compatibility(master, kwargs['open_dataset'], fidsum=fidsum_flag)

        return master


    ##################  Internal use only methods below   ##################


    # These methods shouldn't be called by users of this class. However,
    # subclasses should feel free to override them as necessary.
    def _check_consistency(self, fidsum=False):
        # When opening multiple files that will be concatted into a single
        # raw, _check_consistency() must be called before concatenation.
        # Concatenation might fail otherwise.
        if (len(self.raws) == 1) and (len(self.filenames) == 1):
            # Case 1 - One file, one FID, no problem
            pass
        elif len(self.raws) > 1:
            # Cases 2-4, all objects in the raws list must be the same type
            
            first = type(self.raws[0])
            if not all(type(item)==first for item in self.raws):
                raise util_exceptions.MultifileTypeMismatchError
            
            raw0 = self.raws[0]
            # The attributes (dims & sweep width) must match.
            for raw in self.raws[1:]:
                if fidsum:
                    dims_flag = (raw0.dims[0] == raw.dims[0])
                else:
                    dims_flag = (raw0.dims == raw.dims)
                
                if dims_flag and (raw0.sw == raw.sw):
                    # All is well!
                    pass
                else:
                    raise util_exceptions.MultifileAttributeMismatchError
                    
            # We also need to ensure that at least one dimension is 1. Datasets
            # with all dims > 1 might be valid data, but Vespa doesn't
            # support that.
            if min(raw0.dims) > 1:
                raise util_exceptions.UnsupportedDimensionalityError


    def _check_dimensionality(self, open_dataset):
        # If there's already a dataset open, the attributes of what we're 
        # trying to open must match those of the open dataset(s).
        for raw in self.raws:
            if (raw.dims == open_dataset.raw_dims) and \
               (raw.sw   == open_dataset.sw):
                # All is well!
                pass
            else:
                raise util_exceptions.OpenFileAttributeMismatchError
            
            
    def _check_compatibility(self, raws, open_dataset, fidsum=False):
        # If there's already a dataset open, the attributes and object type
        # of what we are trying to open must match those of the open dataset(s)
        if isinstance(self.raws[0], mrs_data_raw.DataRaw) and \
           not isinstance(open_dataset.blocks["raw"], block_raw.BlockRaw):
            raise util_exceptions.OpenFileTypeMismatchError

        if isinstance(self.raws[0],  mrs_data_raw_fidsum.DataRawFidsum) and \
           not (isinstance(open_dataset.blocks["prep"], block_prep_fidsum.BlockPrepFidsum) or \
                isinstance(open_dataset.blocks["prep"], block_prep_wbnaa.BlockPrepWbnaa)):
            raise util_exceptions.OpenFileTypeMismatchError

        if isinstance(self.raws[0],  mrs_data_raw_timeseries.DataRawTimeseries) and \
           not (isinstance(open_dataset.blocks["prep"], block_prep_timeseries.BlockPrepTimeseries) ):
            raise util_exceptions.OpenFileTypeMismatchError
        
        for raw in raws:
            if fidsum:
                dims_flag = (raw.dims[0] == open_dataset.raw_dims[0])
            else:
                dims_flag = (raw.dims == open_dataset.raw_dims)

            if  dims_flag and (abs(raw.sw - open_dataset.sw) < 0.001):
                # Had to add the 'slight difference' equation for real world conditions
                # All is well!
                pass
            else:
                raise util_exceptions.OpenFileAttributeMismatchError
                   
                   
    def _check_for_si(self):
        for raw in self.raws:
            dims = self.raws[0].dims[3:]
            
            if type(self.raws[0]) == mrs_data_raw_uncomb.DataRawUncomb:
                # this has indiv coil data in it, only check last dim
                dims = self.raws[0].dims[3:]
            
            # This map() call returns a list of bools that are True for
            # each dim == 1. 
            if not all(map(lambda dim: dim == 1, dims)):
                raise util_exceptions.SIDataError

