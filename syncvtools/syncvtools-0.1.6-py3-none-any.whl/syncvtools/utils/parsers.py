from typing import List, Dict, Any,Callable, Tuple
from syncvtools.data.image import Image
from syncvtools.data.detections import DetectionEntity, DetectionsCollection, ImageLevelDetections
import cv2, os, glob, json
import numpy as np
import logging
import syncvtools.utils.file_tools as ft
from syncvtools.utils._dependencies import dep


def image_from_numpy(img_np: np.ndarray, file_name: str = None) -> Image:
    if img_np.dtype != np.uint8:
        raise ValueError("Image should be uint8! Given: {}".format(img_np.dtype))
    if img_np is None:
        raise ValueError("None value is provided instead of numpy array")
    if len(img_np.shape) != 3:
        raise ValueError("Image shape should be always 3. Given: {}".format(img_np.shape))
    img = Image(img_np=img_np, img_filename=file_name)
    return img




def img_read_from_disk(file_src: str) -> Image:
    '''
    Read image from disk to Image object.
    :param file_src:
    :return:
    '''
    if not os.path.exists((file_src)):
        raise ValueError("File doesn't exist: {}".format(file_src))

    file_size = os.path.getsize(file_src)
    if file_size == 0:
        raise ValueError("Empty file size: {}".format(file_src))

    img_np = cv2.imread(filename=file_src)
    img_np = cv2.cvtColor(img_np, cv2.COLOR_BGR2RGB)

    img = image_from_numpy(img_np, file_name=os.path.basename(file_src))
    return img


def imgs_read_from_dir(img_dir: str, types = ('jpg','png','jpeg')) -> dict:
    '''
    Read images into dict of Image objects (img_name => Image obj) from given directory
    :param img_dir:
    :param types: tuple of valid extensions (no dot)
    :return: Dictionary with key: image name without extension (common key in our data), value: Image
    '''
    #if img_dir.endswith('/'):
    #    img_dir = img_dir[:-1]
    #types_masks = ["{}/*.{}".format(img_dir,x) for x in types]
    #imgs_src = glob.glob(types_masks)
    imgs_src = ft.get_file_list_by_ext(dir=img_dir, ext=types)
    result_dict = {}
    for img_src in imgs_src:
        try:
            img = img_read_from_disk(file_src = img_src)
        except Exception:
            logging.warning("Image can't be read: {}".format(img_src))
            continue
        file_name = ft.dataset_filename_to_key(img_src)
        result_dict[file_name] = img
    return result_dict




class ProdDetections:
    '''
    Parser for our production inference
    '''
    @staticmethod
    def to_detection_entity(input_dict: dict) -> DetectionEntity:
        '''
        Convert dict parsed from anywhere in our prod format (inference) to our DetectionEntity (one bbox)
        :param input_dict:
        :return:
        '''
        bbox = input_dict['bounding_box']
        bbox = (int(round(bbox['xmin'])), int(round(bbox['ymin'])), int(round(bbox['xmax'])), int(round(bbox['ymax'])))
        score = input_dict['score']['raw_score']
        label_txt = input_dict['class']
        det_obj = DetectionEntity(label_text = label_txt,
                                  bbox_abs=tuple(bbox),
                                  score = score
                                  )
        return det_obj

    @staticmethod
    def from_file(file_src: str,
                  file_parser: Callable[[str],Any] = ft.json_read_to_object) -> List[DetectionEntity]:
        '''
        Convert prod detection (inference) file to list of DetectionEntity. It can later be inserted into ImageLevelDetections
        :param file_src:
        :param file_parser:
        :return:
        '''
        raw_list = file_parser(file_src)
        all_detections = []
        for json_view in raw_list:
            for json_inference in json_view['inferences']:
                det_obj = ProdDetections.to_detection_entity(input_dict= json_inference)
                all_detections.append(det_obj)
        return all_detections

    @staticmethod
    def from_dir(dir_src: str) -> dict:
        '''
        Parse dir with JSON detections from our prod and return dict with img_name => List of DetectionEntity
        :param dir_src:
        :return: Dictionary of key: name without ext, value: list of DetectionEntity
        '''
        if not os.path.isdir(dir_src):
            raise Exception("Provided argument dir_src should be an existing directory")
        det_files = ft.get_file_list_by_ext(dir=dir_src, ext=('json',))
        result_dict = {}
        for det_file in det_files:
            dets = ProdDetections.from_file(file_src=det_file)
            det_key = ft.dataset_filename_to_key(det_file)
            result_dict[det_key] = dets
        return result_dict

    @staticmethod
    def parse(img_dir: str, predictions_dir: str) -> DetectionsCollection:
        '''
        Main entry point.
        :param img_dir: Dir with input images
        :param predictions_dir: Dir with JSON predictions which follow our production format.
        :return: Dictionary with set images and predictions.
        '''
        det_collection = DetectionsCollection()
        preds = ProdDetections.from_dir(predictions_dir)
        #we create/update DetectionsCollection using our predictions
        det_collection.process_detections(preds, update_only=False)
        imgs = imgs_read_from_dir(img_dir=img_dir)
        #for images we just match existing detections, don't create new objects if corresponding detection doesn't exist
        det_collection.process_images(imgs, update_only=True)
        return det_collection


class TFObjDetAPIDetections:
    '''
    Format for  TF Object Detection API to store predictions after validation in JSON file.
    '''
    @staticmethod
    def to_detections_list(input_dict):
        det_list = []
        if isinstance(input_dict, int):
            print(input_dict)
        for bbox, label_id, score in zip(input_dict['detection_boxes'],input_dict['detection_classes'],input_dict['detection_scores']):
            bbox = (bbox[1], bbox[0], bbox[3], bbox[2])
            det_obj = DetectionEntity(bbox_norm=tuple(np.asarray(bbox).clip(0.0,1.0)),
                                      score=score,
                                      label_id=label_id)
            det_list.append(det_obj)

        gt_list = []
        for bbox, label_id, label_txt in zip(input_dict['groundtruth_boxes'],
                                             input_dict['groundtruth_classes'],
                                             input_dict['object_categories']):
            if label_txt.startswith('b\''):
                label_txt = label_txt[2:]
            if label_txt.endswith('\''):
                label_txt = label_txt[:-1]
            bbox = (bbox[1],bbox[0],bbox[3],bbox[2])
            gt_obj = DetectionEntity(bbox_norm=tuple(np.asarray(bbox).clip(0.0,1.0)),
                                     label_id=label_id,
                                     label_text=label_txt)
            gt_list.append(gt_obj)
        return gt_list, det_list


    @staticmethod
    def parse(detection_file: str,
              file_parser: Callable[[str],Any] = ft.json_read_to_object) -> DetectionsCollection:
        '''
        Main entry point.
        :param detection_file: Path to JSON file (usually detections_and_losses.json).
        :param file_parser: Most of the cases leave default JSON parser.
        :return: Dictionary with groundtruth and predictions, but without image data.
        '''
        raw_dict = file_parser(detection_file)
        det_collection = DetectionsCollection()
        gt_list, det_list = {}, {}
        for det_key in raw_dict:
            if not isinstance(raw_dict[det_key],dict): ##adding 'num_images' to the level of detections = bad idea, we need to fix it
                continue
            gt_list_per_image, det_list_per_image = TFObjDetAPIDetections.to_detections_list(input_dict=raw_dict[det_key])
            det_key = ft.dataset_filename_to_key(det_key)
            gt_list[det_key] = gt_list_per_image
            det_list[det_key] = det_list_per_image

        # we create/update DetectionsCollection using our predictions. label_text not filled, coords are normalized
        det_collection.process_detections(det_list, update_only=False)

        # then we update it with ground truth
        det_collection.process_ground_truth(gt_list, update_only=True)

        return det_collection




class TFRecords:
    '''
    Parse Tensorflow TFRecord format.
    '''

    @staticmethod
    def to_dicts(tfrecord_src: str):
        '''
        Parses TFRecord into separate imgs and ground truth dictionaries.
        :param tfrecord_src: path to input TF Record
        :return:
        '''
        tf = dep('tf')
        tf_obj_det_decoder = dep('tf_obj_det_decoder')
        raw_dataset = tf.data.TFRecordDataset([tfrecord_src])
        decoder = tf_obj_det_decoder()
        imgs_dict = {} #images dict key(filename without extension)=>Image
        gts_dict = {} #ground truth dict key=>DetectionEntity
        for raw_record in raw_dataset:
            decoded = decoder.decode(raw_record)
            gt_bboxes = decoded['groundtruth_boxes'].numpy().tolist()

            for i,bbox in enumerate(gt_bboxes):
                #no idea why tf_example_decoder from Object Detection API makes (ymin,xmin,ymax,xmax) format
                gt_bboxes[i] = (bbox[1],bbox[0],bbox[3],bbox[2])

            image = decoded['image'].numpy()
            #it's BGR
            #image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image_filename = decoded['filename'].numpy().decode("utf-8")
            key = ft.dataset_filename_to_key(image_filename)
            image_size = tuple(decoded['image'].get_shape().as_list())
            #w,h, channels
            image_size = (image_size[1],image_size[0])
            gt_classes_num = decoded['groundtruth_classes'].numpy().tolist()
            #our specific tag for original full label tag
            gt_label_full_tag = [x.decode('utf-8') for x in decoded['object_categories'].numpy().tolist()]
            gt_classes_text = [x.decode('utf-8') for x in decoded['groundtruth_text'].numpy().tolist()]

            gt_obj_list = []
            if gt_bboxes and not (gt_classes_num or gt_classes_text):
                logging.warning("Neither label id or label_text is set inside TF Record")
            for i,gt_bbox in enumerate(gt_bboxes):
                gt_obj = DetectionEntity(bbox_norm=gt_bbox,
                                          label_id=gt_classes_num[i] if i < len(gt_classes_num) else None, #what if this one messed??
                                          label_text=gt_classes_text[i] if i < len(gt_classes_text) else None,
                                          label_full_tag=gt_label_full_tag[i] if i < len(gt_label_full_tag) else None,
                                          img_size=image_size)
                gt_obj_list.append(gt_obj)
            gts_dict[key] = gt_obj_list
            img_obj = image_from_numpy(img_np=image,file_name=image_filename)
            imgs_dict[key] = img_obj
        return imgs_dict, gts_dict

    @staticmethod
    def parse(tfrecord_src: str) -> DetectionsCollection:
        '''
        Main entry function.
        :param tfrecord_src: Input to TF Record
        :return: Returns DetectionCollection with parsed images and ground truth.
        '''
        imgs_dict, gts_dict = TFRecords.to_dicts(tfrecord_src=tfrecord_src)
        det_collection = DetectionsCollection()



        # then we update it with ground truth
        det_collection.process_images(imgs_dict, update_only=False)

        # we create/update DetectionsCollection using our predictions. label_text not filled, coords are normalized
        det_collection.process_ground_truth(gts_dict, update_only=True)
        return det_collection


class PascalVOC:
    '''
    Format used by LabelImg. One XML file = one image detections.
    '''
    @staticmethod
    def to_detection_entity(input_dict: dict, img_size: Tuple[int,int,int] = None) -> DetectionEntity:
        '''
        Convert dict parsed in PascalVOC format (usually ground truth) to our DetectionEntity (one bbox)
        :param input_dict:
        :return:
        '''
        bbox = input_dict['bndbox']
        bbox = (int(bbox['xmin']), int(bbox['ymin']), int(bbox['xmax']), int(bbox['ymax']))
        score = None
        label_txt = input_dict['name']
        det_obj = DetectionEntity(label_full_tag = label_txt,
                                  bbox_abs=tuple(bbox),
                                  score = score,
                                  img_size=img_size
                                  )
        return det_obj

    @staticmethod
    def from_file(file_src: str,
                  file_parser: Callable[[str],Any] = ft.parse_xml_pascalvoc) -> List[DetectionEntity]:
        '''
        Convert PascalVOC format file to list of DetectionEntity. It can later be inserted into ImageLevelDetections
        :param file_src:
        :param file_parser:
        :return:
        '''
        raw_list = file_parser(file_src)['annotation']
        all_detections = []
        img_size = (int(raw_list['size']['width']),int(raw_list['size']['height']),int(raw_list['size']['depth']))
        for detection_xml_element in raw_list['object']:
            det_obj = PascalVOC.to_detection_entity(input_dict=detection_xml_element, img_size=img_size)
            all_detections.append(det_obj)
        return all_detections

    @staticmethod
    def from_dir(dir_src: str) -> dict:
        '''
        Parse dir with JSON detections from our prod and return dict with img_name => List of DetectionEntity
        :param dir_src:
        :return: Dictionary of key: name without ext, value: list of DetectionEntity
        '''
        if not os.path.isdir(dir_src):
            raise Exception("Provided argument dir_src should be an existing directory")
        det_files = ft.get_file_list_by_ext(dir=dir_src, ext=('xml',))
        result_dict = {}
        for det_file in det_files:
            dets = PascalVOC.from_file(file_src=det_file)
            det_key = ft.dataset_filename_to_key(det_file)
            result_dict[det_key] = dets
        return result_dict

    @staticmethod
    def parse(img_dir: str, predictions_dir: str) -> DetectionsCollection:
        '''
        Main entry point.
        :param img_dir: Directory with images
        :param predictions_dir: Directory with corresponding XML files with annotations
        :return: An object with filled imgs and ground truth
        '''
        det_collection = DetectionsCollection()
        gts = PascalVOC.from_dir(predictions_dir)
        #we create/update DetectionsCollection using our predictions
        det_collection.process_ground_truth(gts, update_only=False)
        imgs = imgs_read_from_dir(img_dir=img_dir)
        #for images we just match existing detections, don't create new objects if corresponding detection doesn't exist
        det_collection.process_images(imgs, update_only=True)
        return det_collection


class MSCOCO:
    pass



