# coding=utf-8
"""
Author:Damon
"""
from data_process.get_data import source_file
from sklearn.preprocessing import LabelEncoder
from sklearn import preprocessing
from pypinyin import lazy_pinyin
import csv
import numpy as np
import pandas as pd


def drop_features(data, drop_list):  # 剔除不需要的特征字段
    for row in drop_list:
        try:
            data = data.drop(row, axis=1)
        except Exception as e:
            print('剔除特征发生错误（drop_features）: ', e)
    return data


def features_pinyin(data):  # 将字段改为拼音
    for key in data.keys():
        data[''.join(lazy_pinyin(key))] = data[key]
        del data[key]
    return data


def features_comparison(data_a, data_b):  # 将a和b的字段进行对比，将b缺少的补上去
    data_list = data_a.columns.values.tolist()
    data_b_keys = data_b.columns.values.tolist()
    for key in data_list:
        if key in data_b_keys:
            pass
        else:
            data_b[key] = 0
    for key in data_b_keys:
        if key in data_list:
            pass
        else:
            data_b = data_b.drop(key, 1)
    return data_b


def features_inspect(data, features_list, feature_path):
    # -----------检查特征数量 用于插入新特征重新生成模型 ----------------------
    is_write = False
    for feature in features_list:
        data_feature = source_file.f_read_csv(feature_path + str(feature) + ".csv")  # 读取数据文件
        for word in list(set(data[feature])):
            if word in list(data_feature[feature]):
                pass
            else:
                out = open(feature_path + str(feature) + ".csv", 'a', newline='')  # 打开文件，追加a
                csv_write = csv.writer(out, dialect='excel')  # 设定写入模式
                csv_write.writerow([word])  # 写入具体内容
                out.close()
                is_write = True
    return is_write


def features_change(data, features_list, feature_path):
    # -----------检查特征数量  用于将新特征当中未知，实时返回模型结果----------------------
    for feature in features_list:
        data_feature = source_file.f_read_csv(feature_path + str(feature) + ".csv")  # 读取数据文件
        for word in list(set(data[feature])):
            if word in list(data_feature[feature]):
                pass
            else:
                data[feature] = '未知'
    return data


def generate_label_encoder(data, data_y, feature_path, features_list):
    # -----------处理特征数据  标签化处理----------------------
    for feature in features_list:
        data_feature = source_file.f_read_csv(feature_path + str(feature) + ".csv")  # 读取数据文件
        label_encoder = LabelEncoder()  # 标签化
        label_encoder.fit(data_feature[feature])
        data_feature[feature] = label_encoder.transform(data_feature[feature])
        data[feature] = label_encoder.transform(data[feature])
    try:
        y = data[data_y].replace('是', 1).replace('否', 0)
        x = data.drop(data_y, axis=1)
        del data
        return x, y
    except Exception as e:
        print('处理特征数据发生错误（generate_label_encoder）: ', e)
        return data, None


def generate_onehot_encoder(data, data_y, feature_path, features_list):
    # -----------处理特征数据  独热编码处理----------------------
    data_feature_all = []
    data_temp_list = []
    for feature in features_list:
        data_feature = source_file.f_read_csv(feature_path + str(feature) + ".csv")  # 读取数据文件
        label_encoder = LabelEncoder()  # 标签化
        label_encoder.fit(data_feature[feature])
        data_feature[feature] = label_encoder.transform(data_feature[feature])
        data[feature] = label_encoder.transform(data[feature])
        # print(data_feature[feature])
        data_temp_list.append(feature)
        data_temp = pd.get_dummies(data_feature, columns=data_temp_list)
        data_feature_all = data_feature_all + data_temp.columns.values.tolist()
        data_temp_list = []
    try:
        y = data[data_y].replace('是', 1).replace('否', 0)
        x = data.drop(data_y, axis=1)
        x = pd.get_dummies(x, columns=features_list)
        del data
        return x, y, data_feature_all
    except Exception as e:
        print('处理特征数据发生错误（generate_label_encoder）: ', e)
        return data, None


def filling_mode_miss_value(data, miss_value_features, feature_path, type=1):  # 用众数填补缺失值
    if type == 1:
        for features in miss_value_features:
            miss_value = data[features].mode()
            out = open(feature_path + str(features) + ".csv", 'w+', newline='')  # 打开文件
            csv_write = csv.writer(out, dialect='excel')  # 设定写入模式
            csv_write.writerow(miss_value)  # 写入具体内容
            out.close()
            data[features] = data[features].fillna(miss_value[0])
            #print(data_01)
        return data
    else:
        for features in miss_value_features:
            features_data = source_file.f_read_csv(feature_path + str(features) + ".csv")
            data[features] = features_data.columns.values[0]
        return data
