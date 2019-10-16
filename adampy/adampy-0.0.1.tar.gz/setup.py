import setuptools

with open("README.md","r") as fh:
    long_description=fh.read()

setuptools.setup(
        name="adampy",
        version="0.0.1",
        author="MEEO s.r.l.",
        author_email="info@meeo.it",
        description="Python Adam API",
        long_description=long_description,
        long_description_content_type="text/markdown",
        url="https://git.services.meeo.it/sistema/adampy",
        packages=['adampy'],
        install_requires=[
            'numpy >= 1.17.2',
            'requests >= 2.18.4',
            'fiona >= 1.8.6',
            'imageio >= 2.5.0',
            'matplotlib >= 3.1.1',
            'geopandas >= 0.5.0',
            'xarray >= 0.13.0',
            'datetime >= 4.0',
            'rasterio >= 1.0.23'
            ],
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: Unix",
            ],
        python_requires='>=3.6',
        )

