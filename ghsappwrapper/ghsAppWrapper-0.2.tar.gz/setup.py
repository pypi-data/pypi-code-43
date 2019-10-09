from distutils.core import setup
setup(
    name='ghsAppWrapper',         # How you named your package folder (MyLib)
    packages=['ghsAppWrapper'],   # Chose the same as "name"
    version='0.2',      # Start with a small number and increase it with every change you make
    # Chose a license from here: https://help.github.com/articles/licensing-a-repository
    license='MIT',
    # Give a short description about your library
    description='Wrapper for the goffstown sports app API',
    author='Matthew Gleich',                   # Type in your name
    author_email='matthewgleich@gmail.com',      # Type in your E-Mail
    # Provide either the link to your github or to your website
    url='https://github.com/goffstown-sports-app/ghsAppWrapper',
    download_url='https://github.com/goffstown-sports-app/ghsAppWrapper/archive/v_02.tar.gz',
    # Keywords that define your package best
    keywords=['goffstown', 'sports', 'wrapper', 'app', 'api', 'high-school'],
    install_requires=[
        'requests',
    ],
    classifiers=[
        # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        'Development Status :: 3 - Alpha',
        # Define that your audience are developers
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',   # Again, pick a license
        # Specify which python versions that you want to support
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)
