from setuptools import find_packages
from setuptools import setup


setup(
    name='thoth-test',
    version="0.0.1",
    description='A test package for Thoth.',
    long_description='A test package for Thoth.',
    author='Fridolin Pokorny',
    author_email='fridolin@redhat.com',
    license='GPLv3+',
    packages=find_packages(),
    zip_safe=False,
    install_requires=["selinon[celery,mongodb,postgresql,redis,s3,sentry]"],
)
