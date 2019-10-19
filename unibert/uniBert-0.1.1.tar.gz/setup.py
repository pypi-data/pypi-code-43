from setuptools import setup, find_packages

setup(
    name='uniBert',
    version='0.1.1',
    description='Bert multi-task multi-class multi-label classification & text generation',
    long_description="Github : https://github.com/voidful/uniBert",
    url='https://github.com/voidful/uniBert',
    author='Voidful',
    author_email='voidful.stack@gmail.com',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='nlp bert multi task class label classification generation',
    packages=find_packages()
)
