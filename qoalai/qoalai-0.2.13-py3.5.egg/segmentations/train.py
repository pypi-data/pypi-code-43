from qoalai.segmentations import deeplab_inceptionresnetv2 as dl
import tensorflow as tf


# --- for initial training
segmentation = dl.DeepLab(num_classes=1, is_training=True)

# ---------------------------------- #
# tensorflow saver                   #
# ---------------------------------- #
segmentation.saver_all = tf.train.Saver()
segmentation.session = tf.Session()
segmentation.session.run(tf.global_variables_initializer())
# load model if any
#segmentation.saver_all.restore(segmentation.session, save_path='/home/model/melon_segmentation/v0')
train_generator = segmentation.batch_generator(batch_size=1, 
                                               dataset_path='/home/dataset/part_segmentation/', message="TRAIN")
val_generator = segmentation.batch_generator(batch_size=1, 
                                             dataset_path='/home/dataset/part_segmentation/', message="VAL")
segmentation.check_val_data(train_generator)

# train
# train
segmentation.optimize(subdivisions = 10, 
                      iterations = 10000, 
                      best_loss= 1000, 
                      train_batch=train_generator, 
                      val_batch=val_generator, 
                      save_path='/home/model/melon_segmentation/v0')
