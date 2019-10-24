from distutils.core import setup

# https://packaging.python.org/tutorials/packaging-projects/
# python setup.py sdist
# twine upload dist/*   

with open("README.rst", "r") as fh:
    long_description = fh.read()

setup(
    name = 'pipulate',
    packages = ['pipulate'],
    version = '0.2.5',
    description = 'Free and Open Source SEO Software (Auto-Update Google Sheets).',
    long_description = long_description,
    author = 'Mike Levin SEO in NYC, alum of Commodore & 360i, Creator of HitTail.com, currently with J2/Ziff-Davis/IGN/Mashable.',
    license='MIT',
    author_email = 'miklevin@gmail.com',
    url = 'https://github.com/miklevin/pipulate',
    python_requires='>=3.6',
    install_requires=['pandas', 'gspread', 'google-api-python-client', 'google-auth-oauthlib'],
    keywords = ['open source', 'seo software', 'google sheets', 'linux scheduling', 'datamaster', 'datamasterng', 'pandas', 'gspread']
)

classifiers=[
    'Development Status :: 2 - Beta',
    'Intended Audience :: Marketing',
	'Topic :: Data',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7'
]
