import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='irida_uploader_cl',
    version='0.2',
    description='IRIDA uploader: upload NGS data to IRIDA system',
    url='https://github.com/duanjunhyq/irida_uploader_cl',
    author='Jun Duan',
    author_email='jun.duan@bccdc.ca',
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='MIT',
    keywords="IRIDA NGS uploader",    
    packages=setuptools.find_packages(include=[ 'irida_uploader_cl',
                                                'irida_uploader_cl.*',
                                                ]),
    install_requires=['rauth',
        'autopep8',
        'pycodestyle',
        'requests',
        'appdirs',
        'pytest',
        'mkdocs',
        'cerberus',
        'argparse',
        'selenium',
        ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    include_package_data = True,
    python_requires='>=3.5',
    entry_points={
    	'console_scripts': [
    		'irida_uploader_cl=irida_uploader_cl.irida_uploader_cl:main'
    	]
    },
  
)
