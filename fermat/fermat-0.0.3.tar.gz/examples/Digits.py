from pprint import pprint
from sklearn.datasets import load_digits
import matplotlib.pyplot as plt
from fermat import FermatKMeans
from collections import defaultdict


def main():
    digits = load_digits()

    fkm = FermatKMeans(
        distance='euclidean',
        cluster_qty=10,
        alpha=4,
        path_method='FW',
        seed=42
    )

    clusters = fkm.fit_predict(digits.data)
    pprint(clusters)

    res = defaultdict(list)
    for i, cluster_id in enumerate(clusters):
        res[cluster_id].append(i)

    for samples in res.values():
        fig, axs = plt.subplots(nrows=3, ncols=5)
        for i, sample in enumerate(samples[:15]):
            ax = axs[i // 5][i % 5]  # type: plt.Axes
            ax.axis('off')
            ax.imshow(digits.data[sample].reshape(8, 8), cmap=plt.cm.gray_r, interpolation='nearest')
        plt.show()
        plt.close()

    print(1)


if __name__ == '__main__':
    main()
