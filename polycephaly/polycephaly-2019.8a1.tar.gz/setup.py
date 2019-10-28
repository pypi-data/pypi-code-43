import setuptools

with open("README.md", "r") as fh:
	long_description = fh.read()

# Frowned upon way of adding in dependencies - see https://caremad.io/posts/2013/07/setup-vs-requirement/
# requires = [ line.strip('\n') for line in open( 'requirements.txt' ).readlines() ]

setuptools.setup(
	name							=	"polycephaly",
	version							=	"2019.08a1",
	author							=	"Louis T. Getterman IV",
	author_email					=	"Thad.Getterman@gmail.com",
	description						=	"Easily create system daemons (and programs) that use an email-like syntax for communicating between threaded and forked processes.",
	install_requires				=	[
											'Logbook',
										],
	long_description				=	long_description,
	long_description_content_type	=	"text/markdown",
	license							=	"MIT",
	url								=	"https://gitlab.com/ltgiv/polycephaly",
	packages						=	setuptools.find_packages(),
	classifiers						=	[
											"Programming Language :: Python :: 3",
											"License :: OSI Approved :: MIT License",
											"Operating System :: POSIX",
										],
)
