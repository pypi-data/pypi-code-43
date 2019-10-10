from syncvtools.examples.vis_prod_detections import *
from syncvtools.examples.converters import *

if __name__ ==  "__main__":
    # visualize_prod_detections(img_dir='resources/prod_predictions/imgs',
    #                           pred_dir='resources/prod_predictions/annotations')

    # visualize_tf_validation(tf_inference_json='/Users/apatsekin/projects/benchmarks/20190719_sdmv_ammo_gunparts_kix_change_dataaug/detections_and_losses.json',
    #                        tf_record='/Users/apatsekin/projects/datasets/synapse/20190717_sdmv_ammo_gunparts_kix/val.record',
    #                         label_map='/Users/apatsekin/projects/datasets/synapse/20190717_sdmv_ammo_gunparts_kix/label_map.pbtxt')

    # tfrecord_shrink(input_tfrecord='resources/tfrecord/example.tfrecord',
    #                 output_tfrecord='resources/tfrecord/example3.tfrecord',
    #                 slice=slice(0,3))
    # visualize_pascalvoc(img_dir='resources/pascalvoc/imgs',
    #                    pred_dir='resources/pascalvoc/annotations')
    pascalvoc_to_tfrecord(img_dir='resources/pascalvoc/imgs',
                          pascal_voc_dir='resources/pascalvoc/annotations',
                          label_map='resources/pascalvoc/label_map.ptxt',
                          output_tfrecord='resources/tfrecord/example.tfrecord')
    visualize_tfrecord_gt(tf_record='/Users/apatsekin/projects/cv-tools/syncvtools/examples/resources/tfrecord/example.tfrecord')