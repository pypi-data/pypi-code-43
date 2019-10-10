from typing import Tuple, Any, Union, List, Dict, Callable
from syncvtools.data.image import ImgSize, Image
from syncvtools.data.bbox import Bbox
#from syncvtools.utils.bbox import normalize_bbox
import syncvtools.utils.file_tools as ft
import syncvtools.data.annotated_tag as annotated_tag
import logging

class DetectionEntity:
    def __init__(self,
                 label_text: str = None,
                 bbox_abs: Tuple[int, int, int, int] = None,
                 bbox_norm: Tuple[float, float, float, float] = None,
                 score: float = None,
                 mask: Tuple[Union[float, int]] = None,
                 label_id: int = None,
                 label_full_tag = None,
                 img_size: Tuple[int, int] = None
                 ):

        # if label_text is None or len(label_text) == 0:
        #     raise ValueError("label_text param is None or zero length")
        #that's what goes to model as label_map text. SOmething like "sharp" or "gun"
        #that's what we store in image/object/category field -- original full tag of the detection. "sharp-c2"
        self.label_full_tag = label_full_tag
        #TODO TEST IF THE TAG IS CONVERTABLE TO CLASS NAME
        if label_text:
            self.label_text = label_text
        else:
            if label_full_tag:
                try:
                    self.label_text = annotated_tag.AnnotatedTag.load_from_raw_tag_name(label_full_tag).class_name
                except annotated_tag.InvalidTagNameException:
                    logging.warning("Wasn't able to parse a full tag: {}. Copying full_tag to label_text as is".format(label_full_tag))
                    self.label_text = self.label_full_tag



        if img_size is not None:
            if len(img_size) not in (2,3):
                raise ValueError("Image size should be a tuple of size 2 or 3")
            self._img_size = ImgSize(width=img_size[0], height=img_size[1])
        else:
            self._img_size = None

        #setting bounding box coordinates either from absolute values or from normalized
        self.bbox = Bbox(bbox_norm=bbox_norm, bbox_abs=bbox_abs, img_size=self._img_size)

        if score is not None:
            if score < 0.0 or score > 1.0:
                raise ValueError("Score (confidence) should be [0;1] range")
            self.score = score

        self.label_id = label_id

    def set_img_size(self, img_size: ImgSize):
        if img_size is None:
            raise Exception("None image size provided")
        self._img_size = img_size
        self.bbox.set_img_size(img_size=self._img_size)
        return self

    @property
    def img_size(self):
        return self._img_size

    @img_size.setter
    def img_size(self, v: ImgSize):
        self.set_img_size(v)



class ImageLevelDetections:
    def __init__(self,
                 img: Image = None,
                 detections: List[DetectionEntity] = None,
                 ground_truth: List[DetectionEntity] = None):
        self._img = None
        self._detections = None
        self._ground_truth = None
        self.img = img
        self.detections = detections
        self.ground_truth = ground_truth

        self.detection_entities = ['img', 'detections', 'ground_truth']
        #TODO add AP and other metrics


    # @detections.setter
    # def detections(self, dets: List[DetectionEntity]):
    #     #when detections are added, check if img size is not set there, and try to link it to images (if they added already)
    #     if self.img is not None:
    #         for det in dets:
    #             if det.img_size is None:
    #                 det.img_size = self.img.img_size
    #     self._detections = dets

    @property
    def img(self):
        return self._img

    @img.setter
    def img(self, im):
        #when img is added, check if detections are already present, update their size if needed
        if im is not None:
            if self.detections is not None:
                for det in self.detections:
                    if det.img_size is None:
                        det.img_size = im.img_size
            if self.ground_truth is not None:
                for gt in self.ground_truth:
                    if gt.img_size is None:
                        gt.img_size = im.img_size
        self._img = im

    @property
    def detections(self):
        return self._detections

    @detections.setter
    def detections(self, dets: List[DetectionEntity]):
        #when detections are added, check if img size is not set there, and try to link it to images (if they added already)
        if dets is not None:
            if self.img is not None:
                for det in dets:
                    if det.img_size is None:
                        det.img_size = self.img.img_size
        self._detections = dets

    @property
    def ground_truth(self):
        return self._ground_truth

    @ground_truth.setter
    def ground_truth(self, gts: List[DetectionEntity]):
        #when gts are added, check if img size is not set there, and try to link it to images (if they added already)
        if gts is not None:
            if self.img is not None:
                for gt in gts:
                    if gt.img_size is None:
                        gt.img_size = self.img.img_size
        self._ground_truth = gts

class DetectionsCollection(dict):
    '''
    Consists of key=>value storage for ImageLevelDetections (or ScanLevelDetections in future)
    Provides options to create/update images, ground_truths, detections.
    '''
    def process_images(self, img_dict: Dict[str, Image], update_only: bool = False):
        for img_key in img_dict:
            if img_key in self:
                self[img_key].img = img_dict[img_key]
            else:
                if update_only: #don't need to create new dict elements
                    continue
                self[img_key] = ImageLevelDetections(img=img_dict[img_key])


    def process_detections(self,det_dict:  Dict[str, List[DetectionEntity]], update_only: bool = False):
        for det_key in det_dict:
            if det_key in self:
                self[det_key].detections = det_dict[det_key]
            else:
                if update_only:  # don't need to create new dict elements
                    continue
                self[det_key] = ImageLevelDetections(detections=det_dict[det_key])

    def process_ground_truth(self, gt_dict:  Dict[str, List[DetectionEntity]], update_only: bool = False):
        for gt_key in gt_dict:
            if gt_key in self:
                self[gt_key].ground_truth = gt_dict[gt_key]
            else:
                if update_only:  # don't need to create new dict elements
                    continue
                self[gt_key] = ImageLevelDetections(ground_truth=gt_dict[gt_key])

    def process_labelmap(self, label_dict: Any, input_parser: Callable[[str],Any] = ft.pbmap_read_to_dict):
        label_dict = input_parser(label_dict)
        inverse_label_dict = {v: k for k, v in label_dict.items()}
        for key in self:
            if self[key].detections is not None:
                for det in self[key].detections:
                    if det.label_text is None and det.label_id is not None:
                        if det.label_id in label_dict:
                            det.label_text = label_dict[det.label_id]
                        else:
                            logging.warning("label_dict ({}) doesn't have corresponding label_id found in detections: {}".format(label_dict.keys(), det.label_id))
                    elif det.label_id is None and det.label_text is not None:
                        if det.label_text in inverse_label_dict:
                            det.label_id = inverse_label_dict[det.label_text]
                        else:
                            logging.warning("label_dict ({}) doesn't have corresponding label_text found in detections: {}".format(label_dict.keys(), det.label_text))

        for key in self:
            if self[key].ground_truth is not None:
                for gt in self[key].ground_truth:
                    if gt.label_text is None and gt.label_id is not None:
                        if gt.label_id in label_dict:
                            gt.label_text = label_dict[gt.label_id]
                        else:
                            logging.warning("label_dict ({}) doesn't have corresponding label_id found in detections: {}".format(label_dict.keys(), gt.label_id))
                    elif gt.label_id is None and gt.label_text is not None:
                        if gt.label_text in inverse_label_dict:
                            gt.label_id = inverse_label_dict[gt.label_text]
                        else:
                            logging.warning("label_dict ({}) doesn't have corresponding label_text found in detections: {}".format(label_dict.keys(), gt.label_text))



    def __add__(self, other):
        for key in self:
            if key in other:
                for attr in self[key].detection_entities:
                    if getattr(self[key],attr) is None and getattr(other[key],attr) is not None:
                        setattr(self[key], attr, getattr(other[key],attr))
        return self

    def __getitem__(self, key):
        if not isinstance(key, slice):
            return super().__getitem__(key)
        slicedkeys = list(self.keys())[key]
        data = DetectionsCollection()
        for key in slicedkeys:
            data[key] = self[key]
        return data