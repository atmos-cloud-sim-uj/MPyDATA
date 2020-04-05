from MPyDATA_examples.Arabas_and_Farhat_2019.analysis_figures_2_and_3 import convergence_in_space
import pytest
import numpy as np


@pytest.fixture(scope="module")
def l2err_vs_l2C():
    return convergence_in_space(num=2)


class TestFig2:
    @pytest.mark.skip()
    @staticmethod
    def test_upwind_1st_order(l2err_vs_l2C):
        for key, value in l2err_vs_l2C.items():
            if key.startswith("upwind"):
                x, y = value[0], value[1]
                slope = np.diff(y) / np.diff(x)
                np.testing.assert_almost_equal(slope, 2, 1)

    @staticmethod
    @pytest.mark.skip()
    def test_mpdata_2nd_order(l2err_vs_l2C):
        for key, value in l2err_vs_l2C.items():
            if key.startswith("MPDATA"):
                x, y = value[0], value[1]
                slope = np.diff(y) / np.diff(x)
                np.testing.assert_almost_equal(slope, 2.8, 1)
