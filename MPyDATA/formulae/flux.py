"""
Created at 11.10.2019

@author: Piotr Bartman
@author: Michael Olesik
@author: Sylwester Arabas
"""

from ..arakawa_c.scalar_field import ScalarField
from ..arakawa_c.vector_field import VectorField
from ..options import Options
import numpy as np
from MPyDATA_tests.utils import debug

if debug.DEBUG:
    import MPyDATA_tests.utils.fake_numba as numba
else:
    import numba

# TODO
HALO = 1


def make_flux(opts: Options, it: int):
    iga = opts.iga
    @numba.njit()         # TODO: check if (abs(c)-C)/2 is not faster
    def flux(psi: ScalarField.Impl, GC: VectorField.Impl):
        if it == 0 or not iga:
            result = (
                np.maximum(0, GC.at(+.5, 0)) * psi.at(0, 0) +
                np.minimum(0, GC.at(+.5, 0)) * psi.at(1, 0)
            )
        else:
            result = GC.at(+.5, 0)
        return result
    return flux


def make_fluxes(opts: Options):
    fluxes = []
    for it in range(opts.n_iters):
        fluxes.append(make_flux(opts, it))
    return fluxes



