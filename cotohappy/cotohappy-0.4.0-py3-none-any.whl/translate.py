#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 20 12:00:00 2019

COTOHA API for Python3.8
@author: Nicolas Toba Nozomi
@id: 278mt
"""


class Translate(object):

    def __init__(self):

        pass


    def dep_list(self, key: str) -> str:

        dic = {
            'O': '掛かり先なし',
            'Q': '自己掛かり',
            'A': '同格',
            'I': '部分並列内関係',
            'P': '並列関係',
            'D': '通常の関係'
        }

        return dic[key] if key in dic else key


    def predicate_list(self, key: str) -> str:

        dic = {
            'negative': '否定',
            'past'    : '過去時制',
            'passive' : '受動態'
        }

        return dic[key] if key in dic else key


    def speech_parts_list(self, key: str) -> str:

        dic = {
            'Symbol': '記号の形態素',
            'Number': '数値をあらわす形態素',
        }

        return dic[key] if key in dic else key


    def features_list(self, key0: str, key1: str) -> str:

        dic = {
            '動詞語幹': {
                'A'      : '一段',
                'K'      : 'カ五',
                'G'      : 'ガ五',
                'S'      : 'サ五',
                'T'      : 'タ五',
                'N'      : 'ナ五',
                'B'      : 'バ五',
                'M'      : 'マ五',
                'R'      : 'ラ五',
                'W'      : 'ワ五',
                'KURU'   : 'カ変',
                'SURU'   : 'サ変',
                'SX'     : 'サ変',
                'RX'     : 'ラ五特殊',
                'IKU'    : 'カ五特殊',
                'ZX'     : 'ザ変',
                'Lて連用': '補助動詞'
            },
            '形容詞語幹': {
                'アウオ段': '活用語尾直前の語がアウオ段になる形容詞',
                'イ段'    : '活用語尾直前の語がイ段になる形容詞',
                'Lて連用' : '補助形容詞'
            }
        }

        return dic[key0][key1] if key0 in dic and key1 in dic[key0] else key1


    def semantic_role_label_list(self, key: str) -> str:

        dic = {
            'agent'            : '有意動作を引き起こす主体',
            'agentnonvoluntary': '意思性のない主体',
            'coagent'          : '主体と一緒に動作をする主体',
            'aobject'          : '属性を持つ対象',
            'object'           : '動作・変化の影響を受ける対象',
            'implement'        : '有意思動作における道具・手段',
            'source'           : '事象の主体または対象の最初の位置',
            'material'         : '材料または構成要素',
            'goal'             : '事象の主体または対象の最後の位置',
            'beneficiary'      : '利益・不利益の移動先',
            'place'            : '事象の成立する場所',
            'scene'            : '事象の成立する場面',
            'manner'           : '動作・変化のやり方',
            'time'             : '事象の起こる時間',
            'timefrom'         : '事象の始まる時間',
            'timeto'           : '事象の終わる時間',
            'basis'            : '比較の基準',
            'unit'             : '単位',
            'fromto'           : '範囲',
            'purpose'          : '目的',
            'condition'        : '事象・事実の条件関係',
            'adjectivals'      : '形容',
            'adverbials'       : '形容(動作)',
            'other'            : 'その他'
        }

        return dic[key] if key in dic else key


    def dependency_label_list(self, key: str):

        pass


    def ne_class_list(self, key: str) -> str:

        dic = {
            'ORG': '組織名',
            'PSN': '人名',
            'LOC': '場所',
            'ART': '固有物名',
            'DAT': '日付表現',
            'TIM': '時刻表現',
            'NUM': '数値表現',
            'MNY': '金額表現',
            'PCT': '割合表現',
            'OTH': 'その他'
        }

        return dic[key] if key in dic else key


    def extended_ne_class_list(self, key: str) -> str:

        dic = {
            'Name'                        : '名前',
            'Name_Other'                  : '名前_その他',
            'Person'                      : '人名',
            'God'                         : '神名',
            'Organization'                : '組織名',
            'Organization_Other'          : '組織名_その他',
            'International_Organization'  : '国際組織名',
            'Show_Organization'           : '公演組織名',
            'Family'                      : '家系名',
            'Ethnic_Group'                : '民族名',
            'Ethnic_Group_Other'          : '民族名_その他',
            'Nationality'                 : '国籍名',
            'Sports_Organization'         : '競技組織名',
            'Sports_Organization_Other'   : '競技組織名_その他',
            'Pro_Sports_Organization'     : 'プロ競技組織名',
            'Sports_League'               : '競技リーグ名',
            'Corporation'                 : '法人名',
            'Corporation_Other'           : '法人名_その他',
            'Company'                     : '企業名',
            'Company_Group'               : '企業グループ名',
            'Political_Organization'      : '政治的組織名',
            'Political_Organization_Other': '政治的組織名_その他',
            'Government'                  : '政府組織名',
            'Political_Party'             : '政党名',
            'Cabinet'                     : '内閣名',
            'Military'                    : '軍隊名',
            'Location'                    : '地名',
            'Location_Other'              : '地名_その他',
            'Spa'                         : '温泉名',
            'GPE'                         : '政府を持つ地域名',
            'GPE_Other'                   : 'GPE_その他',
            'City'                        : '市区町村名',
            'County'                      : '郡名',
            'Province'                    : '都道府県州名',
            'Country'                     : '国名',
            'Region'                      : '地域名',
            'Region_Other'                : '地域名_その他',
            'Continental_Region'          : '大陸地域名',
            'Domestic_Region'             : '国内地域名',
            'Geological_Region'           : '地形名',
            'Geological_Region_Other'     : '地形名_その他',
            'Mountain'                    : '山地名',
            'Island'                      : '島名',
            'River'                       : '河川名',
            'Lake'                        : '湖沼名',
            'Sea'                         : '海洋名',
            'Bay'                         : '湾名',
            'Astral_Body'                 : '天体名',
            'Astral_Body_Other'           : '天体名_その他',
            'Star'                        : '恒星名',
            'Planet'                      : '惑星名',
            'Constellation'               : '星座名',
            'Address'                     : 'アドレス',
            'Address_Other'               : 'アドレス_その他',
            'Postal_Address'              : '郵便住所',
            'Phone_Number'                : '電話番号',
            'Email'                       : '電子メール',
            'URL'                         : 'URL',
            'Facility'                    : '施設名',
            'Facility_Other'              : '施設名_その他',
            'Facility_Part'               : '施設部分名',
            'Archaeological_Place'        : '遺跡名',
            'Archaeological_Place_Other'  : '遺跡名_その他',
            'Tumulus'                     : '古墳名',
            'GOE'                         : 'GOE',
            'GOE_Other'                   : 'GOE_その他',
            'Public_Institution'          : '公共機関名',
            'School'                      : '学校名',
            'Research_Institute'          : '研究機関名',
            'Market'                      : '取引所名',
            'Park'                        : '公園名',
            'Sports_Facility'             : '競技施設名',
            'Museum'                      : '美術博物館名',
            'Zoo'                         : '動植物園名',
            'Amusement_Park'              : '遊園施設名',
            'Theater'                     : '劇場名',
            'Worship_Place'               : '神社寺名',
            'Car_Stop'                    : '停車場名',
            'Station'                     : '電車駅名',
            'Airport'                     : '空港名',
            'Port'                        : '港名',
            'Line'                        : '路線名',
            'Line_Other'                  : '路線名_その他',
            'Railroad'                    : '電車路線名',
            'Road'                        : '道路名',
            'Canal'                       : '運河名',
            'Water_Route'                 : '航路名',
            'Tunnel'                      : 'トンネル名',
            'Bridge'                      : '橋名',
            'Product'                     : '製品名',
            'Product_Other'               : '製品名_その他',
            'Material'                    : '材料名',
            'Clothing'                    : '衣類名',
            'Money_Form'                  : '貨幣名',
            'Drug'                        : '医薬品名',
            'Weapon'                      : '武器名',
            'Stock'                       : '株名',
            'Award'                       : '賞名',
            'Decoration'                  : '勲章名',
            'Offense'                     : '罪名',
            'Service'                     : '便名',
            'Class'                       : '等級名',
            'Character'                   : 'キャラクター名',
            'ID_Number'                   : '識別番号',
            'Vehicle'                     : '乗り物名',
            'Vehicle_Other'               : '乗り物名_その他',
            'Car'                         : '車名',
            'Train'                       : '列車名',
            'Aircraft'                    : '飛行機名',
            'Spaceship'                   : '宇宙船名',
            'Ship'                        : '船名',
            'Food'                        : '食べ物名',
            'Food_Other'                  : '食べ物名_その他',
            'Dish'                        : '料理名',
            'Art'                         : '芸術作品名',
            'Art_Other'                   : '芸術作品名_その他',
            'Picture'                     : '絵画名',
            'Broadcast_Program'           : '番組名',
            'Movie'                       : '映画名',
            'Show'                        : '公演名',
            'Music'                       : '音楽名',
            'Book'                        : '文学名',
            'Printing'                    : '出版物名',
            'Printing_Other'              : '出版物名_その他',
            'Newspaper'                   : '新聞名',
            'Magazine'                    : '雑誌名',
            'Doctrine_Method'             : '主義方式名',
            'Doctrine_Method_Other'       : '主義方式名_その他',
            'Culture'                     : '文化名',
            'Religion'                    : '宗教名',
            'Academic'                    : '学問名',
            'Style'                       : '流派名',
            'Sport'                       : '競技名',
            'Movement'                    : '運動名',
            'Theory'                      : '理論名',
            'Plan'                        : '政策計画名',
            'Rule'                        : '規則名',
            'Rule_Other'                  : '規則名_その他',
            'Treaty'                      : '条約名',
            'Law'                         : '法令名',
            'Title'                       : '称号名',
            'Title_Other'                 : '称号名_その他',
            'Position_Vocation'           : '地位職業名',
            'Language'                    : '言語名',
            'Language_Other'              : '言語名_その他',
            'National_Language'           : '国語名',
            'Unit'                        : '単位名',
            'Unit_Other'                  : '単位名_その他',
            'Currency'                    : '通貨単位名',
            'Event'                       : 'イベント名',
            'Event_Other'                 : 'イベント名_その他',
            'Occasion'                    : '催し物名',
            'Occasion_Other'              : '催し物名_その他',
            'Religious_Festival'          : '例祭名',
            'Game'                        : '競技会名',
            'Conference'                  : '会議名',
            'Incident'                    : '事故事件名',
            'Incident_Other'              : '事故事件名_その他',
            'War'                         : '戦争名',
            'Natural_Phenomenon'          : '自然災害名',
            'Natural_Phenomenon_Other'    : '自然現象名_その他',
            'Natural_Disaster'            : '自然災害名',
            'Earthquake'                  : '地震名',
            'Natural_Object'              : '自然物名',
            'Natural_Object_Other'        : '自然物名_その他',
            'Element'                     : '元素名',
            'Compound'                    : '化合物名',
            'Mineral'                     : '鉱物名',
            'Living_Thing'                : '生物名',
            'Living_Thing_Other'          : '生物名_その他',
            'Fungus'                      : '真菌類名',
            'Mollusc_Arthropod'           : '軟体動物_節足動物名',
            'Insect'                      : '昆虫類名',
            'Fish'                        : '魚類名',
            'Amphibia'                    : '両生類名',
            'Reptile'                     : '爬虫類名',
            'Bird'                        : '鳥類名',
            'Mammal'                      : '哺乳類名',
            'Flora'                       : '植物名',
            'Living_Thing_Part'           : '生物部位名',
            'Living_Thing_Part_Other'     : '生物部位名_その他',
            'Animal_Part'                 : '動物部位名',
            'Flora_Part'                  : '植物部位名',
            'Disease'                     : '病気名',
            'Disease_Other'               : '病気名_その他',
            'Animal_Disease'              : '動物病気名',
            'Color'                       : '色名',
            'Color_Other'                 : '色名_その他',
            'Nature_Color'                : '自然色名',
            'Time_Top'                    : '時間表現',
            'Time_Top_Other'              : '時間表現_その他',
            'Timex'                       : '時間',
            'Timex_Other'                 : '時間_その他',
            'Time'                        : '時刻表現',
            'Date'                        : '日付表現',
            'Day_Of_Week'                 : '曜日表現',
            'Era'                         : '時代表現',
            'Periodx'                     : '期間',
            'Periodx_Other'               : '期間_その他',
            'Period_Time'                 : '時刻期間',
            'Period_Day'                  : '日数期間',
            'Period_Week'                 : '週数期間',
            'Period_Month'                : '月数期間',
            'Period_Year'                 : '年数期間',
            'Numex'                       : '数値表現',
            'Numex_Other'                 : '数値表現_その他',
            'Money'                       : '金額表現',
            'Stock_Index'                 : '株指標',
            'Point'                       : 'ポイント',
            'Percent'                     : '割合表現',
            'Multiplication'              : '倍数表現',
            'Frequency'                   : '頻度表現',
            'Age'                         : '年齢',
            'School_Age'                  : '学齢',
            'Ordinal_Number'              : '序数',
            'Rank'                        : '順位表現',
            'Latitude_Longtitude'         : '緯度経度',
            'Measurement'                 : '寸法表現',
            'Measurement_Other'           : '寸法表現_その他',
            'Physical_Extent'             : '長さ',
            'Space'                       : '面積',
            'Volume'                      : '体積',
            'Weight'                      : '重量',
            'Speed'                       : '速度',
            'Intensity'                   : '密度',
            'Temperature'                 : '温度',
            'Calorie'                     : 'カロリー',
            'Seismic_Intensity'           : '震度',
            'Seismic_Magnitude'           : 'マグニチュード',
            'Countx'                      : '個数',
            'Countx_Other'                : '個数_その他',
            'N_Person'                    : '人数',
            'N_Organization'              : '組織数',
            'N_Location'                  : '場所数',
            'N_Location_Other'            : '場所数_その他',
            'N_Country'                   : '国数',
            'N_Facility'                  : '施設数',
            'N_Product'                   : '製品数',
            'N_Event'                     : 'イベント数',
            'N_Natural_Object'            : '自然物数',
            'N_Natural_Object_Other'      : '自然物数_その他',
            'N_Animal'                    : '動物数',
            'N_Flora'                     : '植物数'
        }

        return dic[key] if key in dic else key


    def speech_act_list(self, key: str) -> str:

        dic = {
            'greeting'             : '挨拶',
            'information-providing': '情報提供',
            'feedback'             : 'フィードバック/相槌',
            'information-seeking'  : '情報獲得',
            'agreement'            : '同意',
            'feedbackElicitation'  : '理解確認',
            'commissive'           : '約束',
            'acceptOffer'          : '受領',
            'selfCorrection'       : '言い直し',
            'thanking'             : '感謝',
            'apology'              : '謝罪',
            'stalling'             : '時間埋め',
            'directive'            : '指示',
            'goodbye'              : '挨拶(別れ)',
            'declineOffer'         : '否認',
            'turnAssign'           : 'ターン譲渡',
            'pausing'              : '中断',
            'acceptApology'        : '謝罪受領',
            'acceptThanking'       : '感謝受領'
        }

        return dic[key] if key in dic else key

