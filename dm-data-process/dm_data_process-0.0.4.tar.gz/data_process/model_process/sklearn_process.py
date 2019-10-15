# coding=utf-8
"""
Created on 2019年2月20日

@author: Administrator
"""
from sklearn.externals import joblib
from sklearn import tree


def model_save(model_tree, data_feature_name):
    joblib.dump(model_tree, "decision_tree.m")  # 模型保存
    with open("decision_tree.dot", 'w', -1, "utf-8") as f:
        f = tree.export_graphviz(model_tree, feature_names=data_feature_name, out_file=f)
    with open('decision_tree.dot', 'r+', encoding='UTF-8') as f:
        content = f.read()
        content = content.replace('''digraph Tree {
node [shape=box] ;''', '''  digraph Tree {
edge [fontname="FangSong"] ;
node [shape=box, fontname="FangSong" size="20,20"] ;\n''')
        f.seek(0, 0)
        # f.write('edge [fontname="SimSun"];\n'+'node [shape=box, fontname="SimSun" size="20,20"];'+content)
        f.write(content)
        # 可视化树图
    # graph = pydotplus.graph_from_dot_data(content)
    # img = Image(graph.create_png())
    # graph.write_png("decision_tree.png")
