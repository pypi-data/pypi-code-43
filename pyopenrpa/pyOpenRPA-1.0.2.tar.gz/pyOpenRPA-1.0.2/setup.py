from setuptools import setup, find_packages

setup(name='pyOpenRPA',
      version='1.0.2',
      description='First open source RPA platform for business',
      long_description='Long description',
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
      ],
      keywords='OpenRPA RPA Robot Automation Robotization',
      url='https://gitlab.com/UnicodeLabs/OpenRPA',
      author='Ivan Maslov',
      author_email='Ivan.Maslov@unicodelabs.ru',
      license='MIT',
      packages=find_packages(),
      install_requires=[
          'pywinauto>=0.6.6','WMI>=1.4.9','pillow>=6.0.0','keyboard>=0.13.3','pyautogui>=0.9.44','pywin32>=224','selenium>=3.141.0','opencv-python>=4.1.1.26','pytesseract>=0.3.0','requests>=2.22.0','lxml>=4.4.1'
      ],
      include_package_data=True,
      zip_safe=False)