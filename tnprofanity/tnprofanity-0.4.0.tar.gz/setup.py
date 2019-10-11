from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(name='tnprofanity',
    version='0.4.0',
    description='thai-text profanity library',
    long_description=readme(),
    long_description_content_type='text/markdown',
    url='',
    author='GarKoZ',
    author_email='gark36@gmail.com',
    license='MIT',
    install_requires=[

    ],
    scripts=[],
    keywords='thai english profanity censor',
    packages=['tnprofanity'],
    package_dir={'tnprofanity': 'src/tnprofanity'},
    package_data={'tnprofanity': ['*']}
)