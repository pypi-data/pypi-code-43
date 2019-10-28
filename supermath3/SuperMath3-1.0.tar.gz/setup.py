from distutils.core import setup

setup(
    name='SuperMath3',     #对外模块的名字
    version='1.0',       #版本号
    description='这是个对外发布的测试模块',   #模块的描述
    author='wang',         #作者
    author_email='wangzhenxu91@gmail.com',
    py_modules=['SuperMath3.demo1','SuperMath3.demo2']    #要发布的模块
)
