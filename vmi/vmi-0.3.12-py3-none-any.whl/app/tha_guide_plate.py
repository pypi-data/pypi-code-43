import vmi
import vtk
import pydicom
import numpy as np
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from numba import jit


def read_dicom():
    dcmdir = vmi.askDirectory()  # 用户选择文件夹

    if dcmdir is not None:  # 判断用户选中了有效文件夹并点击了确认
        series_list = vmi.sortSeries(dcmdir)  # 将文件夹及其子目录包含的所有DICOM文件分类到各个系列

        if len(series_list) > 0:  # 判断该文件夹内包含有效的DICOM系列
            series = vmi.askSeries(series_list)  # 用户选择DICOM系列

            if series is not None:  # 判断用户选中了有效系列并点击了确认
                with pydicom.dcmread(series.filenames()[0]) as ds:
                    global patient_name
                    patient_name = ds.PatientName
                return series.read()  # 读取DICOM系列为图像数据


def on_init_voi():
    size = vmi.askInt(1, 300, 1000, suffix='mm', title='请输入目标区域尺寸')
    if size is not None:
        global original_target, voi_size, voi_center
        original_target = original_view.mouseOnPropCell()
        voi_center = np.array([vmi.imCenter(original_image)[0], original_target[1], original_target[2]])
        voi_size = np.array([vmi.imSize(original_image)[0], size, size])
        init_voi()

        global original_LR
        original_LR = 1 if original_target[0] > voi_center[0] else -1
        patient_LR_box.draw_text('患侧：{}'.format('左' if original_LR > 0 else '右'))
        patient_LR_box.visible(True)

        global spcut_center
        spcut_center = original_target.copy()
        update_spcut()

        voi_view.cameraCoronal()
        update_spcut_section()

        voi_view.cameraFit()
        for v in [voi_view, *spcut_y_views, *spcut_z_views]:
            v.setEnabled(True)


@jit(nopython=True)
def ary_pad(input_ary, constant):
    for k in [0, input_ary.shape[0] - 1]:
        for j in range(input_ary.shape[1]):
            for i in range(input_ary.shape[2]):
                input_ary[k][j][i] = constant
    for k in range(input_ary.shape[0]):
        for j in [0, input_ary.shape[1] - 1]:
            for i in range(input_ary.shape[2]):
                input_ary[k][j][i] = constant
    for k in range(input_ary.shape[0]):
        for j in range(input_ary.shape[1]):
            for i in [0, input_ary.shape[2] - 1]:
                input_ary[k][j][i] = constant


def init_voi():
    global voi_size, voi_center, voi_origin, voi_cs
    voi_origin = voi_center - 0.5 * voi_size
    voi_cs = vmi.CS4x4(origin=voi_origin)

    global voi_image
    voi_image = vmi.imReslice(original_image, voi_cs, voi_size, -1024)
    voi_image.SetOrigin(voi_cs.origin())

    voi_ary = vmi.imArray_VTK(voi_image)
    ary_pad(voi_ary, -1024)
    voi_image = vmi.imVTK_Array(voi_ary, vmi.imOrigin(voi_image), vmi.imSpacing(voi_image))
    voi_volume.clone(voi_image)


def update_line_cut():
    if len(plcut_pts) > 1:
        plcut_prop.clone(vmi.ccWire(vmi.ccSegments(plcut_pts, True)))
    else:
        plcut_prop.clone()


@jit(nopython=True)
def ary_mask(input_ary, mask_ary, threshold, target):
    for k in range(input_ary.shape[0]):
        for j in range(input_ary.shape[1]):
            for i in range(input_ary.shape[2]):
                if mask_ary[k][j][i] != 0 and input_ary[k][j][i] >= threshold:
                    input_ary[k][j][i] = target


def plcut_voi_image():
    global voi_image

    cs = voi_view.cameraCS()
    d = vmi.imSize_Vt(voi_image, cs.axis(2))
    pts = [vmi.ptOnPlane(pt, vmi.imCenter(voi_image), cs.axis(2)) for pt in plcut_pts]
    pts = [pt - d * cs.axis(2) for pt in pts]
    sh = vmi.ccFace(vmi.ccWire(vmi.ccSegments(pts, True)))
    sh = vmi.ccPrism(sh, cs.axis(2), 2 * d)

    mask = vmi.imStencil_PolyData(vmi.ccPd_Sh(sh),
                                  vmi.imOrigin(voi_image),
                                  vmi.imSpacing(voi_image),
                                  vmi.imExtent(voi_image))
    mask_ary = vmi.imArray_VTK(mask)
    voi_ary = vmi.imArray_VTK(voi_image)
    ary_mask(voi_ary, mask_ary, bone_value, target_value)
    voi_image = vmi.imVTK_Array(voi_ary, vmi.imOrigin(voi_image), vmi.imSpacing(voi_image))
    voi_volume.clone(voi_image)

    for v in spcut_z_views + spcut_y_views:
        v.updateInTime()


def spcut_voi_image():
    global voi_image
    spcut_image = vmi.imStencil_PolyData(spcut_prop.data(),
                                         vmi.imOrigin(voi_image),
                                         vmi.imSpacing(voi_image),
                                         vmi.imExtent(voi_image))
    spcut_ary = vmi.imArray_VTK(spcut_image)
    voi_ary = vmi.imArray_VTK(voi_image)

    ary_mask(voi_ary, spcut_ary, bone_value, target_value)
    voi_image = vmi.imVTK_Array(voi_ary, vmi.imOrigin(voi_image), vmi.imSpacing(voi_image))
    voi_volume.clone(voi_image)


def update_spcut():
    spcut_mesh = vmi.pdSphere(spcut_radius, spcut_center)
    spcut_prop.clone(spcut_mesh)


def update_spcut_section():
    angle = 30
    y_oblique = [vmi.CS4x4().rotate(angle, [0, 0, 1]), vmi.CS4x4(), vmi.CS4x4().rotate(-angle, [0, 0, 1])]
    z_oblique = [vmi.CS4x4().rotate(-angle, [0, 1, 0]), vmi.CS4x4(), vmi.CS4x4().rotate(angle, [0, 1, 0])]

    y_normals = [cs.mvt([0, 1, 0]) for cs in y_oblique]
    z_normals = [cs.mvt([0, 0, 1]) for cs in z_oblique]

    y_cs = [vmi.CS4x4_Coronal(), vmi.CS4x4_Coronal(), vmi.CS4x4_Coronal()]
    y_cs[0] = y_cs[0].rotate(-angle, y_cs[0].axis(1))
    y_cs[2] = y_cs[2].rotate(angle, y_cs[2].axis(1))

    z_cs = [vmi.CS4x4_Axial(), vmi.CS4x4_Axial(), vmi.CS4x4_Axial()]
    z_cs[0] = z_cs[0].rotate(-angle, z_cs[0].axis(1))
    z_cs[2] = z_cs[2].rotate(angle, z_cs[2].axis(1))

    hheight = 50
    hwidth = hheight * spcut_y_views[0].width() / spcut_y_views[0].height()

    for i in range(3):
        y_cs[i].origin(spcut_center - y_cs[i].mpt([hwidth, hheight, 0]))
        z_cs[i].origin(spcut_center - z_cs[i].mpt([hwidth, hheight, 0]))

    for i in range(3):
        spcut_y_slices[i].slicePlane(face=y_normals[i], origin=spcut_center)
        spcut_z_slices[i].slicePlane(face=z_normals[i], origin=spcut_center)

    for i in range(3):
        spcut_y_props[i].clone(vmi.pdPolygon_Regular(spcut_radius, spcut_center, y_normals[i]))
        spcut_z_props[i].clone(vmi.pdPolygon_Regular(spcut_radius, spcut_center, z_normals[i]))

    for i in range(3):
        spcut_y_views[i].setCamera_FPlane(y_cs[i], 2 * hheight)
        spcut_z_views[i].setCamera_FPlane(z_cs[i], 2 * hheight)


def update_pelvis():
    # image = vmi.imGradientAnisotropicDiffusion(voi_image)
    # image = vmi.imResample_Isotropic(image)
    pd = vmi.imIsosurface(voi_image, bone_value)
    pd = vmi.pdSmoothLaplacian(pd, 50)
    pelvis_prop.clone(pd)


def update_pelvis_MPP():
    global cup_cs, pelvis_MPP_origin
    vr = pelvis_view.camera('right')
    vr = vr if np.dot(vr, np.array([1, 0, 0])) >= 0 else -vr
    if vmi.vtAngle(vr, cup_cs.axis(1)) < 1 or vmi.vtAngle(vr, cup_cs.axis(1)) > 179:
        return

    cup_cs.axis(0, vr)
    cup_cs.orthogonalize([2, 0])
    update_cup_axis()
    update_cup()

    pelvis_MPP_origin = pelvis_view.pickFPlane([0.5 * pelvis_view.width(), 0.5 * pelvis_view.height()])
    cs = vmi.CS4x4().reflect(cup_cs.axis(0), pelvis_MPP_origin)
    pd = vmi.pdMatrix(pelvis_prop.data(), cs.mat4x4())
    pelvis_MPP_prop.clone(pd)


def update_pelvis_APP():
    global cup_cs
    vr = pelvis_view.camera('right')
    vr = vr if np.dot(vr, np.array([0, 1, 0])) >= 0 else -vr
    if vmi.vtAngle(vr, cup_cs.axis(0)) < 1 or vmi.vtAngle(vr, cup_cs.axis(0)) > 179:
        return

    cup_cs.axis(1, vr)
    cup_cs.orthogonalize([2, 0])
    update_cup_axis()
    update_cup()

    cs = pelvis_view.cameraCS()
    pd = vmi.pdMatrix(pelvis_prop.data(), cs.inv().mat4x4())
    b, c = pd.GetBounds(), pd.GetCenter()
    left_top = np.array([b[0], b[2], c[2]])
    right_top = np.array([b[1], b[2], c[2]])
    left_bottom = np.array([b[0], b[3], c[2]])
    right_bottom = np.array([b[1], b[3], c[2]])
    xn = int(np.round(0.1 * (pd.GetBounds()[1] - pd.GetBounds()[0])))

    lines = []
    for i in range(xn + 1):
        pts = [left_top + i / xn * (right_top - left_top),
               left_bottom + i / xn * (right_bottom - left_bottom)]
        pts = [cs.mpt(pt) for pt in pts]
        line = vmi.ccEdge(vmi.ccSegment(pts[0], pts[1]))
        line = vmi.ccPd_Sh(line)
        lines.append(line)

    pd = vmi.pdAppend(lines)
    pelvis_APP_prop.clone(pd)


def update_cup_axis():
    global cup_axis
    cs = cup_cs.copy()
    cs = cs.rotate(-cup_RI, cs.axis(1)).rotate(-cup_RA, cs.axis(0))
    cup_axis = -cs.axis(2) * np.array([original_LR, 1, 1])


def update_cup():
    plane = vtk.vtkPlane()
    plane.SetNormal(cup_axis)
    plane.SetOrigin(cup_cs.origin())

    pd = vmi.pdSphere(cup_radius, cup_cs.origin())
    pd = vmi.pdClip_Implicit(pd, plane)[1]

    pd_border = vmi.pdPolyline_Regular(cup_radius, cup_cs.origin(), cup_axis)
    pd = vmi.pdAppend([pd, pd_border])

    cs = vmi.CS4x4().reflect(cup_cs.axis(0), pelvis_MPP_origin)
    pd_MPP = vmi.pdMatrix(pd, cs.mat4x4())
    cup_prop.clone(vmi.pdAppend([pd, pd_MPP]))

    if pelvis_slice_box.text() == '断层':
        pd = vmi.pdCut_Implicit(cup_prop.data(), pelvis_slice.slicePlane())
        cup_section_prop.clone(pd)


@jit(nopython=True)
def pt_ary_cs_mask(pt_ary: np.ndarray, cs: np.ndarray, mask: np.ndarray):
    return (pt_ary @ cs) * mask


def update_xray_pelvis():
    cs = pelvis_view.cameraCS()
    pelvis_left_top = pelvis_view.pickFPlane([0, 0])
    pelvis_right_top = pelvis_view.pickFPlane([pelvis_view.width(), 0])
    pelvis_left_bottom = pelvis_view.pickFPlane([0, pelvis_view.height()])

    xray_left_top = xray_view.pickFPlane([0, 0])
    xray_right_top = xray_view.pickFPlane([xray_view.width(), 0])
    xray_left_bottom = xray_view.pickFPlane([0, xray_view.height()])

    global xray_cs
    xray_cs = xray_view.cameraCS()
    xray_cs.axis(0, xray_cs.axis(0) * np.linalg.norm(xray_left_top - xray_right_top) /
                 np.linalg.norm(pelvis_left_top - pelvis_right_top))
    xray_cs.axis(1, xray_cs.axis(1) * np.linalg.norm(xray_left_top - xray_left_bottom) /
                 np.linalg.norm(pelvis_left_top - pelvis_left_bottom))
    xray_cs = xray_cs.mcs(vmi.CS4x4(axis2=[0, 0, 0]).mcs(cs.inv()))

    pd = vmi.pdMatrix(pelvis_prop.data(), xray_cs.mat4x4())
    xray_pelvis_prop.clone(pd)

    global cup_cs
    vr = pelvis_view.camera('right')
    vr = vr if np.dot(vr, np.array([0, 1, 0])) >= 0 else -vr
    if vmi.vtAngle(vr, cup_cs.axis(0)) < 1 or vmi.vtAngle(vr, cup_cs.axis(0)) > 179:
        return

    cup_cs.axis(1, vr)
    cup_cs.orthogonalize([2, 0])
    update_cup_axis()
    update_cup()

    global ctray_cs, ctray_size
    ctray_cs = pelvis_view.cameraCS()
    ctray_size[2] = vmi.imSize_Vt(voi_image, cs.axis(2))

    pt = vmi.imCenter(voi_image) - 0.5 * ctray_size[2] * cs.axis(2)
    ctray_cs.origin(vmi.ptOnPlane(cs.origin(), pt, cs.axis(2)))

    ctray_size[0] = np.linalg.norm(pelvis_left_top - pelvis_right_top)
    ctray_size[1] = np.linalg.norm(pelvis_left_top - pelvis_left_bottom)


def update_ctray():
    image_blend = vmi.imReslice_Blend(voi_image, cs=ctray_cs, size=ctray_size,
                                      back_scalar=-1024, scalar_min=bone_value - 300)
    ctray_slice.clone(image_blend)
    ctray_slice.window(width=350, level=bone_value - 150)


def init_guide():
    global voi_image
    size = np.array([4 * cup_radius, 4 * cup_radius, 4 * cup_radius])
    cs = vmi.CS4x4(origin=cup_cs.origin() - 0.5 * size)
    image = vmi.imReslice(voi_image, cs, size, -1024)
    image.SetOrigin(cs.origin())

    ary = vmi.imArray_VTK(image)
    ary_pad(ary, -1024)
    image = vmi.imVTK_Array(ary, vmi.imOrigin(image), vmi.imSpacing(image))
    image = vmi.imResample_Isotropic(image)

    pd = vmi.imIsosurface(image, bone_value)
    # pd = vmi.pdExtract_Largest(pd)
    pd = vmi.pdSmoothLaplacian(pd, 20)
    aceta_prop.clone(pd)

    update_guide_axis()

    guide_view.cameraCoronal()
    guide_view.cameraFit()
    guide_view.setEnabled(True)


def update_guide_axis():
    pts = [cup_cs.origin() - 100 * cup_axis, cup_cs.origin() + 100 * cup_axis]
    pd = vmi.ccPd_Sh(vmi.ccEdge(vmi.ccSegment(pts[0], pts[1])))
    guide_axis_prop.clone(pd)


def update_guide_path(pts):
    """更新拾取路径显示"""
    if len(pts) > 1:  # 判断拾取路径点数是否足够构成封闭线框
        guide_path_prop.clone(vmi.ccWire(vmi.ccSegments(pts, True)))  # 构造封闭折线段
    else:
        guide_path_prop.clone()  # 否则清空拾取路径显示
    guide_view.updateInTime()  # 刷新视图


def update_plate():
    global guide_shape
    if len(guide_path_pts) > 1:
        axis = vmi.pdOBB_Pts(guide_path_pts)['axis'][2]
        if np.dot(axis, cup_axis) > 0:
            axis *= -1
        guide_shape = vmi.ccMatchPd_ClosedPts(guide_path_pts, axis, aceta_prop.data())
        guide_plate_prop.clone(guide_shape)
    else:
        guide_plate_prop.clone()
    guide_view.updateInTime()


def update_plate_hole(pt, radius):
    global guide_shape

    pt += 20 * cup_axis
    cs = vmi.CS4x4_Vt(2, -cup_axis)
    face = vmi.ccFace(vmi.ccWire(vmi.ccCircle(radius + 2, pt, cs.axis(2), cs.axis(0))))

    solid = vmi.ccMatchSh_Face(face, -cup_axis, guide_shape)

    if solid is None:
        print('invalid')

    guide_shape = vmi.ccBoolean_Union([guide_shape, solid])
    guide_plate_prop.clone(guide_shape)

    l = vmi.ccDiagonal(guide_shape) + np.linalg.norm(vmi.ccCenter(guide_shape) - vmi.ccCenter(face))
    solid = vmi.ccCylinder(radius, l, pt, -cup_axis)
    guide_shape = vmi.ccBoolean_Difference([guide_shape, solid])
    guide_plate_prop.clone(guide_shape)


def LeftButtonPress(**kwargs):
    if kwargs['picked'] is voi_view:
        if plcut_box.text() == '请勾画切割范围':
            pt = voi_view.mouseOnFPlane()
            plcut_pts.clear()
            plcut_pts.append(pt)
            update_line_cut()
    elif kwargs['picked'] is aceta_prop:
        if guide_path_box.text() == '请勾画匹配范围':
            pt = guide_view.mouseOnPropCell()  # 获得拾取到的世界坐标点
            guide_path_pts.clear()  # 清空拾取路径点列，开始拾取
            guide_path_pts.append(pt)  # 添加第一个拾取点
            update_guide_path(guide_path_pts)  # 更新拾取路径显示


def LeftButtonPressMove(**kwargs):
    global spcut_center, cup_cs
    if kwargs['picked'] is voi_view:
        if plcut_box.text() == '请勾画切割范围':
            pt = voi_view.mouseOnPropCell()

            for path_pt in plcut_pts:
                if (path_pt == pt).all():
                    return

            plcut_pts.append(pt)  # 添加拾取路径点
            update_line_cut()
        else:
            voi_view.mouseRotateFocal(**kwargs)
    elif kwargs['picked'] is pelvis_view:
        pelvis_view.mouseRotateFocal(**kwargs)
        if pelvis_MPP_box.text() == '确定':
            update_pelvis_MPP()
        elif pelvis_APP_box.text() == '确定':
            update_pelvis_APP()
        elif xray_align_box.text() == '确定':
            update_xray_pelvis()
    elif kwargs['picked'] in [spcut_prop, *spcut_y_props, *spcut_z_props]:
        spcut_center += kwargs['picked'].view.mouseOverFPlane()
        update_spcut()
        update_spcut_section()
    elif kwargs['picked'] in [cup_prop, cup_section_prop]:
        pt = pelvis_view.mouseOnFPlane()
        pt = vmi.ptOnPlane(pt, cup_cs.origin(), pelvis_view.camera('look'))
        center = vmi.ptOnPlane(pelvis_MPP_origin, cup_cs.origin(), pelvis_view.camera('look'))

        over = kwargs['picked'].view.mouseOverFPlane()
        if np.dot(pt - center, cup_cs.origin() - center) < 0:
            over = cup_cs.inv().mvt(over)
            over[0] *= -1
            over = cup_cs.mvt(over)

        cup_cs.origin(cup_cs.origin() + over)
        update_cup()
    elif kwargs['picked'] is aceta_prop:  # 左键按下移动时，参数传递的仍然是按下时的对象
        if guide_path_box.text() == '请勾画匹配范围':
            pt = guide_view.mouseOnPropCell()  # 获得拾取到的世界坐标点

            for path_pt in guide_path_pts:  # 遍历拾取路径点
                if (path_pt == pt).all():  # 如果已经存在相同的点，则返回
                    return

            update_guide_path([*guide_path_pts, pt])  # 更新拾取路径显示，暂不添加拾取路径点

            if guide_view.mouseOnProp() is aceta_prop:  # 判断鼠标当前位置是否在模型上
                guide_path_pts.append(pt)  # 添加拾取路径点


def LeftButtonPressMoveRelease(**kwargs):
    if kwargs['picked'] is voi_view:
        if plcut_box.text() == '请勾画切割范围':
            plcut_box.draw_text('请耐心等待')
            plcut_voi_image()
            plcut_box.draw_text('线切割')

            plcut_pts.clear()
            update_line_cut()
    elif kwargs['picked'] is aceta_prop:  # 左键按下移动释放时，参数传递的仍然是按下时的对象
        if guide_path_box.text() == '请勾画匹配范围':
            # guide_path_box.draw_text('请耐心等待')
            update_plate()  # 左键释放时更新导板
            d = vmi.askInt(1, 2, 10, prefix='直径: ', suffix=' mm')
            if d is not None:
                update_plate_hole(cup_cs.origin(), d / 2)
            guide_path_box.draw_text('匹配板')
            aceta_prop.pickable(False)


def LeftButtonPressRelease(**kwargs):
    global pelvis_MPP_origin, cup_cs, cup_radius, cup_axis, cup_RA, cup_RI
    if kwargs['picked'] is bone_value_box:
        global bone_value
        v = vmi.askInt(-1000, bone_value, 3000)
        if v is not None:
            bone_value = v
            bone_value_box.draw_text('骨阈值：{:.0f} HU'.format(bone_value))
            voi_volume.opacityScalar({bone_value - 1: 0, bone_value: 1})
    elif kwargs['picked'] is plcut_box:
        if plcut_box.text() == '线切割':
            plcut_box.draw_text('请勾画切割范围')
        elif plcut_box.text() == '请勾画切割范围':
            plcut_box.draw_text('线切割')
    elif kwargs['picked'] is spcut_box:
        spcut_box.draw_text('请耐心等待')
        spcut_voi_image()
        spcut_box.draw_text('球切割')
        update_spcut_section()
    elif kwargs['picked'] is spcut_visible_box:
        visible = spcut_prop.visibleToggle()
        spcut_visible_box.draw_text(back_color=QColor.fromRgbF(0.4, 0.6, 1) if visible else QColor('black'))
    elif kwargs['picked'] is spcut_radius_box:
        global spcut_radius
        r = vmi.askInt(5, spcut_radius, 50)
        if r is not None:
            spcut_radius = r
            spcut_radius_box.draw_text('球半径：{:.0f} mm'.format(spcut_radius))
            update_spcut()
            update_spcut_section()
    elif kwargs['picked'] is init_pelvis_box:
        init_pelvis_box.draw_text('请耐心等待')
        update_pelvis()
        pelvis_view.cameraCoronal()
        pelvis_view.cameraFit()
        pelvis_view.setEnabled(True)

        pelvis_MPP_origin = np.array(pelvis_prop.data().GetCenter())
        cup_cs.origin(original_target)
        update_cup_axis()
        update_cup()

        # cup_RA = np.rad2deg(np.arctan(-cup_axis[1] / np.sqrt(1 - cup_axis[2] ** 2)))
        # cup_RI = np.rad2deg(-np.abs(cup_axis[0] / cup_axis[2]))

        xray_view.setEnabled(True)
        init_pelvis_box.draw_text('创建骨盆')
    elif kwargs['picked'] is cup_radius_box:
        r = vmi.askInt(5, cup_radius, 50)
        if r is not None:
            cup_radius = r
            cup_radius_box.draw_text('半径 = {:.0f} mm'.format(cup_radius))
            update_cup()
    elif kwargs['picked'] is cup_RA_box:
        r = vmi.askInt(-15, cup_RA, 45)
        if r is not None:
            cup_RA = r
            cup_RA_box.draw_text('前倾角 = {:.0f}°'.format(cup_RA))

            update_cup_axis()
            update_cup()
    elif kwargs['picked'] is cup_RI_box:
        r = vmi.askInt(0, cup_RI, 60)
        if r is not None:
            cup_RI = r
            cup_RI_box.draw_text('外展角 = {:.0f}°'.format(cup_RI))

            update_cup_axis()
            update_cup()
    elif kwargs['picked'] is cup_radius_box:
        r = vmi.askInt(5, cup_radius, 50)
        if r is not None:
            cup_radius = r
            cup_radius_box.draw_text('半径 = {:.0f} mm'.format(cup_radius))
            update_cup()
    elif kwargs['picked'] is pelvis_slice_box:
        if pelvis_slice_box.text() == '三维':
            pelvis_slice_box.draw_text('断层')
            cup_prop.visible(False)
            pelvis_prop.visible(False)
            cup_section_prop.visible(True)
            pelvis_slice.visible(True)

            pelvis_slice.slicePlane(pelvis_view.camera('look'), cup_cs.origin())
            pd = vmi.pdCut_Implicit(cup_prop.data(), pelvis_slice.slicePlane())
            cup_section_prop.clone(pd)
        elif pelvis_slice_box.text() == '断层':
            pelvis_slice_box.draw_text('三维')
            cup_prop.visible(True)
            pelvis_prop.visible(True)
            cup_section_prop.visible(False)
            pelvis_slice.visible(False)
    elif kwargs['picked'] is pelvis_MPP_box:
        if pelvis_MPP_box.text() == '配准对称面':
            pelvis_MPP_box.draw_text('确定')
            update_pelvis_MPP()
            pelvis_MPP_prop.visible(True)
        elif pelvis_MPP_box.text() == '确定':
            pelvis_MPP_box.draw_text('配准对称面')
            pelvis_MPP_prop.visible(False)
    elif kwargs['picked'] is pelvis_APP_box:
        if pelvis_APP_box.text() == '配准前平面':
            pelvis_APP_box.draw_text('确定')
            update_pelvis_APP()
            pelvis_APP_prop.visible(True)
        elif pelvis_APP_box.text() == '确定':
            pelvis_APP_box.draw_text('配准前平面')
            pelvis_APP_prop.visible(False)
    elif kwargs['picked'] is xray_align_box:
        if xray_align_box.text() == '配准骨盆正位':
            xray_align_box.draw_text('确定')
            update_xray_pelvis()
        elif xray_align_box.text() == '确定':
            xray_align_box.draw_text('配准骨盆正位')
    elif kwargs['picked'] is init_ctray_box:
        init_ctray_box.draw_text('请耐心等待')
        update_ctray()
        ctray_view.cameraAxial()
        ctray_view.cameraFit()
        ctray_view.setEnabled(True)
        init_ctray_box.draw_text('创建投影')
    elif kwargs['picked'] is xray_open_box:
        global xray_image
        xray_image = read_dicom()  # 读取DICOM路径
        if xray_image is not None:
            xray_slice.clone(xray_image)
            xray_view.cameraAxial()
            xray_view.cameraFit()
            xray_slice.windowAuto()
    elif kwargs['picked'] is init_guide_box:
        init_guide_box.draw_text('请耐心等待')
        init_guide()
        init_guide_box.draw_text('创建导板')
    elif kwargs['picked'] is guide_path_box:
        if guide_path_box.text() == '匹配板':
            guide_path_box.draw_text('请勾画匹配范围')
            aceta_prop.pickable(True)
        elif guide_path_box.text() == '请勾画匹配范围':
            guide_path_box.draw_text('匹配板')
            aceta_prop.pickable(False)
    elif kwargs['picked'] is guide_hole_box:
        if guide_hole_box.text() == '引导孔':
            guide_hole_box.draw_text('请定位引导孔中心')
            guide_plate_prop.pickable(True)
        elif guide_hole_box.text() == '请定位引导孔中心':
            guide_hole_box.draw_text('引导孔')
            guide_plate_prop.pickable(False)
    elif kwargs['picked'] is guide_plate_prop:  # 左键按下移动释放时，参数传递的仍然是按下时的对象
        if guide_hole_box.text() == '请定位引导孔中心':
            # guide_hole_box.draw_text('请耐心等待')
            pt = guide_view.mouseOnPropCell()
            d = vmi.askInt(1, 2, 10, prefix='直径: ', suffix=' mm')
            if d is not None:
                update_plate_hole(pt, d / 2)
            guide_hole_box.draw_text('引导孔')
            aceta_prop.pickable(False)
    elif kwargs['picked'] is aceta_visible_box:
        visible = aceta_prop.visibleToggle()
        aceta_visible_box.draw_text(back_color=QColor.fromRgbF(1, 1, 0.6) if visible else QColor('black'))
    elif kwargs['picked'] is guide_plate_visible_box:
        visible = guide_plate_prop.visibleToggle()
        guide_plate_visible_box.draw_text(back_color=QColor.fromRgbF(0.4, 0.6, 1) if visible else QColor('black'))


def MidButtonPressMove(**kwargs):
    if kwargs['picked'] in [pelvis_view, pelvis_slice]:
        pelvis_view.mousePan()
        if pelvis_MPP_box.text() == '确定':
            update_pelvis_MPP()
        elif pelvis_APP_box.text() == '确定':
            update_pelvis_APP()
        elif xray_align_box.text() == '确定':
            update_xray_pelvis()
    elif kwargs['picked'] in [xray_view, xray_slice]:
        xray_view.mousePan()
        if xray_align_box.text() == '确定':
            update_xray_pelvis()


def RightButtonPressMove(**kwargs):
    if kwargs['picked'] in [pelvis_view, pelvis_slice]:
        pelvis_view.mouseZoom()
        if pelvis_MPP_box.text() == '确定':
            update_pelvis_MPP()
        elif pelvis_APP_box.text() == '确定':
            update_pelvis_APP()
        elif xray_align_box.text() == '确定':
            update_xray_pelvis()
    elif kwargs['picked'] in [xray_view, xray_slice]:
        xray_view.mouseZoom()
        if xray_align_box.text() == '确定':
            update_xray_pelvis()


def NoButtonWheel(**kwargs):
    global cup_cs, cup_radius, cup_axis, cup_RA, cup_RI
    if kwargs['picked'] is bone_value_box:
        global bone_value
        bone_value = min(max(bone_value + 10 * kwargs['delta'], -1000), 3000)
        bone_value_box.draw_text('骨阈值：{:.0f} HU'.format(bone_value))
        voi_volume.opacityScalar({bone_value - 1: 0, bone_value: 1})
    elif kwargs['picked'] is spcut_radius_box:
        global spcut_radius
        spcut_radius = min(max(spcut_radius + kwargs['delta'], 5), 50)
        spcut_radius_box.draw_text('球半径：{:.0f} mm'.format(spcut_radius))
        update_spcut()
        update_spcut_section()
    elif kwargs['picked'] is pelvis_view:
        pelvis_view.mouseRotateLook(**kwargs)
        if pelvis_MPP_box.text() == '确定':
            update_pelvis_MPP()
        elif pelvis_APP_box.text() == '确定':
            update_pelvis_APP()
        elif xray_align_box.text() == '确定':
            update_xray_pelvis()
    elif kwargs['picked'] is cup_radius_box:
        cup_radius = min(max(cup_radius + kwargs['delta'], 5), 50)
        cup_radius_box.draw_text('半径：{:.0f} mm'.format(cup_radius))
        update_cup()
    elif kwargs['picked'] is cup_RA_box:
        cup_RA = min(max(cup_RA + kwargs['delta'], -15), 45)
        cup_RA_box.draw_text('前倾角：{:.0f}°'.format(cup_RA))

        update_cup_axis()
        update_cup()
    elif kwargs['picked'] is cup_RI_box:
        cup_RI = min(max(cup_RI + kwargs['delta'], 0), 60)
        cup_RI_box.draw_text('外展角：{:.0f}°'.format(cup_RI))

        update_cup_axis()
        update_cup()
    elif kwargs['picked'] is pelvis_slice:
        pelvis_slice.slice(**kwargs)
        update_cup()


class Main(QScrollArea):
    def __init__(self):
        QScrollArea.__init__(self)
        brush = QBrush(QColor(255, 255, 255, 255))
        palette = QPalette()
        palette.setBrush(QPalette.Active, QPalette.Base, brush)
        palette.setBrush(QPalette.Active, QPalette.Window, brush)
        palette.setBrush(QPalette.Inactive, QPalette.Base, brush)
        palette.setBrush(QPalette.Inactive, QPalette.Window, brush)
        palette.setBrush(QPalette.Disabled, QPalette.Base, brush)
        palette.setBrush(QPalette.Disabled, QPalette.Window, brush)
        self.setPalette(palette)
        self.setWidgetResizable(True)

    def closeEvent(self, ev: QCloseEvent):
        ev.accept() if vmi.askYesNo('退出程序？') else ev.ignore()


if __name__ == '__main__':
    patient_name = str()
    original_image = read_dicom()  # 读取DICOM路径
    if original_image is None:
        vmi.appexit()

    # 0 原始图像
    original_target, original_LR = np.zeros(3), 1
    original_view = vmi.View()

    original_slice = vmi.ImageSlice(original_view)  # 断层显示
    original_slice.clone(original_image)  # 载入读取到的DICOM图像
    original_slice.windowBone()
    original_slice.slicePlane(face='coronal', origin='center')  # 设置断层图像显示横断面，位置居中

    original_slice_menu = vmi.Menu()
    original_slice_menu.menu.addAction('定位髋关节中心').triggered.connect(on_init_voi)
    original_slice_menu.menu.addSeparator()
    original_slice_menu.menu.addMenu(original_slice.menu)
    original_slice.mouse['RightButton']['PressRelease'] = original_slice_menu.menuexec

    patient_name_box = vmi.TextBox(original_view, text='姓名：{}'.format(patient_name),
                                   size=[0.4, 0.04], pos=[0, 0.04], anchor=[0, 0])
    patient_LR_box = vmi.TextBox(original_view, text='患侧',
                                 size=[0.24, 0.04], pos=[0, 0.08], anchor=[0, 0])
    patient_LR_box.visible(False)

    original_view.cameraCoronal()
    original_view.cameraFit()  # 自动调整视图的视野范围

    # 1 目标区域
    voi_view = vmi.View()
    voi_view.mouse['LeftButton']['Press'] = LeftButtonPress
    voi_view.mouse['LeftButton']['PressMove'] = LeftButtonPressMove
    voi_view.mouse['LeftButton']['PressMoveRelease'] = LeftButtonPressMoveRelease

    bone_value, target_value = 200, -1100

    bone_value_box = vmi.TextBox(voi_view, text='骨阈值：{:.0f} HU'.format(bone_value),
                                 size=[0.24, 0.04], pos=[0, 0.04], anchor=[0, 0], pickable=True)
    bone_value_box.mouse['LeftButton']['PressRelease'] = LeftButtonPressRelease
    bone_value_box.mouse['NoButton']['Wheel'] = NoButtonWheel

    voi_size, voi_center, voi_origin, voi_cs = np.zeros(3), np.zeros(3), np.zeros(3), vmi.CS4x4()

    voi_image = vtk.vtkImageData()
    voi_volume = vmi.ImageVolume(voi_view)
    voi_volume.opacityScalar({bone_value - 1: 0, bone_value: 1})
    voi_volume.color({bone_value: [1, 1, 0.6]})

    # 线切割
    plcut_pts = []
    plcut_prop = vmi.PolyActor(voi_view, rgb=[1, 0.6, 0.6], line=3)
    plcut_prop.alwaysOnTop(True)

    # 球切割
    spcut_center, spcut_radius, spcut_length = np.zeros(3), 22, 200
    spcut_prop = vmi.PolyActor(voi_view, rgb=[0.4, 0.6, 1], pickable=True)
    spcut_prop.mouse['LeftButton']['PressMove'] = LeftButtonPressMove

    plcut_box = vmi.TextBox(voi_view, text='线切割', size=[0.24, 0.04], pos=[0, 0.1], anchor=[0, 0], pickable=True)
    plcut_box.mouse['LeftButton']['PressRelease'] = LeftButtonPressRelease

    spcut_box = vmi.TextBox(voi_view, text='球切割', size=[0.24, 0.04], pos=[0, 0.16], anchor=[0, 0], pickable=True)
    spcut_box.mouse['LeftButton']['PressRelease'] = LeftButtonPressRelease

    spcut_visible_box = vmi.TextBox(voi_view, size=[0.01, 0.04], pos=[0.24, 0.16], anchor=[1, 0],
                                    back_color=QColor.fromRgbF(0.4, 0.6, 1), pickable=True)
    spcut_visible_box.mouse['LeftButton']['PressRelease'] = LeftButtonPressRelease

    spcut_radius_box = vmi.TextBox(voi_view, text='球半径：{:.0f} mm'.format(spcut_radius),
                                   size=[0.24, 0.04], pos=[0, 0.20], anchor=[0, 0], pickable=True)
    spcut_radius_box.mouse['LeftButton']['PressRelease'] = LeftButtonPressRelease
    spcut_radius_box.mouse['NoButton']['Wheel'] = NoButtonWheel

    # 234 球切割局部
    spcut_y_views = [vmi.View(), vmi.View(), vmi.View()]
    spcut_z_views = [vmi.View(), vmi.View(), vmi.View()]

    spcut_y_boxs = [vmi.TextBox(spcut_y_views[i], text=['斜冠状位', '正冠状位', '斜冠状位'][i],
                                size=[0.2, 0.1], pos=[1, 1], anchor=[1, 1]) for i in range(3)]
    spcut_z_boxs = [vmi.TextBox(spcut_z_views[i], text=['斜横断位', '正横断位', '斜横断位'][i],
                                size=[0.2, 0.1], pos=[1, 1], anchor=[1, 1]) for i in range(3)]

    spcut_y_slices = [vmi.ImageSlice(v) for v in spcut_y_views]
    spcut_z_slices = [vmi.ImageSlice(v) for v in spcut_z_views]

    for i in spcut_y_slices + spcut_z_slices:
        i.bind(voi_volume)
        i.bindLookupTable(original_slice)
        i.mouse['NoButton']['Wheel'] = i.mouseblock

    spcut_y_props = [vmi.PolyActor(v, rgb=[0.4, 0.6, 1], alpha=0.5, pickable=True) for v in spcut_y_views]
    spcut_z_props = [vmi.PolyActor(v, rgb=[0.4, 0.6, 1], alpha=0.5, pickable=True) for v in spcut_z_views]

    for i in spcut_y_props + spcut_z_props:
        i.mouse['LeftButton']['PressMove'] = LeftButtonPressMove

    init_pelvis_box = vmi.TextBox(voi_view, text='创建骨盆', text_color=QColor('white'), back_color=QColor('crimson'),
                                  bold=True, size=[0.24, 0.04], pos=[1, 0.04], anchor=[1, 0], pickable=True)
    init_pelvis_box.mouse['LeftButton']['PressRelease'] = LeftButtonPressRelease

    # 5 骨盆规划
    pelvis_view = vmi.View()
    pelvis_view.mouse['LeftButton']['PressMove'] = LeftButtonPressMove
    pelvis_view.mouse['MidButton']['PressMove'] = MidButtonPressMove
    pelvis_view.mouse['RightButton']['PressMove'] = RightButtonPressMove
    pelvis_view.mouse['NoButton']['Wheel'] = NoButtonWheel

    pelvis_prop = vmi.PolyActor(pelvis_view, rgb=[1, 1, 0.6])

    cup_cs = vmi.CS4x4()
    cup_axis = np.array([0, 0, -1])
    cup_radius, cup_RA, cup_RI = 22, 10, 40
    cup_prop = vmi.PolyActor(pelvis_view, rgb=[0.4, 0.6, 1], line=3, pickable=True)
    cup_prop.mouse['LeftButton']['PressMove'] = LeftButtonPressMove

    cup_radius_box = vmi.TextBox(pelvis_view, text='半径: {:.0f} mm'.format(cup_radius), pickable=True,
                                 size=[0.24, 0.04], pos=[0, 0.04], anchor=[0, 0])
    cup_radius_box.mouse['LeftButton']['PressRelease'] = LeftButtonPressRelease
    cup_radius_box.mouse['NoButton']['Wheel'] = NoButtonWheel

    cup_RA_box = vmi.TextBox(pelvis_view, text='前倾角: {:.0f}°'.format(cup_RA), pickable=True,
                             size=[0.24, 0.04], pos=[0, 0.1], anchor=[0, 0])
    cup_RA_box.mouse['LeftButton']['PressRelease'] = LeftButtonPressRelease
    cup_RA_box.mouse['NoButton']['Wheel'] = NoButtonWheel

    cup_RI_box = vmi.TextBox(pelvis_view, text='外展角: {:.0f}°'.format(cup_RI), pickable=True,
                             size=[0.24, 0.04], pos=[0, 0.14], anchor=[0, 0])
    cup_RI_box.mouse['LeftButton']['PressRelease'] = LeftButtonPressRelease
    cup_RI_box.mouse['NoButton']['Wheel'] = NoButtonWheel

    pelvis_slice = vmi.ImageSlice(pelvis_view)
    pelvis_slice.bind(voi_volume)
    pelvis_slice.bindLookupTable(original_slice)
    pelvis_slice.visible(False)
    pelvis_slice.mouse['MidButton']['PressMove'] = MidButtonPressMove
    pelvis_slice.mouse['RightButton']['PressMove'] = RightButtonPressMove
    pelvis_slice.mouse['NoButton']['Wheel'] = NoButtonWheel

    cup_section_prop = vmi.PolyActor(pelvis_view, rgb=[0.4, 0.6, 1], line=3, pickable=True)
    cup_section_prop.mouse['LeftButton']['PressMove'] = LeftButtonPressMove
    cup_section_prop.visible(False)

    pelvis_slice_box = vmi.TextBox(pelvis_view, text='三维', pickable=True,
                                   size=[0.24, 0.04], pos=[0, 0.2], anchor=[0, 0])
    pelvis_slice_box.mouse['LeftButton']['PressRelease'] = LeftButtonPressRelease

    pelvis_MPP_box = vmi.TextBox(pelvis_view, text='配准对称面', pickable=True,
                                 size=[0.24, 0.04], pos=[0, 0.26], anchor=[0, 0])
    pelvis_MPP_box.mouse['LeftButton']['PressRelease'] = LeftButtonPressRelease

    pelvis_APP_box = vmi.TextBox(pelvis_view, text='配准前平面', pickable=True,
                                 size=[0.24, 0.04], pos=[0, 0.3], anchor=[0, 0])
    pelvis_APP_box.mouse['LeftButton']['PressRelease'] = LeftButtonPressRelease

    pelvis_MPP_origin = np.zeros(3)
    pelvis_MPP_prop = vmi.PolyActor(pelvis_view, rgb=[1, 0.4, 0.4])
    pelvis_MPP_prop.rep('points')
    pelvis_MPP_prop.visible(False)
    pelvis_APP_prop = vmi.PolyActor(pelvis_view, rgb=[1, 0.4, 0.4], line=3)
    pelvis_APP_prop.alwaysOnTop(True)
    pelvis_APP_prop.visible(False)

    init_guide_box = vmi.TextBox(pelvis_view, text='创建导板', text_color=QColor('white'), back_color=QColor('crimson'),
                                 bold=True, size=[0.24, 0.04], pos=[1, 0.04], anchor=[1, 0], pickable=True)
    init_guide_box.mouse['LeftButton']['PressRelease'] = LeftButtonPressRelease

    # 6 投影对照
    xray_cs = vmi.CS4x4()
    xray_view = vmi.View()
    xray_view.mouse['LeftButton']['PressMove'] = xray_view.mousepass
    xray_view.mouse['MidButton']['PressMove'] = MidButtonPressMove
    xray_view.mouse['RightButton']['PressMove'] = RightButtonPressMove
    xray_view.mouse['NoButton']['Wheel'] = xray_view.mousepass

    xray_slice = vmi.ImageSlice(xray_view)
    xray_slice.mouse['MidButton']['PressMove'] = MidButtonPressMove
    xray_slice.mouse['RightButton']['PressMove'] = RightButtonPressMove

    xray_pelvis_prop = vmi.PolyActor(xray_view, rgb=[1, 1, 0.6], alpha=0.1)
    xray_pelvis_prop.rep('points')
    xray_pelvis_prop.shade(False)

    xray_open_box = vmi.TextBox(xray_view, text='打开X-ray图像',
                                size=[0.24, 0.04], pos=[0, 0.04], anchor=[0, 0], pickable=True)
    xray_open_box.mouse['LeftButton']['PressRelease'] = LeftButtonPressRelease

    xray_align_box = vmi.TextBox(xray_view, text='配准骨盆正位',
                                 size=[0.24, 0.04], pos=[0, 0.1], anchor=[0, 0], pickable=True)
    xray_align_box.mouse['LeftButton']['PressRelease'] = LeftButtonPressRelease

    init_ctray_box = vmi.TextBox(xray_view, text='创建投影', text_color=QColor('white'), back_color=QColor('crimson'),
                                 bold=True, size=[0.24, 0.04], pos=[1, 0.04], anchor=[1, 0], pickable=True)
    init_ctray_box.mouse['LeftButton']['PressRelease'] = LeftButtonPressRelease

    # 7 站立位投影
    ctray_cs = vmi.CS4x4()
    ctray_size = np.zeros(3)
    ctray_view = vmi.View()
    ctray_slice = vmi.ImageSlice(ctray_view)

    # 8 导板
    guide_view = vmi.View()

    guide_shape = vmi.TopoDS_Shape()

    aceta_prop = vmi.PolyActor(guide_view, rgb=[1, 1, 0.6])
    aceta_prop.mouse['LeftButton']['Press'] = LeftButtonPress
    aceta_prop.mouse['LeftButton']['PressMove'] = LeftButtonPressMove
    aceta_prop.mouse['LeftButton']['PressMoveRelease'] = LeftButtonPressMoveRelease
    guide_axis_prop = vmi.PolyActor(guide_view, rgb=[1, 0.4, 0.4], line=3, pickable=True)

    guide_path_pts = []
    guide_path_prop = vmi.PolyActor(guide_view, rgb=[1, 0.4, 0.4], line=3)
    guide_plate_prop = vmi.PolyActor(guide_view, rgb=[0.4, 0.6, 1])
    guide_plate_prop.mouse['LeftButton']['PressRelease'] = LeftButtonPressRelease

    guide_path_box = vmi.TextBox(guide_view, text='匹配板',
                                 size=[0.24, 0.04], pos=[0, 0.04], anchor=[0, 0], pickable=True)
    guide_path_box.mouse['LeftButton']['PressRelease'] = LeftButtonPressRelease

    guide_hole_box = vmi.TextBox(guide_view, text='引导孔',
                                 size=[0.24, 0.04], pos=[0, 0.1], anchor=[0, 0], pickable=True)
    guide_hole_box.mouse['LeftButton']['PressRelease'] = LeftButtonPressRelease

    aceta_visible_box = vmi.TextBox(guide_view, size=[0.01, 0.04], pos=[0.23, 0.04], anchor=[1, 0],
                                    back_color=QColor.fromRgbF(1, 1, 0.6), pickable=True)
    aceta_visible_box.mouse['LeftButton']['PressRelease'] = LeftButtonPressRelease

    guide_plate_visible_box = vmi.TextBox(guide_view, size=[0.01, 0.04], pos=[0.24, 0.04], anchor=[1, 0],
                                          back_color=QColor.fromRgbF(0.4, 0.6, 1), pickable=True)
    guide_plate_visible_box.mouse['LeftButton']['PressRelease'] = LeftButtonPressRelease

    views = [original_view, voi_view, *spcut_y_views, *spcut_z_views, pelvis_view, xray_view, ctray_view, guide_view]

    screen_width = QGuiApplication.screens()[0].geometry().width()
    for v in views:
        v.setMinimumWidth(0.5 * screen_width)
    for v in spcut_y_views + spcut_z_views:
        v.setMinimumWidth(0.25 * screen_width)

    for v in views[1:]:
        v.setEnabled(False)

    # 视图布局
    widget = QWidget()
    layout = QGridLayout(widget)
    layout.addWidget(original_view, 0, 0, 3, 1)
    layout.addWidget(voi_view, 0, 1, 3, 1)
    layout.addWidget(spcut_y_views[0], 0, 2, 1, 1)
    layout.addWidget(spcut_y_views[1], 1, 2, 1, 1)
    layout.addWidget(spcut_y_views[2], 2, 2, 1, 1)
    layout.addWidget(spcut_z_views[0], 0, 3, 1, 1)
    layout.addWidget(spcut_z_views[1], 1, 3, 1, 1)
    layout.addWidget(spcut_z_views[2], 2, 3, 1, 1)
    layout.addWidget(pelvis_view, 0, 4, 3, 1)
    layout.addWidget(xray_view, 0, 5, 3, 1)
    layout.addWidget(ctray_view, 0, 6, 3, 1)
    layout.addWidget(guide_view, 0, 7, 3, 1)

    main = Main()
    main.setWidget(widget)

    vmi.appexec(main)  # 执行主窗口程序
    vmi.appexit()  # 清理并退出程序
