from setuptools import setup, find_packages

setup(
    name="wagtail-spa-integration",
    version="0.3.0",
    author="David Burke",
    author_email="david@thelabnyc.com",
    description=(
        "Tools for using Wagtail API with javascript single page apps"),
    license="Apache License",
    keywords="django wagtail",
    url="https://gitlab.com/thelabnyc/wagtail-spa-integration",
    packages=find_packages(exclude=('sandbox.*', 'sandbox',)),
    include_package_data=True,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Wagtail',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Intended Audience :: Developers',
        "License :: OSI Approved :: Apache Software License",
    ],
    install_requires=[
        'wagtail>=2.0.0'
    ]
)
