"""Interpolators of cross-section data."""

from __future__ import absolute_import, division, print_function  # py2

import logging
import sys
from typing import (Any, Callable, List, Mapping, Sequence,  # noqa: F401
                    Tuple, Union, cast)

import pandas  # noqa: F401
import scipy.interpolate

from susy_cross_section.axes_wrapper import AxesWrapper

if sys.version_info[0] < 3:  # py2
    str = basestring          # noqa: A001, F821

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

InterpolationType = Callable[[Sequence[float]], float]


class InterpolationWithUncertainties:
    """An interpolation result of values accompanied by uncertainties."""

    def __init__(self, central, central_plus_unc, central_minus_unc, param_names=None):
        # type: (InterpolationType, InterpolationType, InterpolationType, List[str])->None
        self._f0 = central
        self._fp = central_plus_unc
        self._fm = central_minus_unc
        self.param_index = {name: i for i, name in enumerate(param_names or [])}  # type: Mapping[str, int]

    # py2 does not accept single kwarg after args.
    def __call__(self, *args, **kwargs):   # py2; in py3, def __call__(self, *args, unc_level=0):
        # type: (Any, float)->float
        """Return the fitted value with requested uncertainty level."""
        unc_level = kwargs.get('unc_level', 0)  # py2
        return self.f0(*args) + (
            unc_level * self.unc_p_at(*args) if unc_level > 0 else
            unc_level * abs(self.unc_m_at(*args)) if unc_level < 0 else
            0
        )

    def _interpret_args(self, *args, **kwargs):
        # type: (float, float)->Sequence[float]
        if not kwargs:
            return args
        tmp = list(args)   # type: List[Union[float, None]]
        for key, value in kwargs.items():
            index = self.param_index[key]
            if index >= len(tmp):
                tmp.extend([None for i in range(index + 1 - len(tmp))])
            tmp[index] = value
        if any(v is None for v in tmp):
            raise ValueError('insufficient arguments: %s, %s.', args, kwargs)
        return cast(Sequence[float], tmp)

    def f0(self, *a, **kw):
        # type: (float, float)->float
        """Return the fitted value of central value."""
        return self._f0(self._interpret_args(*a, **kw))

    def fp(self, *a, **kw):
        # type: (float, float)->float
        """Return the fitted value of central value."""
        return self._fp(self._interpret_args(*a, **kw))

    def fm(self, *a, **kw):
        # type: (float, float)->float
        """Return the fitted value of central value."""
        return self._fm(self._interpret_args(*a, **kw))

    def tuple_at(self, *a, **kw):
        # type: (float, float)->Tuple[float, float, float]
        """Return the tuple (central, +unc, -unc) at the fit point."""
        args = self._interpret_args(*a, **kw)
        return self.f0(*args), self.unc_p_at(*args), self.unc_m_at(*args)

    def unc_p_at(self, *a, **kw):
        # type: (float, float)->float
        """Return the fitted value of positive uncertainty."""
        args = self._interpret_args(*a, **kw)
        return self.fp(*args) - self.f0(*args)

    def unc_m_at(self, *a, **kw):
        # type: (float, float)->float
        """Return the fitted (negative) value of negative uncertainty."""
        args = self._interpret_args(*a, **kw)
        return -(self.f0(*args) - self.fm(*args))


class AbstractInterpolator:
    """Abstract class for interpolators of values with 1sigma uncertainties.

    Actual interpolators, inheriting this abstract class, will perform
    interpolation of pandas data frame.
    """

    def interpolate(self, df_with_unc):
        # type: (pandas.DataFrame)->InterpolationWithUncertainties
        """Interpolate the values accompanied by uncertainties."""
        return InterpolationWithUncertainties(
            self._interpolate(df_with_unc['value']),
            self._interpolate(df_with_unc['value'] + df_with_unc['unc+']),
            self._interpolate(df_with_unc['value'] - abs(df_with_unc['unc-'])),
            param_names=df_with_unc.index.names)

    def _interpolate(self, df):
        # type: (pandas.DataFrame)->InterpolationType
        raise NotImplementedError


class Scipy1dInterpolator(AbstractInterpolator):
    """Interpolator for values with uncertainty based on Scipy interp1d."""

    def __init__(self, kind=None, axes=None):
        # type: (str, str)->None
        self.kind = (kind or 'linear').lower()  # type: str
        self.wrapper = {
            'linear': AxesWrapper(['linear'], 'linear', 'linear'),
            'log': AxesWrapper(['linear'], 'log', 'exp'),
            'loglinear': AxesWrapper(['log'], 'linear', 'linear'),
            'loglog': AxesWrapper(['log'], 'log', 'exp'),
        }[axes or 'linear']  # type: AxesWrapper

    def _interpolate(self, df):
        # type: (pandas.DataFrame)->InterpolationType
        if df.index.nlevels != 1:
            raise Exception('Scipy1dInterpolator not handle multiindex data.')
        x_list = [self.wrapper.wx[0](x) for x in df.index.to_numpy()]   # array(n_points)
        y_list = [self.wrapper.wy(y) for y in df.to_numpy()]            # array(n_points)
        # as interp1d is float->float, we convert it to Tuple[float]->float.

        def fit(x, f=scipy.interpolate.interp1d(x_list, y_list, self.kind)):  # noqa: B008
            # type: (Sequence[float], Callable[[float], float])->float
            return f(*x)

        return self.wrapper.correct(fit)
