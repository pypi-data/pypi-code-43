"""
   Copyright 2019 Riley John Murray

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""
from sageopt.coniclifts.standards import constants as CL_CONSTANTS
from sageopt.coniclifts.problems.solvers.ecos import ECOS
from sageopt.coniclifts.problems.solvers.mosek import Mosek
from sageopt.coniclifts.compilers import compile_problem
from sageopt.coniclifts.base import Expression
import numpy as np
import time


class Problem(object):
    """
    A representation for a convex optimization problem. When this Problem object is constructed,
    the constraints are immediately compiled into a flattened conic representation. This compilation
    process may take some time for large problems.

    Parameters
    ----------
    objective_sense : str
        Either coniclifts.MIN or coniclifts.MAX

    objective_expr : Expression
        The function to minimize or maximize. ScalarExpressions and real numeric types
        are also accepted. The final (cast) expression must be linear in its Variables.

    constraints : list of coniclifts.Constraint
        Variables appearing in objective_expr are subject to Constraint objects in this list.

    Attributes
    ----------
    objective_sense: str

        The value passed by the user to the constructor.

    objective_expr : Expression

        The value passed by the user to the constructor.

    constraints : list of coniclifts.Constraint

        The value passed by the user to the constructor.

    A : CSC-format sparse matrix

        The matrix in the flattened conic representation of the feasible set.

    b : ndarray

        The offset vector in the flattened conic representation of the feasible set.

    K : list of coniclifts.Cone

        The cartesian product of these cones (in order) defines the convex cone appearing
        in the flattened conic representation of the feasible set.

    all_variables : list of coniclifts.Variable

        All Variable objects needed to represent the feasible set. This includes user-declared
        Variables, and Variables which were required to write the problem in terms of coniclifts
        primitives. It is recommended to access this list by calling ``self.variables()``.

    variable_map : Dict[str,ndarray]

        A map from a Variable's ``name`` field to a numpy array. If ``myvar``
        is a coniclifts Variable appearing in the system defined by ``constraints``,
        then a point ``x`` satisfying :math:`A x + b \in K` maps to a feasible value for
        ``myvar`` by ::

            x0 = np.hstack([x, 0])
            myvar_val = x0[variable_map[myvar.name]]

        In particular, we guarantee ``myvar.shape == variable_map[myvar.name].shape``.
        Augmenting ``x`` by zero to create ``x0`` reflects a convention that if a component of
        a Variable does not affect the constraints, that component is automatically assigned
        the value zero.

    variable_values : Dict[str, ndarray]

        A map from a Variable's ``name`` field to a numpy array, containing a feasible
        value for that Variable for this problem's constraints.

    solver_apply_data : Dict[str,dict]

        A place to store metadata during a call to ``self.solve(cache_apply_data=True)``.

    solver_raw_output : Dict[str,dict]

        A place to store metadata during a call to ``self.solve(cache_raw_output=True)``.

    metadata : dict

        A place for users to store metadata produced when constructing this Problem.

    value : float

        The objective value from the last call to ``self.solve``. Can be a float,
         ``np.inf``, ``-np.inf``, or ``np.NaN``.

    status : str

        The problem status from the last call to ``self.solve``.
        Either ``coniclifts.SOLVED`` or ``coniclifts.INACCURATE`` or ``coniclifts.FAILED``.

    Notes
    -----

    Problem status being ``coniclifts.SOLVED`` does not mean that the decision variables have
    been assigned specific values. It only means that the solver returned a normal status code
    (i.e. that the solver didn't run into numerical difficulties). If a solver return code
    indicates the problem is "infeasible" or "unbounded", we still set
    ``self.status = coniclifts.SOLVED``. Therefore it is important to check that
    ``self.status == coniclifts.SOLVED`` and that ``-np.inf < self.value < np.inf`` before
    accessing a Variable's value.
    """

    _SOLVERS_ = {'ECOS': ECOS(), 'MOSEK': Mosek()}

    _SOLVER_ORDER_ = ['MOSEK', 'ECOS']

    def __init__(self, objective_sense, objective_expr, constraints):
        self.objective_sense = objective_sense
        if not isinstance(objective_expr, Expression):
            objective_expr = Expression(objective_expr)
        self.objective_expr = objective_expr
        self.constraints = constraints
        self.timings = dict()
        t = time.time()
        c, A, b, K, variable_map, all_vars = compile_problem(objective_expr, constraints)
        if objective_sense == CL_CONSTANTS.minimize:
            self.c = c
        else:
            self.c = -c
        self.timings['compile_time'] = time.time() - t
        self.A = A
        self.b = b
        self.K = K
        self.all_variables = all_vars
        self.variable_map = variable_map
        self.variable_values = dict()
        self.solver_apply_data = dict()
        self.solver_raw_output = dict()
        self.status = None  # "solved", "inaccurate", or "failed"
        self.value = np.NaN
        self.metadata = dict()
        self.default_options = {'cache_apply_data': False, 'cache_raw_output': False,
                                'destructive': False, 'compilation_options': dict(),
                                'verbose': True}
        pass

    def solve(self, solver=None, **kwargs):
        """
        Parameters
        ----------
        solver : str
            None or ``'MOSEK'`` or ``'ECOS'``. Defaults to the first installed solver found in
            ``Problem._SOLVER_ORDER_``.

        Returns
        -------
        status : str

            Either ``coniclifts.SOLVED`` or ``coniclifts.INACCURATE`` or ``coniclifts.FAILED``.
            Refer to the Notes of the Problem class for the meanings of these values.

        value : float

            The optimal objective value reported by the solver. Can be a float, ``-np.inf``,
            ``np.inf``, or ``np.NaN``.

        Notes
        -----

        Keyword arguments.

            cache_apply_data
        """
        if solver is None:
            for svr in Problem._SOLVER_ORDER_:
                if Problem._SOLVERS_[svr].is_installed():
                    solver = svr
                    break
        if solver is None:
            raise RuntimeError('No acceptable solver is installed.')
        options = self.default_options.copy()
        options.update(kwargs)
        solver_object = Problem._SOLVERS_[solver]
        if not solver_object.is_installed():
            raise RuntimeError('Solver "' + solver + '" is not installed.')
        self.timings[solver] = dict()

        # Finish solver-specific compilation
        t0 = time.time()
        data, inv_data = solver_object.apply(self.c, self.A, self.b, self.K,
                                             options['destructive'],
                                             options['compilation_options'])
        self.timings[solver]['apply'] = time.time() - t0
        if options['cache_apply_data']:
            self.solver_apply_data[solver] = (data, inv_data)

        # Solve the problem
        t1 = time.time()
        raw_result = solver_object.solve_via_data(data, options)
        self.timings[solver]['solve_via_data'] = time.time() - t1
        if options['cache_raw_output']:
            self.solver_raw_output[solver] = raw_result
        parsed_result = solver_object.parse_result(raw_result, inv_data, self.variable_map)
        self.status = parsed_result[0]
        self.variable_values = parsed_result[1]

        # Load values into ScalarVariable objects.
        if len(self.variable_values) > 0:
            for v in self.all_variables:
                if v.name in self.variable_values:
                    var_val = self.variable_values[v.name]
                    v.set_scalar_variables(var_val)
        else:
            for v in self.all_variables:
                nans = np.NaN * np.empty(v.shape)
                v.set_scalar_variables(nans)

        # Record objective value
        if self.status in {CL_CONSTANTS.solved, CL_CONSTANTS.inaccurate}:
            if self.objective_sense == CL_CONSTANTS.minimize:
                self.value = parsed_result[2]
            else:
                self.value = -parsed_result[2]
        else:
            self.value = np.NaN

        self.timings[solver]['total'] = time.time() - t0
        return self.status, self.value

    def variables(self):
        """
        Return a shallow copy of ``self.all_variables``.

        This function is provided to match the syntax of CVXPY Problem objects.
        """
        shallow_copy = [v for v in self.all_variables]
        return shallow_copy


