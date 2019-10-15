from distutils.core import setup


with open("README.md", "r", encoding="utf8") as fh:
    long_description = fh.read()


# # 导入setup函数并传参
setup(name='glooweb',
      version='0.1.3',
      description='Simple web framework based on WSGI protocol',
      # long_description=long_description,
      # long_description=long_description,
      # long_description_content_type='text/markdown',
      author='gloo',
      author_email='gloo.luo@foxmail.com',
      packages=['glooweb'],
      install_requires=[
          'Webob>=1.8.5'
      ],
      data_files=["./README.md"]
      )
