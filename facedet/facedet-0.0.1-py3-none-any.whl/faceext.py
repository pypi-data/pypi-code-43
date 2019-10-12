import cv2
import sys
import numpy as np
from PIL import Image
from numpy import unravel_index

#imagePath = sys.argv[1]

image = cv2.imread("data/data1.jpg")
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)	#Image grayscaling.

assert image is not None,"Image not found!"

def detection():
 """Extracts the largest face among the total no.of faces detected"""
 print('Imagesize:',image.shape[0:2])
 faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
 faces = faceCascade.detectMultiScale(
    gray,
    scaleFactor=1.3,
    minNeighbors=3,
    minSize=(30, 30)
 )	#Haar-cascade: A Face detection algorithm

 area = faces[:,2] * faces[:,3]
 faces = np.c_[faces,area]	#concatenates area values to last column of 'face' array.

 print('All detected faces\n',faces)
 i,j = unravel_index(faces.argmax(), faces.shape)	# gets the position of maximum value from 'face' array.
 print(i,j)
 print("Found %d Face%s!" %(len(faces),"s"[len(faces)==1:]))

 X = faces[i,0]
 Y = faces[i,1]
 W = faces[i,2]
 H = faces[i,3]
 
 cv2.rectangle(image, (X, Y), (X + W, Y + H), (0, 255, 0), 2)
 roi_color = image[Y:Y + H, X:X + W]    
 print("Face(largest) Extracted.")
 cv2.imwrite('Extracted_face.jpg', roi_color)	#Image Extraction.
 status = cv2.imwrite('Output.jpg', image)
 print("Image Output.jpg written to filesystem: ", status)
# cv2.waitKey(0)

def main():
 condition = image.shape[0] < 1024 and image.shape[1] < 1024
 if condition: 
    detection()
 else:
  print("High-resoluted images are not accepted. Enter images less than 1024*1024 resolution.")
  sys.exit(1)

#main() 
