from setuptools import setup

setup(
    name='cf_netSDM',
    install_requires=['numpy>=1.7.1', 'rdflib>=4.2.2', 'Orange==3.7.0'],
    version='0.0.3',
    license='MIT License',
    description='ClowdFlows 3 module for network analysis for semantic data mining',
    url='https://github.com/JanKralj/cf_netSDM',
    author='Jan Kralj',
    author_email='jan.kralj@ijs.si',
    packages=['cf_netSDM', ],
    classifiers= ['Development Status :: 2 - Pre-Alpha',
                  'Environment :: Web Environment',
                  'Framework :: Django',
                  'Intended Audience :: Developers',
                  'License :: OSI Approved :: MIT License',
                  'Operating System :: OS Independent',
                  'Programming Language :: Python',
                  'Programming Language :: Python :: 3',
                  ],
    include_package_data=True,
)
