import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dmarc",
    version="1.0.0",
    author="Dusan Obradovic",
    author_email="dusan@euracks.net",
    description="Parse and evaluate DMARC email authentication policy",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='MIT',
    url="https://gitlab.com/duobradovic/pydmarc",
    packages=setuptools.find_packages(),
    keywords = ['dkim', 'spf', 'dmarc', 'email', 'authentication', 'rfc5451', 'rfc7001', 'rfc7601', 'rfc8601'],
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Communications :: Email :: Mail Transport Agents",
        "Topic :: Communications :: Email :: Filters",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires='>=2.7',
)