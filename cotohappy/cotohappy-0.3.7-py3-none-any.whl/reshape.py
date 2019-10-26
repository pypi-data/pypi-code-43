#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 20 12:00:00 2019

COTOHA API for Python3.8
@author: Nicolas Toba Nozomi
@id: 278mt
"""

from cotohappy.translate import Translate

class Reshape(object):

    def __init__(self, mode: str, data: dict or list, translate: bool=False):

        self.data = data
        tl = Translate()

        if mode == 'parse':
            chunk_info = data['chunk_info']
            self.id_        = chunk_info['id']
            self.head       = chunk_info['head']
            self.dep        = chunk_info['dep']
            self.chunk_head = chunk_info['chunk_head']
            self.chunk_func = chunk_info['chunk_func']
            self.links      = [
                Reshape('links', link, translate)
                for link in chunk_info['links']
            ]
            self.predicate  = chunk_info['predicate'] if 'predicate' in chunk_info else []

            self.tokens     = [
                Reshape('tokens', token, translate)
                for token in data['tokens']
            ]

            # translate
            if translate:
                self.dep       = tl.dep_list(self.dep)
                self.predicate = [part for part in self.predicate]

            len_predicate = len(self.predicate)

            self.form = ''.join(map(lambda token: token.form, self.tokens))
            self.key_name   = 'form\t id,head,dep,chunk_head,chunk_func,predicate[:5]'
            self.result_str = '{}\t {},{},{},{},{},{},{},{},{},{}'.format(
                self.form,
                self.id_,
                self.head,
                self.dep,
                self.chunk_head,
                self.chunk_func,
                *[self.predicate[i] if len_predicate > i else '*' for i in range(5)]
            )

        elif mode == 'links':
            self.link  = data['link']
            self.label = data['label']

            # translate
            if translate:
                self.label = tl.semantic_role_label_list(self.label)

            self.key_name   = 'link,label'
            self.result_str = '{},{}'.format(
                self.link,
                self.label
            )

        elif mode == 'tokens':
            self.id_               = data['id']
            self.form              = data['form']
            self.kana              = data['kana']
            self.lemma             = data['lemma']
            self.pos               = data['pos']
            self.features          = data['features']
            self.dependency_labels = [
                Reshape('dependency_labels', dependency_label, translate)
                for dependency_label in data['dependency_labels']
            ] if 'dependency_labels' in data else []
            self.attribute         = data['attribute'] if 'attribute' in data else '*'

            # translate
            if translate:
                self.pos      = tl.speech_parts_list(self.pos)
                self.features = [tl.features_list(self.pos, feature) for feature in self.features]

            len_features = len(self.features)

            self.key_name   = 'form\t id,kana,lemma,pos,features[:5]'
            self.result_str = '{}\t {},{},{},{},{},{},{},{},{}'.format(
                self.form,
                self.id_,
                self.kana,
                self.lemma,
                self.pos,
                *[self.features[i] if len_features > i else '*' for i in range(5)]
            )

        elif mode == 'dependency_labels':
            self.token_id = data['token_id']
            self.label    = data['label']

            self.key_name   = 'token_id,label'
            self.result_str = '{},{}'.format(
                self.token_id,
                self.label
            )

        elif mode == 'ne':
            self.form           = data['form']
            self.begin_pos      = data['begin_pos']
            self.end_pos        = data['end_pos']
            self.std_form       = data['std_form']
            self.class_         = data['class']
            self.extended_class = data['extended_class']
            self.info           = data['info'] if 'info' in data else '*'
            self.source         = data['source']

            # translate
            if translate:
                self.class_ = self.ne_class_list(self.class_)
                self.extended_class = self.extended_ne_class_list(self.extended_class)

            self.key_name   = 'form\t begin_pos,end_pos,std_form,class,extended_class,info,source'
            self.result_str = '{}\t {},{},{},{},{},{},{}'.format(
                self.form,
                self.begin_pos,
                self.end_pos,
                self.std_form,
                self.class_,
                self.extended_class,
                self.info,
                self.source
            )

        elif mode == 'coreference':
            self.coreference = [
                Reshape('content', content, translate)
                for content in data['coreference']
            ]
            self.tokens      = data['tokens']

            self.key_name   = 'None'
            self.result_str = '<called Reshape on coreference>'


        elif mode == 'content':
            self.representative_id = data['representative_id']
            self.referents         = [
                Reshape('referents', referent, translate)
                for referent in data['referents']
            ]

            self.key_name   = 'representative_id'
            self.result_str = '{}'.format(
                self.representative_id
            )

        elif mode == 'referents':
            self.form          = data['form']
            self.referent_id   = data['referent_id']
            self.sentence_id   = data['sentence_id']
            self.token_id_from = data['token_id_from']
            self.token_id_to   = data['token_id_to']

            self.key_name   = 'form\t referent_id,sentence_id,token_id_from,token_id_to'
            self.result_str = '{}\t {},{},{},{}'.format(
                self.form,
                self.referent_id,
                self.sentence_id,
                self.token_id_from,
                self.token_id_to
            )

        elif mode == 'keyword':
            self.form  = data['form']
            self.score = data['score']

            self.key_name   = 'form\t score'
            self.result_str = '{}\t {}'.format(
                self.form,
                self.score
            )

        elif mode == 'similarity':
            self.score = data['score']

            self.key_name   = 'score'
            self.result_str = '{}'.format(
                self.score
            )

        elif mode == 'sentence_type':
            self.modality   = data['modality']
            self.dialog_act = data['dialog_act']

            # translate
            if translate:
                self.dialog_act = [tl.speech_act_list(part) for part in self.dialog_act]

            len_dialog_act = len(self.dialog_act)

            self.key_name   = 'modality\t dialog_act[:5]'
            self.result_str = '{}\t {},{},{},{},{}'.format(
                self.modality,
                *[self.dialog_act[i] if len_dialog_act > i else '*' for i in range(5)]
            )

        elif mode == 'sentiment':
            self.sentiment        = data['sentiment']
            self.score            = data['score']
            self.emotional_phrase = [
                Reshape('emotional_phrase', content, translate)
                for content in data['emotional_phrase']
            ]

            self.key_name   = 'sentiment,score'
            self.result_str = '{},{}'.format(
                self.sentiment,
                self.score
            )

        elif mode == 'emotional_phrase':
            self.form    = data['form']
            self.emotion = data['emotion'].split(',')

            len_emotion = len(self.emotion)

            self.key_name   = 'form\t emotion[:5]'
            self.result_str = '{}\t {},{},{},{},{}'.format(
                self.form,
                *[self.emotion[i] if len_emotion > i else '*' for i in range(5)]
            )

        elif mode == 'user_attribute':
            self.age                = data['age']                if 'age'                in data else '*'
            self.civilstatus        = data['civilstatus']        if 'civilstatus'        in data else '*'
            self.earnings           = data['earnings']           if 'earnings'           in data else '*'
            self.gender             = data['gender']             if 'gender'             in data else '*'
            self.habit              = data['habit']              if 'habit'              in data else '*'
            self.hobby              = data['hobby']              if 'hobby'              in data else '*'
            self.kind_of_bussiness  = data['kind_of_bussiness']  if 'kind_of_bussiness'  in data else '*'
            self.kind_of_occupation = data['kind_of_occupation'] if 'kind_of_occupation' in data else '*'
            self.location           = data['location']           if 'location'           in data else '*'
            self.moving             = data['moving']             if 'moving'             in data else '*'
            self.occupation         = data['occupation']         if 'occupation'         in data else '*'
            self.position           = data['position']           if 'position'           in data else '*'

            len_habit  = len(self.habit)
            len_hobby  = len(self.hobby)
            len_moving = len(self.moving)

            self.key_name   = 'age,civilstatus,earnings,gender,kind_of_bussiness,kind_of_occupation,location,position,habit[:2],hobby[:5],moving[:5]'
            self.result_str = '{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}'.format(
                self.age,
                self.civilstatus,
                self.earnings,
                self.gender,
                self.kind_of_bussiness,
                self.kind_of_occupation,
                self.location,
                self.occupation,
                self.position,
                *[self.habit[i]  if len_habit  > i else '*' for i in range(2)],
                *[self.hobby[i]  if len_hobby  > i else '*' for i in range(5)],
                *[self.moving[i] if len_moving > i else '*' for i in range(2)]
            )

        elif mode == 'remove_filler':
            self.fillers             = [
                Reshape('filler', filler, translate)
                for filler in data['fillers']
            ]
            self.normalized_sentence = data['normalized_sentence']
            self.fixed_sentence      = data['fixed_sentence']

            self.key_name   = 'normalized_sentence\t fixed_sentence'
            self.result_str = '{}\t {}'.format(
                self.normalized_sentence,
                self.fixed_sentence
            )

        elif mode == 'filler':
            self.form      = data['form']
            self.begin_pos = data['begin_pos']
            self.end_pos   = data['end_pos']

            self.key_name   = 'form\t begin_pos,end_pos'
            self.result_str = '{}\t {},{}'.format(
                self.form,
                self.begin_pos,
                self.end_pos
            )


        elif mode == 'detect_misrecognition':
            self.candidates = [
                Reshape('candidate', candidate, translate)
                for candidate in data['candidates']
            ]
            self.score      = data['score']

            self.key_name   = 'score'
            self.result_str = '{}'.format(
                self.score
            )

        elif mode == 'candidate':
            self.form         = data['form']
            self.begin_pos    = data['begin_pos']
            self.end_pos      = data['end_pos']
            self.detect_score = data['detect_score']
            self.correction   = [
                Reshape('correction', content, translate)
                for content in data['correction']
            ]

            len_correction = len(self.correction)

            self.key_name   = 'form\t begin_pos,end_pos,detect_score,correct_score[:5]'
            self.result_str = '{}\t {},{},{},{},{},{},{},{}'.format(
                self.form,
                self.begin_pos,
                self.end_pos,
                self.detect_score,
                *[self.correction[i].form if len_correction > i else '*' for i in range(5)]
            )

        elif mode == 'correction':
            self.form          = data['form']
            self.correct_score = data['correct_score']

            self.key_name   = 'form\t correct_score'
            self.result_str = '{}\t {}'.format(
                self.form,
                self.correct_score
            )

        else:
            self.result_str = 'TEST Reshape'


    def __str__(self):

        return self.result_str

