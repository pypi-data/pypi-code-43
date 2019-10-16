import vmi
from PySide2.QtGui import Qt, QImage, QColor, QPainter


def read_png() -> QImage:
    """读取*.png文件"""
    file_name = vmi.askOpenFile('*.png')
    if file_name is not None:
        image = QImage(file_name)
        if image:
            return image


def LeftButtonPressRelease(**kwargs):
    if kwargs['picked'] is image_box:
        # 重新读取png图像
        png = read_png()
        if png is not None:
            image_box.draw(png)
    elif kwargs['picked'] is click_box:
        # 切换选项
        options = ['单击', '再击', '三击']
        options = dict(zip(options, [*options[1:], options[0]]))
        click_box.draw_text(options[click_box.text()])
    elif kwargs['picked'] is value_box:
        # 输入数值
        global value
        v = vmi.askInt(0, value, 100)
        if v is not None:
            value = vmi.askInt(0, value, 100)
            draw_value()


def NoButtonWheel(**kwargs):
    if kwargs['picked'] is value_box:
        global value
        value = min(max(value + kwargs['delta'], 0), 100)  # 控制数值范围
        draw_value()  # 更新绘图框


def draw_value():
    """自定义绘图"""
    value_box.draw_text(text='滚轮或单击：{}'.format(value))

    w, h = value_draw_box.size()[0] * view.width(), value_draw_box.size()[1] * view.height()
    painter = QPainter()
    image = QImage(w, h, value_draw_box.image().format())
    painter.begin(image)

    painter.fillRect(0, 0, w, h, QColor('white'))
    painter.fillRect(0, 0, value / 100 * w, h, QColor('lightskyblue'))

    painter.end()
    value_draw_box.draw(image)


if __name__ == '__main__':
    png = read_png()  # 读取PNG图像
    if png is None:  # 判断用户是否有效读取了模型文件
        vmi.appexit()  # 清理并退出程序

    view = vmi.View()  # 视图

    # 画一个三维物体作参照
    mesh_prop = vmi.PolyActor(view, rgb=[1, 1, 0.6])
    mesh_prop.clone(vmi.ccCylinder(5, 20, [0, 0, 0], [0, -1, -1]))

    # 绘图框，显示外部png图像
    # siz：视图中的显示尺寸，视图宽高的比例
    # pos：视图中的对齐位置，视图宽高的比例
    # anchor：图像中的对齐位置，图像宽高的比例
    image_box = vmi.ImageBox(view, image=png, size=[0.2, 0.4], pos=[1, 0.1], anchor=[1, 0], pickable=True)
    image_box.mouse['LeftButton']['PressRelease'] = LeftButtonPressRelease

    # 文本框，fore_color文本颜色，back_color背景颜色
    # bold：粗体
    # italic：斜体
    # underline：下划线
    # 颜色名称：https://www.w3.org/wiki/CSS/Properties/color/keywords
    text_box = vmi.TextBox(view, text='静态文本' + ' ' * 10,
                           text_color=QColor('white'), back_color=QColor('crimson'),
                           bold=True, italic=True, underline=True,
                           size=[0.2, 0.04], pos=[0, 0.1], anchor=[0, 0])

    # 单击框，text_align组合文本对齐方式
    # 水平：Qt.AlignLeft/Qt.AlignRight/Qt.AlignHCenter
    # 竖直：Qt.AlignTop/Qt.AlignBottom/Qt.AlignVCenter/Qt.AlignBaseline
    # 水平竖直：Qt.AlignCenter
    click_box = vmi.TextBox(view, text='单击', text_align=Qt.AlignCenter,
                            size=[0.2, 0.04], pos=[0, 0.14], anchor=[0, 0], pickable=True)
    click_box.mouse['LeftButton']['PressRelease'] = LeftButtonPressRelease

    # 数值框
    value = 50
    value_box = vmi.TextBox(view, size=[0.2, 0.04], pos=[0, 0.45], anchor=[0, 0], pickable=True)
    value_box.mouse['LeftButton']['PressRelease'] = LeftButtonPressRelease
    value_box.mouse['NoButton']['Wheel'] = NoButtonWheel

    # 绘图框，自定义绘图
    value_draw_box = vmi.ImageBox(view, size=[0.2, 0.01], pos=[0, 0.49], anchor=[0, 0])

    # 初始化
    draw_value()

    view.cameraFit()  # 自动调整视图的视野范围
    vmi.appexec(view)  # 执行主窗口程序
    vmi.appexit()  # 清理并退出程序
