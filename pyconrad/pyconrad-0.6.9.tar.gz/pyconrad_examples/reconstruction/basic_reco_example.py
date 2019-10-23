
import pyconrad
import pyconrad.config


def project(volume):
    volume_cl = _.OpenCLGrid3D(volume)
    projector = _.ConeBeamProjector()
    sino = _.OpenCLGrid3D(_.Grid3D(*pyconrad.config.get_sino_size()))
    projector.fastProjectRayDrivenCL(sino, volume_cl)
    return sino


def back_project(sino):
    back_projector = _.ConeBeamBackprojector()
    return back_projector.backprojectPixelDrivenCL(sino)


pyconrad.setup_pyconrad(max_ram='8G', dev_dirs=[
                        '/localhome/local/projects/CONRAD/'])
pyconrad.start_gui()

_ = pyconrad.ClassGetter(
    'edu.stanford.rsl.conrad.phantom',
    'edu.stanford.rsl.tutorial.cone',
    'edu.stanford.rsl.conrad.utils',
    'edu.stanford.rsl.conrad.data.numeric.opencl'
)

phantom = _.NumericalSheppLogan3D(
    *pyconrad.config.get_reco_size()).getNumericalSheppLoganPhantom()
phantom.show('Phantom')

sino = project(phantom)
sino.show('Sinogram')

# import numpy as np
# dot_phantom = np.zeros(pyconrad.config.get_reco_shape())
# # Let's place a small dot in the middle!
# dot_phantom[150, 150, 150] = 1
# dot_phantom = _.Grid3D.from_numpy(dot_phantom)
# sino = project(dot_phantom)


cosine_filter = _.edu.stanford.rsl.conrad.filtering.CosineWeightingTool()
cosine_filter.configure()
filtered_sino = _.ImageUtil.applyFilterInParallel(sino, cosine_filter, True)
filtered_sino.show('Cosine filtered')

# Parker weights missing

filter = _.edu.stanford.rsl.conrad.filtering.rampfilters.SheppLoganRampFilter()
filter.configure()
filtertool = _.edu.stanford.rsl.conrad.filtering.RampFilteringTool()
filtertool.setRamp(filter)
filtered_sino = _.ImageUtil.applyFilterInParallel(filtered_sino, filtertool, True)
filtered_sino.show('Ramp filtered')

reconstruction = back_project(sino)
reconstruction.show('Unfiltered Reconstruction')

reconstruction = back_project(filtered_sino)
reconstruction.show('Filtered Reconstruction')
