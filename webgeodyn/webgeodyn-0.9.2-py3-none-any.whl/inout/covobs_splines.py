import os
import glob
import numpy as np
import re
import scipy.signal
import scipy.interpolate


def build_operator_spl_to_gnm(t_gnm, t_spl, spl_order, deriv=0):
    """
    Builds the operator A linking B-splines coefficients to gnm

    .. math::

        g_n^m = A \tilde{g}_{spl}

    :param t_gnm: Array of times at which the gnm are given
    :type t_gnm: np.ndarray (dim: N_gnm)
    :param t_spl: Array giving the knot times of the splines
    :type t_spl: np.ndarray (dim: N_spl)
    :param spl_order: Order of the splines (passed to scipy.bspline)
    :type spl_order: int
    :param deriv: If equal to 1, the operator will link spline coeffs to the derivative of gnms. Default: 0.
    :type deriv: int
    :return: Operator linking the B-splines coefficients to the gnms
    :rtype: np.ndarray (dim: N_gnm x N_spl)
    """
    N_gnm = len(t_gnm)
    N_spl = len(t_spl)

    if N_spl <= 1:
        raise ValueError('Too few spline knots were given !')

    knot_spacing = t_spl[1] - t_spl[0]

    spl_eval_fc = eval_derivative_spline if deriv == 1 else eval_spline

    A = np.zeros((N_gnm, N_spl))
    for i, t_i in enumerate(t_gnm):
        for j, t_j in enumerate(t_spl):
            A[i, j] = spl_eval_fc(date_to_eval=t_i, center_date=t_j, spl_order=spl_order, knot_spacing=knot_spacing)

    return A


def build_gnm_from_file(file_name, dt=0.5, with_derivatives=False):
    """
    Builds gnm from the spline coeffs stored in a file. The timestep of the resulting dates can be changed.

    :param file_name: Name of the file where the spline coeffs are stored
    :type file_name: str
    :param dt: Timestep of the evaluation dates (default: 0.5)
    :type dt: float
    :param with_derivatives: If True, returns as well dgnm/dt and d2gnm/dt2 evaluated from derivative of splines
    :type with_derivatives: bool
    :return: evaluation dates and the gnm at these dates (and its first and second derivative if with_derivatives is True)
    :rtype: np.array (dim: n_dates), np.array (dim: n_dates x n_gnm) (, np.array (dim: n_dates), np.array (dim: n_dates x n_gnm))
    """
    center_dates, spl_coeffs, spl_order, knot_sp = read_spline_coeffs_file(file_name)
    eval_dates = np.arange(center_dates[spl_order//2+1], center_dates[-spl_order//2-1], dt)
    return build_gnm_from_spline_coeffs(eval_dates, center_dates, spl_coeffs, spl_order, with_derivatives)


def eval_spline(date_to_eval, center_date, spl_order, knot_spacing):
    """ Evaluates a spline at date_to_eval.
    The spline is of order spl_order, spacing knot_spacing and centered on center_date."""
    normalised_X = (date_to_eval - center_date) / knot_spacing
    return scipy.signal.bspline(normalised_X, spl_order)


def eval_derivative_spline(date_to_eval, center_date, spl_order, knot_spacing):
    """ Evaluates the derivative of a spline at date_to_eval.
    The spline from which the derivative is computed is of order spl_order, spacing knot_spacing and centered on center_date."""

    def t_iplus(n):
        return center_date + n*knot_spacing

    normalised_X0 = (date_to_eval - t_iplus(-0.5)) / knot_spacing
    normalised_X1 = (date_to_eval - t_iplus(0.5)) / knot_spacing
    term1 = scipy.signal.bspline(normalised_X0, spl_order-1)/(t_iplus(spl_order) - t_iplus(0))
    term2 = scipy.signal.bspline(normalised_X1, spl_order-1)/(t_iplus(spl_order+1) - t_iplus(1))
    return spl_order*(term1 - term2)


def get_date_indexes_for_spl_eval(eval_date, spl_dates, spl_order):
    """ Returns the indexes of the dates of spl_dates needed to evaluate the value at eval_date."""
    eval_date_index = np.searchsorted(spl_dates, eval_date)
    return np.arange(eval_date_index - spl_order//2 - 1, eval_date_index + spl_order//2 + 1)


def get_full_knots(center_knots, spl_order, n):
    """
    Builds the full knots array (n+spl_order+1) from a subset of knots assumed to be the center of the full knots array.

    :param center_knots: center of the full knots array
    :type center_knots: np.array
    :param spl_order: order of the splines
    :type spl_order: int
    :param n: number of spline coeffs
    :type n: int
    :return:
    :rtype:
    """
    # Check if len(knots) = nb_dates + spl_order + 1
    mismatch = (n + spl_order + 1) - len(center_knots)

    if mismatch == 0:
        # If no mismatch, the center knots are the full knots
        return center_knots
    else:
        # Else add appropriate number of knots at the beginning and the end
        dt_knot = center_knots[1] - center_knots[0]
        full_knots = np.arange(center_knots[0] - mismatch//2 * dt_knot, center_knots[-1] + (mismatch//2 + 1) * dt_knot, dt_knot)
        return full_knots


def build_gnm_from_spline_coeffs_old(dates_for_eval, spl_dates, spl_coeffs, spl_order, with_derivative, all_splines=False):
    """
    Old manual method to build the gnm from the spline coeffs and the parameters of splines (center_dates, order, spacing).
    This method uses scipy.signal.bspline to evaluate manually the splines.

    :param dates_for_eval: Dates where the splines must be computed
    :type dates_for_eval: np.array (dim: Nt)
    :param spl_dates: Dates of the splines (knots)
    :type spl_dates: np.array (dim: Nspl)
    :param spl_coeffs: Coefficients of the data in the Bspline basis
    :type spl_coeffs: np.array (dim: Nspl x Nb)
    :param spl_order: Order of the used splines
    :type spl_order: int
    :param with_derivative: If True, returns the reconstructed dgnm/dt evaluated from derivative of splines
    :type with_derivative: bool
    :param all_splines: If True, uses all splines to reconstruct the gnm (For debugging purposes. Default is False).
    :type all_splines: bool
    :return: Dates, gnm evaluated from splines (and derivative of gnm evaluated from the derivative of splines if with_derivative is True)
    :rtype: np.array (dim: Nt), np.array (dim: Nt x Nb) (, np.array (dim: Nt x Nb))
    """
    n_spl_dates, Nb = spl_coeffs.shape
    assert n_spl_dates == spl_dates.shape[0]
    knot_spacing = spl_dates[1] - spl_dates[0]

    if all_splines:
        date_index_method = lambda eval_date, spl_dates, spl_order: range(len(spl_dates))
    else:
        date_index_method = get_date_indexes_for_spl_eval

    gnm = np.zeros((len(dates_for_eval), Nb))
    dgnm = np.zeros((len(dates_for_eval), Nb))
    for i_date, eval_date in enumerate(dates_for_eval):
        date_indexes = date_index_method(eval_date, spl_dates, spl_order)

        for j in date_indexes:
            center_date = spl_dates[j]
            spl_value = eval_spline(eval_date, center_date, spl_order, knot_spacing)
            deriv_spl_value = eval_derivative_spline(eval_date, center_date, spl_order, knot_spacing)
            gnm[i_date] += spl_coeffs[j]*spl_value
            dgnm[i_date] += spl_coeffs[j]*deriv_spl_value

    if with_derivative:
        return dates_for_eval, gnm, dgnm
    else:
        return dates_for_eval, gnm


def build_gnm_from_spline_coeffs(dates_for_eval, spl_dates, spl_coeffs, spl_order, with_derivatives):
    """
    Method to build the gnm from the spline coeffs and the parameters of splines (center_dates, order, spacing).
    This method uses the class scipy.interpolate.BSpline.

    :param dates_for_eval: Dates where the splines must be computed
    :type dates_for_eval: np.array (dim: Nt)
    :param spl_dates: Dates of the splines (knots)
    :type spl_dates: np.array (dim: Nspl)
    :param spl_coeffs: Coefficients of the data in the Bspline basis
    :type spl_coeffs: np.array (dim: Nspl x Nb)
    :param spl_order: Order of the used splines
    :type spl_order: int
    :param with_derivatives: If True, returns the reconstructed dgnm/dt and d2gnm/dt2 evaluated from derivatives of splines
    :type with_derivatives: bool
    :return: Dates, gnm evaluated from splines (and derivatives of gnm if with_derivatives is True)
    :rtype: np.array (dim: Nt), np.array (dim: Nt x Nb) (, np.array (dim: Nt x Nb), np.array (dim: Nt x Nb))
    """
    import scipy.interpolate

    full_knots = get_full_knots(spl_dates, spl_order, len(spl_coeffs))
    bsplines = scipy.interpolate.BSpline(full_knots, spl_coeffs, spl_order, extrapolate=False)

    gnm = bsplines(dates_for_eval)
    if with_derivatives:
        return dates_for_eval, gnm, bsplines(dates_for_eval, nu=1), bsplines(dates_for_eval, nu=2)
    else:
        return dates_for_eval, gnm


def read_spline_coeffs_file(file_name):
    """
    Extracts the spline coeffs and the spline parameters from a file

    :param file_name: name of the spline coeffs file
    :type file_name: str
    :return: center dates, spline coeffs, spline order and knot spacing
    :rtype: np.array, np.array, int, float
    """
    with open(file_name) as f:
        f.readline()  # Skip header with mod name
        header = f.readline().split()
        # Read info
        Lb = int(header[0])
        if Lb == 1:
            Nb = 1  # External field has only one coeff (q10)
        else:
            Nb = Lb * (Lb + 2)
        n_dates = int(header[1])
        jorder = int(header[2])
        center_dates = np.array(header[3:][jorder // 2:-jorder // 2], dtype=float)
        knot_sp = center_dates[1] - center_dates[0]
        # Create the list of coeffs and append the coeffs to it
        read_spl_coeffs = []
        for line in f:
            line_coeffs = line.split()
            read_spl_coeffs.extend(line_coeffs)

    spl_coeffs = np.array(read_spl_coeffs, dtype=np.float64)
    spl_coeffs = spl_coeffs.reshape((n_dates, Nb))

    # The Jorder read in the file is in fact spl_order+1
    # Starts at 1 for COVOBS whereas it starts at 0 for scipy.signal.bspline
    spl_order = jorder - 1
    return center_dates, spl_coeffs, spl_order, knot_sp


def scaling_EF(EF_data, back_EF=20.):
    """
    Scales the external field (EF) data with the formula:
        EF = (-1)*EF_data + back_EF

    :param EF_data: External field data to scale
    :type EF_data: np.ndarray
    :param back_EF: Background of external field (default: 20 nT)
    :type back_EF: float or np.ndarray
    :return: Scaled external field data (-1)*EF_data + back_EF
    :rtype: np.ndarray
    """
    return (-1)*EF_data + back_EF


def load(dataDirectory, dataModel, keepRealisations=False):
    """ Loading function for splines files (COV-OBS-like).  Also adds the data to the dataModel.

    :param dataDirectory: directory where the data is located
    :type dataDirectory: str (path)
    :param dataModel: Model to which the data should be added
    :type dataModel: Model
    :param keepRealisations: if True, searches for files matching real*mod* to load mean and RMS. Else, loads the latest mod* file.
    :type keepRealisations: bool (default: False)
    :return: 0 if everything went well, -1 otherwise
    :rtype: int
    """
    pattern = 'real*mod*' if keepRealisations else 'mod*'

    # MF
    gnm_times = None
    measureFolder = os.path.join(dataDirectory, 'models')
    generic_model_path = os.path.join(measureFolder, pattern)
    model_files = glob.glob(str(generic_model_path))

    if len(model_files) == 0:
        print('No spline files matching {} were found in {} ! Aborting loading...'.format(pattern, measureFolder))
        return -1

    if keepRealisations:
        # Loads all the real files and computes the mean and rms
        real_data = {'MF': [], 'SV': [], 'SA': []}
        for real_file in model_files:
            # print(os.path.basename(real_file))
            times, gnm, dgnm, d2gnm = build_gnm_from_file(real_file, with_derivatives=True)
            real_data['MF'].append(gnm)
            real_data['SV'].append(dgnm)
            real_data['SA'].append(d2gnm)
            if gnm_times is None:
                gnm_times = times
            else:
                assert np.allclose(times, gnm_times)

        model_data = {}
        for measure, data in real_data.items():
            data_as_array = np.array(data)
            # Real model data must have the shape (nb_times, nb_coeffs, nb_reals)
            model_data[measure] = np.moveaxis(data_as_array, 0, 2)
    else:
        # Load the latest model in the directory
        model_files.sort(reverse=True)
        model_data = {}
        # If no realisation, the model data has the shape (nb_times, nb_coeffs)
        gnm_times, model_data['MF'], model_data['SV'], model_data['SA'] = build_gnm_from_file(model_files[0], with_derivatives=True)

    # EF
    gnm_times = None
    measureFolder = os.path.join(dataDirectory, 'models_ext')

    generic_model_path = os.path.join(measureFolder, pattern)
    model_files = glob.glob(str(generic_model_path))

    if len(model_files) == 0:
        print('No spline files matching {} were found in {} ! Aborting loading...'.format(pattern, measureFolder))
        return -1

    # Get the mean dipolar coefficients
    if keepRealisations:
        mean_dip = model_data['MF'].mean(axis=2)[:, :3]
    else:
        mean_dip = model_data['MF'][:, :3]

    # Internal dipole to project from q10_cd to [q10, q11, s11]_geocentric
    internal_dip = mean_dip / np.linalg.norm(mean_dip, axis=1).reshape(len(mean_dip), 1)

    if keepRealisations:
        # Loads all the real files and computes the mean and rms
        q10_data = []
        for real_file in model_files:
            # print(os.path.basename(real_file))
            times, gnm = build_gnm_from_file(real_file, with_derivatives=False)
            q10_data.append(gnm)
            if gnm_times is None:
                gnm_times = times
            else:
                assert np.allclose(times, gnm_times)

        q10_data = np.array(q10_data)
        q10_data = scaling_EF(q10_data)

        nb_reals = q10_data.shape[0]

        real_ef_data = np.zeros((nb_reals, len(gnm_times), 3))
        # Transform q10_cd into [q10, q11, s11]_geocentric for every time
        for i_t in range(len(gnm_times)):
            real_ef_data[:, i_t] = - q10_data[:, i_t]*internal_dip[i_t]

        model_data['EF'] = np.moveaxis(real_ef_data, 0, 2)
    else:
        # Load the latest model in the directory
        model_files.sort(reverse=True)

        gnm_times, q10_data = build_gnm_from_file(model_files[0], with_derivatives=False)
        q10_data = scaling_EF(q10_data)

        # Transform q10_cd into [q10, q11, s11]_geocentric for every time
        ef_data = - q10_data * internal_dip

        model_data['EF'] = ef_data

    for measure_name, measure_data in model_data.items():

        if measure_name == "SV":
            units = "nT/yr"
        elif measure_name == "SA":
            units = "nT/yr^2"
        elif measure_name.endswith('F'):
            units = "nT"
        else:
            units = ""

        Nb = measure_data.shape[1]
        Lb = np.sqrt(Nb + 1) - 1
        lmax = int(Lb)
        # Assert that Nb gives an integer Lb
        assert Lb == lmax
        dataModel.addMeasure(measure_name, measure_name, lmax, units, data=measure_data, times=gnm_times)

    return 0
