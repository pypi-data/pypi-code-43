'''
    File name: math_utils.py
    Author: [Mochammad F Rahman]
    Date created: / /2019
    Date last modified: 31/07/2019
    Python Version: >= 3.5
    Simple-tensor version: v0.3
    License: MIT License
    Maintainer: [Mochammad F Rahman]
'''

import cv2
import numpy as np 
import random
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon


class LineInspect():
    def __init__(self, image_shape, lines, decay=0.001):
        """[summary]
        
        Arguments:
            image_shape {list of list of int} -- 
            lines {[type]} -- [description]
        
        Keyword Arguments:
            decay {float} -- [description] (default: {0.001})
        """
        # ------------------------------------ #
        # get the width of image               #
        # for each line in line list:          #
        # -- get the pointss, gradient, and cutting point
        # -- loop over x (image width)         #
        # -- calculate the line point on (x, y)#
        # -- -- check it insides image or not  #
        # ------------------------------------ #
        self.image_w = image_shape[1]
        self.lines = lines
        self.line_points = []
        
        for i in self.lines:
            m = (i[3] - i[1])/(i[2] - i[0] + decay)
            b = i[1]-(m * i[0])
            
            for j in range(self.image_w):
                # check the x limit 
                if j > min(i[0], i[2]) or j < max(i[0], i[2]):
                    y = int(m * j + b)
                    # check the j limit
                    if y > min(i[1], i[3]) and y < max(i[1], i[3]):
                        self.line_points.append([j, y])

        # ------------------------------------- #
        # line eqution for discrete is different with analog
        # in discrete, the minimum unit is integer
        # for line with high gradient,          #
        # the y value for each x is jumping     #
        # this method is designed for handling this problem
        # ------------------------------------- #
        for idx, i in enumerate(self.line_points):
            delta = 0

            if idx > 0:
                y_point_before = self.line_points[idx-1][1]
                y_point_now = i[1]
                delta = abs(y_point_now - y_point_before)
            
            for j in range(delta):
                new_y = y_point_before + j + 1
                self.line_points.append([i[0], new_y])


    def is_crossing_line(self, rects, reduce_rect_size=0.3):
        """[summary]
        
        Arguments:
            rects {[type]} -- [description]
        
        Keyword Arguments:
            reduce_rect_size {float} -- [description] (default: {0.3})
        
        Returns:
            [type] -- [description]
        """
        is_crossing = []
        for i in rects:
            is_point_inside = False
            height = abs(i[3] - i[1])
            xr1 = i[0] 
            xr2 = i[2]
            yr1 = i[1] + (reduce_rect_size * height / 2)
            yr2 = i[3] - (reduce_rect_size * height / 2)
            for j in self.line_points:
                if j[0] > xr1 and j[0] < xr2 and j[1]>yr1 and j[1] < yr2:
                    is_point_inside = True
                    break
            if is_point_inside:
                is_crossing.append([1, i])
        return is_crossing

    def crossing_flow(self):
        a = 0


def nms(batch, num_class, confidence_threshold=0.5, overlap_threshold=0.5, is_relative=False, size=416):
    """[summary]
    Arguments:
        num_class{int} -- the number of object class
    
    Keyword Arguments:
        confidence_threshold {float} -- [description] (default: {0.5})
        overlap_threshold {float} -- [description] (default: {0.5})
        is_relative {bool} --  [description] (default: {False})
    
    Returns:
        [type] -- [description]
    """

    result_box = []
    result_conf = []
    result_class = []
    final_box = []
    
    for boxes in batch:
        mask = boxes[:, 4] > confidence_thresholdt
        boxes = boxes[mask, :] 
        classes = np.argmax(boxes[:, 5:], axis=-1)
        classes = classes.astype(np.float32).reshape((classes.shape[0], 1))
        boxes = np.concatenate((boxes[:, :5], classes), axis=-1)
        
        # ------------------------------------ #
        # NMS for EACH CLASS                   #
        # ------------------------------------ #
        boxes_dict = dict()
        for cls in range(num_class):
            mask = (boxes[:, 5] == cls)
            mask_shape = mask.shape
            
            if np.sum(mask.astype(np.int)) != 0:
                class_boxes = boxes[mask, :]
                boxes_coords = class_boxes[:, :4]
                boxes_ = boxes_coords.copy()
                boxes_[:, 2] = (boxes_coords[:, 2] - boxes_coords[:, 0])
                boxes_[:, 3] = (boxes_coords[:, 3] - boxes_coords[:, 1])
                boxes_ = boxes_.astype(np.int)
                
                boxes_conf_scores = class_boxes[:, 4:5]
                boxes_conf_scores = boxes_conf_scores.reshape((len(boxes_conf_scores)))
                the_class = class_boxes[:, 5:]

                result_box.extend(boxes_.tolist())
                result_conf.extend(boxes_conf_scores.tolist())
                result_class.extend(the_class.tolist())
    
    indices = cv2.dnn.NMSBoxes(result_box, result_conf, confidence_threshold, overlap_threshold)
    for i in indices:
        i = i[0]
        box = result_box[i]
        left = box[0]
        top = box[1]
        width = box[2]
        height = box[3]
        conf = result_conf[i]
        the_class = result_class[i][0]

        if is_relative:
            final_box.append([float(left)/size, float(top)/size, float(width)/size, float(height)/size, conf, the_class])
        else:
            final_box.append([left, top, width, height, conf, the_class])
    return final_box


def point_inside_area(area_list, point_list):
    """[summary]
    
    Arguments:
        area_list {list of list} -- the list of areas
        point_list {list of list} -- the list of points
    """

    result = []
    for idi, i in enumerate(area_list):
        polygon = Polygon(i)

        for idj, j in enumerate(point_list):
            point = Point(j[0], j[1])
            res = polygon.contains(point)
            result.append((idi, idj, res))
    
    return result

