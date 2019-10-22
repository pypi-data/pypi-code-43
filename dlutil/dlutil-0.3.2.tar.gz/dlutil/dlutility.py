import torch
import torch.nn as nn

__all__ = ['safe_div', 'scaled_dot_product_attention',
           'positional_encoding', 'create_mask', 'pointwise_dense_network']


def safe_div(x, y):
    return torch.where(y != 0, x / y, torch.zeros_like(x))


def scaled_dot_product_attention(q, k, v, mask):
    matmul_qk = torch.matmul(q, k.transpose(-1, -2))
    dk = torch.ones([], dtype=torch.float32, device=q.device) * k.size(-1)
    scaled_attention_logits = (matmul_qk / torch.sqrt(dk))
    if mask is not None:
        scaled_attention_logits += mask * -1e9
    attention_weights = torch.softmax(scaled_attention_logits, dim=-1)
    output = torch.matmul(attention_weights, v)
    return output, attention_weights


def positional_encoding(min_rate, maximum_position_encoding, dimensions, device=None):
    assert dimensions % 2 == 0, 'Model dimensions must be even!'
    positions = torch.arange(
        maximum_position_encoding, dtype=torch.float32, device=device)
    dim_positions = torch.arange(
        dimensions, dtype=torch.float32, device=device)
    angle_rates = min_rate ** (2 * (dim_positions // 2) / dimensions)
    angle_rads = positions.unsqueeze(-1) * angle_rates.unsqueeze(0)
    sines = torch.sin(angle_rads[:, 0::2])
    cosines = torch.cos(angle_rads[:, 1::2])
    pos_encoding = torch.cat([sines, cosines], dim=-1)[None]
    return pos_encoding


def create_mask(seq, mode=0):
    '''
    mode: 0 for no mask, 1 for padding mask, 2 for looking-ahead mask
    '''
    if mode == 0:
        mask = torch.ones_like(seq, dtype=torch.float32)
        return mask.reshape(seq.size(0), 1, 1, seq.size(1))
    else:
        padding_mask = (seq == 0).type(torch.float32)
        padding_mask = padding_mask.reshape(seq.size(0), 1, 1, seq.size(1))
        if mode == 1:
            mask = padding_mask
        elif mode == 2:
            mere_look_ahead_mask = torch.triu(torch.ones(
                seq.size(1), seq.size(1), dtype=torch.float32, device=seq.device), 1)
            mask = torch.where(
                mere_look_ahead_mask > padding_mask, mere_look_ahead_mask, padding_mask)
        else:
            raise ValueError(f'mode should only be 0, 1, 2')
        return mask


def pointwise_dense_network(in_features, dff, d_model):
    network = nn.Sequential(
        nn.Linear(in_features, dff),
        nn.ReLU(),
        nn.Linear(dff, d_model)
    )
    return network
