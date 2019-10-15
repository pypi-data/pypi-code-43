from setuptools import setup, find_packages

# from vtool.changelog import ChangeLog

# changelog = ChangeLog()


setup(
	name = 'vtool',         # How you named your package folder (MyLib)
	packages = find_packages(),   # Chose the same as "name"
	version = "1.5.0",
	license='MIT',      # Chose a license from here: https://help.github.com/articles/licensing-a-repository
	description = 'tool kampretcode',   # Give a short description about your library
	author = 'kampretcode',                   # Type in your name
	author_email = 'manorder123@gmail.com',      # Type in your E-Mail
	url = 'https://github.com/Vaziria/vtool',   # Provide either the link to your github or to your website
	keywords = ['PDC', 'KAMPRETCODE', 'CUSTOMBUILDER', 'PYTHON', 'VAZIRIA', 'PACKAGE'],   # Keywords that define your package best
	classifiers=[
		'Development Status :: 5 - Production/Stable',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
		'Intended Audience :: Developers',      # Define that your audience are developers
		'Topic :: Software Development :: Build Tools',
		'License :: OSI Approved :: MIT License',   # Again, pick a license
		'Programming Language :: Python :: 2.7'
	],
)