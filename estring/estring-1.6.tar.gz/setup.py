from setuptools import setup, find_packages
setup(
        name="estring",
        version = "1.6",
        description="javascript style string APIs",
        author="dapeli",
        url="https://github.com/ihgazni2/estring",
        author_email='terryinzaghi@163.com', 
        license="MIT",
        long_description = "refer to .md files in https://github.com/ihgazni2/estring",
        entry_points = {
            'console_scripts': [
                'eses_capinit=estring.BINS.capinit:main',
                'eses_camel2lod=estring.BINS.camel2lod:main',
                'eses_lod2camel=estring.BINS.lod2camel:main',
                'eses_camel2dash=estring.BINS.camel2dash:main',
                'eses_dash2camel=estring.BINS.dash2camel:main',
                'eses_lod2dash=estring.BINS.lod2dash:main',
                'eses_dash2lod=estring.BINS.dash2lod:main',
                'eses_h5entity_loose=estring.BINS.h5entity:loose',
                'eses_h5entity_strict=estring.BINS.h5entity:strict',
                'eses_emoji_loose=estring.BINS.emoji:loose',
                'eses_emoji_strict=estring.BINS.emoji:strict',
                ]
            },
      include_package_data=True,
      package_data = {
          'resources':["estring/emoji/resources/*.json"]
      },
        classifiers=[
            'Environment :: Console',
            'Environment :: Web Environment',
            'Intended Audience :: End Users/Desktop',
            'Intended Audience :: Developers',
            'Intended Audience :: System Administrators',
            'Programming Language :: Python',
            ],
        packages= find_packages(),
        py_modules=['estring'], 
        )


# python3 setup.py bdist --formats=tar
# python3 setup.py sdist

