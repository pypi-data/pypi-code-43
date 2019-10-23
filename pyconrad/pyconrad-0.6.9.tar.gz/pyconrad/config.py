import numpy as np

from pyconrad._classgetter import ClassGetter
import pyconrad

from ._autocomplete_files.autocomplete_conrad import AutoCompleteConrad

_ = pyconrad.ClassGetter(
    'edu.stanford.rsl.conrad.utils',
    'java.beans',
    'java.io',
    'edu.stanford.rsl.conrad.geometry.trajectories'
)


def get_conf() -> AutoCompleteConrad.edu.stanford.rsl.conrad.utils.Configuration:
    from edu.stanford.rsl.conrad.utils import Configuration
    conf = Configuration.getGlobalConfiguration()

    return conf


def get_geometry() -> AutoCompleteConrad.edu.stanford.rsl.conrad.geometry.trajectories.Trajectory:
    from edu.stanford.rsl.conrad.utils import Configuration
    geo = Configuration.getGlobalConfiguration().getGeometry()
    return geo


def get_sino_shape() -> tuple:
    from edu.stanford.rsl.conrad.utils import Configuration
    conf = Configuration.getGlobalConfiguration()
    geo = conf.getGeometry()
    return (geo.getProjectionStackSize(), geo.getDetectorHeight(), geo.getDetectorWidth())


def get_sino_size() -> list:
    return (reversed(get_sino_shape()))


def get_reco_shape() -> tuple:
    from edu.stanford.rsl.conrad.utils import Configuration
    conf = Configuration.getGlobalConfiguration()
    geo = conf.getGeometry()
    return (geo.getReconDimensionZ(), geo.getReconDimensionY(), geo.getReconDimensionX())


def get_reco_size() -> list:
    return [*reversed(get_reco_shape())]


def get_reco_origin() -> tuple:
    from edu.stanford.rsl.conrad.utils import Configuration
    conf = Configuration.getGlobalConfiguration()
    geo = conf.getGeometry()  # type: AutoCompleteConrad.edu.stanford.rsl
    return (geo.getOriginX(), geo.getOriginY(), geo.getOriginZ())


def get_reco_spacing() -> tuple:
    from edu.stanford.rsl.conrad.utils import Configuration
    conf = Configuration.getGlobalConfiguration()
    geo = conf.getGeometry()  # type: AutoCompleteConrad.edu.stanford.rsl
    return (geo.getVoxelSpacingX(), geo.getVoxelSpacingY(), geo.getVoxelSpacingZ())


def set_reco_spacing(spacing):
    from edu.stanford.rsl.conrad.utils import Configuration
    conf = Configuration.getGlobalConfiguration()
    geo = conf.getGeometry()  # type: AutoCompleteConrad.edu.stanford.rsl
    geo.setVoxelSpacingX(spacing[0])
    geo.setVoxelSpacingY(spacing[1])
    geo.setVoxelSpacingZ(spacing[2])


def set_reco_origin(origin):
    from edu.stanford.rsl.conrad.utils import Configuration
    conf = Configuration.getGlobalConfiguration()
    geo = conf.getGeometry()  # type: AutoCompleteConrad.edu.stanford.rsl

    geo.setOriginInWorld(_.PointND([origin[0], origin[1], origin[2]]))


def set_reco_shape(shape):
    from edu.stanford.rsl.conrad.utils import Configuration
    conf = Configuration.getGlobalConfiguration()
    geo = conf.getGeometry()  # type: AutoCompleteConrad.edu.stanford.rsl

    geo.setReconDimensionX(shape[2])
    geo.setReconDimensionY(shape[1])
    geo.setReconDimensionZ(shape[0])


def set_reco_size(size):
    from edu.stanford.rsl.conrad.utils import Configuration
    conf = Configuration.getGlobalConfiguration()
    geo = conf.getGeometry()  # type: AutoCompleteConrad.edu.stanford.rsl

    geo.setReconDimensionX(size[0])
    geo.setReconDimensionY(size[1])
    geo.setReconDimensionZ(size[2])


def center_volume():

    reco_size = get_reco_size()
    spacing = get_reco_spacing()
    origin_in_world = [-(reco_size[i] - 1.0) / 2. * spacing[i]
                       for i in range(3)]
    get_geometry().setOriginInWorld(_.PointND(origin_in_world))


def get_projection_matrices() -> np.ndarray:
    projMats = pyconrad.config.get_geometry().getProjectionMatrices()
    numProjs = pyconrad.config.get_geometry().getProjectionStackSize()
    projMatsArray = np.empty((numProjs, 3, 4), np.float32)
    idx = 0

    for p in range(numProjs):
        matrix = projMats[p].computeP()
        for row in range(3):
            for col in range(4):
                projMatsArray[p, row, col] = np.float32(
                    matrix.getElement(row, col))
    return projMatsArray
