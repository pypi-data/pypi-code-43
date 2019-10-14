from distutils.core import setup

setup(
    name='ddc_d2019_test_install_module', #这个名字可随便写,因为他没有什么用
    version='1.0.0',
    description='测试安装module',
    author='',
    author_email='',
    py_modules=['ddc_d2019.test01','ddc_d2019.test02']  #说明要发布的模块,这里包名必须是实际的
)