import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sms_sdk_renderer_python",
    version="0.1.8",
    author="Reed Feldman",
    author_email="reed.feldman@symphony.com",
    description="Sample Renderer for Symphony Elements",
    package_data = {'': ['*.hbs']},
    include_package_data=True,
    install_requires=['pybars3==0.9.6'],
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/SymphonyPlatformSolutions/sms_sdk_renderer_python",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
