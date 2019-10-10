from typing import Tuple
import json
from syncvtools.utils.bbox import normalize_bbox, validate_norm_coords, denormalize_bbox
from syncvtools.data.image import ImgSize

class Bbox:
    def __init__(self,
                 bbox_norm: Tuple[float,float,float,float] = None,
                 bbox_abs: Tuple[int,int,int,int] = None,
                 img_size: ImgSize = None):
        if bbox_norm is None and bbox_abs is None:
            #bbox_norm = normalize_bbox(bbox = bbox_abs, img_size = img_size)
            raise ValueError("Either bbox_norm or bbox_abs should be set")

        self._bbox_norm = None
        #self.bbox_abs = None
        if bbox_norm is not None:
            validate_norm_coords(bbox_norm)
            self._bbox_norm =  bbox_norm
        self._bbox_abs = bbox_abs

        #self.xmin, self.ymin, self.xmax, self.ymax = bbox_norm[:4]
        if img_size is not None:
            self._img_size = img_size
        else:
            self._img_size = None



    @property
    def bbox_abs(self):
        if self._bbox_abs is not None:
            return self._bbox_abs
        if self._img_size is None:
            #raise Exception("Cannot infer abs box size! Call bbox.set_img_size((w,h)).bbox_abs to set img size first.")
            return None
        if self._bbox_norm is None:
            raise Exception("Something went wrong. Box has neither abs nor normalized coordinates!")
        self._bbox_abs = denormalize_bbox(bbox=self._bbox_norm, img_size=self._img_size.as_tuple())
        return self._bbox_abs

    @bbox_abs.setter
    def bbox_abs(self, value):
        raise Exception("Not implemented")

    @property
    def bbox_norm(self):
        if self._bbox_norm is not None:
            return self._bbox_norm
        if self._img_size is None:
            #raise Exception("Cannot infer norm box size! Call bbox.set_img_size((w,h)).bbox_norm to set img size first.")
            return None
        if self._bbox_abs is None:
            raise Exception("Something went wrong. Box has neither abs nor normalized coordinates!")
        self._bbox_norm = normalize_bbox(bbox=self._bbox_abs, img_size=self._img_size.as_tuple())
        return self._bbox_norm

    @bbox_norm.setter
    def bbox_norm(self, value):
        raise Exception("Not implemented")

    #instead of property for chaining
    def set_img_size(self,img_size: ImgSize):
        self._img_size = img_size
        return self





    def __str__(self):
        return json.dumps({'bbox_abs': self._bbox_abs, 'bbox_norm': self._bbox_norm, 'img_size': self._img_size.as_tuple() if self._img_size is not None else "None"})
