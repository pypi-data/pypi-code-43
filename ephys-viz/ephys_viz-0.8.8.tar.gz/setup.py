import setuptools

pkg_name = "ephys_viz"

setuptools.setup(
    name=pkg_name,
    version="0.8.8",
    author="Jeremy Magland",
    description="Neurophysiology visualization widgets",
    packages=setuptools.find_packages(),
    scripts=['bin/ephys_viz'],
    include_package_data=True,
    install_requires=[
        'simplejson',
        'jupyter',
        'numpy',
        'mountaintools',
        'spikeforest',
        'scipy',
        'vtk',
        'imageio',
        'imageio-ffmpeg'
        ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ]
)