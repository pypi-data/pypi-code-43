import setuptools
from setuptools import find_packages

def readme():
    return open('README.md').read()

setuptools.setup(
    name="msg91-otp",
    version="0.1.0",
    author="Prasanna Venkadesh",
    author_email="prasanna@cooponscitech.in",
    description="Minimal OTP only API coverage for msg91.com service",
    long_description_content_type="text/markdown",
    long_description=readme(),
    python_requires='>=2.7',
    install_requires=["httpx==0.7.4"],
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    url="https://gitlab.com/coopon/reusable-libs/python/msg91-otp",
    classifiers=[
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',

        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Operating System :: OS Independent",
    ]
)

