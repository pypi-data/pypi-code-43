import vmi
import numpy as np


def reslice_blend():
    left_top = view[1].pickFPlane([0, 0])  # 拾取视图左上角的焦平面点
    right_top = view[1].pickFPlane([view[1].width(), 0])  # 拾取视图右上角的焦平面点
    left_bottom = view[1].pickFPlane([0, view[1].height()])  # 拾取视图左下角的焦平面点

    cs = view[1].cameraCS()  # 获得视角坐标系

    xl = np.linalg.norm(left_top - right_top)  # 视图左右方向的真实尺度
    yl = np.linalg.norm(left_top - left_bottom)  # 视图上下方向的真实尺度
    zl = vmi.imSize_Vt(image, cs.axis(2))  # 图像沿视图入射方向的最大包围盒尺寸

    pt = vmi.imCenter(image) - 0.5 * zl * cs.axis(2)  # 计算图像包围盒中心到近平面投影点
    cs.origin(vmi.ptOnPlane(cs.origin(), pt, cs.axis(2)))  # 将坐标系原点投影到近平面

    # 重采样混叠，背景体素值-1024，平均密度投影，忽略-200以下的体素值
    image_blend = vmi.imReslice_Blend(image, cs, [xl, yl, zl], -1024, 'mean', -200)

    # 更新视图
    blend_prop.clone(image_blend)
    blend_prop.windowSoft()
    view[0].cameraFit()


if __name__ == '__main__':
    from PySide2.QtWidgets import QWidget, QHBoxLayout
    from vmi.example.read_dicom_slice_view import read_dicom

    image = read_dicom()  # 读取DICOM路径
    if image is None:
        vmi.appexit()

    iso_value = vmi.askInt(-1000, 200, 3000, None, 'HU')  # 用户输入-1000HU至3000HU范围内的一个CT值
    if iso_value is None:
        vmi.appexit()

    view = [vmi.View(), vmi.View()]  # 左右视图
    blend_prop = vmi.ImageSlice(view[0])  # 左视图显示混叠图像

    menu = vmi.Menu()  # 右键菜单
    view[1].mouse['RightButton']['PressRelease'] = menu.menuexec  # 连接右视图的右键信号到菜单

    menu.menu.addSection('自定义')  # 添加分割线
    menu.menu.addAction('重采样混叠').triggered.connect(reslice_blend)  # 创建并连接菜单选项
    menu.menu.addSection('视图')  # 添加分割线
    menu.menu.addActions(view[1].menu.actions())  # 添加右视图原有菜单

    mesh_prop = vmi.PolyActor(view[1], rgb=[1, 1, 0.6])  # 右视图显示模型
    mesh_prop.clone(vmi.imIsosurface(image, iso_value))  # 三维重建并显示
    view[1].cameraCoronal()
    view[1].cameraFit()  # 重置视野范围

    # 创建窗口包含两个视图
    widget = QWidget()
    layout = QHBoxLayout(widget)
    layout.addWidget(view[0])
    layout.addWidget(view[1])

    vmi.appexec(widget)  # 执行主窗口程序
    vmi.appexit()  # 清理并退出程序
