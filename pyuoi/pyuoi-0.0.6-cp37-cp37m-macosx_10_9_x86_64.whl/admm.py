def lasso_admm(
    X, y, lamb, rho=1., alpha=1.,
    max_iter=1000, abs_tol=1e-5, rel_tol=1e-3,
    verbose=False
):
    """Solve the Lasso optimization problem using Alternating Direction Method
    of Multipliers (ADMM) Convergence criteria are given in section 3.3.1 in
    the Boyd manuscript (equation 3.12).
    """
    n_samples, n_features = X.shape

    # initialize parameter estimates x/z and dual estimates u (equivalent to y)
    x = np.zeros((n_features, 1))
    z = np.zeros((n_features, 1))
    # dual; equivalent to y in most formulations
    u = np.zeros((n_features, 1))

    Xy = np.dot(X.T, y).reshape((n_features, 1))
    inv = np.linalg.inv(np.dot(X.T, X) + rho * np.identity(n_features))

    for iteration in range(max_iter):
        # update x estimates
        x = np.dot(inv, Xy + rho * (z - u))

        # handle the over-relaxation term
        z_old = np.copy(z)
        x_hat = alpha * x + (1 - alpha) * z_old

        # update z term with over-relaxation
        z = shrinkage(x=x_hat, threshold=lamb / rho)

        # update dual
        u += x_hat - z

        # check convergence using eqn 3.12
        r_norm = norm(x - z)
        s_norm = norm(rho * (z - z_old))

        eps_primal = np.sqrt(n_features) * abs_tol + \
            np.maximum(norm(x), norm(z)) * rel_tol
        eps_dual = np.sqrt(n_features) * abs_tol + norm(u) * rel_tol

        if (r_norm <= eps_primal) and (s_norm <= eps_dual):
            if verbose:
                print('Convergence: iteration %s' % iteration)
            break
    return z.ravel()


def shrinkage(x, threshold):
    return np.maximum(0., x - threshold) - np.maximum(0., -x - threshold)


def factor(X, rho):
    n_samples, n_features = X.shape
    if n_samples >= n_features:
        L = cholesky(np.dot(X.T, X) + rho * sparse.eye(n_features))
    else:
        L = cholesky(sparse.eye(n_samples) + 1. / rho * (np.dot(X, X.T)))
    L = sparse.csc_matrix(L)
    U = sparse.csc_matrix(L.T)
    return L, U