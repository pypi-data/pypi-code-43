import setuptools

with open('README.md') as f:
	ld = f.read()

setuptools.setup(
	name="lose",
	version="0.5",
	description="A helper package for hdf5 data handling",
	long_description=ld,
	long_description_content_type="text/markdown",
	author="okawo",
	author_email="okawo.198@gmail.com",
	url="https://github.com/okawo80085/lose",
	packages=['lose'],
	install_requires=['tables', 'numpy'],
	license='MIT',
	classifiers=[
		"Programming Language :: Python :: 3",
		"Programming Language :: Python :: 3.6",
		"Operating System :: OS Independent",
		"Intended Audience :: Developers",
		"Intended Audience :: Education",
		"Intended Audience :: Science/Research",
		"Topic :: Scientific/Engineering :: Artificial Intelligence",
	],
	python_requires='>=3',
)
