    # import the necessary packages
import os
from imutils import paths
import argparse
import cv2


def variance_of_laplacian(image):
    # compute the Laplacian of the image and then return the focus
    # measure, which is simply the variance of the Laplacian
    return cv2.Laplacian(image, cv2.CV_64F).var()


def test_images(image_path, threshold):
    # loop over the input images

    if not os.path.exists(image_path):
        print(f"Directory for images not found: {image_path}")
        return

    num_blurry = 0
    num_not_blurry = 0
    for imagePath in paths.list_images(image_path):
        # load the image, convert it to grayscale, and compute the
        # focus measure of the image using the Variance of Laplacian
        # method
        image = cv2.imread(imagePath)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        fm = variance_of_laplacian(gray)
        blurry = fm < threshold

        if blurry:
            num_blurry += 1
        else:
            num_not_blurry +=1

        #print(fm)
        print(f"{imagePath} - Blurry={blurry}")

    if num_blurry + num_not_blurry == 0:
        print("No results.")
    else:
        print(f"\nResults: {num_blurry} blurry, {num_not_blurry} not blurry")

def main():

    # construct the argument parse and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--image-path",
                    help="path to input directory of images", default="img")
    ap.add_argument("-t", "--threshold", type=float, default=200.0,
                    help="focus measures that fall below this value will be considered 'blurry'")
    args = vars(ap.parse_args())
    test_images(args['image_path'], args['threshold'])



if __name__ == "__main__":
    main()