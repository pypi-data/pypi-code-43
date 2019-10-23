import os
from imutils import paths
import numpy as np
from clearviewai.processing.aspectresize import AspectAwareResize
from clearviewai.processing.simple_processor import SimplePreprocessor, ImageToArray
from clearviewai.processing.image_loader import SimpleDataSetLoader
import cv2
from keras.models import load_model


def check_model(input_dir, model_path, image_size, bs=32, test_size=10):
    print("[INFO] loading images")
    imagePaths = list(paths.list_images(input_dir))

    classNames = [pt.split(os.path.sep)[-2] for pt in imagePaths]
    classNames = [str(x) for x in np.unique(classNames)]

    # grab the list of images in the dataset then randomly sample
    # indexes into the image paths list
    print("[INFO] sampling images...")
    imagePaths = np.array(list(paths.list_images(input_dir)))
    idxs = np.random.randint(0, len(imagePaths), size=(test_size,))
    imagePaths = imagePaths[idxs]

    s = AspectAwareResize(image_size, image_size)
    iap = ImageToArray()


    sdl = SimpleDataSetLoader(preprocessors=[s, iap])
    (data, labels) = sdl.load(imagePaths, verbose=500)
    data = data.astype("float") / 255.0

    print("[INFO] loading model")
    model = load_model(model_path)

    print("[INFO] predicting")
    pred = model.predict(data, batch_size=bs).argmax(axis=1)

    points = 0.0
    #
    for (i, imagePath) in enumerate(imagePaths):
    # load the example image, draw the prediction, and display it
    # to our screen
        image = cv2.imread(imagePath)
        title = imagePath.split(os.path.sep)[-2]
        if title == classNames[pred[i]]:
            points += 1
        cv2.putText(image, "Label: {}".format(classNames[pred[i]]),(10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.imshow(title, image)
        cv2.waitKey(0)

    score = float(points / test_size) * 100
    print("score is {} %".format(score))
