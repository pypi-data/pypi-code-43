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
    size = vmi.askInt(1, 200, 1000, suffix='mm', title='请输入目标区域尺寸')
    if size is not None:
        global original_target, voi_size, voi_center
        original_target = original_view.mouseOnPropCell()
        voi_center = np.array([vmi.imCenter(original_image)[0], original_target[1], original_target[2]])
        voi_size = np.array([vmi.imSize(original_image)[0], size, size])
        init_voi()

        voi_view.cameraCoronal()
        voi_view.cameraFit()
        voi_view.setEnabled(True)


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
    voi_image.SetOrigin(*list(voi_cs.origin()))

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
    ary_mask(voi_ary, mask_ary, threshold, back_value)
    voi_image = vmi.imVTK_Array(voi_ary, vmi.imOrigin(voi_image), vmi.imSpacing(voi_image))
    voi_volume.clone(voi_image)


def update_cline_curve():
    if len(cline_centers) > 1:
        for i in range(len(cline_centers)):
            cline_center_props[i].clone(vmi.pdSphere(1, cline_centers[i]))

        edge = vmi.ccEdge(vmi.ccBSpline_Kochanek(cline_centers))
        l = vmi.ccLength(edge)
        pts = vmi.ccUniformPts_Edge(edge, round(max(l / 0.1, 2)))
        cline_curve_prop.clone(vmi.pdPolyline(pts))
    elif len(cline_centers) > 0:
        cline_center_props[0].clone(vmi.pdSphere(1, cline_centers[0]))
        cline_curve_prop.clone()
    else:
        cline_curve_prop.clone()
    voi_view.updateInTime()


def update_cline_wire():
    if cline_curve_prop.data().GetNumberOfPoints() >= 2:
        kd = vtk.vtkKdTreePointLocator()
        kd.SetDataSet(cline_curve_prop.data())
        kd.BuildLocator()

        for i in range(len(cline_centers)):
            ids = vtk.vtkIdList()
            kd.FindClosestNPoints(2, cline_centers[i], ids)

            pts = [np.array(kd.GetDataSet().GetPoint(ids.GetId(0))),
                   np.array(kd.GetDataSet().GetPoint(ids.GetId(1)))]
            n = pts[1] - pts[0]

            circle = vmi.ccCircle(cline_radiuss[i], cline_centers[i], n)
            cline_wires[i] = vmi.ccWire(circle)
            cline_wire_props[i].clone(cline_wires[i])


def update_cline_tube():
    if len(cline_wires) > 1:
        sh0 = vmi.ccFace(cline_wires[0])
        sh1 = vmi.ccLoft(cline_wires, redirect=True)
        sh2 = vmi.ccFace(cline_wires[-1])
        sh = vmi.ccSolid(vmi.ccSew([sh0, sh1, sh2]))
        cline_tube_prop.clone(sh)
    elif len(cline_wires) > 0:
        sh = vmi.ccFace(cline_wires[0])
        cline_tube_prop.clone(sh)
    else:
        cline_tube_prop.clone()


def LeftButtonPress(**kwargs):
    if kwargs['picked'] is voi_view:
        if plcut_box.text() == '请勾画切割范围':
            pt = voi_view.mouseOnFPlane()
            plcut_pts.clear()
            plcut_pts.append(pt)
            update_line_cut()


def LeftButtonPressMove(**kwargs):
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
    elif kwargs['picked'] is original_slice:
        original_slice.windowMove(**kwargs)
        voi_view.updateInTime()
    elif kwargs['picked'] in cline_center_props:
        i = cline_center_props.index(kwargs['picked'])
        if not voi_volume.visible() and voi_slice.visible():
            pt = voi_view.mouseOnPropCell()
            pt = vmi.rayPlane(voi_slice.slicePlaneOrigin(), voi_slice.slicePlaneNormal(),
                              pt, voi_view.camera('look'))
            if np.linalg.norm(cline_centers[i] - pt) < 10:
                cline_centers[i] = pt
        else:
            cline_centers[i] += voi_view.mouseOverFPlane()
        update_cline_curve()
        update_cline_wire()


def LeftButtonPressMoveRelease(**kwargs):
    if kwargs['picked'] is voi_view:
        if plcut_box.text() == '请勾画切割范围':
            plcut_box.draw_text('请耐心等待')
            plcut_voi_image()
            plcut_box.draw_text('线切割')

            plcut_pts.clear()
            update_line_cut()


def LeftButtonPressRelease(**kwargs):
    global cline_centers, cline_radiuss
    if kwargs['picked'] in [voi_view, voi_slice]:
        if kwargs['double'] is True:
            pt = voi_view.mouseOnPropCell()

            cline_center_prop = vmi.PolyActor(voi_view, rgb=[0.6, 1, 0.6], pickable=True)
            cline_center_prop.alwaysOnTop(True)
            cline_center_prop.mouse['LeftButton']['PressMove'] = LeftButtonPressMove
            cline_center_prop.mouse['LeftButton']['PressRelease'] = LeftButtonPressRelease
            cline_center_prop.mouse['NoButton']['Wheel'] = NoButtonWheel

            cline_wire_prop = vmi.PolyActor(voi_view, rgb=[0.6, 1, 0.6], line=3, pickable=True)

            if len(cline_centers) > 1:
                if np.linalg.norm(pt - cline_centers[0]) < np.linalg.norm(pt - cline_centers[-1]):
                    cline_centers.insert(0, pt)
                    cline_radiuss.insert(0, 1)
                    cline_wires.insert(0, vmi.TopoDS_Shape())
                    cline_center_props.insert(0, cline_center_prop)
                    cline_wire_props.insert(0, cline_wire_prop)
                else:
                    cline_centers.append(pt)
                    cline_radiuss.append(1)
                    cline_wires.append(vmi.TopoDS_Shape())
                    cline_center_props.append(cline_center_prop)
                    cline_wire_props.append(cline_wire_prop)
            else:
                cline_centers.append(pt)
                cline_radiuss.append(1)
                cline_wires.append(vmi.TopoDS_Shape())
                cline_center_props.append(cline_center_prop)
                cline_wire_props.append(cline_wire_prop)
            update_cline_curve()
            update_cline_wire()
    elif kwargs['picked'] is voi_slice_visible_box:
        visible = voi_slice.visibleToggle()
        voi_slice_visible_box.draw_text(back_color=QColor('whitesmoke') if visible else QColor('black'))
    elif kwargs['picked'] is voi_volume_visible_box:
        visible = voi_volume.visibleToggle()
        voi_volume_visible_box.draw_text(back_color=QColor.fromRgbF(1, 1, 0.6) if visible else QColor('black'))
    elif kwargs['picked'] is threshold_box:
        global threshold
        v = vmi.askInt(-1000, threshold, 3000)
        if v is not None:
            threshold = v
            threshold_box.draw_text('阈值：{} HU'.format(threshold))
            voi_volume.opacityScalar({threshold - 1: 0, threshold: 1})
            voi_volume.color({threshold: [1, 0.4, 0.4], threshold + 100: [1, 1, 0.6]})
    elif kwargs['picked'] is plcut_box:
        if plcut_box.text() == '线切割':
            plcut_box.draw_text('请勾画切割范围')
        elif plcut_box.text() == '请勾画切割范围':
            plcut_box.draw_text('线切割')
    elif kwargs['picked'] in cline_center_props:
        if kwargs['double'] is True:
            i = cline_center_props.index(kwargs['picked'])
            cline_center_props[i].delete()
            cline_wire_props[i].delete()
            del cline_centers[i], cline_radiuss[i], cline_wires[i]
            del cline_center_props[i], cline_wire_props[i]
            update_cline_curve()
            update_cline_wire()
        else:
            i = cline_center_props.index(kwargs['picked'])
            voi_view.camera().SetFocalPoint(*cline_centers[i])

            if cline_curve_prop.data().GetNumberOfPoints() >= 2:
                kd = vtk.vtkKdTreePointLocator()
                kd.SetDataSet(cline_curve_prop.data())
                kd.BuildLocator()

                ids = vtk.vtkIdList()
                kd.FindClosestNPoints(2, cline_centers[i], ids)

                pts = [np.array(kd.GetDataSet().GetPoint(ids.GetId(0))),
                       np.array(kd.GetDataSet().GetPoint(ids.GetId(1)))]
                n = pts[1] - pts[0]
                voi_slice.slicePlane(n, cline_centers[i])
            else:
                voi_slice.slicePlane(origin=cline_centers[i])
    elif kwargs['picked'] is cline_tube_box:
        cline_tube_box.draw_text('请耐心等待')
        update_cline_tube()
        cline_tube_box.draw_text('血管')
    elif kwargs['picked'] is cline_tube_visible_box:
        visible = cline_tube_prop.visibleToggle()
        cline_tube_visible_box.draw_text(back_color=QColor.fromRgbF(0.4, 0.6, 1) if visible else QColor('black'))
    elif kwargs['picked'] is cline_clear_box:
        for i in range(len(cline_centers)):
            cline_center_props[-1].delete()
            cline_wire_props[-1].delete()
            del cline_centers[-1], cline_radiuss[-1], cline_wires[-1]
            del cline_center_props[-1], cline_wire_props[-1]
        update_cline_curve()
        update_cline_wire()
    elif kwargs['picked'] is cline_data_open_box:
        file = vmi.askOpenFile(nameFilter='*.npz', title='npz')
        if file is not None:
            with open(file, mode='rb') as f:
                f.seek(0)
                data = np.load(f)
                print(data, sorted(data))
                if 'cline_centers' in data and 'cline_radius' in data:
                    cline_centers = list(data['cline_centers'])
                    cline_radiuss = list(data['cline_radius'])

                    for i in range(len(cline_centers)):
                        cline_wires.append(vmi.TopoDS_Shape())

                        prop = vmi.PolyActor(voi_view, rgb=[0.6, 1, 0.6], pickable=True)
                        prop.alwaysOnTop(True)
                        prop.mouse['LeftButton']['PressMove'] = LeftButtonPressMove
                        prop.mouse['LeftButton']['PressRelease'] = LeftButtonPressRelease
                        prop.mouse['NoButton']['Wheel'] = NoButtonWheel
                        cline_center_props.append(prop)

                        prop = vmi.PolyActor(voi_view, rgb=[0.6, 1, 0.6], line=3, pickable=True)
                        cline_wire_props.append(prop)

                    update_cline_curve()
                    update_cline_wire()
    elif kwargs['picked'] is cline_data_save_box:
        if len(cline_centers) > 0:
            file = vmi.askSaveFile(nameFilter='*.npz', title='npz')
            if file is not None:
                np.savez(file, cline_centers=np.array(cline_centers),
                         cline_radius=np.array(cline_radiuss))
    elif kwargs['picked'] is cline_tube_stl_box:
        if cline_tube_prop.data().GetNumberOfCells() > 0:
            file = vmi.askSaveFile(nameFilter='*.stl', title='stl')
            if file is not None:
                vmi.pdExport_STL(cline_tube_prop.data(), file)


def NoButtonWheel(**kwargs):
    if kwargs['picked'] is threshold_box:
        global threshold
        threshold = min(max(threshold + 10 * kwargs['delta'], -1000), 3000)
        threshold_box.draw_text('阈值：{} HU'.format(threshold))
        voi_volume.opacityScalar({threshold - 1: 0, threshold: 1})
        voi_volume.color({threshold: [1, 0.4, 0.4], threshold + 100: [1, 1, 0.6]})
    elif kwargs['picked'] in cline_center_props:
        i = cline_center_props.index(kwargs['picked'])
        cline_radiuss[i] = min(max(cline_radiuss[i] + 0.1 * kwargs['delta'], 1), 10)
        update_cline_wire()


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
    original_target = np.zeros(3)
    original_view = vmi.View()

    original_slice = vmi.ImageSlice(original_view)  # 断层显示
    original_slice.clone(original_image)  # 载入读取到的DICOM图像
    original_slice.windowSoft()
    original_slice.slicePlane(face='coronal', origin='center')  # 设置断层图像显示横断面，位置居中
    original_slice.mouse['LeftButton']['PressMove'] = LeftButtonPressMove

    original_slice_menu = vmi.Menu()
    original_slice_menu.menu.addAction('定位目标区域').triggered.connect(on_init_voi)
    original_slice_menu.menu.addSeparator()
    original_slice_menu.menu.addMenu(original_slice.menu)
    original_slice.mouse['RightButton']['PressRelease'] = original_slice_menu.menuexec

    patient_name_box = vmi.TextBox(original_view, text='姓名：{}'.format(patient_name),
                                   size=[0.24, 0.04], pos=[0, 0.04], anchor=[0, 0])

    original_view.cameraCoronal()
    original_view.cameraFit()  # 自动调整视图的视野范围

    # 1 目标区域
    voi_view = vmi.View()
    voi_view.mouse['LeftButton']['Press'] = LeftButtonPress
    voi_view.mouse['LeftButton']['PressMove'] = LeftButtonPressMove
    voi_view.mouse['LeftButton']['PressMoveRelease'] = LeftButtonPressMoveRelease
    voi_view.mouse['LeftButton']['PressRelease'] = LeftButtonPressRelease

    threshold, back_value = 120, -1100

    threshold_box = vmi.TextBox(voi_view, text='阈值：{} HU'.format(threshold),
                                size=[0.24, 0.04], pos=[0, 0.04], anchor=[0, 0], pickable=True)
    threshold_box.mouse['LeftButton']['PressRelease'] = LeftButtonPressRelease
    threshold_box.mouse['NoButton']['Wheel'] = NoButtonWheel

    voi_image = vtk.vtkImageData()
    voi_volume = vmi.ImageVolume(voi_view)
    voi_volume.opacityScalar({threshold - 1: 0, threshold: 1})
    voi_volume.color({threshold: [1, 0.4, 0.4], threshold + 100: [1, 1, 0.6]})

    voi_slice = vmi.ImageSlice(voi_view)
    voi_slice.slicePlaneAxial()
    voi_slice.visible(False)
    voi_slice.bind(voi_volume)
    voi_slice.bindLookupTable(original_slice)
    voi_slice.mouse['LeftButton']['PressMove'] = voi_view.mouseRotateFocal

    voi_slice_visible_box = vmi.TextBox(voi_view, back_color=QColor('black'),
                                        size=[0.01, 0.04], pos=[0.24, 0.04], anchor=[1, 0], pickable=True)
    voi_slice_visible_box.mouse['LeftButton']['PressRelease'] = LeftButtonPressRelease

    voi_volume_visible_box = vmi.TextBox(voi_view, back_color=QColor.fromRgbF(1, 1, 0.6),
                                         size=[0.01, 0.04], pos=[0.23, 0.04], anchor=[1, 0], pickable=True)
    voi_volume_visible_box.mouse['LeftButton']['PressRelease'] = LeftButtonPressRelease

    voi_size, voi_center, voi_origin, voi_cs = np.zeros(3), np.zeros(3), np.zeros(3), vmi.CS4x4()

    # 线切割
    plcut_pts = []
    plcut_prop = vmi.PolyActor(voi_view, rgb=[1, 0.4, 0.4], line=3)
    plcut_prop.alwaysOnTop(True)

    plcut_box = vmi.TextBox(voi_view, text='线切割', pickable=True,
                            size=[0.24, 0.04], pos=[0, 0.1], anchor=[0, 0])
    plcut_box.mouse['LeftButton']['PressRelease'] = LeftButtonPressRelease

    # 中心线
    cline_centers, cline_center_props = [], []
    cline_radiuss, cline_wires, cline_wire_props = [], [], []
    cline_curve_prop = vmi.PolyActor(voi_view, rgb=[0.4, 0.6, 1], line=3)
    cline_tube_prop = vmi.PolyActor(voi_view, rgb=[0.4, 0.6, 1])

    cline_tube_box = vmi.TextBox(voi_view, text='血管', pickable=True,
                                 size=[0.24, 0.04], pos=[0, 0.16], anchor=[0, 0])
    cline_tube_box.mouse['LeftButton']['PressRelease'] = LeftButtonPressRelease

    cline_tube_visible_box = vmi.TextBox(voi_view, back_color=QColor.fromRgbF(0.4, 0.6, 1),
                                         size=[0.01, 0.04], pos=[0.24, 0.16], anchor=[1, 0], pickable=True)
    cline_tube_visible_box.mouse['LeftButton']['PressRelease'] = LeftButtonPressRelease

    cline_clear_box = vmi.TextBox(voi_view, text='清空', pickable=True,
                                  size=[0.06, 0.04], pos=[0, 0.2], anchor=[0, 0])
    cline_clear_box.mouse['LeftButton']['PressRelease'] = LeftButtonPressRelease

    cline_data_open_box = vmi.TextBox(voi_view, text='导入', pickable=True,
                                      size=[0.06, 0.04], pos=[0.06, 0.2], anchor=[0, 0])
    cline_data_open_box.mouse['LeftButton']['PressRelease'] = LeftButtonPressRelease

    cline_data_save_box = vmi.TextBox(voi_view, text='导出', pickable=True,
                                      size=[0.06, 0.04], pos=[0.12, 0.2], anchor=[0, 0])
    cline_data_save_box.mouse['LeftButton']['PressRelease'] = LeftButtonPressRelease

    cline_tube_stl_box = vmi.TextBox(voi_view, text='STL', pickable=True,
                                     size=[0.06, 0.04], pos=[0.18, 0.2], anchor=[0, 0])
    cline_tube_stl_box.mouse['LeftButton']['PressRelease'] = LeftButtonPressRelease

    # 测量视图

    # 视图布局
    views = [original_view, voi_view]

    screen_width = QGuiApplication.screens()[0].geometry().width()
    for v in views:
        v.setMinimumWidth(0.5 * screen_width)

    for v in views[1:]:
        v.setEnabled(False)

    widget = QWidget()
    layout = QGridLayout(widget)
    layout.addWidget(original_view, 0, 0, 3, 1)
    layout.addWidget(voi_view, 0, 1, 3, 1)

    main = Main()
    main.setWidget(widget)

    vmi.appexec(main)  # 执行主窗口程序
    vmi.appexit()  # 清理并退出程序
