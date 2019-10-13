import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cloud_weather_app",
    version="0.0.1",
    author="Deepak Natanmai",
    description="Simple Package to connect with weather.com endpoints and get quick info",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/0xdebug/cloud-weather",
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        "Operating System :: OS Independent",
    ],
    keywords='Weather api crawling scraping',
    install_requires=['requests','beautifulsoup4'],
    python_requires='>=3.6',
)