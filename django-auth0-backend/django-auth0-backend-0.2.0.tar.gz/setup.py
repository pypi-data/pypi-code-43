from setuptools import setup

setup(
    name='django-auth0-backend',
    author = "Bryan Marty",
    author_email = "bryan@bryanmarty.com",
    keywords = "django python social auth auth0",
    version='0.2.0',
    packages=['django_auth0_backend'],
    license='MIT License',
    install_requires=[
        'python-jose>=3.0.0',
        'requests>=2.22.0',
        'social-auth-core>=3.2.0',
    ],
    extra_requires=[
        'nameparser',
        'cryptography',
    ],
    classifiers=[
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
    ],
)
