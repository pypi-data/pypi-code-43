try:
    from setuptools import setup
except:
    from distutils.core import setup

setup(
    name='keras_augm_layer',
    version='1.0.4',
    author='Roman Sol (ZFTurbo)',
    packages=['keras_augm_layer', ],
    url='https://github.com/ZFTurbo/Keras-augmentation-layer',
    description='Keras implementation of layer which performs augmentations of images using GPU.',
    long_description='Keras implementation of layer which performs augmentations of images using GPU.'
                     'More details: https://github.com/ZFTurbo/Keras-augmentation-layer',
    install_requires=[
        "numpy",
        "pandas",
        "keras",
    ],
)
