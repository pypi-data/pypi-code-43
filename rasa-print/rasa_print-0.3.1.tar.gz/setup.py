# import setuptools
#
# with open("README.md", 'r') as f:
#     long_description = f.read()
#
#
# setuptools.setup(
#     name="rasa_print",
#     version="6.0",
#     author="ZhongLei",
#     author_email="625015751@qq.com",
#     description="rasa_chi_exd",
#     long_description=long_description,
#     long_description_content_type="text/markdown",
#     license="MIT",
#     url="https://github.com/zlxwl/rasa_print.git",
#     packages=setuptools.find_packages(),
#     classifiers=[
#         "Programming Language :: Python :: 3",
#         "Operating System :: OS Independent",
#     ],
# )

import io
import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

# Avoids IDE errors, but actual version is read from version.py
__version__ = None
with open("version.py") as f:
    exec(f.read())

# Get the long description from the README file
with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

install_requires = [
    "rasa~=1.1.3",
    "jieba~=0.39",
    "bert-serving-client==1.8.9"
]

setup(
    name='rasa_print',
    packages=find_packages(),
    version=__version__,
    install_requires=install_requires,
    include_package_data=True,
    description="Rasa NLU addons a natural language parser for bots",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Zhong Lei',
    author_email='625015751@qq.com',
    maintainer="Zhong Lei",
    maintainer_email="625015751@qq.com",
    license='Apache 2.0',
    url="https://rasa.com",
    keywords="nlp machine-learning machine-learning-library bot bots "
             "botkit rasa conversational-agents conversational-ai chatbot"
             "chatbot-framework bot-framework",
    download_url="https://github.com/zlxwl/rasa_print/archive/{}.tar.gz"
                 "".format(__version__),
    project_urls={
        'Bug Reports': 'https://github.com/zlxwl/rasa_print/issues',
        'Source': 'https://github.com/zlxwl/rasa_print',
    },
)

print("\nWelcome to Rasa NLU!")
print("If any questions please visit documentation "
      "page https://nlu.rasa.com")