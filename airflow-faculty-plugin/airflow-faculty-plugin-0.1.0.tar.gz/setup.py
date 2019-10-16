
from setuptools import setup, find_packages

setup(
    name="airflow-faculty-plugin",
    description="Airflow plugin for interacting with the Faculty platform",
    url="https://faculty.ai/products-services/platform/",
    author="Faculty",
    author_email="opensource@faculty.ai",
    license="Apache Software License",
    packages=find_packages(),
    use_scm_version={"version_scheme": "post-release"},
    setup_requires=["setuptools_scm"],
    install_requires=["faculty"],
    entry_points={
        'airflow.plugins': [
            'unused = airflow_faculty_plugin:FacultyPlugin'
        ]
    }
)
