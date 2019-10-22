try:
    from setuptools import setup
except ImportError:
    raise ImportError(
        "setuptools module required, please go to https://pypi.python.org/pypi/setuptools and follow the instructions for installing setuptools")

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()
setup(
    version='1.40',
    url='https://github.com/Saylermb/Address_Templeter',
    description='search for addresses in the text',
    name='address_templeter',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=['address_templeter'],
    package_data={'address_templeter': ['learned_settings.crfsuite']},
    license='The MIT License: http://www.opensource.org/licenses/mit-license.php',
    install_requires=['python-crfsuite>=0.9.6',
                      'lxml'],
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: Russian',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Information Analysis']
)
