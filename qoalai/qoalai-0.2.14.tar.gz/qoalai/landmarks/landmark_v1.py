import json
import cv2
import random
import numpy as np
import tensorflow as tf
import qoalai.networks.densenet as densenet
from simple_tensor.tensor_operations import *
from comdutils.file_utils import *
slim = tf.contrib.slim



class Landmark(object):
    def __init__(self,
                 num_landmark_point,
                 input_height = 400,
                 input_width = 400, 
                 input_channel = 3):

        """Constructor
        
        Arguments:
            classes {list of string} -- the image classes list

        Keyword Arguments:
            input_height {int} -- the height of input image (default: {512})
            input_width {int} -- the width of input image (default: {512})
            input_channel {int} -- the channel of input image (default: {3})
        """
        self.num_landmark_point = num_landmark_point
        self.input_height = input_height
        self.input_width = input_width
        self.input_channel = input_channel

        self.input_placeholder = tf.placeholder(tf.float32, shape=(None, self.input_height, self.input_width, self.input_channel))
        self.output_placeholder = tf.placeholder(tf.float32, shape=(None, 1, self.num_landmark_point, 2))

    
    def build_densenet_base(self, input_tensor,
                            dropout_rate,
                            is_training,
                            top_layer_depth):
        """[summary]
        
        Arguments:
            input_tensordropout_rate {[type]} -- [description]
            is_training {bool} -- [description]
        """
        arg_scoope = densenet.densenet_arg_scope()
        out = None

        with slim.arg_scope(arg_scoope):
            out = densenet.densenet121(inputs=input_tensor, 
                                       num_classes=1, 
                                       is_training=is_training)
            base_var_list = tf.get_collection(tf.GraphKeys.GLOBAL_VARIABLES)


        h = out.get_shape().as_list()[1]
        w = out.get_shape().as_list()[2]
        print ('-------------INFO-------------------')
        print ('INFO the height of the basenet output ' + str(h))
        print ('INFO the width of the basenet output ' + str(w))
        print ('------------------------------------')

        if w < self.num_landmark_point:
            print ('-------------WARNING---------------')
            print ('WARNING the number of your landmark point is to many')
            print ('WARNING the maximum number is: ' + str(w))
            print ('-----------------------------------')

        while(True):
            if w == self.num_landmark_point:
                break

            out = new_conv2d_layer(out, 
                                    filter_shape=[2, 2, out.get_shape().as_list()[-1], top_layer_depth], 
                                    name='cv1', 
                                    dropout_val=0.85, 
                                    activation = 'LRELU', 
                                    lrelu_alpha=0.2,
                                    padding='VALID', 
                                    strides=[1, 1, 1, 1],
                                    data_type=tf.float32,  
                                    is_training=is_training,
                                    use_bias=True,
                                    use_batchnorm=True) 
            w = out.get_shape().as_list()[2]

        while(True):
            if h == 1:
                break
            
            out = new_conv2d_layer(out, 
                                    filter_shape=[2, 2, out.get_shape().as_list()[-1], top_layer_depth], 
                                    name='cv1', 
                                    dropout_val=0.85, 
                                    activation = 'LRELU', 
                                    lrelu_alpha=0.2,
                                    padding='SAME', 
                                    strides=[1, 2, 1, 1],
                                    data_type=tf.float32,  
                                    is_training=is_training,
                                    use_bias=True,
                                    use_batchnorm=True) 
            h = out.get_shape().as_list()[1]

        out = new_conv2d_layer(out, 
                                    filter_shape=[1, 1, out.get_shape().as_list()[-1], 2], 
                                    name='cv1', 
                                    dropout_val=0.85, 
                                    activation = 'LRELU', 
                                    lrelu_alpha=0.2,
                                    padding='SAME', 
                                    strides=[1, 1, 1, 1],
                                    data_type=tf.float32,  
                                    is_training=is_training,
                                    use_bias=False,
                                    use_batchnorm=False) 
        out = tf.nn.sigmoid(out)
        print ('--------------INFO-----------------')
        print ('The shape of the detector is: (None,' + str(h) +' ' + str(w) + ' 2)')
        print ('-----------------------------------')
        return out


    def read_target(self, file_path):
        tmp = np.zeros((1, self.num_landmark_point,  2))

        #----------------------------------------------------------------#
        # this part is reading the label in a .txt file for a single image #
        #----------------------------------------------------------------#
        file = open(file_path, "r") 
        data = file.read()
        data = data.split()
        length = len(data)
        
        if length != 2 * self.num_landmark_point:
            print ("-------------------WARNING-------------------")
            print ("WRONG label format")
            print ("the label format is x1, y1, x2, y2, ..., xn, yn")
            print ("the value of x and y are relative to image width and height")
            print ("each image has single .txt file as label with the name")
            print ("---------------------------------------------")

        for i in range(self.num_landmark_point):
            tmp[0, i, 0] = float(data[i*2])
            tmp[0, i, 1] = float(data[i*2 + 1])

        return tmp


    def batch_generator(self, batch_size, dataset_path, message):
        """Train Generator
        
        Arguments:
            batch_size {integer} -- the size of the batch
            image_name_list {list of string} -- the list of image name
        """
        label_folder_path = dataset_path + "labels/"
        dataset_folder_path = dataset_path + "images/"
        dataset_file_list = get_filenames(dataset_folder_path)
        random.shuffle(dataset_file_list)
        
        print ("------------------------INFO-------------------")
        print ("Image Folder: " + dataset_folder_path)
        print ("Number of Image: " + str(len(dataset_file_list)))
        print ("-----------------------------------------------")

        # Infinite loop.
        idx = 0
        while True:
            x_batch = []
            y_pred = []

            for i in range(batch_size):
                if idx >= len(dataset_file_list):
                    random.shuffle(dataset_file_list)
                    print ("==>>> INFO: your " + message +" dataset is reshuffled again: ", idx)
                    idx = 0
                try:
                    tmp_x = cv2.imread(dataset_folder_path + dataset_file_list[idx])
                    tmp_x = cv2.cvtColor(tmp_x, cv2.COLOR_BGR2RGB)
                    tmp_x = cv2.resize(tmp_x, (self.input_width, self.input_height))
                    tmp_x = tmp_x.astype(np.float32) / 255.
                    tmp_y = self.read_target(label_folder_path + dataset_file_list[idx].split('.')[0] + ".txt")
                    x_batch.append(tmp_x)
                    y_pred.append(tmp_y)
                except Exception as e:
                    print ("---------------------------------------------------------------")
                    print ("WARNING: the " + str(e))
                    print ("---------------------------------------------------------------")

                idx += 1
            yield (np.array(x_batch), np.array(y_pred))


    def optimize(self, 
                 iteration, 
                 subdivition,
                 cost_tensor,
                 optimizer_tensor,
                 out_tensor, 
                 session,
                 saver, 
                 train_generator,
                 val_generator,
                 best_loss,
                 path_tosave_model='model/model1'):
        """[summary]
        
        Arguments:
            iteration {[type]} -- [description]
            subdivition {[type]} -- [description]
            cost_tensor {[type]} -- [description]
            optimizer_tensor {[type]} -- [description]
            out_tensor {[type]} -- [description]
        
        Keyword Arguments:
            train_batch_size {int} -- [description] (default: {32})
            val_batch_size {int} -- [description] (default: {50})
            path_tosave_model {str} -- [description] (default: {'model/model1'})
        """

        self.train_loss = []
        self.val_loss = []
        best_loss = best_loss
        
        for i in range(iteration):
            sign = "-"
            t_losses = []

            for j in range(subdivition):
                x_train, y_train = next(train_generator)
                feed_dict = {}
                feed_dict[self.input_placeholder] = x_train
                feed_dict[self.output_placeholder] = y_train
                session.run(optimizer_tensor, feed_dict)
                loss = session.run(cost_tensor, feed_dict)
                t_losses.append(loss)
                print ("> Train sub", j, 'loss : ', loss)
                
            x_val, y_val = next(val_generator)
            feed_dict = {}
            feed_dict[self.input_placeholder] = x_val
            feed_dict[self.output_placeholder] = y_val
            loss = session.run(cost_tensor, feed_dict)
            
            t_loss = sum(t_losses) / (len(t_losses) + 0.0001)
            self.train_loss.append(t_loss)
            self.val_loss.append(loss)
                
            if best_loss > loss:
                best_loss = loss
                sign = "************* model saved"
                saver.save(session, path_tosave_model)
        
            print (">> epoch: ", i, "train loss: ", round(t_loss, 3), "val loss: ", round(loss, 3), sign)    