# Python modules
from __future__ import division

# 3rd party modules

# Our Modules
import vespa.common.constants               as constants
import vespa.common.rfp_create_slr          as rfp_create_slr
import vespa.common.rfp_create_hs           as rfp_create_hs
import vespa.common.rfp_create_gaussian     as rfp_create_gaussian
import vespa.common.rfp_create_randomized   as rfp_create_randomized
import vespa.common.rfp_create_import       as rfp_create_import
import vespa.common.rfp_interpolate_rescale as rfp_interpolate_rescale
import vespa.common.rfp_root_reflection     as rfp_root_reflection
import vespa.common.rfp_optimal_control_nonselective as rfp_ocn

# The dict below is the equivalent of a C switch statement. In Python, the
# idiom is called dictionary dispatch. This particular dict maps a constant
# (TransformationType.Xxxx["db"]) to a 2-tuple containing the two constructors
# associated with that TransformationType (the transformation ctor and 
# transformation params ctor, respectively). Using a dict like this reduces
# the need for long if/elif/elif/elif... statements that have to be updated
# every time a new TransformationType is added.
# Side note: it would have been a bit more intuitive to use the
# TransformationType constants directly as the dict keys rather than using
# the constant's ["db"] value. But Python does not allow dicts to be used as 
# the keys to other dicts.

constt = constants.TransformationType

CONSTRUCTORS = { 
    constt.CREATE_GAUSSIAN["db"]          : (rfp_create_gaussian.GaussianPulseTransformation,
                                             rfp_create_gaussian.GaussianPulseParameters),                             
    constt.CREATE_HYPERBOLIC_SECANT["db"] : (rfp_create_hs.HyperbolicSecantPulseTransformation,
                                             rfp_create_hs.HyperbolicSecantPulseParameters),
    constt.CREATE_IMPORT["db"]            : (rfp_create_import.CreateImportPulseTransformation,
                                             rfp_create_import.CreateImportPulseParameters),                             
    constt.CREATE_RANDOMIZED["db"]        : (rfp_create_randomized.RandomizedPulseTransformation,
                                             rfp_create_randomized.RandomizedPulseParameters),
    constt.CREATE_SLR["db"]               : (rfp_create_slr.SLRPulseTransformation,
                                             rfp_create_slr.SLRPulseParameters),                             
    constt.INTERPOLATE_RESCALE["db"]      : (rfp_interpolate_rescale.InterpolateRescaleTransformation,
                                             rfp_interpolate_rescale.InterpolateRescaleParameters),
    constt.ROOT_REFLECTION["db"]          : (rfp_root_reflection.RootReflectionTransformation,
                                             rfp_root_reflection.RootReflectionParameters),
    constt.OCN["db"]                      : (rfp_ocn.OCNTransformation,
                                             rfp_ocn.OCNParameters),                             
               }
                        

def create_transformation(type_, parameters=None):
    """A convenience function for creating transformations."""
    type_ = type_["db"]
    assert(type_ in CONSTRUCTORS)
    
    transformation_ctor, parameters_ctor = CONSTRUCTORS[type_]
    
    transform = transformation_ctor()
    if not parameters:
        # create default params
        parameters = parameters_ctor()
    transform.parameters = parameters

    return transform


def transformation_from_element(e):
    """
    Given an ElementTree.Element, figures out what transformation type to
    create, instantiates & populates an instance and returns it. 
    
    """
    
    # 'type' element specifies what kind of transformation to create
    type_ = e.findtext("type")
    
    assert(type_ in CONSTRUCTORS)
    
    transformation_ctor, _ = CONSTRUCTORS[type_]
    transformation = transformation_ctor(e)

    return transformation

