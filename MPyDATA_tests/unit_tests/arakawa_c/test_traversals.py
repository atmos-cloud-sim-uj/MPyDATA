from MPyDATA.arakawa_c.traversals import Traversals
from MPyDATA.arakawa_c.meta import meta_halo_valid
from MPyDATA import Options, ScalarField, VectorField, ConstantBoundaryCondition
from MPyDATA.arakawa_c.indexers import indexers
import pytest
import numba
import numpy as np

jit_flags = Options().jit_flags


@numba.njit(**jit_flags)
def cell_id(i, j, k):
    if i == -1:
        i = 0
    if j == -1:
        j = 0
    return 100 * i + 10 * j + k


@numba.njit(**jit_flags)
def _cell_id_scalar(value, arg_1_vec, arg_2_scl, arg_3_scl, arg_4_scl):
    focus = arg_1_vec[0]
    if focus != arg_2_scl[0]:
        raise Exception()
    if focus != arg_3_scl[0]:
        raise Exception()
    if focus != arg_4_scl[0]:
        raise Exception()
    return value + cell_id(*focus)


@numba.njit(**jit_flags)
def _cell_id_vector(arg_1, arg_2, arg_3):
    focus = arg_1[0]
    if focus != arg_2[0]:
        raise Exception()
    if focus != arg_3[0]:
        raise Exception()
    return cell_id(*focus)


class TestTraversals:
    @staticmethod
    @pytest.mark.parametrize("n_threads", (1, 2, 3))
    @pytest.mark.parametrize("halo", (1, 2, 3))
    @pytest.mark.parametrize("grid", ((5, 6), (11,)))  # TODO: 3d
    @pytest.mark.parametrize("loop", (True, False))
    def test_apply_scalar(n_threads, halo, grid, loop):
        n_dims = len(grid)
        if n_dims == 1 and n_threads > 1:
            return

        # arrange
        traversals = Traversals(grid, halo, jit_flags, n_threads)
        sut = traversals.apply_scalar(loop=loop)

        scl_null_arg_impl = ScalarField.make_null(n_dims).impl
        vec_null_arg_impl = VectorField.make_null(n_dims).impl

        out = ScalarField(np.zeros(grid), halo, [ConstantBoundaryCondition(np.nan)]*n_dims)

        # act
        sut(_cell_id_scalar, _cell_id_scalar, _cell_id_scalar,
            *out.impl[0],
            *vec_null_arg_impl[0], *vec_null_arg_impl[1],
            *scl_null_arg_impl[0], *scl_null_arg_impl[1],
            *scl_null_arg_impl[0], *scl_null_arg_impl[1],
            *scl_null_arg_impl[0], *scl_null_arg_impl[1]
            )

        # assert
        data = out.get()
        assert data.shape == grid
        focus = (-halo, -halo)
        for i in range(halo, halo + grid[0]):
            for j in (-1,) if n_dims < 2 else range(halo, halo + grid[1]):
                for k in (-1,) if n_dims < 3 else range(halo, halo + grid[2]):
                    value = indexers[n_dims].at[0](focus, data, i, j, k)
                    assert value == (n_dims if loop else 1) * cell_id(i, j, k)
        assert scl_null_arg_impl[0][0][meta_halo_valid]
        assert vec_null_arg_impl[0][0][meta_halo_valid]
        assert not out.impl[0][0][meta_halo_valid]

    @staticmethod
    @pytest.mark.parametrize("n_threads", (1, 2, 3))
    @pytest.mark.parametrize("halo", (1, 2, 3))
    @pytest.mark.parametrize("grid", ((5, 6), (11,)))  # TODO: 3d
    def test_apply_vector(n_threads, halo, grid):
        n_dims = len(grid)
        if n_dims == 1 and n_threads > 1:
            return

        # arrange
        traversals = Traversals(grid, halo, jit_flags, n_threads)
        sut = traversals.apply_vector()

        scl_null_arg_impl = ScalarField.make_null(n_dims).impl
        vec_null_arg_impl = VectorField.make_null(n_dims).impl

        if n_dims == 1:
            data = (np.zeros(grid[0]+1),)
        elif n_dims == 2:
            data = (
                np.zeros((grid[0]+1, grid[1])),
                np.zeros((grid[0], grid[1]+1))
            )
        else:
            raise NotImplementedError()

        out = VectorField(data, halo, [ConstantBoundaryCondition(np.nan)] * n_dims)

        # act
        sut(_cell_id_vector, _cell_id_vector, _cell_id_vector,
            *out.impl[0],
            *scl_null_arg_impl[0], *scl_null_arg_impl[1],
            *vec_null_arg_impl[0], *vec_null_arg_impl[1],
            *scl_null_arg_impl[0], *scl_null_arg_impl[1]
            )

        # assert
        halos = (
            (halo-1, halo),
            (halo, halo-1)
        )
        for d in range(n_dims):
            data = out.get_component(d)
            focus = tuple(-halos[d][i] for i in range(n_dims))
            for i in range(halos[d][0], halos[d][0] + data.shape[0]):
                for j in (-1,) if n_dims < 2 else range(halos[d][1], halos[d][1] + data.shape[1]):
                    for k in (-1,) if n_dims < 3 else range(halos[d][2], halos[d][2] + data.shape[2]):
                        value = indexers[n_dims].at[0](focus, data, i, j, k)
                        assert value == cell_id(i, j, k)

        assert scl_null_arg_impl[0][0][meta_halo_valid]
        assert vec_null_arg_impl[0][0][meta_halo_valid]
        assert not out.impl[0][0][meta_halo_valid]
