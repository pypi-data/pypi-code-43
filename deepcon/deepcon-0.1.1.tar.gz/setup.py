import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="deepcon",
    version="0.1.1",
    author="Badri Adhikari",
    author_email="adhikarib@umsl.edu",
    description="Protein Contact Prediction using Dilated Convolutional Neural Networks with Dropout",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ba-lab/deepcon-package",
    packages=setuptools.find_packages(),    
	package_data={
        'deepcon': [
            'deepcon/weights-rdd-covariance.hdf5'
        ]
    },
    include_package_data=True,
	install_requires=['numpy', 'pyYAML', 'tensorflow', 'keras',],
	setup_requires=['numpy', 'pyYAML', 'tensorflow', 'keras',],
    classifiers=[
        'Programming Language :: Python',
        'License :: OSI Approved :: MIT License',
		'Intended Audience :: Science/Research',
        'Operating System :: OS Independent',
    ],
)
