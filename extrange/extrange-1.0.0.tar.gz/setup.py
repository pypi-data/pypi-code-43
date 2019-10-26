from setuptools import setup


with open('README.md', encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='extrange',
    version='1.0.0',
    description='Extra range library',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/zakuro9715/extrange',
    author='z@kuro',
    author_email='z@kuro.red',
    license='MIT',
    keywords='range datetime time',
    packages=[
        'extrange',
    ],
    install_requires=[],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Software Development ',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
    ],
)
