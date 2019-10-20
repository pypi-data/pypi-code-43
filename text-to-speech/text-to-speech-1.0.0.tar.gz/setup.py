import setuptools

with open('README.md') as f:
    README = f.read()

setuptools.setup(
    author="Thomas Dewitte",
    author_email="thomasdewittecontact@gmail.com",

    name='text-to-speech',
    version='1.0.0',
    license="MIT",
    url='https://github.com/dewittethomas/text-to-speech',
    
    description='A python package that says something of your choice',
    long_description=README,
    long_description_content_type="text/markdown",

    package_dir={"text-to-speech": "text-to-speech"},
    install_requires=["playsound>=1.2.2", "gTTS>=2.0.4"],
    
    packages=setuptools.find_packages(),

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 3'
    ]
)