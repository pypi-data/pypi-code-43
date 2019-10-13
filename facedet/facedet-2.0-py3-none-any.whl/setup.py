## import the necessary packages
#from imutils import face_utils
#import numpy as np
#import cv2
#import sys
#import dlib

#detector = dlib.get_frontal_face_detector()
#win = dlib.image_window()
##rect = dlib.draw_rectangle() 

#for f in sys.argv[1:]:
#    print("Processing file: {}".format(f))
#    img = dlib.load_rgb_image(f)
#    # The 1 in the second argument indicates that we should upsample the image
#    # 1 time.  This will make everything bigger and allow us to detect more
#    # faces.
#    dets = detector(img, 1)
#    print("Number of faces detected: {}".format(len(dets)))

#	# datatype is dlib.rectangle
##    print(dets[0])
##    a = np.asarray(dets)
##    print("shape: ", a)
##    cascade = cv2.CascadeClassifier('/Users/snehabelkhale/opencv/data/haarcascades/haarcascade_frontalface_default.xml')
#    cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
#    #get a bounding rectangle for the primary face in the image
#    
#    rects = cascade.detectMultiScale(img, 1.3, 5)
#    # only get the x y w h coordinates of the first face detected
#    x, y, w, h = rects[0].astype(int)
#    # define a rectangle that will contain the face
#    rect = dlib.rectangle(x, y, x + w, y + h)
#    win.set_image(rect)
##    # use our predictor to find the facial points within our bounding box
##    face_points = predictor(img, rect).parts()

##    #save our results in an array
##    landmarks = []
##    for p in face_points:
##        landmarks.append([p.x, p.y])
##    print("landmarks",landmarks) 
#    win.clear_overlay()
##    win.set_image(img)
#    win.add_overlay(dets)

import sys
import dlib
import cv2
import openface
# You can download the required pre-trained face detection model here:
# http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2
predictor_model = "shape_predictor_68_face_landmarks.dat"
# Take the image file name from the command line
file_name = sys.argv[1]
# Create a HOG face detector using the built-in dlib class
face_detector = dlib.get_frontal_face_detector()
face_pose_predictor = dlib.shape_predictor(predictor_model)
face_aligner = openface.AlignDlib(predictor_model)
# Take the image file name from the command line
file_name = sys.argv[1]
# Load the image
image = cv2.imread(file_name)
# Run the HOG face detector on the image data
detected_faces = face_detector(image, 1)
print("Found {} faces in the image file {}".format(len(detected_faces), file_name))
# Loop through each face we found in the image
for i, face_rect in enumerate(detected_faces):
        # Detected faces are returned as an object with the coordinates
        # of the top, left, right and bottom edges
        print("- Face #{} found at Left: {} Top: {} Right: {} Bottom: {}".format(i, face_rect.left(), face_rect.top(), face_rect.right(), face_rect.bottom()))
        # Get the the face's pose
        pose_landmarks = face_pose_predictor(image, face_rect)
        # Use openface to calculate and perform the face alignment
        alignedFace = face_aligner.align(534, image, face_rect, landmarkIndices=openface.AlignDlib.OUTER_EYES_AND_NOSE)
        # Save the aligned image to a file
        cv2.imwrite("aligned_face_{}.jpg".format(i), alignedFace)     

#    skipMulti=False
#    assert img is not None,"Image not found!"
##    dets = self.getAllFaceBoundingBoxes(img)
#    if (not skipMulti and len(dets) > 0) or len(dets) == 1:
#      out = max(dets, key=lambda rect: rect.width() * rect.height())
#      print("largest face co-ordinates:",rect: rect.width)
#      cv2.rectangle(dets, (X, Y), (X + W, Y + H), (0, 255, 0), 2)
#      
#      cv2.imshow("ROI",roi)
##      cv2.imshow(out)
#    else:
#      print("No face found!") 
#    print("one element shape", a[1])

#    for i, d in enumerate(dets):
#        print("Detection {}: Left: {} Top: {} Right: {} Bottom: {}".format(i, d.left(), d.top(), d.right(), d.bottom()))
#        cv2.rectangle(img, (d.left(), d.top()), (d.right(), d.bottom()), (255, 0, 255), 2)
#        W = d.right()-d.bottom()
#        H = d.left()-d.top()
#        area = W*H
#        print(W,H,area)
#        
#        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)


#        cv2.imwrite('faces.jpg',rgb)

#    cv2.imwrite('output.jpg',img)
#    for (x, y, w, h) in dets:
#    for face in dets:
#        x = face.left()
#        y = face.bottom() #could be face.bottom() - not sure
#        w = face.right() - face.left()
#        h = face.top() - face.bottom()
##        dlib::draw_rectangle(rect_image, rect, dlib::rgb_pixel(255, 0, 0), 1)
#        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
#   for k, d in enumerate(dets):
#     print ("Detection {}: Left: {} Top: {} Right: {} Bottom: {}".format(k, d.left(), d.top(), d.right(), d.bottom()))
#     cv2.rectangle(img, (d.left(), d.top()), (d.right(), d.bottom()), (255, 0, 255), 2)
#     cv2.imwrite(outname, img)
#    
#    status = cv2.imshow('output.jpg', img)
#    print("Results are printed into filesystem: ", status)

#        ext_roi = img[d.top():d.bottom(), d.left():d.right()]
#        print("Faces Extracted")
#        rgb = cv2.cvtColor(ext_roi, cv2.COLOR_GRAY2BGR)
#        cv2.imwrite(str(d.left())+'-'+str(d.top())+'face.jpg',rgb)
#    for (x, y, w, h) in faces:
#      cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
#      roi_color = image[y:y + h, x:x + w]
#      print("[INFO] Object found. Saving locally.")
#      cv2.imwrite(str(w) +'-'+ str(h) + 'faces.jpg', roi_color)


#    dlib.hit_enter_to_continue()


# Finally, if you really want to you can ask the detector to tell you the score
# for each detection.  The score is bigger for more confident detections.
# The third argument to run is an optional adjustment to the detection threshold,
# where a negative value will return more detections and a positive value fewer.
# Also, the idx tells you which of the face sub-detectors matched.  This can be
# used to broadly identify faces in different orientations.
#if (len(sys.argv[1:]) > 0):
#    img = dlib.load_rgb_image(sys.argv[1])
#    dets, scores, idx = detector.run(img, 1, -1)
#    for i, d in enumerate(dets):
#        print("Detection {}, score: {}, face_type:{}".format(
#            d, scores[i], idx[i]))
