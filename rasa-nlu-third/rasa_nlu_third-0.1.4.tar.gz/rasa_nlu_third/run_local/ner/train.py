# create by fanfan on 2019/4/10 0010
import sys
sys.path.append(r"/data/python_project/nlp_research")
import os

import argparse

from rasa_nlu_third.tf_models.ner.params import Params
from rasa_nlu_third.tf_models.ner.bilstm import BiLSTM
import tensorflow as tf
import tqdm
from sklearn.metrics import f1_score
from rasa_nlu_third.data_process.ner.data_loader import RasaData
from rasa_nlu_third.data_process.ner.tf_record_util import input_fn,make_tfrecord_files



def argument_parser():
    parser = argparse.ArgumentParser(description="训练参数")
    parser.add_argument('--output_path',type=str,default='output/',help="中间文件生成目录")
    parser.add_argument('--origin_data', type=str, default=None, help="原始数据地址")
    parser.add_argument('--data_type', type=str, default="rasa", help="原始数据格式，，目前支持默认的，还有rasa格式")

    parser.add_argument('--device_map', type=str, default="0", help="gpu 的设备id")
    parser.add_argument('--use_bert', type=int, default="0", help="是否使用bert模型")
    #parser.add_argument('--use_bert',action='store_true',help='是否使用bert')
    parser.add_argument('--bert_model_path',type=str,help='bert模型目录')

    parser.add_argument('--max_sentence_length', type=int,default=20, help='一句话的最大长度')
    return parser.parse_args()


def train(params):
    if os.path.isabs(params.output_path) == False:
        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), params.output_path)
        params.output_path = output_path

    if not os.path.exists(params.output_path):
        os.mkdir(params.output_path)

    make_tfrecord_files(params)
    if params.data_type == 'default':
        raise NotImplementedError("还没有实现")
        #data_processer = data_process.NormalData(params.origin_data, output_path=params.output_path)
    else:
        data_processer = RasaData(params.origin_data, output_path=params.output_path,tag_schema=params.tag_schema)

    vocab, vocab_list, labels = data_processer.load_vocab_and_labels()

    params.vocab_size = len(vocab_list)
    params.num_tags = len(labels)
    if not os.path.exists(params.output_path):
        os.makedirs(params.output_path)


    os.environ["CUDA_VISIBLE_DEVICES"] = params.device_map
    with tf.Graph().as_default():
        session_conf = tf.ConfigProto(allow_soft_placement=True, log_device_placement=False)
        session_conf.gpu_options.allow_growth = True
        session_conf.gpu_options.per_process_gpu_memory_fraction = 0.9

        sess = tf.Session(config=session_conf)
        with sess.as_default():
            tfrecord_input = input_fn(os.path.join(params.output_path,'train.tfrecord'),
                                                         mode=tf.estimator.ModeKeys.TRAIN,
                                                         batch_size= params.batch_size,
                                                         max_sentence_length=params.max_sentence_length,
                                                         )

            ner_model = BiLSTM(params)
            loss, global_step, train_op, merger_op = ner_model.make_train(input_x=tfrecord_input['input_ids'], input_y=tfrecord_input['label_ids'],use_tfrecord=True)
            # 初始化所有变量
            saver = tf.train.Saver(tf.global_variables(), max_to_keep=5)
            ner_model.model_restore(sess, saver)

            best_f1 = 0
            for _ in tqdm.tqdm(range(params.total_train_steps), desc="steps", miniters=10):
                sess_loss, steps, _ = sess.run([loss, global_step, train_op])

                if steps % params.evaluate_every_steps == 1:
                    tfrecord_input_test = input_fn(os.path.join(params.output_path, "test.tfrecord"),
                                                          batch_size=params.batch_size,
                                                          max_sentence_length=params.max_sentence_length,
                                                          mode=tf.estimator.ModeKeys.EVAL)
                    loss_test, predict_test,sentence_length = ner_model.make_test(input_x=tfrecord_input_test['input_ids'], input_y=tfrecord_input_test['label_ids'],use_tfrecord=True)

                    predict_var = []
                    train_y_var = []
                    loss_total = 0
                    num_batch = 0
                    try:
                        while 1:
                            loss_, predict_, test_input_y_,length = sess.run([loss_test, predict_test, tfrecord_input_test['label_ids'],sentence_length])
                            loss_total += loss_
                            num_batch += 1
                            for p_,t_,len_ in zip(predict_.tolist(),test_input_y_.tolist(),length.tolist()):

                                predict_var += p_[:len_]
                                train_y_var += t_[:len_]
                    except tf.errors.OutOfRangeError:
                        print("eval over")
                    if num_batch > 0:

                        f1_val = f1_score(train_y_var, predict_var, average='micro')
                        print("current step:%s ,loss:%s , f1 :%s" % (steps, loss_total / num_batch, f1_val))

                        if f1_val >= best_f1:
                            saver.save(sess, params.model_path, steps)
                            print("new best f1: %s ,save to dir:%s" % (f1_val, params.output_path))
                            best_f1 = f1_val

            return ner_model.make_pb_file(params.output_path),vocab_list, labels




if __name__ == '__main__':

    argument_dict = argument_parser()

    params = Params()
    params.update_object(argument_dict)



    train(params)
