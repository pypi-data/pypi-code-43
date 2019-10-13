from setuptools import setup
#from distutils.core import setup

setup(
    name='nepsy',
    version='0.1.2.0',
    author='Enrique Coronado',
    author_email='enriquecoronadozu@gmail.mx',
    url='http://enriquecoronadozu.github.io',
    description='NEP additional packages',
    packages=["nepsy", "nep_aldebaran"],
    install_requires=[
          'nep', 'tinydb', 'kapuccino', 'SpeechRecognition', 'pyaudio'
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.6",
        "Topic :: Software Development"
    ]
)

