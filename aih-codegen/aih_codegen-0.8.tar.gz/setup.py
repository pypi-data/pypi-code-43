from setuptools import setup

setup(name='aih_codegen',
      version='0.8',
      description='Generate graphql code',
      url='https://github.com/quyencao/aih_codegen',
      author='aih',
      author_email='flyingcircus@example.com',
      license='MIT',
      packages=['aih_codegen'],
      install_requires=[
          'JinJa2',
          'six',
          'PyYAML'
      ],
      scripts=['bin/aih'],
      include_package_data=True,
      zip_safe=False)