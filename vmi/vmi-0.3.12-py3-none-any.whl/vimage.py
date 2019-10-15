import tempfile
import pathlib
import math
from typing import Union, Optional, List

import SimpleITK as sitk
import vtk
import vmi
import numpy as np
import numba

sitk.ProcessObject_SetGlobalWarningDisplay(False)

UC = sitk.sitkUInt8
SS = sitk.sitkInt16
SI = sitk.sitkInt32
F = sitk.sitkFloat32
D = sitk.sitkFloat64


def imSITKScalar_VTK(t: int) -> int:
    """
    转换图像体素类型

    :param t: UC - unsigned char, SS - signed short, SI - signed int, F - float, D - double
    :return: vtk.VTK_UNSIGNED_CHAR, vtk.VTK_SHORT, vtk.VTK_INT, vtk.VTK_FLOAT, vtk.VTK_DOUBLE
    """
    return {vtk.VTK_UNSIGNED_CHAR: UC,
            vtk.VTK_SHORT: SS,
            vtk.VTK_INT: SI,
            vtk.VTK_FLOAT: F,
            vtk.VTK_DOUBLE: D}[t]


def imVTKScalar_SITK(t: int) -> int:
    """
    转换图像体素类型

    :param t: vtk.VTK_UNSIGNED_CHAR, vtk.VTK_SHORT, vtk.VTK_INT, vtk.VTK_FLOAT, vtk.VTK_DOUBLE
    :return: UC - unsigned char, SS - signed short, SI - signed int, F - float, D - double
    """
    return {UC: vtk.VTK_UNSIGNED_CHAR,
            SS: vtk.VTK_SHORT,
            SI: vtk.VTK_INT,
            F: vtk.VTK_FLOAT,
            D: vtk.VTK_DOUBLE}[t]


def imSITK_VTK(image: Union[vtk.vtkImageData, sitk.Image], output_scalar_type=SS) -> sitk.Image:
    """
    转换图像数据类型

    :param image: 输入vtkImageData
    :param output_scalar_type: 输出图像的体素类型
    :return: 输出SimpleITK.Image
    """
    with tempfile.TemporaryDirectory() as p:
        p = pathlib.Path(p) / '.nii'

        if isinstance(image, vtk.vtkImageData):
            w = vtk.vtkNIFTIImageWriter()
            w.SetFileName(str(p))
            w.SetInputData(image)
            w.Update()
        else:
            w = sitk.ImageFileWriter()
            w.SetFileName(str(p))
            w.SetImageIO('NiftiImageIO')
            w.Execute(image)

        r = sitk.ImageFileReader()
        r.SetFileName(str(p))
        r.SetImageIO('NiftiImageIO')
        r.SetOutputPixelType(output_scalar_type)
        return r.Execute()


def imVTK_SITK(image: Union[sitk.Image, vtk.vtkImageData], data_scalar_type=vtk.VTK_INT) -> vtk.vtkImageData:
    """
    转换图像数据类型

    :param image: 输入SimpleITK.Image
    :param data_scalar_type: 输出图像的体素类型
    :return: 输出vtkImageData
    """
    with tempfile.TemporaryDirectory() as p:
        p = pathlib.Path(p) / '.nii'

        if isinstance(image, vtk.vtkImageData):
            w = vtk.vtkNIFTIImageWriter()
            w.SetFileName(str(p))
            w.SetInputData(image)
            w.Update()
        else:
            w = sitk.ImageFileWriter()
            w.SetFileName(str(p))
            w.SetImageIO('NiftiImageIO')
            w.Execute(image)

        r = vtk.vtkNIFTIImageReader()
        r.SetFileName(str(p))
        r.SetDataScalarType(data_scalar_type)
        r.Update()
        return r.GetOutput()


def imArray_VTK(image: vtk.vtkImageData) -> np.ndarray:
    """
    转换图像数据类型

    :param image: 输入vtkImageData
    :return: 输出ndarray
    """
    return sitk.GetArrayFromImage(imSITK_VTK(image))


def imVTK_Array(ary: np.ndarray, origin: Union[np.ndarray, List[float]],
                spacing: Union[np.ndarray, List[float]]) -> vtk.vtkImageData:
    """
    转换图像数据类型

    :param origin: 图像原点
    :param spacing: 图像体素间距
    :param extent: 图像数据坐标范围
    :param ary: 输入图像体素值ndarray
    :return: 输出图像vtkImageData
    """
    if ary.ndim == 3:
        ext = [0, ary.shape[2] - 1, 0, ary.shape[1] - 1, 0, ary.shape[0] - 1]
    elif ary.ndim == 2:
        ext = [0, ary.shape[1] - 1, 0, ary.shape[0] - 1, 0, 0]
    elif ary.ndim == 1:
        ext = [0, ary.shape[0] - 1, 0, 0, 0, 0]
    else:
        ext = [0, 0, 0, 0, 0, 0]

    types = {'uint16': vtk.VTK_UNSIGNED_CHAR, 'int32': vtk.VTK_INT, 'float32': vtk.VTK_FLOAT, 'float64': vtk.VTK_DOUBLE}

    image = imVTK_SITK(sitk.GetImageFromArray(ary), data_scalar_type=types[str(ary.dtype)])
    image.SetOrigin(origin[0], origin[1], origin[2])
    image.SetSpacing(spacing[0], spacing[1], spacing[2])
    image.SetExtent(ext[0], ext[1], ext[2], ext[3], ext[4], ext[5])
    return image


def imOrigin(image: vtk.vtkImageData) -> np.ndarray:
    """返回图像原点[x, y, z]"""
    return np.array(image.GetOrigin())


def imBounds(image: vtk.vtkImageData) -> np.ndarray:
    """返回图像边界[xmin, xmax, ymin, ymax, zmin, zmax]"""
    return np.array(image.GetBounds())


def imCenter(image: vtk.vtkImageData) -> np.ndarray:
    """返回图像中心点[x, y, z]"""
    return np.array(image.GetCenter())


def imDimensions(image: vtk.vtkImageData) -> np.ndarray:
    """返回图像数据维数(整数)"""
    return np.array(image.GetDimensions())


def imExtent(image: vtk.vtkImageData, bounds: Union[np.ndarray, List[float]] = None) -> np.ndarray:
    """
    返回图像数据范围(整数)，如果设置了边界范围bounds则输出边界内的数据范围

    :param image: 输入图像
    :param bounds: 边界范围[xmin, xmax, ymin, ymax, zmin, zmax]
    :return: 数据范围[imin, imax, jmin, jmax, kmin, kmax]
    """
    if bounds is not None:
        ori, spc, ext = imOrigin(image), imSpacing(image), imExtent(image)
        first, last = [bounds[0], bounds[2], bounds[4]], [bounds[1], bounds[3], bounds[5]]
        for i in range(3):
            f = int((first[i] - ori[i]) / spc[i])
            l = int((last[i] - ori[i]) / spc[i] + 1)
            if f > ext[2 * i]:
                ext[2 * i] = f
            if l < ext[2 * i + 1]:
                ext[2 * i + 1] = l
        return ext
    return np.array(image.GetExtent())


def imSpacing(image: vtk.vtkImageData) -> np.ndarray:
    """
    返回图像沿三个坐标轴方向的体素间距

    :param image: 输入图像
    :return: [spacing_x, spacing_y, spacing_z]
    """
    return np.array(image.GetSpacing())


def imSpacing_Vt(image: vtk.vtkImageData, vt: np.ndarray = None) -> float:
    """
    返回图像的体素间距，如果设置了方向vt则返回沿该方向的体素间距

    :param image: 输入图像
    :param vt: 任意方向[x, y, z]
    :return: 各方向体素间距[dx, dy, dz]，或沿vt方向体素间距dvt
    """
    spc, vt = imSpacing(image), np.array([vt[0], vt[1], vt[2]])
    spc = vmi.vtOnVector(spc, vt)
    return np.linalg.norm(spc)


def imSize(image: vtk.vtkImageData) -> np.ndarray:
    """
    返回图像包围盒沿三个坐标轴方向的尺度

    :param image: 输入图像
    :return: [size_x, size_y, size_z]
    """
    bnd = imBounds(image)
    return np.array([bnd[1] - bnd[0], bnd[3] - bnd[2], bnd[5] - bnd[4]])


def imSize_Vt(image: vtk.vtkImageData, vt: np.ndarray) -> float:
    """
    返回图像包围盒沿方向vt的尺度

    :param image: 输入图像
    :param vt: 任意方向[x, y, z]
    :return: 各方向图像包围和边长[sx, sy, sz]，或沿vt方向体素间距svt
    """
    size, vt = imSize(image), np.array([vt[0], vt[1], vt[2]])
    size = vmi.vtOnVector(size, vt)
    return np.linalg.norm(size)


def imStencil_PolyData(pd: vtk.vtkPolyData, output_origin: Union[np.ndarray, List[float]],
                       output_spacing: Union[np.ndarray, List[float]],
                       output_extent: Union[np.ndarray, List[float]]) -> vtk.vtkImageData:
    """
    将面网格数据pd转化为图像模板数据，再转化为图像数据vtkImageData，网格内体素值为255，网格外体素值为0

    :param pd: 输入面网格数据
    :param output_extent: 输出数据范围[imin, imax, jmin, jmax, kmin, kmax]
    :param output_spacing: 输出体素间距[dx, dy, dz]
    :param output_origin: 输出图像原点[x, y, z]
    :return: 图像模板数据vtkImageData
    """
    stencil = vtk.vtkPolyDataToImageStencil()
    stencil.SetInputData(pd)
    stencil.SetOutputOrigin([output_origin[0], output_origin[1], output_origin[2]])
    stencil.SetOutputSpacing([output_spacing[0], output_spacing[1], output_spacing[2]])
    stencil.SetOutputWholeExtent([output_extent[0], output_extent[1], output_extent[2],
                                  output_extent[3], output_extent[4], output_extent[5]])
    stencil.Update()

    image = vtk.vtkImageStencilToImage()
    image.SetInputData(stencil.GetOutput())
    image.SetOutputScalarTypeToUnsignedChar()
    image.SetInsideValue(255)
    image.SetOutsideValue(0)
    image.Update()
    return image.GetOutput()


def imValue(image: vtk.vtkImageData, ijk: List[int] = None, value: float = None, component: int = 0) -> float:
    """
    获得体素值

    :param image: 输入图像
    :param ijk: 体素值数据坐标
    :param value: 改写体素值
    :param component: 体素值是向量时的元素位置，默认为0
    :return: 体素值
    """
    if value is not None:
        image.SetScalarComponentFromDouble(ijk[0], ijk[1], ijk[2], component, value)
        image.Modified()
    return image.GetScalarComponentAsDouble(ijk[0], ijk[1], ijk[2], component)


def imGradientAnisotropicDiffusion(image: vtk.vtkImageData) -> vtk.vtkImageData:
    stype = image.GetScalarType()
    origin = imOrigin(image)
    image = imSITK_VTK(image, F)
    image = sitk.GradientAnisotropicDiffusion(image)
    image = imVTK_SITK(image, stype)
    image.SetOrigin(list(origin))
    return image


def imResample_Isotropic(image: vtk.vtkImageData) -> vtk.vtkImageData:
    """
    各项同性重采样，将图像各个方向不均匀的体素间距均匀化，输出立方体体素体积不变

    :param image: 输入图像
    :return: 输出重采样图像
    """
    origin = imOrigin(image)
    spc = imSpacing(image)
    isospc = (spc[0] * spc[1] * spc[2]) ** (1 / 3)

    itkimage: sitk.Image = imSITK_VTK(image, F)

    smooth = sitk.RecursiveGaussianImageFilter()
    smooth.SetDirection(0)
    smooth.SetSigma(isospc)
    itkimage = smooth.Execute(itkimage)

    smooth = sitk.RecursiveGaussianImageFilter()
    smooth.SetDirection(1)
    smooth.SetSigma(isospc)
    itkimage = smooth.Execute(itkimage)

    size = itkimage.GetSize()
    dx = size[0] * spc[0] / isospc
    dy = size[1] * spc[1] / isospc
    dz = size[2] * spc[2] / isospc

    resample = sitk.ResampleImageFilter()
    resample.SetTransform(sitk.Transform())
    resample.SetInterpolator(sitk.sitkLinear)
    resample.SetDefaultPixelValue(-1024)
    resample.SetOutputSpacing([isospc, isospc, isospc])
    resample.SetOutputOrigin(itkimage.GetOrigin())
    resample.SetOutputDirection(itkimage.GetDirection())
    resample.SetSize([int(dx), int(dy), int(dz)])
    itkimage = resample.Execute(itkimage)

    itkimage = imSITK_VTK(itkimage, imSITKScalar_VTK(image.GetScalarType()))
    vtkimage = imVTK_SITK(itkimage)
    vtkimage.SetOrigin(origin)
    return vtkimage


def imIsosurface(image: vtk.vtkImageData, isovalue: Union[int, float]) -> vtk.vtkPolyData:
    """
    提取图像等值面三维重建为面网格数据
    
    :param image: 输入图像
    :param isovalue: 等体素值
    :return: 三维面网格数据
    """
    fe3 = vtk.vtkFlyingEdges3D()
    fe3.SetInputData(image)
    fe3.SetValue(0, isovalue)
    fe3.SetComputeNormals(1)
    fe3.SetComputeGradients(0)
    fe3.SetComputeScalars(0)
    fe3.Update()

    pd = vtk.vtkPolyData()
    pd.SetPoints(fe3.GetOutput().GetPoints())
    pd.SetPolys(fe3.GetOutput().GetPolys())
    return vmi.pdNormals(pd)


def imReslice(image: vtk.vtkImageData,
              cs: Optional[vmi.CS4x4] = None,
              size: Union[np.ndarray, List[float]] = None,
              back_scalar: Union[int, float] = 0) -> vtk.vtkImageData:
    """
    图像重采样

    :param image: 输入图像
    :param cs: 输出图像的坐标系
    :param size: 输出图像的尺度
    :param output_origin: 输出图像在新坐标系下的原点坐标
    :param back_scalar: 输出体素的背景值
    :return: 输出重采样图像
    """
    if cs is None:
        cs = vmi.CS4x4()

    if size is None:
        size = [vmi.imSize_Vt(image, cs.axis(0)),
                vmi.imSize_Vt(image, cs.axis(1)),
                vmi.imSize_Vt(image, cs.axis(2))]

    spc = [vmi.imSpacing_Vt(image, cs.axis(0)),
           vmi.imSpacing_Vt(image, cs.axis(1)),
           vmi.imSpacing_Vt(image, cs.axis(2))]

    ext = [0, math.ceil(size[0] / spc[0]),
           0, math.ceil(size[1] / spc[1]),
           0, math.ceil(size[2] / spc[2])]

    reslice = vtk.vtkImageReslice()
    reslice.SetInputData(image)
    reslice.SetInterpolationModeToCubic()
    reslice.SetResliceAxes(cs.mat4x4())
    reslice.SetOutputOrigin([0, 0, 0])
    reslice.SetOutputSpacing(spc)
    reslice.SetOutputExtent(ext)
    reslice.SetBackgroundLevel(back_scalar)
    reslice.Update()

    return reslice.GetOutput()


def imReslice_Blend(image: vtk.vtkImageData,
                    cs: Optional[vmi.CS4x4] = None,
                    size: Union[np.ndarray, List[float]] = None,
                    back_scalar: Union[int, float] = 0,
                    scalar_mode: str = 'mean',
                    scalar_min: Union[int, float] = None,
                    scalar_max: Union[int, float] = None) -> vtk.vtkImageData:
    """
    图像重采样，并沿输出坐标系的z轴方向混叠

    :param image: 输入图像
    :param cs: 输出图像的坐标系
    :param size: 输出图像的尺度
    :param back_scalar: 输出体素的背景值
    :param scalar_mode: mean - 平均体素值（默认） max - 最大体素值 min - 最小体素值
    :param scalar_min: 混叠体素最小值
    :param scalar_max: 混叠体素最大值
    :return: 输出重采样图像
    """

    @numba.jit(nopython=True)
    def blend(ary: np.ndarray, scalar_min=None, scalar_max=None):
        ary = ary.copy()

        # 沿z方向累加大于minimum的体素，取平均值
        for j in range(ary.shape[1]):
            for i in range(ary.shape[2]):
                voxels = []
                for k in range(ary.shape[0]):
                    if scalar_min is not None and ary[k][j][i] < scalar_min:
                        continue
                    elif scalar_max is not None and ary[k][j][i] > scalar_max:
                        continue
                    else:
                        voxels.append(ary[k][j][i])

                if len(voxels):
                    if scalar_mode == 'mean':
                        ary[0][j][i] = np.mean(np.array(voxels))
                    elif scalar_mode == 'max':
                        ary[0][j][i] = np.max(np.array(voxels))
                    elif scalar_mode == 'min':
                        ary[0][j][i] = np.min(np.array(voxels))
                    else:
                        ary[0][j][i] = np.mean(np.array(voxels))
                else:
                    ary[0][j][i] = back_scalar

        return ary[0]

    image = imReslice(image, cs, size, back_scalar=back_scalar)
    ary = vmi.imArray_VTK(image)
    ary = blend(ary, scalar_min, scalar_max)

    image = vmi.imVTK_Array(ary, vmi.imOrigin(image), vmi.imSpacing(image))

    return image
