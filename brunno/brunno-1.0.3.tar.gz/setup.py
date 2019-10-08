from setuptools import setup

setup(
    name = 'brunno',
    version = '1.0.3',
    author = 'Reinan Bezerra',
    author_email = 'perseu912@gmail.com',
    packages=["brunno"],
    include_package_data=True,
    install_requires=["numpy", "mpmath"],
    description = 'lib for math and phisyc',
    long_description = 'one lib for phisyc and math ' + ',lib of functions specials, ' + 'phisyc marh',
    url = 'https://github.com/perseu912/brunnopy',
    project_urls = {
        'Código fonte': 'https://github.com/perseu912',
        'Download': 'https://github.com/perseu912/brunnopy/archive/master.zip'
    },
    license = 'MIT',
    keywords = 'fisica matematica funcoes especiais matematica computacional',
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: Portuguese (Brazilian)',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Internationalization',
        'Topic :: Scientific/Engineering :: Physics'
    ]
)
