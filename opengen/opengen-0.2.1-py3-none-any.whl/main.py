import opengen as og
import casadi.casadi as cs
import logging as lg

# Build parametric optimizer
# ------------------------------------
u = cs.SX.sym("u", 5)
p = cs.SX.sym("p", 2)
phi = og.functions.rosenbrock(u, p)
phi = 0
for i in range(4):
    phi += p[1] * (u[i+1] - u[i]**2)**2 \
           + (p[0] - u[i])**2
c = cs.vertcat(1.5 * cs.sin(u[0])
               - cs.cos(u[1] + u[2]),
               cs.fmax(u[2] + u[3] - 0.2, 0)**2)
bounds = og.constraints.Ball2(None, 0.73)

# problem = og.builder.Problem(u, p, phi) \
#     .with_penalty_constraints(c)        \
#     .with_constraints(bounds)

problem = og.builder.Problem(u, p, phi) \
    .with_aug_lagrangian_constraints(c, og.constraints.Zero(), og.constraints.BallInf(None, 1000000))        \
    .with_constraints(bounds)

build_config = og.config.BuildConfiguration()  \
    .with_build_directory("python_build") \
    .with_build_mode("debug")                  \
    .with_tcp_interface_config().with_open_version('*') \
    .with_build_c_bindings()
meta = og.config.OptimizerMeta()                   \
    .with_optimizer_name("nmpc")
solver_config = og.config.SolverConfiguration()    \
    .with_tolerance(1e-6)                          \
    .with_initial_tolerance(1e-4)                  \
    .with_delta_tolerance(1e-4)                    \
    .with_initial_penalty(1e3)                     \
    .with_penalty_weight_update_factor(1.5)        \
    .with_max_outer_iterations(40)                 \
    .with_max_inner_iterations(500)
builder = og.builder.OpEnOptimizerBuilder(
    problem, meta, build_config, solver_config)\
    .with_verbosity_level(lg.DEBUG)
builder.build()

# Use TCP server
# ------------------------------------
mng = og.tcp.OptimizerTcpManager('python_build/nmpc')
mng.start()

mng.ping()
solution = mng.call([1.0, 50.0])
print(solution)

mng.kill()