import torch
import warnings
import torch.nn.functional as F
from torch import nn
from torch.nn.utils.rnn import pack_padded_sequence, pad_packed_sequence

def dropout_mask(x, sz, p):
    """ we pass size in so that we get nice broadcasting along the sequence
    in RNNDropout"""
    return x.new(*sz).bernoulli_(1-p).div_(1-p)

class RNNDropout(nn.Module):
    """
    Note the way size is passed in the forward function: we insert a 3rd
    dimension in between the width and height of the minibatch:
    (x.size(0), 1, x.size(2)).
    The middle dimension is the sequence dimension, so the zeroed-out positions
    will stay the same along the sequence, i.e., througout the bptt sequence.
    """
    def __init__(self, p=0.5):
        super().__init__()
        self.p=p

    def forward(self, x):
        if not self.training or self.p == 0.: return x
        m = dropout_mask(x.data, (x.size(0), 1, x.size(2)), self.p)
        return x * m

WEIGHT_HH = 'weight_hh_l0'

class WeightDropout(nn.Module):
    """
    Dropout to the weights (not activations!) of the inner LSTM hidden to hidden
    matrix.
    We want to preserve the CuDNN speed and not reimplement the cell from scratch,
    so in __init__, we add a parameter that will contain the raw weights:
    self.register_parameter(f'{layer}_raw', nn.Parameter(w.data)).
    We then replace the weight matrix in the LSTM in forward when we call:
    self._setweights()
    """
    def __init__(self, module, weight_p=[0.], layer_names=[WEIGHT_HH]):
        super().__init__()
        self.module,self.weight_p,self.layer_names = module,weight_p,layer_names
        for layer in self.layer_names:
            #Makes a copy of the weights of the selected layers.
            w = getattr(self.module, layer)
            self.register_parameter(f'{layer}_raw', nn.Parameter(w.data))
            # we dropout on the actual weights below
            self.module._parameters[layer] = F.dropout(w, p=self.weight_p, training=False)

    def _setweights(self):
        for layer in self.layer_names:
            raw_w = getattr(self, f'{layer}_raw')
            self.module._parameters[layer] = F.dropout(raw_w, p=self.weight_p, training=self.training)

    def forward(self, *args):
        self._setweights()
        with warnings.catch_warnings():
            #To avoid the warning that comes because the weights aren't flattened.
            warnings.simplefilter("ignore")
            return self.module.forward(*args)

class EmbeddingDropout(nn.Module):
    """
    Applies dropout in the embedding layer by zeroing out some elements of
    the embedding vector.
    Importantly, this applies dropout to full rows of the embedding matrix,
    that is, we drop out entire words and not components of a word's dense
    embedding.
    """
    def __init__(self, emb, embed_p):
        super().__init__()
        self.emb,self.embed_p = emb,embed_p
        self.pad_idx = self.emb.padding_idx
        if self.pad_idx is None: self.pad_idx = -1

    def forward(self, words, scale=None):
        if self.training and self.embed_p != 0:
            size = (self.emb.weight.size(0),1)
            mask = dropout_mask(self.emb.weight.data, size, self.embed_p)
            masked_embed = self.emb.weight * mask
        else: masked_embed = self.emb.weight
        if scale: masked_embed.mul_(scale)
        return F.embedding(words, masked_embed, self.pad_idx, self.emb.max_norm,
                           self.emb.norm_type, self.emb.scale_grad_by_freq, self.emb.sparse)

def to_detach(h):
    "Detaches h from its gradient history."
    return h.detach() if type(h) == torch.Tensor else tuple(to_detach(v) for v in h)

class AWD_LSTM(nn.Module):
    "AWD-LSTM inspired by https://arxiv.org/abs/1708.02182."
    initrange=0.1

    def __init__(self, vocab_sz, emb_sz, n_hid, n_layers, pad_token,
                 hidden_p=0.2, input_p=0.6, embed_p=0.1, weight_p=0.5):
        super().__init__()
        self.bs = 1
        self.emb_sz = emb_sz
        self.n_hid = n_hid
        self.n_layers = n_layers
        self.emb = nn.Embedding(vocab_sz, emb_sz, padding_idx=pad_token)
        self.emb_dp = EmbeddingDropout(self.emb, embed_p)
        # we create n_layers of LSTMs below
        self.rnns = [nn.LSTM(emb_sz if l == 0 else n_hid, (n_hid if l != n_layers-1 else emb_sz), 1, batch_first=True)
                     for l in range(n_layers)]
        # we add dropout to the LSTM layers
        self.rnns = nn.ModuleList([WeightDropout(rnn, weight_p) for rnn in self.rnns])
        self.emb.weight.data.uniform_(-self.initrange, self.initrange)
        self.input_dp = RNNDropout(input_p)
        self.hidden_dps = nn.ModuleList([RNNDropout(hidden_p) for l in range(n_layers)])

    def forward(self, input):
        bs, sl = input.size()
        if bs != self.bs:
            self.bs = bs
            self.reset()
        raw_output = self.input_dp(self.emb_dp(input))
        new_hidden, raw_outputs, outputs = [], [], []
        # we loop through the LSTM layers (plus the hidden dropout layers)
        for l, (rnn, hid_dp) in enumerate(zip(self.rnns, self.hidden_dps)):
            raw_output, new_h = rnn(raw_output, self.hidden[l])
            new_hidden.append(new_h)
            raw_outputs.append(raw_output)
            # we do hidden dropout for all layers but the last one
            if l != self.n_layers - 1: raw_output = hid_dp(raw_output)
            outputs.append(raw_output)
        self.hidden = to_detach(new_hidden)
        return raw_outputs, outputs

    def _one_hidden(self, l):
        "Return one hidden state."
        nh = self.n_hid if l != self.n_layers - 1 else self.emb_sz
        return next(self.parameters()).new(1, self.bs, nh).zero_()

    def reset(self):
        "Reset the hidden states."
        self.hidden = [(self._one_hidden(l), self._one_hidden(l))
                       for l in range(self.n_layers)]

class LinearDecoder(nn.Module):
    """
    We add a top layer to the AWD LSTM. This is a linear model with a dropout.
    """
    def __init__(self, n_out, n_hid, output_p, tie_encoder=None, bias=True):
        super().__init__()
        self.output_dp = RNNDropout(output_p)
        self.decoder = nn.Linear(n_hid, n_out, bias=bias)
        if bias:
            self.decoder.bias.data.zero_()
        if tie_encoder:
            self.decoder.weight = tie_encoder.weight
        else:
            init.kaiming_uniform_(self.decoder.weight)

    def forward(self, input):
        raw_outputs, outputs = input
        # we call dropout first
        output = self.output_dp(outputs[-1]).contiguous()
        # we call the linear model
        decoded = self.decoder(output.view(output.size(0)*output.size(1),
                                           output.size(2)))
        return decoded, raw_outputs, outputs

class SequentialRNN(nn.Sequential):
    "A sequential module that passes the reset call to its children."
    def reset(self):
        for c in self.children():
            if hasattr(c, 'reset'): c.reset()

def get_language_model(vocab_sz, emb_sz, n_hid, n_layers, pad_token,
                       output_p=0.4, hidden_p=0.2, input_p=0.6,
                       embed_p=0.1, weight_p=0.5, tie_weights=True, bias=True):
    rnn_enc = AWD_LSTM(vocab_sz, emb_sz, n_hid=n_hid, n_layers=n_layers,
                       pad_token=pad_token, hidden_p=hidden_p, input_p=input_p,
                       embed_p=embed_p, weight_p=weight_p)
    enc = rnn_enc.emb if tie_weights else None
    # the rnn_enc is the AWD LSTM
    # its output is passed to the top linear layer (with dropout)
    return SequentialRNN(rnn_enc,
                         LinearDecoder(vocab_sz, emb_sz, output_p,
                                       tie_encoder=enc, bias=bias))

def lm_splitter(m):
    """
    Splits the language model provided by the get_language_model into multiple
    param groups to do transfer learning (e.g., from Wikipedia to IMDB):
    -- we have one group for each rnn + corresponding dropout (for a
    total of 2 if we had 2 n_layers in the get_language_model call)
    -- we have one last group that contains the embeddings/decoder.
    The last group needs to be trained the most (new embeddings vectors).
    """
    groups = []
    for i in range(len(m[0].rnns)):
        groups.append(nn.Sequential(m[0].rnns[i], m[0].hidden_dps[i]))
    groups += [nn.Sequential(m[0].emb, m[0].emb_dp, m[0].input_dp, m[1])]
    return [list(o.parameters()) for o in groups]

class AWD_LSTM1(nn.Module):
    """
    AWD-LSTM inspired by https://arxiv.org/abs/1708.02182,
    updated to deal with pad_packed_sequence and pack_padded_sequence.
    """
    initrange=0.1

    def __init__(self, vocab_sz, emb_sz, n_hid, n_layers, pad_token,
                 hidden_p=0.2, input_p=0.6, embed_p=0.1, weight_p=0.5):
        super().__init__()
        self.bs = 1
        self.emb_sz = emb_sz
        self.n_hid = n_hid
        self.n_layers = n_layers
        self.pad_token = pad_token
        self.emb = nn.Embedding(vocab_sz, emb_sz, padding_idx=pad_token)
        self.emb_dp = EmbeddingDropout(self.emb, embed_p)
        self.rnns = [nn.LSTM(emb_sz if l == 0 else n_hid, (n_hid if l != n_layers - 1 else emb_sz), 1, batch_first=True)
                     for l in range(n_layers)]
        self.rnns = nn.ModuleList([WeightDropout(rnn, weight_p)
                                   for rnn in self.rnns])
        self.emb.weight.data.uniform_(-self.initrange, self.initrange)
        self.input_dp = RNNDropout(input_p)
        self.hidden_dps = nn.ModuleList([RNNDropout(hidden_p)
                                         for l in range(n_layers)])

    def forward(self, input):
        bs, sl = input.size()
        mask = (input == self.pad_token)
        lengths = sl - mask.long().sum(1)
        n_empty = (lengths == 0).sum()
        if n_empty > 0:
            input = input[:-n_empty]
            lengths = lengths[:-n_empty]
            self.hidden = [(h[0][:,:input.size(0)], h[1][:,:input.size(0)])
                           for h in self.hidden]
        raw_output = self.input_dp(self.emb_dp(input))
        new_hidden,raw_outputs,outputs = [],[],[]
        for l, (rnn, hid_dp) in enumerate(zip(self.rnns, self.hidden_dps)):
            # take data of different lengths and shape it to pass to RNN
            raw_output = pack_padded_sequence(raw_output, lengths, batch_first=True)
            raw_output, new_h = rnn(raw_output, self.hidden[l])
            # this is where the padding actually happens
            raw_output = pad_packed_sequence(raw_output, batch_first=True)[0]
            raw_outputs.append(raw_output)
            if l != self.n_layers - 1: raw_output = hid_dp(raw_output)
            outputs.append(raw_output)
            new_hidden.append(new_h)
        self.hidden = to_detach(new_hidden)
        return raw_outputs, outputs, mask

    def _one_hidden(self, l):
        "Return one hidden state."
        nh = self.n_hid if l != self.n_layers - 1 else self.emb_sz
        return next(self.parameters()).new(1, self.bs, nh).zero_()

    def reset(self):
        "Reset the hidden states."
        self.hidden = [(self._one_hidden(l), self._one_hidden(l)) for l in range(self.n_layers)]


# We use three things for the classification head of the model:
# -- the last hidden state
# -- the average of all the hidden states
# -- the maximum of all the hidden states
# Once again, we need to ignore the padding in the last element/average/maximum.

class Pooling(nn.Module):
    """
    The LSTMs create hidden states for bptt time steps. We decide here what to
    pass to the classifier. Following concat pooling from vision, we concatenate:
    -- the final hidden state
    -- the mean (average pool) of all the bptt hidden states
    -- the maxpool of all the bptt hidden states
    We pass the resulting concatenated tensor to the classifier.
    """
    def forward(self, input):
        raw_outputs,outputs,mask = input
        output = outputs[-1]
        lengths = output.size(1) - mask.long().sum(dim=1)
        avg_pool = output.masked_fill(mask[:,:,None], 0).sum(dim=1)
        avg_pool.div_(lengths.type(avg_pool.dtype)[:,None])
        max_pool = output.masked_fill(mask[:,:,None], -float('inf')).max(dim=1)[0]
        x = torch.cat([output[torch.arange(0, output.size(0)),lengths-1], max_pool, avg_pool], 1) #Concat pooling.
        return output,x

def bn_drop_lin(n_in, n_out, bn=True, p=0., actn=None):
    layers = [nn.BatchNorm1d(n_in)] if bn else []
    if p != 0: layers.append(nn.Dropout(p))
    layers.append(nn.Linear(n_in, n_out))
    if actn is not None: layers.append(actn)
    return layers

class PoolingLinearClassifier(nn.Module):
    """
    Create a linear classifier with pooling:
    -- the concat pooling layer, followed by
    -- a list of batchnorm + dropout + linear layers
    """
    def __init__(self, layers, drops):
        super().__init__()
        mod_layers = []
        activs = [nn.ReLU(inplace=True)] * (len(layers) - 2) + [None]
        # list of batchnorm + dropout + linear layers
        for n_in, n_out, p, actn in zip(layers[:-1], layers[1:], drops, activs):
            mod_layers += bn_drop_lin(n_in, n_out, p=p, actn=actn)
        self.layers = nn.Sequential(*mod_layers)

    def forward(self, input):
        raw_outputs,outputs,mask = input
        output = outputs[-1]
        lengths = output.size(1) - mask.long().sum(dim=1)
        avg_pool = output.masked_fill(mask[:,:,None], 0).sum(dim=1)
        avg_pool.div_(lengths.type(avg_pool.dtype)[:,None])
        max_pool = output.masked_fill(mask[:,:,None], -float('inf')).max(dim=1)[0]
        # Concat pooling.
        x = torch.cat([output[torch.arange(0, output.size(0)),lengths-1], max_pool, avg_pool], 1)
        # pass that through the linear layers
        x = self.layers(x)
        return x

def pad_tensor(t, bs, val=0.):
    if t.size(0) < bs:
        return torch.cat([t, val + t.new_zeros(bs-t.size(0), *t.shape[1:])])
    return t

class SentenceEncoder(nn.Module):
    "The encoder is the AWD LSTM model that gets called on the input text."
    def __init__(self, encoder, bptt, pad_idx=1):
        super().__init__()
        self.bptt = bptt
        self.encoder = encoder
        self.pad_idx = pad_idx

    def concat(self, arrs, bs):
        return [torch.cat([pad_tensor(l[si],bs) for l in arrs], dim=1)
                for si in range(len(arrs[0]))]

    def forward(self, input):
        bs, sl = input.size()
        self.encoder.bs = bs
        self.encoder.reset()
        raw_outputs, outputs, masks = [], [], []
        # We go through the input one bptt at a time
        for i in range(0, sl, self.bptt):
            # we call the RNN model on it
            r, o, m = self.encoder(input[:,i: min(i+self.bptt, sl)])
            # we keep appending the results
            masks.append(pad_tensor(m, bs, 1))
            raw_outputs.append(r)
            outputs.append(o)
        return self.concat(raw_outputs, bs), self.concat(outputs, bs),torch.cat(masks,dim=1)

def get_text_classifier(vocab_sz, emb_sz, n_hid, n_layers, n_out, pad_token,
                        bptt, output_p=0.4, hidden_p=0.2, input_p=0.6,
                        embed_p=0.1, weight_p=0.5, layers=None, drops=None):
    "To create a full AWD-LSTM"
    rnn_enc = AWD_LSTM1(vocab_sz, emb_sz, n_hid=n_hid, n_layers=n_layers,
                        pad_token=pad_token, hidden_p=hidden_p, input_p=input_p,
                        embed_p=embed_p, weight_p=weight_p)
    enc = SentenceEncoder(rnn_enc, bptt)
    if layers is None:
        layers = [50]
    if drops is None:
        drops = [0.1] * len(layers)
    layers = [3 * emb_sz] + layers + [n_out]
    drops = [output_p] + drops
    return SequentialRNN(enc, PoolingLinearClassifier(layers, drops))

def class_splitter(m):
    enc = m[0].encoder
    groups = [nn.Sequential(enc.emb, enc.emb_dp, enc.input_dp)]
    for i in range(len(enc.rnns)):
        groups.append(nn.Sequential(enc.rnns[i], enc.hidden_dps[i]))
    groups.append(m[1])
    return [list(o.parameters()) for o in groups]
