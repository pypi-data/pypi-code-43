# Python modules
from __future__ import division
import copy

# 3rd party modules
import xml.etree.cElementTree as ElementTree
import numpy as np

# Our modules
import vespa.common.util.generic_spectral as util_spectral
import vespa.common.mrs_generic_basis as mrs_generic_basis
import vespa.common.util.xml_ as util_xml



from vespa.common.constants import Deflate

# The _DEFAULT_MODEL are the values used when someone calls
# UserPriorSpectrum.reset_to_default(). See also _DEFAULT_PRIOR below.
_DEFAULT_MODEL = { 
   "checks"            : [True, True, True],
   "values_ppm"        : [2.01, 3.01, 3.22],
   "values_area"       : [0.51, 0.42, 0.40],
   "values_phase"      : [0.00, 0.00, 0.00],
   "values_linewidth"  : [5.0,  5,    5],
   "limits_ppm"        : [0.0,  0.0,  0.0],
   "limits_area"       : [0.0,  0.0,  0.0],
   "limits_phase"      : [0.0,  0.0,  0.0],
   "limits_linewidth"  : [0.0,  0.0,  0.0],
                 }


# _DEFAULT_PRIOR is a slightly different take on the default model. It's 
# calculated once by the function below and then saved in a dict. A copy of
# that dict is returned when someone calls UserPriorSpectrum.default_prior()

def _calculate_default_prior():
    keys = _DEFAULT_MODEL.keys()

    length = len(_DEFAULT_MODEL["checks"])

    lines = [ ]
    for i in range(length):
        d = { }
        for key in keys:
            d[key] = _DEFAULT_MODEL[key][i]

        lines.append(d)

    renames = ( ("checks", "check"),         ("values_ppm", "ppm"), 
                ("values_area", "area"),     ("values_phase", "phase"),
                ("values_linewidth", "lw"),  ("limits_ppm", "ppm_lim"),
                ("limits_area", "area_lim"), ("limits_phase", "phase_lim"), 
                ("limits_linewidth", "lw_lim")
              )

    for d in lines:
        for rename in renames:
            source_key, target_key = rename
            d[target_key] = d[source_key]
            del d[source_key]

    default = { }
    default["source"] = "default"
    default["source_id"] = "default"
    default["line"] = lines

    return default

_DEFAULT_PRIOR = _calculate_default_prior()



class UserPriorSpectrum(mrs_generic_basis.GenericBasis):
    # FIXME PS - need a docstring
    
    # The XML_VERSION enables us to change the XML output format in the future 
    XML_VERSION = "1.0.0"

    def __init__(self, attributes=None):
        mrs_generic_basis.GenericBasis.__init__(self, attributes)

        # _summed caches the value returned by the summed property. We could
        # expose this as an attribute, but wrapping this in a property 
        # emphasizes that it is read-only. It's updated by a call to
        # calculate_spectrum().
        self._summed = None


    @property
    def summed(self):
        """Returns a numpy array containing the sum of the lines checked 
        in the widget.
        """
        return self._summed


    ##### Standard Methods and Properties #####################################

    def deflate(self, flavor=Deflate.ETREE):
        if flavor == Deflate.ETREE:
            # Make my base class do its deflate work
            e = mrs_generic_basis.GenericBasis.deflate(self, flavor)

            # Alter the tag name & XML version info   
            e.tag = "user_prior_spectrum"
            e.set("version", self.XML_VERSION)
            
            return e
        elif flavor == Deflate.DICTIONARY:
            # My base class does all the work
            return mrs_generic_basis.GenericBasis.deflate(self, flavor)


    def inflate(self, source):
        # Make my base class do its inflate work
        mrs_generic_basis.GenericBasis.inflate(self, source)

        # Here I would inflate the attribs that are specific to this class.
        # As it turns out, there are none, so I don't have anything more
        # to do.


    ##### Object Specific Methods and Properties ###########################

    def calculate_spectrum(self, dataset):
        """Given a dataset, calculates the list of spectral lines that are 
        described in the widget and returns them. It also updates the
        value returned by this object's summed property.

        There are two cases where this method will return a single line of 
        zeros, first there are no lines in the widget, second there are lines
        but none have been checked to include.
        """
        all_spectra = [ ]
        checks = self.checks
        areas  = self.values_area       
        ppms   = self.values_ppm        
        phases = self.values_phase      
        lwhz   = self.values_linewidth  
        if areas and any(checks):
            for i in range(len(areas)):
                if checks[i]:
                    apod = 1.0 / (lwhz[i] * 0.34 * np.pi)
                    spectrum = util_spectral.calculate_spectrum(  areas[i], 
                                                                  ppms[i], 
                                                                  phases[i], 
                                                                  dataset, 
                                                                  10000.0, 
                                                                  apod)
                    all_spectra.append(spectrum)
        else:
            zfmult   = dataset.zero_fill_multiplier
            acqdim0  = dataset.raw_dims[0]
            all_spectra = [np.zeros((acqdim0 * zfmult), complex)]

        # Update the sum.
        self._summed = np.sum(all_spectra, axis=0)
            
        return all_spectra


    def reset_to_default(self):
        """Resets model values to the defaults expressed in _DEFAULT_MODEL."""
        for key in _DEFAULT_MODEL:
            setattr(self, key, _DEFAULT_MODEL[key][:])
        

    def default_prior(self):
        """Returns a dict expressing _DEFAULT_MODEL as a prior object 
        appropriate for passing to the inflate() method of GenericBasis
        classes and subclasses.
        """
        # We return a copy so that the recipient can change the values without
        # altering the master copy of _DEFAULT_PRIOR.
        return copy.deepcopy(_DEFAULT_PRIOR)

