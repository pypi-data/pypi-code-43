import torch
from ._ext import lm_decoder


class KenLMDecoder(object):
    def __init__(self, vocab=None, model_path=None):
        self.vocab = vocab
        self.lm_scorer = lm_decoder.get_kenlm_scorer(model_path, vocab)

    def language_model_scores(self, targets, masks, workers=20, n_best=False):
        """
        inputs:
            targets:  batch x seqlen
            masks:    batch x seqlen
        """
        lm_scores = targets.new_zeros(*targets.size()).fill_(-1000).cpu().float()
        lm_scorer = lm_decoder.get_kenlm_nbest_scores if n_best else lm_decoder.get_kenlm_scores

        lm_scorer(self.lm_scorer,
                  targets.cpu().int(),
                  masks.sum(1).cpu().int(), lm_scores, workers)
        if targets.is_cuda:
            lm_scores = lm_scores.cuda(targets.get_device())
        return lm_scores

    def beam_search_with_language_model(self,
                                        log_probs,
                                        seqs,
                                        masks,
                                        alpha=0.8,
                                        beta=0.2,
                                        beam_size=5,
                                        workers=20,
                                        type='moe'):
        """
        inputs:
            probs:     batch x seqlen x candidates
            seqs:      batch x seqlen 
            masks:     batch x seqlen
            type:      moe, shallow, simple
        return:
            best translation
        """
        types = {'moe': 0, 'shallow': 1, 'simple': 2}
        _seqs = seqs.cpu().int()
        _log_probs = log_probs.cpu().float()
        lm_decoder.beam_search(self.lm_scorer,
                                _log_probs, 
                                _seqs,
                                masks.sum(1).cpu().int(), 
                                alpha, beta,
                                beam_size,
                                workers, types[type])
        
        if seqs.is_cuda:
            _seqs = _seqs.cuda(seqs.get_device())
            _log_probs = _log_probs.cuda(seqs.get_device())
        _seqs = _seqs.type_as(seqs)
        _log_probs = _log_probs.type_as(log_probs)
        return _log_probs, _seqs