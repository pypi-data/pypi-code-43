import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="testwizard.android-set-top-box",
    version="3.1.5",
    author="Eurofins Digital Testing - Belgium",
    author_email="support-be@eurofins.com",
    description="Testwizard for Android set-top box testobjects",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=['testwizard.android_set_top_box'],
    install_requires=[
        'testwizard.core==3.1.5',
        'testwizard.testobjects-core==3.1.5',
        'testwizard.commands-audio==3.1.5',
        'testwizard.commands-mobile==3.1.5',
        'testwizard.commands-powerswitch==3.1.5',
        'testwizard.commands-remotecontrol==3.1.5',
        'testwizard.commands-video==3.1.5'
    ],
    classifiers=[
        "Programming Language :: Python :: 3.3",
        "Development Status :: 5 - Production/Stable",
        "Operating System :: OS Independent",
    ],
)




















