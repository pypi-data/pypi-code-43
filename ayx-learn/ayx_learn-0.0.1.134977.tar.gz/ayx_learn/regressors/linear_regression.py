# Copyright (C) 2019 Alteryx, Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
"""Linear regression algorithm."""

from sklearn.linear_model import ElasticNet


class LinearRegression(ElasticNet):
    """Linear regression wrapper class."""

    def __init__(
        self,
        alpha=1.0,
        l1_ratio=0.5,
        fit_intercept=True,
        normalize=True,
        precompute=False,
        max_iter=1000,
        copy_X=True,  # noqa: N803
        tol=0.0001,
        warm_start=False,
        positive=False,
        random_state=10,
        selection="cyclic",
    ):
        """
        Linear regression object constructor.

        The only differences between this implementation and sklearns are:
            1. normalize defaults to True. Normalizing variables is best practice when
            using ElasticNet since it includes weight regularization.

            2. random_state default to 10. Since random_state is not yet exposed
            through the CFML configuration panels, default seeding is necessary to
            guarantee consistency.
        """
        super().__init__(
            self,
            alpha,
            l1_ratio,
            fit_intercept,
            normalize,
            precompute,
            max_iter,
            copy_X,
            tol,
            warm_start,
            positive,
            random_state,
            selection,
        )
