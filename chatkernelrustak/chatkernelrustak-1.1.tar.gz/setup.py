import setuptools
with open("README.md", "r") as fh:
    long_description = fh.read()
setuptools.setup(
     name='chatkernelrustak',
     version='1.1',
     scripts=[] ,
     author="rustak",
     author_email="admin@rustak.tk",
     description="Kernel for encrypted chat",
     long_description=long_description,
     long_description_content_type="text/markdown",
     url="https://github.com/rustakss/security-chat",
     packages=setuptools.find_packages(),
     classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
     ],
     python_requires='>=3.6',
 )
