from threading import Thread
from PySide2.QtCore import *
import vmi
import sys
import numpy as np

W = vmi.View()
vmi.appwindow(W)


def NoButtonEnter(**kwargs):
    if kwargs['picked'] in Actor.values():
        kw = [kw for kw in Actor if Actor[kw] is kwargs['picked']][0]

        if kw in Actor:
            Text['显示名称'].draw_text('{}'.format(kw))
        return Actor[kw].mouseEnter(**kwargs)


def NoButtonLeave(**kwargs):
    if kwargs['picked'] in Actor.values():
        kw = [kw for kw in Actor if Actor[kw] is kwargs['picked']][0]
        Text['显示名称'].draw_text('')
        return Actor[kw].mouseLeave(**kwargs)


def LeftButtonPressRelease(**kwargs):
    if kwargs['picked'] in Actor.values():
        kw = [kw for kw in Actor if Actor[kw] is kwargs['picked']][0]

        if kwargs['double']:
            text = '{}-{}-{}-{}-{}-{}-{}-{}'.format(Data['长度'], Data['宽度'], Data['高度中'],
                                                    Data['高度尾'], Data['高度头'], Data['高度前'], Data['高度后'], kw)
            vmi.app.clipboard().setText(text)
            vmi.ccSaveFile_STEP(Data[kw])


def NoButtonWheel(**kwargs):
    if kwargs['picked'] in Actor.values():
        kw = [kw for kw in Actor if Actor[kw] is kwargs['picked']][0]
        Actor[kw].rgb(alpha=(1 if Actor[kw].rgb()['alpha'] < 1 else 0.1))


def Input(args):
    args = dict(zip(InputKeys, args))

    for kw in args:
        try:
            args[kw] = float(args[kw])
        except:
            pass

    Data.update(args)


def Rebuild():
    W.updateInTime()
    time = QTime()
    time.start()

    global Data
    text = '输入'
    for k in InputKeys:
        text += ' ' + str(Data[k])
    print(text)

    print('{:.2f}'.format(time.elapsed() / 1e3), '开始')

    Data['左'] = np.array([1, 0, 0], np.float)
    Data['后'] = np.array([0, 1, 0], np.float)
    Data['上'] = np.array([0, 0, 1], np.float)
    Data['原点'] = np.array([0, 0, 0], np.float)

    Data['长向'] = (-1 if Data['后路侧'] > 0 else 1) * Data['左']
    Data['入旋向'] = np.cross(Data['长向'], Data['后'])

    Data['长向'] = vmi.CS4x4().rotate(-Data['横偏角'], Data['入旋向']).mvt(Data['长向'])
    Data['宽向'] = np.cross(Data['入旋向'], Data['长向'])
    Data['高向'] = Data['上']

    lh, wh, th = 0.5 * Data['长度'], 0.5 * Data['宽度'], Data['壁厚']

    # 长宽高坐标系
    cs = vmi.CS4x4(origin=Data['原点'],
                   axis0=Data['长向'],
                   axis1=Data['宽向'],
                   axis2=Data['高向'])

    # 长宽坐标
    length_width = np.array([
        [[-(lh - wh), -wh], [-lh, -0.5 * wh], [-(lh - 1.5 * wh), wh]],
        [[0, -wh], [0, 0], [0, wh]],
        [[lh - 1.5 * wh, -wh], [lh, 0.5 * wh], [lh - wh, wh]]], np.float)

    # 高坐标
    height = np.array([
        [0, Data['高度尾'], 0],
        [Data['高度前'], Data['高度中'], Data['高度后']],
        [0, Data['高度头'], 0]], np.float)

    height[0][0] = 0.5 * (height[0][1] + height[1][0])
    height[0][2] = 0.5 * (height[0][1] + height[1][2])
    height[2][0] = 0.5 * (height[2][1] + height[1][0])
    height[2][2] = 0.5 * (height[2][1] + height[1][2])

    points = {}

    # 外侧底面点
    Data['点外下'] = np.zeros((3, 3, 3), np.float)
    for j in range(3):
        for i in range(3):
            Data['点外下'][j][i] = cs.mpt([*length_width[j][i], 0])

    # 外侧顶面点
    Data['点外上'] = np.zeros((3, 3, 3), np.float)
    for j in range(3):
        for i in range(3):
            Data['点外上'][j][i] = cs.mpt([0, 0, height[j][i]], origin=Data['点外下'][j][i])

    # 内侧底面点
    Data['点内下'] = np.zeros((3, 3, 3), np.float)
    for j in range(3):
        for i in range(3):
            Data['点内下'][j][i] = cs.mpt([0, 0, th], origin=Data['点外下'][j][i])

    # 内侧顶面点
    Data['点内上'] = np.zeros((3, 3, 3), np.float)
    for j in range(3):
        for i in range(3):
            Data['点内上'][j][i] = cs.mpt([0, 0, -th], origin=Data['点外上'][j][i])

    # 内侧点向内缩进
    for inner in [Data['点内下'], Data['点内上']]:
        inner[0][0] = cs.mpt([0, th, 0], origin=inner[0][0])
        inner[0][1] = cs.mpt([th, 0, 0], origin=inner[0][1])
        inner[0][2] = cs.mpt([0, -th, 0], origin=inner[0][2])
        inner[1][0] = cs.mpt([0, th, 0], origin=inner[1][0])
        inner[1][2] = cs.mpt([0, -th, 0], origin=inner[1][2])
        inner[2][0] = cs.mpt([0, th, 0], origin=inner[2][0])
        inner[2][1] = cs.mpt([-th, 0, 0], origin=inner[2][1])
        inner[2][2] = cs.mpt([0, -th, 0], origin=inner[2][2])

    # 显示点
    pts = []
    for pt in [Data['点外下'], Data['点外上'], Data['点内下'], Data['点内上']]:
        for j in range(3):
            for i in range(3):
                pts.append(vmi.ccVertex(pt[j][i]))
    Data['点'] = vmi.ccBoolean_Union(pts)

    # 切向量
    tg_xy = np.array(
        [[[-2, 0], [0, 1], [2, 1]],
         [[0, 1], [0, 1], [0, 1]],
         [[2, 1], [0, 1], [-2, 0]]])

    tg = np.zeros((3, 3, 3), np.float)
    for j in range(3):
        for i in range(3):
            tg[j][i] = cs.mvt([*tg_xy[j][i], 0])

    # 切向量约束状态
    tgflag = [[True, True, True], [False, True, False], [True, True, True]]

    for l in ['外', '内']:
        for k in ['下', '上']:
            Data['宽边' + l + k] = [0] * 3

            for j in range(3):
                if l == '外':
                    curve = vmi.ccBSpline(Data['点' + l + k][j], tg[j], tgflag[j])
                else:
                    curve = vmi.ccSegment(Data['点' + l + k][j][0], Data['点' + l + k][j][2])

                Data['宽边' + l + k][j] = vmi.ccEdge(curve)

                kw = '宽边' + l + ['尾', '中', '头'][j] + k
                Data[kw] = Data['宽边' + l + k][j]

        for k in ['下', '上']:
            Data['端面' + l + k] = vmi.ccLoft(Data['宽边' + l + k])

            endpts = [vmi.ccEdge_FirstLastPoint(Data['宽边' + l + k][i]) for i in [0, 2]]
            for edge in vmi.ccExplore_Recursive(Data['端面' + l + k], vmi.TopAbs_EDGE):
                pts = vmi.ccEdge_FirstLastPoint(edge)
                if pts[0] in [endpts[0][0], endpts[1][0]] and pts[1] in [endpts[0][0], endpts[1][0]]:
                    Data['长边' + l + k + '前'] = edge
                elif pts[0] in [endpts[0][1], endpts[1][1]] and pts[1] in [endpts[0][1], endpts[1][1]]:
                    Data['长边' + l + k + '后'] = edge

        Data['端面' + l + '右'] = vmi.ccLoft([Data['宽边' + l + '下'][0], Data['宽边' + l + '上'][0]], ruled=True)
        Data['端面' + l + '左'] = vmi.ccLoft([Data['宽边' + l + '下'][2], Data['宽边' + l + '上'][2]], ruled=True)

        for j in ['前', '后']:
            Data['端面' + l + j] = vmi.ccLoft([Data['长边' + l + '下' + j], Data['长边' + l + '上' + j]], ruled=True)

        Data['实体' + l] = vmi.ccSolid(vmi.ccSew([Data['端面' + l + i] for i in ['下', '上', '右', '左', '前', '后']]))

    solid = vmi.ccBoolean_Difference([Data['实体外'], Data['实体内']])

    print('{:.2f}'.format(time.elapsed() / 1e3), '创建外壳')

    pts = [[cs.mpt([0, 0, 0], origin=Data['点内下'][0][0]),
            cs.mpt([0, 0, 0], origin=Data['点内上'][0][0]),
            cs.mpt([0.25 * wh - 0.5 * th, 0, 0], origin=Data['点内下'][1][0]),
            cs.mpt([0.25 * wh - 0.5 * th, 0, 0], origin=Data['点内上'][1][0]),
            cs.mpt([0.25 * wh + 0.5 * th, 0, 0], origin=Data['点内下'][1][0]),
            cs.mpt([0.25 * wh + 0.5 * th, 0, 0], origin=Data['点内上'][1][0]),
            cs.mpt([0, 0, 0], origin=Data['点内下'][2][0]),
            cs.mpt([0, 0, 0], origin=Data['点内上'][2][0])],
           [cs.mpt([0, 0, 0], origin=Data['点内下'][0][2]),
            cs.mpt([0, 0, 0], origin=Data['点内上'][0][2]),
            cs.mpt([-0.25 * wh - 0.5 * th, 0, 0], origin=Data['点内下'][1][2]),
            cs.mpt([-0.25 * wh - 0.5 * th, 0, 0], origin=Data['点内上'][1][2]),
            cs.mpt([-0.25 * wh + 0.5 * th, 0, 0], origin=Data['点内下'][1][2]),
            cs.mpt([-0.25 * wh + 0.5 * th, 0, 0], origin=Data['点内上'][1][2]),
            cs.mpt([0, 0, 0], origin=Data['点内下'][2][2]),
            cs.mpt([0, 0, 0], origin=Data['点内上'][2][2])]]

    cut = [[vmi.ccWire(vmi.ccSegments([pts[0][0], pts[0][1], pts[0][3], pts[0][2]], True)),
            vmi.ccWire(vmi.ccSegments([pts[0][7], pts[0][6], pts[0][4], pts[0][5]], True))],
           [vmi.ccWire(vmi.ccSegments([pts[1][0], pts[1][1], pts[1][3], pts[1][2]], True)),
            vmi.ccWire(vmi.ccSegments([pts[1][7], pts[1][6], pts[1][4], pts[1][5]], True))]]
    cut = [[vmi.ccPrism(vmi.ccFace(c), [-i for i in Data['宽向']], th) for c in cut[0]],
           [vmi.ccPrism(vmi.ccFace(c), Data['宽向'], th) for c in cut[1]]]

    solid = vmi.ccBoolean_Difference([solid, *cut[0], *cut[1]])

    porous = vmi.ccBoolean_Union(cut[0] + cut[1])

    print('{:.2f}'.format(time.elapsed() / 1e3), '创建前后窗')

    pts = [cs.mpt([0, 0, -th], Data['点内下'][0][0]),
           cs.mpt([0, 0, -th], Data['点内下'][0][2]),
           cs.mpt([0.25 * wh - 0.5 * th, 0, -th], Data['点内下'][1][0]),
           cs.mpt([-0.25 * wh - 0.5 * th, 0, -th], Data['点内下'][1][2]),
           cs.mpt([0.25 * wh + 0.5 * th, 0, -th], Data['点内下'][1][0]),
           cs.mpt([-0.25 * wh + 0.5 * th, 0, -th], Data['点内下'][1][2]),
           cs.mpt([0, 0, -th], Data['点内下'][2][0]),
           cs.mpt([0, 0, -th], Data['点内下'][2][2])]

    cut = [vmi.ccSegments([pts[0], pts[1], pts[3], pts[2]], True),
           vmi.ccSegments([pts[4], pts[5], pts[7], pts[6]], True)]
    cut = [vmi.ccWire([vmi.ccEdge(c) for c in cut[0]]),
           vmi.ccWire([vmi.ccEdge(c) for c in cut[1]])]
    cut = [vmi.ccPrism(vmi.ccFace(c), Data['高向'], 2 * Data['高度中']) for c in cut]

    if not Data['植骨窗'] > 0:
        porous = vmi.ccBoolean_Union([vmi.ccBoolean_Intersection([solid, *cut]), porous])
        print('{:.2f}'.format(time.elapsed() / 1e3), '创建植骨窗')

    solid = vmi.ccBoolean_Difference([solid, *cut])

    print('{:.2f}'.format(time.elapsed() / 1e3), '创建上下窗')

    if Data['植骨孔'] > 0:
        hmin = min(height[2][0] - th, height[2][1], height[2][2] - th)
        r = min(0.5 * (hmin - th), wh - th) - 0.5
        Data['植骨孔直径'] = 2 * r
        cut = cs.mpt([0, 0, (hmin + th) / 2], Data['点外下'][1][1])
        cut = vmi.ccCylinder(r, Data['长度'], cut, Data['长向'], Data['高向'])
        solid = vmi.ccBoolean_Difference([solid, cut])

        print('{:.2f}'.format(time.elapsed() / 1e3), '创建植骨孔')

    l, w, h = wh - th, 0.5 * Data['夹持宽度'], 0.5 * Data['夹持高度']
    pts = [cs.mpt([-lh, -w - 0.25 * wh, 0.5 * Data['高度尾'] - h], Data['原点']),
           cs.mpt([-lh, -(w + wh) - 0.25 * wh, 0.5 * Data['高度尾'] - h], Data['原点']),
           cs.mpt([-(lh - l), -w - 0.25 * wh, 0.5 * Data['高度尾'] - h], Data['原点']),
           cs.mpt([-(lh - l), -(w + wh) - 0.25 * wh, 0.5 * Data['高度尾'] - h], Data['原点']),
           cs.mpt([-lh, w - 0.25 * wh, 0.5 * Data['高度尾'] - h], Data['原点']),
           cs.mpt([-lh, w + wh - 0.25 * wh, 0.5 * Data['高度尾'] - h], Data['原点']),
           cs.mpt([-(lh - l), w - 0.25 * wh, 0.5 * Data['高度尾'] - h], Data['原点']),
           cs.mpt([-(lh - l), w + wh - 0.25 * wh, 0.5 * Data['高度尾'] - h], Data['原点'])]

    box = [vmi.ccWire(vmi.ccSegments([pts[0], pts[1], pts[3], pts[2]], True)),
           vmi.ccWire(vmi.ccSegments([pts[4], pts[5], pts[7], pts[6]], True))]
    box = [vmi.ccPrism(vmi.ccFace(b), Data['高向'], 2 * h) for b in box]
    box = vmi.ccBoolean_Union([box[0], box[1]])
    solid = vmi.ccBoolean_Difference([solid, box])

    print('{:.2f}'.format(time.elapsed() / 1e3), '创建夹持槽')

    n = int(vmi.ccLength(Data['宽边外下'][0]) / Data['敲击带半径'])
    pts = [np.array(vmi.ccUniformPts_Edge(Data['宽边外下'][0], n + 1)),
           np.array(vmi.ccUniformPts_Edge(Data['宽边外上'][0], n + 1))]
    for i in range(2, n + 1 - 2, 3):
        c = [cs.mpt([0, 0, 0.5 * Data['高度尾']], pts[0][i - 2]),
             cs.mpt([0, 0, 0.5 * Data['高度尾']], pts[0][i]),
             cs.mpt([0, 0, 0.5 * Data['高度尾']], pts[0][i + 2])]

        cylinders = []
        if not vmi.ccInside_Pt(box, c[0]) and not vmi.ccInside_Pt(box, c[1]) and not vmi.ccInside_Pt(box, c[2]):
            h = np.linalg.norm(pts[0][i] - pts[1][i]) - 2 * th
            o = cs.mpt([0, 0, th], pts[0][i])
            cylinders.append(vmi.ccCylinder(Data['敲击带半径'], h, o, Data['高向'], Data['长向']))

        solid = vmi.ccBoolean_Union([solid, *cylinders])

    print('{:.2f}'.format(time.elapsed() / 1e3), '创建敲击带')

    Data['实体'], Data['多孔'] = solid, porous
    Actor['实体'].clone(solid)
    Actor['多孔'].clone(porous)

    print('{:.2f}'.format(time.elapsed() / 1e3), '离散化')


InputKeys = ['后路侧', '横偏角',
             '长度', '宽度',
             '高度中', '高度尾', '高度头', '高度前', '高度后',
             '壁厚',
             '植骨窗', '植骨孔',
             '夹持宽度', '夹持高度',
             '敲击带半径']

Data = {'后路侧': 1, '横偏角': 15,
        '长度': 32, '宽度': 12,
        '高度中': 14, '高度尾': 12, '高度头': 12, '高度前': 13, '高度后': 13,
        '壁厚': 1.5,
        '植骨窗': 0, '植骨孔': 1, '植骨孔直径': 0.5,
        '夹持宽度': 3, '夹持高度': 3,
        '敲击带半径': 0.3}

Input(sys.argv[1:])

Actor, Text = {}, {}


def info():
    text = '输入 (mm)' + '\n\n'
    text += '后路侧: ' + ('左' if Data['后路侧'] > 0 else '右') + '\n'
    text += '横偏角: ' + str(Data['横偏角']) + '°' + '\n'
    text += '长度: ' + str(Data['长度']) + '\n'
    text += '宽度: ' + str(Data['宽度']) + '\n'
    text += '高度: ' + '中 ' + str(Data['高度中']) + \
            ' 尾 ' + str(Data['高度尾']) + ' 头 ' + str(Data['高度头']) + \
            ' 前 ' + str(Data['高度前']) + ' 后 ' + str(Data['高度后']) + '\n'
    text += '壁厚: ' + str(Data['壁厚']) + '\n'
    text += '植骨窗: ' + ('启用' if Data['植骨窗'] > 0 else '禁用') + '\n'
    text += '植骨孔: ' + ('启用' if Data['植骨孔'] > 0 else '禁用') + ' 直径: {:.2f}'.format(Data['植骨孔直径']) + '\n'
    text += '夹持槽: ' + '宽度 ' + str(Data['夹持宽度']) + ' 高度 ' + str(Data['夹持高度']) + '\n'
    text += '敲击带: ' + '半径 ' + str(Data['敲击带半径']) + '\n'

    print(text)


Actor['点'] = vmi.PolyActor(W, name='点', rgb=[0.2, 0.6, 1], point=8, pickable=True)
Actor['点'].mouse['NoButton']['Enter'] = NoButtonEnter
Actor['点'].mouse['NoButton']['Leave'] = NoButtonLeave

for l in ['外', '内']:
    for k in ['下', '上']:
        for j in ['尾', '中', '头']:
            kw = '宽边' + l + j + k
            Actor[kw] = vmi.PolyActor(W, name=kw, rgb=[1, 0.2, 0.2], line=4, pickable=True)
            Actor[kw].mouse['NoButton']['Enter'] = NoButtonEnter
            Actor[kw].mouse['NoButton']['Leave'] = NoButtonLeave

    for k in ['下', '上']:
        for kw in ['长边' + l + k + kk for kk in ['前', '后']]:
            Actor[kw] = vmi.PolyActor(W, name=kw, rgb=[1, 0.2, 0.2], line=4, pickable=True)
            Actor[kw].mouse['NoButton']['Enter'] = NoButtonEnter
            Actor[kw].mouse['NoButton']['Leave'] = NoButtonLeave

kw = '实体'
Actor[kw] = vmi.PolyActor(W, name=kw, rgb=[0.9, 0.9, 0.9], pickable=True)
Actor[kw].mouse['NoButton']['Enter'] = NoButtonEnter
Actor[kw].mouse['NoButton']['Leave'] = NoButtonLeave
Actor[kw].mouse['LeftButton']['PressRelease'] = LeftButtonPressRelease
Actor[kw].mouse['NoButton']['Wheel'] = NoButtonWheel

kw = '多孔'
Actor[kw] = vmi.PolyActor(W, name=kw, rgb=[0.9, 0.5, 0.5], pickable=True)
Actor[kw].mouse['NoButton']['Enter'] = NoButtonEnter
Actor[kw].mouse['NoButton']['Leave'] = NoButtonLeave
Actor[kw].mouse['LeftButton']['PressRelease'] = LeftButtonPressRelease
Actor[kw].mouse['NoButton']['Wheel'] = NoButtonWheel

Text['显示名称'] = vmi.TextBox(W, text_align=Qt.AlignCenter, size=[0.1, 0.05], pos=[0, 1], anchor=[0, 1])

T = Thread(target=Rebuild)
T.start()
vmi.appwait(T)

info()

W.cameraCoronal()
W.cameraReverse()
W.cameraFit()
vmi.appexec(W)
