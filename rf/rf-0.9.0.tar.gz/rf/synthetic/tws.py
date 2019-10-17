# Copyright 2019 Tom Eulenfeld, MIT license

"""
Wrapper arround telewavesim package utilizing the matrix propagator approach.

See Kennet1983, Thomson1997, BostockTrehu2012.
"""
import numpy as np

try:
    import telewavesim.utils as _tws
    from telewavesim.utils import Model as _TWSModel
except ImportError:
    _tws = None
    _TWSModel = object
    from warnings import warn
    warn('telewavesim import error. rf.synthetic.tws module not working.')


def read_model(fname, encoding=None):
    """
    Reads model parameters from file and returns a Model object.

    """
    assert _tws is not None
    values = np.genfromtxt(fname, dtype=None, encoding=encoding)
    return TWSModel(*zip(*values))

class TWSModel(_TWSModel):

    def calc_ttime(self, slowness, wvtype='P'):
        return _tws.calc_ttime(self, slowness, wvtype=wvtype)

    def synthetic(self, npts, delta,
                  slowness, back_azimuth=0, wvtype='P',
                  depth=None, c=1.5, rhof=1027,
                  tshift=0, rtype='tf', rotate='ZRT'
                  ):
        # set metadata of stream and transfer function
        # apply tshift
        # rotate to zne, zrt, lqt or pvh
        # add tests
        stream = _tws.run_plane(self, slowness, npts, delta, baz=back_azimuth,
                                wvtype=wvtype, obs=depth is not None,
                                dp=depth, c=c, rhof=rhof)
        if rtype == 'pw':
            return stream
        tf = _tws.tf_from_xyz(stream)
        return tf

    def __repr__(self):
        s = ('TWSModel(' + ', '.join(
                 '{0}={{0.{0}!r}}'.format(k)
                 for k in 'thickn rho vp vs isoflg ani tr pl'.split()) + ')')
        return s.format(self)


def test():
    from pkg_resources import resource_filename
    fname = resource_filename('telewavesim',
                              'examples/models/model_Porter2011.txt')
    model = read_model(fname)
    return model