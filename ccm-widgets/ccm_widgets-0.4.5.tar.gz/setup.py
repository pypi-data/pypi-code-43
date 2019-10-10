import setuptools

pkg_name = "ccm_widgets"

setuptools.setup(
    name=pkg_name,
    version="0.4.5",
    author="Jeremy Magland",
    description="Reactopya widgets of relevance to the Center for Computational Mathematics, Flatiron Institute",
    packages=setuptools.find_packages(),
    scripts=['bin/ccm_widgets'],
    include_package_data=True,
    install_requires=[
        'simplejson',
        'numpy',
        'mountaintools',
        'vtk'
        ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ]
)