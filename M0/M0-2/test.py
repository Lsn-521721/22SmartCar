import unittest
from legacy_corr import calc_corr

class TestCalcCorr(unittest.TestCase):
    def test_perfect_positive_corr(self):
        n, mean_x, mean_y, r = calc_corr([1, 2, 3], [2, 4, 6])
        self.assertAlmostEqual(r, 1.0, places=6)

    def test_perfect_negative_corr(self):
        n, mean_x, mean_y, r = calc_corr([1, 2, 3], [6, 4, 2])
        self.assertAlmostEqual(r, -1.0, places=6)

if __name__ == "__main__":
    unittest.main()
