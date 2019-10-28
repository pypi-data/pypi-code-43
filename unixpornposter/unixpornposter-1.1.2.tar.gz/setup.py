from distutils.core import setup
setup(
    name='unixpornposter',
    packages = ['unixpornposter'],
    version='1.1.2',
    license='idgaf',
    description='A cli tool for making post to unixporn',
    author='Ellie Mae Schipper',
    url='https://github.com/lifesgood123/unixpornposter',
    download_url="https://github.com/Lifesgood123/unixpornposter/archive/1.1.1.tar.gz",
    scripts=['./unixpornpost'],
    install_requires=[
        'katfetch<=1.2.6'
        'requests',
        'tqdm',
        'praw',
        'elliesImgurUploader'
    ],
    classifiers=[
    'Development Status :: 4 - Beta',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3.7',
  ]
)
