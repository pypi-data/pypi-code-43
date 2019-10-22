import setuptools

setuptools.setup(
    name='notarius',
    version=open('VERSION', 'r').read(),
    scripts=['notarius'],
    author='Jean-Francois Theroux',
    author_email='jftheroux@devolutions.net',
    description='Tool to notarize a macOS dmg',
    long_description=open('README.md', 'r').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/Devolutions/notarius',
    packages=setuptools.find_packages(),
    license='MIT',
    keywords=['apple', 'macos', 'dmg', 'notarize'],
    classifiers=[
        'Programming Language :: Python :: 3',
         'License :: OSI Approved :: MIT License',
         'Operating System :: OS Independent',
    ],
    install_requires=['requests'],
    platforms=['any']
)
