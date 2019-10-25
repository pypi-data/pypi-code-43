from distutils.core import setup

setup(
    name = 'baizhanSuperMath12', #对外我们模块的名字
    version = '1.0', #版本号
    description='这是第一个对外发布的模块，里面只有数学方法，用于测试哦',  #描述
    author='qiuyang11', #作者
    author_email='1227570389@qq.com',
    py_modules = ['baizhanSuperMath12.demo1','baizhanSuperMath12.demo2']  #要发布的模块
)