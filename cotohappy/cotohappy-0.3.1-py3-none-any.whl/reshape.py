#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 20 12:00:00 2019

COTOHA API for Python3.8
@author: Nicolas Toba Nozomi
@id: 278mt
"""


class Reshape(object):

    def __init__(self, mode: str, data: dict or list):

        self.data = data

        if mode == 'parse':
            self.chunk_info = Reshape(mode='chunk_info', data=data['chunk_info'])
            self.tokens     = [
                Reshape(mode='tokens', data=token)
                for token in data['tokens']
            ]

            self.form = ''.join(map(lambda token: token.form, self.tokens))
            self.key_name   = 'form\t id,head,dep,chunk_head,chunk_func'
            self.result_str = '{}\t {},{},{},{},{}'.format(
                self.form,
                self.chunk_info.id_,
                self.chunk_info.head,
                self.chunk_info.dep,
                self.chunk_info.chunk_head,
                self.chunk_info.chunk_func
            )

        elif mode == 'chunk_info':
            self.id_        = data['id']
            self.head       = data['head']
            self.dep        = data['dep']
            self.chunk_head = data['chunk_head']
            self.chunk_func = data['chunk_func']
            self.links      = [
                Reshape(mode='links', data=link)
                for link in data['links']
            ]
            self.predicate  = data['predicate'] if 'predicate' in data else []
            
            self.key_name   = 'id,head,dep,chunk_head,chunk_func'
            self.result_str = '{},{},{},{},{}'.format(
                self.id_,
                self.head,
                self.dep,
                self.chunk_head,
                self.chunk_func,
            )

        elif mode == 'links':
            self.link  = data['link']
            self.label = data['label']

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
                Reshape(mode='dependency_labels', data=dependency_label)
                for dependency_label in data['dependency_labels']
            ] if 'dependency_labels' in data else []
            self.attribute         = data['attribute'] if 'attribute' in data else '*'

            len_features = len(self.features)

            self.key_name   = 'form\t id,kana,lemma,pos,features[:5]'
            self.result_str = '{}\t {},{},{},{},{},{},{},{},{}'.format(
                self.form,
                self.id_,
                self.kana,
                self.lemma,
                self.pos,
                self.features[0] if len_features > 0 else '*',
                self.features[1] if len_features > 1 else '*',
                self.features[2] if len_features > 2 else '*',
                self.features[3] if len_features > 3 else '*',
                self.features[4] if len_features > 4 else '*'
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
                Reshape(mode='content', data=content)
                for content in data['coreference']
            ]
            self.tokens      = data['tokens']

            self.key_name   = 'None'
            self.result_str = '<called Reshape on coreference>'


        elif mode == 'content':
            self.representative_id = data['representative_id']
            self.referents         = [
                Reshape(mode='referents', data=referent)
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

            len_dialog_act = len(self.dialog_act)

            self.key_name   = 'modality\t dialog_act[:5]'
            self.result_str = '{}\t {},{},{},{},{}'.format(
                self.modality,
                self.dialog_act[0],
                self.dialog_act[1] if len_dialog_act > 1 else '*',
                self.dialog_act[2] if len_dialog_act > 2 else '*',
                self.dialog_act[3] if len_dialog_act > 3 else '*',
                self.dialog_act[4] if len_dialog_act > 4 else '*'
            )

        elif mode == 'sentiment':
            self.sentiment        = data['sentiment']
            self.score            = data['score']
            self.emotional_phrase = [
                Reshape(mode='emotional_phrase', data=content)
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
                self.emotion[0],  # required
                self.emotion[1] if len_emotion > 1 else '*',
                self.emotion[2] if len_emotion > 2 else '*',
                self.emotion[3] if len_emotion > 3 else '*',
                self.emotion[4] if len_emotion > 4 else '*'
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
                self.habit[0]  if len_habit  > 0 else '*',
                self.habit[1]  if len_habit  > 1 else '*',
                self.hobby[0]  if len_hobby  > 0 else '*',
                self.hobby[1]  if len_hobby  > 1 else '*',
                self.hobby[2]  if len_hobby  > 3 else '*',
                self.hobby[3]  if len_hobby  > 4 else '*',
                self.hobby[4]  if len_hobby  > 5 else '*',
                self.moving[0] if len_moving > 0 else '*',
                self.moving[1] if len_moving > 1 else '*',
            )

        elif mode == 'remove_filler':
            self.fillers             = [
                Reshape('filler', filler)
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
                Reshape('candidate', candidate)
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
                Reshape('correction', content)
                for content in data['correction']
            ]

            len_correction = len(self.correction)

            self.key_name   = 'form\t begin_pos,end_pos,detect_score,correct_score[:5]'
            self.result_str = '{}\t {},{},{},{},{},{},{},{}'.format(
                self.form,
                self.begin_pos,
                self.end_pos,
                self.detect_score,
                self.correction[0].form,  # required
                self.correction[1].form if len_correction > 1 else '*',
                self.correction[2].form if len_correction > 2 else '*',
                self.correction[3].form if len_correction > 3 else '*',
                self.correction[4].form if len_correction > 4 else '*'
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

