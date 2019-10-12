# -*- coding: utf-8 -*-
import tflex
import tensorflow as tf

def test_from_session():
    img = tf.placeholder(name="img", dtype=tf.float32, shape=(1, 64, 64, 3))
    var = tf.get_variable("weights", dtype=tf.float32, shape=(1, 64, 64, 3))
    val = img + var
    out = tf.identity(val, name="out")

    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())
        converter = tflex.Converter.from_session(sess, [img], [out])
        converter._print()


def main(_):
    # test from_session() method.
    test_from_session()


if __name__ == '__main__':
    tf.app.run()