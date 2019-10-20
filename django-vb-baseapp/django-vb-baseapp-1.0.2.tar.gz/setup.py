import os

from setuptools import find_packages, setup

CURRENT_WORKING_DIRECTORY = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(CURRENT_WORKING_DIRECTORY, 'README.md')) as fp:
    README = fp.read()

setup(
    name='django-vb-baseapp',
    version='1.0.2',
    description='Magical app for django-vb-admin',
    long_description=README,
    long_description_content_type='text/markdown',
    url='https://github.com/vbyazilim/django-vb-baseapp',
    author='vb YAZILIM',
    author_email='hello@vbyazilim.com',
    license='MIT',
    install_requires=['vb-console'],
    python_requires='>=3.6',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 2.2',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    include_package_data=True,
)
