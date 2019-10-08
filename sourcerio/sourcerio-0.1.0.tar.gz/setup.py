import setuptools

setuptools.setup(
    name='sourcerio',
    version=open('VERSION', 'r').read(),
    scripts=['sourcerio'],
    author='Jean-Francois Theroux',
    author_email='jftheroux@devolutions.net',
    description='Backup tool for Bitbucket Cloud and Github',
    long_description=open('README.md', 'r').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/Devolutions/sourcerio',
    packages=setuptools.find_packages(),
    license='MIT',
    keywords=['backup', 'bitbucket', 'github'],
    classifiers=[
        'Programming Language :: Python :: 3',
         'License :: OSI Approved :: MIT License',
         'Operating System :: OS Independent',
    ],
    install_requires=['pygithub', 'requests'],
    platforms=['any']
)
