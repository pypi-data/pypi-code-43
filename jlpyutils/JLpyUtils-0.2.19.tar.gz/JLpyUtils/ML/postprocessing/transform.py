
class one_hot():
    def prob_to_class_transform(y_probs, prob_threshold = 0.5 ):
        """
        Transform a one-hot encoded style numpy array of probablities into 0, 1 class IDs
        """
        for i in range(y_probs.shape[1]):
            y_probs[:,i][y_probs[:,i]>=prob_threshold] = 1
            y_probs[:,i][y_probs[:,i]<prob_threshold] = 0
        return y_probs