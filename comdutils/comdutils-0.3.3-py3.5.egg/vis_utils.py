import cv2
import numpy as np 
import random


def give_frame(image, company_name, project_name):
	"""
	a function for giving an image a frame witch contains a rectngle border, company and project name at the top
	Args:
		image:				an opencv image with format of BGR
		company_name:		a string, the name of the company
		project_name:       a string, the name of the project
	Return:
		An opencv image
	"""
	# get the characteristic of the image
	h, w, _ = image.shape
	# we wan to make a fullfill rectangle on the top of the image
	space = int(0.1 * h/2)
	cv2.rectangle(image, (0, 0), (int(0.5 * w), int(0.1 * h)), (255, 255, 255), -1)
	# put project name on the rectangle
	cv2.putText(image, project_name, (5, int( 5 + space/2)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 100, 255), 2, cv2.LINE_AA)
	# put company name on the rectangle
	cv2.putText(image, company_name, (5, int( 5 + space + space/2)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 100, 255), 2, cv2.LINE_AA)
	return image


def draw_rectangles(image, rects, COLORS):
	"""
	a function for drawing some rectangles with random color
	Args:
		image:				an opencv image with format of BGR
		rects:				a list of opencv rectangle
		COLORS:       		a list of opencv color 
	Return:
		An opencv image
	"""
	# draw the rectangle
	for i in rects:
		# get random color
		idx = random.randint(0,len(COLORS)-1)
		rect_width = int(abs(i[2] - i[0]))
		rect_height = int(abs(i[3] - i[1]))
		# draw rectangle
		cv2.rectangle(image, (i[0], i[1]), (i[2], i[3]), COLORS[idx], 1)

		# top left 
		cv2.line(image, (i[0], i[1]), (int(i[0] + rect_width/4), i[1]), COLORS[idx], 2)
		cv2.line(image, (i[0], i[1]), (i[0], int(i[1] + rect_height/4)), COLORS[idx], 2)
		# bottom left
		cv2.line(image, (i[0], i[3]), (int(i[0] + rect_width/4), i[3]), COLORS[idx], 2)
		cv2.line(image, (i[0], i[3]), (i[0], int(i[3] - rect_height/4)), COLORS[idx], 2)
		# top right 
		cv2.line(image, (i[2], i[1]), (int(i[2] - rect_width/4), i[1]), COLORS[idx], 2)
		cv2.line(image, (i[2], i[1]), (i[2], int(i[1] + rect_height/4)), COLORS[idx], 2)
		# bottom left
		cv2.line(image, (i[2], i[3]), (int(i[2] - rect_width/4), i[3]), COLORS[idx], 2)
		cv2.line(image, (i[2], i[3]), (i[2], int(i[3] - rect_height/4)), COLORS[idx], 2)
		# ---- outer
		i[0] = i[0] - int(0.05 * rect_width)
		i[2] = i[2] + int(0.05 * rect_width)
		i[1] = i[1] - int(0.05 * rect_width)
		i[3] = i[3] + int(0.05 * rect_width)
		# top left 
		cv2.line(image, (i[0], i[1]), (int(i[0] + rect_width/8), i[1]), COLORS[idx], 2)
		cv2.line(image, (i[0], i[1]), (i[0], int(i[1] + rect_height/8)), COLORS[idx], 2)
		# bottom left
		cv2.line(image, (i[0], i[3]), (int(i[0] + rect_width/8), i[3]), COLORS[idx], 2)
		cv2.line(image, (i[0], i[3]), (i[0], int(i[3] - rect_height/8)), COLORS[idx], 2)
		# top right 
		cv2.line(image, (i[2], i[1]), (int(i[2] - rect_width/8), i[1]), COLORS[idx], 2)
		cv2.line(image, (i[2], i[1]), (i[2], int(i[1] + rect_height/8)), COLORS[idx], 2)
		# bottom left
		cv2.line(image, (i[2], i[3]), (int(i[2] - rect_width/8), i[3]), COLORS[idx], 2)
		cv2.line(image, (i[2], i[3]), (i[2], int(i[3] - rect_height/8)), COLORS[idx], 2)
	return image


def put_topoverlays(image, rects, alpha=0.3):
	"""
	a function for drawing some rectangles with random color
	Args:
		image:				an opencv image with format of BGR
		rects:				a list of opencv rectangle
		alpha:       		a float, blend level
	Return:
		An opencv image
	"""
	h, w, _ = image.shape
	im = np.ones(shape=image.shape).astype(np.uint8)
	overlay_bboxs = []
	for i in rects:
		x1 = int(i[0])
		x2 = int(min(i[0] + 1.7 * (i[2] - i[0]), w))
		y1 = int(i[1])
		y2 = int(max(i[1] - 0.2 * (i[3] - i[1]), 0))
		overlay_bboxs.append([x1, y1, x2, y2])
		cv2.rectangle(im, (x1, y1), (x2, y2), (100, 100, 0), -1)
		cv2.rectangle(im, (x1, y1), (x2, y2), (0, 100, 255), 2)
	image = cv2.addWeighted(im, alpha, image, 1 - alpha, 0, image)
	return image, overlay_bboxs


def put_vertical_textsoverrect(image, rects, text_list):
	"""
	a function for drawing some rectangles with random color
	Args:
		image:				an opencv image with format of BGR
		rects:				a list of opencv rectangle
		text_list:       	a list of string
	Return:
		An opencv image
	"""
	for idx, i in enumerate(rects):
		h = i[3] - i[1]
		space = int(h/len(text_list[0]))

		for idx2, j in enumerate(text_list[idx]):
			cv2.putText(image, j, ((i[0] + 5), int(i[1] + space * idx2 + space/2)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2, cv2.LINE_AA)
	return image


def draw_yolo_bbox(bbox_list, label_list, image, font_size=1, line_size=1, color=(0, 255, 100)):
	"""function for drawing yolo bbox
	
	Arguments:
		bbox_list {list of integer list} -- list of bounding box, ex: [[0, 10, 100, 120], [100, 10, 100, 120]]
		label_list {list of string} -- the label list
		image {numpy array} -- opencv numpy image
	
	Keyword Arguments:
		font_size {int} -- [description] (default: {1})
		line_size {int} -- [description] (default: {1})
		color {tuple} -- [description] (default: {(0, 255, 100)})
	
	Returns:
		[numpy array] -- the result image
	"""
	for i, j in zip(bbox_list, label_list):
        cv2.rectangle(image, (i[0], i[1]), (i[2], i[3]), color, line_size)
		cv2.putText(image, j, (i[0], i[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, font_size, cv2.LINE_AA)
	
	return image
