import numpy as _np
import pandas as _pd

from .__init__ import Simulator as _Simulator
from ..utils.plotting import heatmap_from_dataframe as _heatmap_from_dataframe

_DISPLACEMENT = 1e-4


def _find_steady_state(m, y0):
    """Conveniece wrapper around modelbase.ode.simulator.simulate_to_steady_state

    Parameters
    ----------
    m : modelbase.ode.Model
    y0 : dict
        Initial conditions
    """
    s = _Simulator(m, "scipy")
    s.set_initial_conditions(y0)
    return s.simulate_to_steady_state()


def get_substrate_elasticities(
    m, y0, metabolite, normalized=True, displacement=_DISPLACEMENT
):
    """Sensitivity of all rates to a change of the concentration of a metabolite.

    Also called epsilon-elasticities. Not in steady state!

    m: modelbase.ode.Model
    y0: dict
    metabolite: str

    Returns
    -------
        elasticities: numpy.ndarray

    .. math:: \epsilon_i^k = \frac{S_i}{v_k} \frac{\partial v_k}{\partial S_i}
    """
    if isinstance(y0, dict):
        y0 = y0.copy()
    else:
        y0 = m.get_full_concentration_dict(y0)
    c0 = y0[metabolite]
    rates = []
    for s in [c0 * (1 + _DISPLACEMENT), c0 * (1 - _DISPLACEMENT)]:
        y0[metabolite] = s
        rates.append(m.get_flux_array(0, m.get_full_concentration_dict(y0)))
    elasticity_coef = (rates[0] - rates[1]) / (2 * _DISPLACEMENT * c0)
    if normalized:
        y0[metabolite] = c0
        rates = m.get_flux_array(0, m.get_full_concentration_dict(y0))
        elasticity_coef *= c0 / rates
    return elasticity_coef


def get_substrate_elasticities_matrix(
    m, y0, normalized=True, displacement=_DISPLACEMENT
):
    """Sensitivity of all rates to a change of the concentration of all metabolites. Not in steady state!
    m: modelbase.ode.Model
    y0: dict
    metabolite: str

    Returns
    -------
        elasticities: numpy.ndarray

    .. math:: \epsilon_i^k = \frac{S_i}{v_k} \frac{\partial v_k}{\partial S_i}
    """
    elasticities = [
        get_substrate_elasticities(m, y0, metabolite, normalized, _DISPLACEMENT)
        for metabolite in m.get_compound_names()
    ]
    return _np.squeeze(_np.array(elasticities).T)


def get_substrate_elasticities_df(m, y0, normalized=True, displacement=_DISPLACEMENT):
    """Sensitivity of all rates to a change of the concentration of a metabolites. Not in steady state!
    m: modelbase.ode.Model
    y0: Dict
    metabolite: str

    Returns
    -------
        elasticities: pandas.DataFrame

    .. math:: \epsilon_i^k = \frac{S_i}{v_k} \frac{\partial v_k}{\partial S_i}
    """
    matrix = get_substrate_elasticities_matrix(m, y0, normalized, _DISPLACEMENT)
    return _pd.DataFrame(
        matrix, index=m.get_rate_names(), columns=m.get_compound_names()
    )


def get_parameter_elasticities(
    m, y0, parameter, normalized=True, displacement=_DISPLACEMENT, decimal_points=2
):
    """Sensitivity of all rates to a change of the parameter value. Not in steady state!
    m: modelbase.ode.Model
    y0: Dict
    parameter: str

    Returns
    -------
        elasticities: numpy.ndarray

    .. math:: \pi_m^k = \frac{p_m}{v_k} \frac{\partial v_k}{\partial p_m}
    """
    m = m.copy()
    p0 = m.get_parameter(parameter)
    rates = []
    for p in [p0 * (1 + _DISPLACEMENT), p0 * (1 - _DISPLACEMENT)]:
        m.update_parameters({parameter: p})
        rates.append(m.get_flux_array(0, m.get_full_concentration_dict(y0)))
    elasticity_coef = (rates[0] - rates[1]) / (2 * _DISPLACEMENT * p0)
    if normalized:
        m.update_parameters({parameter: p0})
        rates = m.get_flux_array(0, m.get_full_concentration_dict(y0))
        elasticity_coef *= p0 / rates
    return elasticity_coef


def get_parameter_elasticities_matrix(
    m, y0, normalized=True, displacement=_DISPLACEMENT
):
    """Sensitivity of all rate to a change of all parameter values. Not in steady state!
    m: modelbase.ode.Model
    y0: Dict
    parameter: str

    Returns
    -------
        elasticities: numpy.ndarray

    .. math:: \pi_m^k = \frac{p_m}{v_k} \frac{\partial v_k}{\partial p_m}
    """
    elasticities = [
        get_parameter_elasticities(m, y0, parameter, normalized, _DISPLACEMENT)
        for parameter in m.get_all_parameters()
    ]
    return _np.squeeze(_np.array(elasticities).T)


def get_parameter_elasticities_df(m, y0, displacement=_DISPLACEMENT):
    """Sensitivity of all rate to a change of all parameter values. Not in steady state!
    m: modelbase.ode.Model
    y0: Dict
    parameter: str

    Returns
    -------
        elasticities: pandas.DataFrame

    .. math:: \pi_m^k = \frac{p_m}{v_k} \frac{\partial v_k}{\partial p_m}
    """
    matrix = get_parameter_elasticities_matrix(m, y0, _DISPLACEMENT)
    return _pd.DataFrame(
        matrix, index=m.get_rate_names(), columns=m.get_all_parameters().keys()
    )


def get_concentration_response_coefficients(
    m, y0, parameter, normalized=True, displacement=_DISPLACEMENT
):
    """Response of the steady state concentrations to a small change of the given parameter m
    R_m^i = p_m / S_i^SS * delta S_i^SS / delta p_m

    Returns
    -------
        concentration response coefficients: numpy.ndarray

    .. math:: R_m^i = \frac{p_m}{S_i^{SS}} \frac{\partial S_i^{SS}}{\partial p_m}
    """
    m = m.copy()
    param_value = m.get_parameter(parameter)
    ss = []
    for val in [param_value * (1 + _DISPLACEMENT), param_value * (1 - _DISPLACEMENT)]:
        m.update_parameters({parameter: val})
        ss.append(_find_steady_state(m, y0))
    resp_coef = (ss[0] - ss[1]) / (2 * _DISPLACEMENT * param_value)
    if normalized:
        m.update_parameters({parameter: param_value})
        resp_coef *= param_value / _find_steady_state(m, y0)
    return resp_coef


def get_concentration_response_coefficients_matrix(
    m, y0, parameters, normalized=True, displacement=_DISPLACEMENT
):
    """Response of the steady state concentrations to a small change of the given parameter m
    R_m^i = p_m / S_i^SS * delta S_i^SS / delta p_m

    Returns
    -------
        concentration response coefficients: numpy.ndarray

    .. math:: R_m^i = \frac{p_m}{S_i^{SS}} \frac{\partial S_i^{SS}}{\partial p_m}
    """
    coefs = [
        get_concentration_response_coefficients(
            m, y0, parameter, normalized, _DISPLACEMENT
        )
        for parameter in parameters
    ]
    return _np.squeeze(_np.array(coefs).T)


def get_concentration_response_coefficients_df(
    m, y0, parameters, normalized=True, displacement=_DISPLACEMENT
):
    """Response of the steady state concentrations to a small change of the given parameter m
    R_m^i = p_m / S_i^SS * delta S_i^SS / delta p_m

    Returns
    -------
        concentration response coefficients: pandas.DataFrame

    .. math:: R_m^i = \frac{p_m}{S_i^{SS}} \frac{\partial S_i^{SS}}{\partial p_m}
    """
    matrix = get_concentration_response_coefficients_matrix(
        m, y0, parameters, normalized, _DISPLACEMENT
    )
    return _pd.DataFrame(matrix, index=m.get_compound_names(), columns=parameters)


def get_concentration_control_coefficients(
    m, y0, rate, rate_parameter, normalized=True, displacement=_DISPLACEMENT
):
    """Control of rate v_k(p_k) over concentration S_i

    Returns
    -------
        concentration control coefficients: numpy.ndarray

    .. math:: C_k^i = \frac{v_k}{S_i^{SS}} \frac{\partial S_i^{SS}}{\partial v_k}
    """
    R = get_concentration_response_coefficients(
        m, y0, rate_parameter, normalized=False, displacement=_DISPLACEMENT
    )

    # The elasticities have to be given in steady state
    SS = _find_steady_state(m, y0)
    y_SS = m.get_full_concentration_dict(SS)
    e = get_parameter_elasticities(
        m, y_SS, rate_parameter, normalized=False, displacement=_DISPLACEMENT
    )[m.get_rate_indexes(rate)]
    cc = R / e
    if normalized:
        vk = m.get_fluxes(0, y_SS)[rate]
        cc *= vk / SS
    return cc


def get_concentration_control_coefficients_matrix(
    m, y0, rates, parameters, normalized=True, displacement=_DISPLACEMENT
):
    """Control of rate v_k(p_k) over concentration S_i

    Returns
    -------
        concentration control coefficients: numpy.ndarray

    .. math:: C_k^i = \frac{v_k}{S_i^{SS}} \frac{\partial S_i^{SS}}{\partial v_k}
    """
    coefs = [
        get_concentration_control_coefficients(
            m, y0, rate, parameter, normalized, _DISPLACEMENT
        )
        for rate, parameter in zip(rates, parameters)
    ]
    return _np.squeeze(_np.array(coefs).T)


def get_concentration_control_coefficients_df(
    m, y0, rates, parameters, normalized=True, displacement=_DISPLACEMENT
):
    """Control of rate v_k(p_k) over concentration S_i

    Returns
    -------
        concentration control coefficients: pandas.DataFrame

    .. math:: C_k^i = \frac{v_k}{S_i^{SS}} \frac{\partial S_i^{SS}}{\partial v_k}
    """
    matrix = get_concentration_control_coefficients_matrix(
        m, y0, rates, parameters, normalized, _DISPLACEMENT
    )
    return _pd.DataFrame(matrix, index=m.get_compound_names(), columns=rates)


def get_flux_response_coefficients(
    m, y0, parameter, normalized=True, displacement=_DISPLACEMENT, decimal_points=2
):
    """Response of the steady state fluxes to a small change of the given parameter m
    R_m^j = p_m / J_j * delta J_j / delta p_m

    Returns
    -------
        flux response coefficients: numpy.ndarray

    .. math:: R_m^j = \frac{p_m}{J_j^{SS}} \frac{\partial J_j^{SS}}{\partial p_m}
    """
    m = m.copy()
    param_value = m.get_parameter(parameter)
    fluxes = []
    for val in [param_value * (1 + _DISPLACEMENT), param_value * (1 - _DISPLACEMENT)]:
        m.update_parameters({parameter: val})
        ss = _find_steady_state(m, y0)
        fluxes.append(m.get_flux_array(0, m.get_full_concentration_dict(ss)))
    resp_coef = (fluxes[0] - fluxes[1]) / (2 * _DISPLACEMENT * param_value)
    if normalized:
        m.update_parameters({parameter: param_value})
        ss = _find_steady_state(m, y0)
        resp_coef *= param_value / m.get_flux_array(
            0, m.get_full_concentration_dict(ss)
        )
    return resp_coef


def get_flux_response_coefficients_matrix(
    m, y0, parameters, normalized=True, displacement=_DISPLACEMENT
):
    """Response of the steady state fluxes to a small change of the given parameter m
    R_m^j = p_m / J_j * delta J_j / delta p_m

    Returns
    -------
        flux response coefficients: numpy.ndarray

    .. math:: R_m^j = \frac{p_m}{J_j^{SS}} \frac{\partial J_j^{SS}}{\partial p_m}
    """
    coefs = [
        get_flux_response_coefficients(m, y0, parameter, normalized, _DISPLACEMENT)
        for parameter in parameters
    ]
    return _np.squeeze(_np.array(coefs).T)


def get_flux_response_coefficients_df(
    m, y0, parameters, normalized=True, displacement=_DISPLACEMENT
):
    """Response of the steady state fluxes to a small change of the given parameter m
    R_m^j = p_m / J_j * delta J_j / delta p_m

    Returns
    -------
        flux response coefficients: numpy.ndarray

    .. math:: R_m^j = \frac{p_m}{J_j^{SS}} \frac{\partial J_j^{SS}}{\partial p_m}
    """
    matrix = get_flux_response_coefficients_matrix(
        m, y0, parameters, normalized, _DISPLACEMENT
    )
    return _pd.DataFrame(matrix, index=m.get_rate_names(), columns=parameters)


def get_flux_control_coefficients(
    m,
    y0,
    rate,
    rate_parameter,
    normalized=True,
    displacement=_DISPLACEMENT,
    decimal_points=2,
):
    """Control of rate v_k(p_k) over concentration S_i
    Returns
    -------
        flux control coefficients: numpy.ndarray

    .. math:: C_k^i = \frac{v_k}{S_i^{SS}} \frac{\partial S_i^{SS}}{\partial v_k}
    """
    R = get_flux_response_coefficients(
        m, y0, rate_parameter, normalized=False, displacement=_DISPLACEMENT
    )

    # The elasticities have to be given in steady state
    SS = _find_steady_state(m, y0)
    y_SS = m.get_full_concentration_dict(SS)
    e = get_parameter_elasticities(
        m, y_SS, rate_parameter, normalized=False, displacement=_DISPLACEMENT
    )[m.get_rate_indexes(rate)]
    cc = R / e
    if normalized:
        SS_fluxes = m.get_flux_array(0, y_SS)
        vk = SS_fluxes[m.get_rate_indexes(rate)]
        cc *= vk / SS_fluxes
    return cc


def get_flux_control_coefficients_matrix(
    m, y0, rates, parameters, normalized=True, displacement=_DISPLACEMENT
):
    """Control of rates v_k(p_k) over concentrations S_i

    Returns
    -------
        flux control coefficients: numpy.ndarray

    .. math:: C_k^i = \frac{v_k}{S_i^{SS}} \frac{\partial S_i^{SS}}{\partial v_k}
    """
    coefs = [
        get_flux_control_coefficients(m, y0, rate, parameter, normalized, _DISPLACEMENT)
        for rate, parameter in zip(rates, parameters)
    ]
    return _np.squeeze(_np.array(coefs).T)


def get_flux_control_coefficients_df(
    m, y0, rates, parameters, normalized=True, displacement=_DISPLACEMENT
):
    """Control of rates v_k(p_k) over concentrations S_i

    Returns
    -------
        flux control coefficients: pandas.DataFrame

    .. math:: C_k^i = \frac{v_k}{S_i^{SS}} \frac{\partial S_i^{SS}}{\partial v_k}
    """
    matrix = get_flux_control_coefficients_matrix(
        m, y0, rates, parameters, normalized, _DISPLACEMENT
    )
    return _pd.DataFrame(matrix, index=m.get_rate_names(), columns=rates)


def plot_concentration_response_coefficients(
    m, y0, parameters, ax=None, droprows=None, dropcols=None
):
    """Plots all concentration response coefficients for the given parameters.

    Parameters
    ----------
    m : modelbase.ode.Model
    y0 : dict
        Initial concentrations
    parameters : list[str]
        List of the parameter names
    ax : matplotlib.pyplot.axes, optional
        Axes on which to draw the plot
    droprows : list[str], optional
        List of rows (compounds) to drop from the plot
    dropcols : list[str], optional
        List of columns (parameters) to drop from the plot
    """
    df = get_concentration_response_coefficients_df(m, y0, parameters).round(2)
    if droprows is not None:
        df = df.drop(droprows, axis=0)
    if dropcols is not None:
        df = df.drop(dropcols, axis=1)
    return _heatmap_from_dataframe(
        df, title="Concentration Response Coefficients", ax=ax
    )


def plot_concentration_control_coefficients(
    m, y0, rates, parameters, ax=None, droprows=None, dropcols=None
):
    """Plots all concentration control coefficients for the given parameters.

    Parameters
    ----------
    m : modelbase.ode.Model
    y0 : dict
        Initial concentrations
    rates : list[str]
        Names of the rate functions
    parameters : list[str]
        List of the parameter names
    ax : matplotlib.pyplot.axes, optional
        Axes on which to draw the plot
    droprows : list[str], optional
        List of rows (compounds) to drop from the plot
    dropcols : list[str], optional
        List of columns (parameters) to drop from the plot
    """
    df = get_concentration_control_coefficients_df(m, y0, rates, parameters).round(2)
    if droprows is not None:
        df = df.drop(droprows, axis=0)
    if dropcols is not None:
        df = df.drop(dropcols, axis=1)
    return _heatmap_from_dataframe(
        df, title="Concentration Control Coefficients", ax=ax
    )


def plot_flux_response_coefficients(
    m, y0, parameters, ax=None, droprows=None, dropcols=None
):
    """Plots all flux response coefficients for the given parameters.

    Parameters
    ----------
    m : modelbase.ode.Model
    y0 : dict
        Initial concentrations
    parameters : list[str]
        List of the parameter names
    ax : matplotlib.pyplot.axes, optional
        Axes on which to draw the plot
    droprows : list[str], optional
        List of rows (compounds) to drop from the plot
    dropcols : list[str], optional
        List of columns (parameters) to drop from the plot
    """
    df = get_flux_response_coefficients_df(m, y0, parameters).round(2)
    if droprows is not None:
        df = df.drop(droprows, axis=0)
    if dropcols is not None:
        df = df.drop(dropcols, axis=1)
    return _heatmap_from_dataframe(df, title="Flux Response Coefficients", ax=ax)


def plot_flux_control_coefficients(
    m, y0, rates, parameters, ax=None, droprows=None, dropcols=None
):
    """Plots all flux control coefficients for the given parameters.

    Parameters
    ----------
    m : modelbase.ode.Model
    y0 : dict
        Initial concentrations
    rates : list[str]
        Names of the rate functions
    parameters : list[str]
        List of the parameter names
    ax : matplotlib.pyplot.axes, optional
        Axes on which to draw the plot
    droprows : list[str], optional
        List of rows (compounds) to drop from the plot
    dropcols : list[str], optional
        List of columns (parameters) to drop from the plot
    """
    df = get_flux_control_coefficients_df(m, y0, rates, parameters).round(2)
    if droprows is not None:
        df = df.drop(droprows, axis=0)
    if dropcols is not None:
        df = df.drop(dropcols, axis=1)
    return _heatmap_from_dataframe(df, title="Flux Control Coefficients", ax=ax)
