from setuptools import setup, find_packages

setup(
    name='flairstreamlined',
    python_requires='>3.7',
    version='1.0',
    description='streamlined version of flair to use with aws lambda',
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    license='MIT',
    packages=find_packages(),
    install_requires = [
        'torch',
        'requests',
        'segtok',
        'gensim',
        'tqdm'
        ]
    )
