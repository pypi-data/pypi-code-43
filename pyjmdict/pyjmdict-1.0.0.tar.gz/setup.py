from setuptools import setup, find_packages
pkg = "pyjmdict"
ver = '1.0.0'
setup(
    name             = pkg,
    version          = ver,
    description      = "JMDict sqlalchemy interface",
    long_description = "Interface to JMDict and KanjiDic based on sqlalchemy",
    author           = "jikan@cock.li",
    author_email     = "jikan@cock.li",
    license          = "LGPLv3",
    url              = "https://hydra.ecd.space/jikan/pyjmdict/",
    zip_safe         = True,
    packages         = find_packages(),
    install_requires = ['sqlalchemy>=1', 'cachetools>=1', 'lxml>=3',
                        'jikan_sqlalchemy_utils>=1.0.0'],
    classifiers      = ["Programming Language :: Python :: 3 :: Only"])
