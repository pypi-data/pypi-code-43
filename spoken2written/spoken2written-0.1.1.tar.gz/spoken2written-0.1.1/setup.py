import setuptools
with open("README.md", "r") as fh:
    long_description = fh.read()
setuptools.setup(
     name='spoken2written',  
     version='0.1.1',
     scripts=['spoken2written'] ,
     author="Heramb Devbhankar",
     author_email="heramb1711@gmail.com",
     description="Spoken English to Written English translation package",
     long_description=long_description,
   long_description_content_type="text/markdown",
     url="https://github.com/HerambVD/s2w_en",
     packages=setuptools.find_packages(),
     classifiers=[
         "Programming Language :: Python :: 3",
         "Operating System :: OS Independent",
     ],
     install_requires=[
          'spacy','pprint','word2number',
      ]
 )