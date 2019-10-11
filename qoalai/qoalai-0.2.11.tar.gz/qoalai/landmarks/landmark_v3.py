import json
import cv2
import math
import random
import numpy as np
import tensorflow as tf
import qoalai.networks.densenet as densenet
from simple_tensor.tensor_operations import *
from simple_tensor.tensor_metrics import calculate_acc
from simple_tensor.tensor_losses import mse_loss_mean, sigmoid_crossentropy_mean
from comdutils.file_utils import *
slim = tf.contrib.slim



class Landmark(object):
    def __init__(self,
                 num_landmark_point,
                 input_height = 300,
                 input_width = 300, 
                 input_channel = 3,
                 grid_num = 3,
                 threshold = 0.5):

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
        self.grid_num = grid_num
        self.grid_size_relative = 1./self.grid_num
        self.threshold = threshold

        self.input_placeholder = tf.placeholder(tf.float32, shape=(None, self.input_height, self.input_width, self.input_channel))
        self.point_position_placeholder = tf.placeholder(tf.float32, shape=(None, 1, self.num_landmark_point, 2))
        self.point_map_placeholder = tf.placeholder(tf.float32, shape=(None, self.grid_num, self.grid_num, num_landmark_point))

    
    def build_densenet_base(self, input_tensor,
                            dropout_rate,
                            is_training,
                            top_layer_depth):
        """[summary]
        
        Arguments:
            input_tensordropout_rate {[type]} -- [description]
            is_training {bool} -- [description]
        """
        # ----------------------------------- #
        # building the densenet base network  #
        # ----------------------------------- #
        arg_scoope = densenet.densenet_arg_scope()
        out = None

        with slim.arg_scope(arg_scoope):
            out = densenet.densenet121(inputs=input_tensor, 
                                       num_classes=1, 
                                       is_training=is_training)
            base_var_list = tf.get_collection(tf.GraphKeys.GLOBAL_VARIABLES)

        out = new_conv2d_layer(input=out, 
                               filter_shape=[2, 2, out.get_shape().as_list()[-1], top_layer_depth], 
                               dropout_val=1.-dropout_rate, 
                               activation = 'NONE', 
                               padding='SAME', 
                               strides=[1, 2, 2, 1],
                               is_training=is_training,
                               use_bias=False,
                               use_batchnorm=False) 
        
        # ----------------------------------- #
        # preparing the point hetamap         #
        # ----------------------------------- #
        self.point_map_nonlogit = new_conv2d_layer(input=out, 
                               filter_shape=[2, 2, out.get_shape().as_list()[-1], self.num_landmark_point], 
                               dropout_val=1-dropout_rate, 
                               activation = 'NONE', 
                               padding='SAME', 
                               strides=[1, 1, 1, 1],
                               is_training=is_training,
                               use_bias=False,
                               use_batchnorm=False)
        first_map = self.point_map_nonlogit[:, :, :, 0]
        second_map = self.point_map_nonlogit[:, :, :, 1]
        third_map = self.point_map_nonlogit[:, :, :, 2]
        fourth_map = self.point_map_nonlogit[:, :, :, 3]
        
        first_map = tf.nn.softmax(tf.keras.layers.Flatten()(first_map))
        second_map = tf.nn.softmax(tf.keras.layers.Flatten()(second_map))
        third_map = tf.nn.softmax(tf.keras.layers.Flatten()(third_map))
        fourth_map = tf.nn.softmax(tf.keras.layers.Flatten()(fourth_map))

        first_map = tf.reshape(first_map, [tf.shape(first_map)[0], self.grid_num, self.grid_num, 1])
        second_map = tf.reshape(second_map, [tf.shape(second_map)[0], self.grid_num, self.grid_num, 1])
        third_map = tf.reshape(third_map, [tf.shape(third_map)[0], self.grid_num, self.grid_num, 1])
        fourth_map = tf.reshape(fourth_map, [tf.shape(fourth_map)[0], self.grid_num, self.grid_num, 1])

        self.point_map = tf.concat([first_map, second_map, third_map, fourth_map], axis=-1)
        
        # ----------------------------------- #
        # preparing the x center predictor    #
        # preparing the y center predictor    #
        # the value is relative to the grid size
        # ----------------------------------- #
        out = tf.keras.layers.Flatten()(out)
        out_x = new_fc_layer(out, 
                             num_inputs=int(out.get_shape().as_list()[-1]), 
                             num_outputs=1000,
                             dropout_val=1.-dropout_rate, 
                             activation="NONE",
                             is_training=is_training,
                             use_bias=False)
        out_x = new_fc_layer(out_x, 
                             num_inputs=int(out_x.get_shape().as_list()[-1]), 
                             num_outputs=self.num_landmark_point,
                             dropout_val=1., 
                             activation="sigmoid",
                             is_training=is_training,
                             use_bias=False)
        
        out_y = new_fc_layer(out, 
                             num_inputs=int(out.get_shape().as_list()[-1]), 
                             num_outputs=1000,
                             dropout_val=1.-dropout_rate, 
                             activation="NONE",
                             is_training=is_training,
                             use_bias=False)
        out_y = new_fc_layer(out_y, 
                             num_inputs=int(out_y.get_shape().as_list()[-1]), 
                             num_outputs=self.num_landmark_point,
                             dropout_val=1., 
                             activation="sigmoid",
                             is_training=is_training,
                             use_bias=False)

        out_x = tf.expand_dims(out_x, 1)
        out_y = tf.expand_dims(out_y, 1)
        out_x = tf.expand_dims(out_x, -1)
        out_y = tf.expand_dims(out_y, -1)
        self.point_position = tf.nn.sigmoid(tf.concat([out_x, out_y], axis=-1))
        
        print ('--------------------INFO---------------------')
        print ('The shape of your point map: ', self.point_map)
        print ('The shape of your point position: ', self.point_position)
        print ('---------------------------------------------')


    def calculate_loss(self):
        """[summary]
        
        Returns:
            [type] -- [description]
        """
        self.point_map_loss = mse_loss_mean(self.point_map, self.point_map_placeholder)
        self.point_position_loss = mse_loss_mean(self.point_position, self.point_position_placeholder)
        self.total_loss = 2 * self.point_map_loss + self.point_position_loss
        self.point_map_acc = self.object_accuracy(self.point_map, self.point_map_placeholder)
        return self.total_loss


    def object_accuracy(self, objectness_pred, objectness_label):
        """[summary]
        
        Arguments:
            objectness_pred {[type]} -- [description]
            objectness_label {[type]} -- [description]
        
        Returns:
            [type] -- [description]
        """
        objectness_mask = tf.math.greater(objectness_pred, tf.convert_to_tensor(np.array(self.threshold), tf.float32))
        objectness_mask = tf.cast(objectness_mask, tf.float32)
        delta = (objectness_label - objectness_mask) * objectness_label
        obj_acc = 1. - tf.reduce_sum(delta) / (tf.reduce_sum(objectness_label) + 0.0001)
        return obj_acc


    def read_target(self, file_path):
        # ----------------------------------- #
        # create initial label for point map and position   
        # ----------------------------------- #
        point_position_label = np.zeros((1, self.num_landmark_point,  2))
        point_map_lable = np.zeros((self.grid_num, self.grid_num, self.num_landmark_point))

        # ----------------------------------- #
        # reading the label in a .txt file foreach image 
        #------------------------------------ #
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
            # ----------------------------------- #
            # filling the point map label         #
            #------------------------------------ #
            data_x = float(data[i*2])
            data_y = float(data[i*2 + 1])
            cell_x = int(math.floor(data_x / self.grid_size_relative))
            cell_y = int(math.floor(data_y / self.grid_size_relative))
            point_map_lable[cell_y, cell_x, i] = 1.0

            # ----------------------------------- #
            # filling the point position label    #
            #------------------------------------ #
            point_position_label[0, i, 0] = (data_x - cell_x * self.grid_size_relative)/self.grid_size_relative
            point_position_label[0, i, 1] = (data_y - cell_y * self.grid_size_relative)/self.grid_size_relative

        return point_map_lable, point_position_label


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
            y_pred_map = []
            y_pred_position = []

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
                    tmp_y_map, tmp_y_position = self.read_target(label_folder_path + dataset_file_list[idx].split('.')[0] + ".txt")
                    x_batch.append(tmp_x)
                    y_pred_map.append(tmp_y_map)
                    y_pred_position.append(tmp_y_position)

                except Exception as e:
                    print ("---------------------------------------------------------------")
                    print ("WARNING: the " + str(e))
                    print ("---------------------------------------------------------------")

                idx += 1
            yield (np.array(x_batch), np.array(y_pred_map), np.array(y_pred_position))


    def optimize(self, 
                 iteration, 
                 subdivition,
                 cost_tensor,
                 optimizer_tensor,
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
                x_train, y_train_map, y_train_position = next(train_generator)
                feed_dict = {}
                feed_dict[self.input_placeholder] = x_train
                feed_dict[self.point_map_placeholder] = y_train_map
                feed_dict[self.point_position_placeholder] = y_train_position
                session.run(optimizer_tensor, feed_dict)
                loss = session.run(cost_tensor, feed_dict)
                t_losses.append(loss)
                print ("> Train sub", j, 'loss : ', loss)
                
            x_val, y_val_map, y_val_position = next(val_generator)
            feed_dict = {}
            feed_dict[self.input_placeholder] = x_val
            feed_dict[self.point_map_placeholder] = y_val_map
            feed_dict[self.point_position_placeholder] = y_val_position
            loss = session.run(cost_tensor, feed_dict)
            map_acc, pml, ppl = session.run([self.point_map_acc, self.point_map_loss, self.point_position_loss], feed_dict)
            
            t_loss = sum(t_losses) / (len(t_losses) + 0.0001)
            self.train_loss.append(t_loss)
            self.val_loss.append(loss)
                
            if best_loss > loss:
                best_loss = loss
                sign = "************* model saved"
                saver.save(session, path_tosave_model)
        
            print (">> epoch: ", i, "train loss: ", round(t_loss, 3), "val loss: ", round(loss, 3), \
                "val map acc: ", round(map_acc, 3), round(pml, 3), round(ppl, 3), sign)  
