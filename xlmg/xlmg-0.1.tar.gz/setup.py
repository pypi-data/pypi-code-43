
import setuptools

setuptools.setup(name="xlmg",
    version="0.1",
    description="Module for importing and exporting data between Microsoft Excel workbook and MongoDB database",
    url="https://github.com/naiim-khaskhoussi/xlmg",
    author="Naiim Khaskhoussi",
    author_email="khaskhoussi.naiim@gmail.com",
    license='MIT',
    packages=setuptools.find_packages(),
	install_requires=['peppercorn'],
    classifiers=[
		"Development Status :: 3 - Alpha",
		"Intended Audience :: Developers",
		"Topic :: Software Development :: Build Tools",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6')