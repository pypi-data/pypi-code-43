import tensorflow as tf
import tf_utils
from stable_baselines.common.mpi_adam import MpiAdam
from stable_baselines.common.tf_util import in_session


def logsigmoid(a):
    '''Equivalent to tf.log(tf.sigmoid(a))'''
    return -tf.nn.softplus(-a)


def logit_bernoulli_entropy(logits):
    ent = (1. - tf.nn.sigmoid(logits)) * logits - logsigmoid(logits)
    return ent


def wasserstein_generator_loss(generator_logits):
    return tf.contrib.gan.losses.wargs.wasserstein_generator_loss(generator_logits)


def wasserstein_discriminator_loss(expert_logits, generator_logits):
    return tf.contrib.gan.losses.wargs.wasserstein_discriminator_loss(expert_logits, generator_logits)


def discriminator_regression_loss(logits):
    """
        Computes sigmoid cross entropy given `logits`.

      Measures the probability error in discrete classification tasks in which each
      class is independent and not mutually exclusive.  For instance, one could
      perform multilabel classification where a picture can contain both an elephant
      and a dog at the same time.

      For brevity, let `x = logits`, `z = labels`.  The logistic loss is

            z * -log(sigmoid(x)) + (1 - z) * -log(1 - sigmoid(x))
          = z * -log(1 / (1 + exp(-x))) + (1 - z) * -log(exp(-x) / (1 + exp(-x)))
          = z * log(1 + exp(-x)) + (1 - z) * (-log(exp(-x)) + log(1 + exp(-x)))
          = z * log(1 + exp(-x)) + (1 - z) * (x + log(1 + exp(-x))
          = (1 - z) * x + log(1 + exp(-x))
          = x - x * z + log(1 + exp(-x))
        :param logits:
        :return:
        """
    return tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(logits=logits, labels=tf.ones_like(logits)))


def generator_regression_loss(logits):
    return tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(logits=logits, labels=tf.zeros_like(logits)))


def crossentropy_loss(d_fake_logits, d_real_logits, ent_coeff=0.001):
    """
    Similar to Goodfellow loss
    Was used in Andrew Liao gail-tf
    discriminator_loss is 1.3856011629104614 away from zero

    :param d_fake_logits:
    :param d_real_logits:
    :param ent_coeff:
    :return:
    """
    d_fake_loss = generator_regression_loss(d_fake_logits)  # - log {1 - D(G(z))}
    d_real_loss = discriminator_regression_loss(d_real_logits)  # - log D(x)
    generator_loss = discriminator_regression_loss(d_fake_logits)
    # Build entropy loss
    logits = tf.concat([d_fake_logits, d_real_logits], 0)
    entropy = tf.reduce_mean(logit_bernoulli_entropy(logits))
    entropy_loss = -ent_coeff * entropy

    discriminator_loss = d_fake_loss + d_real_loss + entropy_loss - 1.3856011629104614
    return discriminator_loss, generator_loss, d_fake_loss, d_real_loss, entropy, entropy_loss


def goodfellow_loss(d_real, d_fake):
    """
    Loss as in Goodfellow et al 2014:
            J(D, G) = 1/2m * sum{log(D(x)) + log(1 - D(G(z)))}
    There is no prebuild loss for GANs, customized loss as below.
    Given tensorflow.nn.sigmoid_cross_entropy_with_logits is:
            J(θ) = - y * log g(z) - (1 - y) * log (1 - g(z))
                                where z = θ.T * x, g = sigmoid function
    when y = 1, we obtain left side of d_loss: - log(D(x));
    when y = 0, we obtain right side of d_loss: - log(1 - D(G(z)))
    D and G are interpreted as probabilities so sigmoid function squashes
    logits to interval (0, 1).
    hence:
        d_loss = 1/2m * sum{log(D(x)) + log(1 - D[G(z)])}

        d_loss is 0.6931471824645996 away from zero
    """
    # - log D(x)
    d_left_term = tf.nn.sigmoid_cross_entropy_with_logits(
        logits=d_real,
        labels=tf.ones_like(d_real))
    # - log {1 - D(G(z))}
    d_right_term = tf.nn.sigmoid_cross_entropy_with_logits(
        logits=d_fake,
        labels=tf.zeros_like(d_fake))
    # - 1 / 2m sum{log D(x) + log {1 - D(G(z))}}
    d_loss = tf.reduce_mean(d_left_term + d_right_term) / 2.
    # - log D(G(z))
    g_xentropy = tf.nn.sigmoid_cross_entropy_with_logits(
        logits=d_fake,
        labels=tf.ones_like(d_fake))

    g_loss = tf.reduce_mean(g_xentropy)
    return d_loss, g_loss, d_left_term, d_right_term


def wasserstein(d_fake, d_real, derivative=None, lda=10, epsilon=1e-10, target=1.):
    """
    Wasserstein distance as in Arjosky et al 2017:
            J(D, G) = 1/m * sum {f(x)} - 1/m * sum {f(G(z))}
    Gradient Penalty as in Gulrajani et al 2017:
            J(D, G) + ƛ * 1/m * {l2_norm[d f(r) / d r] - 1}**2
        where r = G(z), f does not produce interval (0, 1)
    """
    fake_loss = tf.reduce_mean(d_fake)
    real_loss = tf.reduce_mean(d_real)
    d_loss = fake_loss - real_loss
    # minimize {- 1/m * sum f(G(z))}
    g_loss = - tf.reduce_mean(d_fake)
    if derivative is not None:
        gradient_squares = tf.reduce_sum(tf.square(derivative), axis=list(range(1, derivative.shape.ndims)))
        slopes = tf.sqrt(gradient_squares + epsilon)
        penalties = slopes / target - 1.0
        penalties_squared = lda * tf.reduce_mean(tf.square(penalties))
        d_loss += penalties_squared
    return d_loss, g_loss, fake_loss, real_loss


def wasserstein_penalty(disc_fake, disc_real, fake_data, real_data, discriminator_fn, batch_size, l=1):
    disc_cost = tf.reduce_mean(disc_fake) - tf.reduce_mean(disc_real)

    # Gradient Penalty
    alpha = tf.random_uniform(shape=[batch_size, 1],
                              minval=0.,
                              maxval=1., name='alpha')
    differences = fake_data - real_data
    interpolates = real_data + (alpha * differences)
    gradients = tf.gradients(discriminator_fn(interpolates), [interpolates])[0]
    slopes = tf.sqrt(tf.reduce_sum(tf.square(gradients), reduction_indices=[1]))
    gradient_penalty = l * tf.reduce_mean((slopes - 1.) ** 2)
    disc_cost += gradient_penalty
    return disc_cost, gradient_penalty


# def wasserstein_penalty_2(disc_fake, disc_real, fake_data, real_data, discriminator_fn, batch_size, l=1):
#     disc_cost = tf.reduce_mean(disc_fake) - tf.reduce_mean(disc_real)
#
#     # Gradient Penalty
#     alpha = tf.random_uniform(shape=[batch_size, 1],
#                               minval=0.,
#                               maxval=1., name='alpha')
#     interpolated = alpha * real_data + (1 - alpha) * fake_data
#     d_penalty_logits = discriminator_fn(interpolated)
#     derivative, = tf.gradients(d_penalty_logits, [interpolated])
#     gradient_squares = tf.reduce_sum(tf.square(derivative), axis=list(range(1, derivative.shape.ndims)))
#     slopes = tf.sqrt(gradient_squares + epsilon)
#     penalties = slopes / target - 1.0
#     penalties_squared = tf.reduce_mean(tf.square(penalties))
#
#     penalty = losses.compute_weighted_loss(
#         penalties_squared, weights, scope=scope,
#         loss_collection=loss_collection, reduction=reduction)
#     return disc_cost, gradient_penalty

@in_session
def _mpi_adam():
    import numpy as np
    """
    tests the MpiAdam object's functionality
    """
    np.random.seed(0)
    tf.set_random_seed(0)

    a_var = tf.Variable(np.array([0] * 10).astype('float32'))
    b_var = tf.Variable(np.array([5] * 10).astype('float32'))
    print("A: {} B: {}".format(a_var, b_var))
    # loss = tf.reduce_sum(tf.square(a_var)) + tf.reduce_sum(tf.sin(b_var))
    loss = wasserstein_generator_loss(a_var)
    # loss,_,_,_,_,_ = crossentropy_loss(a_var, b_var)
    # _,loss,_,_= goodfellow_loss(a_var, b_var)

    learning_rate = 1e-2
    rng = 2
    update_op = tf.train.AdamOptimizer(learning_rate).minimize(loss)
    do_update = tf_utils.function([], loss, updates=[update_op])

    tf.get_default_session().run(tf.global_variables_initializer())
    adamOpt = []
    print("Run AdamOptimizer")
    for step in range(rng):
        # print(step, do_update())
        adamOpt.append(do_update())

    tf.set_random_seed(0)
    tf.get_default_session().run(tf.global_variables_initializer())

    var_list = [a_var, b_var]
    lossandgrad = tf_utils.function([], [loss, tf_utils.flatgrad(loss, var_list)])
    adam = MpiAdam(var_list)
    adam_res = []
    print("\nRun MpiAdam")
    for step in range(rng):
        loss, grad = lossandgrad()
        adam.update(grad, learning_rate)
        adam_res.append(loss)
        # print(step, loss)

    print("AdamOptimizer: Adam")
    for i in range(len(adamOpt)):
        print("{}:{}".format(adamOpt[i], adam_res[i]))


if __name__ == "__main__":
    # Run with mpirun -np 2 python <filename>
    _mpi_adam()
