from distutils.core import setup

setup(
    name='StuMath',#对外我们模块的名字
    version='1.0',#版本号
    description='这是第二个对外发布的模块',#描述
    aythor='zhangxingzhi', #作者
    author_email='860730354@qq.com',
    py_modules=['StuMath.student']  #要发布的模块
)