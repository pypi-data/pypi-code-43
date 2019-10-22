from setuptools import setup

setup(
    name='pytest_ec2',
    version='0.1',
    packages=['pytest_ec2'],
    url='https://github.com/randomlock/pytest_ec2',
    license='MIT',
    author='abdullahhasan',
    author_email='abdullahh546@gmail.com',
    description='Pytest execution on EC2 instance',
    install_requires=[
        'boto3',
        'slackclient',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',  # Define that your audience are developers
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',  # Again, pick a license
        'Programming Language :: Python :: 3',
        # Specify which python versions that you want to support
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    download_url='https://github.com/randomlock/pytest_ec2/archive/0.1.tar.gz',
)
