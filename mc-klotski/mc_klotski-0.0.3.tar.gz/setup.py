from setuptools import setup
setup(
    name='mc_klotski',
    version='0.0.3',
    author='魔扣少儿编程_Hugn',
    author_email='wang1183478375@outlook.com',
    url ='https://www.coding4fun.com.cn/',
    install_requires=['pygame>=1.9.4'
                      ],
    data_files=[('',['mc_klotski.py']),
                ('Images',['Images/1.png',
                           'Images/2.png',
                           'Images/3.png',
                           'Images/4.png',
                           'Images/5.png',
                           'Images/6.png',
                           'Images/7.png',
                           'Images/8.png',
                           'Images/9.png',
                           'Images/10.png'])
                ],
    packages = ['Images'],
    include_package_data = True, 
    zip_safe=False,
    )