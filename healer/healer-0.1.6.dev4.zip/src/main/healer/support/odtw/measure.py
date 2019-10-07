"""
On-line Dynamic Time Warping for Streaming Time Series
http://ecmlpkdd2017.ijs.si/papers/paperID187.pdf
https://bitbucket.org/izaskun_oregui/odtw/src/master/OEM.py
"""

from __future__ import annotations

import enum
from typing import Tuple

import numpy as np

from healer.support.typing import AutoNameEnum


@enum.unique
class Distance(AutoNameEnum):
    "provided distance measures"
    euclidean = enum.auto()
    manhattan = enum.auto()


class DistanceSupport:
    "provided distance measures"

    @staticmethod
    def measure(
            A:np.array, B:np.array,  # 1D
            distance:Distance,
        ) -> np.array:  # 2D
        ""

        if distance == Distance.euclidean:
            AA, BB = np.meshgrid(A, B)
            return np.sqrt((AA - BB) ** 2)

        if distance == Distance.manhattan:
            AA, BB = np.meshgrid(A, B)
            return np.abs(AA - BB)

        raise RuntimeError(f"wrong distance: {distance}")


class MeasureSupport:

    '''
    X,S: time series
     -----------
    X| XS | XY |
     -----------
    R|prev| RY |
     -----------
       S    Y

    dtw_S: partial solutions to DTW(R,S)

    ini_X: Index of the first point of X in the complete time series
    ini_S: Index of the first point of S in the complete time series

    '''

    @staticmethod
    def solve_XS(
            X:np.array, S:np.array,
            dtw_S:np.array,
            ini_X:int, ini_S:int,
            weight:float, distance:Distance,
        ) -> np.array:  # 2D

        size_X, size_S = X.size, S.size

        # compute point-wise distance
        XS = DistanceSupport.measure(X, S, distance)  # note order

        # solve zero point
        XS[0, 0] += (weight if ini_X <= ini_S else 1) * dtw_S[0]

        # solve first row
        for idx_S in range(1, size_S):
            pos_S = ini_S + idx_S
            XS[0, idx_S] += np.min([
                (weight if pos_S <= ini_X else 1) * XS[0, idx_S - 1],
                (weight * dtw_S[idx_S - 1]),
                (weight if ini_X <= pos_S else 1) * dtw_S[idx_S]
            ])

        # solve first col
        for idx_X in range(1, size_X):
            XS[idx_X, 0] += XS[idx_X - 1, 0]

        # solve the rest
        for idx_X in range(1, size_X):
            pos_X = ini_X + idx_X
            for idx_S in range(1, size_S):
                pos_S = ini_S + idx_S
                XS[idx_X, idx_S] += np.min([
                    (weight if (pos_X <= pos_S) else 1) * XS[idx_X - 1, idx_S],
                    (weight * XS[idx_X - 1, idx_S - 1]),
                    (weight if (pos_S <= pos_X - 1) else 1) * XS[idx_X, idx_S - 1]
                ])

        return XS

    '''
    R,Y: time series
     -----------
    X| XS | XY |
     -----------
    R| RS | RY |
     -----------
       S    Y
    '''

    @staticmethod
    def solve_RY(
            R:np.array, Y:np.array,
            dtw_R:np.array,
            ini_R:int, ini_Y:int,
            weight:float, distance:Distance,
        ) -> np.array:  # 2D

        size_R, size_Y = R.size, Y.size

        # compute point-wise distance
        RY = DistanceSupport.measure(Y, R, distance)  # note order

        # solve zero point
        RY[0, 0] += (weight if ini_Y <= ini_R else 1) * dtw_R[0]

        # solve first col
        for idx_R in range(1, size_R):
            pos_R = ini_R + idx_R
            RY[idx_R, 0] += np.min([
                (weight if pos_R <= ini_Y else 1) * RY[idx_R - 1, 0],
                (weight * dtw_R[idx_R - 1]),
                (weight if ini_Y <= pos_R else 1) * dtw_R[idx_R]])

        # solve first row
        for idx_Y in range(1, size_Y):
            RY[0, idx_Y] += RY[0, idx_Y - 1]

        # solve the rest
        for idx_R in range(1, size_R):
            for idx_Y in range(1, size_Y):
                pos_R = ini_R + idx_R
                pos_Y = ini_Y + idx_Y
                RY[idx_R, idx_Y] += np.min([
                    (weight if pos_R <= pos_Y else 1) * RY[idx_R - 1, idx_Y],
                    (weight * RY[idx_R - 1, idx_Y - 1]),
                    (weight if pos_Y <= pos_R else 1) * RY[idx_R, idx_Y - 1]])

        return RY

    '''
    R,S: time series
     -----------
    X| XS | XY |
     -----------
    R|prev| RY |
     -----------
       S    Y

    '''

    @staticmethod
    def solve_RS(
            R:np.array, S:np.array,
            ini_R, ini_S,
            weight:float, distance:Distance,
        ) -> np.array:  # 2D

        size_R, size_S = R.size, S.size

        # compute point-wise distance
        RS = DistanceSupport.measure(S, R, distance)  # note order

        # solve first row
        for idx_S in range(1, size_S):
            pos_S = ini_S + idx_S
            RS[0, idx_S] += (weight if pos_S <= ini_R else 1) * RS[0, idx_S - 1]

        # solve first col
        for idx_R in range(1, size_R):
            pos_R = ini_R + idx_R
            RS[idx_R, 0] += (weight if pos_R <= ini_S else 1) * RS[idx_R - 1, 0]

        # solve the rest
        for idx_R in range(1, size_R):
            for idx_S in range(1, size_S):
                pos_S = ini_S + idx_S
                pos_R = ini_R + idx_R
                RS[idx_R, idx_S] += np.min([
                    (weight if (pos_R <= pos_S) else 1) * RS[idx_R - 1, idx_S],
                    (weight * RS[idx_R - 1, idx_S - 1]),
                    (weight if (pos_S <= pos_R - 1) else 1) * RS[idx_R, idx_S - 1]
                ])

        return RS

    '''
    X,S: time series
     -----------
    X| XS | XY |
     -----------
    R| RS | RY |
     -----------
       S    Y

    dtwXS: partial solutions to DTW(X,S), DTW(X,S)[:,-1]
    dtwRS: solution to DTW(R,S)
    dtwRY: partial solutions to DTW(R,Y), DTW(R,Y)[-1,:]

    ini_X: Index of the first point of X in the complete time series
    ini_Y: Index of the first point of Y in the complete time series

    '''

    @staticmethod
    def solve_XY(
            X:np.array, Y:np.array,
            dtw_XS:np.array, dtw_RS:np.array, dtw_RY:np.array,
            ini_X:int, ini_Y:int,
            weight:float, distance:Distance,
        ) -> np.array:  # 2D

        size_X, size_Y = X.size, Y.size

        # compute point-wise distance
        XY = DistanceSupport.measure(Y, X, distance)  # note order

        # solve zero point
        XY[0, 0] += np.min([
            (weight if ini_Y <= ini_X else 1) * dtw_XS[0],
            (weight * dtw_RS),
            (weight if ini_X <= ini_Y else 1) * dtw_RY[0],
        ])

        # solve first row
        for idx_Y in range(1, size_Y):
            pos_Y = ini_Y + idx_Y
            XY[0, idx_Y] += np.min([
                (weight if pos_Y <= ini_X else 1) * XY[0, idx_Y - 1],
                (weight * dtw_RY[idx_Y - 1]),
                (weight if ini_X <= pos_Y else 1) * dtw_RY[idx_Y],
            ])

        # solve first col
        for idx_X in range(1, size_X):
            pos_X = ini_X + idx_X
            XY[idx_X, 0] += np.min([
                (weight if pos_X <= ini_Y else 1) * XY[idx_X - 1, 0],
                (weight * dtw_XS[idx_X - 1]),
                (weight if ini_Y <= pos_X else 1) * dtw_XS[idx_X],
            ])

        # solve the rest
        for idx_X in range(1, size_X):
            pos_X = ini_X + idx_X
            for idx_Y in range(1, size_Y):
                pos_Y = ini_Y + idx_Y
                XY[idx_X, idx_Y] += np.min([
                    (weight if pos_X <= pos_Y else 1) * XY[idx_X - 1, idx_Y],
                    (weight * XY[idx_X - 1, idx_Y - 1]),
                    (weight if pos_Y <= pos_X else 1) * XY[idx_X, idx_Y - 1],
                ])

        return XY


class MeasureODTW:
    '''
    size_X:    length of the memory for X series
    size_Y:    length of the memory for Y series

    weight:     weight

    distance:  type of distance
    '''

    size_X:int
    size_Y:int

    distance:Distance

    R:np.array  # 1D persisted X
    S:np.array  # 1D persisted Y

    dtw_R:np.array  # 2D
    dtw_S:np.array  # 2D

    ini_X:int  # starting index in S
    ini_Y:int  # starting index in R

    def __init__(self,
            weight:float,
            size_X:int, size_Y:int,
            distance:Distance=Distance.manhattan,
        ):

        self.weight = weight
        self.size_X = size_X
        self.size_Y = size_Y
        self.distance = distance

        self.R = np.empty(size_X)
        self.S = np.empty(size_Y)
        self.dtw_R = np.empty(size_X)
        self.dtw_S = np.empty(size_Y)

        self.ini_X = 0
        self.ini_Y = 0

    def solve_RS(self,
            R:np.array, S:np.array, ini_R, ini_S,
        ) -> np.array:  # 2D

        RS = MeasureSupport.solve_RS(
            R, S, ini_R, ini_S,
            self.weight, self.distance,
        )

        size_R, size_S = R.size, S.size

        # Save the statistics, size O(size_X + size_Y)
        if self.size_X >= size_R:
            self.R = R
            self.dtw_R = RS[:, -1]
        else:
            self.R = R[-self.size_X:]
            self.dtw_R = RS[-self.size_X:, -1]

        if self.size_Y >= size_S:
            self.S = S
            self.dtw_S = RS[-1, :]
        else:
            self.S = S[-self.size_Y:]
            self.dtw_S = RS[-1, -self.size_Y:]

        return RS[-1, -1]

    def solve_RY(self,
            R, Y, dtw_R, ini_R, ini_Y,
        ) -> Tuple:
        RY = MeasureSupport.solve_RY(
            R, Y, dtw_R, ini_R, ini_Y,
            self.weight, self.distance,
        )
        return (RY[-1, :], RY[:, -1])

    def solve_XS(self,
            X, S, dtw_S, ini_X, ini_S,
        ) -> Tuple:
        XS = MeasureSupport.solve_XS(
            X, S, dtw_S, ini_X, ini_S,
            self.weight, self.distance,
        )
        return (XS[:, -1], XS[-1, :])

    def solve_XY(self,
            X, Y, dtw_XS, dtw_RS, dtw_RY, ini_X, ini_Y,
        ) -> Tuple:
        XY = MeasureSupport.solve_XY(
            X, Y, dtw_XS, dtw_RS, dtw_RY, ini_X, ini_Y,
            self.weight, self.distance,
        )
        return (XY[-1, :], XY[:, -1])

    '''
    Add two chunks of the time series X, Y
    X, Y: last measures of the time series

      -----------
    X | XS | XY |
      -----------
    R | RS | RY |
      -----------
        S    Y
    '''

    def with_block(self,
            X:np.array,  # 1D
            Y:np.array,  # 1D
        ) -> float:

        size_X, size_Y = X.size, Y.size

        # solve XS
        dtw_XSv, dtw_XSh = self.solve_XS(
            X=X, S=self.S,
            dtw_S=self.dtw_S,
            ini_X=self.ini_X, ini_S=self.ini_Y - self.size_Y,
        )

        # solve RY
        dtw_RYh, dtw_RYv = self.solve_RY(
            R=self.R, Y=Y,
            dtw_R=self.dtw_R,
            ini_R=self.ini_X - self.size_X, ini_Y=self.ini_Y,
        )

        # solve XY
        dtw_XYh, dtw_XYv = self.solve_XY(
            X=X, Y=Y,
            dtw_XS=dtw_XSv, dtw_RS=self.dtw_S[-1], dtw_RY=dtw_RYh,
            ini_X=self.ini_X, ini_Y=self.ini_Y,
            weight=self.weight, distance=self.distance,
        )

        # Save the statistics
        if(size_X < self.size_X):
            self.R = np.concatenate((self.R[-(self.size_X - size_X):], X))
            self.dtw_R = np.concatenate((dtw_RYv[-(self.size_X - size_X):], dtw_XYv))
        else:
            self.R = X[size_X - self.size_X:size_X]
            self.dtw_R = dtw_XYv[size_X - self.size_X:size_X]

        if(size_Y < self.size_Y):
            self.S = np.concatenate((self.S[-(self.size_Y - size_Y):], Y))
            self.dtw_S = np.concatenate((dtw_XSh[-(self.size_Y - size_Y):], dtw_XYh))
        else:
            self.S = Y[size_Y - self.size_Y:size_Y]
            self.dtw_S = dtw_XYh[size_Y - self.size_Y:size_Y]

        # Save the starting index of the next block
        size_X += self.ini_X
        size_Y += self.ini_Y
        self.ini_X = np.max([0, size_X - size_Y])
        self.ini_Y = np.max([0, size_Y - size_X])

        # return dtw_XYv[-1]
        return min(np.concatenate((self.dtw_R, self.dtw_S)))

    def with_point(self, x:float, y:float) -> float:

        size_R, size_S = len(self.R), len(self.S)

        X = np.array([x])
        Y = np.array([y])

        # solve XS
        dtw_XS_col, dtw_XS_row = self.solve_XS(
            X=X, S=self.S,
            dtw_S=self.dtw_S,
            ini_X=self.ini_X, ini_S=self.ini_Y - self.size_Y,
        )

        # solve RY
        dtw_RY_row, dtw_RY_col = self.solve_RY(
            R=self.R, Y=Y,
            dtw_R=self.dtw_R,
            ini_R=self.ini_X - self.size_X, ini_Y=self.ini_Y,
        )

        # solve XY (last row and last column)
        dtw_XY_row, dtw_XY_col = self.solve_XY(
            X=X, Y=Y,
            dtw_XS=dtw_XS_col, dtw_RS=self.dtw_S[-1], dtw_RY=dtw_RY_row,
            ini_X=self.ini_X, ini_Y=self.ini_Y,
        )

        if size_R < self.size_X:
            self.R = np.concatenate((self.R, X))
            self.dtw_R = np.concatenate((self.dtw_R, dtw_XY_col))
        else:
            self.R = np.concatenate((self.R[1:], X))
            self.dtw_R = np.concatenate((self.dtw_R[1:], dtw_XY_col))

        if size_S < self.size_Y:
            self.S = np.concatenate((self.S, Y))
            self.dtw_S = np.concatenate((self.dtw_S, dtw_XY_row))
        else:
            self.S = np.concatenate((self.S[1:], Y))
            self.dtw_S = np.concatenate((self.dtw_S[1:], dtw_XY_row))

        # return dtw_XY_col[-1]
        return min(np.concatenate((self.dtw_R, self.dtw_S)))


def getW(s=100, p=0.001) -> float:
    "Heuristic for setting the weight of OEM"
    return np.power(p, 1.0 / s)
