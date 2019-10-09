# """ Example: Shows how to create, train and use a image classifier. """
#
# import urllib3
# import cv2
# import numpy as np
#
#
# # cap = cv2.VideoCapture(0)  # pylint: disable=no-member
# while True:
#     # Capture frame-by-frame
#     # ret, frame = cap.read()
#
#     frame = cv2.imread('/Users/bduvenhage/Desktop/disc3.jpg')
#
#     height, width = frame.shape[:2]
#     target_size = 512
#
#     if width > height:
#         resized_height = target_size
#         resized_width = int((target_size / height) * width)
#     else:
#         resized_height = int((target_size / width) * height)
#         resized_width = target_size
#
#     resized_image = \
#         cv2.resize(frame, (resized_width, resized_height), interpolation=cv2.INTER_LINEAR)  # pylint: disable=no-member
#
#     gray_image = cv2.cvtColor(resized_image, cv2.COLOR_BGR2GRAY)
#
#     # gray_image = gray_image / 256.0
#     # blurred_im = cv2.GaussianBlur(gray_image, (65, 65), 0)
#     # im = (gray_image - blurred_im)*0.5 + 0.5
#     im = gray_image
#
#     kernel = np.ones((3, 3), np.uint8)
#     im = cv2.morphologyEx(im, cv2.MORPH_BLACKHAT, kernel, anchor=(-1, -1))
#
#     # thresh, im = cv2.threshold(im, 0.1, 1.0, cv2.THRESH_BINARY)
#     thresh, im = cv2.threshold(im, 20, 255, cv2.THRESH_BINARY)
#
#     kernel = np.ones((3, 3), np.uint8)
#     im = cv2.morphologyEx(im, cv2.MORPH_DILATE, kernel, anchor=(-1, -1), iterations=2)
#     im = cv2.morphologyEx(im, cv2.MORPH_ERODE, kernel, anchor=(-1, -1), iterations=2)
#     im = cv2.morphologyEx(im, cv2.MORPH_DILATE, kernel, anchor=(-1, -1), iterations=2)
#
#     kernel = np.ones((3, 3), np.uint8)
#     im = cv2.morphologyEx(im, cv2.MORPH_OPEN, kernel, iterations=2)
#
#     # kernel = np.ones((3, 3), np.uint8)
#     # im = cv2.morphologyEx(im, cv2.MORPH_OPEN, kernel, iterations=3)
#
#     # kernel = np.ones((5, 5), np.uint8)
#     # im = cv2.morphologyEx(im, cv2.MORPH_DILATE, kernel, anchor=(-1, -1), iterations=2)
#     # im = cv2.morphologyEx(im, cv2.MORPH_ERODE, kernel, anchor=(-1, -1), iterations=2)
#     # im = cv2.morphologyEx(im, cv2.MORPH_CLOSE, kernel, anchor=(-1, -1), iterations=2)
#
#     # kernel = np.ones((30, 90), np.uint8)
#     # im = cv2.morphologyEx(im, cv2.MORPH_OPEN, kernel, iterations=1)
#
#     final_image = cv2.bitwise_and(gray_image, im)
#     # final_image = im
#
#     final_image = cv2.cvtColor(final_image, cv2.COLOR_GRAY2BGR)
#
#     contours, hierarchy = cv2.findContours(im, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
#
#     if contours is not None:
#         for contour in contours:
#
#             if cv2.contourArea(contour) <= 200:
#                 continue
#
#             rect = cv2.minAreaRect(contour)
#             box = cv2.boxPoints(rect)
#             box = np.int0(box)
#             cv2.drawContours(final_image, [box], 0, (255, 255, 0), thickness=1)
#
#     display_text = "text"
#
#     # Display the resulting frame
#     font = cv2.FONT_HERSHEY_SIMPLEX  # pylint: disable=no-member
#     cv2.putText(final_image,  # pylint: disable=no-member
#                 f"{display_text}",  # pylint: disable=no-member
#                 (10, 30), font, 1, (0, 0, 0), 5)  # pylint: disable=no-member
#     cv2.putText(final_image,  # pylint: disable=no-member
#                 f"{display_text}",  # pylint: disable=no-member
#                 (10, 30), font, 1, (255, 255, 255), 2)  # pylint: disable=no-member
#
#     cv2.imshow('final_image', final_image)  # pylint: disable=no-member
#
#     if cv2.waitKey(1) & 0xFF == ord('q'):  # pylint: disable=no-member
#         break
#
# # When everything done, release the capture
# cap.release()
# cv2.destroyAllWindows()  # pylint: disable=no-member
#
