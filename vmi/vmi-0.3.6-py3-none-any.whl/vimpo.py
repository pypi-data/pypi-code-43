import tempfile
import pathlib
# import itk
import SimpleITK as sitk
import vtk
import vmi

UC = sitk.sitkUInt8
SS = sitk.sitkInt16
F = sitk.sitkFloat32
D = sitk.sitkFloat64


def toITKType(t):
    return {vtk.VTK_UNSIGNED_CHAR: UC,
            vtk.VTK_SHORT: SS,
            vtk.VTK_FLOAT: F,
            vtk.VTK_DOUBLE: D}[t]


def toVTKType(t):
    return {UC: vtk.VTK_UNSIGNED_CHAR,
            SS: vtk.VTK_SHORT,
            F: vtk.VTK_FLOAT,
            D: vtk.VTK_DOUBLE}[t]


def toITKImage(image, tpixel=SS):
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
        r.SetOutputPixelType(tpixel)
        return r.Execute()


def toVTKImage(itkimage):
    with tempfile.TemporaryDirectory() as p:
        p = pathlib.Path(p) / '.nii'

        w = sitk.ImageFileWriter()
        w.SetFileName(str(p))
        w.SetImageIO('NiftiImageIO')
        w.Execute(itkimage)

        r = vtk.vtkNIFTIImageReader()
        r.SetFileName(str(p))
        r.Update()
        return r.GetOutput()


def imOrigin(vtkimage):
    return list(vtkimage.GetOrigin())


def imBounds(vtkimage):
    return list(vtkimage.GetBounds())


def imCenter(vtkimage):
    return list(vtkimage.GetCenter())


def imDimensions(vtkimage):
    return list(vtkimage.GetDimensions())


def imExtent(vtkimage, bounds=None):
    if bounds is not None:
        ori, spc, ext = imOrigin(vtkimage), imSpacing(vtkimage), imExtent(vtkimage)
        first, last = [bounds[0], bounds[2], bounds[4]], [bounds[1], bounds[3], bounds[5]]
        for i in range(3):
            f = int((first[i] - ori[i]) / spc[i])
            l = int((last[i] - ori[i]) / spc[i] + 1)
            if f > ext[2 * i]:
                ext[2 * i] = f
            if l < ext[2 * i + 1]:
                ext[2 * i + 1] = l
        return ext
    return list(vtkimage.GetExtent())


def imSpacing(vtkimage, normal=None):
    if normal is not None:
        n3, spc = [abs(_) for _ in vmi.normalized3(normal)], imSpacing(vtkimage)
        return n3[0] * spc[0] + n3[1] * spc[1] + n3[2] * spc[2]
    return list(vtkimage.GetSpacing())


def imLength(vtkimage, normal=None):
    if normal is not None:
        n3, lth = [abs(_) for _ in vmi.normalized3(normal)], imLength(vtkimage)
        return n3[0] * lth[0] + n3[1] * lth[1] + n3[2] * lth[2]
    bnd = imBounds(vtkimage)
    return [bnd[1] - bnd[0], bnd[3] - bnd[2], bnd[5] - bnd[4]]


def imStencil(vtkimage, polydata):
    stencil = vtk.vtkPolyDataToImageStencil()
    stencil.SetInputData(polydata)
    stencil.SetOutputOrigin(imOrigin(vtkimage))
    stencil.SetOutputSpacing(imSpacing(vtkimage))
    stencil.SetOutputWholeExtent(imExtent(vtkimage))
    stencil.Update()
    return stencil.GetOutput()


def imIterator(vtkimage, ext=None, stencil=None):
    it = vtk.vtkImagePointIterator()
    it.Initialize(vtkimage, ext, stencil)
    return it


def imValue(vtkimage, ijk=None, value=None, m=0):
    if value is not None:
        vtkimage.SetScalarComponentFromDouble(ijk[0], ijk[1], ijk[2], m, value)
        vtkimage.Modified()
    return vtkimage.GetScalarComponentAsDouble(ijk[0], ijk[1], ijk[2], m)


def imResample(vtkimage, origin, extent, spacing):
    resample = vtk.vtkImageReslice()
    resample.SetInputData(vtkimage)
    resample.SetInterpolationModeToCubic()
    resample.SetOutputOrigin(origin)
    resample.SetOutputExtent(extent)
    resample.SetOutputSpacing(spacing)
    resample.Update()
    return resample.GetOutput()


def imResampleIsotropic(vtkimage: vtk.vtkImageData):
    spc = imSpacing(vtkimage)
    isospc = (spc[0] * spc[1] * spc[2]) ** (1 / 3)

    itkimage: sitk.Image = toITKImage(vtkimage, F)

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
    resample.SetDefaultPixelValue(-3071)
    resample.SetOutputSpacing([isospc, isospc, isospc])
    resample.SetOutputOrigin(itkimage.GetOrigin())
    resample.SetOutputDirection(itkimage.GetDirection())
    resample.SetSize([int(dx), int(dy), int(dz)])
    itkimage = resample.Execute(itkimage)

    itkimage = toITKImage(itkimage, toITKType(vtkimage.GetScalarType()))
    return toVTKImage(itkimage)


def poIsosurface(vtkimage: vtk.vtkImageData, isovalue):
    fe3 = vtk.vtkFlyingEdges3D()
    fe3.SetInputData(vtkimage)
    fe3.SetValue(0, isovalue)
    fe3.SetComputeNormals(1)
    fe3.SetComputeGradients(0)
    fe3.SetComputeScalars(0)
    fe3.Update()
    return fe3.GetOutput()


def poExtract_Largest(vtkpoly: vtk.vtkPolyData):
    connectivity = vtk.vtkPolyDataConnectivityFilter()
    connectivity.SetInputData(vtkpoly)
    connectivity.SetExtractionModeToLargestRegion()
    connectivity.Update()
    return connectivity.GetOutput()


def poExtract_Closest(vtkpoly: vtk.vtkPolyData, closest_point):
    connectivity = vtk.vtkPolyDataConnectivityFilter()
    connectivity.SetInputData(vtkpoly)
    connectivity.SetExtractionModeToClosestPointRegion()
    connectivity.SetClosestPoint([closest_point[i] for i in range(3)])
    connectivity.Update()
    return connectivity.GetOutput()


def poSmoothWindowedSinc(vtkpoly: vtk.vtkPolyData, iter_num=20):
    smooth = vtk.vtkWindowedSincPolyDataFilter()
    smooth.SetInputData(vtkpoly)
    smooth.SetNumberOfIterations(iter_num)
    smooth.SetPassBand(0.1)
    smooth.SetNonManifoldSmoothing(1)
    smooth.SetNormalizeCoordinates(1)
    smooth.SetFeatureAngle(60)
    smooth.SetBoundarySmoothing(0)
    smooth.SetFeatureEdgeSmoothing(0)
    smooth.Update()
    return smooth.GetOutput()


def poSmoothLaplacian(vtkpoly: vtk.vtkPolyData, iter_num=20):
    smooth = vtk.vtkSmoothPolyDataFilter()
    smooth.SetInputData(vtkpoly)
    smooth.SetNumberOfIterations(iter_num)
    smooth.SetConvergence(0)
    smooth.SetRelaxationFactor(0.33)
    smooth.SetFeatureAngle(60)
    smooth.SetBoundarySmoothing(0)
    smooth.SetFeatureEdgeSmoothing(0)
    smooth.Update()
    return smooth.GetOutput()


def poNormals(vtkpoly: vtk.vtkPolyData):
    if vtkpoly.GetPointData().GetNormals() is None or vtkpoly.GetCellData().GetNormals() is None:
        normals = vtk.vtkPolyDataNormals()
        normals.SetInputData(vtkpoly)
        normals.SetComputePointNormals(1)
        normals.SetComputeCellNormals(1)
        normals.Update()
        return normals.GetOutput()
    return vtkpoly


def poTriangle(vtkpoly: vtk.vtkPolyData, pass_verts=1, pass_lines=1):
    triangle = vtk.vtkTriangleFilter()
    triangle.SetPassVerts(pass_verts)
    triangle.SetPassLines(pass_lines)
    triangle.SetInputData(vtkpoly)
    triangle.Update()
    return triangle.GetOutput()


def poClip_Implicit(vtkpoly: vtk.vtkPolyData, clip_function: vtk.vtkImplicitFunction):
    clip = vtk.vtkClipPolyData()
    clip.SetClipFunction(clip_function)
    clip.SetInputData(poNormals(vtkpoly))
    clip.Update()
    return [clip.GetOutput(), clip.GetClippedOutput()]


def poClip_PolyData(vtkpoly: vtk.vtkPolyData, clip_poly_data: vtk.vtkPolyData):
    clip_function = vtk.vtkImplicitPolyDataDistance()
    clip_function.SetInput(poNormals(clip_poly_data))
    return poClip_Implicit(vtkpoly, clip_function)


def poAppend(vtkpolys):
    append = vtk.vtkAppendPolyData()
    for vtkpoly in vtkpolys:
        append.AddInputData(vtkpoly)
    append.Update()
    return append.GetOutput()


def poClean(vtkpoly: vtk.vtkPolyData, point_merging=1):
    clean = vtk.vtkCleanPolyData()
    clean.SetInputData(vtkpoly)
    clean.SetPointMerging(point_merging)
    clean.Update()
    return clean.GetOutput()


def poBoolean_Union(vtkpoly0: vtk.vtkPolyData, vtkpoly1: vtk.vtkPolyData):
    boolean = vtk.vtkLoopBooleanPolyDataFilter()
    boolean.SetOperationToUnion()
    boolean.SetInputData(0, poNormals(vtkpoly0))
    boolean.SetInputData(1, poNormals(vtkpoly1))
    boolean.Update()
    return boolean.GetOutput()


def poBoolean_Intersection(vtkpoly0: vtk.vtkPolyData, vtkpoly1: vtk.vtkPolyData):
    boolean = vtk.vtkLoopBooleanPolyDataFilter()
    boolean.SetOperationToIntersection()
    boolean.SetInputData(0, poNormals(vtkpoly0))
    boolean.SetInputData(1, poNormals(vtkpoly1))
    boolean.Update()
    return boolean.GetOutput()


def poBoolean_Difference(vtkpoly0: vtk.vtkPolyData, vtkpoly1: vtk.vtkPolyData):
    boolean = vtk.vtkLoopBooleanPolyDataFilter()
    boolean.SetOperationToDifference()
    boolean.SetInputData(0, poNormals(vtkpoly0))
    boolean.SetInputData(1, poNormals(vtkpoly1))
    boolean.Update()
    return boolean.GetOutput()
