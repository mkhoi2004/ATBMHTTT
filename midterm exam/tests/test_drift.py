"""
Kiểm thử đơn vị cho mô-đun drift.py (PSI, KS-test, Label drift).
"""

import unittest
import numpy as np
import pandas as pd
from src.drift import calculate_psi, calculate_ks_test, compute_label_drift


class TestDrift(unittest.TestCase):
    def test_psi_identical_distribution(self):
        # Hai phân bố giống hệt nhau -> PSI phải xấp xỉ 0 (< 0.05)
        np.random.seed(42)
        expected = np.random.normal(0, 1, 1000)
        actual = np.random.normal(0, 1, 1000)

        psi = calculate_psi(expected, actual)
        self.assertLess(psi, 0.05, f"PSI should be near zero for identical distributions, got {psi}")

    def test_psi_shifted_distribution(self):
        # Hai phân bố lệch nhau rõ rệt (mean lệch 3 đơn vị) -> PSI phải lớn (> 0.25)
        np.random.seed(42)
        expected = np.random.normal(0, 1, 1000)
        actual = np.random.normal(3, 1, 1000)

        psi = calculate_psi(expected, actual)
        self.assertGreater(psi, 0.25, f"PSI should exceed 0.25 for heavily drifted distributions, got {psi}")

    def test_ks_test(self):
        np.random.seed(42)
        ref = np.random.normal(0, 1, 500)
        cur = np.random.normal(2, 1, 500)

        stat, pval = calculate_ks_test(ref, cur)
        self.assertGreater(stat, 0.3)
        self.assertLess(pval, 1e-4)

    def test_label_drift_calculation(self):
        data = {
            "appeared": ["2018-01", "2018-01", "2018-02", "2018-02"],
            "label": [1, 0, 1, 1],
        }
        df = pd.DataFrame(data)
        drift_df = compute_label_drift(df, "appeared", "label")

        self.assertEqual(len(drift_df), 2)
        self.assertEqual(drift_df.loc[drift_df["appeared"] == "2018-01", "malware_ratio"].values[0], 0.5)
        self.assertEqual(drift_df.loc[drift_df["appeared"] == "2018-02", "malware_ratio"].values[0], 1.0)


if __name__ == "__main__":
    unittest.main()
