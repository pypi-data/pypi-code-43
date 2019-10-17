from distutils.core import setup

setup(
    name="locuspeerexplorer",
    packages=["locuspeerexplorer"],
    version="0.2.7",  # Start with a small number and increase it with every change you make
    license="MIT",
    description="A package that lets you find similar community peers based off of functional or outcomee data",
    author="Locus Analytics",
    author_email="alee@locus.co",
    url="https://github.com/LocusAnalytics/peer-explorer",
    # Keywords that define your package best
    keywords=["Economics", "Peer Finder"],
    install_requires=["numpy", "pandas", "scipy", "fastdtw"],
    classifiers=[
        # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        "Development Status :: 3 - Alpha",
        # Define that your audience are developers
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
    ],
)
