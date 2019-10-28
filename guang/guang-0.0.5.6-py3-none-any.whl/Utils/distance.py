import numpy as np 

'''
Some common distance function
'''

def euclidean_dist(vec1, vec2):
    """欧氏距离:
    我们现实所说的直线距离"""
    assert vec1.shape == vec2.shape 
    return np.sqrt(np.sum((x - y) ** 2))


def manhattan_dist(vec1, vec2):
    """曼哈顿距离:
    城市距离"""
    return np.sum(np.abs(vec1 - vec2))


def chebyshev_dist(vec1, vec2):
    """切比雪夫距离:
    国际象棋距离
    """
    return np.max(np.abs(vec1 - vec2))

def minkowski_dist(vec1, vec2, p=2):
    """闵可夫斯基距离:
    应该说它其实是一组距离的定义: 
    inputParam: p
    return distance,
    while p=1: dist = manhattan_dist
    while p=2: dist = euclidean_dist
    while p=inf: dist = chebyshev_dist
    """
    s = np.sum(np.power(vec2 - vec1, p))
    return np.power(s,1/p)


def cosine_dist(vec1, vec2):
    """夹角余弦"""
    # np.linalg.norm(vec, ord=1) 计算p=1范数,默认p=2
    return (vec1.T @ vec2)/(np.linalg.norm(vec1) * np.linalg.norm(vec2))


def hamming_dist():
    return np.sum(x != y) / len(x)


def jaccard_simil_coef():
    pass