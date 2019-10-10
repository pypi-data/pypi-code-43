import cvxpy as cp
import numpy as np

IP_SOLUTION_OPTIMAL = 'optimal'
IP_SOLUTION_TIME_BOUND = 'time_bound'


class IPSolverParameters:
    def __init__(
            self,
            alpha_nu=1000.0,
            alpha_llc=10.0,
            alpha_l12=400.0,
            alpha_prev=10.0,
            alpha_oversubscription=10.0):
        self.alpha_nu = alpha_nu
        self.alpha_llc = alpha_llc
        self.alpha_l12 = alpha_l12
        self.alpha_prev = alpha_prev
        self.alpha_oversubscription = alpha_oversubscription

    def __str__(self):
        return str(vars(self))


def get_mip_solver_extra_args(solver, max_runtime_secs, tol_obj, mip_gap):
    extra_args = {}
    if solver == 'GLPK_MI':
        extra_args = {
            "tm_lim": int(1000 * max_runtime_secs),
            "fp_heur": "GLP_ON",
            "ps_heur": "GLP_ON",
            "pp_tech": "GLP_PP_ALL",
            "bt_tech": "GLP_BT_BPH",
            "tol_obj": tol_obj,
            "mir_cuts": "GLP_ON",
            "binarize": "GLP_ON",
            "presolve": "GLP_ON",
            "mip_gap": mip_gap,
        }
    elif solver == 'MOSEK':
        extra_args = {"mosek_params": {
            "MSK_DPAR_MIO_MAX_TIME": max_runtime_secs,
            "MSK_IPAR_NUM_THREADS": 1,
            "MSK_DPAR_MIO_TOL_REL_GAP": mip_gap
        }}
    elif solver == 'GUROBI':
        extra_args = {
            "TimeLimit": max_runtime_secs,
            "Threads": 2,
            "MIPGap": mip_gap,
            "ConcurrentMIP": 2,
            "PreSparsify": 1,
            "ImproveStartTime": 2 * max_runtime_secs / 3
        }
    return extra_args


class PlacementSolver:

    def __init__(self, total_available_cus, num_sockets, solver_params=IPSolverParameters(), backend='GLPK_MI'):
        self.total_available_cus = total_available_cus
        self.num_sockets = num_sockets
        self.solver_params = solver_params
        self.backend = backend

    def optimize(
            self,
            requested_cus,
            previous_allocation=None,
            use_per_workload=None,
            verbose=False,
            compute_placement_statistics=False,
            max_runtime_secs=1,
            tol_obj=1e-1,
            mip_gap=0.05):
        """
        This function will find the optimal placement of workloads on the compute units of the instance,
        potentially starting from an initial allocation state (in which case it will also try to minimize
        the changes required to the current placement to satisfy the new request).
        The algorithm will strive to balance actual CPU usage per socket and core.
        It also supports oversubscription.

        Arguments:
            - requested_cus: array of integers representing the number of compute units requested by each workload. Ex: [2,4,8,4]
            - total_available_cus: total # of compute units on the instance
            - num_sockets: # of NUMA sockets on the instance
            - previous allocation: array of assignment vectors from a previous placement
            - use_per_workload: actual (or forecasted) CPU use per workload
            - verbose: flag to turn on verbose output of the MIP solver
            - max_runtime_secs: the maximum runtime allowed to compute a solution (if supported by the solver)

        Returns:
            - an array of binary assignment vectors. For example: [[0, 1, 0, 0], [1, 0, 1, 0]] could be a possible
            return value for a call where requested_cus=[1, 2] and total_available_cus=4
            This would mean that the first workload was assigned the compute unit with index 1, and that
            the second workload was assigned the compute units with indices 0 and 3
            - status of the solution ("optimal" or "time_bound")
        """

        d = self.total_available_cus
        n = self.num_sockets
        c = d // 2  # number of physical cores
        b = self.total_available_cus // n  # number of CUs per socket
        k = len(requested_cus)

        if self.total_available_cus % 2 != 0:
            raise ValueError("Odd number of compute units on the instance not allowed."
                            " we assume that there always are 2 hyper-threads per physical core.")

        r = np.array(requested_cus)

        prev_M = None
        if previous_allocation is not None:
            prev_M = np.zeros((d, k), dtype=np.int32)
            for j, v in enumerate(previous_allocation):
                if j == k:  # means that previous one was bigger, we removed a task
                    break
                for i in range(d):
                    if v[i] > 0.5:
                        prev_M[i, j] = 1

        # Optimal boolean assignment matrix we wish to find
        M = cp.Variable((d, k), boolean=True)

        # Auxiliary variables needed
        X = cp.Variable((n, k), integer=True)
        Y = cp.Variable(c, integer=True)
        U = cp.Variable(1)
        Z = cp.Variable(c, boolean=True)

        # 1) Penalize placements where workloads span multiple sockets
        cost_NU = -(self.solver_params.alpha_nu / (n * k)) * cp.sum(X)

        # 2) Try to even the # of busy CPUs per socket
        cost_LLC = (self.solver_params.alpha_llc / n) * sum([cp.abs(U - cp.sum(M[t * b: (t + 1) * b, :])) for t in range(n)])

        # 3) Penalize full cores (because it means more L1/L2 thrashing)
        cost_L12 = (self.solver_params.alpha_l12 / c) * cp.max(Y)

        # 5) [optional] if starting from a previous allocation,
        # penalize placements that move assignements too much
        # compared to reference placement.
        cost_prev = None
        if prev_M is not None:
            cost_prev = (self.solver_params.alpha_prev / (d * k)) * cp.sum(cp.abs(M - prev_M))

        # The placement has to satisfy the requested # of units for each workload
        CM1 = [M.T * np.ones((d,)) == r]

        if sum(requested_cus) < d:
            # Each compute unit can only be assigned to a single workload
            CM2 = [M * np.ones((k, 1)) <= np.ones((d, 1))]
            cost_oversubscription = None
        else:
            CM2 = []
            cost_oversubscription = (self.solver_params.alpha_oversubscription / k) * cp.sum(cp.abs(M * np.ones((k, 1))))

        # Extra variables constraints (coming from linearization of min/-max operators)
        CX1 = [X[t, j] <= (1.0 / max(r[j], 1)) * cp.sum(M[t * b: (t + 1) * b, j]) for t in range(n) for j in range(k)]
        CX2 = [X <= 1]

        CY1 = [Y[l] >= -1 + cp.sum(M[2 * l, :]) + cp.sum(M[2 * l + 1, :]) for l in range(c)]
        CY2 = [Y >= 0]

        # Don't leave cores empty
        min_cores_req = np.sum(r)
        CC = [Z[l] <= cp.sum(M[2 * l: 2 * l + 1, :]) for l in range(c)] + [cp.sum(Z) >= min(min_cores_req, c)]

        if np.sum(r) >= d:
            # don't leave threds empty
            CC += [cp.sum(M[i, :]) >= 1 for i in range(d)]

        if use_per_workload is not None:
            weights = np.ones((k,), dtype=np.float32)
            for j, use in enumerate(use_per_workload):
                if not np.isnan(r[j]) and r[j] > 0:
                    weights[j] = use / r[j]
                else:
                    weights[j] = 1

            # Even CPU usage per core:
            TT = cp.Variable(1)
            RW1 = np.vstack([weights.T] * 2)
            cost_L12 = (self.solver_params.alpha_l12 / c) * sum(
                [cp.abs(TT - cp.sum(cp.multiply(M[2 * t: 2 * t + 2, :], RW1))) for t in range(c)])

        cost = cost_NU + cost_LLC + cost_L12
        if cost_prev is not None:
            cost += cost_prev
        if cost_oversubscription is not None:
            cost += cost_oversubscription

        constraints = CM1 + CM2 + CY1 + CY2 + CX1 + CX2 + CC

        prob = cp.Problem(cp.Minimize(cost), constraints)

        if verbose:
            print("Number of scalar variables in problem: ", prob.size_metrics.num_scalar_variables)
        try:
            extra_args = get_mip_solver_extra_args(self.backend, max_runtime_secs, tol_obj, mip_gap)
            prob.solve(solver=self.backend, verbose=verbose, **extra_args)
        except Exception as e:
            msg = "Solver crashed. (requested_cus=%s , previous_allocation=%s)" % (
                requested_cus, previous_allocation)
            raise Exception(msg).with_traceback(e.__traceback__)

        if prob.status not in ('optimal', 'optimal_inaccurate'):
            raise Exception("Could not solve the integer program: `%s`" % (prob.status,))

        status = IP_SOLUTION_OPTIMAL if prob.status == 'optimal' else IP_SOLUTION_TIME_BOUND

        res = [None] * (len(requested_cus))
        for i, e in enumerate(M.value.T):
            res[i] = [1 if u > 0.5 else 0 for u in e]

        sol_stats = None
        if compute_placement_statistics:
            sol_stats = SolutionStatistics(res, weights, k, c, n, b)
        return res, status, prob, sol_stats

class SolutionStatistics:
    def __init__(self, res, weights, k, c, n, b):
        usage_per_core = np.full(c, np.nan, dtype=np.float32)
        for l in range(c):
            s = 0.0
            for j, alloc in enumerate(res):
                if alloc[2 * l] == 1:
                    s += weights[j]
                if alloc[2 * l + 1] == 1:
                    s += weights[j]
            if s > 0:
                usage_per_core[l] = s
        self.usage_per_core = usage_per_core

        usage_per_socket = np.full(n, np.nan, dtype=np.float32)
        for t in range(n):
            s = 0.0
            for j, alloc in enumerate(res):
                for u in range(t * b, (t + 1) * b):
                    if alloc[u] == 1:
                        s += weights[j]
            if s > 0:
                usage_per_socket[t] = s
        self.usage_per_socket = usage_per_socket

    def __str__(self):
        return str(vars(self))
