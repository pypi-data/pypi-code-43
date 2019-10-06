# Based on https://github.com/luuuyi/RefineDet.PyTorch/blob/master/models/
#          refinedet.py

import os
import sys
import pickle
import numpy as np

if sys.version_info[0] == 2:
    import xml.etree.cElementTree as ET
else:
    import xml.etree.ElementTree as ET


VOC_CLASSES = (
    "aeroplane",
    "bicycle",
    "bird",
    "boat",
    "bottle",
    "bus",
    "car",
    "cat",
    "chair",
    "cow",
    "diningtable",
    "dog",
    "horse",
    "motorbike",
    "person",
    "pottedplant",
    "sheep",
    "sofa",
    "train",
    "tvmonitor",
)


def get_voc_results_file_template(data_root, dataset_year, image_set, cls):
    # VOCdevkit/VOC2007/results/det_test_aeroplane.txt
    filename = "det_" + image_set + "_%s.txt" % (cls)
    filedir = os.path.join(
        data_root, "VOCdevkit", "VOC", str(dataset_year), "results"
    )
    if not os.path.exists(filedir):
        os.makedirs(filedir)
    path = os.path.join(filedir, filename)
    return path


def parse_rec(filename):
    """Parse a PASCAL VOC xml file."""
    tree = ET.parse(filename)
    objects = []
    for obj in tree.findall("object"):
        obj_struct = {}
        obj_struct["name"] = obj.find("name").text
        obj_struct["pose"] = obj.find("pose").text
        obj_struct["truncated"] = int(obj.find("truncated").text)
        obj_struct["difficult"] = int(obj.find("difficult").text)
        bbox = obj.find("bndbox")
        obj_struct["bbox"] = [
            int(bbox.find("xmin").text) - 1,
            int(bbox.find("ymin").text) - 1,
            int(bbox.find("xmax").text) - 1,
            int(bbox.find("ymax").text) - 1,
        ]
        objects.append(obj_struct)

    return objects


def voc_ap(rec, prec, use_07_metric=True):
    """Compute VOC AP given precision and recall.

    If use_07_metric is true, uses the VOC 07 11 point method (default:True).
    """
    if use_07_metric:
        # 11 point metric
        ap = 0.0
        for t in np.arange(0.0, 1.1, 0.1):
            if np.sum(rec >= t) == 0:
                p = 0
            else:
                p = np.max(prec[rec >= t])
            ap = ap + p / 11.0
    else:
        # correct AP calculation
        # first append sentinel values at the end
        mrec = np.concatenate(([0.0], rec, [1.0]))
        mpre = np.concatenate(([0.0], prec, [0.0]))

        # compute the precision envelope
        for i in range(mpre.size - 1, 0, -1):
            mpre[i - 1] = np.maximum(mpre[i - 1], mpre[i])

        # to calculate area under PR curve, look for points
        # where X axis (recall) changes value
        i = np.where(mrec[1:] != mrec[:-1])[0]

        # and sum (\Delta recall) * prec
        ap = np.sum((mrec[i + 1] - mrec[i]) * mpre[i + 1])
    return ap


def voc_eval(
    detpath,
    annopath,
    imagesetfile,
    classname,
    cachedir,
    ovthresh=0.5,
    use_07_metric=True,
):
    """Voc evaluation.

    ::

        rec, prec, ap = voc_eval(
            detpath, annopath, imagesetfile, classname, [ovthresh],
            [use_07_metric]
        )

    Top level function that does the PASCAL VOC evaluation.

    Args:
        detpath: Path to detections detpath.format(classname) should produce
            the detection results file.
        annopath: Path to annotations annopath.format(imagename) should be the
            xml annotations file.
        imagesetfile: Text file containing the list of images, one image per
            line.
        classname: Category name (duh).
        cachedir: Directory for caching the annotations.
        ovthresh: Overlap threshold (default = 0.5).
        use_07_metric: Whether to use VOC07's 11 point AP computation.
            (default True).
    """
    # assumes detections are in detpath.format(classname)
    # assumes annotations are in annopath.format(imagename)
    # assumes imagesetfile is a text file with each line an image name
    # cachedir caches the annotations in a pickle file
    # first load gt
    if not os.path.isdir(cachedir):
        os.mkdir(cachedir)
    cachefile = os.path.join(cachedir, "annots.pkl")
    # read list of images
    with open(imagesetfile, "r") as f:
        lines = f.readlines()
    imagenames = [x.strip() for x in lines]
    if not os.path.isfile(cachefile):
        # load annots
        recs = {}
        for i, imagename in enumerate(imagenames):
            recs[imagename] = parse_rec(annopath % (imagename))
            if i % 100 == 0:
                print(
                    "Reading annotation for {:d}/{:d}".format(
                        i + 1, len(imagenames)
                    )
                )
        # save
        print("Saving cached annotations to {:s}".format(cachefile))
        with open(cachefile, "wb") as f:
            pickle.dump(recs, f)
    else:
        # load
        with open(cachefile, "rb") as f:
            recs = pickle.load(f)

    # extract gt objects for this class
    class_recs = {}
    npos = 0
    for imagename in imagenames:
        R = [obj for obj in recs[imagename] if obj["name"] == classname]
        bbox = np.array([x["bbox"] for x in R])
        difficult = np.array([x["difficult"] for x in R]).astype(np.bool)
        det = [False] * len(R)
        npos = npos + sum(~difficult)
        class_recs[imagename] = {
            "bbox": bbox,
            "difficult": difficult,
            "det": det,
        }

    # read dets
    detfile = detpath.format(classname)
    with open(detfile, "r") as f:
        lines = f.readlines()
    if any(lines) == 1:

        splitlines = [x.strip().split(" ") for x in lines]
        image_ids = [x[0] for x in splitlines]
        confidence = np.array([float(x[1]) for x in splitlines])
        BB = np.array([[float(z) for z in x[2:]] for x in splitlines])

        # sort by confidence
        sorted_ind = np.argsort(-confidence)
        BB = BB[sorted_ind, :]
        image_ids = [image_ids[x] for x in sorted_ind]

        # go down dets and mark TPs and FPs
        nd = len(image_ids)
        tp = np.zeros(nd)
        fp = np.zeros(nd)
        for d in range(nd):
            R = class_recs[image_ids[d]]
            bb = BB[d, :].astype(float)
            ovmax = -np.inf
            BBGT = R["bbox"].astype(float)
            if BBGT.size > 0:
                # compute overlaps
                # intersection
                ixmin = np.maximum(BBGT[:, 0], bb[0])
                iymin = np.maximum(BBGT[:, 1], bb[1])
                ixmax = np.minimum(BBGT[:, 2], bb[2])
                iymax = np.minimum(BBGT[:, 3], bb[3])
                iw = np.maximum(ixmax - ixmin, 0.0)
                ih = np.maximum(iymax - iymin, 0.0)
                inters = iw * ih
                uni = (
                    (bb[2] - bb[0]) * (bb[3] - bb[1])
                    + (BBGT[:, 2] - BBGT[:, 0]) * (BBGT[:, 3] - BBGT[:, 1])
                    - inters
                )
                overlaps = inters / uni
                ovmax = np.max(overlaps)
                jmax = np.argmax(overlaps)

            if ovmax > ovthresh:
                if not R["difficult"][jmax]:
                    if not R["det"][jmax]:
                        tp[d] = 1.0
                        R["det"][jmax] = 1
                    else:
                        fp[d] = 1.0
            else:
                fp[d] = 1.0

        # compute precision recall
        fp = np.cumsum(fp)
        tp = np.cumsum(tp)
        rec = tp / float(npos)
        # avoid divide by zero in case the first detection matches a difficult
        # ground truth
        prec = tp / np.maximum(tp + fp, np.finfo(np.float64).eps)
        ap = voc_ap(rec, prec, use_07_metric)
    else:
        rec = -1.0
        prec = -1.0
        ap = -1.0

    return rec, prec, ap


def write_voc_results_file(
    all_boxes, data_loader, data_root, dataset_year, labelmap
):
    for cls_ind, cls in enumerate(labelmap):
        print("Writing {:s} VOC results file".format(cls))
        filename = get_voc_results_file_template(
            data_root, dataset_year, "val", cls
        )
        with open(filename, "wt") as f:
            for im_ind, file_name in enumerate(data_loader.dataset.images):
                index = file_name.split("/")[-1].strip(".jpg")
                dets = all_boxes[cls_ind + 1][im_ind]
                if dets == []:
                    continue
                # the VOCdevkit expects 1-based indices
                for k in range(dets.shape[0]):
                    f.write(
                        "{:s} {:.3f} {:.1f} {:.1f} {:.1f} {:.1f}\n".format(
                            index,
                            dets[k, -1],
                            dets[k, 0] + 1,
                            dets[k, 1] + 1,
                            dets[k, 2] + 1,
                            dets[k, 3] + 1,
                        )
                    )
