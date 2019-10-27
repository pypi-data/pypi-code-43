import tensorflow as tf

class MultiLabelMacroRecall(tf.keras.metrics.Metric):
    def __init__(
        self, name='multi_label_macro_recall',
        threshold=0.5, from_logits=True, activation='sigmoid',
        **kwargs
    ):
        super(MultiLabelMacroRecall, self).__init__(name=name, **kwargs)
        self.threshold       = tf.constant(threshold)
        self.from_logits     = from_logits
        self.activation      = activation
        self.recall = self.add_weight(name='mlm_recall', initializer='zeros')
        self.true_positives  = self.add_weight(name='tp', initializer='zeros')
        self.false_positives = self.add_weight(name='fp', initializer='zeros')

    def update_state(self, y_true, y_pred):
        y_pred = tf.cond(
            tf.equal(self.from_logits, False), y_pred,
            tf.cond(
                tf.equal(self.activation, 'sigmoid'),
                tf.sigmoid(y_pred),
                y_pred
            )
        )

        # Compare predictions and threshold.
        pred_is_pos  = tf.greater(tf.cast(y_pred, tf.float32), self.threshold)
        label_is_pos = tf.greater(tf.cast(y_true, tf.float32), self.threshold)
        label_is_neg = tf.logical_not(tf.cast(label_is_pos, tf.bool))

        self.true_positives.assign_add(
            tf.reduce_sum(tf.cast(tf.logical_and(pred_is_pos, label_is_pos), tf.float32))
        )
        self.false_positives.assign_add(
            tf.reduce_sum(tf.cast(tf.logical_and(pred_is_pos, label_is_neg), tf.float32))
        )

        tp = self.true_negatives
        fp = self.false_positives
        recall = tf.div_no_nan(tp, tf.add(tp, fp))
        self.recall.assign(recall)
        return recall

    def result(self):
        return self.recall



class MultiLabelMacroSpecificity(tf.keras.metrics.Metric):

    def __init__(
        self, name='multi_label_macro_specificity',
        threshold=0.5, from_logits=True, activation='sigmoid',
        **kwargs
    ):
        super(MultiLabelMacroSpecificity, self).__init__(name=name, **kwargs)
        self.threshold       = tf.constant(threshold)
        self.from_logits     = from_logits
        self.activation      = activation

        self.specificity = self.add_weight(name='mlm_spec', initializer='zeros')
        self.true_negatives  = self.add_weight(name='tn', initializer='zeros')
        self.false_positives = self.add_weight(name='fp', initializer='zeros')

    def update_state(self, y_true, y_pred):
        y_pred = tf.cond(
            tf.equal(self.from_logits, False), y_pred,
            tf.cond(
                tf.equal(self.activation, 'sigmoid'),
                tf.sigmoid(y_pred),
                y_pred
            )
        )

        # Compare predictions and threshold.
        pred_is_pos  = tf.greater(tf.cast(y_pred, tf.float32), self.threshold)
        pred_is_neg  = tf.logical_not(tf.cast(pred_is_pos, tf.bool))
        label_is_pos = tf.greater(tf.cast(y_true, tf.float32), self.threshold)
        label_is_neg = tf.logical_not(tf.cast(label_is_pos, tf.bool))

        self.true_negatives.assign_add(
            tf.reduce_sum(tf.cast(tf.logical_and(pred_is_neg, label_is_neg), tf.float32))
        )
        self.false_positives.assign_add(
            tf.reduce_sum(tf.cast(tf.logical_and(pred_is_pos, label_is_neg), tf.float32))
        )

        tn = self.true_negatives
        fp = self.false_positives
        specificity = tf.div_no_nan(tn, tf.add(tn, fp))
        self.specificity.assign(specificity)
        return specificity

    def result(self):
        return self.specificity

class MultiLabelMacroSensitivity(tf.keras.metrics.Metric):

    def __init__(
        self, name='multi_label_macro_sensitivity',
        threshold=0.5, from_logits=True, activation='sigmoid',
        **kwargs
    ):
        super(MultiLabelMacroSensitivity, self).__init__(name=name, **kwargs)
        self.threshold       = tf.constant(threshold)
        self.from_logits     = from_logits
        self.activation      = activation

        self.sensitivity = self.add_weight(name='mlm_sens', initializer='zeros')
        self.true_positives  = self.add_weight(name='tp', initializer='zeros')
        self.false_negatives = self.add_weight(name='fn', initializer='zeros')

    def update_state(self, y_true, y_pred):
        y_pred = tf.cond(
            tf.equal(self.from_logits, False), y_pred,
            tf.cond(
                tf.equal(self.activation, 'sigmoid'),
                tf.sigmoid(y_pred),
                y_pred
            )
        )

        # Compare predictions and threshold.
        pred_is_pos  = tf.greater(tf.cast(y_pred, tf.float32), self.threshold)
        label_is_pos = tf.greater(tf.cast(y_true, tf.float32), self.threshold)

        pred_is_neg  = tf.logical_not(tf.cast(pred_is_pos, tf.bool))
        label_is_neg = tf.logical_not(tf.cast(label_is_pos, tf.bool))

        self.true_positives.assign_add(
            tf.reduce_sum(tf.cast(tf.logical_and(pred_is_pos, label_is_pos), tf.float32))
        )
        self.false_negatives.assign_add(
            tf.reduce_sum(tf.cast(tf.logical_and(pred_is_neg, label_is_pos), tf.float32))
        )

        tp = self.true_positives
        fn = self.false_negatives
        sensitivity = tf.div_no_nan(tp, tf.add(tp, fn))
        self.sensitivity.assign(sensitivity)
        return sensitivity

    def result(self):
        return self.sensitivity
