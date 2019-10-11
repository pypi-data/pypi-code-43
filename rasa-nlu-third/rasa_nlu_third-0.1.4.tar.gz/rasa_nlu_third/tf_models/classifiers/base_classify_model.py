# create by fanfan on 2019/3/26 0026
import tensorflow as tf
import os
from rasa_nlu_third.tf_models.classifiers import constant
from rasa_nlu_third.third_models.bert import modeling as bert_modeling




class BaseClassifyModel(object):
    def __init__(self,params,use_bert=False):
        self.params = params
        self.bert_config = None
        if use_bert:
            bert_config = bert_modeling.BertConfig.from_json_file(
                os.path.join(params.bert_model_path, "bert_config.json"))
            if params.max_sentence_length > bert_config.max_position_embeddings:
                raise ValueError(
                    "Cannot use sequence length %d because the BERT model "
                    "was only trained up to sequence length %d" %
                    (params.max_sentence_length, bert_config.max_position_embeddings)
                )

            self.bert_config = bert_config
        self.input_initialization = False

    def create_placeholder(self):
        if self.input_initialization == False:
            self.input_x = tf.placeholder(dtype=tf.int32, shape=[None, self.params.max_sentence_length],
                                          name=constant.INPUT_NODE_NAME)
            self.input_y = tf.placeholder(dtype=tf.int32, shape=[None],
                                          name="Targets")
            self.dropout = tf.placeholder_with_default(self.params.dropout_prob, (), name='dropout')
            self.input_mask = tf.placeholder(dtype=tf.int32, shape=[None, self.params.max_sentence_length], name=constant.INPUT_MASK_NAME)
            self.input_segment = tf.placeholder(dtype=tf.int32, shape=[None, self.params.max_sentence_length], name='segment')
            self.input_initialization = True
        return self.input_x, self.input_y, self.dropout, self.input_mask, self.input_segment


    def get_sentence_length(self, data):
        used = tf.sign(tf.abs(data))
        length = tf.reduce_sum(used, reduction_indices=1)
        length = tf.cast(length, tf.int32)
        return length

    def embedding_layer(self,input_ids,is_training,input_mask=None,segment_ids=None,use_one_hot_embeddings=False):
        if self.bert_config != None:
            bert_model_layer = bert_modeling.BertModel(
                config=self.bert_config,
                is_training=is_training,
                input_ids=input_ids,
                input_mask=input_mask,
                token_type_ids=segment_ids,
                use_one_hot_embeddings=use_one_hot_embeddings
            )
            # 获取对应的embedding 输入数据[batch_size, seq_length, embedding_size]
            input_embeddings = bert_model_layer.get_sequence_output()
        else:
            with tf.variable_scope('embeddings_layer'):
                word_embeddings = tf.get_variable('word_embeddings',
                                                  [self.params.vocab_size, self.params.embedding_size])
                input_embeddings = tf.nn.embedding_lookup(word_embeddings, input_ids)

        return input_embeddings

    def create_model(self,input_x,dropout,is_training=False,input_mask=None,input_segment=None):
        with tf.variable_scope("model_define", reuse=tf.AUTO_REUSE) as scope:
            real_sentence_length = self.get_sentence_length(input_x)
            input_embeddings = self.embedding_layer(input_x, is_training, input_mask, input_segment)

            with tf.variable_scope('classify_layer'):
                output_layer = self.classify_layer(input_embeddings,dropout,real_sentence_length)


            with tf.name_scope("output"):
                logits = tf.layers.dense(output_layer, self.params.num_tags)

        return logits

    def make_train(self,input_x=None, input_y=None, input_mask=None, input_segment=None,use_tfrecord=False):
        if not use_tfrecord:
            input_x, input_y, dropout, input_mask, input_segment = self.create_placeholder()
        else:
            dropout = tf.placeholder_with_default(self.params.dropout_prob, shape=[], name='dropout')

        logits = self.create_model(input_x,dropout,is_training=True,input_mask=input_mask,input_segment=input_segment)
        logits = tf.identity(logits,name=constant.OUTPUT_NODE_LOGIT)

        globalStep = tf.Variable(0, name="globalStep", trainable=False)
        with tf.variable_scope('loss'):
            loss = tf.reduce_mean(tf.nn.sparse_softmax_cross_entropy_with_logits(logits=logits,labels=input_y))
            optimizer = tf.train.AdamOptimizer(self.params.learning_rate)

            grads_and_vars = optimizer.compute_gradients(loss)
            capped_grads_vars = [[tf.clip_by_value(g, -self.params.clip, self.params.clip), v]
                                 for g, v in grads_and_vars]
            train_op = optimizer.apply_gradients(capped_grads_vars,globalStep)

        predict = tf.argmax(logits,axis=1,output_type=tf.int32,name=constant.OUTPUT_NODE_NAME)
        accuracy = tf.reduce_mean(tf.cast(tf.equal(predict,input_y),dtype=tf.float32))


        with tf.variable_scope('summary'):
            tf.summary.scalar("loss", loss)
            tf.summary.scalar("accuracy", accuracy)
            summary_op = tf.summary.merge_all()

        return loss,globalStep,train_op,summary_op


    def make_test(self,input_x=None, input_y=None, dropout=None, input_mask=None, input_segment=None,use_tfrecord=False):
        if not use_tfrecord:
            input_x, input_y, dropout, input_mask, input_segment = self.create_placeholder()
        else:
            dropout = tf.placeholder_with_default(1.0, shape=[], name='dropout')
        logits = self.create_model(input_x, dropout,is_training=False,input_mask=input_mask,input_segment=input_segment)
        with tf.variable_scope('loss'):
            loss = tf.reduce_mean(tf.nn.sparse_softmax_cross_entropy_with_logits(logits=logits,labels=input_y))
        predict = tf.argmax(logits,axis=1,output_type=tf.int64,name=constant.OUTPUT_NODE_NAME)
        return loss,predict


    def model_restore(self, sess, tf_saver):
        '''
        模型恢复或者初始化
        :param sess: 
        :param tf_saver: 
        :return: 
        '''
        ckpt = tf.train.get_checkpoint_state(os.path.dirname(self.params.model_path))
        if ckpt and ckpt.model_checkpoint_path:
            print("restor model")
            tf_saver.restore(sess, ckpt.model_checkpoint_path)
        else:
            print("init model")
            sess.run(tf.global_variables_initializer())

        if self.bert_config != None:
            tvars = tf.trainable_variables()
            # 加载BERT模型
            bert_init_checkpoint = os.path.join(self.params.bert_model_path, 'bert_model.ckpt')
            if os.path.exists(self.params.bert_model_path):
                (assignment_map, initialized_variable_names) = bert_modeling.get_assignment_map_from_checkpoint(tvars,
                                                                                                                bert_init_checkpoint)
                tf.train.init_from_checkpoint(bert_init_checkpoint, assignment_map)


    def classify_layer(self, input_embedding,dropout,real_sentence_length=None):
        """Implementation of specific classify layer"""
        raise NotImplementedError()


    @staticmethod
    def load_model_from_pb(model_path):
        sess = tf.Session(config=tf.ConfigProto(
            allow_soft_placement=True,
            log_device_placement=False
        ))

        with tf.gfile.GFile(model_path,'rb') as fr:
            graph_def = tf.GraphDef()
            graph_def.ParseFromString(fr.read())
            sess.graph.as_default()
            tf.import_graph_def(graph_def,name="")

        input_node = sess.graph.get_operation_by_name(constant.INPUT_NODE_NAME).outputs[0]
        input_node_mask = sess.graph.get_operation_by_name(constant.INPUT_MASK_NAME).outputs[0]
        predict_node = sess.graph.get_operation_by_name(constant.OUTPUT_NODE_LOGIT).outputs[0]
        return sess,input_node,input_node_mask,predict_node


    def make_pb_file(self,model_dir):
        graph = tf.Graph()
        with graph.as_default():
            session_conf = tf.ConfigProto(allow_soft_placement=True, log_device_placement=False)
            session_conf.gpu_options.allow_growth = True
            session_conf.gpu_options.per_process_gpu_memory_fraction = 0.9

            sess = tf.Session(config=session_conf)
            with sess.as_default():
                input_x = tf.placeholder(dtype=tf.int32,shape=(None,self.params.max_sentence_length),name=constant.INPUT_NODE_NAME)
                input_x_mask = tf.placeholder(dtype=tf.int32, shape=(None, self.params.max_sentence_length),
                                              name=constant.INPUT_MASK_NAME)
                dropout = tf.placeholder_with_default(1.0,shape=(), name='dropout')
                logits = self.create_model(input_x, dropout,is_training=False,input_mask=input_x_mask,input_segment=None)
                logits_output = tf.nn.softmax(logits,name=constant.OUTPUT_NODE_LOGIT)
                predict = tf.argmax(logits, axis=1, output_type=tf.int32,
                                    name=constant.OUTPUT_NODE_NAME)

                saver = tf.train.Saver(tf.global_variables(), max_to_keep=5)
                checkpoint = tf.train.latest_checkpoint(model_dir)
                if checkpoint:
                    saver.restore(sess,checkpoint)
                else:
                    raise FileNotFoundError("模型文件未找到")

                output_graph_with_weight = tf.graph_util.convert_variables_to_constants(sess,sess.graph_def,[constant.OUTPUT_NODE_NAME,constant.OUTPUT_NODE_LOGIT,constant.INPUT_MASK_NAME])

                with tf.gfile.GFile(os.path.join(model_dir,'classify.pb'),'wb') as gf:
                    gf.write(output_graph_with_weight.SerializeToString())
        return os.path.join(model_dir,'classify.pb')




