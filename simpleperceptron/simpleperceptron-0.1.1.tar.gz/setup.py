import setuptools

setuptools.setup( name = 'simpleperceptron',  
                    version = '0.1.1',
                    author = 'Wiphoo Methachawalit',\
                    description = 'A simple percepton package for understanding neural network concept',
                    url = "https://github.com/wiphoo/neural-simple_perceptron",
                    packages = [ 
                                   'simpleperceptron',
                    ],
                    install_requires = [ 
                                        'numpy',
                    ],
                    classifiers = [
                            "Programming Language :: Python :: 3",
                            "License :: OSI Approved :: MIT License",
                            "Operating System :: OS Independent",
                    ],
 )