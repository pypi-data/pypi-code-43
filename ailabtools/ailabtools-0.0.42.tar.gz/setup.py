from setuptools import setup

required_packages = ['numpy', 'tensorflow', 'matplotlib', 'scipy', 'scikit-learn', 'scikit-image', 'keras', 
                     # For extract_distinct_image and file_processer
                     'imagehash', # Perceptual Hash for compare image: https://github.com/JohannesBuchner/imagehash
                     'send2trash', # Just send to trash
                     'python-magic', # Fro read file info: https://github.com/ahupp/python-magic,
                     'tqdm',
                     ]

required_packages = []

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='ailabtools',
    packages=['ailabtools', 'ailabtools.keras'],
    version='0.0.42',
    author="Zalo AILab",
    description='Common tools for Zalo AILab',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://lab.zalo.ai',
    include_package_data=True,
    install_requires=required_packages,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
