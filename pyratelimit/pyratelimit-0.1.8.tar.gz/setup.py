import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name='pyratelimit',
    packages=['pyratelimit'],
    version='0.1.8',
    description='A distributed rate limiting library for python using leaky bucket algorithm and Redis',
    author='Biplap Sarkar, Andreas Scheucher',
    author_email='andreas.scheucher@gmail.com',
    url='https://github.com/ascheucher/pyratelimit',
    keywords=['rate limiting', 'throttle', 'redis'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
