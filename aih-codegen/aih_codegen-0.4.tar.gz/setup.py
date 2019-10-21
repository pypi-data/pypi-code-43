from setuptools import setup

setup(name='aih_codegen',
      version='0.4',
      description='Generate graphql code',
      url='https://github.com/quyencao/aih_generate',
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