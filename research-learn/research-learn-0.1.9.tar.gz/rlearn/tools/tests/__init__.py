from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.datasets import make_classification
from imblearn.over_sampling import RandomOverSampler, SMOTE, ADASYN

X1, y1 = make_classification(weights=[0.90, 0.10], n_samples=100, random_state=0)
X2, y2 = make_classification(
    weights=[0.80, 0.20], n_samples=100, n_features=10, random_state=1
)
X3, y3 = make_classification(
    weights=[0.60, 0.40], n_samples=100, n_features=5, random_state=2
)
DATASETS = [('A', (X1, y1)), ('B', (X2, y2)), ('C', (X3, y3))]
OVERSAMPLERS = [
    ('random', RandomOverSampler(), {}),
    ('smote', SMOTE(), {'k_neighbors': [2, 3]}),
    ('adasyn', ADASYN(), {'n_neighbors': [2, 3, 4]}),
]
CLASSIFIERS = [
    ('knn', KNeighborsClassifier(), {}),
    ('dtc', DecisionTreeClassifier(), {'max_depth': [3, 5]}),
]
