from setuptools import setup, find_packages


setup(
    name='clldlucl',
    version='3.0.0-beta2',
    description=(
        'Python library supporting development of CLLD apps maintained by LUCL'),
    long_description='',
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
    ],
    keywords='web pyramid',
    author="Gereon A. Kaiping",
    author_email="g.a.kaiping@hum.leidenuniv.nl",
    url="http://clld.org",
    license="Apache Software License",
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'clld',
        'purl',
        'clldutils',
    ],
    extras_require={
        'test': [
            'mock>=2.0',
            'pytest-clld',
            'pytest-mock',
            'coverage>=4.2',
            'pytest-cov',
        ],
        'dev': [
            'tox',
            'flake8',
            'wheel',
            'twine',
        ],
    },
    message_extractors={'src/clldlucl': [
        ('**.py', 'python', None),
        ('**.mako', 'mako', None),
        ('static/**', 'ignore', None)]},
    entry_points={
        'pyramid.scaffold': ['clldlucl_app=clldlucl.scaffolds:ClldAppTemplate'],
        'console_scripts': ['clldlucl=clldlucl.__main__:main'],
    },
)
