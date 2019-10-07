# Python modules
from __future__ import division
import inspect

# 3rd party modules
import numpy as np

# Our modules
import vespa.analysis.src.block_raw_probep as block_raw_probep
import vespa.analysis.src.block_raw_cmrr_slaser as block_raw_cmrr_slaser
import vespa.analysis.src.block_raw_edit_fidsum as block_raw_edit_fidsum
import vespa.analysis.src.block_prep_fidsum as block_prep_fidsum
import vespa.analysis.src.block_prep_timeseries as block_prep_timeseries
import vespa.analysis.src.block_prep_wbnaa as block_prep_wbnaa

import vespa.common.util.misc  as util_misc
import vespa.common.constants  as common_constants

# Keep 'em in alphabetical order, please, unless you can impose a better
# ordering.


# Returns the phase 0 correction that produces the largest area under real spectrum
def automatic_phasing(freq):
    max_freq = -1e40
    for i in range(0,360):
        phase = np.exp(1j * i * common_constants.DEGREES_TO_RADIANS)
        max_  = np.sum((freq * phase).real)
        if max_ > max_freq:
            max_freq = max_
            max_index = i
    return max_index


def build_area_text(area, rms, plot_label=None):
    txt = ' Area = %1.5g  RMS = %1.5g' % (area, rms)
    if plot_label:
        # used to indicate if area value from Plot A, B, C, D
        txt = plot_label+': '+txt
    return txt


def calculate_area(dimension_size, frequencies, phases, x_left, x_right):
    """ 
    Calculates & returns the selected area.
        
    The param dimension_size is a scalar like data.dims[0].
    The param phases is a tuple of info.ph0 and info.ph1. 
    The params x_left and x_right are translated from event coordinates to 
    native values.
    """
    phase0 = phases[0] * common_constants.DEGREES_TO_RADIANS
    phase1 = phases[1] * common_constants.DEGREES_TO_RADIANS * \
        (np.arange(dimension_size, dtype=float) - (dimension_size / 2))
    phase1 /= dimension_size
    phase  = np.exp(complex(0, 1) * (phase0 + phase1))
    pdata  = (frequencies * phase).real[::-1]

    if x_right >= x_left:
        area = sum(pdata[x_left:x_right + 1])
    else:
        area = sum(pdata[x_right:x_left + 1])

    return area


def custom_tab_names(datasets, count):
    
    if util_misc.is_iterable(datasets):
        dataset = datasets[0]
    else:
        datasets = [datasets,]
        dataset = datasets[0]
        
    if isinstance(dataset.blocks['raw'], block_raw_probep.BlockRawProbep):
        if len(datasets) == 2:
            count += 1
            name1 = "Probe%d.Metab" % count
            name2 = "Probe%d.Water" % count
            names = [name1,name2]
        elif len(datasets) == 1:
            count +=1
            name1 = "FidCsi%d" % count
            names = [name1]
    elif isinstance(dataset.blocks['raw'], block_raw_edit_fidsum.BlockRawEditFidsum):
        count += 1
        name1 = "Edit%d.On"  % count
        name2 = "Edit%d.Off" % count
        name3 = "Edit%d.Sum" % count
        name4 = "Edit%d.Dif" % count
        names = [name1,name2,name3,name4]
    elif isinstance(dataset.blocks['raw'], block_raw_cmrr_slaser.BlockRawCmrrSlaser):

        count += 1
        names  = []
        base   = "CMRR%d."  % count
        iother = 1
        
        for dataset in datasets:
            fname = dataset.blocks['raw'].data_sources[0]
            if ".combine" in fname:
                names.append(base+"Coil")
            elif ".ecc1" in fname:
                names.append(base+"Ecc1")
            elif ".water1" in fname:
                names.append(base+"Water1")
            elif ".metab64" in fname:
                names.append(base+"Metab64")
            elif ".ecc2" in fname:
                names.append(base+"Ecc2")
            elif ".water2" in fname:
                names.append(base+"Water2")
            else:
                names.append(base+"Other"+str(iother))      # typically for MMol Basis dataset, but unknowns too.
                iother += 1
        
    elif isinstance(dataset.blocks['prep'], block_prep_fidsum.BlockPrepFidsum):
        names = []
        for dataset in datasets:
            count += 1
            names.append("Fidsum %d" % count)
    elif isinstance(dataset.blocks['prep'], block_prep_timeseries.BlockPrepTimeseries):
        names = []
        for dataset in datasets:
            count += 1
            names.append("Timeseries %d" % count)
    elif isinstance(dataset.blocks['prep'], block_prep_wbnaa.BlockPrepWbnaa):
        count += 1
        name1 = "Wbnaa %d" % count
        names = [name1]
    else:
        names = []
        for dataset in datasets:
            count += 1
            names.append("Dataset%d" % count)
        
    return names, count

    
    
    
    
    
    


