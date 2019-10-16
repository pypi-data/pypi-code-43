from typing import Union, List

import vtk
import vmi
import numpy as np

import tempfile
import pathlib
import shutil


def pdExport_STL(pd: vtk.vtkPolyData, filename: str):
    with tempfile.TemporaryDirectory() as p:
        p = pathlib.Path(p) / '.stl'
        w = vtk.vtkSTLWriter()
        w.SetInputData(pd)
        w.SetFileName(str(p))
        w.SetFileTypeToBinary()
        w.Update()
        shutil.copyfile(p, filename)


def pdPolyline(pts: List[Union[np.ndarray, List[float]]], closed=False):
    if len(pts) < 2:
        return

    points = vtk.vtkPoints()
    for pt in pts:
        points.InsertNextPoint([pt[0], pt[1], pt[2]])

    ids = vtk.vtkIdList()

    for i in range(points.GetNumberOfPoints() - 1):
        ids.InsertNextId(i)

    if closed:
        ids.InsertNextId(0)

    lines = vtk.vtkCellArray()
    lines.InsertNextCell(ids)

    pd = vtk.vtkPolyData()
    pd.SetPoints(points)
    pd.SetLines(lines)
    return pd


def pdPolyline_Regular(radius: float, center: Union[np.ndarray, List[float]], normal: Union[np.ndarray, List[float]],
                       resolution: float = 120) -> vtk.vtkPolyData:
    polyline = vtk.vtkRegularPolygonSource()
    polyline.SetCenter(*list(center[:3]))
    polyline.SetNormal(*list(normal[:3]))
    polyline.SetRadius(radius)
    polyline.SetNumberOfSides(resolution)
    polyline.SetGeneratePolygon(0)
    polyline.Update()
    return polyline.GetOutput()


def pdPolygon_Regular(radius: float, center: Union[np.ndarray, List[float]], normal: Union[np.ndarray, List[float]],
                      resolution: float = 120) -> vtk.vtkPolyData:
    polyline = vtk.vtkRegularPolygonSource()
    polyline.SetCenter(*list(center[:3]))
    polyline.SetNormal(*list(normal[:3]))
    polyline.SetRadius(radius)
    polyline.SetNumberOfSides(resolution)
    polyline.SetGeneratePolygon(1)
    polyline.Update()
    return polyline.GetOutput()


def pdSphere(radius: float, center: Union[np.ndarray, List[float]], resolution: float = 120) -> vtk.vtkPolyData:
    source = vtk.vtkSphereSource()
    source.SetCenter(list(center[:3]))
    source.SetRadius(radius)
    source.SetPhiResolution(resolution)
    source.SetThetaResolution(resolution)
    source.Update()
    return source.GetOutput()


def pdExtract_Largest(pd: vtk.vtkPolyData):
    connectivity = vtk.vtkPolyDataConnectivityFilter()
    connectivity.SetInputData(pd)
    connectivity.SetExtractionModeToLargestRegion()
    connectivity.Update()
    return connectivity.GetOutput()


def pdExtract_Closest(pd: vtk.vtkPolyData, closest_point):
    connectivity = vtk.vtkPolyDataConnectivityFilter()
    connectivity.SetInputData(pd)
    connectivity.SetExtractionModeToClosestPointRegion()
    connectivity.SetClosestPoint([closest_point[i] for i in range(3)])
    connectivity.Update()
    return connectivity.GetOutput()


def pdSmoothWindowedSinc(pd: vtk.vtkPolyData, iter_num=20):
    smooth = vtk.vtkWindowedSincPolyDataFilter()
    smooth.SetInputData(pd)
    smooth.SetNumberOfIterations(iter_num)
    smooth.SetPassBand(0.1)
    smooth.SetNonManifoldSmoothing(1)
    smooth.SetNormalizeCoordinates(1)
    smooth.SetFeatureAngle(60)
    smooth.SetBoundarySmoothing(0)
    smooth.SetFeatureEdgeSmoothing(0)
    smooth.Update()
    return smooth.GetOutput()


def pdSmoothLaplacian(pd: vtk.vtkPolyData, iter_num=20):
    smooth = vtk.vtkSmoothPolyDataFilter()
    smooth.SetInputData(pd)
    smooth.SetNumberOfIterations(iter_num)
    smooth.SetConvergence(0)
    smooth.SetRelaxationFactor(0.33)
    smooth.SetFeatureAngle(60)
    smooth.SetBoundarySmoothing(0)
    smooth.SetFeatureEdgeSmoothing(0)
    smooth.Update()
    return smooth.GetOutput()


def pdNormals(pd: vtk.vtkPolyData):
    if pd.GetPointData().GetNormals() is None or pd.GetCellData().GetNormals() is None:
        normals = vtk.vtkPolyDataNormals()
        normals.SetInputData(pd)
        normals.SetComputePointNormals(1)
        normals.SetComputeCellNormals(1)
        normals.Update()
        return normals.GetOutput()
    return pd


def pdTriangle(pd: vtk.vtkPolyData, pass_verts=1, pass_lines=1):
    triangle = vtk.vtkTriangleFilter()
    triangle.SetPassVerts(pass_verts)
    triangle.SetPassLines(pass_lines)
    triangle.SetInputData(pd)
    triangle.Update()
    return triangle.GetOutput()


def pdClip_Implicit(pd: vtk.vtkPolyData, clip_function: vtk.vtkImplicitFunction):
    clip = vtk.vtkClipPolyData()
    clip.SetClipFunction(clip_function)
    clip.SetInputData(pdNormals(pd))
    clip.SetGenerateClippedOutput(1)
    clip.Update()
    return [clip.GetOutput(), clip.GetClippedOutput()]


def pdClip_Pd(pd: vtk.vtkPolyData, clip_pd: vtk.vtkPolyData):
    clip_function = vtk.vtkImplicitPolyDataDistance()
    clip_function.SetInput(pdNormals(clip_pd))
    return pdClip_Implicit(pd, clip_function)


def pdCut_Implicit(pd: vtk.vtkPolyData, cut_function: vtk.vtkImplicitFunction):
    cut = vtk.vtkCutter()
    cut.SetCutFunction(cut_function)
    cut.SetInputData(pdNormals(pd))
    cut.SetGenerateCutScalars(0)
    cut.Update()

    pd = cut.GetOutput()
    pd.GetPointData().DeepCopy(vtk.vtkPolyData().GetPointData())
    pd.GetCellData().DeepCopy(vtk.vtkPolyData().GetCellData())
    return pd


def pdAppend(pds):
    append = vtk.vtkAppendPolyData()
    for pd in pds:
        append.AddInputData(pd)
    append.Update()
    return append.GetOutput()


def pdClean(pd: vtk.vtkPolyData, point_merging=1):
    clean = vtk.vtkCleanPolyData()
    clean.SetInputData(pd)
    clean.SetPointMerging(point_merging)
    clean.Update()
    return clean.GetOutput()


def pdBoolean_Union(pd0: vtk.vtkPolyData, pd1: vtk.vtkPolyData):
    boolean = vtk.vtkLoopBooleanPolyDataFilter()
    boolean.SetOperationToUnion()
    boolean.SetInputData(0, pdNormals(pd0))
    boolean.SetInputData(1, pdNormals(pd1))
    boolean.Update()
    return boolean.GetOutput()


def pdBoolean_Intersection(pd0: vtk.vtkPolyData, pd1: vtk.vtkPolyData):
    boolean = vtk.vtkLoopBooleanPolyDataFilter()
    boolean.SetOperationToIntersection()
    boolean.SetInputData(0, pdNormals(pd0))
    boolean.SetInputData(1, pdNormals(pd1))
    boolean.Update()
    return boolean.GetOutput()


def pdBoolean_Difference(pd0: vtk.vtkPolyData, pd1: vtk.vtkPolyData):
    boolean = vtk.vtkLoopBooleanPolyDataFilter()
    boolean.SetOperationToDifference()
    boolean.SetInputData(0, pdNormals(pd0))
    boolean.SetInputData(1, pdNormals(pd1))
    boolean.Update()
    return boolean.GetOutput()


def pdRayCast_Pt(pt: Union[np.ndarray, List[float]], vt: Union[np.ndarray, List[float]], base: vtk.vtkPolyData,
                 base_kd=None, base_obb=None):
    pt = np.array([pt[i] for i in range(3)])
    vt = np.array([vt[i] for i in range(3)])
    vt /= np.linalg.norm(vt)

    bnd = base.GetBounds()
    d1 = np.array([bnd[1] - bnd[0], bnd[3] - bnd[2], bnd[5] - bnd[4]])
    d1 = np.linalg.norm(d1)

    if base_kd is None:
        base_kd = vtk.vtkKdTreePointLocator()
        base_kd.SetDataSet(base)
        base_kd.BuildLocator()

    cid = base_kd.FindClosestPoint(pt)

    cpt = np.array(base.GetPoint(cid))
    d2 = np.linalg.norm(pt - cpt)

    pt_last = pt + (d1 + d2) * vt

    if base_obb is None:
        base_obb = vtk.vtkOBBTree()
        base_obb.SetDataSet(base)
        base_obb.BuildLocator()

    pts = vtk.vtkPoints()
    base_obb.IntersectWithLine(pt, pt_last, pts, None)

    if pts.GetNumberOfPoints() > 0:
        return np.linalg.norm(pt - np.array(pts.GetPoint(0)))
    else:
        return None


def pdRayCast_Pd(pd: vtk.vtkPolyData, vt, base: vtk.vtkPolyData, default_origin):
    vt = np.array([vt[i] for i in range(3)])
    vt /= np.linalg.norm(vt)

    base_kd = vtk.vtkKdTreePointLocator()
    base_kd.SetDataSet(base)
    base_kd.BuildLocator()

    base_obb = vtk.vtkOBBTree()
    base_obb.SetDataSet(base)
    base_obb.BuildLocator()

    out = vtk.vtkPolyData()
    out.DeepCopy(pd)

    for i in range(pd.GetNumberOfPoints()):
        pt = pd.GetPoint(i)
        d = pdRayCast_Pt(pt, vt, base, base_kd, base_obb)

        if d is None:
            pt = vmi.ptOnPlane(pt, default_origin, vt)
        else:
            pt = pt + d * vt
        out.GetPoints().SetPoint(i, pt)

    return out


def pdOBB_Pts(pts):
    if isinstance(pts, vtk.vtkPolyData):
        pts = pts.GetPoints()
    elif not isinstance(pts, vtk.vtkPoints):
        points = vtk.vtkPoints()
        for pt in pts:
            points.InsertNextPoint([pt[0], pt[1], pt[2]])
        pts = points

    if pts.GetNumberOfPoints() > 0:
        args = {'origin': [0, 0, 0], 'axis': [[0, 0, 0], [0, 0, 0], [0, 0, 0]], 'size': [0, 0, 0]}
        vtk.vtkOBBTree().ComputeOBB(pts, args['origin'], args['axis'][0], args['axis'][1], args['axis'][2],
                                    args['size'])

        args['center'] = args['origin']
        for i in args:
            args[i] = np.array(args[i])

        for j in range(3):
            args['axis'][j] = args['axis'][j] / np.linalg.norm(args['axis'][j])
            args['center'] = [args['center'][i] + 0.5 * args['size'][j] * args['axis'][j][i] for i in range(3)]
        return args


def pdOffset_Normals(pd: vtk.vtkPolyData, d):
    pd = pdNormals(pd)
    pd_out = vtk.vtkPolyData()
    pd_out.DeepCopy(pd)

    normals = pd.GetPointData().GetNormals()
    for i in range(pd.GetNumberOfPoints()):
        n = [0, 0, 0]
        normals.GetTypedTuple(i, n)
        n = np.array(n)
        n /= np.linalg.norm(n)

        pt = np.array(pd.GetPoint(i)) + d * n
        pd_out.GetPoints().SetPoint(i, pt)
    return pd_out


def pdMatrix(pd: vtk.vtkPolyData, matrix: vtk.vtkMatrix4x4):
    t = vtk.vtkTransform()
    t.SetMatrix(matrix)
    return pdTransform(pd, t)


def pdTransform(pd: vtk.vtkPolyData, t: vtk.vtkTransform):
    tf = vtk.vtkTransformPolyDataFilter()
    tf.SetTransform(t)
    tf.SetInputData(pd)
    tf.Update()
    return tf.GetOutput()


def pdBorder_Pts(pd: vtk.vtkPolyData):
    ph = vmi.cgPh_Pd(pd)
    return vmi.cgBorder_Pts(ph)
