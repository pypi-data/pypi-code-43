from distutils.core import setup
setup(
    name='elliesImgurUploader',
    packages = ['elliesImgurUploader'],
    version='0.1',
    license='idgaf',
    description='A small library for uploading imgur albums',
    author='Ellie Mae Schipper',
    url='https://github.com/lifesgood123/elliesImgurUploader',
    download_url="https://github.com/Lifesgood123/elliesImgurUploader/archive/0.1.tar.gz",
    install_requires=[
        'requests',
        'tqdm'
    ],
    classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3.7',
  ]
)
