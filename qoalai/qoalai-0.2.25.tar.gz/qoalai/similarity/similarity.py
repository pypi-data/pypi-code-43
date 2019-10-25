import cv2
import math
import random
import numpy as np 
import tensorflow as tf 
import qoalai.networks.densenet as densenet
from simple_tensor.tensor_operations import *
from simple_tensor.tensor_losses import mse_loss_mean, mse_loss_sum
from comdutils.file_utils import *
slim = tf.contrib.slim


class Similarity(): 
    def __init__(self, 
                 classes = ['normal', 'hard_damage', 'other'],
                 input_height = 300,
                 input_width = 300, 
                 input_channel = 3,
                 num_feature = 128): 

        self.input_height = input_height
        self.input_width = input_width
        self.input_channel = input_channel
        self.num_feature = num_feature
        self.classes = classes

        self.input_placeholder = tf.placeholder(tf.float32, shape=(None, self.input_height, self.input_width, self.input_channel))
        self.input_placeholder_pos = tf.placeholder(tf.float32, shape=(None, self.input_height, self.input_width, self.input_channel))
        self.input_placeholder_neg = tf.placeholder(tf.float32, shape=(None, self.input_height, self.input_width, self.input_channel))
        self.input_placeholder_other = tf.placeholder(tf.float32, shape=(None, self.input_height, self.input_width, self.input_channel))

    
    def build_net(self, input_tensor, is_training, reuse=None): 
        arg_scoope = densenet.densenet_arg_scope()
        out = None

        with slim.arg_scope(arg_scoope):
            out = densenet.densenet121(inputs=input_tensor, 
                                       num_classes=1, 
                                       is_training=is_training,
                                       reuse = reuse)
            base_var_list = tf.get_collection(tf.GraphKeys.GLOBAL_VARIABLES)
        out = tf.keras.layers.Flatten()(out)
        
        out = tf.layers.Dense(units=128, use_bias=False, _reuse=reuse)(out)
        out = tf.nn.sigmoid(out)
    
        return out

    
    def calculate_loss(self, feature1, feature2, feature3, feature4): 
        self.pos_loss = mse_loss_mean(feature1, feature2)
        self.neg_loss = mse_loss_mean(feature1, feature3)
        self.other_loss = mse_loss_mean(feature1, feature4)
        self.loss = self.pos_loss - 1.3 * self.neg_loss - self.other_loss

    
    def batch_generator(self, batch_size, dataset_path, message):
        """Train Generator
        
        Arguments:
            batch_size {integer} -- the size of the batch
            image_name_list {list of string} -- the list of image name
        """
        file_list_by_class = {}
        idx = {}
        for i in self.classes:
            file_list_by_class[i] = get_filenames(dataset_path + i)
            random.shuffle(file_list_by_class[i])
            idx[i] = 0
        
        perclass_sample = int(batch_size/len(self.classes))

        print ("------------------------INFO IMAGES-------------------")
        print ("Image Folder: " + dataset_path)
        for i in self.classes:
            print ("Number of Image in " + str(i) + ": ", len(file_list_by_class[i]))
        print ("------------------------------------------------------")

        # Infinite loop.
        while True:
            x_batch = []
            x_pos = []
            x_neg = []
            x_other = []

            for i in self.classes:
                if i != 'other':
                    for j in range(perclass_sample):
                        if idx[i] >= len(file_list_by_class[i]):
                            random.shuffle(file_list_by_class[i])
                            print ("==>>> INFO: your " + message + " in class " + str(i) + " dataset is reshuffled again", idx[i])
                            idx[i] = 0
                        try:
                            tmp_x = cv2.imread(dataset_path + i + "/" + file_list_by_class[i][idx[i]])
                            tmp_x = cv2.cvtColor(tmp_x, cv2.COLOR_BGR2RGB)
                            tmp_x = cv2.resize(tmp_x, dsize=(self.input_width, self.input_height), interpolation=cv2.INTER_CUBIC)
                            tmp_x = tmp_x.astype(np.float32) / 255.
                            x_batch.append(tmp_x)
                            
                            # ------------------------------------ #
                            # get the positive input image         #
                            # ------------------------------------ #
                            idx_pos= random.randint(0, len(file_list_by_class[i])-1)
                            tmp_x_pos = cv2.imread(dataset_path + i + "/" + file_list_by_class[i][idx_pos])
                            tmp_x_pos = cv2.cvtColor(tmp_x_pos, cv2.COLOR_BGR2RGB)
                            tmp_x_pos = cv2.resize(tmp_x_pos, dsize=(self.input_width, self.input_height), interpolation=cv2.INTER_CUBIC)
                            tmp_x_pos = tmp_x_pos.astype(np.float32) / 255.
                            x_pos.append(tmp_x_pos)

                            # ------------------------------------ #
                            # get the negative input image         #
                            # ------------------------------------ #
                            the_list = list(file_list_by_class.keys())
                            the_list.remove(i)
                            if i != 'other':
                                the_list.remove('other')
                            tmp_class = random.choice(the_list)

                            idx_neg = random.randint(0, len(file_list_by_class[tmp_class])-1)
                            tmp_x_neg = cv2.imread(dataset_path + tmp_class + "/" + file_list_by_class[tmp_class][idx_neg])
                            tmp_x_neg = cv2.cvtColor(tmp_x_neg, cv2.COLOR_BGR2RGB)
                            tmp_x_neg = cv2.resize(tmp_x_neg, dsize=(self.input_width, self.input_height), interpolation=cv2.INTER_CUBIC)
                            tmp_x_neg = tmp_x_neg.astype(np.float32) / 255.
                            x_neg.append(tmp_x_neg)

                            # ------------------------------------ #
                            # get the "other" input image          #
                            # ------------------------------------ #
                            idx_other = random.randint(0, len(file_list_by_class['other'])-1)
                            tmp_x_other = cv2.imread(dataset_path + 'other' + "/" + file_list_by_class['other'][idx_other])
                            tmp_x_other = cv2.cvtColor(tmp_x_other, cv2.COLOR_BGR2RGB)
                            tmp_x_other = cv2.resize(tmp_x_other, dsize=(self.input_width, self.input_height), interpolation=cv2.INTER_CUBIC)
                            tmp_x_other = tmp_x_other.astype(np.float32) / 255. 
                            x_other.append(tmp_x_other)

                        except Exception as e:
                            print ("-----------------------------------------------------------------------------")
                            print ('>>> WARNING: fail handling ' +  file_list_by_class[i][idx[i]], e)
                            print ("-----------------------------------------------------------------------------")
                        
                        idx[i] += 1

            c = list(zip(x_batch, x_pos, x_neg, x_other))
            random.shuffle(c)
            x_batch, x_pos, x_neg, x_other = zip(*c)
            yield (np.array(x_batch), np.array(x_pos), np.array(x_neg), np.array(x_other))


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
                x_train, x_train_pos, x_train_neg, x_train_other = next(train_generator)
                feed_dict = {}
                feed_dict[self.input_placeholder] = x_train
                feed_dict[self.input_placeholder_pos] = x_train_pos
                feed_dict[self.input_placeholder_neg] = x_train_neg
                feed_dict[self.input_placeholder_other] = x_train_other
                session.run(optimizer_tensor, feed_dict)
                loss = session.run(self.loss, feed_dict) 
                t_losses.append(loss)
                print ("> Train sub", j, 'loss : ', loss)
                
            x_val, y_val_pos, y_val_neg, y_val_other = next(val_generator)
            feed_dict = {}
            feed_dict[self.input_placeholder] = x_val
            feed_dict[self.input_placeholder_pos] = y_val_pos
            feed_dict[self.input_placeholder_neg] = y_val_neg
            feed_dict[self.input_placeholder_other] = y_val_other
            loss, p_loss, n_loss, o_loss = session.run([self.loss, self.pos_loss, self.neg_loss, self.other_loss], feed_dict)
            
            t_loss = sum(t_losses) / (len(t_losses) + 0.0001)
            self.train_loss.append(t_loss)
            self.val_loss.append(loss)
                
            if best_loss > loss:
                best_loss = loss
                sign = "************* model saved"
                saver.save(session, path_tosave_model)
        
            print (">> epoch: ", i, "train loss: ", round(t_loss, 3), "val loss: ", round(loss, 3), \
                "p loss: ", round(p_loss, 3), "n loss: ", round(n_loss, 3), "o loss: ", round(o_loss,3), sign)  
