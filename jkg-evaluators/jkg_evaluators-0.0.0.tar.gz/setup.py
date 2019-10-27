from setuptools import find_packages, setup
import jkg_evaluators

pkg_name = 'jkg_evaluators'

version = jkg_evaluators.__version__


with open("README.md") as fp:
    long_description = fp.read()

if __name__ == '__main__':
    setup(
        name=pkg_name,
        version=version,
        description="challenge evaluation",
        long_description=long_description,
        long_description_content_type="text/markdown",
        license='MIT',
        classifiers=[
            "License :: OSI Approved :: MIT License",
        ],
        url='https://github.com/endremborza/{}'.format(pkg_name),
        keywords='education challenges',
        author='Endre Márk Borza',
        author_email='endremborza@gmail.com',
        packages=find_packages(),
        include_package_data=True,
        python_requires='>=3.6',
    )
