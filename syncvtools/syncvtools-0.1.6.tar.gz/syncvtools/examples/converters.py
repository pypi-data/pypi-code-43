from syncvtools.utils.draw_detections import DrawDetections
from syncvtools.utils.parsers import TFRecords, TFObjDetAPIDetections, PascalVOC
from syncvtools.utils.converters import TFRecordsExport
import itertools, cv2

def tfrecord_shrink(input_tfrecord: str, output_tfrecord: str, slice: slice = slice(0,3) ):
    '''
        Shrink a tfrecord using Python's standard slicing method
    :param input_tfrecord: path to input TF record
    :param output_tfrecord: path where to save output TF record
    :return:
    '''
    tf_gts = TFRecords.parse(tfrecord_src=input_tfrecord)
    tf_gts = tf_gts[slice]
    TFRecordsExport.convert(src = tf_gts, out_path=output_tfrecord)


def pascalvoc_to_tfrecord(img_dir, pascal_voc_dir, output_tfrecord, label_map, slice: slice = None):
    '''

    :param img_dir: Directory with input images
    :param pascal_voc_dir: Directory with XML annotations (one file corresponds to one image)
    :param output_tfrecord: Path to output TF Record
    :param label_map: Path to label_map in TF format.
    :param slice: Slice in Python's format: slice(0,3)
    :return:
    '''
    pascal_gts = PascalVOC.parse(img_dir=img_dir, predictions_dir=pascal_voc_dir)
    if slice:
        pascal_gts = pascal_gts[slice]
    # to convert to TensorFlow we need to apply label_map, since label_id is required for TF-Record
    pascal_gts.process_labelmap(label_dict = label_map)
    TFRecordsExport.convert(src=pascal_gts, out_path=output_tfrecord)