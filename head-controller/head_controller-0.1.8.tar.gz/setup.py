from setuptools import setup

long_description = '''

#### Requirements

- Anaconda Python >= 3.7

#### Quickstart

Quickly train 4 gestures for the model to learn. Press the UP, DOWN, RIGHT, and LEFT arrows on your keyboard to 'label' each gesture in realtime. After 30 seconds you'll be prompted to save (append) the new training data. It will immediately show you a cross-validation score of the fitted data.
Initialize, Train, and Predict in less than 60 seconds (using your webcam).


```
import head_controller.db as db
import head_controller.Camera as Camera

# Initialize gesture training data
db.setup_db()

# Capture webcam gestures with live arrow-key labelling
Camera.capture_review_submit_labels()

# Realtime predict webcam gestures
Camera.check_video_frame_data_predict()
```

'''

setup(
    name='head_controller',
    packages=['head_controller'],
    description='A package to quickly train and predict head gestures',
    long_description=long_description,
    version='0.1.8',
    url = 'https://github.com/nightvision04/simple-gesture-tracking',
    author='Dan Scott',
    author_email='danscottlearns@gmail.com',
    keywords=['head','controller','nueral net','movement','axis','recognition','computer vision','head tracking'],
    install_requires=[
          'opencv-python',
          'mysqlclient',
          'pymysql',
          'sklearn'
      ],
      classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3.7',
  ],
    )
