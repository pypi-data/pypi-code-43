import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="xzqhotspot",
    version="3.0.4",
    author="XZQ",
    author_email="690933685@qq.com",
    description="Mobile Hotspot Manager for Win10",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),
    classifiers=[],
    python_requires='>=3.7',
    install_requires=[
        'winrt',
        'pythonnet',
	'pywifi'
    ]
)