from distutils.core import setup


# 导入setup函数并传参
setup(name='glooweb',
      version='0.1.1',
      description='Simple web framework based on WSGI protocol',
      author='gloo',
      author_email='gloo.luo@foxmail.com',
      packages=['glooweb'],
      install_requires=[
          'Webob>=1.8.5'
      ]
      )
