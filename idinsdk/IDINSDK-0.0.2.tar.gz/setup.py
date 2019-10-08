import setuptools

with open('README.md') as fp:
    long_description = fp.read()

setuptools.setup(
    name='IDINSDK',
    version='0.0.2',
    author='Finema Co., Ltd.',
    author_email='hi@finema.co',
    description='Python SDK for IDIN Blockchain API',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://git.finema.co/finema/idinsdk-python',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)