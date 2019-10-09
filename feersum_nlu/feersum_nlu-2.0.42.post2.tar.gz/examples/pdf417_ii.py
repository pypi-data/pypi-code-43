# """ Example: Shows how to create, train and use a image classifier. """
#
# import urllib3
# import cv2
# from typing import List, Tuple
# import uuid
# import os
# import numpy as np
#
#
# def load_templates(data_path: str):
#     directory = os.fsencode(data_path)
#
#     template_list = []
#
#     for file in os.listdir(directory):
#         filename = os.fsdecode(file)
#         if filename.lower().endswith((".jpg", ".jpeg", ".j2k", ".j2p", ".jpx", ".png", ".bmp")):
#             image = cv2.imread(data_path + "/" + filename)
#             image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#
#             height, width = image.shape[:2]
#             resized_height = 32
#             resized_width = 32  # int((resized_height / height) * width)
#
#             image = cv2.resize(image, (resized_width, resized_height),
#                                interpolation=cv2.INTER_LINEAR)  # pylint: disable=no-member
#
#             label = filename[:filename.find('_')]
#
#             template_list.append((image, label))
#
#     return template_list
#
#
# def segment_lines(image, y0: int, y1: int) -> List[Tuple[int, int]]:
#     im_heigh, im_width = image.shape[:2]
#     filt_window_size = 40
#
#     line_sum_list = []  #
#
#     for y in range(y0, y1):
#         line_sum = 0.0
#
#         for x in range(-im_width//3, im_width//3):
#             line_sum += image[y, x + im_width//2]
#
#         line_sum_list.append(line_sum)
#
#     line_list = []  # type: List[Tuple[int, int]]
#     above_threshold = True
#     line_start = 0
#
#     for h in range(y0+filt_window_size, y1-filt_window_size):
#         window_max = max(line_sum_list[h - filt_window_size: h + filt_window_size])
#
#         if above_threshold and (line_sum_list[h] < window_max*0.95):
#             line_start = h
#             above_threshold = False
#         elif (not above_threshold) and (line_sum_list[h] > window_max*0.95):
#             line_list.append((line_start, h))
#             above_threshold = True
#
#     return line_list
#
#
# def segment_chars(image, y0: int, y1: int) -> List[Tuple[int, int]]:
#     im_heigh, im_width = image.shape[:2]
#     filt_window_size = 20
#
#     col_sum_list = []
#
#     for x in range(0, im_width):
#         col_sum = 0.0
#
#         for y in range(y0, y1):
#             col_sum += image[y, x]
#
#         col_sum_list.append(col_sum)
#
#     char_list = []  # type: List[Tuple[int, int]]
#     above_threshold = True
#     char_start = 0
#
#     for w in range(0+filt_window_size, im_width-filt_window_size):
#         window_max = max(col_sum_list[w - filt_window_size: w + filt_window_size])
#
#         if above_threshold and (col_sum_list[w] < window_max*0.95):
#             char_start = w
#             above_threshold = False
#         elif (not above_threshold) and (col_sum_list[w] > window_max*0.95):
#             char_list.append((char_start, w))
#             above_threshold = True
#
#     return char_list
#
#
# def main():
#
#     character_template_list = load_templates("/Users/bduvenhage/myWork/dev/Praekelt/feersum-nlu-api-wrappers_develop/"
#                                              "examples/templates")
#
#     # cap = cv2.VideoCapture(0)  # pylint: disable=no-member
#     while True:
#         # Capture frame-by-frame
#         # ret, frame = cap.read()
#
#         frame = cv2.imread('/Users/bduvenhage/Desktop/disc5.jpg')
#         frame = cv2.GaussianBlur(frame, (3, 3), 0)
#
#         height, width = frame.shape[:2]
#         target_size = 800
#
#         if width > height:
#             resized_height = target_size
#             resized_width = int((target_size / height) * width)
#         else:
#             resized_height = int((target_size / width) * height)
#             resized_width = target_size
#
#         resized_image = \
#             cv2.resize(frame, (resized_width, resized_height), interpolation=cv2.INTER_LINEAR)  # pylint: disable=no-member
#
#         gray_image = cv2.cvtColor(resized_image, cv2.COLOR_BGR2GRAY)
#         thresholded_image = cv2.adaptiveThreshold(gray_image, 255,
#                                                   cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY,
#                                                   ((target_size//20)//2)*2+1, 20)
#
#         line_list = segment_lines(thresholded_image, 0, resized_height)
#
#         final_image = cv2.cvtColor(thresholded_image, cv2.COLOR_GRAY2BGR)
#
#         run_id = uuid.uuid4()
#         char_num = 0
#
#         for line_start, line_end in line_list:
#             cv2.line(final_image, (0, line_start), (resized_width, line_start), (255, 0, 0), 1)
#             cv2.line(final_image, (0, line_end), (resized_width, line_end), (255, 0, 0), 1)
#
#             char_list = segment_chars(thresholded_image, line_start, line_end)
#
#             for char_start, char_end in char_list:
#                 cv2.line(final_image, (char_start, line_start), (char_start, line_end), (255, 0, 0), 1)
#                 cv2.line(final_image, (char_end, line_start), (char_end, line_end), (255, 0, 0), 1)
#
#                 char_image = thresholded_image[(line_start-1):(line_end+1), (char_start-1):(char_end+1)]
#
#                 # Save the char image.
#                 # cv2.imwrite(f"images/{run_id}_{char_num}.jpg", char_image)
#
#                 char_height, char_width = char_image.shape[:2]
#                 resized_char_height = 32
#                 resized_char_width = 32  # int((resized_char_height / char_height) * char_width)
#
#                 char_image = cv2.resize(char_image, (resized_char_width, resized_char_height),
#                                         interpolation=cv2.INTER_LINEAR)  # pylint: disable=no-member
#
#                 char_num += 1
#
#                 min_template_error = np.inf
#                 min_template_idx = 0
#
#                 # Find the closest template
#                 for template_idx, template in enumerate(character_template_list):
#
#                     template_error = \
#                         (np.abs(np.array(char_image, np.float32) - np.array(template[0], np.float32))).mean(axis=None)
#
#                     if template_error < min_template_error:
#                         min_template_idx = template_idx
#                         min_template_error = template_error
#
#                 if min_template_error < 20.0:
#                     char_value = character_template_list[min_template_idx][1]
#                     print(char_value, end='')
#
#         display_text = "text"
#
#         # Display the resulting frame
#         font = cv2.FONT_HERSHEY_SIMPLEX  # pylint: disable=no-member
#         cv2.putText(final_image,  # pylint: disable=no-member
#                     f"{display_text}",  # pylint: disable=no-member
#                     (10, 30), font, 1, (0, 0, 0), 5)  # pylint: disable=no-member
#         cv2.putText(final_image,  # pylint: disable=no-member
#                     f"{display_text}",  # pylint: disable=no-member
#                     (10, 30), font, 1, (255, 255, 255), 2)  # pylint: disable=no-member
#
#         cv2.imshow('final_image', final_image)  # pylint: disable=no-member
#
#         if cv2.waitKey(100) & 0xFF == ord('q'):  # pylint: disable=no-member
#             break
#
#     # When everything done, release the capture
#     cap.release()
#     cv2.destroyAllWindows()  # pylint: disable=no-member
#
#
# main()
