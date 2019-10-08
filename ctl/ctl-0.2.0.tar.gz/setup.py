from setuptools import find_packages, setup


version = open('Ctl/VERSION').read().strip()
requirements = open('Ctl/requirements.txt').read().split("\n")
test_requirements = open('Ctl/requirements-test.txt').read().split("\n")


setup(
    name='ctl',
    version=version,
    author='20C',
    author_email='code@20c.com',
    description='Get control of your environment',
    long_description='',
    license='LICENSE.txt',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    packages=find_packages("src"),
    package_dir={"": "src"},
    include_package_data=True,
    url='https://github.com/getctl/ctl',
    download_url='https://github.com/getctl/ctl/%s' % version,

    install_requires=requirements,
    test_requires=test_requirements,

    entry_points={
        'console_scripts': [
            'ctl=ctl.cli:main'
        ]
    },

    scripts=[
        # virtualenv helper scripts
        'src/ctl/bin/ctl_venv_build',
        'src/ctl/bin/ctl_venv_copy',
        'src/ctl/bin/ctl_venv_sync',
    ],

    zip_safe=True
)
