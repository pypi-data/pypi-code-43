from setuptools import setup, find_packages
pkg = "learnusumjap"
ver = '1.0.0'
setup(
    name             = pkg,
    version          = ver,
    description      = "Japanese language utilities",
    author           = "jikan@cock.li",
    author_email     = "jikan@cock.li",
    license          = "LGPLv3",
    url              = "https://hydra.ecd.space/jikan/learnusumjap/",
    packages         = find_packages(),
    install_requires = ['pyjmdict>=1.0.0',
                        'jikan_sqlalchemy_utils>=1.0.0',
                        'romkan>=0.2.1',
                        'tqdm'],
    classifiers      = ["Programming Language :: Python :: 3 :: Only"])
