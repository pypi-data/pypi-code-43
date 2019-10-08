import setuptools
from azskpy.constants import __name__, __version__

setuptools.setup(
		name=__name__,
		version=__version__,
		description="Scans Azure Controls",
		author="AzSK Dev Team",
		author_email="dsreazsksup@microsoft.com",
		url="https://aka.ms/azskpy",
		packages=setuptools.find_packages(),
		install_requires=[
			"kubernetes",
			"applicationinsights",

		]
)
