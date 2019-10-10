from typing import List, Dict, Any,Callable
from syncvtools.data.image import Image
from syncvtools.data.detections import DetectionEntity, DetectionsCollection, ImageLevelDetections
import cv2, os, glob, json, hashlib
import numpy as np
import logging
import syncvtools.utils.file_tools as ft
from syncvtools.utils._dependencies import dep

class TFRecordsExport:
    @staticmethod
    def convert(src: DetectionsCollection, out_path: str):
        '''
        Dumps DetectionsCollection object into TensorFlow record format in Object Detection API format.
        :param src:
        :param out_path: path to save TF Record
        :return:
        '''
        if not src:
            raise ValueError("Empty input DetectionsCollection")
        test = next(iter(src.values()))


        tf = dep('tf')
        with  tf.io.TFRecordWriter(out_path) as writer:
            for det_obj in src:
                tf_det_obj = TFRecordsExport.convert_image(img_det=src[det_obj])
                writer.write(tf_det_obj.SerializeToString())
        logging.info("TF Record written: {}. Objects: {}".format(out_path, len(src)))

    @staticmethod
    def convert_image(img_det: ImageLevelDetections):
        '''
        Pieces from  Synapse CV repo and Object Detection API
        :param img_det:
        :return:
        '''
        def int64_feature(value):
            return tf.train.Feature(int64_list=tf.train.Int64List(value=[value]))

        def int64_list_feature(value):
            return tf.train.Feature(int64_list=tf.train.Int64List(value=value))

        def bytes_feature(value):
            return tf.train.Feature(bytes_list=tf.train.BytesList(value=[value]))

        def bytes_list_feature(value):
            return tf.train.Feature(bytes_list=tf.train.BytesList(value=value))

        def float_list_feature(value):
            return tf.train.Feature(float_list=tf.train.FloatList(value=value))

        if not img_det.img:
            raise ValueError("Images are not set! Can't convert to TF Record")
        tf = dep('tf')
        #to use OpenCV for encoding we need convert to BGR
        img_np = cv2.cvtColor(img_det.img.img_np, cv2.COLOR_RGB2BGR)
        img_conv_success, jpeg_numpy = cv2.imencode('.png', img_np)
        if not img_conv_success:
            raise ValueError("Cannot encode numpy image to jpg! Status: {}".format(img_conv_success))
        image_enc_bytes = jpeg_numpy.tostring()
        key = hashlib.sha256(image_enc_bytes).hexdigest()
        bbox_coords = ([],[],[],[])
        classes = []
        classes_text = []
        label_full_tag = []
        truncated = []
        poses = []
        difficult_obj = []
        if img_det.ground_truth is None:
            raise ValueError("Ground truth is not set for the input. TF format expects ground truth.")

        for gt in img_det.ground_truth:
            if gt.label_id is None:
                raise ValueError("You need to assign label_id to all boxes. Call .process_labelmap() on DetectionCollections object")
            classes.append(gt.label_id)
            if not gt.label_text:
                raise ValueError("You need to assign label_text to all boxes. Call .process_labelmap() on DetectionCollections object")
            classes_text.append(gt.label_text.encode('utf-8'))
            if gt.label_full_tag is not None:
                label_full_tag.append(gt.label_full_tag.encode('utf-8'))
            truncated.append(0)
            difficult_obj.append(0)
            poses.append("".encode('utf8'))
            for i in range(len(bbox_coords)):
                bbox_coords[i].append(gt.bbox.bbox_norm[i])



        return tf.train.Example(features=tf.train.Features(feature={
            'image/height': int64_feature(img_det.img.img_size.as_tuple()[1]),
            'image/width': int64_feature(img_det.img.img_size.as_tuple()[0]),
            'image/filename': bytes_feature(
                img_det.img.img_filename.encode('utf8')),
            'image/source_id': bytes_feature(
                img_det.img.img_filename.encode('utf8')),
            'image/key/sha256': bytes_feature(key.encode('utf8')),
            'image/encoded': bytes_feature(image_enc_bytes),
            'image/format': bytes_feature('png'.encode('utf8')),
            'image/object/bbox/xmin': float_list_feature(bbox_coords[0]),
            'image/object/bbox/xmax': float_list_feature(bbox_coords[2]),
            'image/object/bbox/ymin': float_list_feature(bbox_coords[1]),
            'image/object/bbox/ymax': float_list_feature(bbox_coords[3]),
            'image/object/class/text': bytes_list_feature(classes_text),
            'image/object/class/label': int64_list_feature(classes),
            'image/object/difficult': int64_list_feature(difficult_obj),
            'image/object/truncated': int64_list_feature(truncated),
            'image/object/view': bytes_list_feature(poses),
            'image/object/category': bytes_list_feature(label_full_tag),
        }))





