from setuptools import setup, find_packages

setup(
    name='drf-dynamicfieldserializer',
    version='0.2.1',
    packages=find_packages(),
    install_requires=[
        'Django >= 1.11',
        'djangorestframework >= 3.8.2'
    ],
    description='Django Rest Framework DynamicFieldSerializer',
    author='bzdvdn',
    author_email='bzdv.dn@gmail.com',
    url='https://github.com/bzdvdn/drf-dynamicfieldserializer.git',
    license='MIT',
    python_requires=">=3.6",
)
