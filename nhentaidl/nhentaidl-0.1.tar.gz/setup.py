from distutils.core import setup
setup(
    name='nhentaidl',
    packages=['nhentaidl'],
    version='0.1',
    license='MIT',
    description='Download nhentai images',
    author='Manish Karki',
    author_email='9tyninelives@gmail.com',
    url='https://github.com/ManishKarki1997/nhentaidl',
    download_url='https://github.com/ManishKarki1997/nhentaidl/archive/v_01.tar.gz',
    keywords=['hentai', 'manga', 'manga download'],
    install_requires=[
        'requests',
        'beautifulsoup4',
        'wget'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
