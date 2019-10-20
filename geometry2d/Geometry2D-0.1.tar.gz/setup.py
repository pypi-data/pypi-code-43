import setuptools
with open("README.md", "r") as fh:
    long_description = fh.read()
setuptools.setup(
     name='Geometry2D',  
     version='0.1',
     packages=['Geometry2D'] ,
     license='MIT',
     author="Ron Rivest",
     author_email="ron.rivest@gmail.com",
     description="This is a library for creating and manipulating 2D Geometric Shapes",
     url="https://github.com/circleshavecorners/Geometry2D",
     download_url="https://github.com/circleshavecorners/Geometry2D/archive/v_01.tar.gz",
     classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3',      #Specify which pyhton versions that you want to support
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
  ],
 )
