import setuptools
import wfp

setuptools.setup(
    name=wfp.__name__,
    version=wfp.__version__,
    author="wangab",
    author_email="wangab@yunanbao.com.cn",
    description="A proxy application for kubeflow pipeline",
    long_description="A proxy application for kubeflow pipeline",
    url="http://www.yunanbao.com.cn",
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=[
        "traitlets==4.3.2",
        "kfp==0.1.11",
        "wf-pipeline-api==1.2.0rc0"
    ],
    python_requires=">=3.5",
    entry_points={
        'console_scripts': [
            'wfp = wfp.app:main'
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
