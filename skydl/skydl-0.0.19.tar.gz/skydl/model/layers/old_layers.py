# -*- coding: utf-8 -*-


class OldLayers:
    """
    临时从super_net.py中移过来的一些layer
    TODO 以后可以删除该类
    """
    def __init__(self, parser_args):
        self.parser_args = parser_args

    def keras_cnn_layers(self, _x, name="predict"):
        import tensorflow as tf
        # 单机双卡GTX T1080下，mnist跑完batch_size=64,epochs=10的train data只需要24秒，用时最短！
        reuse = tf.AUTO_REUSE
        with tf.variable_scope('L1', reuse=reuse):
            L1 = tf.layers.conv2d(_x, 64, [3, 3], reuse=reuse)
            L1 = tf.layers.max_pooling2d(L1, [2, 2], [2, 2])
            L1 = tf.layers.dropout(L1, 0.7, True)
        with tf.variable_scope('L2', reuse=reuse):
            L2 = tf.layers.conv2d(L1, 128, [3, 3], reuse=reuse)
            L2 = tf.layers.max_pooling2d(L2, [2, 2], [2, 2])
            L2 = tf.layers.dropout(L2, 0.7, True)
        with tf.variable_scope('L2-1', reuse=reuse):
            L2_1 = tf.layers.conv2d(L2, 128, [3, 3], reuse=reuse)
            L2_1 = tf.layers.max_pooling2d(L2_1, [2, 2], [2, 2])
            L2_1 = tf.layers.dropout(L2_1, 0.7, True)
        with tf.variable_scope('L3', reuse=reuse):
            L3 = tf.contrib.layers.flatten(L2_1)
            L3 = tf.layers.dense(L3, 1024, activation=tf.nn.relu)
            L3 = tf.layers.dropout(L3, 0.5, True)

        with tf.variable_scope('L4', reuse=reuse):
            L4 = tf.layers.dense(L3, 256, activation=tf.nn.relu)
        with tf.variable_scope('LF', reuse=reuse):
            LF = tf.layers.dense(L4, 10, activation=None, name=name)
        return LF

    def bilstm_layers(self, _x, name="predict"):
        import tensorflow as tf
        from tensorflow.contrib import rnn
        from py_common_util.tensorflow.tf_utils import TFUtils
        _weights, _biases = TFUtils.tf_random_normal_weight_biases(self.parser_args.rnn_hidden,
                                                                   self.parser_args.classes,
                                                                   self.parser_args.num_hidden)
        _x = tf.transpose(_x, [1, 0, 2])
        _x = tf.reshape(_x, [-1, self.parser_args.rnn_input])
        _x = tf.split(_x, self.parser_args.time_steps, 0)
        lstm_fw_cell = rnn.BasicLSTMCell(self.parser_args.rnn_hidden, forget_bias=1.0)
        lstm_bw_cell = rnn.BasicLSTMCell(self.parser_args.rnn_hidden, forget_bias=1.0)
        # static_bidirectional_rnn | bidirectional_dynamic_rnn
        outputs, states_fw, states_bw = tf.nn.static_bidirectional_rnn(cell_fw=lstm_fw_cell,
                                                                       cell_bw=lstm_bw_cell,
                                                                       inputs=_x,
                                                                       dtype=tf.float32,
                                                                       scope="BiLSTM")
        outputs = tf.nn.dropout(outputs, self.parser_args.keep_prob)
        wx_plus_b = tf.matmul(outputs[-1], _weights) + _biases
        return self.batch_normalization_layer(self.parser_args, wx_plus_b, self.parser_args.channels, name=name)

    def lstm_layers(self, _x, name="predict"):
        import tensorflow as tf
        from py_common_util.tensorflow.tf_utils import TFUtils
        with tf.variable_scope(tf.get_variable_scope(), reuse=tf.AUTO_REUSE):
            _weights, _biases = TFUtils.tf_random_normal_weight_biases(self.parser_args.rnn_hidden,
                                                                       self.parser_args.classes,
                                                                       self.parser_args.num_hidden)
            _x = tf.transpose(_x, [1, 0, 2])  # [batch, height, width] -> [height, batch, width]
            _x = tf.reshape(_x, [-1, self.parser_args.rnn_input])
            _x = tf.split(_x, self.parser_args.time_steps, 0)
            # init_state = tf.placeholder(tf.float32, [self.flags.num_hidden, 2, self.flags.batch_size, self.flags.n_hidden])
            # state_per_layer_list = tf.unstack(init_state, axis=0)
            # rnn_tuple_state = tuple(
            #     [tf.nn.rnn_cell.LSTMStateTuple(state_per_layer_list[idx][0], state_per_layer_list[idx][1]) for idx in range(self.flags.num_hidden)]
            # )
            lstm_cell = tf.nn.rnn_cell.BasicLSTMCell(self.parser_args.rnn_hidden, forget_bias=1.0)
            lstm_cell = tf.nn.rnn_cell.DropoutWrapper(cell=lstm_cell, output_keep_prob=self.parser_args.keep_prob)
            lstm_cell = tf.nn.rnn_cell.MultiRNNCell([lstm_cell] * self.parser_args.num_hidden, state_is_tuple=True)
            outputs, states = tf.nn.static_rnn(lstm_cell, _x, dtype=tf.float32, scope="LSTM")
            # outputs, states = tf.nn.dynamic_rnn(cell=lstm_cell, inputs=_x, initial_state=rnn_tuple_state, dtype=tf.float32, scope="LSTM")
            wx_plus_b = tf.matmul(outputs[-1], _weights) + _biases
            return self.batch_normalization_layer(self.parser_args, wx_plus_b, self.parser_args.channels, name=name)

    def cnn2_layers(self, _x, name="predict"):
        import tensorflow as tf
        """Model function for CNN. ref: https://www.tensorflow.org/tutorials/layers"""
        # Input Layer
        input_layer = tf.reshape(_x, [-1, self.parser_args.width, self.parser_args.height, self.parser_args.channels])

        # Convolutional Layer #1
        conv1 = tf.layers.conv2d(
            inputs=input_layer,
            filters=32,
            kernel_size=[5, 5],
            padding="same",
            activation=tf.nn.relu)
        # conv1 = SuperModel.batch_normalization_layer(conv1, self.flags.channels)

        # Pooling Layer #1
        pool1 = tf.layers.max_pooling2d(inputs=conv1, pool_size=[2, 2], strides=2)

        # Convolutional Layer #2 and Pooling Layer #2
        conv2 = tf.layers.conv2d(
            inputs=pool1,
            filters=self.parser_args.width,
            kernel_size=[5, 5],
            padding="same",
            activation=tf.nn.relu)
        pool2 = tf.layers.max_pooling2d(inputs=conv2, pool_size=[2, 2], strides=2)

        # Dense Layer
        pool_size = self.parser_args.height//4
        pool2_flat = tf.reshape(pool2, [-1, pool_size * pool_size * self.parser_args.width])
        dense = tf.layers.dense(inputs=pool2_flat, units=1024, activation=tf.nn.relu)
        dropout = tf.layers.dropout(inputs=dense, rate=(1 - self.parser_args.keep_prob), training=True)

        # Logits Layer
        logits = tf.layers.dense(inputs=dropout, units=self.parser_args.classes, name=name)
        return logits

    def cnn_layers(self, _x, name="predict"):
        import tensorflow as tf
        # Store layers weight & bias
        pool_size = self.parser_args.height // 4
        weights = {
            # 5x5 conv, 1 input, 32 outputs
            'wc1': tf.Variable(tf.random_normal([5, 5, 1, 32])),
            # 5x5 conv, 32 inputs, 64 outputs
            'wc2': tf.Variable(tf.random_normal([5, 5, 32, self.parser_args.width])),
            # fully connected, 7*7*64 inputs, 1024 outputs
            'wd1': tf.Variable(tf.random_normal([pool_size * pool_size * self.parser_args.width, 1024])),
            # 1024 inputs, 10 outputs (class prediction)
            'out': tf.Variable(tf.random_normal([1024, self.parser_args.classes]))
        }
        biases = {
            'bc1': tf.Variable(tf.random_normal([32])),
            'bc2': tf.Variable(tf.random_normal([self.parser_args.width])),
            'bd1': tf.Variable(tf.random_normal([1024])),
            'out': tf.Variable(tf.random_normal([self.parser_args.classes]))
        }

        # Create some wrappers for simplicity
        def conv2d(x, W, b, strides=1):
            # Conv2D wrapper, with bias and relu activation
            x = tf.nn.conv2d(x, W, strides=[1, strides, strides, 1], padding='SAME')
            x = tf.nn.bias_add(x, b)
            return tf.nn.relu(x)

        def maxpool2d(x, k=2):
            # MaxPool2D wrapper
            return tf.nn.max_pool(x, ksize=[1, k, k, 1], strides=[1, k, k, 1], padding='SAME')

        # Create model
        def conv_net(x, weights, biases, keep_prob, name="predict"):
            # Reshape input picture, shape:[-1, width, height, channels]， 它的值和[channels, height, width, -1]相反
            x = tf.reshape(x, shape=[-1, self.parser_args.width, self.parser_args.height, self.parser_args.channels])

            # Convolution Layer
            conv1 = conv2d(x, weights['wc1'], biases['bc1'])
            # conv1 = self.batch_normalization_layer(conv1, self.flags.channels)
            # Max Pooling (down-sampling)
            conv1 = maxpool2d(conv1, k=2)

            # Convolution Layer
            conv2 = conv2d(conv1, weights['wc2'], biases['bc2'])
            # Max Pooling (down-sampling)
            conv2 = maxpool2d(conv2, k=2)

            # Fully connected layer
            # Reshape conv2 output to fit fully connected layer input
            fc1 = tf.reshape(conv2, [-1, weights['wd1'].get_shape().as_list()[0]])
            fc1 = tf.add(tf.matmul(fc1, weights['wd1']), biases['bd1'])
            fc1 = tf.nn.relu(fc1)
            # Apply Dropout
            fc1 = tf.nn.dropout(fc1, keep_prob)

            # Output, class prediction
            out = tf.add(tf.matmul(fc1, weights), biases, name=name)
            return out

        # Construct model
        pred = conv_net(_x, weights, biases, self.parser_args.keep_prob, name=name)
        return pred

    def batch_normalization_layer(self, _x, n_out, phase_train=None, name="predict"):
        """
        ref: https://gist.github.com/tomokishii/0ce3bdac1588b5cca9fa5fbdf6e1c412
        invoke as e.g. conv1_bn = TFUtils.batch_norm(conv1.output(), 32, phase_train)
        Batch normalization on convolutional maps.
        Ref.: http://stackoverflow.com/questions/33949786/how-could-i-use-batch-normalization-in-tensorflow
        Args:
            x:           Tensor, 4D BHWD input maps, after wx_plus_b operation()
            n_out:       integer, depth of input maps, eq: channels
            phase_train: boolean tf.Varialbe, true indicates training phase e.g. phase_train=tf.cast(True, tf.bool)
            scope:       string, variable scope
        Return:
            normed:      batch-normalized maps
        """
        import tensorflow as tf
        from py_common_util.tensorflow.tf_utils import TFUtils
        with tf.variable_scope('bn'):
            beta = tf.Variable(tf.constant(0.0, shape=[n_out]),
                               name='beta', trainable=True)
            gamma = tf.Variable(tf.constant(1.0, shape=[n_out]),
                                name='gamma', trainable=True)
            axis = TFUtils.get_axis(_x)
            batch_mean, batch_var = tf.nn.moments(_x, axis, name='moments')
            ema = tf.train.ExponentialMovingAverage(decay=0.5)

            def mean_var_with_update():
                ema_apply_op = ema.apply([batch_mean, batch_var])
                with tf.control_dependencies([ema_apply_op]):
                    return tf.identity(batch_mean), tf.identity(batch_var)
            mean, var = tf.cond(phase_train,
                                mean_var_with_update,
                                lambda: (ema.average(batch_mean), ema.average(batch_var)))
            _x = tf.nn.batch_normalization(_x, mean, var, beta, gamma, TFUtils.get_small_epsilon(), name=name)
        return _x
