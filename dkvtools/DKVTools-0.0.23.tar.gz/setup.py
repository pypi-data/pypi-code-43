# -*- coding:utf-8 -*-

from setuptools import setup
from setuptools import find_packages
from DKVTools import __version__

setup(
    name='DKVTools',
    version=__version__,
    description=(
        'Some useful functions.'
    ),
    long_description='Some useful functions.',
    author='dekiven',
    author_email='dekiven@163.com',
    # maintainer='<维护人员的名字>',
    # maintainer_email='<维护人员的邮件地址',
    license='BSD License',
    packages=find_packages(),
    # 将包内资源包含到打的包中，貌似仅支持wheel
    include_package_data = True,
    install_requires=[
        # 'Pillow',
        # 'other>=1.1'
    ],
    data_files=[
    	# data_files的元素都是元组，元组的第一个元素是文件要放入的文件夹名称，第二个元素是文件列表。这里需要注意的是，如果不想把文件放入文件夹，可以将元组的第一个元素指定为空字符串，此时要打包的文件要被放入根目录，这里根目录是指python解释器所在的目录。比如我需要将文件资源放入python解释器所在目录下的/Lib/site-packages/myfolder路径，myfolder是自定义的文件夹，元组的第一个元素就可以写‘Lib/site-packages/myfolder’，打包时会自动在指定位置新建一个名为myfolder的目录，将文件资源放入其中。
        # 详见：https://www.cnblogs.com/lyrichu/p/6818008.html
    ],
    platforms=['all'],
    url='https://www.baidu.com',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries'
    ],
)