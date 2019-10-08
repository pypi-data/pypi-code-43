from xtoy import Toy

d = get_training_data()

X, y = d.iloc[:, :-1], d.iloc[:, -1]

toy.fit(X, y)

toy.best_features_(n=30, aggregation=None)
