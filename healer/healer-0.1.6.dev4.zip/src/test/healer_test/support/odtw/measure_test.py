
from healer.support.odtw.measure import  *


def xtest_distance_measure():
    print()

    A = np.array([1, 2, 3])
    B = np.array([1, 2, 3])

    temp_A, temp_B = np.meshgrid(A, B)

    diff_C = temp_A - temp_B

    print(f"temp_A=\n{temp_A}")
    print(f"temp_B=\n{temp_B}")
    print(f"diff_C=\n{diff_C}")

    dist_one = DistanceSupport.measure(A, B, distance=Distance.euclidean)
    dist_two = DistanceSupport.measure(A, B, distance=Distance.manhattan)

    print(f"dist_one=\n{dist_one}")
    print(f"dist_two=\n{dist_two}")


def xtest_with_point():
    print()

    measure = MeasureODTW(size_X=5, size_Y=5, weight=1)

    point_list = [
        (0, 0),
        (1, 1),
    ]

    for point in point_list:
        x = point[0]
        y = point[1]
        delta = measure.with_point(x, y)
        print(f"delta={delta}")

