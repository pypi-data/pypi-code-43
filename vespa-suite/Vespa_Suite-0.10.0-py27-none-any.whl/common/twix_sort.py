# Python modules
from __future__ import division
import os
import struct
import itertools
import sys
import time

import numpy as np

import vespa.common.twix_parser as twix_parser
import vespa.common.twix_parser_multi_raid as twix_parser_multi_raid


"""
This is a Python parser for ...

Brief sample usage is at the end of this file. 

This file itself is executable; invoke like so:
   python twix.py  your_filename.dat

Enjoy,
Brian Soher on behalf of the Vespa project
http://scion.duhs.duke.edu/vespa/

==============================
 NEWS
==============================

2017-01-27  Released version 0.1.0, developed and tested only under VE11

"""

VERSION = "0.1.0"


SCAN_INDICES = ['ide', 'idd', 'idc', 'idb', 'ida', 
                'segment', 'phase', 
                'echo', 'partition', 
                'slice', 'acquisition', 
                'line', 'repetition', 
                'set', 'channel_id' ]

MULTI_INDICES = ['ide', 'idd', 'idc', 'idb', 'ida', 
                 'segment', 'phase', 
                 'echo', 'partition', 
                 'slice', 'acquisition', 
                 'line', 'repetition', 'set' ]      # no channel_id index, inherent now




class TwixSort(object):

    def __init__(self, twix_obj):
        """
        On being passed a TwixRaid (VB twix) object that has evps and scans in it we 
        automatically create a list of all ICE dimensions for each scan and
        run a check on these dims to ensure that they are unique. 
        
        If dims are unique, we can (if asked) return a numpy array will all 
        14 ICE dimensions and let the user make full use of the ICE loop 
        counter organization of the data. The array would look like:
        
        [ide, idd, idc, idb, ... , partition, slice, line, chan, col]
        
        If dims are unique, we can also return a numpy array in this order:
        [ repetition, channel_id, set (averages), spectral points ] but we 
        require that all other dims be equal to 1.
        
        If we don't care if dims unique or not, we can sort data into two
        types of numpy arrays. The first is in [scan order, spectral points]
        and the second is in [ channel_id, set (averages), spectral points]
        order. The second version requires that the number of scans divides 
        evenly in to the number of channels.
        
        """
        msg = ''
        if not isinstance(twix_obj, twix_parser.TwixRaid):
            msg = "Twix object not a TwixRaid object, returning!"
        elif twix_obj.scans is None:
            msg = "TwixRaid object has no scans, returning!"

        if msg:
            raise ValueError(msg)
        
        self.twix           = twix_obj
       
        self.indices_list   = self.create_ice_indices()
        self.indices_unique = self.check_unique_indices()
        self.dims           = self.get_dims()
        

    def get_ice_index(self, iscan):
        """ 
        Return tuple of ICE loop values in SCAN_INDICES order given an index
        in the self.indices_list attribute. This method is typically used by
        the get_data_numpy() call, so we add an Ellipsis object to the end
        of the index list and convert the list into a tuple so it can be used
        to index a location in the numpy output array for the scan data. 
        
        """
        if iscan > len(self.indices_list):
            msg = "Scan index outside range of indices_list"
            raise ValueError(msg)

        indx = list(self.indices_list[iscan])
        indx.append(Ellipsis)
        indx = tuple(indx)
        return indx
    

    def create_ice_indices(self):
        """ return list of the dims of each Scan """
        dims = []
         
        for scan in self.twix.scans:
            vals = []
            for attr in SCAN_INDICES:
                vals.append(getattr(scan, attr))
            dims.append(vals)
         
        return dims

    
    def get_dims(self):
        """ return list of the max value in each dim, plus samples per scan """

        # transpose the list of lists and check max val in each dimension         
        dims = [max(item)+1 for item in zip(*self.indices_list)]
        
        dims.append(self.twix.scans[0].samples_in_scan) 
         
        return dims    
    
    
    def check_unique_indices(self):
        """ uses set to determine if all ice dims are unique """
        tmp = [tuple(item) for item in self.indices_list]
        tmp = set(tmp)
        if len(tmp) == len(self.indices_list):
            return True
        else:
            return False
        
    
    def get_data_numpy_ice_indexed(self):
        """
        Use the ICE loop indices to sort each scan into a numpy array with 
        all 16 dimensions.  This option can not be used if we don't have a
        unique set of ICE indices. We use check_unique_indices() to determine
        if this is the case.  If everything is OK, we return a numpy array,
        if it is not, we return None.
        
        """
        if not self.indices_unique:
            msg = "ICE indices are not unique, can not return in a Loop Counter dimensioned numpy array."
            raise ValueError(msg)
        
        nparr = np.zeros(self.dims, np.complex)
        
        for i,scan in enumerate(self.twix.scans):
            indx = self.get_ice_index(i)
            print "List, index = "+str(self.indices_list[i])+"  "+str(indx)
            nparr[indx] = np.array(scan.data)

        return nparr


    def get_data_numpy_scan_order(self):
        """ return numpy array of all FID data in scan order - no indexing """

        nscan = len(self.twix.scans)
        npts  = self.twix.scans[0].samples_in_scan
        
        nparr = np.zeros([nscan, npts], np.complex)

        nparr = np.zeros([len(self.twix.scans), self.twix.scans[0].samples_in_scan], np.complex)
        
        for i,scan in enumerate(self.twix.scans):
            nparr[i,:] = np.array(scan.data)

        return nparr


    def get_data_numpy_channel_scan_order(self):
        """
        Sort all scans into numpy array in [channel_id, fid, spectral points] order.
        
        This does not require unique dimensions. It does require that total 
        number of scans divided by number of channels is an integer. It is
        assumed that all channels for a given FID follow one after the other
        in the scan list.
        
        """
        npts  = self.twix.scans[0].samples_in_scan
        nscan = len(self.twix.scans)
        ncha  = self.twix.scans[0].used_channels
        
        if (nscan % ncha) > 0:
            msg = "Number of scans not divisible by number of channels, inconsistent array size, returning.."
            raise ValueError(msg)
        
        nfid = int(nscan / ncha)
        
        nparr = np.zeros([ncha, nfid, npts], np.complex)
        
        for j in range(nfid):
            for i in range(ncha):
                scan = self.twix.scans[i+j*ncha]
                icha = scan.channel_id
                nparr[icha, j, :] = np.array(scan.data)

        return nparr


    def get_data_numpy_scan_channel_order(self):
        """
        Sort all scans into numpy array in [fid, channel_id, spectral points] order.
        
        This does not require unique dimensions. It does require that total 
        number of scans divided by number of channels is an integer. It is
        assumed that all channels for a given FID follow one after the other
        in the scan list.
        
        """
        npts  = self.twix.scans[0].samples_in_scan
        nscan = len(self.twix.scans)
        ncha  = self.twix.scans[0].used_channels
        
        if (nscan % ncha) > 0:
            msg = "Number of scans not divisible by number of channels, inconsistent array size, returning.."
            raise ValueError(msg)
        
        nfid = int(nscan / ncha)
        
        nparr = np.zeros([nfid, ncha, npts], np.complex)
        
        for j in range(nfid):
            for i in range(ncha):
                scan = self.twix.scans[i+j*ncha]
                icha = scan.channel_id
                nparr[j, icha, :] = np.array(scan.data)

        return nparr


    def get_data_numpy_rep_channel_scan_order(self):
        """
        Use the ICE loop indices to sort each scan into a numpy array with 
        all 16 dimensions.  This option can not be used if we don't have a
        unique set of ICE indices. We use check_unique_indices() to determine
        if this is the case.  If everything is OK, we return a numpy array,
        if it is not, we return None.
        
        """
        items = ['ide', 'idd', 'idc', 'idb', 'ida','segment', 'phase', 'echo', 'partition', 'slice', 'acquisition', 'line']
        for item in items:
            indx = SCAN_INDICES.index(item)
            if self.dims[indx] > 1:
                msg = "ICE dimension - '"+item+"' is greater than 1, can not create a unique numpy array."
                raise ValueError(msg)

        nrep = self.dims[SCAN_INDICES.index('repetition')]     # number of repetitions, may be 1
        nset = self.dims[SCAN_INDICES.index('set')]            # number of FIDs for spectroscopy
        ncha = self.dims[SCAN_INDICES.index('channel_id')]     # number of channels, may be 1
        
        nparr = np.zeros([nrep, ncha, nset, self.twix.scans[0].samples_in_scan], np.complex)
        
        for scan in self.twix.scans:
            irep = scan.repetition
            iset = scan.set
            icha = scan.channel_id
            nparr[irep,icha,iset,:] = np.array(scan.data)

        return nparr

            

class TwixMultiSort(object):
    
    def __init__(self, twix_obj, meas_index=-1):
        """
        The user creates this object by passing in a TwixMultiRaid object and
        an index for the measurement of interest. The TwixMultiRaid object 
        must contain at least as many measurements as needed to index the 
        requested one. The default index is -1 indicating the last measurement
        in the TwixMultiRaid object. According to Siemens documentation, this
        is the 'real' measurement. All previous measurements are in support of
        the final one.
        
        We create a list of all ICE dimensions for each scan in the requested 
        measurement and run a check on these dims to ensure that they are unique. 
        
        If dims are unique, we can (if asked) return a numpy array will all 
        14 ICE dimensions and let the user make full use of the ICE loop 
        counter organization of the data. The array would look like:
        
        [ide, idd, idc, idb, ... , partition, slice, line, chan, col]
        
        If dims are unique, we can also return a numpy array in this order:
        [ repetition, channel_id, set (averages), spectral points ] but we 
        require that all other dims be equal to 1.
        
        If we don't care if dims unique or not, we can sort data into two
        types of numpy arrays. The first is in [scan order, spectral points]
        and the second is in [ channel_id, set (averages), spectral points]
        order. The second version requires that the number of scans divides 
        evenly in to the number of channels.
        
        """
        msg = ''
        if not isinstance(twix_obj, twix_parser_multi_raid.TwixMultiRaid):
            msg = "Twix object not a TwixRaid object, returning!"
        elif meas_index != -1 and meas_index >= len(twix_obj.measurements) is None:
            msg = "TwixMultiRaid object does not have a measurement number = "+str(meas_index)+", returning!"

        if msg:
            raise ValueError(msg)
        
        self.multi_raid     = twix_obj
        self.meas_index     = meas_index
       
        self.twix           = self.multi_raid.measurements[meas_index]
       
        self.indices_list   = self.create_ice_indices()
        self.indices_unique = self.check_unique_indices()
        self.dims           = self.get_dims()
        

    def get_ice_index(self, iscan):
        """ 
        Return list of ICE loop values in MULTI_INDICES order given an index
        in the self.indices_list attribute. This method is typically used by
        the get_data_numpy() call, so we add an Ellipsis object to the end
        of the index list and convert the list into a tuple so it can be used
        to index a location in the numpy output array for the scan data. 
        
        """
        if iscan > len(self.indices_list):
            msg = "Scan index outside range of indices_list"
            raise ValueError(msg)

        indx = list(self.indices_list[iscan])
        return indx
    

    def create_ice_indices(self):
        """ return list of the dims of each Scan """
        dims = []
         
        for scan in self.twix.scans:
            vals = []
            for attr in MULTI_INDICES:
                vals.append(getattr(scan.scan_header, attr))
            dims.append(vals)
         
        return dims

    
    def get_dims(self):
        """ return list of the max value in each dim, plus samples per scan """

        # transpose the list of lists and check max val in each dimension         
        dims = [max(item)+1 for item in zip(*self.indices_list)]
        
        dims.append(self.twix.scans[0].scan_header.used_channels)
        dims.append(self.twix.scans[0].scan_header.samples_in_scan) 
         
        return dims    
    
    
    def check_unique_indices(self):
        """ uses set to determine if all ice dims are unique """
        tmp = [tuple(item) for item in self.indices_list]
        tmp = set(tmp)
        if len(tmp) == len(self.indices_list):
            return True
        else:
            return False
        
    
    def get_data_numpy_ice_indexed(self):
        """
        Use the ICE loop indices to sort each scan into a numpy array with 
        all 16 dimensions.  This option can not be used if we don't have a
        unique set of ICE indices. We use check_unique_indices() to determine
        if this is the case.  If everything is OK, we return a numpy array,
        if it is not, we return None.
        
        NB. channel_id is not always 0 .. Nchan, sometimes it is an odd 
            assorment of integers, maybe the elements turned on, so we have
            to use an enumeration to fill the icha index
        
        """
        if not self.indices_unique:
            msg = "ICE indices are not unique, can not return in a Loop Counter dimensioned numpy array."
            raise ValueError(msg)
        
        nparr = np.zeros(self.dims, np.complex)
        
        for i,scan in enumerate(self.twix.scans):
            loops = self.get_ice_index(i)
            
            for icha, chan in enumerate(scan.channels):
                loops.append(icha)  # chan[0].channel_id
                loops.append(Ellipsis)
                indx = tuple(loops)
                
                print "List, index = "+str(self.indices_list[i])+"  "+str(indx)
                nparr[indx] = np.array(chan[1])

        return nparr


    def get_data_numpy_scan_order(self):
        """ 
        Return numpy array of all FID data in scan order - no indexing
        
        NB. channel_id is not always 0 .. Nchan, sometimes it is an odd 
            assorment of integers, maybe the elements turned on, so we have
            to use an enumeration to fill the icha index

        """

        ncha = self.twix.scans[0].scan_header.used_channels
        npts = self.twix.scans[0].scan_header.samples_in_scan

        nparr = np.zeros([len(self.twix.scans) * ncha, npts], np.complex)
        
        for i,scan in enumerate(self.twix.scans):
            for j,chan in enumerate(scan.channels):
                nparr[i*ncha + j,:] = np.array(chan[1])

        return nparr


    def get_data_numpy_channel_scan_order(self):
        """
        Sort all scans into numpy array in [channel_id, fid, spectral points] order.
        
        This does not require unique dimensions. It does require that total 
        number of scans divided by number of channels is an integer. It is
        assumed that all channels for a given FID follow one after the other
        in the scan list.

        NB. channel_id is not always 0 .. Nchan, sometimes it is an odd 
            assorment of integers, maybe the elements turned on, so we have
            to use an enumeration to fill the icha index
        
        """
        npts  = self.twix.scans[0].scan_header.samples_in_scan
        nscan = len(self.twix.scans)
        ncha  = self.twix.scans[0].scan_header.used_channels
        
        nparr = np.zeros([ncha, nscan, npts], np.complex)
        
        for i,scan in enumerate(self.twix.scans):
            for j,chan in enumerate(scan.channels):
                nparr[j,i,:] = np.array(chan[1])

        return nparr

 
    def get_data_numpy_scan_channel_order(self):
        """
        Sort all scans into numpy array in [fid, channel_id, spectral points] order.
        
        NB. Right now, this is the order funct_coil_combine module expects
        
        This does not require unique dimensions. It does require that total 
        number of scans divided by number of channels is an integer. It is
        assumed that all channels for a given FID follow one after the other
        in the scan list.

        NB. channel_id is not always 0 .. Nchan, sometimes it is an odd 
            assorment of integers, maybe the elements turned on, so we have
            to use an enumeration to fill the icha index
        
        """
        npts  = self.twix.scans[0].scan_header.samples_in_scan
        nscan = len(self.twix.scans)
        ncha  = self.twix.scans[0].scan_header.used_channels
        
        nparr = np.zeros([nscan, ncha, npts], np.complex)
        
        for i,scan in enumerate(self.twix.scans):
            for j,chan in enumerate(scan.channels):
                nparr[i,j,:] = np.array(chan[1])

        return nparr


    def get_data_numpy_rep_channel_scan_order(self):
        """
        Use the ICE loop indices to sort each scan into a numpy array with 
        all 16 dimensions.  This option can not be used if we don't have a
        unique set of ICE indices. We use check_unique_indices() to determine
        if this is the case.  If everything is OK, we return a numpy array,
        if it is not, we return None.

        NB. channel_id is not always 0 .. Nchan, sometimes it is an odd 
            assorment of integers, maybe the elements turned on, so we have
            to use an enumeration to fill the icha index
        
        """
        items = ['ide', 'idd', 'idc', 'idb', 'ida','segment', 'phase', 'echo', 'partition', 'slice', 'acquisition', 'line']
        for item in items:
            indx = SCAN_INDICES.index(item)
            if self.dims[indx] > 1:
                msg = "ICE dimension - '"+item+"' is greater than 1, can not create a unique numpy array."
                raise ValueError(msg)

        nrep = self.dims[MULTI_INDICES.index('repetition')]     # number of repetitions, may be 1
        nset = self.dims[MULTI_INDICES.index('set')]            # number of FIDs for spectroscopy
        
        ncha = self.twix.scans[0].scan_header.used_channels
        npts = self.twix.scans[0].scan_header.samples_in_scan
        
        nparr = np.zeros([nrep, ncha, nset, npts], np.complex)
        
        for scan in self.twix.scans:
            irep = scan.scan_header.repetition
            iset = scan.scan_header.set
            for icha,chan in enumerate(scan.channels):
                nparr[irep,icha,iset,:] = np.array(chan[1])

        return nparr     



##################   Public functions start here   ##################   




##################   "Private" functions start here   ##################   






if __name__ == "__main__":

#     fname = 'D:\\bsoher\\testdata\\meas_MID00098_FID12966_vb19_svs_se.dat'
#    
#     twix = twix_parser.TwixRaid()
#     twix.populate_from_file(fname)
# 
#     sort = TwixSort(twix)
#     
#     data11 = sort.get_data_numpy_ice_indexed()
#     data12 = sort.get_data_numpy_rep_channel_scan_order()

    fname2 = 'D:\\bsoher\\testdata\\meas_MID00765_FID24095_ve11_svs_se.dat'

    twix2 = twix_parser_multi_raid.TwixMultiRaid()
    twix2.populate_from_file(fname2)

    sort2 = TwixMultiSort(twix2)
    
    # data21 = sort2.get_data_numpy_ice_indexed()
    data2_1 = sort2.get_data_numpy_channel_scan_order()
    data2_2 = sort2.get_data_numpy_rep_channel_scan_order()

    
    bob = 10





