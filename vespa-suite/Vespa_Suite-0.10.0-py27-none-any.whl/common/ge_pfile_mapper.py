#
# Some of the code in this file was derived from C++ code in the
# SIVIC project, http://sourceforge.net/apps/trac/sivic/
# and as such we have included their BSD statement in this file.
#
# Copyright 2009-2010 The Regents of the University of California.
# All Rights Reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# *   Redistributions of source code must retain the above copyright notice,
#     this list of conditions and the following disclaimer.
# *   Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions and the following disclaimer in the documentation
#     and/or other materials provided with the distribution.
# *   None of the names of any campus of the University of California, the name
#     "The Regents of the University of California," or the names of any of its
#     contributors may be used to endorse or promote products derived from this
#     software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE COPYRIGHT HOLDERS OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
# NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY
# OF SUCH DAMAGE.

# Python modules
from __future__ import division
import os
import math

# Third party packages
import numpy as np


from ctypes import *



class PfileMapper(object):

    def __init__(self, file_name, hdr, version, endian):
        """
        Given a file name, its header, version number and endianess, this
        class will parse the data section of the file for the suppressed and
        unsuppressed data.  
        
        All 'timePts' (aka. FID data arrays) are stored in the raw_data 
        attribute. It is a numpy ndarray with shape of:
        
        [cols, rows, slices, numTimePts, numCoils, numSpecPts], np.complex64
        
        For SVS data, cols, rows and slices are all equal to 1. 
        
            - raw_suppressed   is a view onto the  water suppressed fids data
            - raw_unsuppressed is a view onto the water unsuppressed fids data
            - avg_suppressed and avg_unsuppressed are numpy arrays where the
                  relevant raw_ views have been summed along the numTimePts
                  dimension. shape = [cols, rows, slices, numCoils, numSpecPts]
                  
        For non-SVS data, only the raw_data attribute has data in it.
        
        History:
        
        Derived from SIVIC file svkGEPFileMapper.cc which was used to map data
        from PROBE-P ad PRESSCSI P-files.  SIVIC has other mapper classes for
        other types of P-file data. I will plan on using this model here, too.
        
        """
        
        self.file_name = file_name
        self.hdr       = hdr
        self.version   = version
        self.endian    = endian
        self.is_svs    = False
        
        self.raw_data         = None
        self.raw_suppressed   = None
        self.avg_suppressed   = None
        self.raw_unsuppressed = None
        self.avg_unsuppressed = None
    
        
        
    @property
    def get_select_box_center(self):
        """
        Center position is taken from user variables.  The Z "slice"
        position used to be taken from the image header "image.loc",
        but with the LX architecture, this held the table position only,
        so if Graphic RX was used to introduce an offset, it wouldn't
        be successfully extracted.
        
        """
        center0 = -1 * self.hdr.rhi_user11
        center1 = -1 * self.hdr.rhi_user12
        center2 =      self.hdr.rhi_user13
        
        return np.array([center0, center1, center2])
        

    @property
    def get_select_box_size(self):        
        
        boxsize = np.array([0.0, 0.0, 0.0])
        dcos = self.get_dcos
        
        if self.version > 9:

            lMax   = 0
            pMax   = 0
            sMax   = 0
            lIndex = 0
            pIndex = 0
            sIndex = 0
            for i in range(3):
                if abs( dcos[i][0] ) > lMax:
                    lIndex = i
                    lMax = abs( dcos[i][0] )
                if abs( dcos[i][1] ) > pMax:
                    pIndex = i
                    pMax = abs( dcos[i][1] ) 
                if abs( dcos[i][2] ) > sMax:
                    sIndex = i
                    sMax = abs( dcos[i][2] )

            boxsize[ lIndex ] = self.hdr.rhi_user8
            boxsize[ pIndex ] = self.hdr.rhi_user9
            boxsize[ sIndex ] = self.hdr.rhi_user10

        else:

            boxsize[0] = self.hdr.rhr_roilenx
            boxsize[1] = self.hdr.rhr_roileny
            boxsize[2] = self.hdr.rhr_roilenz

            if self.is_swap_on:
                ftemp = boxsize[0]
                boxsize[0] = boxsize[1]
                boxsize[1] = ftemp
        
        return boxsize


    @property
    def get_voxel_spacing(self):  
        """
        Get the voxel spacing in 3D. Note that the slice spacing may include
        a skip.
        Swaps the FOV if necessary based on freq_dir setting.

        """
        user19 = self.hdr.rhi_user19
        voxspace = np.array([0.0, 0.0, 0.0])
        
        if (user19 > 0)  and (self.version > 9):
            voxspace[0] = user19
            voxspace[1] = user19
            voxspace[2] = user19
        else:
            fov  = self.get_fov
            nvox = self.get_num_voxels
            voxspace[0] = fov[0]/nvox[0]
            voxspace[1] = fov[1]/nvox[1]
            voxspace[2] = fov[2]/nvox[2]       
    
        return voxspace
        

    @property
    def get_fov(self): 
        fov  = np.array([0.0, 0.0, 0.0])
        nvox = self.get_num_voxels
    
        dfov = self.hdr.rhi_dfov
        
        if self.version > 9:

            fov[0] = dfov
            fov[1] = dfov

            # 2D case vs 3D cases
            if self.is_2d:
                fov[2] = self.hdr.rhi_user10
            else:
                fov[2] = self.hdr.rhi_scanspacing * self.hdr.rhr_zcsi
        else:
            fov[0] = self.hdr.rhr_rh_user7
            fov[1] = self.hdr.rhr_rh_user8
            fov[2] = self.hdr.rhr_rh_user9

        #  Anisotropic voxels:
        if (self.version > 9) and (nvox[0] != nvox[1]):

            # CSI has already been reordered if needed - so fov  calculated 
            # with this CSI will not need reordering, need next power of 2:
            xdim = int(pow(2, math.ceil(math.log(nvox[0], 2))))
            ydim = int(pow(2, math.ceil(math.log(nvox[1], 2))))

            if( ydim > xdim ):
                fov_spatial_resolution = dfov/ydim
            else:
                fov_spatial_resolution = dfov/xdim

            fov[1] = fov_spatial_resolution * ydim
            fov[0] = fov_spatial_resolution * xdim

        elif self.is_swap_on:

            #  Swap the FOV if necessary based on freq dir:
            temp = fov[0]
            fov[0] = fov[1]
            fov[1] = temp

        return fov        
     
     
    @property
    def get_num_voxels(self):   
        """
        Get the 3D spatial dimensionality of the data set
        Returns an int array with 3 dimensions.  Swaps
        if necessary based on freq_dir setting.
        
        """
        nvox = np.array([0, 0, 0])
     
        if self.hdr.rhr_rh_file_contents == 0:
            nvox[0] = 1
            nvox[1] = 1
            nvox[2] = 1
        else:
            nvox[0] = int(self.hdr.rhr_xcsi)
            nvox[1] = int(self.hdr.rhr_ycsi)
            nvox[2] = int(self.hdr.rhr_zcsi)

        #  Swap dimensions if necessary:
        if self.is_swap_on:
            temp = nvox[0]
            nvox[0] = nvox[1]
            nvox[1] = temp

        return nvox
     

    @property
    def get_dcos(self):      
        dcos = np.zeros([3, 3], float)     
     
        dcos[0][0] = -( self.hdr.rhi_trhc_R - self.hdr.rhi_tlhc_R )
        dcos[0][1] = -( self.hdr.rhi_trhc_A - self.hdr.rhi_tlhc_A )
        dcos[0][2] =  ( self.hdr.rhi_trhc_S - self.hdr.rhi_tlhc_S )
        
        dcosLengthX = np.sqrt( dcos[0][0] * dcos[0][0]
                             + dcos[0][1] * dcos[0][1]
                             + dcos[0][2] * dcos[0][2] )

        dcos[0][0] /= dcosLengthX
        dcos[0][1] /= dcosLengthX
        dcos[0][2] /= dcosLengthX


        dcos[1][0] = -( self.hdr.rhi_brhc_R - self.hdr.rhi_trhc_R )
        dcos[1][1] = -( self.hdr.rhi_brhc_A - self.hdr.rhi_trhc_A )
        dcos[1][2] =  ( self.hdr.rhi_brhc_S - self.hdr.rhi_trhc_S )

        dcosLengthY = np.sqrt( dcos[1][0] * dcos[1][0]
                             + dcos[1][1] * dcos[1][1]
                             + dcos[1][2] * dcos[1][2] )

        dcos[1][0] /= dcosLengthY
        dcos[1][1] /= dcosLengthY
        dcos[1][2] /= dcosLengthY


        # third row is the vector product of the first two rows
        # actually, -1* vector product, at least for the axial and axial oblique
        # which is all that we support now
        dcos[2][0] = - dcos[0][1] * dcos[1][2] + dcos[0][2] * dcos[1][1]
        dcos[2][1] = - dcos[0][2] * dcos[1][0] + dcos[0][0] * dcos[1][2]
        dcos[2][2] = - dcos[0][0] * dcos[1][1] + dcos[0][1] * dcos[1][0]

        return dcos
     

    @property
    def is_swap_on(self):      
        """ Is frequency direction swapped? """     
        if self.hdr.rhi_freq_dir != 1:
            return True
        else:
            return False
   

    @property
    def is_2d(self):      
        """ Is this a 2D or 3D data set (spatial dimensions)? """        
        is2D = False
        ndims = self.hdr.rhr_csi_dims

        if ndims == 0:
            if self.hdr.rhr_xcsi >= 0:
                ndims += 1
            if self.hdr.rhr_ycsi >= 0:
                ndims += 1
            if self.hdr.rhr_zcsi >= 0:
                ndims += 1

        if ndims == 2:
            is2D = True

        return is2D
   

    @property
    def is_chop_on(self):      
        """ Is data chopped? """        
        chop  = False
        nex   = self.hdr.rhi_nex
        necho = self.hdr.rhi_numecho

        if ( math.ceil(nex) * necho ) <= 1:
            chop = True

        return chop
        
        
    @property
    def get_frequency_offset(self):      
        """ Returns the spectral frquency offset """        
        if self.version > 9:
            return 0.0
        else:
            return self.hdr.rhr_rh_user13

        
    @property
    def get_center_from_raw_file(self):      
        """ 
        Gets the center of the acquisition grid.  May vary between sequences.
        
        """
        center = np.array([0.0, 0.0, 0.0])
        if self.version < 11:
            center[0] = 0
            center[1] = 0
            center[2] = self.hdr.rhi_user13
        else:
            center[0] = -1 * self.hdr.rhi_user11
            center[1] = -1 * self.hdr.rhi_user12
            center[2] = self.hdr.rhi_user13
       
        return center

   
    @property
    def get_num_coils(self):      
        """ Determine number of coils of data in the PFile. """
        ncoils = 0
        for i in range(4):
            start_rcv = getattr(self.hdr, "rhr_rh_dab["+str(i)+"]_start_rcv")
            stop_rcv  = getattr(self.hdr, "rhr_rh_dab["+str(i)+"]_stop_rcv")

            if ( start_rcv != 0) or (stop_rcv != 0):
                ncoils += ( stop_rcv - start_rcv ) + 1

        #  Otherwise 1
        if ncoils == 0:
            ncoils = 1

        return int(ncoils)   
 
 
    @property
    def get_num_time_points(self):      
        """ 
        Determine number of time points in the PFile.
        Number of time points is determined from the file size,
        number of voxels and number of coils.
        """
        passSize      = float(self.hdr.rhr_rh_raw_pass_size)
        numCoils      = float(self.get_num_coils)
        numVoxels     = float(self.get_num_voxels_in_vol)
        dataWordSize  = float(self.hdr.rhr_rh_point_size)
        numFreqPoints = float(self.hdr.rhr_rh_frame_size)
        kSpacePoints  = float(self.get_num_kspace_points)

        numTimePoints = int( ( passSize ) / ( numCoils * 2 * dataWordSize * numFreqPoints ) - 1 ) / kSpacePoints

        # bjs - added this after Pom's fidcsi 13C data came up with 0 here
        if numTimePoints <= 0:
            numTimePoints = 1

        return int(numTimePoints)

       
    @property
    def get_num_dummy_scans(self):        
        """
        Determine number of dummy scans (FIDs) in the data block.
        This is the difference between the raw pass size and the
        expected size of the data based on numCoils, numTimePts, numKSpacePts
        and numFreqPts.        
        
        """
        passSize         = self.hdr.rhr_rh_raw_pass_size
        numCoils         = self.get_num_coils 
        numTimePoints    = self.get_num_time_points 
        numSampledVoxels = self.get_num_kspace_points
        numFreqPoints    = self.hdr.rhr_rh_frame_size
        dataWordSize     = self.hdr.rhr_rh_point_size

        dataRepresentation = "COMPLEX"  # this was hard set in DcmHeader code
        if ( dataRepresentation == "COMPLEX" ):
            numComponents = 2
        else:
            numComponents = 1

        #  Calc the diff between the size of the data buffer and the number of real data points
        #  then divide by the number of bytes in a single fid to get the number of dummy FIDs
        numDummyScans = passSize - ( numCoils * numTimePoints * numSampledVoxels * numFreqPoints * numComponents * dataWordSize )

        numDummyScans = numDummyScans / ( numFreqPoints * numComponents * dataWordSize)

        return int(numDummyScans)
 
   
    @property
    def get_num_frames(self):    
        """ Number of frames is number of slices * numCoils * numTimePoints """   

        nvox = self.get_num_voxels
        nframes = nvox[2] * self.get_num_coils * self.get_num_time_points

        return int(nframes)
   
   
    @property
    def get_num_voxels_in_vol(self):    

        nvox = self.get_num_voxels
        
        return int(nvox[0] * nvox[1] * nvox[2])   
   
   
    @property
    def get_num_kspace_points(self):    
        """
        Determine the number of sampled k-space points in the data set.
        This may differ from the number of voxels in the rectalinear grid,
        for example if elliptical or another non rectangular acquisition
        sampling strategy was employed.  GE product sequences pad the
        reduced k-space data with zeros so the number of k-space points
        is the same as the number of voxels, but that may not be true for
        custom sequences.        
        
        """
        return int(self.get_num_voxels_in_vol)


    @property
    def was_index_sampled(self):    
        """
        Determines whether a voxel (index) was sampled (or a zero padded
        point is present in the data set), or not, i.e. was it within
        the elliptical sampling volume if reduced k-space elliptical sampling
        was used. Could be extended to support other sparse sampling
        trajectories. Note that for product sequences this always returns true
        since GE  zero-pads reduced k-space data to a full rectilinear grid.
        
        """
        return True   


    @property
    def get_number_unsuppressed_acquisitions(self):    
        """
        For single voxel acquisitions, return the number of
        unsuppressed acquisitions.        
        
        """
        nex = self.hdr.rhi_nex
        return int(16 / nex)

        
    @property
    def get_number_suppressed_acquisitions(self):    
        """
        For single voxel acquisitions, return the number of
        suppressed acquisitions.        
        
        """
        nex   = self.hdr.rhi_nex
        user4 = self.hdr.rhi_user4
        return int( user4 / nex )


    def add_dummy(self, offset, coilNum, timePt):      
        """ 
        Determine whether to add a dummy scan. The assumption is that
        the number of dummy scans should be equal to the number of coils
        or numCoils * numTimePts (e.g. for a spectral editing sequence).
        If true, then the an FID worth of data should be skipped over when
        reading data (e.g. frame_size * numComponents, or numFreqPts * numComponents)        
        """
        numDummyScans    = self.get_num_dummy_scans
        numCoils         = self.get_num_coils
        numTimePoints    = self.get_num_time_points 
        numSampledVoxels = self.get_num_kspace_points
        numFreqPoints    = self.hdr.rhr_rh_frame_size
        numComponents    = 2
        numPointsPerFID  = numFreqPoints * numComponents

        #  subtract the number of dummy words from the current offset to see if another
        #  dummy scan should be skipped or not
        
        if numDummyScans == numCoils:
            numWordsBetweenDummies = numSampledVoxels * numPointsPerFID * numTimePoints
            offset = offset - (coilNum * numPointsPerFID)
            # additional time points have an offset that includes the per-coil dummy
            if timePt > 1:
                offset = offset - numPointsPerFID
        
        elif ( numDummyScans == (numCoils * numTimePoints) ):
            numWordsBetweenDummies = numSampledVoxels * numPointsPerFID
            offset = offset - (coilNum * numPointsPerFID) - ( ( coilNum + timePt ) * numPointsPerFID )
        
        elif numDummyScans == 0:    # bjs - added for fidcsi 13C data from Pom
            return False
        
        else:
            pass
            # "ERROR: Can not determine placement of dummy scans in raw file reader. \n"

        addDummy = False
        if ( ( offset % numWordsBetweenDummies ) == 0 ):
            addDummy = True

        return addDummy
   
   
    def get_xyz_indices(self, dataIndex): 
        """
        If swapping is turned on, the data will need to get mapped correctly
        from the input data buffer read from disk (specData) to the correct
        svkImageData arrays. If swap is true, then the data indices are swapped
        and ky is flipped.
        
        """

        numVoxels = self.get_num_voxels

        z = int( dataIndex/(numVoxels[0] * numVoxels[1]) )

        if self.is_swap_on:

            # If swap is on use numVoxels[1] for x dimension and numVoxels[0] for y dimension
            x = int((dataIndex - (z * numVoxels[0] * numVoxels[1]))/numVoxels[1])

            # In addition to swapping reverse the y direction
            y = numVoxels[1] - int( dataIndex % numVoxels[1] ) - 1

        else:
            x = int( dataIndex % numVoxels[0] )
            y = int((dataIndex - (z * numVoxels[0] * numVoxels[1]))/numVoxels[0])

        return x, y, z





    def get_center_from_origin(self, origin, numVoxels, voxelSpacing, dcos): 
        """
        Calculates the LPS center from the origin(toplc).
        
        """
        center = np.array([0.0, 0.0, 0.0])

        for i in range(3):
            center[i] = origin[i]
            for j in range(3):
                center[i] += dcos[j][i] * voxelSpacing[j] * ( numVoxels[j] / 2.0 - 0.5 )


    def get_origin_from_center(self, center, numVoxels, voxelSpacing, dcos): 
        """
        Calculates the LPS origin (toplc) from the center.
        
        """
        origin = np.array([0.0, 0.0, 0.0])

        for i in range(3):
            origin[i] = center[i]
            for j in range(3):
                origin[i] -= dcos[j][i] * voxelSpacing[j] * ( numVoxels[j] / 2.0 - 0.5 )
        
        


    def read_data(self):            
        """
        This method reads data from the pfile and puts the data into 
        the CellData arrays. If elliptical k-space sampling was used, 
        the data is zero-padded.  Other reduced k-space sampling 
        strategies aren't supported yet.
        
        """

        numCoils        = self.get_num_coils
        numTimePts      = self.get_num_time_points
        numSpecPts      = self.hdr.rhr_rh_frame_size
        numFreqPts      = numSpecPts
        numComponents   =  2
        dataWordSize    = self.hdr.rhr_rh_point_size

        numBytesInVol   = self.get_num_kspace_points * numSpecPts * numComponents * dataWordSize
        numBytesPerCoil = numBytesInVol * numTimePts

        numPtsPerSpectrum = numSpecPts * numComponents

        #  one dummy spectrum per volume/coil:
        numDummyBytes = self.get_num_dummy_scans * numPtsPerSpectrum * dataWordSize
        numDummyBytesPerCoil = int(numDummyBytes/numCoils)

        numBytesPerCoil += numDummyBytesPerCoil

        #  Only read in one coil at a time to reduce memory footprint 
        specData_size = long(np.round((numBytesPerCoil / dataWordSize),0))
        specData = np.zeros([specData_size, ],float) 

        try:
            readOffset = self.hdr.rhr_rdb_hdr_off_data
            filelike = open(self.file_name, 'rb')
            filelike.seek(0)
            filelike.seek(readOffset)
        except:
            pass
            # "ERROR: Exception opening/reading file " << pFileNames->GetValue(0) << " => " << e.what() << endl;

        numVoxels       = self.get_num_voxels
        cols            = numVoxels[0]
        rows            = numVoxels[1]
        slices          = numVoxels[2]
        arraysPerVolume = cols * rows * slices

        #  Preallocate data arrays. The API only permits dynamic assignment at end of CellData, so for
        #  swapped cases where we need to insert data out of order they need to be preallocated.
        
        data = np.zeros([cols, rows, slices, numTimePts, numCoils, numSpecPts], np.complex64)

        #  Blank scan prepended to data blocks.
        dummyOffset = numPtsPerSpectrum 

        #  If Chop On, then reinitialize chopVal:
        chopVal = 1
        if self.is_chop_on:
            chopVal = -1 

        #  pFileOOffset is the offset of the current data set within the 
        #  pFile (i.e. a global data offset).  #  a given coil. 
        pFileOffset = 0

        for coilNum in range(numCoils):
            #  Offset is the offset within the current block of loaded data (ie. within a given coil)
            offset = 0 

            if dataWordSize == 4:
                tempData = np.fromfile(filelike , dtype='i4' , count=int(numBytesPerCoil/dataWordSize) )
            elif dataWordSize == 2:
                tempData = np.fromfile(filelike , dtype='i2' , count=int(numBytesPerCoil/dataWordSize) )
            if self.endian != 'little':
                tempData.byteswap(True)     # swap in-place
            specData = tempData.astype(np.float32)     

            for timePt in range(numTimePts):

                #  Should a dummy scan be skipped over?
                if self.add_dummy( pFileOffset, coilNum, timePt ):
                    offset      += dummyOffset 
                    pFileOffset += dummyOffset

                for arrayNumber in range(arraysPerVolume):
                    x, y, z = self.get_xyz_indices(arrayNumber)

                    #  if k-space sampling was used check if the point was sampled, or if it needs
                    #  to be zero-padded in the grid.
                    #  if zero-padding don't increment the data pointer offset.

                    wasSampled = self.was_index_sampled

                    #  Default, chop is off, so multiply all values by 1
                    #  Only chop sampled data points.
                    if self.is_chop_on and wasSampled:
                        chopVal *= -1

                    if wasSampled:
                        tempFloat = specData[offset:offset+numFreqPts*numComponents]
                        data[x, y, z, timePt, coilNum, :] = chopVal * tempFloat.view(np.complex64)
                    else:
                        pass # do nothing because array is initialized to zeros 

                    if wasSampled:
                        offset      += numPtsPerSpectrum
                        pFileOffset += numPtsPerSpectrum


        filelike.close() 

        self.raw_data = data
        
        #  Modify the data loading behavior.  For single voxel multi-acq data
        #  this means return the averaged (suppresssed data, if applicable).

        numUnsuppressed = self.get_number_unsuppressed_acquisitions 
        numSuppressed   = self.get_number_suppressed_acquisitions

        # bjs - changed numTimePoints to >= 1 below due to Pom's fidcsi 13C data
        # bjs - changed numSuppressed to >= 1 below due to oslaser dv26 data

        # Check if single voxel
        self.is_svs = False
        if ( (numVoxels[0] * numVoxels[1] * numVoxels[2] == 1) and (numTimePts >= 1) and (numSuppressed >= 1)): 
            self.is_svs = True
        
        if self.is_svs:
            self.raw_unsuppressed = self.raw_data[:,:,:,0:numUnsuppressed,:,:]
            self.raw_suppressed   = self.raw_data[:,:,:,numUnsuppressed:,:,:]
            self.avg_unsuppressed = np.sum(self.raw_unsuppressed, axis=3) / float(numUnsuppressed)
            self.avg_suppressed   = np.sum(self.raw_suppressed,   axis=3) / float(numSuppressed)
            self.phase_first_point_deg = np.angle(self.avg_unsuppressed[0,0,0,:,0], True)
        else:
            self.raw_suppressed   = None
            self.avg_suppressed   = None
            self.raw_unsuppressed = None
            self.avg_unsuppressed = None
            self.phase_of_first_point_deg = None
            
        return
    


class PfileMapperSlaser(PfileMapper):

    def __init__(self, file_name, hdr, version, endian):
        """
        This info was provided by Ralph Noeske at GE who wrote the sLASER
        sequence in collaboration with Gulin Oz. Needed to get a few 
        parameters from different header locations, but otherwise the basic
        code seems to work OK.

        rdb_hdr_user0 = rhuser0 = 6024 (sampling frequency)
        rdb_hdr_user4 = rhuser4 = 64 (number of averages)
        rdb_hdr_user19 = rhuser19 = 8 (number of reference frames)
        
        image_user8 = opuser8 is used as starting for voxel dimension and location (opuser8,9,10,11,12,13)
        
        The sub-echo-times are TE1 = 8ms and TE2 = 12ms (opuser20 and 21).  

        
        """
        PfileMapper.__init__(self, file_name, hdr, version, endian)


    @property
    def get_number_unsuppressed_acquisitions(self):    
        """
        For single voxel acquisitions, return the number of
        unsuppressed acquisitions.        
        
        """
        user19 = self.hdr.rhr_rh_user19
        return int(user19)

        
    @property
    def get_number_suppressed_acquisitions(self):    
        """
        For single voxel acquisitions, return the number of
        suppressed acquisitions.        
        
        """
        user4 = self.hdr.rhr_rh_user4
        return int( user4 )
   


        
