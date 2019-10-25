import os
import sys
import numpy as np
import skimage
import argparse
import onnxruntime

import fine_grained_segmentation.model as model
import fine_grained_segmentation.visualize as visualize

# list of fashion class names
CLASS_NAMES = ['BG', 'shirt, blouse', 'top, t-shirt, sweatshirt', 'sweater', 
                'cardigan', 'jacket', 'vest', 'pants', 'shorts', 'skirt', 'coat', 
                'dress', 'jumpsuit', 'cape', 'glasses', 'hat', 
                'headband, head covering, hair accessory', 'tie', 'glove', 'watch', 
                'belt', 'leg warmer', 'tights, stockings', 'sock', 'shoe', 
                'bag, wallet', 'scarf', 'umbrella', 'hood', 'collar', 'lapel', 
                'epaulette', 'sleeve', 'pocket', 'neckline', 'buckle', 'zipper', 
                'applique', 'bead', 'bow', 'flower', 'fringe', 'ribbon', 'rivet', 
                'ruffle', 'sequin', 'tassel']

FILE_DIR = os.path.dirname(os.path.realpath(__file__))


def generate_image(images, molded_images, windows, results):
    results_final = []
    for i, image in enumerate(images):
        final_rois, final_class_ids, final_scores, final_masks = \
            model.unmold_detections(results[0][i], results[3][i], # detections[i], mrcnn_mask[i]
                                   image.shape, molded_images[i].shape,
                                   windows[i])
        results_final.append({
            "rois": final_rois,
            "class_ids": final_class_ids,
            "scores": final_scores,
            "masks": final_masks,
        })
        r = results_final[i]
        visualize.display_instances(image, r['rois'], r['masks'], r['class_ids'],
                                    CLASS_NAMES, r['scores'])
    return results_final


def detect(filename):
    BATCH_SIZE = 1
    
    model_file_name = os.path.join(FILE_DIR, 'mrcnn.onnx')
    session = onnxruntime.InferenceSession(model_file_name)

    # get image
    image = skimage.io.imread(filename)
    images = [image]
    
    # preprocessing
    molded_images, image_metas, windows = model.mold_inputs(images)
    anchors = model.get_anchors(molded_images[0].shape)
    anchors = np.broadcast_to(anchors, (BATCH_SIZE,) + anchors.shape)

    results = \
        session.run(None, {"input_image": molded_images.astype(np.float32),
                        "input_anchors": anchors,
                        "input_image_meta": image_metas.astype(np.float32)})

    # postprocessing
    results_final = generate_image(images, molded_images, windows, results)
