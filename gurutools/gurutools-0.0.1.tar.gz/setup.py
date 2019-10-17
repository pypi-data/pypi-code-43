import setuptools

with open("./README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="gurutools",
    version="0.0.1",
    author="AppointmentGuru",
    author_email="tech@appointmentguru.co",
    description="A collection of tools we commonly use in Guru services",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/SchoolOrchestration/libs/gurutools",
    packages=['gurutools'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
