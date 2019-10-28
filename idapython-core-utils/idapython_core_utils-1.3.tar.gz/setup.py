from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()


setup(name='idapython_core_utils',
      version='1.03',
      description='Utilities for developing IDAPython scripts',
      classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Disassemblers',
      ],
      keywords='ida api research reversing',
      url='https://xxx/idapython_core_utils',
      author='The Council of Pwners',
      author_email='carlos.g.prado@gmail.com',
      license='MIT',
      install_requires=[
        'networkx',
      ],
      extras_require={
        'dev': [
          'pytest',
          'pytest-pycodestyle'
        ]
      },
      packages=['idapython_core_utils'],
      include_package_data=True,
      zip_safe=False)
