from distutils.core import setup

setup(
    name='wangyesupermath',#对外我们模块的名字
    version='1.0',#版本号
    description='这是第一个对外发布的模块',#描述
    aythor='zhangxingzhi', #作者
    author_email='860730354@qq.com',
    py_modules=['wangyesupermath.demo01', 'wangyesupermath.demo02']  #要发布的模块
)