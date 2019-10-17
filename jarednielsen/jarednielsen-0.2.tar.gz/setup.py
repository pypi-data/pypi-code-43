from distutils.core import setup

setup(
    name='jarednielsen',
    packages=['jarednielsen'],
    version='0.2',
    license='MIT',
    description='Uploading my first package to PyPi',
    author='Jared Nielsen',
    author_email='jaredtnielsen@gmail.com',
    url='https://jaredtn.com',
    download_url='https://jaredtn.com',
    keywords=['SOME', 'MEANINGFUL', 'KEYWORDS'],
    install_requires=[
        'numpy',
    ],
    classifiers=[
        'Programming Language :: Python :: 3.7',
    ],
)