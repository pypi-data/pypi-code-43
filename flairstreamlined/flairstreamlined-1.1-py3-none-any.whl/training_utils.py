from typing import List
from flair.data import Sentence

def store_embeddings(sentences: List[Sentence], storage_mode: str):

    # if memory mode option 'none' delete everything
    if storage_mode == "none":
        for sentence in sentences:
            sentence.clear_embeddings()

    # else delete only dynamic embeddings (otherwise autograd will keep everything in memory)
    else:
        # find out which ones are dynamic embeddings
        delete_keys = []
        for name, vector in sentences[0][0]._embeddings.items():
            if sentences[0][0]._embeddings[name].requires_grad:
                delete_keys.append(name)

        # find out which ones are dynamic embeddings
        for sentence in sentences:
            sentence.clear_embeddings(delete_keys)

    # memory management - option 1: send everything to CPU
    if storage_mode == "cpu":
        for sentence in sentences:
            sentence.to("cpu")
