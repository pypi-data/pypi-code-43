from casadi import integrator, Function, MX, hcat, vertcat, vcat, linspace, veccat, DM, repmat, cumsum, inf
from .direct_method import DirectMethod
from numpy import nan
import numpy as np

class SamplingMethod(DirectMethod):
    def __init__(self, N=50, M=1, intg='rk', grid='uniform', dt_min=0, dt_max=inf, intg_options=None, **kwargs):
        DirectMethod.__init__(self, **kwargs)
        self.N = N
        self.M = M
        self.intg = intg
        self.intg_options = {} if intg_options is None else intg_options
        self.grid = grid

        self.X = []  # List that will hold N+1 decision variables for state vector
        self.U = []  # List that will hold N decision variables for control vector
        self.T = None
        self.t0 = None
        self.P = []
        self.V = None
        self.V_control = []
        self.V_states = []
        self.P_control = []

        self.poly_coeff = None  # Optional list to save the coefficients for a polynomial
        self.xk = []  # List for intermediate integrator states
        self.q = 0
        self.dt_min = dt_min
        self.dt_max = dt_max

    def discrete_system(self, stage):
        f = stage._ode()

        # Coefficient matrix from RK4 to reconstruct 4th order polynomial (k1,k2,k3,k4)
        # nstates x (4 * M)
        poly_coeffs = []

        t0 = MX.sym('t0')
        T = MX.sym('T')
        DT = T / self.M

        # Size of integrator interval
        X0 = f.mx_in("x")            # Initial state
        U = f.mx_in("u")             # Control
        P = f.mx_in("p")
        Z = f.mx_in("z")

        X = [X0]
        if hasattr(self, 'intg_'+ self.intg):
            intg = getattr(self, "intg_" + self.intg)(f, X0, U, P, Z)
        else:
            intg = self.intg_builtin(f, X0, U, P, Z)
        assert not intg.has_free()

        # Compute local start time
        t0_local = t0
        quad = 0
        for j in range(self.M):
            intg_res = intg(x0=X[-1], u=U, t0=t0_local, DT=DT, p=P)
            X.append(intg_res["xf"])
            quad = quad + intg_res["qf"]
            poly_coeffs.append(intg_res["poly_coeff"])
            t0_local += DT

        ret = Function('F', [X0, U, T, t0, P], [X[-1], hcat(X), hcat(poly_coeffs), quad],
                       ['x0', 'u', 'T', 't0', 'p'], ['xf', 'Xi', 'poly_coeff', 'qf'])
        assert not ret.has_free()
        return ret

    def intg_rk(self, f, X, U, P, Z):
        assert Z.is_empty()
        DT = MX.sym("DT")
        t0 = MX.sym("t0")
        # A single Runge-Kutta 4 step
        k1 = f(x=X, u=U, p=P, t=t0, z=Z)
        k2 = f(x=X + DT / 2 * k1["ode"], u=U, p=P, t=t0+DT/2, z=Z)
        k3 = f(x=X + DT / 2 * k2["ode"], u=U, p=P, t=t0+DT/2)
        k4 = f(x=X + DT * k3["ode"], u=U, p=P, t=t0+DT)

        f0 = k1["ode"]
        f1 = 2/DT*(k2["ode"]-k1["ode"])/2
        f2 = 4/DT**2*(k3["ode"]-k2["ode"])/6
        f3 = 4*(k4["ode"]-2*k3["ode"]+k1["ode"])/DT**3/24
        poly_coeff = hcat([X, f0, f1, f2, f3])
        return Function('F', [X, U, t0, DT, P], [X + DT / 6 * (k1["ode"] + 2 * k2["ode"] + 2 * k3["ode"] + k4["ode"]), poly_coeff, DT / 6 * (k1["quad"] + 2 * k2["quad"] + 2 * k3["quad"] + k4["quad"])], ['x0', 'u', 't0', 'DT', 'p'], ['xf', 'poly_coeff', 'qf'])

    def intg_builtin(self, f, X, U, P, Z):
        # A single CVODES step
        DT = MX.sym("DT")
        t = MX.sym("t")
        t0 = MX.sym("t0")
        res = f(x=X, u=U, p=P, t=t0+t*DT, z=Z)
        data = {'x': X, 'p': vertcat(U, DT, P, t0), 'z': Z, 't': t, 'ode': DT * res["ode"], 'quad': DT * res["quad"], 'alg': res["alg"]}
        options = dict(self.intg_options)
        if self.intg in ["collocation"]:
            options["number_of_finite_elements"] = 1
        I = integrator('intg_cvodes', self.intg, data, options)
        res = I.call({'x0': X, 'p': vertcat(U, DT, P, t0)})
        return Function('F', [X, U, t0, DT, P], [res["xf"], MX(), res["qf"]], ['x0', 'u', 't0', 'DT', 'p'], ['xf', 'poly_coeff','qf'])

    def register(self, stage):
        if self.grid=='free':
            Ts = stage.variable(grid='states')
            stage.subject_to(stage.at_t0(Ts)==stage.t0)
            stage.subject_to(stage.at_tf(Ts)==stage.tf)
            stage.set_initial(Ts, np.linspace(stage.t0_init, stage.t0_init+stage.T_init, self.N+1))

    def transcribe(self, stage, opti):
        """
        Transcription is the process of going from a continuous-time OCP to an NLP
        """

        self.add_variables(stage, opti)
        self.add_parameter(stage, opti)

        # Create time grid (might be symbolic)
        if self.grid=='free':
            self.control_grid = hcat(self.V_states[0])
            for k in range(self.N):
                stage.subject_to(self.dt_min<=(self.V_states[0][k+1]-self.V_states[0][k]<=self.dt_max))
        else:
            self.control_grid = linspace(MX(self.t0), self.t0 + self.T, self.N + 1)

        self.add_constraints(stage, opti)
        self.add_objective(stage, opti)
        self.set_initial(stage, opti)
        self.set_parameter(stage, opti)
        placeholders = stage._bake_placeholders(self)
        return placeholders

    def fill_placeholders_integral_control(self, stage, expr, *args):
        r = 0
        for k in range(self.N):
            dt = self.control_grid[k + 1] - self.control_grid[k]
            r = r + self.eval_at_control(stage, expr, k)*dt
        return r

    def fill_placeholders_sum_control(self, stage, expr, *args):
        r = 0
        for k in range(self.N):
            r = r + self.eval_at_control(stage, expr, k)
        return r

    def fill_placeholders_at_t0(self, stage, expr, *args):
        return self.eval_at_control(stage, expr, 0)

    def fill_placeholders_at_tf(self, stage, expr, *args):
        return self.eval_at_control(stage, expr, -1)

    def fill_placeholders_t0(self, stage, expr, *args):
        return self.t0

    def fill_placeholders_T(self, stage, expr, *args):
        return self.T

    def add_objective(self, stage, opti):
        opti.add_objective(self.eval(stage, stage._objective))

    def add_time_variables(self, stage, opti):
        if stage.is_free_time():
            self.T = opti.variable()
            opti.set_initial(self.T, stage.T_init)
        else:
            self.T = stage._T

        if stage.is_free_starttime():
            self.t0 = opti.variable()
            opti.set_initial(self.t0, stage.t0_init)
        else:
            self.t0 = stage._t0

    def get_p_control_at(self, stage, k=-1):
        return veccat(*[p[:,k] for p in self.P_control])

    def get_v_control_at(self, stage, k=-1):
        return veccat(*[v[k] for v in self.V_control])

    def get_v_states_at(self, stage, k=-1):
        return veccat(*[v[k] for v in self.V_states])

    def eval(self, stage, expr):
        return stage._expr_apply(expr, p=veccat(*self.P), v=self.V)

    def eval_at_control(self, stage, expr, k):
        if k==-1 or k==self.N-1:
            du = 0*self.U[-1]
        else:
            du = self.U[k+1]-self.U[k]
        du = du[:stage.du.shape[0]]
        return stage._expr_apply(expr, du=du, x=self.X[k], xq=self.q if k==-1 else nan, u=self.U[k], p_control=self.get_p_control_at(stage, k), v=self.V, p=veccat(*self.P), v_control=self.get_v_control_at(stage, k), v_states=self.get_v_states_at(stage, k), t=self.control_grid[k])

    def eval_at_integrator(self, stage, expr, k, i):
        if k==-1 or k==self.N-1:
            du = 0*self.U[-1]
        else:
            du = self.U[k+1]-self.U[k]
        du = du[:stage.du.shape[0]]
        return stage._expr_apply(expr, du=du, x=self.xk[k*self.M + i], u=self.U[k], p_control=self.get_p_control_at(stage, k), v=self.V, p=veccat(*self.P), v_control=self.get_v_control_at(stage, k),  v_states=self.get_v_states_at(stage, k), t=self.control_grid[k])
    
    def set_initial(self, stage, opti):
        for var, expr in stage._initial.items():
            for k in list(range(self.N))+[-1]:
                target = self.eval_at_control(stage, var, k)
                value = DM(opti.debug.value(self.eval_at_control(stage, expr, k), opti.initial()))
                if target.numel()*(self.N)==value.numel():
                    if repmat(target, self.N, 1).shape==value.shape:
                        value = value[k,:]
                    elif repmat(target, 1, self.N).shape==value.shape:
                        value = value[:,k]

                if target.numel()*(self.N+1)==value.numel():
                    if repmat(target, self.N+1, 1).shape==value.shape:
                        value = value[k,:]
                    elif repmat(target, 1, self.N+1).shape==value.shape:
                        value = value[:,k]
                opti.set_initial(target, value)

    def set_value(self, stage, opti, parameter, value):
        for i, p in enumerate(stage.parameters['']):
            if parameter is p:
                opti.set_value(self.P[i], value)
        for i, p in enumerate(stage.parameters['control']):
            if parameter is p:
                opti.set_value(self.P_control[i], value)

    def add_parameter(self, stage, opti):
        for p in stage.parameters['']:
            self.P.append(opti.parameter(p.shape[0], p.shape[1]))
        for p in stage.parameters['control']:
            self.P_control.append(opti.parameter(p.shape[0], self.N * p.shape[1]))

    def set_parameter(self, stage, opti):
        for i, p in enumerate(stage.parameters['']):
            opti.set_value(self.P[i], stage._param_vals[p])
        for i, p in enumerate(stage.parameters['control']):
            opti.set_value(self.P_control[i], stage._param_vals[p])
