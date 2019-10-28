from setuptools import setup

setup(name='aih_codegen',
      version='0.13',
      description='Generate graphql code',
      url='https://github.com/quyencao/aih_codegen',
      author='aih',
      author_email='quyen.cm@example.com',
      license='MIT',
      packages=['aih_codegen'],
      install_requires=[
          'JinJa2',
          'six',
          'PyYAML'
      ],
      scripts=['bin/aih'],
      zip_safe=False,
      include_package_data=True,
      python_requires='>=3.6')