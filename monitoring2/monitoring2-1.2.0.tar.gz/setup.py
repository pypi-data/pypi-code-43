import setuptools

with open('README.md', 'r', encoding='utf8') as fh:
	long_description = fh.read()

setuptools.setup(
    name='monitoring2',
    version='1.2.0',
    author='Dmitry Dimonoff',
    author_email='mr.dimonoff@gmail.com',
    description='Библиотека для работы с системой мониторинг 2.0',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://pypi.org/manage/project/monitoring2/release/',
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)