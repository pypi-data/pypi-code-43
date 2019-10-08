import numpy as np

def dice_score(prob, truth, threshold=0.5):
    num = prob.shape[0]
    # prob = np.squeeze(prob)

    prob = prob > threshold
    truth = truth > 0.5

    prob = prob.reshape(num, -1)
    truth = truth.reshape(num, -1)
    intersection = (prob * truth)

    score = (2. * (intersection.sum(1) + 1.)) / (prob.sum(1) + truth.sum(1) + 2.)
    score[score >= 1] = 1
    score = score.sum() / num

    return score


def iou(preds, targets, thresh=0.5):
    '''
    for np.argmax(preds) to get answer
    :param preds: N * C * H * W, ndarray
    :param targets: N * H * W, ndarray
    :return:
    '''
    n_classes = preds.shape[1]
    confusion_matrix = np.zeros((n_classes, n_classes))

    if n_classes == 1:
        preds = preds > thresh
    else:
        preds = np.transpose(preds, [0, 2, 3, 1])
        preds = np.argmax(preds, axis=-1)

    for lt, lp in zip(targets, preds):
        confusion_matrix += fast_hist(lt.flatten(), lp.flatten(), n_classes)
    return get_scores(confusion_matrix, n_classes)[3]


def fast_hist(label_true, label_pred, n_class):
    mask = (label_true >= 0) & (label_true < n_class)
    hist = np.bincount(
        n_class * label_true[mask].astype(int) +
        label_pred[mask], minlength=n_class**2).reshape(n_class, n_class)

    return hist


def get_scores(confusion_matrix, n_classes):
        """Returns accuracy score evaluation result.
            - overall accuracy
            - mean accuracy
            - mean IU
            - fwavacc
        """
        hist = confusion_matrix
        acc = np.diag(hist).sum() / hist.sum()
        acc_cls = np.diag(hist) / hist.sum(axis=1)
        acc_cls = np.nanmean(acc_cls)
        iu = np.diag(hist) / (hist.sum(axis=1) + hist.sum(axis=0) - np.diag(hist))
        mean_iu = np.nanmean(iu)
        freq = hist.sum(axis=1) / hist.sum()
        fwavacc = (freq[freq > 0] * iu[freq > 0]).sum()
        cls_iu = dict(zip(range(n_classes), iu))

        return acc, acc_cls, fwavacc, mean_iu, cls_iu
