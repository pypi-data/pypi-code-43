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
    "rasa_nlu == 0.15.0",
    "rasa_core == 0.14.0",
    "jieba~=0.39",
    "bert-serving-client==1.8.9"
]

setup(
    name='rasa_chinese_plugin',
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
    # license='Apache 2.0',
    url="https://rasa.com",
    keywords="nlp machine-learning machine-learning-library bot bots "
             "botkit rasa conversational-agents conversational-ai chatbot"
             "chatbot-framework bot-framework",
    download_url="https://github.com/zlxwl/rasa_chinese_extend_plugin/archive/{}.tar.gz"
                 "".format(__version__),
    project_urls={
        'Bug Reports': 'https://github.com/zlxwl/rasa_chinese_extend_plugin/issues',
        'Source': 'https://github.com/zlxwl/rasa_chinese_extend_plugin',
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)",
        "Operating System :: OS Independent",
    ],
)

print("\nWelcome to Rasa NLU!")
print("If any questions please visit documentation "
      "page https://nlu.rasa.com")