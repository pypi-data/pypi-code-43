from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()


setup(
    name='CollectiveIntelligence',
    version='0.1.4',
    description='Collective Intelligence modules',
    long_description=readme(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
    ],
    project_urls={
        'Homepage': 'http://github.com/10fish/CollectiveIntelligence',
        'Source Code': 'http://github.com/10fish/CollectiveIntelligence',
    },
    author='10fish',
    author_email='ohth@sina.com',
    license='MIT',
    packages=['recommandations', 'clustering'],
    install_requires=[
        'markdown',
    ],
    zip_safe=False
)
