import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
        name= 'ADvis',
        version='0.0.1',
        author = 'Lindsey Brown, Xinyue Wang',
        author_email="lindsey_brown@g.harvard.edu",
        description='AD library for visualization to aid in the learning of automatic differentiation',
        long_description = long_description,
        long_description_content_type = 'text/markdown',
        url='https://github.com/CS207-AD20/ADvisualizationtools',
        packages = setuptools.find_packages(),
        classifiers = [
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
        ],
        python_requires='>=3.6'
)
