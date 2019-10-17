import setuptools

setuptools.setup(
     name='ucamdsm',
     version='1.2.8',
     packages=['ucamdsm', 'ucamdsm.lib', ],
     entry_points={
        'console_scripts': [
            'ucamdsm = ucamdsm.__main__:main'
        ]
     },
     scripts=['dellsc/replace_volume', 'dellsc/delete_volume',
              'dellsc/create_snapshot', 'dellsc/clone_volume',
              'dellsc/record_recycled_volumes', 'dellsc/remove_recycled_volumes', ],
     license="MIT License (MIT)",
     author="UIS Infrastructure Servers and Storage, University of Cambridge",
     author_email="wh330@cam.ac.uk",
     description="A Dell SC tasks automation using REST API",
     long_description=open('README.md').read(),
     long_description_content_type='text/markdown',
     url="https://gitlab.developers.cam.ac.uk/uis/infra/dell-sc",
)
