import vmi

if __name__ == '__main__':
    from vmi.example.read_dicom_slice_view import read_dicom
    from vmi.example.surface_volume_rendering import view_surface

    image = read_dicom()  # 读取DICOM路径
    if image is None:
        vmi.appexit()

    iso_value = vmi.askInt(-1000, 200, 3000, None, 'HU')  # 用户输入-1000HU至3000HU范围内的一个CT值
    if iso_value is None:
        vmi.appexit()

    pts = []  # 取点列表


    def rebuild():
        """构造曲线"""
        if len(pts) > 1:  # 如果有2个点以上，可以构造曲线
            curve = vmi.ccBSpline_Kochanek(pts)  # 由多个点坐标构造几何曲线
            edge = vmi.ccEdge(curve)  # 由几何曲线构造拓扑边
            prop_curve.clone(edge)  # 传入shape数据
        else:  # 如果没有点或只有1个点，不能构造曲线
            prop_curve.clone()  # 重置shape数据


    def LeftButtonPressRelease(**kwargs):
        """响应左键点击"""
        if kwargs['picked'] is prop_mesh:  # 判断鼠标拾取到的是模型
            if kwargs['double'] is False:  # 鼠标单击时
                pt = view.mouseOnPropCell()  # 在视图中取物体表面点
                pts.append(pt)  # 添加进取点列表
                rebuild()  # 重新构造曲线
            else:  # 鼠标双击时
                pts.clear()  # 清空取点列表
                rebuild()  # 重新构造曲线
            return prop_mesh.mouseRelease()


    view = vmi.View()  # 视图

    prop_mesh = view_surface(view, image, iso_value)  # 三维重建获得单元数据和表示
    prop_mesh.rgb([1, 1, 0.6])  # 颜色
    prop_mesh.pickable(True)  # 设置可拾取
    prop_mesh.mouse['LeftButton']['PressRelease'] = LeftButtonPressRelease  # 连接鼠标左键点击

    prop_curve = vmi.PolyActor(view)  # 曲线表示
    prop_curve.rgb([1, 0.4, 0.4])  # 颜色
    prop_curve.size(line=3)  # 设置线宽3个屏幕像素

    vmi.appexec(view)  # 执行主窗口程序
    vmi.appexit()  # 清理并退出程序
