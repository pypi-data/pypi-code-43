from setuptools import find_packages, setup


with open('src/pydist_cli/__init__.py') as fp:
    # defines __version__
    exec(fp.read())


with open('README.md') as fp:
    README = fp.read()


setup(
    name='pydist-cli',
    version=__version__,
    author='Alex Becker',
    author_email='alex@pydist.com',
    url='https://github.com/alexbecker/pydist-cli',
    description='CLI for uploading and downloading Python packages from pydist.com.',
    long_description=README,
    long_description_content_type='text/markdown',
    license='MIT',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    package_data={},
    entry_points={
        'console_scripts': [
            'pydist = pydist_cli.__main__:main'
        ],

    },
    install_requires=[
        'pip>=10.0',
        'setuptools>=39.0',
        'wheel',
        'twine',
    ],
    extras_require={},
    python_requires='>=3.5',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ],
    keywords='packaging dependencies',
)
