import keras.backend as K
import numpy as np


def gradient_check(x, theta, epsilon=1e-7):
    """
    https://github.com/marcopeix/Deep_Learning_AI/blob/master/2.Improving%20Deep%20Neural%20Networks/1.Practical%20Aspects%20of%20Deep%20Learning/Gradient%20Checking.ipynb
    :param x:
    :param theta:
    :param epsilon:
    :return:
    """
    thetaplus = theta + epsilon
    thetaminus = theta - epsilon

    J_plus = np.dot(x, thetaplus)
    J_minus = np.dot(x, thetaminus)

    gradapprox = (J_plus - J_minus) / (2 * epsilon)

    # Check if gradapprox is close enough to backward propagation
    grad = x

    numerator = np.linalg.norm(grad - gradapprox)
    denominator = np.linalg.norm(grad) + np.linalg.norm(gradapprox)
    difference = numerator / denominator

    if difference < 1e-7:
        print('The gradient is correct')
    else:
        print('The gradient is wrong')

    return difference


def calc_zeros_percentage(gradients):
    i = 0
    non_zero = []
    total_length = len(gradients)
    for gradient in gradients:
        if gradient == 0.0:
            i += 1
        else:
            non_zero.append(gradient)
    return i * 100 / total_length, np.mean(non_zero)


def get_weight_grad_keras(model, inputs, outputs):
    """ Gets gradient of model for given inputs and outputs for all weights"""
    grads = model.optimizer.get_gradients(model.total_loss, model.trainable_weights)
    symb_inputs = (model._feed_inputs + model._feed_targets + model._feed_sample_weights)
    f = K.function(symb_inputs, grads)
    x, y, sample_weight = model._standardize_user_data(inputs, outputs)
    output_grad = f(x + y + sample_weight)
    return output_grad


def get_layer_output_grad_keras(model, inputs, outputs, layer=-1):
    """ Gets gradient a layer output for given inputs and outputs"""
    grads = model.optimizer.get_gradients(model.total_loss, model.layers[layer].output)
    symb_inputs = (model._feed_inputs + model._feed_targets + model._feed_sample_weights)
    f = K.function(symb_inputs, grads)
    x, y, sample_weight = model._standardize_user_data(inputs, outputs)
    output_grad = f(x + y + sample_weight)
    return output_grad
