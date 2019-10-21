import setuptools

setuptools.setup(
     name='custom_git',  
     version='4.2',
     author="voziq",
     author_email="mgoli@voziq.com",
     description="A Docker and AWS utility package",
     url="https://github.com/voziq/custom-git",
     packages=setuptools.find_packages(),
     scripts=['jupyterlab_git/excute.sh'],
     install_requires=[
        'notebook',
        'nbdime >= 1.1.0'
    ],
     package_data={'custom_git': ['*']},
 )
