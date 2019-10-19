from distutils.core import setup

import setuptools

setup(
    name='TemplateCreator',
    packages=setuptools.find_packages(),
    version='0.35',
    include_package_data = True,
    package_data={
        'templates': ['*']
    },
    license='MIT',
    description='This project is intended unify boilerplate code between team members and make the setup process for starting a new component shorted and less tedious.',
    author='Gal Ben Haim',
    author_email='gal_ben_haim@yahoo.com',
    url='https://github.com/galbh/template-generator',
    download_url='https://github.com/galbh/template-generator/archive/v_35.tar.gz',
    keywords=['TEMPLATE'],
    install_requires=['jinja2'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        'Intended Audience :: Developers',  # Define that your audience are developers
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3'
    ],
)
