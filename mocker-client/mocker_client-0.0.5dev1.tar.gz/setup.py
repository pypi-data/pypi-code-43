from distutils.core import setup


if __name__ == '__main__':

    with open('README.rst', 'r') as f:
        long_description = f.read()

    setup(
        name='mocker_client',
        version='0.0.5dev1',
        description='client for http mock server https://github.com/vilus/mocker',
        long_description=long_description,
        packages=['mocker_client'],
        author='Shevchenko Vladimir',
        url='https://github.com/vilus/mocker_client',
        install_requires=['requests']
    )
