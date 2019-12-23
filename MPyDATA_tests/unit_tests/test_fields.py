"""
Created at 14.10.2019

@author: Piotr Bartman
@author: Michael Olesik
@author: Sylwester Arabas
"""

from MPyDATA.arakawa_c.scalar_field import ScalarField
from MPyDATA.arakawa_c.vector_field import VectorField
import numpy as np
import pytest


class TestScalarField1D:
    def test_fill_halos(self):
        # Arrange
        halo = 2
        data = np.arange(0, 9)
        sut = ScalarField(data, halo)

        # Act
        sut._impl.fill_halos()

        # Assert
        np.testing.assert_equal(sut.get(), data)

        np.testing.assert_equal(sut._impl._data[:halo], data[-halo:])
        np.testing.assert_equal(sut._impl._data[-halo:], data[:halo])


class TestScalarField2D:
    def test_fill_halos(self):
        # Arrange
        halo = 2
        data = np.arange(0,9).reshape(3,3)
        sut = ScalarField(data, halo)

        # Act
        sut._impl.fill_halos()

        # Assert
        np.testing.assert_equal(sut.get(), data)

        np.testing.assert_equal(sut._impl._data[:halo,halo:-halo], data[-halo:,:])
        np.testing.assert_equal(sut._impl._data[-halo:,halo:-halo], data[:halo,:])

        np.testing.assert_equal(sut._impl._data[halo:-halo,:halo], data[:,-halo:])
        np.testing.assert_equal(sut._impl._data[halo:-halo,-halo:], data[:,:halo])


class TestVectorField1D:
    @pytest.mark.parametrize("halo", [
        pytest.param(1),
        pytest.param(2),
        pytest.param(3),
    ])
    def test_at(self, halo):
        # Arrange
        idx = 3
        data = np.zeros((10,))
        data[idx] = 44
        sut = VectorField(data=[data], halo=halo)

        # Act
        value = sut._impl.at((halo - 1) + (idx - 0.5), None)

        # Assert
        assert value == data[idx]

    @pytest.mark.parametrize("halo", [
        pytest.param(1),
        pytest.param(2),
        pytest.param(3),
    ])
    def test_fill_halos(self, halo):
        # Arrange
        data = np.arange(3)
        sut = VectorField(data=[data], halo = halo)

        # Act
        sut._impl.fill_halos()

        # Assert
        actual = sut._impl._data_0
        desired = np.concatenate([
            data[-(halo-1):] if halo > 1 else [],
            data,
            data[:(halo-1)]
        ])
        np.testing.assert_equal(actual, desired)


class TestVectorField2D:
    @pytest.mark.parametrize("halo", [
        pytest.param(1),
        pytest.param(2),
        pytest.param(3),
    ])
    def test_at(self, halo):
        # Arrange
        idx = (3, 5)
        data1 = np.arange(0, 10 * 12, 1).reshape(10, 12)
        data2 = np.zeros((9, 13))
        data1[idx] = -1
        sut = VectorField(data=(data1, data2), halo=halo)

        # Act
        value = sut._impl.at((halo - 1) + (idx[0] - 0.5), halo + idx[1] - 1)

        # Assert
        assert value == data1[idx]

    @pytest.mark.parametrize("halo", [
        pytest.param(1),
        pytest.param(2),
        pytest.param(3),
    ])
    def test_set_axis(self, halo):
        # Arrange
        idx = (0, 0)
        data1 = np.zeros((10, 12))
        data2 = np.zeros((9, 13))
        data2[idx] = 44
        sut = VectorField(data=(data1, data2), halo=halo)

        # Act
        sut._impl.set_axis(1)
        value = sut._impl.at(halo - 1 + idx[0] - 0.5, halo + idx[1] - 1)

        # Assert
        assert value == data2[idx]

