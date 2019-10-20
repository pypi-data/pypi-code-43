import setuptools


def readme():
    with open('README.md') as f:
        return f.read()


setuptools.setup(
    author='Ugo Popée',
    author_email='ugo.popee@me.com',
    name='nzbget-file-opener',
    version='1.0.1',
    url='http://github.com/bil0u/nzbget-file-opener',
    description='nzbget-file-opener allows you to download *.nzb files with just a double click',
    long_description=readme(),
    long_description_content_type='text/markdown',
    keywords='nzbget-file-opener nzbget extension',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
        'Topic :: Text Processing :: Linguistic',
    ],
    license='MIT',
    packages=[
        'nzbget_file_opener'
    ],
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'nzbget-file-opener=nzbget_file_opener.app:main'
        ],
    },
    python_requires='>=3.6',
    install_requires=[
        'pytest',
        'psutil'
    ]
)
