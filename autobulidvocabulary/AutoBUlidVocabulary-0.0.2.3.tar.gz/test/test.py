#encoding=utf-8
from __future__ import unicode_literals
import sys
sys.path.append("../")
from AutoBUlidVocabulary import Vocab

word_list=["哈士奇","狗子",'niub']
vocab=Vocab()


vocab_list=vocab.get_vectorizer(word_list)
print(vocab_list)

# vocab_list=vocab.add_vectorizer(word_list)
# print(vocab_list)


c= vocab.text_voc_ids("猫喜欢吃什么")
print(c)
