import torch


def get_last_rnn_state(padded_seq, length):
    masks = (length-1).view(1, -1, 1).expand(torch.max(length), padded_seq.size(1), padded_seq.size(2))
    return padded_seq.gather(0, masks)[0]
