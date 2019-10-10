from syncvtools.utils.draw_detections import DrawDetections
from syncvtools.utils.parsers import ProdDetections, TFRecords, TFObjDetAPIDetections, PascalVOC
import cv2
import logging


def visualize_prod_detections(img_dir: str, pred_dir: str):
    '''
    Visualize detections in production format (JSON per one scan).
    :param img_dir: directory with images
    :param pred_dir: directory with corresponding predictions in JSON format
    :return:
    '''
    prod_dets = ProdDetections.parse(img_dir=img_dir, predictions_dir=pred_dir)
    drawer = DrawDetections(bbox_line_height=1, threshold=0.5)
    for pro_det in prod_dets:
        if not prod_dets[pro_det].img:
            logging.warning("Image source not found for key: {}".format(pro_det))
            continue
        vis_img = drawer.draw_imageleveldetections(img_dets=prod_dets[pro_det])
        vis_img = cv2.cvtColor(vis_img, cv2.COLOR_RGB2BGR)
        cv2.imshow("predictions", vis_img)
        cv2.waitKey(0)

def visualize_tfrecord_gt(tf_record: str):
    '''
    Just visualize plain TFRecord of TF Object Detection API. TensorFlow should be installed (Object Detection API is not required)
    :param tf_record: path to tf_record
    :return:
    '''
    tf_gts = TFRecords.parse(tfrecord_src=tf_record)
    logging.info("Loaded: {}".format(len(tf_gts)))
    drawer = DrawDetections(bbox_line_height=1, threshold=0.5)
    for pro_det in tf_gts:
        vis_img = drawer.draw_imageleveldetections(img_dets=tf_gts[pro_det])
        vis_img = cv2.cvtColor(vis_img, cv2.COLOR_RGB2BGR)
        cv2.imshow("predictions", vis_img)
        cv2.waitKey(0)

def visualize_tf_validation(tf_inference_json: str, tf_record: str, label_map: str =None):
    '''
    Take a JSON produced by TF Object Detection API training/validation with predictions.
    Enrich it with image data using TFRecord and labels file.
    Draw image predictions with ground truth for images with detections.
    :param tf_inference_json: path to tf_inference_json
    :param tf_record:
    :param label_map:
    :return:
    '''
    tf_inf = TFObjDetAPIDetections.parse(detection_file=tf_inference_json)
    tf_gts = TFRecords.parse(tfrecord_src=tf_record)
    #adding image info to predictions/gt
    tf_inf += tf_gts
    if label_map is not None:
        tf_inf.process_labelmap(label_map)

    drawer = DrawDetections(bbox_line_height=1, threshold=0.5)


    for pro_det in tf_inf:
        if not tf_inf[pro_det].detections and not tf_inf[pro_det].ground_truth:
            continue #no gt/detections here
        vis_img = drawer.draw_imageleveldetections(img_dets=tf_inf[pro_det])
        vis_img = cv2.cvtColor(vis_img, cv2.COLOR_RGB2BGR)
        cv2.imshow("predictions/gt from TF inference", vis_img)
        cv2.waitKey(0)


def visualize_pascalvoc(img_dir: str, pred_dir: str):
    '''
    Visualize detections in PascalVOC (LabelImg) format (XML per one scan).
    :param img_dir: directory with images
    :param pred_dir: directory with corresponding predictions in XML format
    :return:
    '''
    prod_dets = PascalVOC.parse(img_dir=img_dir, predictions_dir=pred_dir)
    drawer = DrawDetections(bbox_line_height=1, threshold=0.5)
    for pro_det in prod_dets:
        vis_img = drawer.draw_imageleveldetections(img_dets=prod_dets[pro_det])
        vis_img = cv2.cvtColor(vis_img, cv2.COLOR_RGB2BGR)
        cv2.imshow("predictions", vis_img)
        cv2.waitKey(0)
