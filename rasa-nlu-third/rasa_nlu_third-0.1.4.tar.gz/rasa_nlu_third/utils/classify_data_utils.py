# create by fanfan on 2019/9/29 0029

def pad_sentence(words,intention, max_sentence_length,vocabulary,label_dict):
    '''
    对batch中的序列进行补全，保证batch中的每行都有相同的sequence_length

    参数：
    - sentence
    '''
    tokens = words
    if len(tokens) >= max_sentence_length - 1:
        tokens = tokens[0:(max_sentence_length - 2)]

    ntokens = []
    segment_ids = []
    label_id = [label_dict.get(intention)]

    # 加第一个开始字符
    ntokens.append('[CLS]')
    segment_ids.append(0)


    ## 整个句子转换
    for i,token in enumerate(tokens):
        ntokens.append(token)
        segment_ids.append(0)


    # 句尾添加[SEP] 标志
    ntokens.append('[SEP]')
    segment_ids.append(0)



    unk_id = vocabulary.get('[UNK]')
    input_ids = [vocabulary.get(token,unk_id) for token in ntokens]
    input_mask = [1] * len(input_ids)


    while len(input_ids) < max_sentence_length:
        input_ids.append(0)
        input_mask.append(0)
        segment_ids.append(0)

        ntokens.append("**NULL**")

    assert len(input_ids) == max_sentence_length
    assert len(input_mask) == max_sentence_length
    assert len(segment_ids) == max_sentence_length


    return input_ids,label_id,segment_ids,input_mask