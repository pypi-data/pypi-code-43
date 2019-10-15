import setuptools

with open('README.md', 'r') as read_me:
    description = read_me.read()

setuptools.setup(
    name='jbtech-utils-package',
    version='0.0.3',
    author='James Beringer',
    author_email='jamberin@gmail.com',
    description='Package for just basic utitilies',
    long_description=description,
    long_description_content_type='text/markdown',
    url='https://github.com/jamberin/jbtech-utils-package',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3.7',
        'Development Status :: 2 - Pre-Alpha',
        'License :: Public Domain'
    ]
)
