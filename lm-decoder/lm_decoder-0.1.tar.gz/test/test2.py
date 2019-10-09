import torch
import lm_decoder

vocab, probs, gates, masks = torch.load('/private/home/jgu/work/test2.pt')
print(len(vocab))
print(probs.size(), masks.size())

# i = 61
KenLM = lm_decoder.KenLMDecoder(vocab, '/private/home/jgu/data/wmt16/en-de/lm/lm.train.bpe.4gram.de.bin')
# print(logits[i])
# print(nbest[i])
# print(masks[i])
for i in range(probs.size(0)):
    print(i)
    scores, seqs = KenLM.beam_search_with_language_model(
                    probs[i:i+1], gates[i:i+1], masks[i:i+1], 30, 10, type='shallow')
    print(scores)
    print(seqs[0, :, :10])
    print(masks[i])
    break
print('done')