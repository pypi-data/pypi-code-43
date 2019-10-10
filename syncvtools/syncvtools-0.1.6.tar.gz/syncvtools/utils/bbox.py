from typing import Tuple
from syncvtools.data.image import ImgSize


def normalize_bbox(bbox: Tuple[int,int,int,int], img_size: Tuple[int,int]) -> Tuple[float,float,float,float]:
    if bbox is None or len(bbox) < 4 or len(bbox) > 5:
        raise ValueError("Bbox is either None or not a tuple of size 4,5: (xmin, ymin, xmax, ymax)")

    img_size = ImgSize(width = img_size[0], height= img_size[1])
    norm_coords = (float(bbox[0] / img_size.width), float(bbox[1] / img_size.height), float(bbox[2] / img_size.width), float(bbox[3] / img_size.height))
    for coord in norm_coords:
        if coord < 0 or coord > 1:
            raise ValueError("Norm coordinates should be [0;1]: {}".format(bbox[:4]))
    return norm_coords


def denormalize_bbox(bbox: Tuple[float,float,float,float], img_size: Tuple[int,int]) -> Tuple[int,int,int,int]:
    def cl(v, mn, mx):
        return max(min(v,mx),mn)
    #just to validate width/height
    img_size = ImgSize(width=img_size[0], height=img_size[1])
    validate_norm_coords(bbox=bbox)
    abs_coords = bbox[0] * img_size.width, bbox[1] * img_size.height, bbox[2] * img_size.width, bbox[3] * img_size.height
    abs_coords = list(map(int,map(round, abs_coords)))
    abs_coords = (cl(abs_coords[0],0,img_size.width-1),
                 cl(abs_coords[1],0,img_size.height-1),
                 cl(abs_coords[2],0,img_size.width-1),
                 cl(abs_coords[3],0,img_size.height-1))
    return abs_coords


def validate_norm_coords(bbox: Tuple[float,float,float,float]):
    if bbox is None or len(bbox) != 4:
        raise ValueError("Bbox should take a tuple of float (x1,y1,x2,y2)")
    for coord in bbox[:4]:
        if coord < 0 or coord > 1:
            raise ValueError("Norm coordinates should be [0;1]: {}".format(bbox[:4]))


