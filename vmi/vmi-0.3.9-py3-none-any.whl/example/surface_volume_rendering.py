import vmi


def view_surface(view, image, iso_value):
    pd = vmi.imIsosurface(image, iso_value)  # 提取CT值为iso_value的等值面，面绘制三维重建
    actor = vmi.PolyActor(view)  # 面绘制显示
    actor.clone(pd)  # 载入三维重建得到的面网格模型
    view.cameraFit()  # 自动调整视图的视野范围
    return actor


def view_volume(view, image, iso_value):
    volume = vmi.ImageVolume(view)  # 体绘制显示
    volume.clone(image)  # 载入读取到的DICOM图像
    volume.opacityScalar({iso_value - 1: 0, iso_value: 1})  # 设置像素和透明度之间的函数关系
    view.cameraFit()  # 自动调整视图的视野范围
    return view, volume


if __name__ == '__main__':
    from PySide2.QtWidgets import QWidget, QHBoxLayout
    from vmi.example.read_dicom_slice_view import read_dicom

    image = read_dicom()  # 读取DICOM路径
    if image is None:
        vmi.appexit()

    iso_value = vmi.askInt(-1000, 200, 3000, None, 'HU')  # 用户输入-1000HU至3000HU范围内的一个CT值
    if iso_value is None:
        vmi.appexit()

    surface_view = vmi.View()  # 面绘制视图
    volume_view = vmi.View()  # 体绘制视图

    view_surface(surface_view, image, iso_value)
    view_volume(volume_view, image, iso_value)

    # 创建窗口包含两个视图
    widget = QWidget()
    layout = QHBoxLayout(widget)
    layout.addWidget(surface_view)
    layout.addWidget(volume_view)

    vmi.appexec(widget)  # 执行主窗口程序
    vmi.appexit()  # 清理并退出程序
