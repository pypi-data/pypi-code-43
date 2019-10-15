from setuptools import setup
setup(
    name='mc_sprite',
    version='0.0.22',
    author='魔扣少儿编程_Hugn',
    author_email='',
    url ='https://www.coding4fun.com.cn/',
    install_requires=['pygame>=1.9.4'
                      ],
    packages = ['GameObject','Engine','Timer'],
    data_files=[('',['mc_sprite.py'])
                ],
    include_package_data = True, 
    zip_safe=False,
    )