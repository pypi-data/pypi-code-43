from .contours import Contours
from .masks import Masks
from .texture import texture_features
from .color import Color
import cv2

Features_mask = {'Solidity': Masks.solidity, 'CH Perimeter': Masks.convex_hull_perimeter,
                 'CH Area': Masks.convex_hull_area, 'BB Area': Masks.bounding_box_area,
                 'Rectangularity': Masks.rectangularity, 'Min r': Masks.min_r, 'Max r': Masks.max_r,
                 'Feret': Masks.feret, 'Breadth': Masks.breadth,
                 'Circularity': Masks.circularity, 'Roundness': Masks.roundness,
                 'Feret Angle': Masks.feret_angle,
                 'Eccentricity': Masks.eccentricity,
                 'Center': Masks.center, 'Sphericity': Masks.sphericity,
                 'Aspect Ratio': Masks.aspect_ratio,
                 'Area equivalent': Masks.area_equivalent_diameter,
                 'Perimeter equivalent': Masks.perimeter_equivalent_diameter,
                 'Equivalent elipse area': Masks.equivalent_ellipse_area,
                 'Compactness': Masks.compactness, 'Area': Masks.area, 'Convexity': Masks.convexity,
                 'Shape': Masks.shape, 'Perimeter': Masks.perimeter,
                 }

Color_features = {"lab": (Color.mean_sdv_lab, cv2.COLOR_BGR2LAB),
                  "rgb": (Color.mean_sdv_rgb, cv2.COLOR_BGR2RGB),
                  "hsv": (Color.mean_sdv_hsv, cv2.COLOR_BGR2HSV)}