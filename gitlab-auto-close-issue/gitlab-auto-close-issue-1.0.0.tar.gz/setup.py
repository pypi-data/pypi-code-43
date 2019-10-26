from setuptools import find_packages
from setuptools import setup

setup(
    name="gitlab-auto-close-issue",
    version="1.0.0 ",
    description="Python script which will automatically close issues on GitLab for you.",
    long_description=open("README.rst").read(),
    long_description_content_type="text/x-rst",
    author="Haseeb Majid",
    author_email="me@haseebmajid.dev",
    keywords="",
    license="Apache License",
    url="https://gitlab.com/gitlab-automation-toolkit/gitlab-auto-close-issue",
    python_requires="~=3.7",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    zip_safe=False,
    include_package_data=True,
    install_requires=["click>=7.0", "python-gitlab>=1.8.0"],
    entry_points={"console_scripts": ["gitlab_auto_close_issue = gitlab_auto_close_issue.cli:cli"]},
    classifiers=[
        "Programming Language :: Python",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
