import astropy.cosmology as cosmo
from astropy.cosmology import Planck15
import astropy.units as u
import numpy as np
import warnings

import matplotlib
from matplotlib import pyplot

import seaborn as sns

def li_prior_wt(m1s, m2s, dls, zs):
    return (
        dls * dls * (1 + zs) * (1 + zs) * (dls / ( 1 + zs) +
        (1 + zs) * Planck15.hubble_distance.to(u.Mpc).value / Planck15.efunc(zs))
    )

def approx_pop_dist_wt(m1s, m2s, dls, zs):
    return (
        m1s**(-2.5) * m2s**(-2.5) * (1 + zs)**(3 - 1) * 
        Planck15.differential_comoving_volume(zs).value
    )

approx_pop_dist_norm = {
    'BNS' : 0.652137,
    'NSBH': 0.144459,
    'MassGap': 0.195404,
    'BBH': 0.008
}

def rewt_samples(samples, wts):
    wts = wts / np.max(wts)

    neff = np.sum(wts)

    if neff < 100:
        warnings.warn(
            'only {:.1f} effective samples in reweighting'.format(neff))

    rs = np.random.rand(len(samples))
    sel = rs < wts

    return samples[sel]

def rewt_approx_massdist_redshift(samples):
    m1s = samples['m1_source']
    m2s = samples['m2_source']
    zs = samples['redshift']
    dls = samples['dist']

    li_wt = li_prior_wt(m1s, m2s, dls, zs)

    approx_dist = approx_pop_dist_wt(m1s, m2s, dls, zs)

    wts = approx_dist / li_wt
    return rewt_samples(samples, wts)

def is_BNS(samples):
    r"""Predicate for 'BNS': :math:`1 \, M_\odot < m_2 < m_1 < 3 \, M_\odot`.

    Parameters
    ----------
    samples: pandas.DataFrame
        Pandas DataFrame containing samples for 'm2_source' and 'm1_source'
    """
    return np.argwhere((1 <= samples['m2_source']) \
                          & (samples['m1_source'] < 3))

def BNS_p(samples):
    r"""Fraction of samples matching `is_BNS` predicate.

    >>> BNS_p(np.array([(1.4, 1.4)],
    ...       dtype=[('m1_source', float), ("m2_source", float)]))
    1.0

    Parameters
    ----------
    samples: pandas.DataFrame
        Pandas DataFrame containing samples for 'm2_source' and 'm1_source'
    """
    return len(is_BNS(samples)) / float(len(samples))

def is_NSBH(samples):
    r"""Predicate for 'NSBH': :math:`1 \, M_\odot < m_2 < 3 \, M_\odot`
    and :math:`5 \, M_\odot < m_1`

    Parameters
    ----------
    samples: pandas.DataFrame
        Pandas DataFrame containing samples for 'm2_source' and 'm1_source'
    """
    return np.argwhere((1 <= samples['m2_source']) \
                          & (samples['m2_source'] < 3) \
                          & (5 <= samples['m1_source']))

def NSBH_p(samples):
    r"""Fraction of samples matching `is_NSBH` predicate.

    >>> NSBH_p(np.array([(4.0, 1.4)],
    ...        dtype=[('m1_source', float), ("m2_source", float)]))
    0.0
    >>> NSBH_p(np.array([(10.0, 1.4)],
    ...        dtype=[('m1_source', float), ("m2_source", float)]))
    1.0

    Parameters
    ----------
    samples: pandas.DataFrame
        Pandas DataFrame containing samples for 'm2_source' and 'm1_source'
    """
    return len(is_NSBH(samples)) / float(len(samples))

def is_BBH(samples):
    r"""Predicate for 'BBH': :math:`5 \, M_\odot < m_2 < m_1`.

    Parameters
    ----------
    samples: pandas.DataFrame
        Pandas DataFrame containing samples for 'm2_source' and 'm1_source'
    """
    return np.argwhere(5 <= samples['m2_source'])

def BBH_p(samples):
    r"""Fraction of samples matching `is_BBH` predicate.

    >>> BBH_p(np.array([(4.0, 1.4)],
    ...       dtype=[('m1_source', float), ("m2_source", float)]))
    0.0
    >>> BBH_p(np.array([(4.0, 4.0)],
    ...       dtype=[('m1_source', float), ("m2_source", float)]))
    0.0
    >>> BBH_p(np.array([(10.0, 10.0)],
    ...       dtype=[('m1_source', float), ("m2_source", float)]))
    1.0

    Parameters
    ----------
    samples: pandas.DataFrame
        Pandas DataFrame containing samples for 'm2_source' and 'm1_source'
    """
    return len(is_BBH(samples)) / float(len(samples))

def has_NS(samples):
    r"""Predicate for presence of a neutron star, defined as :math:`m_2 < 3`
    (note difference with is_BNS above)

    Parameters
    ----------
    samples: pandas.DataFrame
        Pandas DataFrame containing samples for 'm2_source' and 'm1_source'
    """
    return np.argwhere(samples['m2_source'] < 3)

def HasNS_p(samples):
    r"""Fraction of samples matching the `has_NS` predicateself.

    >>> np.abs(0.667 - HasNS_p(np.array([(2.5,), (3.1,), (1.2,)],
    ...                        dtype=[('m2_source', np.float)]))) < 0.01
    True
    >>> HasNS_p(np.array([(3.1,), (3.2,), (3.3,)],
    ...         dtype=[('m2_source', np.float)]))
    0.0

    Parameters
    ----------
    samples: pandas.DataFrame
        Pandas DataFrame containing samples for 'm2_source' and 'm1_source'
    """
    return len(has_NS(samples)) / float(len(samples))

def remnant_mass(m1, m2, chi_bh, CNS=0.15):
    r"""Equation 4 in Foucart, Hinderer, and Nissanke, 2018. The default value
    of C_NS=0.15 is picked to be in the middle of the simulations presented in
    Figure 2 of this article.

    Parameters
    ----------
    m1: numpy.ndarray
        array of samples for m1
    m2: numpy.ndarray
        array of samples for m2
    chi_bh: numpy.ndarray
        something
    """
    alpha = 0.406
    beta = 0.139
    gamma = 0.255
    delta = 1.761

    q = m1 / m2 # Note Q > 1, following reference
    eta = q / (1 + q)**2

    Z1 = 1.0 + np.cbrt(1 - chi_bh**2) * (np.cbrt(1 + chi_bh) + \
        np.cbrt(1 - chi_bh))
    Z2 = np.sqrt(3 * chi_bh**2 + Z1**2)

    Rhat_ISCO = 3.0 + Z2 - np.sign(chi_bh) * np.sqrt((3.0 - Z1) * \
        (3.0 + Z1 + 2.0*Z2))

    return (np.maximum(alpha * (1 - 2 * CNS) / np.cbrt(eta) - \
        beta * Rhat_ISCO * CNS / eta + gamma, 0))**delta

def has_remnant(samples):
    r"""Predicate for remnant mass greater than 0, following
    Foucart, Hinderer, & Nissanke (2018). For details see
    https://ui.adsabs.harvard.edu/abs/2018PhRvD..98h1501F/abstract.

    Parameters
    ----------
    samples: pandas.DataFrame
        Pandas DataFrame containing samples for 'm2_source', 'm1_source', 'a1'
        and 'tilt1'
    """

    m1 = samples['m1_source']
    m2 = samples['m2_source']

    try:
        chi_bh = samples['a1']*np.where(samples['tilt1'] > np.pi/2.0, -1.0, 1.0)
    except ValueError:
        # Maybe there is no tilt1 field, so assume aligned?
        chi_bh = samples['a1']

    # Need a BH and a NS, and then remnant mass > 0.
    return np.argwhere((samples["m2_source"] < 3) & \
                       (samples["m1_source"] > 3) & \
                       (remnant_mass(m1, m2, chi_bh) > 0))

def HasRemnant_p(samples):
    r"""Fraction of samples matching the `has_remnant` predicate.

    >>> HasRemnant_p(np.array([(3.5, 3.4, 0.3, np.pi/4)],
    ...              dtype=np.dtype(
    ...                  [('m1_source', np.float),
    ...                   ('m2_source', np.float),
    ...                   ('a1', np.float),
    ...                   ('tilt1', np.float)])))
    0.0
    >>> HasRemnant_p(np.array([(3.5, 1.8, 0.4, 3*np.pi/4)],
    ...              dtype=np.dtype(
    ...                  [('m1_source', np.float),
    ...                   ('m2_source', np.float),
    ...                   ('a1', np.float),
    ...                   ('tilt1', np.float)])))
    1.0

    Parameters
    ----------
    samples: pandas.DataFrame
        Pandas DataFrame containing samples for 'm2_source' and 'm1_source'
    """
    return len(has_remnant(samples)) / float(len(samples))

def is_MG(samples):
    r"""Predicate for 'mass gap': :math:`3 \, M_\odot < m_2 < 5 \, M_\odot` or
    :math:`3 \, M_\odot < m_1 < 5 \, M_\odot`.

    Parameters
    ----------
    samples: pandas.DataFrame
        Pandas DataFrame containing samples for 'm2_source' and 'm1_source'
    """

    return np.argwhere(((3 <= samples['m2_source']) & \
                             (samples['m2_source'] < 5)) | \
                             ((3 <= samples['m1_source']) & \
                             (samples['m1_source'] < 5)))

def MG_p(samples):
    r"""Fraction of samples matching `is_MG` predicate.

    >>> MG_p(np.array([(10.0, 1.4)],
    ...      dtype=[('m1_source', float), ("m2_source", float)]))
    0.0
    >>> MG_p(np.array([(10.0, 10.0)],
    ...      dtype=[('m1_source', float), ("m2_source", float)]))
    0.0
    >>> MG_p(np.array([(4.0, 1.4)],
    ...      dtype=[('m1_source', float), ("m2_source", float)]))
    1.0
    >>> MG_p(np.array([(10.0, 4.0)],
    ...      dtype=[('m1_source', float), ("m2_source", float)]))
    1.0
    >>> MG_p(np.array([(4.0, 4.0)],
    ...     dtype=[('m1_source', float), ("m2_source", float)]))
    1.0

    Parameters
    ----------
    samples: pandas.DataFrame
        Pandas DataFrame containing samples for 'm2_source' and 'm1_source'
    """
    return len(is_MG(samples)) / float(len(samples))

def predicate_table(tab, samples):
    """Returns a table of probabilities.

    Parameters
    ----------
    table: dict
        dictionary that maps keys to predicate functions
    samples: pandas.DataFrame
        Pandas DataFrame containing samples

    Return
    ------
    dictionary that maps the keys of `table` to the probabilities of the
    associated predicates over the samples
    """

    pt = {}

    for k, v in tab.items():
        pt[k] = v(samples)

    total = sum([pt['BNS'], pt['MassGap'], pt['NSBH'], pt['BBH']])

    if abs(total - 1.0) > 1e-8:
        warnings.warn(
            'Probability sums to {:g} (= 1 - {:g}); some fraction of posterior '
            'lies outside our categorization'.format(total, 1-total))

    return pt

def plot_predicates(tab, samples, probs=None, **kwargs):
    """
    Scatter plot samples with their categorizations, according to supplied
    predicated table. kwargs are passed to `matplotlib.pyplot.scatter`, with
    the exception of `figsize` and `title`. Returns the completed figure.
    """

    fig = pyplot.figure()
    ax = pyplot.gca()

    title = kwargs.pop("title", None)
    if title is not None:
        pyplot.title(title)

    _defaults = {"s": 1}
    _defaults.update(kwargs)

    # Setup plot
    symaxis = pyplot.Polygon([[0, 0], [0, 1000], [1000, 1000]], \
                              color='k', alpha=0.2)
    ax.add_patch(symaxis)

    x_extent = samples["m1_source"].min(), samples["m1_source"].max()
    pyplot.xlim(x_extent[0] * 0.95, x_extent[1] * 1.05)
    y_extent = samples["m2_source"].min(), samples["m2_source"].max()
    pyplot.ylim(y_extent[0] * 0.95, y_extent[1] * 1.05)

    # Plot each region
    for bintype, color in default_colors.items():
        if bintype == "BNS":
            reg = pyplot.Polygon([[1, 1], [3, 1], [3, 3]], \
                              color=color, alpha=0.2)
        elif bintype == "BBH":
            reg = pyplot.Polygon([[5, 5], [1000, 5], [1000, 1000]], \
                              color=color, alpha=0.2)
        elif bintype == "MassGap":
            reg = pyplot.Polygon([[3, 1], [5, 1], [5, 3], [1000, 3],
                                  [1000, 5], [5, 5], [3, 3]], \
                              color=color, alpha=0.2)
        elif bintype == "NSBH":
            reg = pyplot.Polygon([[5, 1], [1000, 1], [1000, 3], [5, 3]], \
                              color=color, alpha=0.2)
        else:
            continue
        ax.add_patch(reg)

    # Get fractional membership

    default = {
        'BNS': BNS_p,
        'NSBH': NSBH_p,
        'BBH': BBH_p,
        'MassGap': MG_p}
    if probs is None:
        fracs = predicate_table(default, samples)
    else:
        fracs = probs
    # Plot mrem > 0 region
    m1, m2 = np.meshgrid(np.linspace(3, x_extent[-1], 1000), \
                         np.linspace(y_extent[0], min(3, y_extent[-1]), 1000))

    # Zero may be a little hard to capture, 1e-5 is (likely) insignificant
    # NOTE for chi_bh = -0.8 --- -1 tends to produce nothing within the
    # tolerance allowed by these grids
    for chi_bh in (0, 1., -0.8):
        mrem = remnant_mass(m1, m2, chi_bh)
        cs = pyplot.contour(m1, m2, mrem, [1e-5], colors='k', linestyles='--')
        for lbl in pyplot.clabel(cs, inline=1):
            lbl.set_text(r"$\chi={0:.1f}$".format(chi_bh))

    # Get sum of probability in mass categorizations
    cat_sum = sum([v for k, v in fracs.items() if k in default_categorizers])
    # Plot everything in black, this is the default "don't know"
    lbl = "other ({0:.2f}%)".format(100 - cat_sum * 100)
    pyplot.scatter(samples["m1_source"], samples["m2_source"], color='k', \
                    label=lbl, **_defaults)
    # Plot each category
    samples_new = {i: np.array(samples[i]) for i in samples.keys()}
    for bintype, cat in tab.items():
        is_cat = cat
        lbl = "{0} ({1:.2f}%)".format(bintype, fracs[bintype] * 100)
        pyplot.scatter(samples_new["m1_source"][is_cat], \
                       samples_new["m2_source"][is_cat], \
                       color=default_colors[bintype], \
                       label=lbl, **_defaults)
    pyplot.legend(loc="upper right")
    pyplot.xlabel(r"$m_{1}^{source} [M_{\odot}]$")
    pyplot.ylabel(r"$m_{2}^{source} [M_{\odot}]$")
    pyplot.tight_layout()

    return fig

default_categorizers = {
    'BNS': is_BNS,
    'NSBH': is_NSBH,
    'BBH': is_BBH,
    'MassGap': is_MG
}

default_colors = dict(zip(default_categorizers.keys(), \
                         sns.color_palette(n_colors=len(default_categorizers))))

default_predicates = {
    'BNS': BNS_p,
    'NSBH': NSBH_p,
    'BBH': BBH_p,
    'MassGap': MG_p,
    'HasNS': HasNS_p,
    'HasRemnant': HasRemnant_p
}
