from distutils.core import setup, Extension

module1 = Extension('main',
                    sources = ['main.cxx'])

setup (name = 'add_by_cpp',
       version = '1.0',
       description = 'This is a demo package',
       ext_modules = [module1])
