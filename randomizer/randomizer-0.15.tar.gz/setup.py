try:
    from setuptools import setup
except ImportError:
    raise ImportError(
        "setuptools module required, please go to "
        "https://pypi.python.org/pypi/setuptools and follow the instructions for installing setuptools")

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='randomizer',
    version='0.15',
    packages=['randomizer', ],
    url='https://github.com/Saylermb/randomizer',
    license='The MIT License: http://www.opensource.org/licenses/mit-license.php',
    author='Saylermb',
    author_email='Saylermb@gmail.com',
    description='Liberty for generate random data.',
    install_requires=['numpy', ],
    long_description=long_description,
    long_description_content_type='text/markdown',
    python_requires='>3.6.2',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Education :: Testing',
        'Topic :: Text Processing',
        'Topic :: Utilities']
)
